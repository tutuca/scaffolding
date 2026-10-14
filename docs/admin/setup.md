# Admin — setup

The first-time setup of an installation, from the administrator's side.

## Install

```bash
uv sync --extra dev
make configure
cp .env.example .env       # set SECRET_KEY; DEBUG=true locally
scaffolding migrate
scaffolding migrate --database tasks django_tasks_database
scaffolding createsuperuser
scaffolding runserver
```

## First tenant and members

1. Log in at `/login/` with the superuser account.
2. Open `/admin/` → **Tenants** → Add: give it a name (its slug is derived from the
   name, or set it).
3. Open the tenant → **Memberships** inline → add a user with a role:
   - `OWNER` — administers the tenant and its memberships.
   - `EDITOR` — works on the tenant's rows.
   - `VIEWER` — reads only.
4. Set the user's **active tenant**: `/admin/` → **Users** → the user → Person →
   active tenant. A user with no active tenant cannot act on any rows.

`data/visibility.py` is the single table that says what each role may do; the admin
honors it automatically through `data/backends.py`.
