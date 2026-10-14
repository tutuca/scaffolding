"""Membership: who may do what on whose books."""

import pytest

from scaffolding.data.enums import Role
from scaffolding.data.models import Membership, Taxpayer
from scaffolding.exceptions import DomainRefusal


@pytest.fixture
def taxpayer(db):
    return Taxpayer.objects.register(tax_id="20123456789", punto_venta_exportacion=5)


@pytest.fixture
def owner(user, taxpayer):
    """Shadows the conftest fixture of the same name: this one grants the role
    without switching the active books, which these tests never read."""
    user.join(taxpayer, role=Role.OWNER)
    return user


@pytest.fixture
def contador(other_user, taxpayer, owner):
    other_user.join(taxpayer, role=Role.ACCOUNTANT, invited_by=owner)
    return other_user


@pytest.mark.django_db
def test_an_owner_may_write_and_administer(owner, taxpayer):
    assert owner.may_write(taxpayer)
    assert owner.may_administer(taxpayer)


@pytest.mark.django_db
def test_an_accountant_may_write_but_not_administer(contador, taxpayer):
    """Using a credential is not the same as being able to replace it."""
    assert contador.may_write(taxpayer)
    assert not contador.may_administer(taxpayer)


@pytest.mark.django_db
def test_a_viewer_writes_nothing(other_user, taxpayer, owner):
    other_user.join(taxpayer, role=Role.VIEWER, invited_by=owner)

    assert not other_user.may_write(taxpayer)
    assert not other_user.may_administer(taxpayer)


@pytest.mark.django_db
def test_invite_is_the_other_end_of_join(other_user, taxpayer, owner):
    taxpayer.invite(other_user, role=Role.VIEWER, invited_by=owner)

    assert other_user.role_on(taxpayer) == Role.VIEWER


@pytest.mark.django_db
def test_granting_an_unknown_role_is_refused(owner, taxpayer):
    with pytest.raises(DomainRefusal, match="no es un rol"):
        owner.join(taxpayer, role="EMPEROR")


@pytest.mark.django_db
def test_granting_twice_updates_the_role_rather_than_duplicating(taxpayer, contador):
    contador.join(taxpayer, role=Role.VIEWER)

    assert Membership.objects.filter(user=contador, taxpayer=taxpayer).count() == 1
    assert contador.role_on(taxpayer) == Role.VIEWER


@pytest.mark.django_db
def test_revoking_the_last_owner_is_refused(owner, taxpayer):
    """Books nobody can administer are books nobody can rescue."""
    membership = Membership.objects.get(user=owner, taxpayer=taxpayer)

    with pytest.raises(DomainRefusal, match="último"):
        membership.revoke()


@pytest.mark.django_db
def test_revoking_a_non_last_owner_is_allowed(taxpayer, contador):
    contador.join(taxpayer, role=Role.OWNER)
    membership = Membership.objects.get(user=contador, taxpayer=taxpayer)

    membership.revoke()

    assert contador.role_on(taxpayer) is None


@pytest.mark.django_db
def test_revoking_a_non_owner_is_allowed(taxpayer, contador):
    membership = Membership.objects.get(user=contador, taxpayer=taxpayer)

    membership.revoke()

    assert contador.role_on(taxpayer) is None


@pytest.mark.django_db
def test_str_names_the_person_the_role_and_the_books(contador, taxpayer):
    assert "Contador" in str(Membership.objects.get(user=contador, taxpayer=taxpayer))
    assert taxpayer.tax_id in str(Membership.objects.get(user=contador, taxpayer=taxpayer))
