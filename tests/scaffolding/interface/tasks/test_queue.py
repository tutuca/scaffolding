"""The queue's housekeeping: old results go, recent ones stay, the cycle keeps one link."""

from datetime import timedelta

import pytest
from django.db.models import QuerySet
from django.tasks import TaskResultStatus
from django.utils import timezone
from django_tasks_db.models import DBTaskResult

from scaffolding.interface.tasks.queue import WEEK, prune_tasks
from tests.conftest import RunTask

pytestmark = pytest.mark.django_db(databases={"default", "tasks"}, transaction=True)


@pytest.fixture
def finished(run_task: RunTask) -> DBTaskResult:
    """One finished task's row - prune itself, drained once."""
    return DBTaskResult.objects.get(id=run_task(prune_tasks).id)


def pending_prunes() -> QuerySet[DBTaskResult]:
    return DBTaskResult.objects.filter(status=TaskResultStatus.READY, task_path=prune_tasks.module_path)


def test_prune_drops_results_older_than_a_week(finished: DBTaskResult, run_task: RunTask) -> None:
    """A row finished over a week ago - kwargs and return value with it - is gone."""
    DBTaskResult.objects.filter(id=finished.id).update(finished_at=timezone.now() - WEEK - timedelta(hours=1))

    run_task(prune_tasks)

    assert not DBTaskResult.objects.filter(id=finished.id).exists()


def test_prune_keeps_this_week_s_results(finished: DBTaskResult, run_task: RunTask) -> None:
    """A recent result stays readable."""
    run_task(prune_tasks)

    assert DBTaskResult.objects.filter(id=finished.id).exists()


def test_prune_schedules_itself_a_week_out(run_task: RunTask) -> None:
    """One enqueue starts the weekly cycle."""
    run_task(prune_tasks)

    (next_run,) = pending_prunes()
    assert next_run.run_after > timezone.now() + WEEK - timedelta(minutes=1)


def test_a_second_chain_does_not_double_the_cycle(run_task: RunTask) -> None:
    """A run that finds a prune already waiting schedules nothing more."""
    prune_tasks.using(run_after=timezone.now() + WEEK).enqueue()

    run_task(prune_tasks)

    assert pending_prunes().count() == 1
