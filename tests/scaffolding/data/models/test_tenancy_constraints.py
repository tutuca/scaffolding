"""Four unique constraints stated a per-CUIT rule as if it were global.

ARCA assigns puntos de venta per CUIT and numeración restarts at 1 within each,
so two taxpayers' first Factura E are both (4, 19, 1). Every one of these would
have rejected a second taxpayer's perfectly legal row.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.db.utils import IntegrityError

from scaffolding.data.enums import CbteTipo
from scaffolding.data.models import ExchangeRate, Invoice, Movement, ReversalEntry, Taxpayer
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db


def test_two_taxpayers_may_hold_the_same_comprobante_number(
    taxpayer: Taxpayer, other_taxpayer: Taxpayer, make_authorized_invoice: Maker[Invoice], august_rate: ExchangeRate
) -> None:
    # One rate row for both: ExchangeRate is reference data, shared across
    # taxpayers, and baking a second would collide on its own unique key.
    for owner in (taxpayer, other_taxpayer):
        make_authorized_invoice(
            taxpayer=owner, punto_venta=4, cbte_tipo=CbteTipo.FACTURA_E, numero=1, exchange_rate=august_rate
        )

    assert Invoice.objects.count() == 2


def test_one_taxpayer_may_not(
    taxpayer: Taxpayer, make_authorized_invoice: Maker[Invoice], august_rate: ExchangeRate
) -> None:
    make_authorized_invoice(
        taxpayer=taxpayer, punto_venta=4, cbte_tipo=CbteTipo.FACTURA_E, numero=1, exchange_rate=august_rate
    )

    with pytest.raises(IntegrityError):
        make_authorized_invoice(
            taxpayer=taxpayer, punto_venta=4, cbte_tipo=CbteTipo.FACTURA_E, numero=1, exchange_rate=august_rate
        )


def test_two_taxpayers_may_hold_the_same_arca_cmp_id(
    taxpayer: Taxpayer, other_taxpayer: Taxpayer, make_authorized_invoice: Maker[Invoice], august_rate: ExchangeRate
) -> None:
    """The WSFEX idempotency key is scoped to a CUIT, not to the world."""
    for owner in (taxpayer, other_taxpayer):
        make_authorized_invoice(taxpayer=owner, numero=1, arca_cmp_id=99, exchange_rate=august_rate)

    assert Invoice.objects.filter(arca_cmp_id=99).count() == 2


def test_two_taxpayers_may_hold_the_same_movement_reference(taxpayer: Taxpayer, other_taxpayer: Taxpayer) -> None:
    for owner in (taxpayer, other_taxpayer):
        Movement.objects.create(
            taxpayer=owner,
            source="GALICIA",
            date="2026-06-01",
            description="x",
            inflow=None,
            outflow=Decimal("100.00"),
            currency="ARS",
            reference="TX-1",
        )

    assert Movement.objects.filter(reference="TX-1").count() == 2


def test_two_taxpayers_may_hold_the_same_note_label(taxpayer: Taxpayer, other_taxpayer: Taxpayer) -> None:
    for owner in (taxpayer, other_taxpayer):
        ReversalEntry.objects.record(
            taxpayer=owner,
            note_label="21-00005-00000001",
            original_label="19-00005-00000004",
            fecha_emision=date(2026, 11, 13),
            net=Decimal("0.00"),
            net_ars=Decimal("-120000.00"),
            recorded={},
        )

    assert ReversalEntry.objects.count() == 2
