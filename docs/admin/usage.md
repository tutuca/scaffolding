# Admin — usage

## The admin interface

`/admin/` is the data-entry surface for everything a command does not cover:

- **Tenants** — the workspaces, with their memberships inline.
- **Memberships** — a user's role on a tenant.
- **Users** — accounts (email, name, active tenant, staff/superuser flags).
- **Notes** — the sample domain's rows.

## Role-scoped access

What a role sees and may do comes from `data/visibility.py`, answered by
`data/backends.RoleBackend`. Minimal by default: a resource absent from a role's
row is invisible to it.

A superuser bypasses the role check entirely — that is the escape hatch that makes
the admin usable before any tenant exists, and the reason `is_superuser` should be
reserved for the person who administers the installation.

## The command line

The same data is reachable from the CLI, which is idempotent and scriptable:

```bash
scaffolding notes list
scaffolding notes add --title "…" --body "…"
```

Each command acts on one tenant's rows: `--tenant <slug>`, or the only registered
one.
