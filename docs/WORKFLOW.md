# Development workflow

Light trunk-based: one short-lived branch per issue, squash-merged by pull request
and deleted. `master` is always releasable.

## Labels

Five status labels track an issue: `todo` → `doing` → `done` (hard), plus soft
`reviewing` and `closed`. New issues start at `todo`. `make labels` creates them.

## A change, end to end

1. Branch from `master`: `git switch -c <issue>-<slug>`.
2. Implement, then gate: `make check` (format, lint, typecheck, migrations, JS tests,
   Python tests).
3. Open a PR with a title that is one imperative sentence — release notes generate
   themselves from merged PR titles.
4. Squash-merge and delete the branch.

## Releasing

`make release VERSION=x.y.z` gates, bumps `VERSION`, builds the wheel, and tags.
The pushed tag wakes CI (`.github/workflows/release.yml`), which re-proves the wheel
and attaches it to the tag's GitHub release.
