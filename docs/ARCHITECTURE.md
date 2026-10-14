# Architecture

The binding rules for where logic lives. Every layer has one direction of
dependency: `data` ← `service` ← `interface`/`ui`, and `conf` is read by all.

```
conf/        settings, urls, database router (no business logic)
data/        the one Django app: models, serializers, admin, migrations
service/     use cases and viewsets (the domain rules)
interface/   how the outside reaches in: api, cli, tasks, adapter, web
ui/          templates + static (no models, no views)
```

## Layers

| Layer | Owns | Never does |
|-------|------|------------|
| `data/` | tables, fields, mutators, serializers, admin | business rules, HTTP, argv, templates |
| `service/` | use cases (plain functions over the data layer) | HTTP, argv, templates, ORM writes outside the data layer |
| `interface/` | one file per outside system: `api/` (DRF), `cli/` (management commands), `tasks/` (django.tasks), `adapter/` (external ports), `web/` (server-rendered pages) | business rules — each shell calls the same use cases |
| `ui/` | templates and static assets; Python helpers that read a model's shape | models, views |

## Code principles (binding)

1. **One model per file**, named `<entity>.py`; `data/models/__init__.py` is the
   only index of them.
2. **Every write is a mutator on the model.** Nothing calls `save()` on another
   layer's behalf; a mutator names the invariant it protects.
3. **Use cases are plain functions** with keyword-only arguments, over the data
   layer. No shell reimplements a rule.
4. **The two registries.** `service/views.py` says what HTTP serves;
   `service/commands.py` says what argv serves. Both point at the same use cases.
   `test_conventions.py` checks they agree.
5. **The tenant comes from the request/argv, never the payload.** Owned rows are
   scoped by the active tenant (`data/models/base.py: OwnedModel`); a client that
   could name the tenant could write into another's.
6. **What a role may do is one table** (`data/visibility.py`), answered by
   `data/backends.py`. Minimal by default: a resource absent from a role's row is
   invisible to it.
7. **Refusals are `DomainRefusal`.** The domain raises it; each shell maps it to a
   message (400, a `CommandError`), never a traceback.
8. **Dependency direction is one-way.** `data` never imports `service`; `service`
   never imports `interface`; `ui` imports none of ours (a model is passed in).
