"""Background tasks: `django.tasks` thin shells over the domain use cases.

The queue uses a separate database. The sample domain needs no background work,
so the only task is the queue's own housekeeping: `prune_tasks` clears finished
results.
"""

from scaffolding.interface.tasks.queue import prune_tasks

__all__ = ["prune_tasks"]
