"""The queue's own housekeeping: prune what the worker has finished.

Mirrors `scaffolding prune_db_task_results`. A finished row keeps its kwargs and
return value - bank transcripts, bill text - so the `tasks` database holds
books-grade data until it is pruned. A week is long enough to read a failure and
short enough not to grow a second archive.

Scheduling is deliberately not this task's job: nothing here re-enqueues itself.
Run it weekly from a cron/launchd line (issue #4), the way the rest of the cadence
runs - `prune_tasks.enqueue()` then a `db_worker` pass, or the command directly.
"""

from datetime import timedelta

from django.core.management import call_command
from django.tasks import task

WEEK = timedelta(days=7)


@task
def prune_tasks() -> None:
    """Delete results finished more than a week ago."""
    call_command("prune_db_task_results", min_age_days=WEEK.days, verbosity=0)
