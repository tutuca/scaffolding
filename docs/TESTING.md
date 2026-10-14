# Testing

The suite is the net you refactor over. It is worth what it would notice - not
what it touches - so what a test is *for* has to be readable from it.

`make check` runs ruff, mypy (`src`, `tests` and `bin`), the frontend's
lint/format/test under node (`bin/js.mjs` and `node --test`), and pytest with
**branch** coverage. Coverage is reported and read; it does not gate.

## What a test is for

A test earns its place by naming one thing that could be wrong. Three
consequences, and the suite was pruned against all three on 2026-09-18:

- **No catch-alls.** A test whose assertion is the same for every subject asserts
  something about the harness, not about the code. `assert account; assert
  str(account)` was written once per model and would have survived any bug worth
  finding: sixteen of them are gone. So is `assert str(x)` glued onto a test that
  was about something else - a line reached is not a line checked.
- **A convention is checked as a convention.** "Every model is registered in the
  admin" is a wiring rule over the app registry, so it lives in
  `test_conventions.py` with the other rules read off the source, not among the
  admin's behaviour tests where it read as one.
- **Build evidence from the bottom up.** Model tests establish invariants and
  transitions. Domain tests exercise their composition. Interface tests prove
  that permissions, parsing and persistence preserve the same contract. Detailed
  edge cases belong at the lowest layer that owns them; a few deliberate cases
  cross every boundary. Repeating a critical assertion across layers is useful
  when it catches a bypass.

## Composition

Tests share inputs, lifecycle setup and expected outcomes through ordinary
functions and pytest fixtures. Each test gets fresh state and runs independently;
no test calls another test or relies on execution order or a previous result.

There are two distinct kinds of setup:

- **Raw recipes**, in `tests/recipes/`, describe rows. Use them for unrelated
  prerequisites, query tests, and deliberately invalid states that challenge a
  constraint. Baking `status="AUTHORIZED"` does not exercise authorization.
- **Lifecycle fixtures**, in `tests/fixtures/`, compose real model factories and
  mutators. Use them when a workflow depends on how a state was reached. The
  `billing_draft` fixture calls `Invoice.objects.draft`; `billing_authorized`
  builds on it by calling `authorize`. A domain test can start from those rows
  while keeping the domain operation under test explicit in its body.

Expected results come from a worked specification example, never from the
calculation or constant under test. `BillingCase` names a USD 6,000 August invoice
at ARS 1,480, with an explicitly expected ARS 8,880,000 valuation. Shared
assertions read persisted rows, including the invoice line; successful HTTP
status or agreement between two implementations is insufficient evidence.

The billing slice demonstrates the chain:

| Contract | Model evidence | Domain evidence | Interface evidence |
| --- | --- | --- | --- |
| Draft owns its line and valuation | `test_drafting_persists_the_line_and_frozen_valuation` | `test_the_whole_portal_round_trip_runs_on_ids` | `test_portal_round_trip_preserves_the_model_contract`, CLI and HTTP |
| Authorization preserves valuation | `test_authorization_preserves_the_drafts_valuation` | Same portal round trip | Same CLI and HTTP round trip |
| A second authorization refuses without writes | `test_reauthorizing_is_refused_without_changing_the_row` | `test_recording_a_second_cae_refuses_without_changing_the_ledger` | `test_a_second_portal_authorization_is_refused_without_writes` |
| Drafting requires write permission | Membership and role tests | Authorization belongs to the shell | `test_drafting_requires_a_writable_membership` |

A refusal test checks both the refusal and unchanged persistent state. For a
multi-write operation, include the related rows and external effects in that
check; an exception alone does not establish rollback.

`test_two_shells_agree.py` invokes actual management commands, API routes and
admin form submissions. Calling a domain function in place of an admin action
cannot establish an admin contract.

## Boundaries and doubles

Keep model operations, domain orchestration and permission checks real when
exercising their integration. Replace external transports with recorded
responses or explicit fakes. A focused unit test may isolate a collaborator,
but that test does not establish integration with the collaborator.

No global permission mocks. The shared API clients establish real sessions with
`force_login`; users and memberships are real database rows. Anonymous and
read-only cases construct their own clients. This exercises session
authentication and authorization, not Google's consent flow. CSRF enforcement
needs an explicitly configured client when that is the behavior under test.

`test_default_permissions.py` is a narrow harness regression: it uses the
application's DRF defaults to catch the session-wide permission mock that once
admitted anonymous requests.

For each changed test, name the bug it must catch. Temporarily remove a relevant
validation, state write or interface call and verify the selected test fails for
that reason; restore it before the full suite. A green run alone says nothing
about whether an assertion would detect the intended regression.

## Coverage is a map, not a score

`fail_under` was 100 until 2026-09-18. A gate at 100 buys one real thing -
nothing is unexercised - and charges for it in the only currency that matters: to
reach every line, lines carrying no rule get tests that assert nothing but
reaching them, and those sit in the same files, with the same names, as the tests
that pin an invariant. The number stays at 100 while the signal drops. That is
the opposite of observability - a reader cannot tell which tests would notice a
bug.

So read `term-missing` instead of scoring it. Each uncovered path is a question:
is this worth a test, or is it code nobody needs? Both answers are progress; the
gate allowed only one of them.

Behavioral tests guard the contracts. `test_conventions.py` supplements them
with structural checks: detectable direct ORM writes, tenancy, taxonomy and
secrets. Its source scans cannot prove what a serializer or admin form does at
runtime; that requires exercising those paths.

## Layout mirrors the source tree

```
tests/
  api.py                                                versioned reverse() - never hardcode /api/v1.0/
  files.py                                              where the recordings live
  settings.py                                           what every test runs under: ARCA dry_run, throwaway key
  conftest.py                                           `api` client, users, the certificate pair
  recipes/<model>.py                                    model_bakery, one per model
  fixtures/billing.py                                  worked case, lifecycle fixtures, persisted assertions
  fixtures/rates.py                                     the quotes the invoice fixtures value at
  fixtures/reversal.py                                  a factura and the note that reverses it
  fixtures/cli.py                                       `run`, for driving a management command
  fixtures/scale.py                                     the seeded monotributo scale
  recordings/{bcra,indec,padron,payoneer,wsfex}/         real ARCA envelopes, rail exports and public tables
  scaffolding/data/models/test_<model>.py
  scaffolding/data/admin/test_*.py
  scaffolding/test_conventions.py                          the rules, read off the source
  scaffolding/test_two_shells_agree.py                     one workflow, argv and HTTP
  scaffolding/interface/api/test_versioning.py
  scaffolding/interface/adapter/arca/test_*.py
  scaffolding/service/<domain>/test_{entry_points,use_cases,views}.py
  js/core.test.js                                       the frontend's DOM-free functional core
```

A test's path should be derivable from the module it covers. `tests/recipes` and `tests/fixtures` are both loaded as pytest plugins, so every `make_<model>` and every shared fixture is available anywhere. Recipes are model_bakery only. Anything else shared goes in `tests/fixtures/`. Neither belongs in a `conftest.py`.

Frontend tests live in `tests/js/`, outside `src/`, and run under node's built-in
runner (`node --test tests/js`, or `make test-js`). They cover the pure functions
in `src/scaffolding/ui/static/ui/core/` (one module per concern, one test file each in `tests/js/core/`) - no DOM, no Plot, no dependencies - which
is why a `.js` file sits beside `.py` tests and is collected by neither pytest
nor the Python build.

Lint and format keep the same shape: one standard-library script, `bin/js.mjs`,
with no prettier, no eslint and nothing to install (`make lint-js` / `make
format-js`, or `npm run lint` / `npm run format`). It checks syntax (`node
--check`), line endings, tabs, trailing whitespace, final newlines, blank-line
runs and stray `debugger` statements; `format` rewrites the whitespace half and
reports what it cannot.

## The four patterns

**Model** - a test per rule the model carries, and nothing for a model that
carries none. `Payment.gross`, `Settlement.effective_rate`, `Invoice.freeze_valuation`
and every refusing mutator get explicit tests per branch. A model that is columns
plus `__str__` gets no test of its own: a recipe that stopped building would
break every test that uses it, and a truthy `str()` says nothing about what is
rendered. Where the rendered string *is* an interface - `Invoice.label` in the
CLI output and in `ReversalEntry.note_label` - the test asserts the string, not
its truthiness.

**Admin** - admin classes with behaviour get a file, e.g. `test_invoice_admin.py`
pins the fields the business contract requires frozen. Expected behavior must
be stated independently of the production field list, so removing a protection
cannot remove the expectation too. That every model is
registered at all is a convention, checked in `test_conventions.py`.

**Viewset** - go through HTTP with the `api` fixture and `tests.api.reverse`, so the URL version lives in one place:

```python
response = api.get(reverse("invoice-portal-sheet", {"pk": invoice.pk}))
```

**Domain** - entry points and steps are tested where they live.
`test_entry_points.py` calls what a shell calls, the way a shell calls it - books
by id, subject by id, a read model back - and `test_use_cases.py` exercises the
steps behind them over rows. The split is rule 7's (`docs/ARCHITECTURE.md`), and
having it in the file names is what keeps a step from quietly becoming the thing
a second UI has to reach.

**Adapter** - every adapter is exercised without network. `dry_run` and `manual` are tested directly; WSFEX is driven by response envelopes recorded from ARCA's homologación service under `tests/recordings/`, reached through `tests.files` so no test counts `parents[]` to find them.

## Rules

- **No autouse fixtures, no session scope, no skips.** Banned 2026-09-20. An
  autouse fixture is setup a test's
  signature does not show; session scope shares one instance across tests, so
  order starts to matter; a skip reads as green while checking nothing. What the
  three suite-wide autouse fixtures held moved to `tests/settings.py`; the four
  runtime skips became vacuous assertions (docstring says so) or filtered
  parametrize lists.
- **No test touches the network.** `tests/settings.py` pins `AUTHORIZER=dry_run`
  and `RATE_PROVIDER=manual` for the whole suite; a test wanting another adapter
  opts in explicitly via the `settings` fixture.
- **No test writes outside `tmp_path`.** `tests/settings.py` points
  `VALUATION_REPORT` at a path that cannot be written, so the test that writes
  redirects it to its own `tmp_path` - and one that forgets fails at the write
  instead of leaving a report in `var/`. The journal itself needs no pinning
  since it became a table: it lives in the test database and rolls back with it.
- **Live ARCA checks are scripts, not tests** (`bin/arca_smoke.py`). If one
  ever becomes a test it takes the `integration` marker, which is deselected by
  default.
- **Recipes hold the shape, tests hold the intent.** A recipe's defaults describe
  the normal case (Acme, USD 6,000, Payoneer); anything a test asserts on it
  passes in explicitly, so the assertion is readable without opening the recipe.
- **A value repeated across tests is a fixture, not a literal.** `ExchangeRate` has
  no useful default date or value - a rate only means something against the emission
  it values - so the four the suite uses are named in `fixtures/rates.py`
  (`august_rate`, `november_rate`, `issued_rate`, `reversal_rate`) instead of being
  spelled out at each of the forty-odd call sites they had reached.
- **Setup that two files share moves to `tests/fixtures/`.** `reversed_pair` and the
  `run` helper were each written twice before they did.
- **Refactor the code first, the tests second.** While the tests are being
  rewritten there is no net, so the two never move in the same step: the rework
  of 2026-09-17 changed every use-case signature with the suite green and only
  its call sites edited, and reshaped the suite in a second commit on top.
- Coverage is **branch**, not line: a line both paths of an `if` reach is not a
  tested branch, and line-only coverage reads 100% while whole paths go
  unexercised. It omits `manage.py`/`wsgi.py`/`asgi.py` (framework entrypoints
  with no logic), `data/migrations/*` (they run while the test database is built,
  before the measured phase) and Protocol `...` bodies (declarations that never
  execute). Nothing else is excluded.
