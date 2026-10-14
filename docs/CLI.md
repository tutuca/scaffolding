# CLI decisions

This file is the ADR log of what the command line used to say and why it
changed - history, not the manual. The living reference is the README's
commands table plus each command's own docstring
(`interface/cli/management/commands/`), held to the `COMMANDS` table by the
convention tests.

## ADR — 2026-10-08: remove vestiges and consolidate equivalent operations

The command line remains Django management commands. The Makefile supplies
operator routines and development checks; `make run` uses `runserver` directly.
Collecting static files remains an explicit deployment step, because the
development server reads the apps' assets directly.

The cleanup replaces these spellings without compatibility aliases:

| Before | Now | Meaning |
|---|---|---|
| `experiment validate`, `backtest`, `trend` | `experiment diagnose` | Latest INDEC comparison, historical coverage and annual trend together |
| `experiment … --as-of YYYY-MM-DD` | `experiment … --on YYYY-MM-DD` | Date cutoff, also used by balances and rate |
| `inflation report --mes YYYY-MM` | `inflation report --month YYYY-MM` | Month anchoring the comparison window |
| `movements categorize --mes YYYY-MM` | `movements categorize --month YYYY-MM` | Filter the reported totals to one month |
| `crosswalk --dry-run` | `crosswalk --project` | Add hypothetical missing scaffolding to an already read-only report |

`--since/--until` remain month ranges. `--fecha-emision` remains the fiscal
emission date. These meanings differ from a report's date cutoff.

`experiment diagnose --on 2026-09-30 --since 2025-10` dates all three readings
at the same cutoff and narrows the coverage and trend history. It requires an
IPC series, but no taxpayer's books. Coverage compares the declared band at
that cutoff with observed history; it does not reconstruct forecasts issued
before each observation.

`projection` now defaults to the USD quote in force, just as the investment
forecast does; `--rate` still supplies a hypothetical rate. A missing quote
refuses rather than substituting a constant. `crosswalk --project` instead
resolves the quote for the proposed fiscal emission date.

`rate fetch` retains its name and stores the fiscal cotización. `market fetch
--provider mirror` supplies MEP/CCL and EMBI+; `--provider bcra` supplies interest
rates. The read-only `bin/arca_rate.py` remains a diagnostic probe with explicit
certificate files and environment selection.

### 2026-10-08: daily fiscal-rate refresh selects WSFEX

The daily recipe originally inherited the manual provider. That provider reads
an existing quote, so a missing prior-business-day quote stopped `make daily`
with `No USD rate loaded`. The recipe now runs `ARCA_RATE_PROVIDER=wsfex
scaffolding rate fetch`, explicitly opting into ARCA for that invocation. The
application's manual default and the standalone command's refusal remain.

JSON remains available on taxpayer, penalty and crosswalk. These consumers
share one renderer: dataclass fields form objects, decimals remain exact
strings, and dates are ISO strings. Adding JSON to another operation requires
a consumer and an output contract.

An authorized month is complete without a PDF. An existing WSFEX draft points
to `--issue`; a portal draft points to CAE recording. Competing actions and
incomplete portal values refuse before changing an invoice. The PDF may still
be attached alongside the portal CAE or afterwards.

The old `settings.ARCA["PUNTO_VENTA_EXPORTACION"]` fixture values were ignored
after the point of sale moved onto `Taxpayer`. Portal tests now set the row to
PdV 4 and assert the draft's point of sale; redundant setting-only fixtures
were removed.
