# scaffolding

This repo is the archive of my financial organization; the Django app is one tool inside
it. Human actions (contador, ARCA paperwork, Acme) are tracked in `var/scratchpad/NEXT.md`
(local and gitignored: it never enters the repo) - start there each session.

Read `docs/ARCHITECTURE.md` before touching code; its "Code principles" section is
binding.

The look is one language: read `docs/DESIGN.md` before touching
`src/scaffolding/ui/` or any template. After changing what a page looks like, run
`uv run python bin/ui_shot.py` against a running
server and look at `var/shots/` before claiming done. The checkable rules live
in `tests/scaffolding/ui/`.

- `var/documents/` and `etc/secrets/` are gitignored and sensitive; never commit or print them.
- `uv run scaffolding runserver` runs the tool - Django's own dev server, nothing
  wrapped; the books under `/notebooks/` are server-rendered pages.
  `uv run scaffolding <cmd>` for other management commands; `uv run pytest` for tests. Read `docs/INFRASTRUCTURE.md`
  before adding a dependency or changing what serves.
- Identity: Google is the only gateway. `scaffolding login` authenticates a terminal
  through a loopback consent, and `scaffolding register --cuit <cuit>`
  claims a CUIT and makes you its owner. Commands act on one taxpayer's books -
  `--taxpayer <cuit>`, or the only registered one. See `docs/CERTIFICATE.md` for
  the ARCA certificate, which is uploaded to a taxpayer rather than configured.
- Defaults never touch the network (`ARCA_AUTHORIZER=manual`, `ARCA_RATE_PROVIDER=manual`).
- The wheel is the distribution artifact: `make dist` builds it from committed
  source and proves it boots; `make release VERSION=x.y.z` gates, bumps, builds
  and tags; the pushed tag wakes CI (`.github/workflows/release.yml`), which
  runs `make publish` and attaches the wheel to the tag's GitHub release. The
  machine it installs on sets `SCAFFOLDING_VAR_DIR` and
  `SCAFFOLDING_SECRETS_DIR` (docs/INFRASTRUCTURE.md, "The wheel").
- `make sandbox` runs that wheel in docker from an empty volume (`make sandbox-reset`
  starts over): the quick way to test an install or an ETL change. Production
  needs no docker (docs/INFRASTRUCTURE.md, "The sandbox").

## Workflow

Light trunk-based (see `docs/WORKFLOW.md`): one short-lived branch per GitHub issue,
squash-merged by pull request and deleted - `master` is always releasable. Five status
labels track an issue: `todo` → `doing` → `done` (hard), plus soft `reviewing` and
`closed`; new issues start at `todo`. Release notes generate themselves from merged PR
titles, so a PR title is one imperative sentence. Planning lives in `docs/`; the local
running checklist stays `var/scratchpad/NEXT.md`.
