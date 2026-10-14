# Developer — deployment

The distribution artifact is a wheel built from committed source.

## Build

```bash
make package   # git archive HEAD -> uv build --wheel
make dist      # package + prove it boots in a throwaway venv
```

`make package` runs `git archive HEAD`, never the working tree, so an untracked
file cannot leak into what gets installed.

## Release

```bash
make release VERSION=x.y.z
```

This gates (`make check`), bumps `VERSION`, commits the bump, builds the wheel, and
tags `vX.Y.Z`. Pushing the tag wakes CI (`.github/workflows/release.yml`), which
re-proves the wheel and runs `make publish` to attach it to the tag's GitHub
release.

## The installed machine

The machine that installs the wheel sets two environment variables, because its
state cannot live inside `site-packages` (an upgrade would wipe it):

- `SCAFFOLDING_VAR_DIR` — the database and runtime state.
- `SCAFFOLDING_SECRETS_DIR` — secrets (mode 0600, gitignored).

Then it runs `scaffolding migrate` (both databases) and serves. Before trusting a
machine that faces the network, run `scaffolding check --deploy` and fix what it
lists.
