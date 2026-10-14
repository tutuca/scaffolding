# Developer — setup

## Prerequisites

- Python 3.14 (`pyproject.toml` requires `>=3.14`)
- [`uv`](https://docs.astral.sh/uv/) — the package manager
- `make` and `node` — for the Makefile and the frontend's lint/test

## Install

```bash
uv sync --extra dev        # creates .venv and installs the project + dev tools
make configure             # creates var/ and etc/ trees
cp .env.example .env       # then set SECRET_KEY
```

Generate a secret key with:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Set `DEBUG=true` in `.env` for local work. `conf/serving.py` refuses to serve with
the default key unless `DEBUG` is on, so a machine that faces the network needs a
real key and `DEBUG=false`.

## First run

```bash
scaffolding migrate                                  # the app database
scaffolding migrate --database tasks django_tasks_database   # the task queue
scaffolding createsuperuser                          # the first account
scaffolding runserver                                # http://localhost:8000
```

Log in at `/login/`, create a `Tenant` in the admin, add yourself as a member, and
set it as your active tenant. `/notes/` then works end to end.
