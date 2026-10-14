"""The notes API contract: what HTTP promises, through the versioned endpoint."""

from tests.recipes.note import make_note


def test_list_returns_only_the_active_tenant(api, tenant, other_tenant) -> None:
    make_note(tenant=tenant, title="mine")
    make_note(tenant=other_tenant, title="theirs")

    response = api.get("/api/v1.0/notes/")
    assert response.status_code == 200
    assert [row["title"] for row in response.data["results"]] == ["mine"]


def test_create_makes_a_note_in_the_active_tenant(api) -> None:
    response = api.post("/api/v1.0/notes/", {"title": "Hello", "body": "World"}, format="json")
    assert response.status_code == 201
    assert response.data["title"] == "Hello"


def test_a_viewer_can_read_but_not_write(viewer_api) -> None:
    assert viewer_api.get("/api/v1.0/notes/").status_code == 200
    assert viewer_api.post("/api/v1.0/notes/", {"title": "x"}, format="json").status_code == 403
