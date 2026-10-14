# scaffolding

This repo is a Django application scaffold: the conventions of `tutuca/invoices`,
generalized. The Django app is a multi-tenant skeleton with a sample domain
(`Note`) meant to be copied and renamed.

Read `docs/ARCHITECTURE.md` before touching code; its "Code principles" section is
binding.

The look is one language: read `docs/DESIGN.md` before touching
`src/scaffolding/ui/` or any template. After changing what a page looks like, run
`uv run python bin/ui_shot.py` against a running server and look at `var/shots/`
before claiming done. The checkable rules live in `tests/scaffolding/ui/`.

- `var/` and `etc/secrets/` are gitignored and sensitive; never commit or print them.
- `uv run scaffolding runserver` runs the tool - Django's own dev server, nothing
  wrapped. `uv run scaffolding <cmd>` for other management commands; `uv run pytest`
  for tests. Read `docs/INFRASTRUCTURE.md` before adding a dependency or changing
  what serves.
- Identity: plain Django authentication. `scaffolding createsuperuser` makes the
  first account; members are added through the admin's `Membership` or a tenant's
  inline. Commands act on one tenant's rows - `--tenant <slug>`, or the only
  registered one.
- The wheel is the distribution artifact: `make dist` builds it from committed
  source and proves it boots; `make release VERSION=x.y.z` gates, bumps, builds and
  tags; the pushed tag wakes CI (`.github/workflows/release.yml`), which runs
  `make publish` and attaches the wheel to the tag's GitHub release. The machine it
  installs on sets `SCAFFOLDING_VAR_DIR` and `SCAFFOLDING_SECRETS_DIR`
  (docs/INFRASTRUCTURE.md, "The wheel").
- `make sandbox` runs that wheel in docker from an empty volume (`make sandbox-reset`
  starts over): the quick way to test an install. Production needs no docker
  (docs/INFRASTRUCTURE.md, "The sandbox").

## Workflow

Light trunk-based (see `docs/WORKFLOW.md`): one short-lived branch per GitHub issue,
squash-merged by pull request and deleted - `master` is always releasable. Five status
labels track an issue: `todo` → `doing` → `done` (hard), plus soft `reviewing` and
`closed`; new issues start at `todo`. Release notes generate themselves from merged PR
titles, so a PR title is one imperative sentence. Planning lives in `docs/`.
