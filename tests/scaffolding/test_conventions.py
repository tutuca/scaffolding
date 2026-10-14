"""The architecture rules from docs/ARCHITECTURE.md, enforced.

Every rule here is one a reviewer would otherwise have to remember. They are
checked by reading the source, so they hold for code nobody has run yet.
"""

import ast
import importlib
import re
import subprocess
from pathlib import Path

import pytest
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.db import models
from django.tasks import Task

import scaffolding.data.admin  # noqa: F401 - triggers every @admin.register
from scaffolding.data import serializers, visibility
from scaffolding.data.admin.base import OwnedAdmin
from scaffolding.data.enums import Bucket
from scaffolding.data.models import Bill, InvoiceLine, Payment
from scaffolding.data.models.base import OwnedModel
from scaffolding.data.visibility import VISIBILITY
from scaffolding.interface.tasks import TASK_MODULES
from scaffolding.service.commands import COMMANDS
from scaffolding.service.domain.expenses.calc import INCOME
from scaffolding.service.domain.expenses.description import CBU, TAX_ID
from scaffolding.service.domain.inflation.calc import DIVISION_BY_CATEGORY
from scaffolding.service.domain.movements import use_cases as movements
from scaffolding.service.domain.setup import use_cases as setup
from scaffolding.service.views import RESOURCES

SRC = Path(__file__).resolve().parents[2] / "src" / "scaffolding"
MODELS = SRC / "data" / "models"

# Writes that bypass a model mutator. `update`/`bulk_update` also skip save(),
# so the frozen-field guard never sees them. Matched by attribute name, so a
# plain `dict.update()` in these layers trips it too - use `|=` there.
WRITES = frozenset({"save", "create", "get_or_create", "update_or_create", "update", "bulk_create", "bulk_update"})


def python_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "migrations" not in p.parts)


# `serializer.save()` is DRF writing through a serializer, not the ORM writing a
# row: the model mutator it eventually reaches is still the model's. Matched by
# the receiver's name because the AST has no types to tell them apart, which is
# the same reason `dict.update()` needs `|=` in these layers.
NOT_THE_ORM = frozenset({"serializer"})


def receiver_name(node: ast.Attribute) -> str:
    return node.value.id if isinstance(node.value, ast.Name) else ""


def write_calls(path: Path) -> list[tuple[int, str]]:
    """Every `x.save(...)`-shaped call in a file, with its line number."""
    tree = ast.parse(path.read_text())
    return [
        (node.lineno, node.func.attr)
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in WRITES
        and receiver_name(node.func) not in NOT_THE_ORM
    ]


def write_scan_roots() -> list[Path]:
    """Service, CLI and API files - not the adapter.

    The adapter is the boundary to outside systems (ARCA SOAP, Google Drive/Sheets),
    whose SDKs also name writes `create`/`update`. Those write to the outside world,
    never to the Django database, so the rule does not apply there.
    """
    interface = [path for path in python_files(SRC / "interface") if "adapter" not in path.parts]
    return python_files(SRC / "service") + interface


@pytest.mark.parametrize("path", write_scan_roots())
def test_only_models_write_to_the_database(path: Path) -> None:
    """Tom Christie's rule: `save()` and `create()` belong to the model that owns
    the table. Outside `data/models/`, ask for a named transition instead."""
    offenders = [f"{path.name}:{line} calls .{attr}()" for line, attr in write_calls(path)]

    assert not offenders, (
        f"{path.relative_to(SRC)} writes to the database directly: {offenders}. "
        "Add a mutator or factory to the model and call that instead "
        "(docs/ARCHITECTURE.md, 'Where logic lives')."
    )


def test_the_write_detector_actually_detects_writes() -> None:
    """Guards the guard: a rule that cannot fail protects nothing."""
    found = {attr for _, attr in write_calls(MODELS / "invoice.py")}

    assert {"save", "create"} <= found


def test_the_command_registry_matches_the_command_modules() -> None:
    """`service/commands.py` documents the CLI, so it has to stay true.

    It wires nothing - Django discovers commands by filename - which is exactly
    why it needs a test.
    """
    modules = {path.stem for path in python_files(SRC / "interface" / "cli") if path.parent.name == "commands"}
    modules.discard("__init__")

    assert modules == {name for name, _ in COMMANDS}


TASK_DIR = SRC / "interface" / "tasks"

# A task crosses the wire as JSON: its signature and return may name only these.
JSON_TYPES = frozenset({"str", "int", "float", "bool", "list", "dict", "tuple", "object"})


def is_task_decorator(dec: ast.expr) -> bool:
    """`@task` or `@task(...)`, the only two spellings django.tasks allows."""
    if isinstance(dec, ast.Name) and dec.id == "task":
        return True
    return isinstance(dec, ast.Call) and isinstance(dec.func, ast.Name) and dec.func.id == "task"


def task_functions(path: Path) -> list[ast.FunctionDef]:
    """Every module-level function a `@task` decorator wraps, in one file."""
    tree = ast.parse(path.read_text())
    return [
        node
        for node in tree.body
        if isinstance(node, ast.FunctionDef) and any(is_task_decorator(dec) for dec in node.decorator_list)
    ]


def non_json_names(annotation: ast.expr | None) -> set[str]:
    """Type names in an annotation that cannot cross the JSON boundary.

    `None` and `...` parse as constants, not names, so they pass through free.
    """
    if annotation is None:
        return set()
    return {node.id for node in ast.walk(annotation) if isinstance(node, ast.Name)} - JSON_TYPES


def test_the_task_registry_matches_the_task_modules() -> None:
    """`interface/tasks/__init__.py` documents the shell, so it has to stay true.

    Tasks are imported by name - no discovery walks them - which is exactly why
    the registry needs a test, like `COMMANDS` for argv.
    """
    modules = {path.stem for path in python_files(TASK_DIR) if path.stem != "__init__"}

    assert modules == {name for name, _ in TASK_MODULES}


def test_the_task_registry_names_each_module_s_actual_tasks() -> None:
    """The registry re-exports each module's tasks; a typo there rots silently."""
    for name, tasks in TASK_MODULES:
        assert tasks, f"{name} lists no tasks"
        assert all(isinstance(task, Task) for task in tasks), f"{name} lists something that is not a Task"
        module = importlib.import_module(f"scaffolding.interface.tasks.{name}")
        defined = {value for value in vars(module).values() if isinstance(value, Task)}
        assert set(tasks) == defined, f"{name}: the registry and the module disagree"


def test_tasks_are_keyword_only_and_json_safe() -> None:
    """A task's signature is the JSON boundary: keyword-only, JSON-safe in and out.

    `normalize_json` refuses a `date`, `Decimal` or model at enqueue time, so a
    task that names one in its signature is a task that can never run - the shell
    must bridge them to strings first.
    """
    offenders: list[str] = []
    for path in python_files(TASK_DIR):
        if path.stem == "__init__":
            continue
        for fn in task_functions(path):
            if fn.args.args or fn.args.posonlyargs:
                offenders.append(f"{path.name}:{fn.lineno} {fn.name} takes a positional argument")
            bad = non_json_names(fn.returns)
            for argument in [*fn.args.posonlyargs, *fn.args.args, *fn.args.kwonlyargs]:
                bad |= non_json_names(argument.annotation)
            if bad:
                offenders.append(f"{path.name}:{fn.lineno} {fn.name} names {sorted(bad)} across the JSON boundary")
    assert not offenders, "A task must be keyword-only and JSON-safe in and out: " + "; ".join(offenders)


def test_every_crud_row_has_a_serializer_and_every_plain_serializer_is_routed() -> None:
    """`RESOURCES` (service/views.py) and `PLAIN`/`WITH_RULES` (data/serializers)
    are one contract written twice; drift between them is a row routed with no
    shape, or a shape generated for no route. `Invoice` and `Payment` are the two
    serializers not in RESOURCES: each carries a rule of its own and is served by
    an ACTIONS viewset.
    """
    routed = {model for _, model, _ in RESOURCES}
    serializable = set(serializers.PLAIN) | set(serializers.WITH_RULES)
    missing_shape = sorted(model.__name__ for model in routed if model not in serializable)
    unrouted = sorted(
        model.__name__ for model in serializable if model not in routed and model.__name__ not in {"Invoice", "Payment"}
    )

    assert not missing_shape, f"{missing_shape} are routed in RESOURCES with no serializer"
    assert not unrouted, f"{unrouted} have serializers but no route"


def keys_with_inline_comments(path: Path) -> list[str]:
    """Keys whose value swallowed a trailing `# note`. Keys only: `.env` is secret."""
    return [
        line.split("=", 1)[0].strip()
        for line in path.read_text().splitlines()
        if "=" in line and not line.lstrip().startswith("#") and "#" in line.split("=", 1)[1]
    ]


def test_the_env_template_carries_no_inline_comments() -> None:
    """django-environ keeps a trailing `# note` as part of the value.

    `.env.example` is the file everyone copies, so a habit picked up here becomes
    a setting that silently contains its own documentation.
    """
    offenders = keys_with_inline_comments(SRC.parents[1] / ".env.example")

    assert not offenders, f"Move these comments to their own line: {offenders}"


def test_the_env_actually_loaded_carries_no_inline_comments() -> None:
    """The template test guards the file nobody runs on.

    A comment glued to `ARCA_AUTHORIZER` makes `get_authorizer()` raise
    ImproperlyConfigured, and the suite cannot see it: tests/settings.py
    overwrites both adapter settings for the whole suite. On a machine with no
    `.env` only the defaults load, so there is nothing to check and the
    assertion holds vacuously.
    """
    env = SRC.parents[1] / ".env"
    offenders = keys_with_inline_comments(env) if env.exists() else []

    assert not offenders, f"Move these comments to their own line in .env: {offenders}"


def test_the_env_template_defaults_to_the_offline_adapters() -> None:
    """`.env.example` is what a fresh clone copies; it must not point at ARCA -
    and not at `dry_run` either, which mints CAEs that read as real. `manual`
    mints nothing: the draft stops and names the portal."""
    template = (SRC.parents[1] / ".env.example").read_text().splitlines()

    assert "ARCA_AUTHORIZER=manual" in template
    assert "ARCA_RATE_PROVIDER=manual" in template


def test_the_taxpayer_cuit_is_not_committed() -> None:
    """A CUIT ties every record to a person, so none may be committed.

    Read from `REDACTED_CUIT` rather than named here, so this test does not
    become the place it appears. It read `TAXPAYER_CUIT` until the CUIT moved
    onto the `Taxpayer` row, where a test database cannot see it.

    Read rather than named, so this test does not become the place it appears.

    `-c -o --exclude-standard` is tracked *plus* untracked-but-committable. Tracked
    alone was the first version and it missed the case that matters: a recording
    copied out of `var/` and not yet staged passes, then the next `git add -A`
    commits it. Ignored paths - `.env`, `var/`, `etc/secrets/` - stay out.

    The CUIT counts as leaked only when it stands as its own token - a bare
    eleven-digit value in a table cell or `TAXPAYER_CUIT=…`. A longer identifier
    that merely *embeds* the digits - ARCA's own `MOREO_…pdf` filenames - passes,
    because redacting those would break the pointer to the document it names.

    With `REDACTED_CUIT` unset there is no needle: nothing this machine knows
    could have leaked, so the assertion holds vacuously. The check only bites
    where the real CUIT is configured.

    It knows only the taxpayer's own CUIT: a third party's tax id has no env
    needle. The rule-shape pin (`test_no_rule_keys_on_an_account_id`) covers the
    one place such an id leaked - a categorization rule - and the review watches
    the rest.
    """
    if not settings.REDACTED_CUIT:
        return
    root = SRC.parents[1]
    tracked = subprocess.run(
        ["git", "ls-files", "-z", "-c", "-o", "--exclude-standard"], cwd=root, capture_output=True, check=True
    )
    needle = re.compile(rb"\b" + re.escape(settings.REDACTED_CUIT.encode()) + rb"\b")
    offenders = [
        name
        for name in (raw.decode() for raw in tracked.stdout.split(b"\0") if raw)
        if (root / name).is_file() and needle.search((root / name).read_bytes())
    ]

    assert not offenders, f"Remove the taxpayer CUIT from: {offenders}"


PARSERS = SRC / "interface" / "adapter" / "extractos"
# What every Argentine statement spells the same way. These belong to
# `extractos/mapping.py`; a parser that redefines one is a parser that can
# disagree with its siblings about a decimal separator. `AMOUNT` is the amount
# pattern, `sides` the sign split - both hand-copied across the parsers before
# 2026-09-17.
SHARED_READERS = frozenset(
    {"ars", "sides", "short_date", "long_date", "spanish_date", "normalize_trailing_minus", "AMOUNT"}
)


@pytest.mark.parametrize("path", [p for p in python_files(PARSERS) if p.stem not in {"mapping", "ports", "__init__"}])
def test_no_parser_defines_its_own_amount_or_date_reader(path: Path) -> None:
    """Three hand-copied `ars()` functions is how two of them come to disagree.

    Each parser owns its institution's wire format and nothing else; the
    conventions they share are `mapping`'s. `AMOUNT` is a module-level pattern,
    not a function, so both `def` and assignment are checked.
    """
    defined: set[str] = set()
    for node in ast.parse(path.read_text()).body:
        if isinstance(node, ast.FunctionDef | ast.ClassDef):
            defined.add(node.name)
        elif isinstance(node, ast.Assign):
            defined.update(target.id for target in node.targets if isinstance(target, ast.Name))
    offenders = sorted(defined & SHARED_READERS)

    assert not offenders, f"{path.name} redefines {offenders}; import them from `extractos.mapping` instead."


def test_every_rule_category_has_a_grouping_shipped() -> None:
    """A leaf with no taxonomy row falls into `sin-agrupar` and reads as a hole.

    The starter pack ships its own vocabulary, so this checks the pack rather
    than the database: a rule added without grouping it fails here instead of
    landing silently in a bucket nobody chose.
    """
    pack = setup.starter()
    grouped = {entry.category for entry in pack.taxonomy}
    emitted = {rule.category for rule in (*pack.debit_rules, *pack.credit_rules)} | {INCOME}
    ungrouped = sorted(emitted - grouped)

    assert not ungrouped, f"{ungrouped} can be produced by a rule but has no grouping in the starter pack."


def test_no_rule_keys_on_an_account_id() -> None:
    """A categorization rule matches a payee's name, never an account.

    The alquiler rule once carried the landlord's 11-digit tax id: a rule keyed
    on an id files every transfer to that account as one thing and parks a
    personal identifier in the tree. Refused here by the two account shapes
    `description.py` knows - a tax id (11 digits, AFIP prefix) or a CBU (22) -
    appearing anywhere in a rule's pattern.
    """
    offenders = sorted(
        rule.pattern
        for rule in (*setup.starter().debit_rules, *setup.starter().credit_rules)
        if TAX_ID.search(rule.pattern) or CBU.search(rule.pattern)
    )

    assert not offenders, f"A rule keys on an account id: {offenders}"


def test_every_shipped_grouping_names_a_real_bucket() -> None:
    """A bucket outside the enum is a typo, not a design."""
    unknown = sorted({entry.bucket for entry in setup.starter().taxonomy} - set(Bucket.values))

    assert not unknown, f"{unknown} is not a Bucket."


def test_every_inflation_mapped_category_is_a_shipped_categoria() -> None:
    """A typo in the categoría -> division table would drop a categoría from `scaffolding
    inflation report` without a word, so the mapping is checked against the taxonomy
    that ships."""
    shipped = {entry.category for entry in setup.starter().taxonomy}
    missing = sorted(set(DIVISION_BY_CATEGORY) - shipped)

    assert not missing, f"{missing} is mapped to an IPC division but is not a shipped categoría."


# Every model in `data`, classified. A model added later belongs to exactly one
# of these, and the suite fails until someone says which - which is the point: an
# unclassified model is one whose tenancy nobody decided.
OWNED = frozenset(
    {
        "Client",
        "Contract",
        "Cutoff",
        "Account",
        "AccountBalance",
        "Invoice",
        "InvoiceLine",
        "Movement",
        "Bill",
        "Settlement",
        "Goal",
        "Obligation",
        "InvestmentPlan",
        "CategoryRule",
        "CategoryOverride",
        "BillIssuer",
        "Parameter",
        "MonotributoStatus",
        "ReversalEntry",
        "Result",
    }
)
# Public facts. A per-taxpayer copy of the monotributo scale would be a
# per-taxpayer copy of the law.
REFERENCE_MODELS = frozenset(
    {
        "MonotributoScale",
        "LegalThreshold",
        "ExchangeRate",
        "CompensatoryRate",
        "AutonomosContribution",
        "CategoryGroup",
        "InvestmentPlanKind",
        "PriceIndex",
        "MarketIndex",
        "LaborIndex",
        "NavPoint",
        "Scenario",
    }
)
# Neither ledger nor reference. Named so the gap does not read like an oversight.
IDENTITY_MODELS = frozenset({"BaseUser", "Taxpayer", "Membership"})


def concrete_models() -> list[type[models.Model]]:
    return [model for model in apps.get_app_config("data").get_models() if not model._meta.proxy]


def test_every_model_is_classified() -> None:
    named = OWNED | REFERENCE_MODELS | IDENTITY_MODELS
    found = {model.__name__ for model in concrete_models()}

    assert found == named, (
        f"unclassified: {sorted(found - named)}; stale: {sorted(named - found)}. "
        "Add it to OWNED, REFERENCE_MODELS or IDENTITY_MODELS - an unclassified "
        "model is one whose tenancy nobody decided."
    )


@pytest.mark.parametrize("name", sorted(OWNED))
def test_owned_models_carry_a_taxpayer(name: str) -> None:
    model = apps.get_model("data", name)

    assert issubclass(model, OwnedModel)
    assert hasattr(model._default_manager, "owned_by"), f"{name} needs owned_by (OwnedQuerySet)."


@pytest.mark.parametrize("name", sorted(REFERENCE_MODELS))
def test_reference_models_carry_no_taxpayer(name: str) -> None:
    """The test of the split: if a reference table needed a taxpayer in its
    unique key, it was never reference data."""
    assert not issubclass(apps.get_model("data", name), OwnedModel)


@pytest.mark.parametrize("name", sorted(OWNED))
def test_owned_unique_constraints_name_the_taxpayer_first(name: str) -> None:
    """A unique constraint on owned data that does not start with the taxpayer
    states a global rule where it means a per-CUIT one: ARCA numbers puntos de
    venta per CUIT, so two taxpayers' first Factura E are both (4, 19, 1)."""
    model = apps.get_model("data", name)
    offenders = [
        constraint.name
        for constraint in model._meta.constraints
        if isinstance(constraint, models.UniqueConstraint) and tuple(constraint.fields[:1]) != ("taxpayer",)
    ]

    assert not offenders, f"{name}: {offenders} would reject a second taxpayer's legal rows."


@pytest.mark.parametrize("name", sorted(OWNED))
def test_no_owned_model_is_globally_unique_on_a_column(name: str) -> None:
    """`unique=True` on a column cannot be scoped. Use a UniqueConstraint."""
    model = apps.get_model("data", name)
    offenders = [field.name for field in model._meta.local_fields if field.unique and not field.primary_key]

    assert not offenders, f"{name}.{offenders} is globally unique; make it a UniqueConstraint with taxpayer."


@pytest.mark.parametrize("name", sorted(OWNED))
def test_every_owned_model_is_visible_to_somebody_or_contained(name: str) -> None:
    """Minimal by default has a cost: a resource nobody can reach is dead weight
    nobody notices. Either a role grants it, or it belongs to something granted."""
    model_name = apps.get_model("data", name)._meta.model_name
    granted = {resource for row in VISIBILITY.values() for resource in row}

    assert visibility.root_of(model_name) in granted, (
        f"{name} is in no role's visibility row and is contained by nothing. "
        "Add it to data/visibility.py, or say what contains it."
    )


# Models whose rows belong to one taxpayer. A read of one that is not narrowed
# is a read of everybody's. `Payment`, `Expense` and `Untriaged` are proxies over
# `Movement`, so they read an owned table without being concrete models - which
# is why `OWNED`, built from the registry's concrete rows, does not list them.
OWNED_READS = OWNED | {"Payment", "Expense", "Untriaged"}

# Manager methods handed a taxpayer, or a row that already carries one, so they
# scope themselves: `draft` takes the taxpayer, `cancel`/`credit` take the
# comprobante, `record`/`in_force` take the account or the pks a narrowed read
# produced. Named rather than typed, for the reason `NOT_THE_ORM` is named: the
# AST cannot tell a factory from a query.
SCOPES_ITSELF = frozenset({"draft", "cancel", "credit", "record", "in_force", "plan", "replace", "declare"})


def declared_queryset(tree: ast.Module) -> set[int]:
    """DRF's `queryset = Model.objects.all()`: a declaration, not a read.

    Every viewset here inherits `ScaffoldingModelViewSet.get_queryset`, which narrows
    it with `owned_by` in the one place (`service/base.py`). There is no taxpayer
    at class-definition time, so this is the one site that cannot narrow itself.
    """
    return {
        id(inner)
        for node in ast.walk(tree)
        if isinstance(node, ast.Assign)
        and any(isinstance(target, ast.Name) and target.id == "queryset" for target in node.targets)
        for inner in ast.walk(node)
        if isinstance(inner, ast.Attribute) and inner.attr == "objects"
    }


def overrides_without_super(path: Path) -> list[int]:
    """Every `get_queryset` override that never calls `super().get_queryset()`."""
    found = []
    for node in ast.walk(ast.parse(path.read_text())):
        if not (isinstance(node, ast.FunctionDef) and node.name == "get_queryset"):
            continue
        calls_super = any(
            isinstance(inner, ast.Call)
            and isinstance(inner.func, ast.Attribute)
            and inner.func.attr == "get_queryset"
            and isinstance(inner.func.value, ast.Call)
            and isinstance(inner.func.value.func, ast.Name)
            and inner.func.value.func.id == "super"
            for inner in ast.walk(node)
        )
        if not calls_super:
            found.append(node.lineno)
    return found


@pytest.mark.parametrize("path", python_files(SRC / "service"))
def test_a_viewset_widens_the_narrowed_queryset_rather_than_replacing_it(path: Path) -> None:
    """What `declared_queryset` above rests on. `queryset = Invoice.objects.all()`
    is exempt from the unscoped-read rule only because `ScaffoldingModelViewSet`
    narrows it for every viewset - which an override that skips `super` undoes.
    InvoiceViewSet did exactly that once, and served every taxpayer's
    comprobantes until it was caught by hand."""
    if path == SRC / "service" / "base.py":
        return  # The base is where the narrowing is; it has no super to call.
    offenders = [f"{path.name}:{line}" for line in overrides_without_super(path)]

    assert not offenders, (
        f"{offenders}: get_queryset must widen `super().get_queryset()`, never rebuild from the manager - "
        "rebuilding drops the taxpayer narrowing and serves every taxpayer's rows."
    )


def test_the_super_detector_actually_detects(tmp_path: Path) -> None:
    """Guards the guard: the rebuilt form is caught, the widened one is not."""
    rebuilt = tmp_path / "rebuilt.py"
    rebuilt.write_text("class V:\n    def get_queryset(self):\n        return Invoice.objects.all()\n")
    widened = tmp_path / "widened.py"
    widened.write_text("class V:\n    def get_queryset(self):\n        return super().get_queryset().all()\n")

    assert overrides_without_super(rebuilt) == [2]
    assert overrides_without_super(widened) == []


def owned_reads(path: Path) -> list[tuple[int, str]]:
    """Every `Model.objects…` on an owned model that is not narrowed by `owned_by`.

    Walks the attribute chain rather than matching text, so
    `Invoice.objects.owned_by(t).authorized()` passes and
    `Invoice.objects.authorized()` does not.
    """
    tree = ast.parse(path.read_text())
    narrowed = {
        id(node.value)
        for node in ast.walk(tree)
        if isinstance(node, ast.Attribute) and node.attr in {"owned_by", *SCOPES_ITSELF}
    } | declared_queryset(tree)
    found = []
    for node in ast.walk(tree):
        if not (isinstance(node, ast.Attribute) and node.attr == "objects"):
            continue
        if not (isinstance(node.value, ast.Name) and node.value.id in OWNED_READS):
            continue
        if id(node) not in narrowed:
            found.append((node.lineno, node.value.id))
    return found


@pytest.mark.parametrize("path", write_scan_roots())
def test_owned_models_are_read_through_owned_by(path: Path) -> None:
    """Threading the taxpayer through the domains by hand missed one, and nothing
    failed. This is the rule that would have caught it."""
    offenders = [f"{path.name}:{line} reads {model}.objects unscoped" for line, model in owned_reads(path)]

    assert not offenders, (
        f"{path.relative_to(SRC)}: {offenders}. Narrow with `.owned_by(taxpayer)` - "
        "an unscoped read of an owned model is a read of every taxpayer's rows."
    )


def test_the_unscoped_read_detector_actually_detects(tmp_path: Path) -> None:
    """Guards the guard: a rule that cannot fail protects nothing."""
    unscoped = tmp_path / "reads.py"
    unscoped.write_text("def rows():\n    return Movement.objects.all()\n")

    assert owned_reads(unscoped)


# The admin is this tool's primary UI, so a model missing from the registry is a
# model nobody can maintain. A wiring rule rather than a behaviour, which is why
# it is here and not beside the admin tests: `scaffolding.data.admin` imports each
# module for its `@admin.register` side effect, and nothing else would notice.
#
# The list comes from the app registry, never retyped beside the imports - a
# hand-written list agrees with itself, so a model added tomorrow and registered
# nowhere would pass. Each exception is named, so adding one is a decision
# somebody has to write down.

# Edited inside its parent's form: a line belongs to its comprobante.
EDITED_AS_INLINES = frozenset({InvoiceLine})
# Not records to maintain by hand. A `Payment` is a link over the movements store,
# derived by `movements classify`, its amount and date living in the store; a `Bill`
# is read from its document by `movements bills`, and correcting one is correcting
# the parser.
NOT_EDITABLE = frozenset({Payment, Bill})


def registered_models() -> list[type[models.Model]]:
    return sorted(apps.get_app_config("data").get_models(), key=lambda model: model.__name__)


@pytest.mark.parametrize("model", registered_models(), ids=lambda model: model.__name__)
def test_every_model_is_registered_or_deliberately_not(model: type[models.Model]) -> None:
    assert admin.site.is_registered(model) or model in EDITED_AS_INLINES or model in NOT_EDITABLE


def owned_models_with_pages() -> list[type[models.Model]]:
    """The models the OwnedAdmin rule applies to: owned, and registered with a
    changelist of their own."""
    return [m for m in registered_models() if issubclass(m, OwnedModel) and admin.site.is_registered(m)]


@pytest.mark.parametrize("model", owned_models_with_pages(), ids=lambda model: model.__name__)
def test_an_owned_model_is_administered_through_owned_admin(model: type[models.Model]) -> None:
    """`OwnedAdmin.get_queryset` is the only thing narrowing a changelist to one
    taxpayer, so an owned model on a plain ModelAdmin lists everybody's rows.
    CutoffAdmin was exactly that, and nothing failed."""
    assert isinstance(admin.site._registry[model], OwnedAdmin), (
        f"{model.__name__} carries a taxpayer but its admin does not narrow by one."
    )


def test_the_movements_pipeline_is_declared_in_dependency_order() -> None:
    """The five Movement passes, in the order they depend on each other.

    `run_pipeline` walks `movements.PASSES`, so a reorder here is a reorder in every
    shell. The order is the dependency, not a convenience: `categorize` writes what
    `describe`, `cluster` and `price` read.
    """
    assert [entry.name for entry in movements.PASSES] == [
        "classified",
        "categorized",
        "described",
        "clustered",
        "priced",
    ]
