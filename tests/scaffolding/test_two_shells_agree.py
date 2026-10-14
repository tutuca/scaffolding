"""Architecture rule 6 through real interfaces, with independent expected results.

Each parametrized case gets fresh rows. Agreement alone is insufficient: both
interfaces must satisfy the worked model/domain example in fixtures.billing.
"""

from datetime import date
from decimal import Decimal
from pathlib import Path

import pytest
from django.core.management import CommandError
from django.test import Client
from django.urls import reverse as web_reverse
from pytest_django.fixtures import Settings
from rest_framework.test import APIClient

from scaffolding.data.enums import Bucket, Role
from scaffolding.data.models import BaseUser, CategoryGroup, Contract, ExchangeRate, Expense, Invoice, Payment, Taxpayer
from scaffolding.service.domain.billing import use_cases as billing
from tests.api import reverse
from tests.fixtures.billing import BillingCase, assert_authorized, assert_draft
from tests.fixtures.cli import Runner
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db


@pytest.fixture
def paid(make_payment: Maker[Payment]) -> Payment:
    """The worked month's money, on record: neither shell can say unpaid yet."""
    return make_payment(
        inflow=Decimal("5940.00"),
        date=date(2026, 9, 1),
        reference="9000000001",
        description="Payment from Acme - XX-123456",
    )


@pytest.mark.parametrize("interface", ["cli", "http"])
def test_portal_round_trip_preserves_the_model_contract(
    interface: str,
    api: APIClient,
    run: Runner,
    taxpayer: Taxpayer,
    billing_case: BillingCase,
    billing_contract: Contract,
    billing_rate: ExchangeRate,
    paid: Payment,
) -> None:
    case = billing_case
    if interface == "cli":
        printed = run("month", case.period, "--draft", "--fecha-emision", case.emission.isoformat())
        assert "Escribí esto en Comprobantes en línea" in printed
        invoice = Invoice.objects.owned_by(taxpayer.pk).get()
    else:
        response = api.post(
            reverse("invoice-draft"),
            {
                "contract_id": billing_contract.pk,
                "periodo_desde": case.start.isoformat(),
                "periodo_hasta": case.end.isoformat(),
                "fecha_emision": case.emission.isoformat(),
                "punto_venta": case.point,
                "description": case.description,
            },
            format="json",
        )
        assert response.status_code == 201, response.content
        invoice = Invoice.objects.get(pk=response.data["id"])
        sheet = api.get(reverse("invoice-portal-sheet", {"pk": invoice.pk}))
        assert sheet.status_code == 200
        assert (sheet.data["amount"], sheet.data["rate"]) == ("6000.00", "1480.000000")
    assert invoice.taxpayer_id == taxpayer.pk
    assert invoice.contract_id == billing_contract.pk
    assert_draft(invoice, case)

    if interface == "cli":
        run(
            "month",
            case.period,
            "--cae",
            case.cae,
            "--numero",
            str(case.number),
            "--vencimiento",
            case.expiry.isoformat(),
        )
    else:
        response = api.post(
            reverse("invoice-record-authorization", {"pk": invoice.pk}),
            {
                "cae": case.cae,
                "numero": case.number,
                "fecha_emision": case.emission.isoformat(),
                "cae_vencimiento": case.expiry.isoformat(),
            },
            format="json",
        )
        assert response.status_code == 200, response.content
    assert_authorized(invoice, case)
    assert Invoice.objects.owned_by(taxpayer.pk).count() == 1


@pytest.mark.parametrize("interface", ["cli", "http"])
def test_a_second_portal_authorization_is_refused_without_writes(
    interface: str, api: APIClient, run: Runner, billing_authorized: Invoice, billing_case: BillingCase
) -> None:
    case = billing_case
    before = Invoice.objects.values().get(pk=billing_authorized.pk)
    if interface == "cli":
        with pytest.raises(CommandError, match="Only DRAFT"):
            run(
                "month",
                case.period,
                "--cae",
                case.cae,
                "--numero",
                str(case.number),
                "--vencimiento",
                case.expiry.isoformat(),
            )
    else:
        response = api.post(
            reverse("invoice-record-authorization", {"pk": billing_authorized.pk}),
            {
                "cae": case.cae,
                "numero": case.number,
                "fecha_emision": case.emission.isoformat(),
                "cae_vencimiento": case.expiry.isoformat(),
            },
            format="json",
        )
        assert response.status_code == 400
        assert "Only DRAFT" in response.data["detail"]
    assert Invoice.objects.values().get(pk=billing_authorized.pk) == before


@pytest.mark.parametrize("interface", ["admin", "cli"])
@pytest.mark.usefixtures("starter_setup")
def test_naming_a_movement_pins_it_and_recategorizes_the_rest(
    interface: str, taxpayer: Taxpayer, make_expense: Maker[Expense], run: Runner, settings: Settings, tmp_path: Path
) -> None:
    CategoryGroup.objects.publish(category="nafta", grupo="transporte", bucket=Bucket.NEEDS)
    chosen = make_expense(reference="A-1", description="YPF RUTA 9", outflow=Decimal(50000), category=None)
    other = make_expense(reference="A-2", description="YPF RUTA 9", outflow=Decimal(50000), category=None)

    if interface == "cli":
        run("movements", "triage", "--name", f"{chosen.reference}=nafta")
    else:
        staff = BaseUser.objects.create_user("staff@example.com", is_staff=True)
        staff.join(taxpayer, role=Role.OWNER)
        staff.look_at(taxpayer)
        browser = Client()
        browser.force_login(staff)
        response = browser.post(
            web_reverse("admin:data_untriaged_changelist"),
            {
                "form-TOTAL_FORMS": "1",
                "form-INITIAL_FORMS": "1",
                "form-MIN_NUM_FORMS": "0",
                "form-MAX_NUM_FORMS": "1000",
                "form-0-id": chosen.pk,
                "form-0-category": "nafta",
                "_save": "Save",
            },
        )
        assert response.status_code == 302

    chosen.refresh_from_db()
    other.refresh_from_db()
    assert (chosen.category_id, chosen.pinned) == ("nafta", True)
    assert (other.category_id, other.pinned) == ("nafta", False)


def test_a_second_taxpayers_books_are_not_reachable_from_the_first(
    api: APIClient,
    other_taxpayer: Taxpayer,
    make_contract: Maker[Contract],
    billing_case: BillingCase,
    billing_rate: ExchangeRate,
) -> None:
    theirs = make_contract(taxpayer=other_taxpayer)
    drafted = billing.draft_monthly(taxpayer=other_taxpayer.pk, draft=billing_case.draft(theirs))

    assert api.get(reverse("invoice-portal-sheet", {"pk": drafted.id})).status_code == 404
    assert Invoice.objects.count() == 1
