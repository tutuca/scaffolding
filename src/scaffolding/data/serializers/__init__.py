"""The wire shapes, in one place.

Five resources carry a rule on the wire and keep their own module: `Account`
hides the bank identifiers, `Invoice` freezes what ARCA owns, and `Expense`,
`Payment` and `Settlement` each publish a computed figure. The rest say nothing
but "this model, every field", so they are a table - see `base.plain`.

`PLAIN` is keyed by model rather than by name: `service/views.py` already knows
the model it is routing, and a second spelling of the same noun is a second thing
to keep in step.
"""

from django.db import models
from rest_framework import serializers

from ..models import (
    AutonomosContribution,
    Client,
    CompensatoryRate,
    Contract,
    ExchangeRate,
    LegalThreshold,
    MonotributoScale,
    MonotributoStatus,
    Obligation,
)
from .account import AccountSerializer
from .base import plain
from .expense import ExpenseSerializer
from .invoice import InvoiceLineSerializer, InvoiceSerializer
from .payment import PaymentSerializer
from .settlement import SettlementSerializer

# A table, searched. Adding a CRUD resource is a row here and a row in `VIEWS`.
# `Goal` is deliberately absent: the goals resource carries a rule of its own and
# lives in `planning`, never behind the generic `plain`.
PLAIN: dict[type[models.Model], type[serializers.ModelSerializer]] = {
    model: plain(model)
    for model in (
        AutonomosContribution,
        Client,
        CompensatoryRate,
        Contract,
        ExchangeRate,
        LegalThreshold,
        MonotributoScale,
        MonotributoStatus,
        Obligation,
    )
}

WITH_RULES: dict[type[models.Model], type[serializers.ModelSerializer]] = {
    serializer.Meta.model: serializer
    for serializer in (AccountSerializer, ExpenseSerializer, InvoiceSerializer, PaymentSerializer, SettlementSerializer)
}


def of(model: type[models.Model]) -> type[serializers.ModelSerializer]:
    """The serializer for `model`, whether it carries a rule or not."""
    return WITH_RULES.get(model) or PLAIN[model]


__all__ = [
    "PLAIN",
    "WITH_RULES",
    "AccountSerializer",
    "ExpenseSerializer",
    "InvoiceLineSerializer",
    "InvoiceSerializer",
    "PaymentSerializer",
    "SettlementSerializer",
    "of",
]
