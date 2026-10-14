"""One door.

`SOCIALACCOUNT_ONLY` removes allauth's local login and leaves the admin's, so
until this existed the site's front page sent an anonymous visitor to a
username/password form - the way in `docs/ARCHITECTURE.md` says is not the way
in. These pin that `/login/` forwards to the gateway instead.
"""

import pytest
from django.test import Client
from django.urls import reverse
from pytest_django.fixtures import Settings

from scaffolding.data.models import BaseUser

pytestmark = pytest.mark.django_db


def door() -> str:
    """`/login/`, reversed through the admin: the name it already had."""
    return reverse("admin:login")


def test_the_admin_sends_an_anonymous_visitor_to_google(client: Client) -> None:
    """Two hops, and the second one is ours: an admin page -> `/login/` -> the
    gateway.

    An admin page and not `/`, which the home page took on 2026-09-18 and which
    is `LoginRequiredMixin` - that one reaches the gateway in a single hop and is
    pinned in `test_home.py`. This is the path every *other* admin URL takes.
    """
    first = client.get(reverse("admin:data_invoice_changelist"))

    assert first.status_code == 302
    assert first["Location"].startswith(door())

    second = client.get(first["Location"])

    assert second.status_code == 302
    assert second["Location"].startswith(reverse("account_login"))


def test_it_carries_where_you_were_going(client: Client) -> None:
    response = client.get(f"{door()}?next=/profile/")

    assert response["Location"] == f"{reverse('account_login')}?next=/profile/"


def test_it_refuses_to_forward_to_another_host(client: Client) -> None:
    """`next` is typed by whoever wrote the link, not by us."""
    response = client.get(f"{door()}?next=https://evil.example/")

    assert response["Location"] == f"{reverse('account_login')}?next=/"


def test_no_password_is_asked_for_anywhere_on_the_way(client: Client) -> None:
    body = client.get(door(), follow=True).content.decode()

    assert 'name="password"' not in body


def test_the_escape_hatch_opens_the_form_again(client: Client, settings: Settings) -> None:
    """The reason `ModelBackend` is still in `AUTHENTICATION_BACKENDS`: an OAuth
    client that will not load, and a superuser who has to get in and fix it."""
    settings.ADMIN_PASSWORD_LOGIN = True

    body = client.get(door()).content.decode()

    assert 'name="password"' in body


def test_someone_already_in_is_not_asked_again(client: Client, user: BaseUser) -> None:
    user.open_admin()
    client.force_login(user)

    response = client.get(f"{door()}?next=/profile/")

    assert response.status_code == 302
    assert response["Location"] == "/profile/"
