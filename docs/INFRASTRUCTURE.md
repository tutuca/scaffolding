# Infrastructure

What this runs on, what it is built out of, and the rule for adding to that.
Written 2026-09-18, when the tool stopped being laptop-only.

## The shape

One machine. One process (plus a task worker). Two SQLite files - the ledger and
the task queue. One login. One page at `/`, which is `interface/web.HomeView` and
not the admin index - the admin is a tool inside the product, not the front of it.

That is a decision, not a stage on the way to something. The tool serves one
person and possibly a second related one; every scale concern below that
threshold is out of scope, and a design that costs something today to be ready
for load that is not coming is a design that has been paid for twice.

"Production quality" here means the practices - one door, secrets never in the
repo, a migration for every model change, `make check` green, TLS - not the
capacity. None of it is about surviving traffic.

### Scale-out, if it is ever wanted

**One SQLite database per user, for all of their data.** The Bluesky PDS shape.
Never a shared multi-tenant Postgres. The task queue is the exception to "one
SQLite file": it is process state, not books, so it lives on its own `tasks.sqlite`
beside the ledger (routed by `conf/router.py`), never inside the user's data file.

Recorded because it constrains what to build now: nothing should acquire a
dependency on cross-user queries, and `docs/ARCHITECTURE.md`'s rule that every
table which is not reference data carries `taxpayer` is exactly the column such a
split would follow. The rule already pays for itself in scoping; this is the
second reason to keep it absolute.

## One process

`scaffolding runserver` - Django's own dev server, nothing wrapped - and in
production one WSGI process behind TLS. There is nothing else in the picture:
the books are server-rendered pages and no kernel runs anywhere. Between
2026-09-18 and 2026-09-19 the design was Django mounted inside a jupyter server
(Tornado outermost, for the kernel websocket); the books graduated into pages,
the websocket went with the kernels, and on 2026-10-12 jupyter, the playground,
and the dataframe and plotting stack behind them were removed from the project.
What that design cost to find out is in git history, in the one-nozzle spec.

`bin/serve_smoke.py` checks the running server - the gate from both sides, the
chrome on every surface, the figures mounted - on stdlib alone.

Background tasks (`interface/tasks`, `docs/ARCHITECTURE.md`) run on
`django-tasks-db` (`TASKS` in `conf/settings.py`): an enqueued task is a row on the
`tasks` database - a second SQLite beside the ledger, routed by `conf/router.py` -
and `scaffolding db_worker` runs them. That worker is the one extra process this
document otherwise has no use for; without it running, tasks queue and wait.
`scaffolding migrate --database tasks django_tasks_database` builds the queue's
table (or `make migrate`, which does both databases). The app label scopes the
second migrate to the queue only: an unlabelled `migrate --database tasks` would
record every app's migrations on `tasks` even though the router keeps their
tables on `default`. Note the reverse is expected too - a plain `migrate`
records the task app's migration *names* on `default` without creating the table
there, because Django's migration recorder does not consult the router; that is
harmless and why `showmigrations` on `default` lists them as applied once
`make migrate` has run. The contract holds: task arguments and return values
are JSON (dates, decimals and enums cross as strings, converted with
`date.fromisoformat`/`Decimal` at the call site).

The queue is not only process state: a finished row keeps its kwargs and return
value, so bank transcripts and bill text sit in `tasks.sqlite` until pruned -
treat it like the ledger beside it. `prune_tasks` (`interface/tasks/queue.py`)
deletes results finished over a week ago. Nothing starts it for you: run it from
a cron/launchd line, or by hand, once a week -

```sh
scaffolding db_worker --batch
```

after enqueueing `prune_tasks`, or simply `scaffolding shell -c "from
scaffolding.interface.tasks import prune_tasks; prune_tasks.enqueue()"` followed by a
worker pass. Cron-style scheduling that would make this automatic is issue #4.

Enqueueing commits immediately to the separate queue database, even inside a
ledger transaction. The caller must defer work that depends on that transaction:

```python
from functools import partial

from django.db import transaction

from scaffolding.interface.tasks import run_movements

with transaction.atomic(using="default"):
    # Write the ledger inputs here, then schedule their processing after commit.
    transaction.on_commit(partial(run_movements.enqueue, taxpayer=taxpayer), using="default")
```

A rollback discards the callback; a successful commit enqueues the task. Without
the callback, a worker can run before the ledger commits and a rollback leaves
the task queued. Corrected 2026-10-13: this replaces the claim that enqueueing
automatically defers; neither Django nor this backend supplies that guarantee.

## Software bill of materials

Counted 2026-10-12 with `uv export --no-dev` and `uv tree`.

| set | what it is |
| --- | --- |
| runtime | Django, DRF, drf-spectacular, allauth, cryptography, the Google client, django-environ, pypdf, django-tasks-db |
| dev only, never deployed | pytest, mypy, ruff, the stubs, model-bakery, ipdb, tornado (`bin/ui_shot.py`'s DevTools client) |

Twelve direct runtime dependencies (`django-tasks-db` is the twelfth: it stores the
task queue, and its two dependencies - django-stubs-ext and typing-extensions - were
already in the closure) and one optional group, `dev`. The `notebook` extra
(jupyter, notebook, polars, pyarrow, seaborn, matplotlib) existed only for
`scaffolding playground` and went with it: the lock file lost about 1,560 lines.

### Styling adds nothing

The login, the admin and the notebooks share one language: ten base tokens in
`ui/static/ui/tokens.css`, everything else derived (`docs/DESIGN.md`). Django's
admin is dressed through its **42** documented CSS custom properties plus four
vendored templates, each pinned by `tests/scaffolding/ui/test_vendored.py` to the
sha256 of its upstream origin - an upgrade that moves one fails the suite
naming the re-diff. The book pages draw their figures
client-side with Observable Plot (`ui/static/ui/charts/mount.js`, reading each
figure's JSON read model from `interface/web/charts.py`) from the `--chart-*`
tokens, so a `needs` blue is one blue everywhere.

django-unfold was read and declined on 2026-09-18 - see the one-chrome spec, in
git history. Seven packaged admin themes and six classless CSS bases were
surveyed and declined on 2026-09-19 - the numbers live in the one-language spec,
in git history. The short version: unfold requires every `ModelAdmin` to inherit
its own, which would put its base class under `OwnedAdmin`.

### The rule for adding one

A dependency earns its place by being cheaper than what it replaces, counted in
packages and in things that can break, not in lines of code saved. Check the
closure before adding it:

```
uv run python -c "import importlib.metadata as m; ..."   # or just: uv tree
```

Precedents already in the tree: `jupyter` and its dataframe and plotting stack
were removed outright on 2026-10-12, taking about 1,560 lines out of the lock
file; `django-extensions` was removed before them because `shell_plus --lab`
bought a conditional in `INSTALLED_APPS` and a coverage pragma. `rules`, `django-guardian` and
`django-organizations` were each read and declined in the 2026-09-18
one-asker-for-permissions plan, in git history. The pattern is
to install it, read it, count it, and write down why not.

## Deploying

A machine with a shell. The CLI imports `service/` directly rather than speaking
HTTP, so running a command against the deployed ledger means `uv run scaffolding
<cmd>` over SSH; a host that gives no shell would mean building a second,
HTTP-shaped CLI, which is a larger project than this whole document.

TLS is terminated by whatever sits in front - the host's edge, or Caddy. "No
reverse proxy" means not maintaining an nginx config, not a Python process owning
certificate renewal.

### The wheel

`make dist` produces the artifact: `dist/scaffolding-<version>-py3-none-any.whl`,
built from committed source (never the working tree, so an uncommitted file
cannot leak in), with file timestamps pinned to the build commit, so the same
source builds the same wheel. The
packaging tests pin the wheel's contents - every static asset, template and
reference table in; no dev dependency, user data or tooling - and
`bin/wheel_smoke.py` installs it into a throwaway venv and boots it before
anything is declared done.

Installing on a machine is `uv tool install dist/scaffolding-<version>-py3-none-any.whl`,
which gives the `scaffolding` command in its own environment. Two settings are
mandatory there, because an installed wheel has no repo layout to fall back on
and must never write into site-packages:

- `SCAFFOLDING_VAR_DIR` - the SQLite ledger and task queue, caches and reports
  (defaults to `var/` only in a checkout);
- `SCAFFOLDING_SECRETS_DIR` - the ARCA certificate and OAuth client files
  (defaults to `etc/secrets/` only in a checkout).

Both go on the encrypted volume. An upgrade is rebuild + `uv tool install` of
the new wheel: the state sits outside the install and is untouched, which is
the point of the decoupling.

There is no index. The wheel file is the distribution channel: proprietary
software for one person's machines, so a PyPI or private index would cost
authentication and publication for no consumer. A second person's machine -
which wants a pinned, signed download rather than a hand-carried file - is the
trigger to revisit, and signed artifacts come with it.

`make release VERSION=x.y.z` is the ritual: the full gate, then the VERSION
bump and its commit, then the wheel from that commit, then the tag. Pushing
that tag wakes CI (`.github/workflows/release.yml`), whose only command is
`make publish`: it re-proves the wheel from the tagged commit (`make dist`,
packaging tests and boot smoke) and attaches it to the tag's GitHub release,
the download point the installing machines pull from. A release is only cut when the gate is green; `make deploy-check`
(`scaffolding check --deploy`) is the deployed machine's own checklist, read
there, because it answers for the local `.env`.

The gate is also enforced per pull request: every PR runs `make check` in CI
(`.github/workflows/check.yml`) on a synced dev env (`make sync` first, since
`pytest`/`ruff`/`mypy` live in the dev extra), so a branch's green check means
what `make check` green means on the author's laptop.

What has to change in `conf/settings.py` before it faces a network, all of it
currently written for a laptop:

- The module docstring, which says "Single machine, single superuser, SQLite. Not
  designed to be deployed." The first three clauses stay true; the last stops
  being.
- `ALLOWED_HOSTS`, hardcoded to `["localhost"]`. The loopback IP was dropped on
  2026-09-28: it is a second origin to Google, and allauth mirrors the request's
  host into `redirect_uri`, so a session started on `127.0.0.1:8000` died at a
  Google refusal naming neither cause nor cure. A 400 here names both.
- `SECRET_KEY`, which has a working insecure default so a fresh clone can run the
  suite. A deployment cannot start on it: `runserver` refuses it unless
  `DEBUG` is on, and `check --deploy` lists it (`scaffolding.security.W001`).
- `STATIC_ROOT` stays set and `collectstatic` stays a deployment step, but the
  server is plain `scaffolding runserver` since 2026-09-19: static comes from the
  apps under `DEBUG` and from nothing at all without it. The old serve
  command's uncollected-statics refusal died with it; the unstyled-admin trap
  it guarded is this bullet now. What serves static in production is the same
  open question as what serves at all, and it belongs to this track.
- `DEBUG`, already defaulting to False, and the HTTPS settings that have no
  reason to exist until now - `SECURE_SSL_REDIRECT`, `SESSION_COOKIE_SECURE`,
  `CSRF_COOKIE_SECURE`, `SECURE_HSTS_SECONDS`. `scaffolding check --deploy` is
  Django's own list and should be the thing that passes, rather than a list
  copied into here.

The SQLite file and `etc/secrets/` are the state. Both are already gitignored and
0600; backup is copying them off an encrypted volume, and there is no other
durable state to lose.

### The sandbox

`sandbox/Dockerfile` (2026-10-11): the wheel from `dist/` on `python:3.14-slim`,
plain `pip`, nothing else. Docker is a throwaway for iterating on the ETL and
for testing an install from scratch, never the deployment. Two layers, so a new
wheel costs seconds (cold build 22 s, dependency change with a warm pip cache
13 s, wheel-only rebuild 2 s): the pinned dependencies from
`sandbox/requirements.txt`, then the wheel with `--no-deps`. The file is
`uv export --locked --no-default-groups --no-emit-project`, written by `make
sandbox` from `uv.lock` and gitignored. It is the only exported requirements
file: `dist/requirements-runtime.txt` was dropped on 2026-10-11, a second export
of the same closure that nothing read. 353 MB. State lives in the named volume
`scaffolding-sandbox` (`/state`). The image's `CMD` is `scaffolding`, which lists the
commands; the runtime options are the caller's, and `make sandbox` is the one
that migrates, seeds and serves.

- `make sandbox` - build and serve on `127.0.0.1:8000`;
- `make sandbox-shell C="scaffolding month"` - any command against the same state;
- `make sandbox-reset` - drop the volume; the next start is a fresh install.

It runs with `DEBUG=true` (static, and no real key needed): a sandbox, not a
deployment check. On its first boot it found a wheel that could not import its
URLconf - `models.Field[...]` subscripts only under the dev-only django-stubs.

## What is deliberately not here

No container orchestration, no reverse proxy of ours, no process supervisor per
user, no message queue, no Redis, no CI-built image (the sandbox image is built
locally and thrown away), and no node.js in the serving path. Each of those
was considered for this design and each lost to the same argument: one or two
users on one machine. (Node is a dev-only prerequisite - `make check` runs the
frontend's functional-core tests with node's built-in runner, nothing node
reaches the deployed site.)

Kernel sandboxing is not a question here: no kernel runs anywhere. The
paragraph that used to live here is preserved in git history, in the 2026-09-18
one-nozzle spec.
