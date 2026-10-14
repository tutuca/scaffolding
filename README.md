scaffolding
========

Facturación de exportación de servicios (**Factura E**), cobros, y posición frente al
monotributo. Una máquina, SQLite, y Google como única puerta.

This repository is the archive of my financial organization. The Django app is one
tool inside it: human work - the contador, tax-agency paperwork, chasing a client for a
tax id - is tracked in `var/scratchpad/NEXT.md` (local and gitignored), which is where to
start a session.

## The monthly cycle

Acme issues the invoice and pays it. We issue the Factura E for the month
worked, once their money has arrived - so no comprobante is ever emitted for
money that did not turn up.

```bash
# 1. the payment landed: load the rail's export, then classify it (idempotent)
scaffolding movements load PAYONEER var/documents/bank/transaction-extracts/report_2026-10-02.csv
scaffolding movements classify

# 2. where does the month stand? it names the next command every time
scaffolding month 2026-09

# 3. issue it: the agency's rate, the agency's numbering, the CAE recorded
scaffolding month 2026-09 --issue

# 4. attach a generated PDF if a client needs one (WSFEX returns none)
scaffolding month 2026-09 --pdf var/documents/scaffolding/20111111112_019_00005_00000006.pdf
```

```
$ scaffolding month 2026-09
period 2026-09 · expected 6000.00 for 2026-09-01–2026-09-30
  payment      5940.00 USD on 2026-10-02 (1031657706, candidate)
  factura E    not drafted
  → next: scaffolding month 2026-09 --issue

$ scaffolding month 2026-09 --issue
authorized 2026-09: numero 6, CAE 76367016796758
period 2026-09 · expected 6000.00 for 2026-09-01–2026-09-30
  payment      6000.00 USD on 2026-10-02 (1031657706, matched)
  factura E    AUTHORIZED nº 6 CAE 76367016796758
  → next: file the PDF and pass --pdf
```

The payment goes from `candidate` to `matched`, and its 5940.00 becomes 6000.00:
the 60.00 shortfall is recorded as the rail's fee, not as a discount on the
service. (Transcript from a run against the homologación environment.)

Nothing is interactive, and re-running is always safe: `--issue` on an authorized
month stops and says so, and a retry after a dropped connection returns the
original CAE rather than earning a second one.

`--issue` and `--draft` refuse a month with no payment on record - load the
rail export first, or say `--unpaid` for money that arrived off-rail.

The full runbook - the portal fallback for a WSFEX outage, and why the invoice is
for USD 6,000 when USD 5,940 arrives - is in [`docs/MONTHLY.md`](docs/MONTHLY.md).

## Commands

| Command | Does |
|---------|------|
| `scaffolding month <YYYY-MM>` | Report a period. `--issue` authorizes it against the agency; `--draft` and `--cae …` are the portal fallback; `--pdf` files the document |
| `scaffolding creditnote <id>` | Reverse a comprobante. `--cancel` for all of it, `--amount N` for part; `--issue` authorizes it, `--cae …` records a portal CAE |
| `scaffolding valuation` | What each reversal netted in both currencies, reconciled against the journal. `--write` saves it |
| `scaffolding movements load PAYONEER <csv>…` | Load a rail export; `classify` labels the rows so credits read as payments |
| `scaffolding balances` | The stock side: `derive` reads the statements' closing figures, `set` records them by hand, bare is the report |
| `scaffolding crosswalk` / `scaffolding catchup` | Read a backlog side by side (`--project` adds hypothetical scaffolding), then issue valid months in one idempotent pass |
| `scaffolding projection` | Walk the next twelve months against goals and obligations; uses the quote in force unless `--rate` overrides it |
| `scaffolding penalty` | Price a recategorization that should have happened |
| `scaffolding archive` | Write the yearly spreadsheet to the shared Drive folder |
| `scaffolding register --cuit <cuit>` | Claim a CUIT and become its owner |
| `scaffolding setup status` / `starter` / `import FILE` / `export [FILE]` | Configure the books: what a first run is missing, the neutral starter pack, and a bundle of your own vocabulary, rules and declarations. See [`docs/SETUP_DATA.md`](docs/SETUP_DATA.md) |
| `scaffolding taxpayer` | The agency's constancia: régimen, IVA, category and exclusion, compared with the books |
| `scaffolding login` | Authenticate a terminal through Google's loopback consent |
| `scaffolding inflation fetch` / `report` | Download INDEC's IPC and read spending against it. See [`docs/INFLATION.md`](docs/INFLATION.md) |
| `scaffolding market fetch` / `report` | Download BCRA's reference rates (política monetaria, TAMAR, BADLAR) and read them |
| `scaffolding rate fetch` | Fetch and store the dollar cotización (the agency's registered rate, or the hand-loaded one) |
| `scaffolding experiment run` / `forecast` / `diagnose` / `report` | Snapshot an experiment, forecast live, compare the band with INDEC, or list saved runs |
| `scaffolding loadreference` | Seed the published monotributo scale from `data/reference/` |
| `scaffolding migrate`, `createsuperuser`, `shell` | Django's own |
| `scaffolding runserver` | The HTTP API and the admin, when you want them |

Date cutoffs use `--on YYYY-MM-DD`, month filters use `--month YYYY-MM`, and
ranges use `--since/--until`. See [CLI decisions](docs/CLI.md) for the replaced
spellings and diagnostic workflow.

## Four ways in, one domain

The command line is the everyday interface. The API, the admin and the home
page are the same domain seen from somewhere else - all four call the same use
cases, so it makes no difference which you reach for:

- **CLI** - `interface/cli/`. The monthly cycle, imports, seeding.
- **HTTP** - `interface/api/` binds the viewsets in `service/` to DRF's router.
  `scaffolding runserver`, then Swagger at http://localhost:8000/api/schema/swagger-ui/
  and the API under `/api/v1.0/`.
- **Admin** - http://localhost:8000/ for the data entry no command covers:
  the contract, exchange rates, fixing an ambiguous payment by hand.
- **Home** - http://localhost:8000/, where a login lands (`interface/web/`):
  your books, and what the active ones still need.

Log in through Google once and the API shares the session.

## Setup

```bash
uv sync --extra dev
make configure              # create the var/ and etc/ trees
cp .env.example .env        # SECRET_KEY, the two Google OAuth clients, SIGNUP_ALLOWED_EMAILS
scaffolding migrate
scaffolding migrate --database tasks django_tasks_database   # the task queue's own SQLite
scaffolding createsuperuser
scaffolding loadreference      # the monotributo scale
```

Google is the only registration gateway, and `SIGNUP_ALLOWED_EMAILS` decides who
may use it - empty means nobody. It needs two OAuth clients from one Google Cloud
project, and they are different *types* rather than two copies of one:

- **Web application** - the browser gateway. Give it an *Authorized redirect
  URI* of `http://localhost:8000/accounts/google/login/callback/`. A JavaScript
  origin is a different field and will not do: allauth redirects server-side.
  Download its JSON to `etc/secrets/google-client-web.json`.

  **Then browse to `localhost:8000`, not `127.0.0.1:8000`.** allauth builds the
  redirect URI from the host you typed and Google matches the string exactly, so
  the same server under the other name fails with `redirect_uri_mismatch` -
  which names neither the host nor the mismatch. Register both URIs if you want
  either to work.
- **Desktop app** - `scaffolding login`, which consents over a loopback and needs no
  redirect URI. Download its JSON to
  `etc/secrets/google-client-secret-cli.json`.

A Desktop client cannot take a redirect URI, so it cannot serve the gateway.
Nothing is retyped: both files are read where they lie. Two registrations, one
token store - both end at the same `SocialToken` row.

The scopes asked for are `spreadsheets` and `drive.file`, so the app reaches
only what it created - which is the whole archive, because it creates the folder
too. That keeps the consent screen publishable without Google's paid security
assessment, which full `drive` would require.

Then log in at http://localhost:8000/accounts/google/login/ - `localhost` and not
`127.0.0.1`, for the reason above - and you land on the home page:

1. Register the CUIT there, with the punto de venta if the agency has assigned you one
   yet. That creates the books and makes you their owner. `scaffolding register
   --cuit <cuit>` does the same from a terminal.
2. Work through the gaps the page then names, each linking to the admin page that
   closes it: the fiscal certificate (`docs/CERTIFICATE.md`) - everything that does
   not touch the agency works before this - the `Client` and `Contract`, and an
   `Account` with an opening balance. The contract fee is confidential, so it
   lives in the gitignored database, never in the repo.

`make check` runs ruff, mypy over `src` and `tests`, the frontend's lint, format
and test under node (`lint-js`, `format-js`, `test-js`), and pytest with coverage.
Other targets: `make test lint typecheck format lint-js format-js test-js openapi run`.

## Defaults never touch the network

The authorizer and the rate provider both default to `manual`: drafts are typed
into Comprobantes en línea and the CAE recorded back. `dry_run` mints fake CAEs
for tests and demos; a row it authorized reads `(simulado)` wherever its CAE is
shown. `wsfex` is the real thing - WSAA login signed with your certificate,
WSFEX authorization and the agency's own rate - and refuses at selection time
when no certificate is installed.

The certificate and private key live in `etc/secrets/` (gitignored, mode 0600) and can
issue fiscal documents in your name. `var/documents/` and the SQLite file are equally
sensitive: keep the whole thing on an encrypted volume. See the sensitivity matrix
in [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Layout

```
src/scaffolding/
  conf/                     settings (django-environ), urls (versioned api/v{X.Y}/)
  data/                     the one Django app
    models/<entity>.py      one model per file; every write is a mutator here
    serializers/ admin/     one file per entity
    reference/              public reference data (the monotributo scale)
    management/commands/    loadreference - seeding is data-layer work
  service/
    <entity>.py             flat CRUD viewsets
    views.py                VIEWS registry → the API router
    commands.py             COMMANDS registry → what the CLI exposes (read-only symmetry)
    domain/billing/         schemas · calc · use_cases · serializers · viewsets
    domain/payments/        schemas · classify · matching · use_cases
    domain/tax/             schemas · calc · use_cases · serializers · viewsets
  interface/
    api/                    router, versioned urls
    cli/                    management commands
    adapter/                ports (Protocols), adapters, calendar
var/                        gitignored: the database, documents, scratchpad, runtime
  documents/                papers: statements, scaffolding, bank extracts, sources
  scratchpad/               the human checklist: NEXT.md and one file per track
etc/secrets/                gitignored: the fiscal certificate keys and OAuth credentials
tests/                      mirrors src; recipes/ per model
```

## Documentation

| Read | For |
|------|-----|
| [`docs/MONTHLY.md`](docs/MONTHLY.md) | The monthly runbook |
| [`docs/DATA.md`](docs/DATA.md) | How data is shaped, stored and organized |
| [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) | Where logic lives, and why. Binding. |
| [`docs/TESTING.md`](docs/TESTING.md) | Test conventions |
