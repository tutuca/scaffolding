# Admin — deployment

## Serving

`uv run scaffolding runserver` is Django's own dev server, nothing wrapped.
Production needs no docker. Two rules protect a machine that faces the network:

- `conf/serving.py` refuses to serve with the default `SECRET_KEY` unless `DEBUG`
  is on.
- `scaffolding check --deploy` lists the deploy-time checks (`data/checks.py`).

Before trusting a deployment, run `scaffolding check --deploy` and fix what it
lists.

## The wheel

The distribution artifact is a wheel built from committed source (`make package` /
`make dist`). The installed machine sets:

- `SCAFFOLDING_VAR_DIR` — the database and runtime state.
- `SCAFFOLDING_SECRETS_DIR` — secrets (mode 0600, gitignored).

See [Developer — deployment](../developer/deployment.md) for the release mechanics.
