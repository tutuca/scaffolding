# CLI decisions

The command line is one of four ways into the same domain.

## One flag every command shares

Every command takes `--tenant <slug>`, added by `interface/cli/base.py` rather than
in each `add_arguments`: a flag every command needs should not depend on each
remembering. With no flag and exactly one tenant, that one is meant; with several
and no flag there is no right answer to guess, so it refuses and names them.

## Refusals are messages, not tracebacks

A `DomainRefusal` from the domain is what the operator did, not a bug. The base
command maps it to a `CommandError`, so commands stay free of repeated `except`
ladders.

## The registry

`service/commands.py` is the checked documentation of what argv exposes — it lists
each command and the use cases it binds. `test_conventions.py` asserts the table and
the command modules agree.

## The sample command

```bash
scaffolding notes list                 # the tenant's notes, newest first
scaffolding notes add --title "…" --body "…"
```

A new command is a file under `interface/cli/management/commands/`, a use case in
`service/domain/`, and a row in `service/commands.py`.
