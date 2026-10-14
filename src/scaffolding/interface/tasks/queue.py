"""The queue's own housekeeping: prune what the worker has finished, then come back.

Mirrors `scaffolding prune_db_task_results`. A finished row keeps its kwargs and
return value, so the `tasks` database holds books-grade data until it is pruned.
A week is long enough to read a failure and short enough not to grow a second
archive.

One enqueue starts the weekly cycle: after pruning, the task re-enqueues itself a
week out unless a prune is already waiting, so a second chain dies out on its own.
Seeding is still a human step (see `docs/INFRASTRUCTURE.md`) - cron-style
scheduling that would do the first enqueue is issue #4.
"""

from datetime import timedelta

from django.core.management import call_command
from django.tasks import TaskResultStatus, task
from django.utils import timezone
from django_tasks_db.models import DBTaskResult

WEEK = timedelta(days=7)


@task
def prune_tasks() -> None:
    """Delete results finished more than a week ago, then come back in a week."""
    call_command("prune_db_task_results", min_age_days=WEEK.days, verbosity=0)
    waiting = DBTaskResult.objects.filter(status=TaskResultStatus.READY, task_path=prune_tasks.module_path)
    if not waiting.exists():
        prune_tasks.using(run_after=timezone.now() + WEEK).enqueue()
