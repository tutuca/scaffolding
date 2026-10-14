# Project management

The general method, independent of the code. Scrum, run on the issue tracker
(GitHub issues, milestones and labels — the same artifacts GitLab had under the
same names).

## Artifacts

- **Milestones** — a two-week period in which a concrete set of tasks is resolved.
- **Issues** — any task, by any member of the team; atomic and independently
  actionable, with acceptance criteria.
- **Labels** — the state of a task (`todo` / `doing` / `done` / `reviewing` /
  `closed`) and its type.

## The issue

- **Title** — concise, communicating the expectation that will be satisfied when
  it is closed. A user story takes the form:
  > As <user> I want <feature> so that <goal>.
- **Detail** — the need it arises from, and how to verify it is complete
  (the definition of done).
- **Labels** — type and state, so the board can be filtered at a glance.

## Lifecycle

```
Open → To Do → Doing → Done → Closed
```

- **Open** — new; a title is enough. Anyone can create one at any time.
- **To Do** — scope and acceptance criteria are clear; assigned to a milestone.
- **Doing** — assigned to a person; a development task has an open merge request.
- **Done** — the work is complete and awaiting review; code review happens here.
  It may go back to **Open** (replanned) or **Doing** (reworked), or on to
  **Closed** once merged into the trunk.
- **Closed** — accepted and merged.

## Priority

Urgency pushes a task up; complexity pushes it down. What sits at the top of the
backlog is what is both urgent enough and simple enough to act on. Those are the
tasks that enter the active milestone.

## Ceremonies

- **Weekly scrum** — progress, blockers, and needs.
- **Sprint planning** (every two weeks) — the scope of the milestone.
- **Retrospective** (every other planning) — how the team works, not what it
  built.

These are the formal decision spaces. Day-to-day traffic lives in the team chat,
so decisions still get made — and recorded — between ceremonies.

## Bugs

A bug is behaviour that is affecting users in their normal use of the system —
not a feature request or refactor in disguise. Classify it and notify the
reporter.

**Priority levels**

- **Blocker** — stops use of the application; drop everything and fix.
- **Major** — hinders but does not block; schedule for this or the next sprint.
- **Minor** — a quirk, not a functional break; next sprint.
- **Not-a-bug** — expected-but-undefined behaviour or miscommunication; turn it
  into a requirement.

**Writing the report** — title of the form `Location: short description (env)`,
then a description, steps to reproduce, expected vs actual result, browser/error
details and a screenshot. One bug per report. Report facts; keep assumptions
explicit and separate.

## Git mechanics

The branch-and-merge mechanics that carry this method live in
[`WORKFLOW.md`](WORKFLOW.md).

---

The sources this method draws on: [`REFERENCES.md`](REFERENCES.md).
