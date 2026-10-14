"""One way in over HTTP, and a 401 that says how.

There were three until 2026-09-18. `AccessToken` went because nothing could mint
one. The JWT cookie went because only a `createsuperuser` account could obtain
one - `dj_rest_auth`'s login takes a password, `SOCIALACCOUNT_ONLY` removes the
local signup, and allauth calls `set_unusable_password()` on every social one
(`allauth/socialaccount/adapter.py:156`) - and that account already had the
session.

The reversing goes through `tests.api.reverse`, which supplies the version
segment. `django.urls.reverse("rest_login")` raises `NoReverseMatch` whether the
route exists or not, because the version is a named group - so an absence test
written against it passes vacuously. This one was, for one commit.
"""

import pytest
from django.urls import NoReverseMatch
from rest_framework.test import APIClient

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer
from tests.api import reverse

pytestmark = pytest.mark.django_db

# What `dj_rest_auth.urls` mounted. Each is a door this tool cannot open.
GONE = [
    "rest_login",
    "rest_logout",
    "rest_user_details",
    "rest_password_reset",
    "rest_password_change",
    "token_refresh",
]


def test_the_password_and_jwt_endpoints_are_gone() -> None:
    """The second assertion guards the first: a reverse that finds nothing at all
    would satisfy it whether the routes are gone or merely misspelled."""
    still_routed = []
    for name in GONE:
        try:
            still_routed.append(f"{name} -> {reverse(name)}")
        except NoReverseMatch:
            pass

    assert not still_routed
    assert reverse("client-list").startswith("/api/v")


def test_an_anonymous_request_is_refused_with_401_and_not_403() -> None:
    """DRF answers 403 where it means 401 unless an authenticator supplies a
    `WWW-Authenticate` header. The JWT class used to; now the session one does."""
    response = APIClient().get(reverse("client-list"))

    assert response.status_code == 401
    assert response.headers["WWW-Authenticate"]


def test_a_session_still_authenticates(user: BaseUser, taxpayer: Taxpayer) -> None:
    """The one that stays: the admin is this tool's primary UI and the browsable
    API depends on it."""
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    client = APIClient()
    client.force_login(user)

    assert client.get(reverse("client-list")).status_code == 200
