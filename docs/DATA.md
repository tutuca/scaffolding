# Data

How this repository handles data. Two references set the standard; the rest is
how those ideas apply here.

## Sources

- Wickham, *Tidy Data* (JSS 2014) - the shape every table should take.
- Ellis & Leek, *How to share data for collaboration* (2017) - the package a data
  producer hands an analyst: raw data, tidy data, a code book, and the recipe.

Both PDFs are archived under `var/documents/sources/`.

## The standard, in one screen

**Tidy data** - three rules:

1. Each **variable** is a column.
2. Each **observation** is a row.
3. Each type of **observational unit** is its own table.

A variable holds all values that measure one attribute across units (the amount,
the date). An observation holds all values measured on one unit (one bank
movement, one bill). Tidy data is Codd's third normal form in statistical
clothes: one fact lives in one place, so aggregating a column and joining two
tables are both trivial.

**Fixed vs. measured variables.** Fixed variables are known before the data is
collected (the account, the statement date, the category) and come first;
measured variables are what the instrument reports (the amount, the balance).
Order columns fixed-then-measured, and sort rows by the fixed columns.

**The five ways data is messy, and the one tool for each:**

| Messy shape | Fix |
|-------------|-----|
| column headers are values, not variable names | **melt** (columns → rows) |
| several variables packed into one column | **split** |
| variables in both rows and columns | melt + **cast** (rows → columns) |
| several observational units in one table | split into one table per unit |
| one unit spread across many tables/files | concatenate, keep a source column |

The four manipulation verbs - **filter, transform, aggregate, sort** - all take
tidy input and return tidy output, which is why they compose. Each takes a
"by": group-wise filter, transform, aggregate.

**The data package** (Ellis & Leek): hand over, in order -

1. **The raw data** - as received. No software run on it, no values touched, no
   rows dropped, nothing summarized. If new data would merge into it with no
   modification, it is raw.
2. **The tidy data set** - one variable per column, one value per cell, one table
   per kind of data, and a shared join key across tables.
3. **The code book** - every variable's name, meaning, and units; plus the study
   design (what was collected, from where, and why).
4. **The instruction list** - the exact recipe from raw to tidy, as a rerunnable
   script (or, failing that, step-by-step pseudocode).

**Variable coding** (their Figure 2, abridged to what bites here): meaningful
names, no spaces, consistent capitalization, avoid separators (underscore if one
is unavoidable); one value per cell; missing = `NA` (never blank, never a
sentinel number); dates in ISO 8601 `YYYY-MM-DD`; categories as text, not
numbers; no color/highlighting to carry meaning - encode everything as text.

## What we deal with

The repository holds four kinds of thing, at four levels of stability:

| Folder | Stability | Role |
|--------|-----------|------|
| `docs/` | **Set in stone** until the next docs review | methodology, process, definitions - this file lives here |
| `var/documents/` | **Canonical, organized** | the archive: raw inputs and the derived tables built from them (gitignored, sensitive) |
| `var/scratchpad/` | **Working, mostly organized** | the human checklist; changes over time |
| `tmp/` | **The wild west** | downloads and scratch; things get promoted to `var/documents/` or deleted |

There was a `strategies/` folder, and a command that scored what each contador
proposed on two axes (distance from lawful, and visibility). Both went on
2026-09-17. The reason is in `var/documents/sources/backreporting-devengado.md`: the
devengado rule means the option space is one shape wide - issue the backlog now,
each comprobante in its own period - so there was never more than one strategy to
compare. Keeping the comparison would have been keeping a machine for choosing
between one thing. What survives is the arithmetic that outlives the choice:
`scaffolding penalty`.

`var/documents/` is the canonical repository; `var/scratchpad/` is the working notes.
A document earns its place in `var/documents/` when it is an input someone will
want to re-read or re-run against; a half-formed list belongs in `var/scratchpad/`;
a download nobody has classified yet belongs in `tmp/`.

## The ontology of `var/documents/`

Lowercase, hyphens as the separator, minimum grouping. Do not
over-compartmentalize: a folder earns its name by holding more than one thing.

```
var/documents/
  bank/transaction-extracts/  the bank extractos, Payoneer exports, and the derived tables
  contracts/                  the agreement
  scaffolding/                   Facturas E (issued) + the client's commercial scaffolding
  sources/                    the source cards + the raw documents they summarize
  statements/                 liquidaciones, F931, deudores - statements that are not the bank extract
```

## How we work with the files

**The extract pipeline** (the one data flow built so far), raw → typed:

```
PDF / CSV (raw, as downloaded)               var/documents/bank/transaction-extracts/
  → pdftotext -layout                        *_transcript.txt   (PDFs only)
  → scaffolding movements load <SOURCE> <path>  data.Movement
```

Each stage is typed and idempotent. The PDFs and rail exports are raw and are
never edited; the transcript is the text layer verbatim; `load` parses it through
the institution's parser and appends what is not already there, so re-importing
an overlapping report changes nothing. See `docs/extractos.md`.

**The snapshot rule.** The raw reports are the immutable source of truth and are
never written back to. Everything derived from them - the `Movement` rows, the
`categoria` a movement falls in, the archive sheet - is rebuildable by re-running
the pipeline, which is the same claim `ARCHITECTURE.md` makes for the ledger as a
whole: reconstructible from ARCA, the bank and the contract.

This replaced a pair of standalone SQLite files (`extractos.sqlite` and a
categorized copy) and the `bin/extractos_*` scripts that wrote them, on
2026-09-17. The discipline they encoded - raw data untouched, a derived copy per
analysis - survives; what went was the second store, and with it a second copy of
the categorization table that had drifted into `float` while the app used
`Decimal`.

**Naming.** Folders: lowercase, hyphen-separated, two levels, minimal grouping.
Files we produce: lowercase, hyphen-separated, the source of truth named by
content (`extractos_transacciones.csv`), not by tool. Files we receive keep
their name as the source gave it - renaming a raw document loses provenance;
we organize by folder, not by renaming the artifact.

**One value per cell, one fact per row.** A bill and a bank movement are
different observational units and must not share a table. The join between them
is the payee/amount/date, matched in code, not stored as a merged blob.

## Whose row is it

Every table falls into exactly one of three kinds, and `test_conventions.py`
fails until a new one is classified - an unclassified model is one whose tenancy
nobody decided.

| kind | tables | carries `taxpayer` |
| --- | --- | --- |
| **owned** | `Client`, `Contract`, `Cutoff`, `Account`, `AccountBalance`, `Invoice`, `InvoiceLine`, `Movement` (and its `Payment`/`Expense`/`Untriaged` readings), `Settlement`, `Goal`, `Obligation`, `InvestmentPlan`, `MonotributoStatus`, `ReversalEntry` | yes |
| **reference** | `MonotributoScale`, `LegalThreshold`, `ExchangeRate`, `CompensatoryRate`, `AutonomosContribution`, `CategoryGroup`, `InvestmentPlanKind`, `PriceIndex`, `MarketIndex` | no - public facts, shared by everyone |
| **identity** | `BaseUser`, `Taxpayer`, `Membership` | no - neither ledger nor reference |

The split is not a style choice. It decides which unique constraints are right:
`uniq_comprobante` and `arca_cmp_id` are per-CUIT rules, because ARCA assigns
puntos de venta per CUIT and numeración restarts at 1 within each. Stated
globally they would reject a second taxpayer's perfectly legal first invoice.
A reference table needing `taxpayer` in its unique key was never reference data.

`taxpayer` is a column on every owned table, including the ones whose parent
already implies it. That duplication cannot drift, because a child's taxpayer is
never passed in - `Invoice.objects.draft()` sets each line's from the invoice it
is building. See `docs/ARCHITECTURE.md`, "Identity, ownership and visibility".
