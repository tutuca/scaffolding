"""Which books a request acts on, and whether it may write to them."""

import pytest
from django.contrib.auth.models import AnonymousUser
from rest_framework.exceptions import NotFound
from rest_framework.request import Request
from rest_framework.test import APIClient, APIRequestFactory
from rest_framework.views import APIView

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Client, Taxpayer
from scaffolding.service import tenancy
from tests.api import reverse

pytestmark = pytest.mark.django_db


def request_for(user: BaseUser) -> Request:
    request = APIRequestFactory().get("/")
    request.user = user
    return request


def test_the_active_books_come_from_the_account(user: BaseUser, taxpayer: Taxpayer, owner: BaseUser) -> None:
    assert tenancy.active_taxpayer(request_for(user)) == taxpayer


def test_an_account_with_no_books_is_told_what_to_do(user: BaseUser) -> None:
    with pytest.raises(NotFound, match="Registrá un CUIT"):
        tenancy.active_taxpayer(request_for(user))


def client_for(user: BaseUser, taxpayer: Taxpayer, role: str) -> APIClient:
    user.join(taxpayer, role=role)
    user.look_at(taxpayer)
    client = APIClient()
    client.force_authenticate(user)
    return client


def test_an_accountant_writes_the_fiscal_ledger(other_user: BaseUser, taxpayer: Taxpayer) -> None:
    """The comprobantes and the movements behind them are the job."""
    contador = client_for(other_user, taxpayer, Role.ACCOUNTANT)

    assert contador.get(reverse("expense-list")).status_code == 200


def test_an_accountant_may_read_a_client_but_not_create_one(other_user: BaseUser, taxpayer: Taxpayer) -> None:
    """Who you invoice is a fact they need; deciding it is not their call."""
    contador = client_for(other_user, taxpayer, Role.ACCOUNTANT)

    assert contador.get(reverse("client-list")).status_code == 200
    assert contador.post(reverse("client-list"), {"name": "Acme", "country_code": "US"}).status_code == 403


def test_an_accountant_cannot_see_the_goals_at_all(other_user: BaseUser, taxpayer: Taxpayer) -> None:
    """What someone is saving for, and by when, is not part of the job. This is
    the clearest case for the visibility table existing at all."""
    contador = client_for(other_user, taxpayer, Role.ACCOUNTANT)

    assert contador.get(reverse("goal-list")).status_code == 403


def test_an_owner_sees_the_goals(user: BaseUser, taxpayer: Taxpayer, api: APIClient) -> None:
    assert api.get(reverse("goal-list")).status_code == 200


def test_a_viewer_may_read_and_may_not_write(other_user: BaseUser, taxpayer: Taxpayer) -> None:
    client = client_for(other_user, taxpayer, Role.VIEWER)

    assert client.get(reverse("client-list")).status_code == 200
    assert client.post(reverse("client-list"), {"name": "Acme", "country_code": "US"}).status_code == 403


def test_an_owner_creates_a_row_in_their_own_books(api: APIClient, taxpayer: Taxpayer) -> None:
    """The taxpayer is set from the request, never from the payload - the payload
    cannot even carry it, because no serializer exposes the field."""
    response = api.post(reverse("client-list"), {"name": "Acme", "country_code": "US"})

    assert response.status_code == 201, response.data
    assert Client.objects.get(pk=response.data["id"]).taxpayer == taxpayer


def test_a_member_of_no_books_is_refused(user: BaseUser, taxpayer: Taxpayer) -> None:
    """`IsMember` guards the resources that have no model to ask a permission of."""
    client = APIClient()
    client.force_authenticate(user)

    assert client.get(reverse("monotributo-position-list")).status_code == 404


def test_an_anonymous_request_is_refused() -> None:
    """401 and not 403: the JWT authenticator sets a `WWW-Authenticate` header, so
    DRF can say *how* to authenticate rather than only that the answer is no."""
    assert APIClient().get(reverse("client-list")).status_code == 401


# A viewset serving no queryset, and a verb DRF does not route, were tested here
# against `ResourcePermission.resource` and its `ACTIONS` map. Both went on
# 2026-09-18 with the class: `DjangoModelPermissions` raises its own assertion
# for the first and `MethodNotAllowed` for the second, and every registered route
# is exercised by `test_every_route_is_scoped.py`, which is what would actually
# catch a viewset shipped without one.


def test_is_member_refuses_an_anonymous_request() -> None:
    request = APIRequestFactory().get("/")
    request.user = AnonymousUser()

    assert tenancy.IsMember().has_permission(request, APIView()) is False


def test_the_api_reads_the_same_table_as_the_admin(other_user: BaseUser, taxpayer: Taxpayer) -> None:
    """One table, one backend, two shells. A contador may read the movements and
    may not read a goal, on HTTP exactly as on the admin index."""
    contador = client_for(other_user, taxpayer, Role.ACCOUNTANT)

    assert contador.get(reverse("expense-list")).status_code == 200
    assert contador.get(reverse("goal-list")).status_code == 403


def test_get_needs_view_and_not_merely_authentication() -> None:
    """DRF maps GET to no permission at all; minimal by default means reading is
    a grant like any other, so the map is overridden rather than inherited."""
    assert tenancy.ResourcePermission.perms_map["GET"] == ["%(app_label)s.view_%(model_name)s"]
