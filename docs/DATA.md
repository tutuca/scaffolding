# Data

How rows are shaped and stored. The sample domain is a single owned model.

## One table per concern

- `Tenant` — the unit of isolation. Every owned row points at one.
- `Membership` — the edge between a user and a tenant, carrying a `Role`.
- `BaseUser` — the login (email is the identifier).
- `Note` — the sample owned row: `title` + `body`, scoped to a tenant.

## Ownership

`data/models/base.py` defines `OwnedModel` (a `tenant` foreign key, `PROTECT`) and
`OwnedQuerySet.owned_by(tenant)`. The admin and the API narrow by it, so another
tenant's row is a 404 on a guessed id.

## Tidy data

Every value is stored in one place and derived elsewhere:

- A write lands through a **mutator** on the model, which names its invariant.
- A serialized value comes from `data/serializers/`, and precision is shared with
  the column through the constants in `scaffolding/types.py`.
- Reference/seed data, when a project needs it, lives in `data/reference/` and is
  loaded by a data-layer management command — not typed into the code.
