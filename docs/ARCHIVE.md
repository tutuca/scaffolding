# Archive - the shareable snapshot

A derived copy of the financial situation, written to a **Google Drive shared
folder** for the contador/lawyer. Google-native: the numbers live in **Sheets**,
one spreadsheet per year.

## What it is, and what it is not

- **Archive** - the shareable read of the ledger: scaffolding, movements and the
  spending categorized off them.
- **Not backup** - reconstructing the working state is a different concern,
  deferred. The archive carries derived snapshots, never the sqlite.

## Structure

```
root (the folder the tool created, id on the taxpayer's drive_archive_folder)
  2026 (Sheet)
    léame          the conventions, for whoever opens the folder
    resumen        one row per month: facturas · notas · ingresos netos y acreditado ARS · gastos ARS · movimientos, plus a TOTAL
    movimientos    the year's log: every movement, with its categoría
    ingresos       the year's authorized comprobantes, signed, in USD and their ARS equivalent
    gastos         categoría × month, with its grupo and bucket beside it
    2026-09 …      one tab per month with activity: categoría, movs, total, % del mes
    gráficos       gasto por grupo: one bar chart per recent month, plus the year
    proyección     last: the next twelve months - surplus, balance, and where the goals land
  2025 (Sheet)
    …
```

`gráficos` carries its own data table - grupo, its bucket, a column per charted
month, and the year - and four native Sheets bar charts drawn over it. One table
rather than four ranges, sorted by the annual total so every chart ranks its bars
the same way and they can be read against each other. Bars are horizontal (`BAR`)
because the names are long, and the height scales with the number of rows:
thirty-odd bars in a fixed box is a picture of nothing.

It charts the **grupo**, not the categoría. A movement is tagged at the leaf it
actually is - `carniceria`, `verduleria`, `supermercado` - and read at the level
the question is asked: fifteen bars with one of them `comida` answers "where does
it go", where forty-five bars you have to add up in your head do not. The leaves
are still on `gastos`, one row each, with both levels above them in their own
columns.

Charts are **replaced** on every run, never appended - `SheetWriter.charts` deletes
the tab's embedded charts before drawing. Re-archiving a year otherwise stacks a
second copy of all four. A year with no gasto gets no `gráficos` tab at all: an
empty chart reads as "nothing spent" rather than "no data".

One file a year. It was a folder per month holding a sheet and a prose Doc until
2026-09-17 - twenty-five files a year for one person's ledger. The `nota` was
four figures, so it became a row on `resumen`; the folders organised nothing a
tab does not; and the README was the only surviving Doc, which did not justify a
whole Google service, so it is the `léame` tab.

**Frozen, one level down.** A spreadsheet that accretes months cannot be written
once and never edited - but a *tab* can. A month's tab is written when the month
closes and not touched again; every year-wide tab - `léame`, `resumen`,
`movimientos`, `ingresos`, `gastos`, `gráficos` and `proyección` - is rewritten on
every run, because each is a roll-up of the whole year rather than a record of
one month. `write` clears a tab before filling it, so a shorter month never
leaves the longer one's tail behind.

## Commands

```
scaffolding archive 2026       write the year: every fixed tab, plus a tab per month with activity
scaffolding archive 2026-09    refresh that month's drilldown; every year-wide tab is rewritten either way
```

A month with no movements gets no tab: twelve empty ones would bury the months
that happened.

## Layers

- `interface/adapter/google/` - the outside system. `ports.py` holds one Protocol
  (`SheetWriter`); `sheets.py` implements it over `googleapiclient`; `auth.py` is
  the one place OAuth and discovery live. Two scopes, Sheets and Drive - Drive
  because a spreadsheet is a Drive file, so finding it by name in the shared
  folder and creating it there are Drive operations.
- `service/domain/reporting/` - `use_cases.archive(*, taxpayer, year, sheets,
  month=None, rate=None)` reads the ledger and hands rendered rows to the sink.
  `calc.py` is the pure row builder; every tab is a function there, testable
  without Google.

The ledger stays the derived read model; the sheet is a sink, never a source.

`reporting` reads `Movement.category` rather than running the categorization
rules again: `movements categorize` writes that column, and two readers of one
table must not disagree about what a row means.

## 2026-09-23: credit notes, emission months, and what a refresh rewrites

Three changes, replacing the 2026-09-17 shape. Agreed 2026-09-20 in
`docs/superpowers/specs/2026-09-20-issuance-follows-payment-design.md`, landed
2026-09-23:

- **`ingresos` carries every authorized comprobante, signed.** It was Facturas
  E only, so a reversed factura kept its full figure on the tab while the
  ledger's signed total moved - a synthetic pair showed ARS 8,880,000 here
  against −120,000 there. The nota de crédito is its own row, negative.
- **Months bucket by `fecha_emision`.** It was `periodo_desde`. The ledger and
  the monotributo ceiling count a comprobante under its emission month
  (`peso_total_by_period`), and the resumen now reconciles against both, pinned
  by test. `resumen` shows the signed net plus an `acreditado` column, so gross
  reads as neto + acreditado.
- **A month refresh rewrites every year-wide tab.** The narrow set (resumen +
  the month tab) left `ingresos`, `gastos` and `movimientos` stale. `YYYY-MM`
  now narrows only which per-month drilldowns are rewritten. A full-year
  rewrite on every run was proposed and rejected the same day: the archive
  stays incremental, and the eleven unchanged drilldowns stay untouched.
