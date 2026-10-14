"""The authentication contract: a password logs in, and the login page works."""

import pytest
from django.contrib.auth import authenticate
from django.test import Client

from tests.recipes.user import make_user

pytestmark = pytest.mark.django_db


def test_a_password_authenticates() -> None:
    make_user(email="u@example.com", password="pw-12345678")
    user = authenticate(request=None, username="u@example.com", password="pw-12345678")
    assert user is not None
    assert user.email == "u@example.com"


def test_a_wrong_password_does_not_authenticate() -> None:
    make_user(email="u@example.com", password="pw-12345678")
    assert authenticate(request=None, username="u@example.com", password="wrong") is None


def test_the_login_page_renders() -> None:
    assert Client().get("/login/").status_code == 200


def test_a_client_logs_in_and_reaches_home() -> None:
    make_user(email="u@example.com", password="pw-12345678")
    client = Client()
    assert client.login(username="u@example.com", password="pw-12345678") is True
    assert client.get("/").status_code == 200
