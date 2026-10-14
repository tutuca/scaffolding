# Developer — maintenance

## Dependencies

Add a dependency to `pyproject.toml`, then:

```bash
uv sync
make sandbox/requirements.txt   # regenerates sandbox/requirements.txt from uv.lock
```

Keep the wheel lean: dev-only tools go in `[project.optional-dependencies].dev`.

## Migrations

`make migrations` runs `scaffolding makemigrations --check --dry-run`. A model
changed without a migration is a green suite and a broken clone — commit the
migration with the change. After adding a model:

```bash
scaffolding makemigrations data
scaffolding migrate
scaffolding migrate --database tasks django_tasks_database
```

## The frontend

The frontend is server-rendered templates plus a vanilla-JS core with no build and
no dependencies. `bin/js.mjs` is the lint/format (`make lint-js` / `make format-js`),
and `make test-js` runs the node tests with V8 coverage. There is no
`node_modules`; `node` is a dev prerequisite only.

## Housekeeping

- The task queue keeps its own SQLite; `make sandbox` proves an install from an
  empty volume.
- `make sandbox-reset` drops that volume and starts over.
