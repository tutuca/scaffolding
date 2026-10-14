"""Background tasks: `django.tasks` thin shells over the domain use cases.

A task collects JSON-safe inputs, wires its ports, and calls the same entry point
the CLI does - it owns no logic and no ORM writes of its own. The sample domain
needs no background work, so the only task is the queue's own housekeeping.

Where the CLI is discovered by filename and the API is walked by a router, tasks
are imported by name: this package is the surface a caller imports, and
`TASK_MODULES` is the checked documentation of what it exposes - asserted by
`tests/scaffolding/test_conventions.py`, like `service/commands.py` for argv.
"""

from scaffolding.interface.tasks.queue import prune_tasks

# (module name, the tasks the module defines). Checked documentation, typed
# loosely on purpose like `service/commands.py`: a reader follows the reference
# rather than the signature, which the function already says.
TASK_MODULES: tuple[tuple[str, tuple[object, ...]], ...] = (("queue", (prune_tasks,)),)

__all__ = ["TASK_MODULES", "prune_tasks"]
