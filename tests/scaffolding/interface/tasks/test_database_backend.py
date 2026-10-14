"""The database backend: enqueue stores a READY row on `tasks`, the worker runs it.

The queue tests use the `run_task` fixture; these pin the backend's own contract -
queuing instead of running, the second database, and the worker draining the queue.
"""

import pytest
from django.db import connections
from django.tasks import TaskResultStatus
from django_tasks_db.models import DBTaskResult

from scaffolding.interface.tasks.queue import prune_tasks
from tests.conftest import RunTask

pytestmark = pytest.mark.django_db(databases={"default", "tasks"}, transaction=True)


def test_enqueue_queues_instead_of_running() -> None:
    """Enqueue stores a READY row; the task runs only when a worker drains it."""
    result = prune_tasks.enqueue()

    assert result.status == TaskResultStatus.READY


def test_enqueue_lands_on_the_tasks_database(run_task: RunTask) -> None:
    """A queued task's row lives on `tasks`, reached through the router."""
    result = run_task(prune_tasks)

    assert DBTaskResult.objects.using("tasks").filter(id=result.id).exists()


def test_the_tasks_table_is_not_on_the_ledger() -> None:
    """The ledger's database has no task table; the queue is a second SQLite."""
    tables = connections["default"].introspection.table_names()
    assert "django_tasks_database_dbtaskresult" not in tables


def test_the_worker_runs_a_queued_task(run_task: RunTask) -> None:
    """One worker pass drains the queued task into a successful result."""
    result = run_task(prune_tasks)

    assert result.status == TaskResultStatus.SUCCESSFUL
    assert result.return_value is None
