.PHONY: configure sync run static migrate migrations superuser experiment daily weekly monthly yearly test test-js lint-js format-js lint format typecheck openapi package dist publish deploy-check release check labels sandbox sandbox-reset sandbox-shell

# Declarations: every variable lives here, before any target. `?=` - a value
# the caller exported wins.

# uv's cache, repo-local: the agent sandbox denies the home cache, and a
# repo-local one keeps `package`/`dist` repeatable offline.
export UV_CACHE_DIR ?= $(CURDIR)/tmp/uv-cache

# The experiment the cadence and `experiment` run.
EXPERIMENT ?= rem

# The Payoneer export `monthly` loads: the newest report_*.csv in the extracts
# folder, unless the caller names one.
PAYONEER ?= $(lastword $(sort $(wildcard var/documents/bank/transaction-extracts/report_*.csv)))

# The year `yearly` archives; defaults to the current one.
YEAR ?= $(shell date +%Y)

# Reproducible wheels: file timestamps are the build commit's date, so the
# same source builds the same wheel.
SOURCE_DATE_EPOCH ?= $(shell git log -1 --format=%ct)

# The named volume `sandbox` keeps its state in; the default `sandbox-shell`
# command.
SANDBOX_VOLUME ?= scaffolding-sandbox
C ?= sh

# The tag `publish` uploads to; defaults to the tag HEAD sits on.
TAG ?= $(shell git describe --tags --exact-match 2>/dev/null)

RUN = uv run scaffolding

# The application: Django's own dev server, autoreload and all.
run:
	$(RUN) runserver

configure:
	mkdir -p \
		var/scratchpad/backlog \
		var/documents/statements \
		var/documents/scaffolding \
		var/documents/bank/transaction-extracts \
		var/documents/sources \
		var/documents/contracts \
		var/documents/expenses \
		var/openapi \
		var/wsfex-raw \
		var/wsfex-params \
		etc/secrets \
		tmp

sync:
	uv sync --extra dev

static:
	$(RUN) collectstatic --noinput

migrate:
	$(RUN) migrate
	$(RUN) migrate --database tasks django_tasks_database

# A model changed without a migration is a green suite and a broken clone.
# `makemigrations` runs Django's system checks first, and those probe the
# configured SQLite for JSON support - so `var/` must exist even on a fresh
# clone, where no database file has been created yet.
migrations:
	mkdir -p var
	$(RUN) makemigrations --check --dry-run

superuser:
	$(RUN) createsuperuser

# The experiment, as one dispatch: run it (snapshot the scenarios and the
# strategy bands) then print the year-ahead forecast. Every input is read off the
# books - the surplus from the projection, the FX from the ARCA quote in force,
# the devaluation from the ARCA series - so nothing is typed at the prompt.
experiment:
	$(RUN) experiment run $(EXPERIMENT)
	$(RUN) experiment forecast

# The cadence, one target per frequency. Each is transparent - every line is one
# command, nothing is wrapped or hidden - and idempotent: a skipped run leaves a
# gap the next run fills, never a wrong number (docs/SCHEDULES.md).

# Daily (after 18:00 ART): the published reference rates, and the dollar
# cotización. Why the fiscal quote opts into WSFEX here, and every other rule
# of the cadence, is `docs/SCHEDULES.md` - one owner, not a second copy.
daily:
	$(RUN) market fetch --provider bcra
	$(RUN) market fetch --provider mirror
	ARCA_RATE_PROVIDER=wsfex $(RUN) rate fetch

# Weekly: every pass over the movements table in order, then the places the
# table and the ledger disagree, then the experiment snapshot and its year-ahead
# forecast. `run` prints zeros on a second pass; `reconcile` is a report;
# `experiment run` snapshots whatever the week produced (same-day rerun is a no-op).
weekly:
	$(RUN) movements run
	$(RUN) movements reconcile
	$(RUN) experiment run $(EXPERIMENT)
	$(RUN) experiment forecast

# Monthly (the 2nd, once the rail export lands): the period's fresh inputs, then
# the experiment snapshot. `movements load` appends the named Payoneer export
# and is a no-op on an already-loaded one (override with `make monthly
# PAYONEER=…`). The interactive half - `month --issue`, `balances set` - stays
# out: those take a decision or a hand-entered figure.
monthly:
	$(RUN) inflation fetch
	$(RUN) movements load PAYONEER $(PAYONEER)
	$(RUN) movements classify
	$(RUN) balances derive
	$(RUN) experiment run $(EXPERIMENT)
	$(RUN) experiment forecast

# Yearly: the shareable snapshot - one Sheet per year in the shared Drive folder
# (docs/ARCHIVE.md). Re-archiving rewrites tabs and replaces charts, never stacks
# a second copy. Needs `scaffolding login` first.
yearly:
	$(RUN) archive $(YEAR)

test:
	uv run pytest

# The frontend's functional core: node's built-in runner, no dependencies and
# no build. `node` is a dev prerequisite only - the served site ships no node.
# Coverage is V8's own and gated at 100% on what the tests import (core/);
# a file no test imports (charts.js, telescope.js) is not in the report at all,
# so the gate cannot see it - the way in is to move its pure part into a core/ module.
# The test files themselves are excluded from the report (the gate is on the
# imported core/ modules); the runner takes a glob, not a bare directory (a
# directory path is not recursed).
test-js:
	node --test --experimental-test-coverage --test-coverage-exclude="tests/js/**" --test-coverage-lines=100 --test-coverage-branches=100 --test-coverage-functions=100 "tests/js/**/*.test.js"

# The frontend's lint/format: one stdlib-only script (bin/js.mjs), the JS half
# of what ruff does for Python. `lint-js` checks and never writes; `format-js`
# rewrites whitespace and reports what it cannot.
lint-js:
	node bin/js.mjs lint

format-js:
	node bin/js.mjs format

lint:
	uv run ruff check src tests bin

format:
	uv run ruff format src tests bin && uv run ruff check --fix src tests bin

typecheck:
	uv run mypy src tests bin

openapi:
	$(RUN) spectacular --file var/openapi/schema.yaml --validate --fail-on-warn

# The wheel, built from committed source: `git archive HEAD`, never the working
# tree, so an untracked file (another loop's work in progress) cannot leak into
# what gets installed. SOURCE_DATE_EPOCH pins the timestamps, so the same source
# builds the same wheel. The packaging tests pin the same build; `dist` runs
# them and the smoke.
package:
	rm -rf tmp/dist/build dist
	mkdir -p tmp/dist/build dist
	git archive HEAD | tar -x -C tmp/dist/build
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) uv build --wheel --out-dir dist tmp/dist/build

# The artifact proven: the packaging tests build and pin the wheel, then
# bin/wheel_smoke.py installs it into a throwaway venv (first run resolves the
# closure; uv's cache makes repeats offline), seeds the reference tables, boots
# the server, and checks the insecure-key refusal in the installed shape.
# Both run `--no-project` (the proof pulls pytest ephemerally, the smoke is
# stdlib-only), so `dist` needs no `sync` and CI skips the dev extra.
# Deliberately not in `check`, which stays network-free.
dist: package
	uv run --no-project --with pytest pytest tests/scaffolding/packaging -q
	uv run --no-project python bin/wheel_smoke.py

# Publish the wheel in dist/ to the tag's GitHub release - CI's step: a pushed
# v* tag runs `make publish`, the full `dist` proof first, and the wheel lands
# where machines download it from. The release is created if the tag has none
# (its notes generated from the merged PR titles - the changelog, no tool), and
# the upload replaces a stale same-named asset, so a re-run is a clean run.
# `gh` takes its auth from GITHUB_TOKEN in CI or its own login locally.
publish: dist
	test -n "$(TAG)" || (echo "usage: make publish TAG=vX.Y.Z" && exit 1)
	gh release view "$(TAG)" >/dev/null 2>&1 || gh release create "$(TAG)" --title "$(TAG)" --generate-notes
	gh release upload "$(TAG)" dist/*.whl --clobber

# The sandbox (sandbox/Dockerfile): the wheel in `dist/` on a bare Debian, its
# state in a named volume. Rebuilds only the wheel layer. `sandbox-reset` drops
# the volume: the next `sandbox` starts from an empty install. `sandbox-shell`
# runs any command against that state: `make sandbox-shell C="scaffolding month"`.
sandbox/requirements.txt: uv.lock
	uv export --no-hashes --locked --no-default-groups --no-emit-project -o $@

sandbox: sandbox/requirements.txt
	docker build -q -f sandbox/Dockerfile -t scaffolding-sandbox .
	docker run --rm -p 127.0.0.1:8000:8000 -v $(SANDBOX_VOLUME):/state scaffolding-sandbox \
		sh -c 'scaffolding migrate && scaffolding migrate --database tasks django_tasks_database && scaffolding loadreference && exec scaffolding runserver 0.0.0.0:8000 --noreload'

sandbox-shell:
	docker run --rm -it -v $(SANDBOX_VOLUME):/state scaffolding-sandbox sh -c '$(C)'

sandbox-reset:
	docker volume rm -f $(SANDBOX_VOLUME)

# The deployed machine's checklist: Django's own `check --deploy`, which also
# lists the insecure-SECRET_KEY check (scaffolding.security.W001). Runs on the
# machine that faces the network - it reads the local .env, so the packaging
# laptop's answer is not the deployment's answer.
deploy-check:
	$(RUN) check --deploy

# Cut a release: gate first (the full check), then bump VERSION and commit it,
# build the proven wheel from that commit, and tag. The wheel's version is the
# VERSION file's, so the bump precedes `dist` - the artifact carries the tag's
# number. Pushing the tag wakes CI, which re-proves the wheel and attaches it to
# the tag's GitHub release (`make publish` is that step). A run that fails after
# the bump re-runs cleanly: the staged-diff guard skips the commit when the bump
# is already in, and the gate and dist pick up from there.
release:
	test -n "$(VERSION)" || (echo "usage: make release VERSION=x.y.z" && exit 1)
	$(MAKE) check
	printf '%s\n' '$(VERSION)' > VERSION
	git add VERSION
	git diff --cached --quiet -- VERSION || git commit -m "Bump version to $(VERSION)"
	$(MAKE) dist
	git tag "v$(VERSION)"

check: format lint format-js lint-js typecheck migrations test-js test

# The five status labels (docs/WORKFLOW.md). Idempotent: create fails on an
# existing label, then edit brings it to spec.
labels:
	gh label create todo --description "Queued" --color 1d76db || gh label edit todo --description "Queued" --color 1d76db
	gh label create doing --description "Active" --color fbca04 || gh label edit doing --description "Active" --color fbca04
	gh label create done --description "Shipped" --color 0e8a16 || gh label edit done --description "Shipped" --color 0e8a16
	gh label create reviewing --description "PR open, needs eyes" --color 6f42c1 || gh label edit reviewing --description "PR open, needs eyes" --color 6f42c1
	gh label create closed --description "Tabled or won't-do" --color cccccc || gh label edit closed --description "Tabled or won't-do" --color cccccc
