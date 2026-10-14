"""The plain admins: one row of config per model, registered from one table.

The shape `serializers.base.plain` gave the wire shapes and `service.base.crud`
the viewsets: an admin whose whole body is `list_display` plus a filter is a
row, not a file (ARCHITECTURE, "Data, not hierarchy"). A row is
`(model, base, attributes)` - `OwnedAdmin` for owned models, Django's own for
reference tables. Admins with behaviour of their own keep their file beside
this one. A narrative that used to be a class docstring is a comment above its
row: a table has no docstrings to swallow a body.
"""

from django.contrib import admin

from ..models.account import Account
from ..models.account_balance import AccountBalance
from ..models.autonomos_contribution import AutonomosContribution
from ..models.bill_issuer import BillIssuer
from ..models.category_group import CategoryGroup
from ..models.category_override import CategoryOverride
from ..models.category_rule import CategoryRule
from ..models.client import Client
from ..models.compensatory_rate import CompensatoryRate
from ..models.contract import Contract
from ..models.cutoff import Cutoff
from ..models.exchange_rate import ExchangeRate
from ..models.expense import Expense
from ..models.goal import Goal
from ..models.investment_plan import InvestmentPlan
from ..models.investment_plan_kind import InvestmentPlanKind
from ..models.labor_index import LaborIndex
from ..models.legal_threshold import LegalThreshold
from ..models.market_index import MarketIndex
from ..models.monotributo_scale import MonotributoScale
from ..models.monotributo_status import MonotributoStatus
from ..models.movement import Movement
from ..models.nav_point import NavPoint
from ..models.obligation import Obligation
from ..models.parameter import Parameter
from ..models.payment import Payment
from ..models.price_index import PriceIndex
from ..models.result import Result
from ..models.scenario import Scenario
from .base import OwnedAdmin

# (model, base, attributes)
PLAIN: list[tuple[type, type[admin.ModelAdmin], dict[str, object]]] = [
    (Account, OwnedAdmin, {"list_display": ("__str__", "bank_name", "is_local", "is_liability", "is_active")}),
    # The one table in this project filled in by hand every month: four rows, one
    # per account, read off the statements. `scaffolding balances` is the same write
    # from argv and prints the position back.
    (
        AccountBalance,
        OwnedAdmin,
        {"list_display": ("account", "as_of", "amount"), "list_filter": ("account",), "date_hierarchy": "as_of"},
    ),
    (
        AutonomosContribution,
        admin.ModelAdmin,
        {"list_display": ("valid_from", "monthly_amount"), "list_filter": ("valid_from",)},
    ),
    # Where regrouping happens. Editing here is the point of the table being in
    # the admin, so the two labels are list-editable.
    (
        CategoryGroup,
        admin.ModelAdmin,
        {
            "list_display": (
                "category",
                "grupo",
                "bucket",
                "extracted",
                "committed",
                "real_outflow",
                "card_payment",
                "price_basis",
            ),
            "list_filter": ("bucket", "grupo", "extracted", "committed", "real_outflow"),
            "list_editable": ("grupo", "bucket"),
            "search_fields": ("category", "grupo"),
        },
    ),
    # How this taxpayer's statement lines are read: the rules in the order they are tried, and the
    # payees named by hand. What used to be tuples in the code and a TSV on disk.
    (
        CategoryRule,
        OwnedAdmin,
        {
            "list_display": ("direction", "position", "pattern", "category", "source"),
            "list_filter": ("direction", "source"),
            "search_fields": ("pattern", "category__category"),
        },
    ),
    (
        CategoryOverride,
        OwnedAdmin,
        {"list_display": ("fragment", "op", "amount", "category"), "search_fields": ("fragment", "category__category")},
    ),
    (BillIssuer, OwnedAdmin, {"list_display": ("marker", "parser")}),
    (
        Parameter,
        OwnedAdmin,
        {"list_display": ("name", "date", "source"), "list_filter": ("name",), "date_hierarchy": "date"},
    ),
    (
        Client,
        OwnedAdmin,
        {
            "list_display": ("name", "country_code", "arca_country_cuit", "email"),
            "search_fields": ("name", "legal_name"),
        },
    ),
    (
        CompensatoryRate,
        admin.ModelAdmin,
        {"list_display": ("valid_from", "monthly_rate"), "list_filter": ("valid_from",)},
    ),
    (
        Contract,
        OwnedAdmin,
        {
            "list_display": ("title", "client", "fee_amount", "fee_currency", "effective_date", "is_active"),
            "list_filter": ("is_active", "client"),
        },
    ),
    # Closing the books is a decision, so it is made here and kept. Adding a row
    # freezes every reading dated on or before it, in those books only:
    # `balances derive` and `balances set` refuse to write into a closed period.
    (Cutoff, OwnedAdmin, {"list_display": ("through", "notes")}),
    (
        ExchangeRate,
        admin.ModelAdmin,
        {
            "list_display": ("date", "currency", "value", "source"),
            "list_filter": ("currency", "source"),
            "date_hierarchy": "date",
        },
    ),
    (
        Expense,
        OwnedAdmin,
        {
            "list_display": ("date", "source", "category", "description", "currency", "outflow"),
            "list_filter": ("category", "source"),
            "date_hierarchy": "date",
            "search_fields": ("description", "reference"),
        },
    ),
    (
        Goal,
        OwnedAdmin,
        {
            "list_display": ("title", "target_date", "currency", "amount", "status"),
            "list_filter": ("status", "currency"),
            "date_hierarchy": "target_date",
        },
    ),
    (
        InvestmentPlan,
        OwnedAdmin,
        {
            "list_display": ("kind", "institution", "date_start", "duration", "currency", "principal"),
            "list_filter": ("institution", "currency", "kind"),
            "date_hierarchy": "date_start",
        },
    ),
    # Where a new kind is uploaded. Editing `conditions` here is the point of the
    # table being in the admin.
    (InvestmentPlanKind, admin.ModelAdmin, {"list_display": ("name",), "search_fields": ("name",)}),
    (
        LaborIndex,
        admin.ModelAdmin,
        {
            "list_display": ("period", "series", "value"),
            "list_filter": ("series",),
            "date_hierarchy": "period",
            "ordering": ("-period", "series"),
        },
    ),
    (
        LegalThreshold,
        admin.ModelAdmin,
        {"list_display": ("valid_from", "amount"), "list_filter": ("valid_from",)},
    ),
    (
        MarketIndex,
        admin.ModelAdmin,
        {
            "list_display": ("date", "indicator", "value", "source"),
            "list_filter": ("indicator", "source"),
            "date_hierarchy": "date",
            "ordering": ("-date", "indicator"),
        },
    ),
    (
        MonotributoScale,
        admin.ModelAdmin,
        {
            "list_display": ("valid_from", "category", "annual_income_cap", "monthly_fee_services"),
            "list_filter": ("valid_from",),
        },
    ),
    (MonotributoStatus, OwnedAdmin, {"list_display": ("category", "since")}),
    # Where a one-off gets its name: set both, and `categorize` leaves the row alone.
    (
        Movement,
        OwnedAdmin,
        {
            "list_display": ("date", "source", "currency", "inflow", "outflow", "description", "category", "pinned"),
            "list_filter": ("pinned", "source", "currency", "kind", "category"),
            "date_hierarchy": "date",
            "search_fields": ("description", "reference"),
            "list_editable": ("category", "pinned"),
        },
    ),
    (
        NavPoint,
        admin.ModelAdmin,
        {
            "list_display": ("fund", "date", "value"),
            "list_filter": ("fund",),
            "date_hierarchy": "date",
            "ordering": ("fund", "-date"),
        },
    ),
    # `ends_on` is the field worth filling: an obligation without one never
    # finishes, and a schedule that never finishes reads as debt forever.
    (
        Obligation,
        OwnedAdmin,
        {
            "list_display": ("label", "currency", "monthly_amount", "starts_on", "ends_on", "reference"),
            "list_filter": ("currency",),
        },
    ),
    (
        Payment,
        OwnedAdmin,
        {
            "list_display": ("date", "source", "currency", "inflow", "invoice", "reference"),
            "list_filter": ("source", "currency"),
            "date_hierarchy": "date",
            "search_fields": ("description", "reference"),
        },
    ),
    (
        PriceIndex,
        admin.ModelAdmin,
        {
            "list_display": ("period", "division", "value"),
            "list_filter": ("division",),
            "date_hierarchy": "period",
            "ordering": ("-period", "division"),
        },
    ),
    (
        Result,
        OwnedAdmin,
        {
            "list_display": ("name", "date", "payload"),
            "list_filter": ("name",),
            "date_hierarchy": "date",
            "ordering": ("name", "-date"),
        },
    ),
    (
        Scenario,
        admin.ModelAdmin,
        {
            "list_display": ("name", "date", "payload"),
            "list_filter": ("name",),
            "date_hierarchy": "date",
            "ordering": ("name", "-date"),
        },
    ),
]


def register() -> None:
    """One `ModelAdmin` per row, built from its config - the `@admin.register`
    the table replaces, fired from `__init__`'s import side effect."""
    for model, base, config in PLAIN:
        admin.site.register(model, type(f"{model.__name__}Admin", (base,), config))
