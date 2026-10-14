# Infrastructure

What serves, what ships, and how to change either.

## Serving

`uv run scaffolding runserver` is Django's own dev server, nothing wrapped.
`conf/serving.py` refuses to serve with the default `SECRET_KEY` unless `DEBUG` is
on, and `data/checks.py` lists the same rule under `scaffolding check --deploy`.
Production needs no docker.

## The wheel

The distribution artifact is a wheel built from **committed source** — `make package`
runs `git archive HEAD`, never the working tree, so an untracked file cannot leak
into what gets installed. `make dist` builds it and proves it boots in a throwaway
venv (`bin/wheel_smoke.py`). A machine that installs it sets:

- `SCAFFOLDING_VAR_DIR` — where the database and runtime state live.
- `SCAFFOLDING_SECRETS_DIR` — where secrets live (mode 0600, gitignored).

## The sandbox

`make sandbox` runs that wheel in docker from an empty named volume
(`make sandbox-reset` starts over): the quick way to test an install. `sandbox/`
holds the Dockerfile; its `requirements.txt` is generated from `uv.lock`.

## Adding a dependency

Add it to `pyproject.toml`, then `uv sync` and regenerate `uv.lock` and
`sandbox/requirements.txt` (`make sandbox/requirements.txt`). Keep the wheel lean:
dev-only tools go in `[project.optional-dependencies].dev`.
