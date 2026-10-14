# DeepSeek Harness

The harness this skill normally runs in. Goal tools, subagents, and shell are
native tools; there is no `functions.exec` wrapper.

## Model role map

There is no per-agent reasoning-effort knob; the model name is the lever.

| Role | Model | Use |
|------|-------|-----|
| plan | `deepseek-v4-pro` | Planning, design decisions, difficult debugging |
| sweep | `deepseek-v4-flash` | File checks, scripts, routine transforms |
| vision | `deepseek-v4-flash-vision-exp` | Inspecting screenshots, charts, crops |

`deepseek-flash` (DeepSeek-V41-Flash) also takes images and is a fine
alternative to the vision-exp model. Provider is `deepseek-official` (the
default route); pass it only to be explicit.

## Spawning a part

The `workflow` tool's `agent()` is the routing mechanism:

```js
return await agent(
  "<self-contained task: objective, absolute paths, owned files, evidence, report>",
  { model: "deepseek-v4-flash", label: "<short item name>" }
);
```

Outside a workflow, delegate with `subagent` / `subagent_fork` (background by
default). There is no per-agent reasoning-effort field.

## Reuse, status, stop

- `send_message` steers a running agent and starts a turn for an idle one; it
  returns only delivery confirmation, not an answer.
- `list_agents` resolves uncertain status (`children` or `descendants`).
- `interrupt_agent` stops work that is no longer needed. There is no close-agent
  tool.
- Results arrive as settlement notices; read them, then prove each one yourself.

## Images

Have the vision model call the native `read_image` tool on the exact path:

```
read_image("/absolute/worktree/var/shots/page.png")
```

File size and dimensions are only integrity checks, not visual proof.

## Goal tools

Native tools, called directly (no `functions.exec`):

- `create_goal({ objective })` - objective is the measurable finished state.
- `get_goal()` - read before any update; it returns the exact `goal_id` and
  `revision`.
- `update_goal({ goal_id, revision, action })` - `action` is `complete`,
  `blocked`, `pause`, `resume`, or `edit`; `blocked` needs a concrete reason.
