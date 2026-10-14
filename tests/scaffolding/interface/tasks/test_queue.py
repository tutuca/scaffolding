"""The queue's housekeeping: old results go, recent ones stay."""

from datetime import timedelta

import pytest
from django.utils import timezone
from django_tasks_db.models import DBTaskResult

from scaffolding.interface.adapter import bcra
from scaffolding.interface.tasks.market import fetch_bcra
from scaffolding.interface.tasks.queue import WEEK, prune_tasks
from tests.conftest import RunTask

pytestmark = pytest.mark.django_db(databases={"default", "tasks"}, transaction=True)


@pytest.fixture
def finished(monkeypatch: pytest.MonkeyPatch, run_task: RunTask) -> DBTaskResult:
    """One finished task's row, whatever its outcome."""
    monkeypatch.setattr(bcra, "build_client", lambda: None)
    return DBTaskResult.objects.get(id=run_task(fetch_bcra).id)


def test_prune_drops_results_older_than_a_week(finished: DBTaskResult, run_task: RunTask) -> None:
    """A row finished over a week ago - kwargs and return value with it - is gone."""
    DBTaskResult.objects.filter(id=finished.id).update(finished_at=timezone.now() - WEEK - timedelta(hours=1))

    run_task(prune_tasks)

    assert not DBTaskResult.objects.filter(id=finished.id).exists()


def test_prune_keeps_this_week_s_results(finished: DBTaskResult, run_task: RunTask) -> None:
    """A recent failure stays readable."""
    run_task(prune_tasks)

    assert DBTaskResult.objects.filter(id=finished.id).exists()
