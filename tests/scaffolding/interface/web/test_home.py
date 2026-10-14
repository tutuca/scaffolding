"""The home page: who you are, your books, what is missing, and the way onward.

Three shapes in one day, and the reasons are worth keeping. `/profile/` was a
page beside the admin, which gave the tool two homes. Folding it onto the admin
index gave it one, at the cost of an `AdminSite` subclass and a template that
could not import what it wanted. This is the third: the home page *is* `/`, it
carries the app list itself, and the admin keeps every URL it had except the
index nobody now reaches.
"""

from datetime import date
from decimal import Decimal

import pytest
from django.test import Client
from django.urls import reverse

from scaffolding.data.enums import Division, Indicator, Role
from scaffolding.data.models import (
    Account,
    BaseUser,
    Contract,
    ExchangeRate,
    Goal,
    MarketIndex,
    Movement,
    PriceIndex,
    Result,
    Taxpayer,
)
from scaffolding.service.domain.expenses import use_cases as expenses
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db


@pytest.fixture
def browser(client: Client, user: BaseUser) -> Client:
    """Logged in and staff, which is what a Google signup is: `GatewayAdapter`
    calls `open_admin()` on every one. The admin index is behind `admin_view`,
    so without the flag every test here would only ever see a redirect."""
    user.record_name("Matías")
    user.open_admin()
    client.force_login(user)
    return client


def test_it_needs_a_login(client: Client) -> None:
    """One hop now: the home page is `LoginRequiredMixin`, so it sends a
    stranger straight to the gateway rather than through the admin's `/login/`."""
    response = client.get(reverse("home"), follow=True)

    assert response.redirect_chain[-1][0].startswith(reverse("account_login"))


def test_with_no_books_it_offers_the_one_field_that_matters(browser: Client) -> None:
    body = browser.get(reverse("home")).content.decode()

    assert "cuit" in body.lower()


def test_submitting_a_cuit_registers_the_books(browser: Client, user: BaseUser) -> None:
    response = browser.post(reverse("home"), {"tax_id": "20-12345678-9", "punto_venta": ""})

    active = BaseUser.objects.get(pk=user.pk).active_taxpayer
    assert response.status_code == 302
    assert active is not None and active.tax_id == "20123456789"


def test_a_cuit_somebody_holds_is_refused_on_the_form(browser: Client) -> None:
    """A refusal belongs on the field, not as a 500."""
    Taxpayer.objects.register(tax_id="20123456789")

    response = browser.post(reverse("home"), {"tax_id": "20123456789", "punto_venta": ""})

    assert response.status_code == 200
    assert "ya está registrado" in response.content.decode()


def test_with_books_it_says_what_is_missing(browser: Client) -> None:
    browser.post(reverse("home"), {"tax_id": "20123456789", "punto_venta": ""})

    body = browser.get(reverse("home")).content.decode()

    assert "certificado de ARCA" in body
    assert "contrato activo" in body


def test_it_offers_a_way_out(browser: Client) -> None:
    """The admin base only draws the user tools - the log-out link among them -
    when `has_permission`, which is `is_staff`. Signup sets it; without that the
    landing page is a room with no door."""
    body = browser.get(reverse("home")).content.decode()

    assert "logout" in body.lower()


def test_nothing_missing_is_said_by_saying_nothing(
    browser: Client, user: BaseUser, make_account: Maker[Account]
) -> None:
    """`No falta nada: podés emitir, proyectar y archivar.` stood where the gaps
    go once they were closed. A page that reports the absence of a problem is
    a line the person reads every day for nothing; the section is only there
    when something is."""
    body = browser.get(reverse("home")).content.decode()

    assert "No falta nada" not in body


def test_a_closed_gap_stops_being_shown(browser: Client, user: BaseUser, make_account: Maker[Account]) -> None:
    """`make_account` brings the `taxpayer` fixture with it, which holds
    20123456789 - so these books need a different CUIT."""
    browser.post(reverse("home"), {"tax_id": "30111111118", "punto_venta": "5"})
    make_account(taxpayer=BaseUser.objects.get(pk=user.pk).active_taxpayer)

    body = browser.get(reverse("home")).content.decode()

    # The anchor: a gap that is still open. Without it the two absences below
    # also pass on a 500, an empty body, or a renamed gap.
    assert "certificado de ARCA" in body
    assert "punto de venta" not in body
    assert "cuentas" not in body


def test_the_way_into_the_admin_is_the_nav_and_not_a_table_list(browser: Client) -> None:
    """The home page shadows the admin index at `/`, so it owes the reader a
    way in. Until 2026-10-04 that was the admin's app list repeated on the
    page, beside the list of taxpayers; neither said anything the nav's one
    link does not, and both went."""
    browser.post(reverse("home"), {"tax_id": "20123456789", "punto_venta": "5"})

    body = browser.get(reverse("home")).content.decode()

    assert "/data/invoice/" in body
    assert "Tablas" not in body and "Contribuyentes" not in body


def test_it_offers_the_books_once_there_are_books(browser: Client) -> None:
    """The books, straight from the nav - no shelf. A link and not a mention:
    the pages are served by the same process and session, so there is nothing
    to explain. An account that has not registered a CUIT has nothing to
    explore, and the page it gets asks for the CUIT and nothing else.
    """
    browser.post(reverse("home"), {"tax_id": "20123456789", "punto_venta": "5"})

    body = browser.get(reverse("home")).content.decode()

    assert reverse("movimientos") in body
    assert reverse("inversiones") in body


def test_an_account_with_no_books_is_asked_for_a_cuit_and_nothing_else(browser: Client) -> None:
    """The whole of onboarding, deliberately. Everything else has an admin page
    already, and a wizard would need a completed state that does not exist."""
    body = browser.get(reverse("home")).content.decode()

    assert "cuit" in body.lower()
    assert reverse("movimientos") not in body
    assert reverse("inversiones") not in body


@pytest.fixture
def steady(
    browser: Client,
    user: BaseUser,
    taxpayer: Taxpayer,
    make_contract: Maker[Contract],
    make_exchange_rate: Maker[ExchangeRate],
    scale_aug_2026: None,
) -> Client:
    """A member whose ledger the projection accepts, with one planned goal -
    the shape the four health indicators need to say anything. A quote is
    part of that shape: the income is converted at the one in force."""
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    make_contract(fee_amount=Decimal(6000), fee_currency="USD", is_active=True)
    make_exchange_rate(date=date(2026, 8, 31), value=Decimal(1500))
    Goal.objects.create(
        taxpayer=taxpayer,
        title="colchón",
        amount=Decimal(1000),
        currency="USD",
        target_date=date(2027, 3, 1),
    )
    Movement.objects.create(
        taxpayer=taxpayer,
        source="GALICIA",
        date=date(2026, 8, 5),
        description="alquiler",
        inflow=None,
        outflow=Decimal(1000),
        currency="ARS",
        reference="g8",
    )
    return browser


def test_the_indicators_lead_with_their_references(steady: Client) -> None:
    body = steady.get(reverse("home")).content.decode()

    assert "50/30/20" in body
    assert "colchón" in body
    assert "monotributo" in body.lower()
    assert 'class="indicators"' in body


def test_the_income_is_converted_at_the_quote_in_force(steady: Client, make_exchange_rate: Maker[ExchangeRate]) -> None:
    """`sobre un ingreso de 9,078,000` stood on the page from 2026-09-19 to
    2026-10-04: 6,000 USD at a constant the books carried. The reference now
    reads the table, and the most recent quote wins over the fixture's."""
    make_exchange_rate(date=date(2026, 9, 30), value=Decimal(1600))

    body = steady.get(reverse("home")).content.decode()

    assert "sobre un ingreso de 9,600,000" in body


def test_without_a_quote_the_indicators_stay_off(
    browser: Client, user: BaseUser, taxpayer: Taxpayer, make_contract: Maker[Contract], scale_aug_2026: None
) -> None:
    """A contract and no rate: the projection has nothing to convert at, and
    the page carries on without the section rather than inventing one."""
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    make_contract(fee_amount=Decimal(6000), fee_currency="USD", is_active=True)

    response = browser.get(reverse("home"))

    assert response.status_code == 200
    assert 'class="indicators"' not in response.content.decode()


def test_the_glance_draws_the_last_months_and_weeks(
    steady: Client, taxpayer: Taxpayer, monkeypatch: pytest.MonkeyPatch
) -> None:
    """Pinned to 2026-10-04 so the fixture's August movement stays inside the
    windows; the suite ran in October and an unpinned calendar had emptied the
    projection tests once already. September's own spend is this test's."""
    monkeypatch.setattr(expenses.timezone, "localdate", lambda: date(2026, 10, 4))
    Movement.objects.create(
        taxpayer=taxpayer,
        source="GALICIA",
        date=date(2026, 9, 10),
        description="super",
        inflow=None,
        outflow=Decimal(2500),
        currency="ARS",
        reference="g9",
    )

    body = steady.get(reverse("home")).content.decode()

    assert 'data-chart="flows"' in body
    assert 'data-chart="trajectory"' in body
    assert body.index('data-chart="trajectory"') < body.index("La partición")
    assert '<spending-telescope class="chart narrow" source="weeks">' in body
    assert "Gastado en 2026-09" in body and "2,500" in body
    assert "Gasto semanal" in body and "26 semanas" in body


def test_the_home_lists_the_last_sync_dates(steady: Client, taxpayer: Taxpayer) -> None:
    """The at-a-glance status: each feeder's last write, beside the health boxes."""
    PriceIndex.objects.publish(
        readings=[
            (date(2026, 7, 1), Division.NIVEL_GENERAL, Decimal("100.0000")),
            (date(2026, 8, 1), Division.NIVEL_GENERAL, Decimal("104.0000")),
        ]
    )
    MarketIndex.objects.publish(readings=[(date(2026, 10, 7), Indicator.TAMAR, Decimal("23.75"))])
    Result.objects.record(taxpayer_id=taxpayer.pk, name="rem", date=date(2026, 10, 7), payload={})

    body = steady.get(reverse("home")).content.decode()

    assert "Al día" in body
    assert "IPC" in body and "2026-08" in body
    assert "Mercado" in body and "2026-10-07" in body
    assert "Experimento" in body
    assert "Movimientos" in body


def test_the_home_folds_inflation_into_the_flows_chart(steady: Client) -> None:
    """No standalone index or wage figure: inflation lives in the flows chart."""
    PriceIndex.objects.publish(
        readings=[
            (date(2026, 7, 1), Division.NIVEL_GENERAL, Decimal("100.0000")),
            (date(2026, 8, 1), Division.NIVEL_GENERAL, Decimal("104.0000")),
        ]
    )

    body = steady.get(reverse("home")).content.decode()

    assert 'data-chart="inflation"' not in body
    assert 'data-chart="real_wage"' not in body
    assert "El salario" not in body
    assert "deflactado por IPC" in body
    assert 'data-chart="flows"' in body


def test_a_bare_ledger_shows_no_indicators_and_still_answers(
    browser: Client, user: BaseUser, taxpayer: Taxpayer
) -> None:
    """No contract means the projection refuses; the page carries on without
    the section rather than answering 500."""
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)

    response = browser.get(reverse("home"))

    assert response.status_code == 200
    assert 'class="indicators"' not in response.content.decode()
