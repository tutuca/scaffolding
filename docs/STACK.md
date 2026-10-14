# Stack

The current stack, grouped by the layers it serves, and the reason for each choice.
The layers themselves are defined in [`ARCHITECTURE.md`](ARCHITECTURE.md).

## Language & package management

- **Python 3.14** — `requires-python = ">=3.14"`. Deferred annotations (PEP 649) let
  forward references work without `from __future__ import annotations`.
- **uv** — fast resolution, a committed `uv.lock`, and a repo-local cache
  (`Makefile` sets `UV_CACHE_DIR`), so installs and builds are repeatable offline.

## Data

- **SQLite** (via `django-environ`'s `env.db()`) — one machine, one user; the file is
  itself sensitive data, kept on an encrypted volume. No Postgres, no fleet: "SQLite
  via `env.db()`. No structlog, CORS, Postgres." (invoices `ARCHITECTURE.md`).
- **A second SQLite** for the task queue — worker rows never touch or bloat the app
  database (routed by `conf/router.py`).

## Application

- **Django** — it makes the design decisions (ORM, admin, forms); we lean on them
  rather than re-deciding them. `Model` is the contract with the data.
- **Django REST Framework + drf-spectacular** — serializers are the wire contract; the
  OpenAPI schema is generated from them, so the API has one source of truth.
- **django-environ** — Twelve-Factor configuration: every secret or machine-specific
  value comes from the environment or `.env`.
- **django-tasks-db** — a database-backed queue on its own SQLite; the event shell
  needs no external broker.

## Interface (UI)

- **Django templates + vanilla JS (ES modules) + custom CSS tokens** — no build and no
  vendored libraries. The JS functional core is pure and runs under `node --test`;
  the served site ships no node. (The bigpear/olmo stack's Webpack + Sass + Bulma
  build step is gone for the same reason.)

## Quality

- **ruff** — one tool for lint and format (`E402`, `PLC0415`, `I`, `ANN`, `E722`,
  `BLE`, `DJ`), replacing flake8/black/isort.
- **mypy + django-stubs** — typing as a readability aid, not formal verification.
- **pytest + pytest-django + model-bakery** — contract-first tests, one factory per
  model.
- **node --test** — the frontend core's runner; no dependency and no build.

## Delivery

- **GitHub Actions** — the pull-request gate (eight checks) and the release workflow.
- **setuptools wheel + `gh release`** — the wheel is the distribution artifact; the
  GitHub release is the changelog (no changelog tool).
- **Docker** — only as the throwaway sandbox; production needs no docker.

## Former stack

The scaffold descends from the bigpear/olmo stack — PostgreSQL, Wagtail,
ElasticSearch, Webpack, Sass, Bulma, Docker (as the deployment unit) — documented in
`bigpear/self/docs/desarrollo/tecnologias.md`. It was dropped here for the reasons
above: a single-machine tool needs neither a fleet database nor a frontend build step.
