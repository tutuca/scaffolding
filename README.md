# scaffolding

A multi-tenant Django application scaffold: the conventions and infrastructure of
[`tutuca/invoices`](https://github.com/tutuca/invoices) with the invoice-specific
domains removed and a small sample domain (`Note`) in their place.

One machine, SQLite, plain Django authentication, and a layered architecture —
`conf` / `data` / `service` / `interface` / `ui` — described in
[`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## What it demonstrates

The sample domain is a single `Note` (title + body) that flows through every layer
unchanged, so each layer is a template to copy:

- **CLI** — `scaffolding notes list` / `scaffolding notes add` (`interface/cli/`).
- **HTTP** — the versioned API under `/api/v1.0/` (`interface/api/`, `service/views.py`),
  Swagger at `/api/schema/swagger-ui/`.
- **Admin** — `/admin/` (`data/admin/`), role-scoped per tenant.
- **Web** — `/` and `/notes/` (`interface/web/`).

All four call the same use cases in `service/domain/notes/`, so it makes no
difference which you reach for.

## Quick start

```bash
uv sync --extra dev
make configure               # create var/ and etc/ trees
cp .env.example .env         # set SECRET_KEY (and DEBUG for local work)
scaffolding migrate
scaffolding migrate --database tasks django_tasks_database
scaffolding createsuperuser
scaffolding runserver
```

Log in at `/login/` with the superuser's email and password, create a `Tenant` in
the admin, add yourself as a member, and set it as your active tenant. Then `/notes/`
works end to end.

`make check` runs ruff, mypy, the frontend's lint/test, and pytest with coverage.

## Documentation

| Read | For |
|------|-----|
| [`docs/VALUES.md`](docs/VALUES.md) | Engineering and working values. |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Where logic lives, and why. Binding. |
| [`docs/developer/`](docs/developer/index.md) | Developer guide: setup, usage, deployment, maintenance. |
| [`docs/admin/`](docs/admin/index.md) | Admin guide: setup, usage, deployment, maintenance. |
| [`docs/user/`](docs/user/index.md) | User guide: setup and usage. |
| [`docs/PROJECT-MANAGEMENT.md`](docs/PROJECT-MANAGEMENT.md) | Scrum, issues, priorities, ceremonies, bug triage. |
| [`docs/TESTING.md`](docs/TESTING.md) | Test conventions. |
| [`docs/WORKFLOW.md`](docs/WORKFLOW.md) | Trunk-based workflow. |
| [`docs/INFRASTRUCTURE.md`](docs/INFRASTRUCTURE.md) | Serving, the wheel, the sandbox. |

## Layout

```
src/scaffolding/
  conf/                     settings (django-environ), urls (versioned api/v{X.Y}/)
  data/                     the one Django app
    models/<entity>.py      one model per file; every write is a mutator here
    serializers/ admin/     one file per entity
    management/commands/    seeding is data-layer work
  service/
    base.py                 the CRUD viewset factory
    views.py                VIEWS registry -> the API router
    commands.py             COMMANDS registry -> what the CLI exposes
    domain/notes/           schemas · use_cases (the sample domain)
  interface/
    api/                    router, versioned urls
    cli/                    management commands
    adapter/                ports (Protocols) and adapters
    tasks/                  django.tasks thin shells
    web/                    server-rendered pages
  ui/                       templates + static (tokens, components, grid, table)
var/                        gitignored: the database and runtime state
tests/                      mirrors src; recipes/ per model
```

## Tenancy

A `Tenant` is the unit of isolation; every owned row (like `Note`) points at one.
A `Membership` is the edge between a user and a tenant carrying a `Role`
(`OWNER`, `EDITOR`, `VIEWER`), and `data/visibility.py` is the single table that
says what each role may do. See `docs/ARCHITECTURE.md`.
