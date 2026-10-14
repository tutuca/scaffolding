# Infrastructure

What serves, what ships, and how to change either.

## Serving

`uv run scaffolding runserver` is Django's own dev server, nothing wrapped.
`conf/serving.py` refuses to serve with the default `SECRET_KEY` unless `DEBUG` is
on, and `data/checks.py` lists the same rule under `scaffolding check --deploy`.
Production needs no docker.

## Background tasks

`interface/tasks` (see `docs/ARCHITECTURE.md`) runs on `django-tasks-db` (`TASKS`
in `conf/settings.py`): an enqueued task is a row on the `tasks` database - a
second SQLite beside the ledger, routed by `conf/router.py` - and
`scaffolding db_worker` runs it. That worker is the one extra process this
document otherwise has no use for; without it running, tasks queue and wait.
`scaffolding migrate --database tasks django_tasks_database` builds the queue's
table (or `make migrate`, which does both databases). The contract holds: task
arguments and return values are JSON (enforced by `test_conventions.py`), so a
task that needs a `date` or `Decimal` bridges them to strings at the boundary.

The queue is not only process state: a finished row keeps its kwargs and return
value, so treat it like the ledger beside it. `prune_tasks`
(`interface/tasks/queue.py`) deletes results finished over a week ago and
re-enqueues itself a week out. Nothing starts the cycle for you: once per
install, after migrating the `tasks` database, seed it by hand -

```sh
scaffolding shell -c "from scaffolding.interface.tasks import prune_tasks; prune_tasks.enqueue()"
```

Seeding twice is harmless; a duplicate chain dies out on its own. Cron-style
scheduling that would make this automatic is issue #4.

Enqueueing commits immediately to the separate queue database, even inside a
ledger transaction: a task that must run after the ledger commits has to be
deferred with `transaction.on_commit(partial(task.enqueue, ...), using="default")`
- neither Django nor this backend supplies that guarantee.

## The wheel

The distribution artifact is a wheel built from **committed source** — `make package`
runs `git archive HEAD`, never the working tree, so an untracked file cannot leak
into what gets installed. `make dist` builds it and proves it boots in a throwaway
venv (`bin/wheel_smoke.py`). A machine that installs it sets:

- `SCAFFOLDING_VAR_DIR` — where the database and runtime state live.
- `SCAFFOLDING_SECRETS_DIR` — where secrets live (mode 0600, gitignored).

## The sandbox

`make sandbox` runs that wheel in docker from an empty named volume
(`make sandbox-reset` starts over): the quick way to test an install. `sandbox/`
holds the Dockerfile; its `requirements.txt` is generated from `uv.lock`.

## Adding a dependency

Add it to `pyproject.toml`, then `uv sync` and regenerate `uv.lock` and
`sandbox/requirements.txt` (`make sandbox/requirements.txt`). Keep the wheel lean:
dev-only tools go in `[project.optional-dependencies].dev`.
