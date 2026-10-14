# Testing

Test conventions, and why `make test` looks the way it does.

## What is tested

- **Use cases** in `service/domain/`, as plain functions — no HTTP, no argv.
- **Models** — mutators and their invariants, in `tests/scaffolding/data/models/`.
- **Conventions** — `test_conventions.py` asserts the registries and the docs agree;
  `test_docs_match_code.py` asserts the docs match the code; `test_two_shells_agree.py`
  asserts the CLI and HTTP expose the same use cases.
- **The UI** — `tests/scaffolding/ui/` holds the checkable rules (components, tokens,
  contrast, schema).
- **The frontend's functional core** — `tests/js/core/`, run by node with V8 coverage
  gated at 100% on what the tests import.

## Conventions

- Tests mirror `src`: `tests/scaffolding/<package>/test_<thing>.py`.
- One `recipe` per model under `tests/recipes/` — the fixtures a test builds with.
- A test asserts a rule, not a line; coverage is read, not scored
  (`make test` prints the paths nothing exercises).
- Branch coverage is on (`tool.coverage.run branch = true`): a line both paths of an
  `if` reach is not a tested branch.

## Running

```bash
make test        # pytest with coverage
make test-js     # node --test for the frontend core
make lint        # ruff
make typecheck   # mypy
```
