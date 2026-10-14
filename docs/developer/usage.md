# Developer — usage

## The dev loop

```bash
make run           # scaffolding runserver (autoreload)
make test          # pytest with coverage
make test-js       # node --test for the frontend core
make lint          # ruff check
make format        # ruff format + fix
make typecheck     # mypy
make check         # all of the above, plus migrations and the frontend lint
```

## Four ways in, one domain

The sample domain is a `Note`. The CLI, the API, the admin and the web page all
call the same use cases in `service/domain/notes/`:

```bash
scaffolding notes list
scaffolding notes add --title "Hello" --body "World"
```

- API: `GET/POST /api/v1.0/notes/`, Swagger at `/api/schema/swagger-ui/`.
- Admin: `/admin/` → Notes.
- Web: `/notes/`.

## Adding a model

The sample domain is a template to copy. To add an owned model:

1. `data/models/<entity>.py` — the model (inherit `OwnedModel, TimeStampedModel`).
2. Add it to `data/models/__init__.py`.
3. `data/admin/` — a row in `plain.py`, or a module of its own.
4. `data/serializers/__init__.py` — a row in `PLAIN`.
5. `service/views.py` — a row in `RESOURCES`.
6. `service/domain/<entity>/use_cases.py` — the business rules.
7. `interface/` — a CLI command, and (if needed) a web view.
8. `scaffolding makemigrations data` — the migration.

`test_conventions.py` and `test_docs_match_code.py` fail until each step is done,
so the suite is the checklist.
