"""Background tasks: `django.tasks` thin shells over the domain use cases.

Each module mirrors one `interface/cli/management/commands/` workflow. A task
collects JSON-safe inputs, wires its ports, and calls the same entry point the
CLI does - it owns no logic and no ORM writes of its own.

The queue uses a separate database. Callers scheduling work from a ledger
transaction must use `transaction.on_commit(partial(task.enqueue, ...),
using="default")`; `.enqueue()` itself writes immediately. See
`docs/INFRASTRUCTURE.md` for the transaction boundary.

Where the CLI is discovered by filename and the API is walked by a router, tasks
are imported by name: this package is the surface a caller imports, and
`TASK_MODULES` is the checked documentation of what it exposes - asserted by
`tests/scaffolding/test_conventions.py`, like `service/commands.py` for argv.
"""

from scaffolding.interface.tasks.archive import archive_year
from scaffolding.interface.tasks.balances import derive_balances, set_balance
from scaffolding.interface.tasks.experiment import run_experiment
from scaffolding.interface.tasks.inflation import fetch_inflation, fetch_ipc, fetch_labor
from scaffolding.interface.tasks.market import fetch_bcra, fetch_mirror
from scaffolding.interface.tasks.month import (
    authorize_month,
    draft_month,
    link_month_payment,
    record_month_cae,
    run_month,
)
from scaffolding.interface.tasks.movements import load_bill, load_movements, run_movements
from scaffolding.interface.tasks.queue import prune_tasks

# (module name, the tasks the module defines). Checked documentation, typed
# loosely on purpose like `service/commands.py`: a reader follows the reference
# rather than the signature, which the function already says.
TASK_MODULES: tuple[tuple[str, tuple[object, ...]], ...] = (
    ("market", (fetch_bcra, fetch_mirror)),
    ("inflation", (fetch_ipc, fetch_labor, fetch_inflation)),
    ("movements", (load_movements, load_bill, run_movements)),
    ("month", (run_month, draft_month, authorize_month, record_month_cae, link_month_payment)),
    ("balances", (derive_balances, set_balance)),
    ("archive", (archive_year,)),
    ("experiment", (run_experiment,)),
    ("queue", (prune_tasks,)),
)
