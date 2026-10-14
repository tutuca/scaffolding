"""model_bakery recipes, one per model. Loaded as a pytest plugin, so every
`make_<model>` is available anywhere without importing it."""

from .account import make_account
from .account_balance import make_account_balance
from .category_group import make_category_group
from .client import make_client
from .contract import contract, make_contract
from .cutoff import make_cutoff
from .exchange_rate import make_exchange_rate
from .expense import make_expense
from .goal import make_goal
from .investment_plan import make_investment_plan, make_investment_plan_kind
from .invoice import make_authorized_invoice, make_credit_note, make_invoice
from .invoice_line import make_invoice_line
from .market_index import make_market_index
from .monotributo_status import make_monotributo_status
from .nav_point import make_nav_point
from .obligation import make_obligation
from .payment import make_payment
from .price_index import make_price_index
from .result import make_result
from .scenario import make_scenario
from .settlement import make_settlement

__all__ = [
    "contract",
    "make_account",
    "make_account_balance",
    "make_authorized_invoice",
    "make_category_group",
    "make_client",
    "make_contract",
    "make_credit_note",
    "make_cutoff",
    "make_exchange_rate",
    "make_expense",
    "make_goal",
    "make_investment_plan",
    "make_investment_plan_kind",
    "make_invoice",
    "make_invoice_line",
    "make_market_index",
    "make_monotributo_status",
    "make_nav_point",
    "make_obligation",
    "make_payment",
    "make_price_index",
    "make_result",
    "make_scenario",
    "make_settlement",
]
