---
name: goal-loop
description: Use for a long multi-step objective that needs delegated subagents with per-part model selection, building on the goal skill. Not for a single-step task.
compatibility: Requires git and a harness exposing goal tools and subagents; harness-specific model routing and spawn/image/goal-tool shapes live in references/. Runs on DeepSeek Harness, Claude Code, or Codex.
---

# GOAL-LOOP

Read [goal](../goal/SKILL.md) first. Keep its measurable finish line, one item
at a time, evidence after each item, and `tmp/goals/<slug>/LOOP-STATE.md`.
This skill authorizes delegation and the role routing below for that loop.

## References

Everything harness-specific lives in a referenced file, not here. Before
planning, read the one matching the current harness:

- [references/deepseek.md](references/deepseek.md) - DeepSeek Harness
- [references/codex.md](references/codex.md) - OpenAI Codex CLI

Each file gives the model role map, the spawn call, the reuse/status/stop
tools, the image-viewing call, and the goal-tool shapes. If the harness is not
listed, copy the nearest reference file, adjust it from the local tool
reference, and use it the same way. This file stays vendor-neutral on purpose.

## Worktree

Use an existing isolated worktree when already in one. Otherwise create one
before the plan part:

```sh
git worktree add -b <slug> .agents/worktrees/<slug>
```

All agents share the filesystem; spawning does not change their working
directory. Give every agent the absolute worktree path, and have it set
`workdir` on shell calls and use absolute paths for edits. Read the applicable
AGENTS.md instructions there. Keep the state file and scratch in that worktree.
Preserve the worktree and its results until the work is integrated; remove it
only after checking for uncommitted work and preserving any needed ignored files.
Use the environment's approval mechanism if creating it requires escalation.

## Roles

Three roles, mapped to concrete models in the reference file:

- **plan** - planning, design decisions, difficult debugging.
- **sweep** - file checks, scripts, routine transforms.
- **vision** - any part that reads an image. Always.

An item that reads a screenshot is `vision`, always - no other tag overrides
it, even when its other work is mechanical. A text-only model cannot see the
image.

## Plan and run

The first part runs in the plan role and returns concrete items, each tagged
with its role and the check that will prove it. Record each item's role, actual
model, reasoning effort (if the harness has one), and whether it reads images
in the state file before implementation.

For each item, spawn one agent using the reference file's spawn call. One item at
a time: collect its result, prove it yourself - run the tests, read the file
back, review the screenshot report - then update the state file before
dispatching the next. A subagent's say-so is not proof.

Reuse an agent across items when the role and model match, using the
reference file's follow-up call; provide the next item's scope and current state
explicitly. Use another agent when the required model differs.

Respect the harness's live slot limit (count the controller) and the applicable
AGENTS.md cap on total subagents. Keep each item sequential.

## Visual evidence

The vision task must name the exact image paths and the expected page behavior.
Have the model use the reference file's image-viewing call on those paths.

File size and dimensions are only integrity checks; they cannot prove visual
correctness. Inspect the image yourself when capable, or obtain a second
independent vision inspection when the result needs verification you cannot
perform. If no image-capable route is available, record the visual check as
unresolved.

## Finish

The controller owns the state file and goal status; subagents report item
results. Apply the goal skill's completion rules: unresolved required items
keep the objective incomplete. Report changes, evidence, and remaining work.
