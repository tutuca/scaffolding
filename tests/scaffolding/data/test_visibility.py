"""What each role may do. Who asks it is `VisibleAdmin` and `ResourcePermission`."""

from scaffolding.data.enums import Role
from scaffolding.data.visibility import CONTAINED_BY, VISIBILITY, allows, root_of


def test_a_contained_model_resolves_to_its_root() -> None:
    """An invoice's lines are part of the invoice, not a second thing to grant."""
    assert root_of("invoiceline") == "invoice"
    assert root_of("invoice") == "invoice"


def test_every_contained_model_names_a_root_some_role_can_reach() -> None:
    """A containment pointing at nothing would grant nothing, silently."""
    granted = {resource for row in VISIBILITY.values() for resource in row}

    assert set(CONTAINED_BY.values()) <= granted


def test_no_role_allows_nothing() -> None:
    """A profile with no membership on these books."""
    assert not allows(None, "invoice", "view")


def test_reference_data_is_readable_by_any_role_and_writable_by_none() -> None:
    assert allows(Role.VIEWER, "monotributoscale", "view")
    assert not allows(Role.OWNER, "monotributoscale", "change")


def test_an_unknown_resource_is_invisible() -> None:
    """Minimal by default: a model nobody classified belongs to nobody."""
    assert not allows(Role.OWNER, "somethingnew", "view")


def test_a_line_is_granted_with_its_invoice() -> None:
    assert allows(Role.ACCOUNTANT, "invoiceline", "change")
    assert not allows(Role.VIEWER, "invoiceline", "change")
