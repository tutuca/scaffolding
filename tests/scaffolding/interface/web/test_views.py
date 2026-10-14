"""The web contract: pages answer, and the notes page lists the active tenant's notes."""

from django.test import Client

from tests.recipes.note import make_note


def test_home_renders_for_a_logged_in_member(owner) -> None:
    client = Client()
    client.force_login(owner)
    assert client.get("/").status_code == 200


def test_notes_page_lists_the_notes(owner, tenant) -> None:
    make_note(tenant=tenant, title="Hello")
    client = Client()
    client.force_login(owner)
    response = client.get("/notes/")
    assert response.status_code == 200
    assert b"Hello" in response.content


def test_notes_page_refuses_a_stranger() -> None:
    assert Client().get("/notes/").status_code == 302
