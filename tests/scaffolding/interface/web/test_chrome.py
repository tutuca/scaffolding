"""One chrome, on every surface that has one.

A table rather than a test per page: the assertion is identical and the list is
the point - a surface that stops wearing the chrome should be a row that fails,
not a body somebody forgot to copy.

Asserted on structure, and on *a* stylesheet of ours being linked rather than on
which one. Colour is taste and will change; so are filenames. What must not
change is that the tag is there and that something from `ui/` dressed it.
"""

import pytest
from django.template.loader import render_to_string
from django.test import Client
from django.urls import reverse

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer

pytestmark = pytest.mark.django_db

# Every tag the chrome is made of. Named once, so a page that loses its footer
# fails saying "footer" rather than "assert False".
CHROME = ("<header", "<nav", "<main", "<footer")

# Surfaces a member reaches, by URL name. Grows as the chrome does.
DRESSED = [
    "home",
    "movimientos",
    "inversiones",
    "planes",
    "certificado",
    "colophon",
    "admin:data_invoice_changelist",
]


def undressed(body: str) -> list[str]:
    """Which parts of the chrome this page is missing. Empty means it wears it."""
    return [tag.lstrip("<") for tag in CHROME if tag not in body]


@pytest.fixture
def browser(client: Client, user: BaseUser) -> Client:
    """Logged in and staff, with no books - what a fresh Google signup is."""
    user.record_name("Matías")
    user.open_admin()
    client.force_login(user)
    return client


@pytest.fixture
def member(browser: Client, user: BaseUser, taxpayer: Taxpayer) -> Client:
    """The same person, once they have registered a CUIT.

    Every surface in `DRESSED` needs this: `RoleBackend` grants nothing without
    a membership, so an account with no books gets 403 from a changelist rather
    than a page to look for a footer in.
    """
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    return browser


@pytest.mark.parametrize("surface", DRESSED)
def test_it_wears_the_chrome(member: Client, surface: str) -> None:
    body = member.get(reverse(surface)).content.decode()

    assert not undressed(body), f"{surface} is missing: {undressed(body)}"


@pytest.mark.parametrize("surface", DRESSED)
def test_something_of_ours_dressed_it(member: Client, surface: str) -> None:
    """`/static/ui/` and not a filename: the admin gets its stylesheet through
    `{% block extrastyle %}`, and a block that never fires is the failure worth
    catching. Which file it is, is not."""
    body = member.get(reverse(surface)).content.decode()

    assert "/static/ui/" in body


def test_the_nav_names_every_surface(member: Client) -> None:
    """The books and the way out, once there are books to reach."""
    body = member.get(reverse("home")).content.decode()

    assert reverse("home") in body
    assert reverse("movimientos") in body
    assert reverse("inversiones") in body
    assert "/data/invoice/" in body
    assert reverse("admin:logout") in body


def test_the_nav_offers_nothing_that_would_refuse_you(browser: Client) -> None:
    """With no books the admin is empty changelists and the books have nothing
    to draw, so none of them is offered. Same rule that took allauth's account
    menu off the login page: a menu of dead ends is worse than no menu."""
    body = browser.get(reverse("home")).content.decode()

    assert reverse("movimientos") not in body
    assert reverse("inversiones") not in body
    assert "/data/invoice/" not in body


def test_there_are_surfaces_to_check() -> None:
    """An empty table passes every parametrized test above in silence."""
    assert DRESSED


@pytest.mark.parametrize("surface", DRESSED)
def test_every_surface_carries_the_mark(member: Client, surface: str) -> None:
    """The favicon, included by all three base templates - ours, allauth's and
    the vendored admin's. A tab should say which product it is."""
    body = member.get(reverse(surface)).content.decode()

    assert "ui/mark.svg" in body


def test_a_wrong_url_answers_in_the_chrome(member: Client) -> None:
    """404.html extends the base, so a mistyped URL is still this product and
    still offers the way home rather than Django's bare default."""
    response = member.get("/no-such-page/")

    assert response.status_code == 404
    assert "<nav" in response.content.decode()


def test_a_failure_page_renders_without_a_request() -> None:
    """500.html is rendered with an empty context - no request, no context
    processors - so it must not depend on either. Rendering it here is the
    check; a variable it cannot live without would raise."""
    body = render_to_string("500.html")

    assert "<footer" in body


def test_the_login_page_wears_the_chrome(client: Client) -> None:
    """Not a row in `DRESSED`: every page in that table needs a session, and
    this is the page you see before you have one. It also carries no nav - each
    destination in one would need the session this page exists to get."""
    body = client.get(reverse("account_login")).content.decode()

    assert not [tag for tag in ("<header", "<main", "<footer") if tag not in body]
    assert "/static/ui/" in body


def test_the_login_page_drops_allauths_account_menu(client: Client) -> None:
    """allauth's layout ships a menu of account links - change email, change
    password, connections. `SOCIALACCOUNT_ONLY` makes every one of them a dead
    end, and a menu of dead ends is worse than no menu.

    Both spellings, because the first version of this test asserted the English
    one and passed before the override existed: `LANGUAGE_CODE` is `es-ar`, so
    allauth renders `Menú:` and the test could never have failed.
    """
    body = client.get(reverse("account_login")).content.decode()

    assert not [spelling for spelling in ("Menu:", "Menú:") if spelling in body]


def test_the_admin_keeps_its_own_machinery(member: Client) -> None:
    """The chrome is added to the admin, not swapped for it. `admin/base.html`
    is vendored now - spec decision 7, pinned by `test_vendored.py` - but
    Django's own stylesheet, IDs and machinery must survive the edit: the
    changelist, its filters and its actions still render from Django's own
    templates below ours.

    This one does name a file, because the file is the point: the admin's own
    stylesheet still being linked is what says we extended it rather than
    replaced it."""
    body = member.get(reverse("admin:data_invoice_changelist")).content.decode()

    assert "admin/css/base.css" in body
    assert 'id="changelist"' in body
