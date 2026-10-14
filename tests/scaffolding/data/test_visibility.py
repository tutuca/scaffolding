from scaffolding.data.enums import Role
from scaffolding.data.visibility import allows


def test_owner_writes_notes() -> None:
    assert allows(Role.OWNER, "note", "change")


def test_editor_writes_notes() -> None:
    assert allows(Role.EDITOR, "note", "add")


def test_viewer_reads_only() -> None:
    assert allows(Role.VIEWER, "note", "view")
    assert not allows(Role.VIEWER, "note", "change")


def test_stranger_allows_nothing() -> None:
    assert not allows(None, "note", "view")
