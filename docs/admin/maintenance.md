# Admin — maintenance

## Accounts

- The first account is made with `scaffolding createsuperuser`.
- To reset a user's password, use the admin (or `scaffolding changepassword`).
- A user with no `active_tenant` can log in but cannot act on rows; set it in
  `/admin/` → Users → the user.

## Migrations

```bash
scaffolding migrate
scaffolding migrate --database tasks django_tasks_database
```

`make migrations` checks that no model change is missing its migration.

## Secrets

`etc/secrets/` and `var/` are gitignored and sensitive — never commit or print
them. Keep the whole installation on an encrypted volume.
