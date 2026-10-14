"""The admin asks the same two questions the API asks, of the same table.

What the role may do comes from `data/visibility.py`; which rows it may do it to
comes from `get_queryset`. Nothing asks a per-object permission: the admin
resolves a row through that queryset, so another taxpayer's is already a 404.
"""

from typing import cast

import pytest
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import ForeignKey, QuerySet
from django.forms import ModelForm, modelform_factory
from django.http import HttpRequest
from django.test import Client, RequestFactory
from django.urls import reverse

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Contract, Goal, Taxpayer
from scaffolding.data.models import Client as ClientRow
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db


@pytest.fixture
def clients() -> admin.ModelAdmin:
    return admin.site._registry[ClientRow]


@pytest.fixture
def goals() -> admin.ModelAdmin:
    return admin.site._registry[Goal]


def blank_form() -> ModelForm[ClientRow]:
    """`ModelAdmin.save_model` ignores the form; this only has to be one."""
    return modelform_factory(ClientRow, fields=["name"])()


def looking_at(user: BaseUser, taxpayer: Taxpayer, role: str, rf: RequestFactory) -> HttpRequest:
    user.join(taxpayer, role=role)
    user.look_at(taxpayer)
    request = rf.get("/")
    request.user = user
    return request


def test_the_changelist_shows_only_the_active_books(
    clients: admin.ModelAdmin,
    user: BaseUser,
    taxpayer: Taxpayer,
    other_taxpayer: Taxpayer,
    rf: RequestFactory,
    make_client: Maker[ClientRow],
) -> None:
    mine = make_client(taxpayer=taxpayer)
    make_client(taxpayer=other_taxpayer)

    assert list(clients.get_queryset(looking_at(user, taxpayer, Role.OWNER, rf))) == [mine]


def test_an_account_with_no_active_books_sees_nothing(
    clients: admin.ModelAdmin, user: BaseUser, taxpayer: Taxpayer, rf: RequestFactory, make_client: Maker[ClientRow]
) -> None:
    """Empty rather than everything: the failure direction that leaks nothing."""
    make_client(taxpayer=taxpayer)
    request = rf.get("/")
    request.user = user

    assert list(clients.get_queryset(request)) == []
    assert clients.has_view_permission(request) is False


def test_an_accountant_cannot_reach_the_goals_screen(
    goals: admin.ModelAdmin, user: BaseUser, taxpayer: Taxpayer, rf: RequestFactory
) -> None:
    """The same table that hides them over HTTP hides them here."""
    request = looking_at(user, taxpayer, Role.ACCOUNTANT, rf)

    assert goals.has_view_permission(request) is False
    assert goals.has_add_permission(request) is False


def test_an_owner_can(goals: admin.ModelAdmin, user: BaseUser, taxpayer: Taxpayer, rf: RequestFactory) -> None:
    request = looking_at(user, taxpayer, Role.OWNER, rf)

    assert goals.has_view_permission(request) is True
    assert goals.has_change_permission(request) is True
    assert goals.has_delete_permission(request) is True


def test_a_viewer_reads_and_does_not_write(
    goals: admin.ModelAdmin, user: BaseUser, taxpayer: Taxpayer, rf: RequestFactory
) -> None:
    request = looking_at(user, taxpayer, Role.VIEWER, rf)

    assert goals.has_view_permission(request) is True
    assert goals.has_change_permission(request) is False


def test_another_taxpayers_row_is_out_of_reach(
    clients: admin.ModelAdmin,
    user: BaseUser,
    taxpayer: Taxpayer,
    other_taxpayer: Taxpayer,
    rf: RequestFactory,
    make_client: Maker[ClientRow],
) -> None:
    """An OWNER may change clients, so the role says yes; what says no is the
    queryset the admin resolves the row through."""
    mine = make_client(taxpayer=taxpayer)
    stranger = make_client(taxpayer=other_taxpayer)
    request = looking_at(user, taxpayer, Role.OWNER, rf)

    assert clients.has_change_permission(request, stranger) is True
    assert list(clients.get_queryset(request)) == [mine]
    assert clients.get_object(request, str(stranger.pk)) is None


def test_another_taxpayers_change_page_is_a_dead_end(
    client: Client,
    user: BaseUser,
    taxpayer: Taxpayer,
    other_taxpayer: Taxpayer,
    rf: RequestFactory,
    make_client: Maker[ClientRow],
) -> None:
    """The guarantee end to end, on a guessed id: not a 403 that would confirm
    the row exists, but the admin failing to find it at all."""
    stranger = make_client(taxpayer=other_taxpayer)
    looking_at(user, taxpayer, Role.OWNER, rf)
    user.open_admin()
    client.force_login(user)

    response = client.get(reverse("admin:data_client_change", args=[stranger.pk]))

    assert response.status_code == 302


def test_a_superuser_sees_everything(
    clients: admin.ModelAdmin,
    taxpayer: Taxpayer,
    other_taxpayer: Taxpayer,
    rf: RequestFactory,
    make_client: Maker[ClientRow],
) -> None:
    """Whoever can open the admin as a superuser can already read the database
    file beside the process; pretending otherwise would be theatre."""
    make_client(taxpayer=taxpayer)
    make_client(taxpayer=other_taxpayer)
    request = rf.get("/")
    request.user = get_user_model().objects.create_superuser("root@example.com", password="pw")

    assert clients.get_queryset(request).count() == 2
    assert clients.has_change_permission(request) is True


def test_a_new_row_lands_in_the_active_books(
    clients: admin.ModelAdmin, user: BaseUser, taxpayer: Taxpayer, rf: RequestFactory
) -> None:
    """Never from the form: `taxpayer` is not a field on it."""
    request = looking_at(user, taxpayer, Role.OWNER, rf)
    row = ClientRow(name="Acme", country_code="US")

    clients.save_model(request, row, form=blank_form(), change=False)

    assert row.taxpayer == taxpayer
    assert clients.exclude and "taxpayer" in clients.exclude


def test_editing_a_row_leaves_its_books_alone(
    clients: admin.ModelAdmin,
    user: BaseUser,
    taxpayer: Taxpayer,
    other_taxpayer: Taxpayer,
    rf: RequestFactory,
    make_client: Maker[ClientRow],
) -> None:
    """A superuser editing someone else's row must not quietly re-home it."""
    stranger = make_client(taxpayer=other_taxpayer)
    request = looking_at(user, taxpayer, Role.OWNER, rf)

    clients.save_model(request, stranger, form=blank_form(), change=True)

    stranger.refresh_from_db()
    assert stranger.taxpayer == other_taxpayer


def test_a_superuser_with_no_active_books_is_not_offered_an_add_form(
    clients: admin.ModelAdmin, taxpayer: Taxpayer, rf: RequestFactory
) -> None:
    """Adding is the one action that needs to know which books to file under.
    Offering the form and then filing the row under a null taxpayer is an
    IntegrityError at the constraint - the admin offering what it cannot do."""
    request = rf.get("/")
    request.user = get_user_model().objects.create_superuser("root@example.com", password="pw")

    assert clients.has_add_permission(request) is False
    assert clients.has_view_permission(request) is True
    assert clients.has_change_permission(request) is True
    assert clients.has_delete_permission(request) is True

    request.user.join(taxpayer, role=Role.OWNER)
    request.user.look_at(taxpayer)

    assert clients.has_add_permission(request) is True


def client_choices(request: HttpRequest) -> QuerySet[ClientRow]:
    """What the contract form's client dropdown offers `request`."""
    field = admin.site._registry[Contract].formfield_for_foreignkey(
        cast(ForeignKey, Contract._meta.get_field("client")), request
    )
    assert field is not None and field.queryset is not None
    return cast("QuerySet[ClientRow]", field.queryset)


def test_a_dropdown_offers_no_foreign_rows(
    rf: RequestFactory, owner: BaseUser, make_client: Maker[ClientRow], other_taxpayer: Taxpayer
) -> None:
    """The changelist narrows by books; the change form's relations must too, or
    the form offers a client the person has no membership on."""
    foreign = make_client(taxpayer=other_taxpayer)
    request = rf.get("/")
    request.user = owner

    assert not client_choices(request).filter(pk=foreign.pk).exists()


def test_a_dropdown_still_offers_the_books_own_rows(
    rf: RequestFactory, owner: BaseUser, make_client: Maker[ClientRow]
) -> None:
    """Guards the narrowing above: empty-for-everyone would also pass it."""
    mine = make_client()
    request = rf.get("/")
    request.user = owner

    assert client_choices(request).filter(pk=mine.pk).exists()
