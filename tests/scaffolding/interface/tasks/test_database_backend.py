"""The database backend: enqueue stores a READY row on `tasks`, the worker runs it.

The shell tests use the `run_task` fixture; these pin the backend's own contract —
queuing instead of running, the second database, and the worker draining the queue.
"""

from dataclasses import dataclass
from datetime import date
from decimal import Decimal
from functools import partial

import pytest
from django.core.management import call_command
from django.db import connections, transaction
from django.tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult

from scaffolding.data.enums import Indicator
from scaffolding.data.models import Account, AccountBalance, MarketIndex, Taxpayer
from scaffolding.interface.adapter import bcra
from scaffolding.interface.adapter.bcra.ports import MarketReading
from scaffolding.interface.tasks.balances import set_balance
from scaffolding.interface.tasks.market import fetch_bcra
from tests.conftest import RunTask
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db(databases={"default", "tasks"}, transaction=True)


@dataclass(frozen=True)
class StubBcra:
    """A BCRA source that answers with one reading."""

    def fetch(self) -> list[MarketReading]:
        return [MarketReading(date=date(2026, 10, 5), indicator=Indicator.TAMAR, value=Decimal("23.7500"))]


def test_enqueue_queues_instead_of_running(monkeypatch: pytest.MonkeyPatch) -> None:
    """Enqueue stores a READY row; the task runs only when a worker drains it."""
    monkeypatch.setattr(bcra, "build_client", StubBcra)

    result = fetch_bcra.enqueue()

    assert result.status == TaskResultStatus.READY
    assert MarketIndex.objects.count() == 0


def test_enqueue_lands_on_the_tasks_database(monkeypatch: pytest.MonkeyPatch, run_task: RunTask) -> None:
    """A queued task's row lives on `tasks`, reached through the router."""
    monkeypatch.setattr(bcra, "build_client", StubBcra)

    result = run_task(fetch_bcra)

    assert DBTaskResult.objects.using("tasks").filter(id=result.id).exists()


def test_the_tasks_table_is_not_on_the_ledger() -> None:
    """The ledger's database has no task table; the queue is a second SQLite."""
    tables = connections["default"].introspection.table_names()
    assert "django_tasks_database_dbtaskresult" not in tables


def test_the_worker_runs_a_queued_task(monkeypatch: pytest.MonkeyPatch, run_task: RunTask) -> None:
    """One worker pass drains the queued task into a successful result."""
    monkeypatch.setattr(bcra, "build_client", StubBcra)

    result = run_task(fetch_bcra)

    assert result.status == TaskResultStatus.SUCCESSFUL
    assert result.return_value == 1
    assert MarketIndex.objects.count() == 1


@pytest.mark.parametrize("commit", [True, False], ids=["commit", "rollback"])
def test_on_commit_queues_only_committed_ledger_work(
    taxpayer: Taxpayer, make_account: Maker[Account], commit: bool
) -> None:
    """The documented enqueue pattern waits for the ledger and discards a rollback."""
    with transaction.atomic(using="default"):
        account = make_account()
        transaction.on_commit(
            partial(
                set_balance.enqueue,
                taxpayer=taxpayer.pk,
                account=account.pk,
                as_of="2026-10-01",
                amount="1234.56",
            ),
            using="default",
        )
        assert not DBTaskResult.objects.exists()
        transaction.set_rollback(not commit, using="default")

    assert DBTaskResult.objects.count() == int(commit)
    call_command("db_worker", batch=True, verbosity=0)

    assert AccountBalance.objects.count() == int(commit)
    if commit:
        assert DBTaskResult.objects.get().status == TaskResultStatus.SUCCESSFUL
        written = AccountBalance.objects.get(account_id=account.pk, as_of=date(2026, 10, 1))
        assert written.amount == Decimal("1234.56")
    else:
        assert not Account.objects.filter(pk=account.pk).exists()
