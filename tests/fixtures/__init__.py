"""Every shared fixture that is not a model_bakery recipe. Loaded as a pytest
plugin, so each is available anywhere without importing it."""

from .billing import billing_authorized, billing_case, billing_contract, billing_draft, billing_rate
from .cli import run
from .rates import august_rate, issued_rate, november_rate, reversal_rate
from .reversal import reversed_pair
from .scale import scale_aug_2026

__all__ = [
    "august_rate",
    "billing_authorized",
    "billing_case",
    "billing_contract",
    "billing_draft",
    "billing_rate",
    "issued_rate",
    "november_rate",
    "reversal_rate",
    "reversed_pair",
    "run",
    "scale_aug_2026",
]
