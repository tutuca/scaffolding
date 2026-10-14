"""The household's pages tell one story about its cash.

The home's savings line and the planes' queue are two views of the same money: they start
from the same peso, and a goal is paid in the same month on both. A figure that drew its own
opening cash or its own goal dates would be a second story, so the numbers are held side by
side here instead of each page's tests agreeing with itself.
"""

from datetime import date
from decimal import Decimal

import pytest

from scaffolding.data.models import Account, AccountBalance, Contract, ExchangeRate, Goal, Taxpayer
from scaffolding.service.domain.expenses import flows
from scaffolding.service.domain.planning import calc, deposits
from scaffolding.service.domain.planning import use_cases as planning
from tests.recipes.base import Maker

pytestmark = [pytest.mark.django_db, pytest.mark.usefixtures("scale_aug_2026")]

TODAY = date(2026, 10, 8)
RATE = Decimal(1500)


@pytest.fixture
def household(
    taxpayer: Taxpayer,
    make_contract: Maker[Contract],
    make_goal: Maker[Goal],
    make_exchange_rate: Maker[ExchangeRate],
    make_account: Maker[Account],
    make_account_balance: Maker[AccountBalance],
) -> None:
    make_contract(fee_amount=Decimal(6000), fee_currency="USD", is_active=True)
    make_exchange_rate(currency="USD", date=date(2026, 10, 1), value=RATE)
    make_goal(title="auto", amount=Decimal(2000), currency="USD", target_date=date(2027, 1, 1))
    make_goal(title="familia", amount=Decimal(1000), currency="USD", target_date=date(2027, 3, 1))
    caja = make_account(currency="ARS", label="caja")
    make_account_balance(account=caja, amount=Decimal(20_000_000), as_of=date(2026, 9, 30))


def test_the_home_and_the_queue_start_from_the_same_peso(taxpayer: Taxpayer, household: None) -> None:
    held = deposits.held_savings(taxpayer=taxpayer.pk, as_of=TODAY)
    queue = planning.readiness(taxpayer=taxpayer.pk, rate=RATE, as_of=TODAY)

    assert held == Decimal(20_000_000)
    assert any("saldo inicial 20,000,000" in note for note in queue.assumed)
    path = flows.trajectory(taxpayer=taxpayer.pk, as_of=TODAY, held=held)
    seen = [month for month in path.months if month.observed]
    first = path.months[len(seen)]
    # The line leaves today's holdings and adds only the plan's own month.
    assert first.cumulative - (path.months[len(seen) - 1].cumulative if seen else held) == pytest.approx(
        first.saved - first.landed
    )


def test_a_goal_is_paid_in_the_same_month_on_the_home_and_on_the_planes(taxpayer: Taxpayer, household: None) -> None:
    queue = planning.readiness(taxpayer=taxpayer.pk, rate=RATE, as_of=TODAY)
    middle = queue.outcomes[len(queue.outcomes) // 2].rows
    payments = calc.payments(middle)

    path = flows.trajectory(
        taxpayer=taxpayer.pk,
        as_of=TODAY,
        held=deposits.held_savings(taxpayer=taxpayer.pk, as_of=TODAY),
        payments=payments,
    )

    drawn = {title: month.period for month in path.months for title in month.landings}
    queued = {row.title: row.sequenced for row in middle if row.sequenced is not None}
    assert queued and drawn == queued
