"""The architecture rules from docs/ARCHITECTURE.md, enforced.

Each rule is one a reviewer would otherwise have to remember. They are checked by
reading the source, so they hold for code nobody has run yet.
"""

import ast
import importlib
from pathlib import Path

import pytest
from django.apps import apps
from django.contrib import admin
from django.tasks import Task

import scaffolding.data.admin  # noqa: F401 - triggers every @admin.register
from scaffolding.data import serializers
from scaffolding.data.models.base import OwnedModel
from scaffolding.data.visibility import VISIBILITY, root_of
from scaffolding.interface.tasks import TASK_MODULES
from scaffolding.service.commands import COMMANDS
from scaffolding.service.views import RESOURCES

SRC = Path(__file__).resolve().parents[2] / "src" / "scaffolding"


def python_files(root: Path) -> list[Path]:
    return sorted(p for p in root.rglob("*.py") if "migrations" not in p.parts)


WRITES = frozenset({"save", "create", "get_or_create", "update_or_create", "update", "bulk_create", "bulk_update"})
NOT_THE_ORM = frozenset({"serializer"})


def receiver_name(node: ast.Attribute) -> str:
    return node.value.id if isinstance(node.value, ast.Name) else ""


def write_calls(path: Path) -> list[str]:
    """Every `x.save(...)`-shaped call in a file."""
    tree = ast.parse(path.read_text())
    return [
        node.func.attr
        for node in ast.walk(tree)
        if isinstance(node, ast.Call)
        and isinstance(node.func, ast.Attribute)
        and node.func.attr in WRITES
        and receiver_name(node.func) not in NOT_THE_ORM
    ]


def test_only_models_write_to_the_database() -> None:
    """`save()`/`create()` belong to the model that owns the table. Outside
    `data/models/`, ask for a named transition instead."""
    offenders: list[str] = []
    for root in (SRC / "service", SRC / "interface"):
        for path in python_files(root):
            if "adapter" in path.parts:
                continue
            for attr in write_calls(path):
                offenders.append(f"{path.relative_to(SRC)}: calls .{attr}()")
    assert not offenders, f"Writes outside data/models/: {offenders} (docs/ARCHITECTURE.md)."


def test_the_command_registry_matches_the_command_modules() -> None:
    """`service/commands.py` documents the CLI, so it has to stay true."""
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
    modules = {path.stem for path in python_files(TASK_DIR) if path.stem not in {"__init__", "bridging"}}

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
        if path.stem in {"__init__", "bridging"}:
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


def test_every_crud_row_has_a_serializer() -> None:
    """`RESOURCES` and the serializer tables are one contract written twice."""
    routed = {model for _, model, _ in RESOURCES}
    serializable = set(serializers.PLAIN) | set(serializers.WITH_RULES)
    assert routed == serializable


def test_every_model_is_classified() -> None:
    """The sample domain's four models, and nothing else."""
    found = {model.__name__ for model in apps.get_app_config("data").get_models() if not model._meta.proxy}
    assert found == {"BaseUser", "Tenant", "Membership", "Note"}


@pytest.mark.parametrize("name", ["Note"])
def test_owned_models_carry_a_tenant(name: str) -> None:
    model = apps.get_model("data", name)
    assert issubclass(model, OwnedModel)
    assert hasattr(model._default_manager, "owned_by"), f"{name} needs owned_by (OwnedQuerySet)."


def test_every_owned_model_is_visible() -> None:
    """Minimal by default has a cost: a resource nobody can reach is dead weight."""
    owned = [m for m in apps.get_app_config("data").get_models() if issubclass(m, OwnedModel)]
    granted = {resource for row in VISIBILITY.values() for resource in row}
    for model in owned:
        model_name = model._meta.model_name
        assert model_name is not None
        assert root_of(model_name) in granted, f"{model.__name__} is in no role's visibility row."


def test_every_model_is_registered() -> None:
    """A model missing from the admin registry is a model nobody can maintain."""
    for model in apps.get_app_config("data").get_models():
        assert admin.site.is_registered(model), f"{model.__name__} is not registered in the admin."
