"""The architecture rules from docs/ARCHITECTURE.md, enforced.

Each rule is one a reviewer would otherwise have to remember. They are checked by
reading the source, so they hold for code nobody has run yet.
"""

import ast
from pathlib import Path

import pytest
from django.apps import apps
from django.contrib import admin

import scaffolding.data.admin  # noqa: F401 - triggers every @admin.register
from scaffolding.data import serializers
from scaffolding.data.models.base import OwnedModel
from scaffolding.data.visibility import VISIBILITY, root_of
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
