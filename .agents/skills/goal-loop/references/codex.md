# OpenAI Codex CLI

The Codex CLI harness: tools run through `functions.exec`, agents through the
`collaboration` API.

## Model role map

Use the current `collaboration.spawn_agent` schema and model allowlist as the
authority. These defaults apply when the listed models are available:

| Role | Model | Reasoning effort | Use |
|------|-------|------------------|-----|
| plan | `gpt-6.1-sol` | `high` | Planning, design decisions, difficult debugging |
| sweep | `gpt-6-luna` | `medium` | File checks, scripts, routine transforms |
| vision | `gpt-6.1-sol` | `high` | Inspecting screenshots, charts, crops |

If a listed model is unavailable, choose an allowed model suited to the role
and record the substitution. Confirm image input and an image viewing tool are
available before assigning vision work.

## Spawning a part

Call `collaboration.spawn_agent` directly, outside `functions.exec`. Example for
a mechanical item (substitute the actual paths and task):

```json
{
  "task_name": "sweep",
  "fork_turns": "none",
  "model": "gpt-6-luna",
  "reasoning_effort": "medium",
  "message": "Work in /absolute/worktree. Read its applicable AGENTS.md and tmp/goals/example/LOOP-STATE.md. For the current item, inspect only the assigned files, perform its recorded check, and report evidence and unresolved issues. Do not start another item or manage the goal status."
}
```

## Reuse, status, stop

- Reuse a suitable agent with `collaboration.followup_task`; it starts a turn
  when idle. `send_message` steers a running agent but does not wake an idle
  one.
- When idle, use `collaboration.wait_agent` for up to 60 seconds, then check
  messages and give a progress update as needed.
- `list_agents` resolves uncertain status; `interrupt_agent` stops unneeded
  work. Do not invent a close-agent tool.

## Images

For a local screenshot, display the tool result to the model through
`functions.exec`:

```js
const result = await tools.view_image({path: "/absolute/worktree/var/shots/page.png"});
image(result.image_url);
```

File size and dimensions are only integrity checks, not visual proof.

## Goal tools

Via `functions.exec` as `tools.create_goal`, `tools.get_goal`, and
`tools.update_goal`:

- `tools.create_goal({ objective })`; include `token_budget` only if explicitly
  requested.
- `tools.get_goal({})` before creating or updating.
- `tools.update_goal({ status: "complete" })`; `status` is `complete`, `paused`,
  or `blocked`.
