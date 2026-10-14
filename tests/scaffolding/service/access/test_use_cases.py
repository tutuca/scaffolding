"""Who can reach whose books, and how they got there."""

from unittest import mock

import pytest

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Membership, Taxpayer
from scaffolding.exceptions import DomainRefusal
from scaffolding.service.domain.access import use_cases as access

pytestmark = pytest.mark.django_db


def test_registering_makes_the_books_and_their_owner(user: BaseUser) -> None:
    registered = access.register_taxpayer(user=user.pk, tax_id="20-12345678-9", punto_venta=5)

    account = BaseUser.objects.get(pk=user.pk)
    books = Taxpayer.objects.get(pk=registered.taxpayer)
    assert registered.tax_id == "20123456789"
    assert books.punto_venta_exportacion == 5
    assert account.role_on(books) == Role.OWNER
    assert account.active_taxpayer == books


def test_the_punto_de_venta_is_optional(user: BaseUser) -> None:
    registered = access.register_taxpayer(user=user.pk, tax_id="20123456789")

    assert Taxpayer.objects.get(pk=registered.taxpayer).punto_venta_exportacion is None


def test_a_cuit_somebody_else_holds_is_refused(user: BaseUser, other_user: BaseUser) -> None:
    """This is what stops registration being a way into someone else's ledger."""
    access.register_taxpayer(user=other_user.pk, tax_id="20123456789")

    with pytest.raises(DomainRefusal, match="ya está registrado"):
        access.register_taxpayer(user=user.pk, tax_id="20123456789")


def test_a_refused_registration_leaves_nothing_behind(user: BaseUser, other_user: BaseUser) -> None:
    """A CUIT somebody holds is refused before anything is written."""
    access.register_taxpayer(user=other_user.pk, tax_id="20123456789")
    before = Membership.objects.count()

    with pytest.raises(DomainRefusal):
        access.register_taxpayer(user=user.pk, tax_id="20123456789")

    assert Membership.objects.count() == before


def test_a_failure_after_the_books_exist_takes_them_with_it(user: BaseUser) -> None:
    """The refusal above never reaches the writes, so only a forced failure can
    show the transaction is real. Without `atomic` the books survive ownerless."""
    with (
        mock.patch.object(BaseUser, "join", side_effect=RuntimeError("granting failed")),
        pytest.raises(RuntimeError),
    ):
        access.register_taxpayer(user=user.pk, tax_id="20123456789")

    assert not Taxpayer.objects.filter(tax_id="20123456789").exists()


def test_a_second_registration_does_not_move_the_active_books(user: BaseUser) -> None:
    """Registering another CUIT should not silently switch what you are looking at."""
    first = access.register_taxpayer(user=user.pk, tax_id="20123456789")
    access.register_taxpayer(user=user.pk, tax_id="27987654321")

    active = BaseUser.objects.get(pk=user.pk).active_taxpayer
    assert active is not None
    assert active.pk == first.taxpayer
