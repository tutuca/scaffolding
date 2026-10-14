"""Every row of `service/views.RESOURCES`, swept.

`test_conventions.py` checks *statically* that code calls `owned_by`. That is a
proxy for the thing that matters - that a request cannot read another taxpayer's
rows - and a proxy is what a new route slips past. This reads the same table the
router reads, so a resource added to `RESOURCES` is covered by existing rather
than by somebody remembering.

It earned its place on the first run: five of the thirteen rows are reference
tables, whose querysets have no `owned_by`, and `ScaffoldingModelViewSet.get_queryset`
called it unconditionally. `GET /monotributo/scale/` answered 500 to every member
and no test had ever fetched a reference resource over HTTP.

Each behaviour is one case that names every resource failing it, rather than one
case per resource. The bug above broke five at once and would have reported five
separate failures saying the same thing.
"""

import pytest
from rest_framework.test import APIClient

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer
from scaffolding.data.models.base import OwnedModel
from scaffolding.service.views import RESOURCES
from tests.api import reverse

pytestmark = pytest.mark.django_db

BASENAMES = sorted(basename for _, _, basename in RESOURCES)
# The split that decides what "scoped" means: owned rows narrow to one
# taxpayer's books, reference rows are public facts nobody's copy of.
OWNED = sorted(basename for _, model, basename in RESOURCES if issubclass(model, OwnedModel))
REFERENCE = sorted(basename for _, model, basename in RESOURCES if not issubclass(model, OwnedModel))

# The recipe that puts one row in `taxpayer`'s books, per owned resource. Named
# rather than derived: a recipe is a fixture, and the registry cannot know which.
RECIPES = {
    "account": "make_account",
    "client": "make_client",
    "contract": "make_contract",
    "expense": "make_expense",
    "monotributostatus": "make_monotributo_status",
    "obligation": "make_obligation",
    "settlement": "make_settlement",
}


def member(user: BaseUser, taxpayer: Taxpayer, role: str = Role.OWNER) -> APIClient:
    user.join(taxpayer, role=role)
    user.look_at(taxpayer)
    client = APIClient()
    client.force_authenticate(user)
    return client


def statuses(client: APIClient, basenames: list[str]) -> dict[str, int]:
    return {basename: client.get(reverse(f"{basename}-list")).status_code for basename in basenames}


def test_the_split_and_the_recipes_cover_every_row() -> None:
    """Two lists that must stay exhaustive. A row falling out of the first is
    swept by nothing; an owned resource missing from the second is swept against
    an empty table, which passes however broken the scoping is."""
    assert sorted([*OWNED, *REFERENCE]) == BASENAMES
    assert OWNED and REFERENCE
    assert sorted(RECIPES) == OWNED, f"no recipe for {sorted(set(OWNED) - set(RECIPES))}"


def test_a_stranger_is_refused_every_resource() -> None:
    """401 and not 403: DRF can say *how* to authenticate."""
    wrong = {name: status for name, status in statuses(APIClient(), BASENAMES).items() if status != 401}

    assert not wrong


def test_an_account_with_no_books_reads_no_resource(user: BaseUser) -> None:
    """404 and not 403: whether a CUIT is registered here is itself information."""
    client = APIClient()
    client.force_authenticate(user)

    wrong = {name: status for name, status in statuses(client, BASENAMES).items() if status not in {403, 404}}

    assert not wrong


def test_a_member_reads_every_resource_their_role_grants(user: BaseUser, taxpayer: Taxpayer) -> None:
    """The one that caught the reference-table 500. An owner is granted `view` on
    all thirteen, so a status other than 200 is a broken route, not an answer."""
    wrong = {name: status for name, status in statuses(member(user, taxpayer), BASENAMES).items() if status != 200}

    assert not wrong, f"{wrong} - an owner may view every resource, so these are broken routes"


def test_a_member_of_other_books_sees_none_of_these_rows(
    request: pytest.FixtureRequest, other_user: BaseUser, taxpayer: Taxpayer, other_taxpayer: Taxpayer
) -> None:
    """What the static `owned_by` check is a proxy for: a row exists in these
    books, and an owner of other books gets an empty list rather than it.

    The second assertion guards the first: an empty table would satisfy it
    however broken the scoping is, so the owner of those books must see the row.
    """
    for basename in OWNED:
        request.getfixturevalue(RECIPES[basename])()

    theirs = member(other_user, other_taxpayer)
    mine = member(request.getfixturevalue("user"), taxpayer)
    leaked = [name for name in OWNED if theirs.get(reverse(f"{name}-list")).data["results"]]
    invisible = [name for name in OWNED if not mine.get(reverse(f"{name}-list")).data["results"]]

    assert not leaked, f"{leaked} served another taxpayer's rows"
    assert not invisible, f"{invisible} showed nobody the row, so the check above proved nothing"


def test_reference_data_is_shared_and_read_only(user: BaseUser, taxpayer: Taxpayer) -> None:
    """Public facts: every role reads them, no role writes them through the API.
    `scaffolding loadreference` is what seeds them."""
    client = member(user, taxpayer, Role.VIEWER)

    unreadable = {name: status for name, status in statuses(client, REFERENCE).items() if status != 200}
    writable = [name for name in REFERENCE if client.post(reverse(f"{name}-list"), {}).status_code != 403]

    assert not unreadable
    assert not writable, f"{writable} accepted a write from a role that grants only view"
