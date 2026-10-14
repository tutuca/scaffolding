# User — usage

The sample domain is a note, reachable from the web page and the API.

## On the web

Browse to `/notes/`:

- Add a note: type a title (required) and a body, then **Add note**.
- Read: the list shows each note's title, last-updated date, and body.

## On the command line

```bash
scaffolding notes list
scaffolding notes add --title "…" --body "…"
```

## What you can do

Your role decides what you may do, from the single table in `data/visibility.py`:

- `VIEWER` — read notes.
- `EDITOR` — read and write notes.
- `OWNER` — the above, plus manage the tenant and its memberships.
