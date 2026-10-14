from scaffolding.data.enums import Role


def test_roles_are_owner_editor_viewer() -> None:
    assert set(Role.values) == {"OWNER", "EDITOR", "VIEWER"}
