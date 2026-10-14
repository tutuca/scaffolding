"""The one thing that reads `data/visibility.py`.

No object: the role is one value per request - the person's on the books they
are looking at - so the question every shell asks is the global one, and the
answer is the same whichever row prompted it.
"""

import pytest
from django.contrib.auth.models import AnonymousUser

from scaffolding.data.backends import RoleBackend
from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer

pytestmark = pytest.mark.django_db


def looking_at(user: BaseUser, taxpayer: Taxpayer, role: str) -> None:
    user.join(taxpayer, role=role)
    user.look_at(taxpayer)


def test_an_owner_may_change_an_invoice(user: BaseUser, taxpayer: Taxpayer) -> None:
    looking_at(user, taxpayer, Role.OWNER)

    assert RoleBackend().has_perm(user, "data.change_invoice") is True


def test_an_accountant_may_not_see_a_goal(user: BaseUser, taxpayer: Taxpayer) -> None:
    """What someone is saving for is not part of the job."""
    looking_at(user, taxpayer, Role.ACCOUNTANT)

    assert RoleBackend().has_perm(user, "data.view_goal") is False


def test_a_grant_on_the_root_carries_to_what_it_contains(user: BaseUser, taxpayer: Taxpayer) -> None:
    """An invoice's lines are part of the invoice, per `CONTAINED_BY`."""
    looking_at(user, taxpayer, Role.ACCOUNTANT)

    assert RoleBackend().has_perm(user, "data.change_invoiceline") is True


def test_reference_data_is_readable_by_any_role_and_writable_by_none(user: BaseUser, taxpayer: Taxpayer) -> None:
    looking_at(user, taxpayer, Role.OWNER)

    assert RoleBackend().has_perm(user, "data.view_monotributoscale") is True
    assert RoleBackend().has_perm(user, "data.change_monotributoscale") is False


def test_no_membership_grants_nothing(user: BaseUser) -> None:
    assert RoleBackend().has_perm(user, "data.view_invoice") is False
    assert RoleBackend().has_module_perms(user, "data") is False


def test_a_member_reaches_the_data_app(user: BaseUser, taxpayer: Taxpayer) -> None:
    """`has_module_perms` is the method `TaxpayerBackend` never implemented,
    which is what emptied the admin index for every member and got it deleted in
    `4287167`. `_user_has_module_perms` is an `any()` over the backends, so
    answering here overrules nobody."""
    looking_at(user, taxpayer, Role.VIEWER)

    assert RoleBackend().has_module_perms(user, "data") is True


def test_it_answers_for_no_app_but_data(user: BaseUser, taxpayer: Taxpayer) -> None:
    """`auth` and `socialaccount` are reached by a superuser or not at all; this
    backend must not grant a page it has no table for."""
    looking_at(user, taxpayer, Role.OWNER)

    assert RoleBackend().has_module_perms(user, "auth") is False
    assert RoleBackend().has_perm(user, "socialaccount.view_socialaccount") is False


def test_a_stranger_is_answered_rather_than_raised_at(user: BaseUser) -> None:
    """The 2026-09-18 login-page 500, asked of the backend this time."""
    assert RoleBackend().has_perm(AnonymousUser(), "data.view_invoice") is False
    assert RoleBackend().has_module_perms(AnonymousUser(), "data") is False


def test_a_deactivated_account_is_granted_nothing(user: BaseUser, taxpayer: Taxpayer) -> None:
    """`is_active` is how an account is closed without deleting the person."""
    looking_at(user, taxpayer, Role.OWNER)
    user.is_active = False
    user.save(update_fields=["is_active"])

    assert RoleBackend().has_perm(user, "data.view_invoice") is False


def test_it_never_authenticates(user: BaseUser) -> None:
    """Authorization only. `ModelBackend` and allauth own the other question."""
    assert RoleBackend().authenticate(None) is None
