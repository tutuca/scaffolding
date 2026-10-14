# Development workflow

Status: decided in `tutuca/invoices` (three drafts weighed; the light trunk-based one
chosen), generalized here.

Constraints this honors: few tools, GitHub only, light trunk-based (not gitflow),
agentic-friendly, brevity and clarity. Planning stays in `docs/`; GitHub issues
orchestrate branches and PRs and hold deferred discussions.

## Branching

- `master` is the trunk; it is always releasable.
- One short-lived branch per issue. Work merges by pull request, **squash**, then the
  branch is deleted. No long-lived branches.

## Status labels

Five labels; `make labels` creates them. The first three are the state machine, the
last two are optional overlays.

| label | hard/soft | means |
|---|---|---|
| `todo` | hard | queued, not started (new issues start here) |
| `doing` | hard | a branch/PR is open for it |
| `done` | hard | shipped and merged |
| `reviewing` | soft | a PR is up and needs eyes — coexists with `doing` |
| `closed` | soft | closed without shipping (tabled / won't-do) |

Flow: `todo` → `doing` → `done`, then close. `reviewing` overlays `doing`, never a
stop. `closed` = closed without shipping.

## Issues

- One issue per unit of work. The template starts it at `todo`.
- An issue orchestrates its branch and PR (`Closes #n` links them) and holds the
  discussion that arises in review but is deferred.
- The issue is the changelog source: its merged PR title is the line.

## Templates

Brief on purpose — fields are the example, no instruction prose.

- `.github/ISSUE_TEMPLATE/task.md` — `What` / `Why` / `Done when`.
- `.github/PULL_REQUEST_TEMPLATE.md` — `Closes #<n>`; the PR **title** becomes the
  changelog line, so write it as one imperative sentence.

## Release cycle

- `make release VERSION=x.y.z` gates → bumps `VERSION` → commits → builds the wheel → tags `v*`.
- Pushing the tag wakes `.github/workflows/release.yml`, which re-proves the wheel and
  runs `make publish` — it uploads the wheel and **auto-generates the release notes from
  the merged PR titles** (`gh release create --generate-notes`). No changelog tool: the
  GitHub release is the changelog.
- PR titles are the only input to the changelog, so squash-merge one PR = one line.

## Planning

- Roadmap, plans, specs and reviews stay in `docs/`; the method that produces them is
  [`PROJECT-MANAGEMENT.md`](PROJECT-MANAGEMENT.md).
- The running local checklist stays `var/scratchpad/NEXT.md` (gitignored; never in the repo).
