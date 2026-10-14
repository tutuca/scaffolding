.PHONY: configure sync run static migrate migrations superuser test test-js lint-js format-js lint format typecheck openapi package dist publish deploy-check release check skills-check labels sandbox sandbox-reset sandbox-shell

# Declarations: every variable lives here, before any target. `?=` - a value
# the caller exported wins.

# uv's cache, repo-local: the agent sandbox denies the home cache, and a
# repo-local one keeps `package`/`dist` repeatable offline.
export UV_CACHE_DIR ?= $(CURDIR)/tmp/uv-cache

# Reproducible wheels: file timestamps are the build commit's date, so the same
# source builds the same wheel.
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
	mkdir -p var/scratchpad etc/secrets tmp

sync:
	uv sync --extra dev

static:
	$(RUN) collectstatic --noinput

migrate:
	$(RUN) migrate
	$(RUN) migrate --database tasks django_tasks_database

# A model changed without a migration is a green suite and a broken clone.
migrations:
	mkdir -p var
	$(RUN) makemigrations --check --dry-run

superuser:
	$(RUN) createsuperuser

test:
	uv run pytest

# The frontend's functional core: node's built-in runner, no dependencies and no
# build. Coverage is V8's own and gated at 100% on what the tests import (core/).
test-js:
	node --test --experimental-test-coverage --test-coverage-exclude="tests/js/**" --test-coverage-lines=100 --test-coverage-branches=100 --test-coverage-functions=100 "tests/js/**/*.test.js"

# The frontend's lint/format: one stdlib-only script (bin/js.mjs).
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
# tree, so an untracked file cannot leak into what gets installed.
package:
	rm -rf tmp/dist/build dist
	mkdir -p tmp/dist/build dist
	git archive HEAD | tar -x -C tmp/dist/build
	SOURCE_DATE_EPOCH=$(SOURCE_DATE_EPOCH) uv build --wheel --out-dir dist tmp/dist/build

# The artifact proven: the packaging tests build and pin the wheel, then
# bin/wheel_smoke.py installs it into a throwaway venv and boots the server.
dist: package
	uv run --no-project --with pytest pytest tests/scaffolding/packaging -q
	uv run --no-project python bin/wheel_smoke.py

# Publish the wheel in dist/ to the tag's GitHub release - CI's step.
publish: dist
	test -n "$(TAG)" || (echo "usage: make publish TAG=vX.Y.Z" && exit 1)
	gh release view "$(TAG)" >/dev/null 2>&1 || gh release create "$(TAG)" --title "$(TAG)" --generate-notes
	gh release upload "$(TAG)" dist/*.whl --clobber

# The sandbox (sandbox/Dockerfile): the wheel in `dist/` on a bare Debian, its
# state in a named volume.
sandbox/requirements.txt: uv.lock
	uv export --no-hashes --locked --no-default-groups --no-emit-project -o $@

sandbox: sandbox/requirements.txt
	docker build -q -f sandbox/Dockerfile -t scaffolding-sandbox .
	docker run --rm -p 127.0.0.1:8000:8000 -v $(SANDBOX_VOLUME):/state scaffolding-sandbox \
		sh -c 'scaffolding migrate && scaffolding migrate --database tasks django_tasks_database && exec scaffolding runserver 0.0.0.0:8000 --noreload'

sandbox-shell:
	docker run --rm -it -v $(SANDBOX_VOLUME):/state scaffolding-sandbox sh -c '$(C)'

sandbox-reset:
	docker volume rm -f $(SANDBOX_VOLUME)

# The deployed machine's checklist: Django's own `check --deploy`.
deploy-check:
	$(RUN) check --deploy

# Cut a release: gate first (the full check), then bump VERSION and commit it,
# build the proven wheel, and tag. The pushed tag wakes CI.
release:
	test -n "$(VERSION)" || (echo "usage: make release VERSION=x.y.z" && exit 1)
	$(MAKE) check
	printf '%s\n' '$(VERSION)' > VERSION
	git add VERSION
	git diff --cached --quiet -- VERSION || git commit -m "Bump version to $(VERSION)"
	$(MAKE) dist
	git tag "v$(VERSION)"

check: format lint format-js lint-js typecheck migrations test-js test skills-check

# The skills under .agents/skills are prompt content committed to the repo:
# `.agents/prompt_validate.py` checks each markdown file for control/format
# characters, homoglyph-risk scripts, whitespace-only payloads and secrets.
# Stdlib-only, so the check adds no dependency and stays network-free.
skills-check:
	@fail=0; for f in $$(find .agents/skills -type f -name '*.md' | sort); do out=$$(python3 .agents/prompt_validate.py "$$f" 2>&1) || fail=1; if [ -n "$$out" ]; then printf '%s\n' "$$f:" "$$out"; fi; done; exit $$fail

# The five status labels (docs/WORKFLOW.md). Idempotent.
labels:
	gh label create todo --description "Queued" --color 1d76db || gh label edit todo --description "Queued" --color 1d76db
	gh label create doing --description "Active" --color fbca04 || gh label edit doing --description "Active" --color fbca04
	gh label create done --description "Shipped" --color 0e8a16 || gh label edit done --description "Shipped" --color 0e8a16
	gh label create reviewing --description "PR open, needs eyes" --color 6f42c1 || gh label edit reviewing --description "PR open, needs eyes" --color 6f42c1
	gh label create closed --description "Tabled or won't-do" --color cccccc || gh label edit closed --description "Tabled or won't-do" --color cccccc
