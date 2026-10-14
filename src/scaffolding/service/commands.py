"""What the command line exposes, mirroring `views.py` for HTTP.

This table wires nothing: Django discovers management commands by filename under
`interface/cli/management/commands/`, the way DRF's router needs `VIEWS` walked
explicitly. It is here so the two interfaces can be read side by side - `views.py`
says what HTTP serves, this says what argv serves, and both point at the same use
cases underneath.

`tests/scaffolding/test_conventions.py` asserts the table and the command modules
agree, so it is checked documentation rather than a comment that rots.

`loadreference` is absent on purpose: it seeds public reference data, which is
data-layer work, so it lives under `data/management/commands/`.
"""

from .domain.access import use_cases as access
from .domain.balances import use_cases as balances
from .domain.billing import use_cases as billing
from .domain.expenses import payees as expense_payees
from .domain.expenses import use_cases as expenses
from .domain.extractos import use_cases as extractos
from .domain.inflation import use_cases as inflation
from .domain.market import use_cases as market
from .domain.payments import use_cases as payments
from .domain.regularization import use_cases as regularization
from .domain.reporting import use_cases as reporting
from .domain.savings import use_cases as savings
from .domain.setup import use_cases as setup
from .domain.tax import use_cases as tax

# (command name, the use cases the command binds). Typed loosely on purpose: these
# are references for a reader to follow, never invoked from here, and naming their
# signatures would restate what the functions already say.
COMMANDS: list[tuple[str, tuple[object, ...]]] = [
    (
        "month",
        (
            billing.close_period,
            billing.draft_monthly,
            billing.portal_sheet,
            billing.record_portal_authorization,
            billing.link_payment,
        ),
    ),
    (
        "creditnote",
        (billing.cancel, billing.credit, billing.portal_sheet, billing.record_portal_authorization),
    ),
    (
        "movements",
        (
            extractos.load_report,
            extractos.reconcile,
            payments.import_payoneer,
            expenses.ruleset,
            expenses.categorize_all,
            expenses.category_totals,
            expense_payees.untriaged,
            expense_payees.name,
        ),
    ),
    ("valuation", (billing.valuation,)),
    ("rate", (billing.fetch_rate,)),
    ("crosswalk", (billing.crosswalk,)),
    ("catchup", (billing.catch_up,)),
    ("projection", (expenses.project, expenses.baseline)),
    ("inflation", (inflation.fetch, inflation.cross_reference)),
    ("market", (market.fetch, market.report)),
    (
        "experiment",
        (
            savings.run_experiment,
            savings.forecast,
            savings.experiment_report,
            savings.diagnose,
        ),
    ),
    ("balances", (balances.position, balances.derive, balances.record)),
    ("archive", (reporting.archive,)),
    ("penalty", (regularization.recategorization_penalty,)),
    ("taxpayer", (tax.taxpayer_status,)),
    ("register", (access.register_taxpayer, access.gaps)),
    ("setup", (setup.parse_bundle, setup.import_bundle, setup.export_bundle, setup.starter, setup.status)),
    # Identity rather than a domain use case: it writes the Google consent and
    # the local credential cache, and reaches no domain at all.
    ("login", ()),
]
