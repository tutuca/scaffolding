# Development workflow

Status: decided 2026-10-13 (three drafts weighed in the first pass; C chosen).

Constraints this honors: few tools, GitHub only, light trunk-based (not gitflow),
agentic-friendly, brevity + clarity. Planning stays in `./docs`; GitHub issues
orchestrate branches/PRs and hold deferred discussions.

## Branching

- `master` is the trunk; it is always releasable.
- One short-lived branch per issue. Work merges by pull request, **squash**, then the
  branch is deleted. No long-lived branches.
- Cleanup: `basic-background-tasks`, `access-and-the-profile-page`, `ci-check-matrix`,
  `ci-make-check` are stale — merge what matters and delete them. The
  `snapshot/pre-master-data` tag never wakes CI (only `v*` matches); drop it.

## Status labels

Five labels; `make labels` creates them. The first three are the state machine,
the last two are optional overlays.

| label | hard/soft | means |
|---|---|---|
| `todo` | hard | queued, not started (new issues start here) |
| `doing` | hard | a branch/PR is open for it |
| `done` | hard | shipped and merged |
| `reviewing` | soft | a PR is up and needs eyes — coexists with `doing` |
| `closed` | soft | closed without shipping (tabled / won't-do) |

Flow: `todo` → `doing` → `done`, then close. `closed` = closed without shipping
(deferred, parked, won't-do). `reviewing` overlays `doing`, never a stop.

## Issues

- One issue per unit of work. The template starts it at `todo`.
- An issue orchestrates its branch and PR (`Closes #n` links them), and stores the
  discussion that arises in review but is deferred or tabled until a better decision.
- The issue is a pointer and the changelog source; the doc is what agents and humans read.

## Templates

Brief on purpose — fields are the example, no instruction prose.

- `.github/ISSUE_TEMPLATE/task.md` — `What` / `Why` / `Done when`.
- `.github/PULL_REQUEST_TEMPLATE.md` — `Closes #<n>`; the PR **title** becomes the
  changelog line, so write it as one imperative sentence.

## Release cycle

- `make release VERSION=x.y.z` gates → bumps `VERSION` → commits → builds the wheel → tags `v*`.
- Pushing the tag wakes `.github/workflows/release.yml`, which re-proves the wheel and
  runs `make publish` — uploads it and **auto-generates the release notes from the merged
  PR titles** (`gh release create --generate-notes`). No changelog tool: the GitHub
  release is the changelog.
- PR titles are the only input to the changelog, so squash-merge one PR = one line.

## Planning

- Roadmap, plans, specs, reviews stay in `docs/` (`PLANNING.md`, `superpowers/`,
  `reviews/`).
- The running local checklist stays `var/scratchpad/NEXT.md` (gitignored; never in the repo).
