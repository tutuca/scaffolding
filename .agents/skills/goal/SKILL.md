---
name: goal
description: Use when the user explicitly requests a persistent goal or hands over a long multi-step objective needing a durable checklist across turns. Not for a single-step task.
compatibility: Works inline anywhere; a persistent goal needs a harness exposing create_goal/get_goal/update_goal, otherwise run the checklist inline.
---

# GOAL

A GOAL is one measurable finished state chased over many steps, with the work
written down so a later run never redoes it and the user can always see where it
stands. The GOAL-loop template (`./GOAL-template.md` when it is in the
tree) is the shape; this is how to drive it with the goal tools.

To run the loop through delegated subagents instead of doing each item inline -
routing a lightweight model to mechanical sweeps, a stronger model to the plan,
and an image-capable model to screenshot checks - use the `goal-loop` skill, which
builds on this one and keeps all of its rules.

## Why a loop

A single turn holds a small task end to end. A big one - "remove matplotlib",
"port every chart", "sweep the tests" - cannot: it outruns one turn, and an agent
trying to hold it all in its head loses the thread and re-does finished work.
Putting the finish line in the goal and the item list on disk lets any run pick
it up cold.

## Setting one up

1. **Write the GOAL as a finished state you can check.** "Every chart draws with
   Observable Plot and `make check` is green", not "work on the charts". If you
   cannot say how you would know it is done, it is not a GOAL yet - ask the user
   what done looks like. This sentence becomes the `create_goal` objective, so it
   must stand alone, with no reference to the conversation that produced it.
2. **Map the work and cut it into items.** Read the tree first and name the
   concrete pieces (files, figures, tests). One item is one thing finished fully
   and checked before the next starts. A GOAL whose items you cannot list is
   still a wish - spend the reading time up front.
3. **Create a persistent goal only when explicitly requested by the user or
   higher-priority instructions.** A multi-step task alone, or a request to edit
   this skill, does not authorize `create_goal`; use the checklist inline instead.
   Goal tools are `create_goal`, `get_goal`, and `update_goal`, exposed by the
   current harness; read the goal-loop reference file or the harness's tool
   reference for their exact call shape. Read the goal before creating or
   updating: an unfinished goal cannot be replaced. Call `create_goal` with the
   measurable finished state as the objective when authorized; include any
   budget or round-limit field only if explicitly requested. Use the actual
   returned fields; do not assume an id or revision exists or pass one to
   `update_goal` unless the tool requires it.
4. **Write the state file where no other goal can reach it -
   `tmp/goals/<slug>/LOOP-STATE.md`.** The goal carries the finish line; the file
   carries what the goal cannot: the item list, the checks that prove each item,
   and anything the next run must know. Keep it short and readable.

   `<slug>` is two or three words out of the objective - `ipc-cross-reference`,
   `prestamos-page` - and the head of the file names the goal, so a run that comes
   back cold finds its own file instead of guessing which one is its:

   ```
   # LOOP-STATE - <the goal in six words>

   Objective: <measurable finished state>. Read this first every run.
   Goal: <returned identifier if present, otherwise active or inline>.
   ```

   One file per goal and one directory per loop, with the loop's own scratch -
   probes, crops, logs - beside it. The old shape was one `tmp/LOOP-STATE.md` for
   the whole repo, and when two loops ran at once the slower one lost its item
   list to the faster one's write. A loop already running under the old name
   keeps it until it reaches a natural break, then moves into the directory and
   says so in the file.

## Running it

- **One item at a time**, finished and checked before the next. The loop is what
  keeps a long objective honest.
- **Match the patterns already in the tree.** A new item that invents its own
  convention is a future refactor; the existing files are the spec.
- **Prove each item before marking it done** - run the tests, render the page,
  read the file back. Confidence is not evidence. If the check fails, fix it and
  check again; after three tries, log it blocked and move on rather than grinding.
- **A decision only the user can make** - spending money, deleting something, a
  design call the code cannot settle - goes on a "needs me" list. Do not guess it,
  and do not let it stall the whole loop: note it and take the next item.
- **Update your goal's state file after each item**, not at the end. A run that
  dies mid-item should leave the next one a true picture.

## Several loops at once

More than one GOAL can be running in this repo at the same time - another
session, another agent, often the same afternoon. Each checklist has its own
state file under `tmp/goals/<slug>/`. Goal tools address the current thread's
goal, not a state-file path: separate worktrees or checklists do not create
independent goal-tool state. Use separate threads for independently managed
persistent goals, and keep status updates with each thread's controller.
What the loops share is the tree, and the tree is where one loop takes another's
work by accident.

- **Stage what you changed, by path** - `git add src/scaffolding/ui tests/js`,
  never `git add -A` or `git commit -a`. The other loop's half-finished edit is
  sitting in the tree, and a sweep commits it under your message. Read
  `git status` before staging, and leave what is not yours dirty.
- **Never reach for the repo-wide undo** - `git checkout .`, `git reset --hard`,
  `git stash`. Those are not "clean up after myself" here; they are "delete
  someone else's item".
- **A red test may not be yours.** Read the failure before fixing it and check
  `git diff <the file>`: if the change belongs to another loop, leave it alone,
  take a different item, and let its own loop finish.
- **A file you both need is a scheduling problem, not a merge.** If your next
  item wants a file another loop has dirty, take a different item and write down
  in your state file why you skipped it.
- A loop that wants the tree to itself can take a worktree
  (`git worktree add .agents/worktrees/<slug>`) and run there, where `tmp/` and
  the index are its own. The same rules still apply inside it, with less to
  share.

## Stopping

Logging an item as blocked does not finish it. Continue with independent work.
Mark the goal complete only when its objective is achieved and no required
work remains: gather evidence, read the goal, then complete it via
`update_goal`. Report any final budget or usage the tool returns when
completing a budgeted goal. For inline work, report completion without calling
goal tools.

An active goal remains active while useful work remains. Set `paused` only at
the user's explicit request, then report that status and stop. Set `blocked`
only after the same impasse has recurred for at least three consecutive goal
turns and no meaningful progress is possible without user input or an external
change. Three failed attempts on one item do not meet that threshold. Budget
limits and resumption are controlled by the user or system, not `update_goal`.
After a blocked goal resumes, count a fresh sequence of blocked turns.

When the goal is complete, rename its directory to `<slug>-done-<date>` and say
so at the top of the file: `ls tmp/goals/` is then the list of loops still
running, which is what the next agent and the user both read it for.

Then give the short report: what got done, what is blocked, what needs the user's
call.
