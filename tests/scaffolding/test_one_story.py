"""One story, end to end: sign up, join a tenant, write and read a note.

This is the shortest path that exercises every layer through its public surface,
so a regression in any one of them fails here.
"""

import pytest
from django.test import Client

from scaffolding.data.enums import Role
from tests.recipes.membership import make_membership
from tests.recipes.tenant import make_tenant
from tests.recipes.user import make_user

pytestmark = pytest.mark.django_db


def test_one_story() -> None:
    user = make_user(email="u@example.com", password="pw-12345678")
    tenant = make_tenant(name="Story")
    make_membership(user=user, tenant=tenant, role=Role.OWNER)
    user.look_at(tenant)

    client = Client()
    assert client.login(username="u@example.com", password="pw-12345678") is True

    assert client.post("/notes/", {"title": "First", "body": "hello"}).status_code == 302

    response = client.get("/notes/")
    assert response.status_code == 200
    assert b"First" in response.content
