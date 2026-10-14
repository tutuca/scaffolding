"""What a member actually sees when they land.

The page moved on 2026-09-18 - the home page took `/`, so the admin index is
shadowed - and on 2026-10-04 the home stopped repeating the app list, since
the nav's "Admin" link is the way in. What is asserted here never moved: the
list `get_app_list` builds is narrowed by `RoleBackend`, and that is what each
changelist a member can reach is made of. Asked of the site directly, because
no page carries the whole list any more.

The regression this pins: every permission question used to go through a custom
authentication backend, which had to decline the global question so superusers
fell through to `ModelBackend`. `has_module_permission` is the global question,
so Django dropped the whole app before asking anything per-resource and the
index rendered empty for every non-superuser.
"""

import pytest
from django.contrib import admin
from django.test import RequestFactory

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer

pytestmark = pytest.mark.django_db


def offered(user: BaseUser) -> dict[str, list[str]]:
    """What the admin offers this login, as {app: [model, ...]}."""
    request = RequestFactory().get("/")
    request.user = user
    return {app["app_label"]: [m["object_name"] for m in app["models"]] for app in admin.site.get_app_list(request)}


def landing(user: BaseUser, taxpayer: Taxpayer, role: str) -> dict[str, list[str]]:
    user.join(taxpayer, role=role)
    user.look_at(taxpayer)
    user.open_admin()
    return offered(user)


def test_an_owner_lands_on_a_populated_index(user: BaseUser, taxpayer: Taxpayer) -> None:
    shown = landing(user, taxpayer, Role.OWNER)

    assert "data" in shown, "the index was empty, which is what the backend used to cause"
    assert {"Client", "Contract", "Account", "Invoice", "Movement", "Goal", "Obligation"} <= set(shown["data"])


def test_an_owner_reaches_their_taxpayer_page(user: BaseUser, taxpayer: Taxpayer) -> None:
    """Where the ARCA certificate is installed, so an index without it is a
    dead end for the one gap a new account still has."""
    assert "Taxpayer" in landing(user, taxpayer, Role.OWNER)["data"]


def test_reference_tables_are_offered_to_a_member(user: BaseUser, taxpayer: Taxpayer) -> None:
    """`allows` grants every role `view` on public facts, and nothing more."""
    shown = landing(user, taxpayer, Role.VIEWER)

    assert {"MonotributoScale", "CategoryGroup", "LegalThreshold"} <= set(shown["data"])


def test_an_accountant_is_not_offered_what_is_not_the_job(user: BaseUser, taxpayer: Taxpayer) -> None:
    """The clearest case for the table existing: a contador is a legitimate
    member of these books and still may not see what someone is saving for."""
    shown = set(landing(user, taxpayer, Role.ACCOUNTANT)["data"])

    assert "Invoice" in shown
    assert "Goal" not in shown
    assert "Obligation" not in shown


def test_an_account_with_no_books_is_offered_nothing(user: BaseUser) -> None:
    """No membership, so no role, so no resource - rather than a half-filled
    index whose every changelist is empty."""
    user.open_admin()

    assert offered(user) == {}
