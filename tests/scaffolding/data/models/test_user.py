"""BaseUser: the login and the person on it. Email is the identifier.

`Profile` was a 1:1 side table until 2026-09-18, on the argument that swapping an
auth model is expensive so the auth table should stay thin. That argument was
spent in `0001`, where `AUTH_USER_MODEL` became ours.
"""

import pytest
from django.contrib.auth import get_user_model

from scaffolding.data.enums import Role
from scaffolding.exceptions import DomainRefusal

User = get_user_model()

pytestmark = pytest.mark.django_db


def test_create_user_lowercases_the_domain():
    """Google returns the address as typed; two casings must not be two users."""
    assert User.objects.create_user("Matias@Example.COM").email == "Matias@example.com"


def test_a_google_signup_has_no_usable_password():
    assert not User.objects.create_user("m@example.com").has_usable_password()


def test_create_user_refuses_a_missing_email():
    with pytest.raises(ValueError, match="email"):
        User.objects.create_user("")


def test_create_superuser_is_staff_and_super():
    user = User.objects.create_superuser("root@example.com", password="pw")

    assert user.is_staff
    assert user.is_superuser
    assert user.has_usable_password()


def test_an_account_starts_looking_at_no_books():
    """Signing up does not make somebody a taxpayer; entering a CUIT does."""
    assert User.objects.create_superuser("root@example.com", password="pw").active_taxpayer is None


def test_the_person_lives_on_the_login(user):
    """The fold. `__str__` prefers the name Google returned, then the address."""
    user.full_name = "Matías"
    user.save(update_fields=["full_name"])

    assert str(user) == "Matías"


def test_str_falls_back_to_the_email(user):
    assert str(user) == "owner@example.com"


def test_looking_at_books_you_cannot_reach_is_refused(user, other_taxpayer):
    with pytest.raises(DomainRefusal, match="No tenés acceso"):
        user.look_at(other_taxpayer)


def test_looking_at_books_you_can_reach_sticks(user, taxpayer):
    user.join(taxpayer, role=Role.VIEWER)

    user.look_at(taxpayer)

    assert User.objects.get(pk=user.pk).active_taxpayer == taxpayer


def test_a_role_is_read_off_the_membership(user, taxpayer):
    user.join(taxpayer, role=Role.ACCOUNTANT)

    assert user.role_on(taxpayer) == Role.ACCOUNTANT
    assert user.may_write(taxpayer) is True
    assert user.may_administer(taxpayer) is False


def test_an_owner_may_administer(user, taxpayer):
    """Certificates and memberships. Using a credential is not managing it."""
    user.join(taxpayer, role=Role.OWNER)

    assert user.may_administer(taxpayer) is True


def test_no_membership_is_no_role(user, taxpayer):
    assert user.role_on(taxpayer) is None
    assert user.may_write(taxpayer) is False


def test_taxpayers_lists_every_set_of_books_reachable(user, taxpayer, other_taxpayer):
    user.join(taxpayer, role=Role.OWNER)
    user.join(other_taxpayer, role=Role.ACCOUNTANT)

    assert list(user.taxpayers()) == sorted([taxpayer, other_taxpayer], key=lambda books: books.tax_id)


def test_losing_the_books_does_not_delete_the_person(user, taxpayer):
    """SET_NULL on `active_taxpayer`: a membership can be revoked."""
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)

    taxpayer.delete()

    assert User.objects.filter(pk=user.pk).exists()
