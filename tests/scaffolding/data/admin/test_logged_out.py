"""What a stranger gets. The half of the admin the suite never asked about.

Every other admin test calls `force_login` first, so until 2026-09-18 nothing
fetched an admin URL logged out - and the login page itself raised a TypeError
from inside the ORM. `AdminSite.login` builds the whole app list through
`each_context`, so every registered ModelAdmin is asked `has_module_permission`
*before* anybody has authenticated, and `AnonymousUser` carries none of what
those questions read.

The regression came in with `4287167`, which moved the role check out of
`TaxpayerBackend` - whose `has_perm` opened with `isinstance(user_obj,
AnonymousUser)` - and into `VisibleAdmin`, which had no such clause.

The sweep collects its offenders and names them all at once, the way
`test_conventions.py` does, rather than parametrising over (admin, method). 140
cases said no more than one does, and a single bad method reported all 28 models
one failure at a time.
"""

import pytest
from django.contrib import admin
from django.contrib.auth.models import AnonymousUser
from django.http import HttpRequest
from django.test import Client, RequestFactory
from django.urls import reverse
from pytest_django.fixtures import Settings

from scaffolding.data.models import BaseUser

pytestmark = pytest.mark.django_db

# Every question `AdminSite.each_context` and `_build_app_dict` ask, in order.
# `has_module_permission` is the first and the one that was raising.
QUESTIONS = [
    "has_module_permission",
    "has_view_permission",
    "has_add_permission",
    "has_change_permission",
    "has_delete_permission",
]


def logged_out() -> HttpRequest:
    request = RequestFactory().get("/")
    request.user = AnonymousUser()
    return request


def test_a_logged_out_visitor_reaches_a_page_that_renders(client: Client) -> None:
    """Log out, follow the redirects, arrive somewhere. `?next=/` is where a
    logged-out visit to the index lands, and `interface/web.AdminLoginView`
    forwards it to the gateway from there."""
    assert client.get(reverse("admin:login"), follow=True).status_code == 200
    assert client.get(reverse("admin:login"), {"next": "/"}, follow=True).status_code == 200


def test_the_admin_login_page_renders_when_the_escape_hatch_is_open(client: Client, settings: Settings) -> None:
    """The one the operator hit: log out, follow the redirect, 500.

    An integration test and not only the sweep below, because what broke was a
    path Django takes rather than a method anybody calls by hand. Behind the
    flag now - `AdminSite.login` is the page nobody reaches with it closed, so
    testing it any other way would stop exercising `each_context` at all.
    """
    settings.ADMIN_PASSWORD_LOGIN = True

    assert client.get(reverse("admin:login")).status_code == 200
    assert client.get(reverse("admin:login"), {"next": "/"}).status_code == 200


def test_logging_out_lands_somewhere_that_renders(client: Client, user: BaseUser) -> None:
    user.open_admin()
    client.force_login(user)

    assert client.post(reverse("admin:logout")).status_code == 200
    assert client.get(reverse("admin:index"), follow=True).status_code == 200


def test_every_admin_answers_a_stranger_rather_than_raising() -> None:
    """The convention, enforced rather than written down: a permission method
    answers False for an anonymous request. Raising is not a way of saying no -
    it is a 500 on a page Django renders before anybody can log in.
    """
    request = logged_out()
    offenders = []
    for model, model_admin in sorted(admin.site._registry.items(), key=lambda pair: str(pair[0]._meta.label)):
        for question in QUESTIONS:
            try:
                answer = getattr(model_admin, question)(request)
            except Exception as raised:  # noqa: BLE001 - that nothing raises is the assertion
                offenders.append(f"{model.__name__}.{question} raised {type(raised).__name__}")
            else:
                if answer is not False:
                    offenders.append(f"{model.__name__}.{question} answered {answer!r}")

    assert not offenders, f"{offenders} - a stranger is answered, never raised at"
