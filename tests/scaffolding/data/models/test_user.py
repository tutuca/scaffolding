"""The BaseUser contract: accounts and the auth manager's surface."""

import pytest
from django.contrib.auth import get_user_model

from tests.recipes.user import make_user

pytestmark = pytest.mark.django_db


def test_create_user_has_no_usable_password() -> None:
    user = make_user(email="u@example.com")
    assert not user.has_usable_password()


def test_create_superuser_is_staff_and_superuser() -> None:
    user = make_user(email="u@example.com", superuser=True)
    assert user.is_staff and user.is_superuser


def test_get_by_natural_key_finds_the_email() -> None:
    make_user(email="u@example.com")
    assert get_user_model().objects.get_by_natural_key("u@example.com").email == "u@example.com"
