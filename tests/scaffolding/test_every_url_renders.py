"""Does each page come back at all. The cheapest net there is.

Not about permissions - `test_logged_out.py` and `test_index.py` own those. This
one is about the failure they cannot see: a view that raises before it can
answer. The login page did exactly that from `4287167` until the same day's fix,
and every test in the suite passed throughout, because all of them logged in
first.

Two cases, each sweeping every page and naming every offender, rather than two
per page. A broken base template would otherwise report thirty-six failures that
are one fault.
"""

import pytest
from django.contrib import admin
from django.test import Client
from django.urls import reverse

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer

pytestmark = pytest.mark.django_db

# Renders with no arguments. A changelist per registered model, plus the pages
# that are not a model's: built from the registry so a new admin joins by
# existing, which is the whole point.
CHANGELISTS = [f"admin:{model._meta.app_label}_{model._meta.model_name}_changelist" for model in admin.site._registry]
# `profile` was here until 2026-09-18, when the page folded onto `admin:index` -
# which is in this list and now carries the registration form and the gaps.
PAGES = sorted(["admin:login", "admin:index", "schema", "swagger-ui", "redoc", *CHANGELISTS])

# 200 renders, 302 redirects to the login page. Either is an answer; 500 is not.
ANSWERED = {200, 302}


def unanswered(client: Client, allowed: set[int]) -> list[str]:
    """Every page whose status is not one this caller counts as an answer."""
    seen = ((name, client.get(reverse(name)).status_code) for name in PAGES)
    return [f"{name} -> {status}" for name, status in seen if status not in allowed]


def test_a_stranger_gets_an_answer_and_not_a_traceback(client: Client) -> None:
    assert not unanswered(client, ANSWERED)


def test_an_owner_gets_an_answer_and_not_a_traceback(client: Client, user: BaseUser, taxpayer: Taxpayer) -> None:
    """403 is allowed here and not above: a member may legitimately be refused a
    resource their role does not grant, which is `test_index.py`'s subject."""
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    user.open_admin()
    client.force_login(user)

    assert not unanswered(client, {*ANSWERED, 403})
