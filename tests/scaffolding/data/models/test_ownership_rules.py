"""The two rules that keep a uniform taxpayer column from drifting."""

import pytest

from scaffolding.data.models import Contract, ExchangeRate, Invoice, Taxpayer
from scaffolding.exceptions import DomainRefusal
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db


def test_a_line_takes_its_taxpayer_from_the_invoice(
    taxpayer: Taxpayer, make_contract: Maker[Contract], august_rate: ExchangeRate
) -> None:
    """Never passed in, so it cannot disagree with the invoice it belongs to."""
    invoice = Invoice.objects.draft(
        taxpayer=taxpayer,
        contract=make_contract(taxpayer=taxpayer),
        punto_venta=5,
        fecha_emision=august_rate.date,
        periodo_desde=august_rate.date,
        periodo_hasta=august_rate.date,
        amount=august_rate.value,
        exchange_rate=august_rate,
        description="x",
    )

    assert {line.taxpayer_id for line in invoice.lines.all()} == {taxpayer.pk}


def test_drafting_against_another_taxpayers_contract_is_refused(
    taxpayer: Taxpayer, other_taxpayer: Taxpayer, make_contract: Maker[Contract], august_rate: ExchangeRate
) -> None:
    """No database constraint can span two tables, so the factory refuses."""
    with pytest.raises(DomainRefusal, match="otro contribuyente"):
        Invoice.objects.draft(
            taxpayer=taxpayer,
            contract=make_contract(taxpayer=other_taxpayer),
            punto_venta=5,
            fecha_emision=august_rate.date,
            periodo_desde=august_rate.date,
            periodo_hasta=august_rate.date,
            amount=august_rate.value,
            exchange_rate=august_rate,
            description="x",
        )
