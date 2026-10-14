"""Each page we own reads as a document: landmarks, one h1, no skipped
headings, labels, names.

Two tables. `OURS` is markup this repo authors and answers for fully. The
login page renders allauth's content inside our layout, so it gets the
mechanical checks but not the heading ones - its headings are allauth's, the
way the admin's body is Django's and stays out of both tables. Scope is part
of the claim.
"""

from html.parser import HTMLParser

import pytest
from django.test import Client
from django.urls import reverse

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer

pytestmark = pytest.mark.django_db

OURS = ["home", "movimientos", "inversiones", "planes", "certificado", "colophon"]
WRAPPED = ["account_login"]

HEADINGS = {"h1", "h2", "h3", "h4", "h5", "h6"}


class Story(HTMLParser):
    """What the checks below need, collected in one pass."""

    def __init__(self) -> None:
        super().__init__()
        self.lang = ""
        self.headings: list[int] = []
        self.mains = 0
        self.labeled: set[str] = set()
        self.inputs: list[str] = []
        self.unnamed_media: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        table = {name: value or "" for name, value in attrs}
        if tag == "html":
            self.lang = table.get("lang", "")
        if tag in HEADINGS:
            self.headings.append(int(tag[1]))
        if tag == "main":
            self.mains += 1
        if tag == "label" and table.get("for"):
            self.labeled.add(table["for"])
        if tag in {"input", "select", "textarea"} and table.get("type") not in {"hidden", "submit"}:
            self.inputs.append(table.get("id", table.get("name", tag)))
        if tag == "img" and not table.get("alt"):
            self.unnamed_media.append("img")
        if tag == "iframe" and not table.get("title"):
            self.unnamed_media.append("iframe")


def told(body: str) -> Story:
    story = Story()
    story.feed(body)
    return story


@pytest.fixture
def member(client: Client, user: BaseUser, taxpayer: Taxpayer) -> Client:
    user.open_admin()
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    client.force_login(user)
    return client


def page(browser: Client, surface: str) -> Story:
    return told(browser.get(reverse(surface), follow=True).content.decode())


def mechanics(story: Story, surface: str) -> None:
    assert story.lang == "es-ar", f"{surface}: lang={story.lang!r}"
    assert story.mains == 1, f"{surface} has {story.mains} <main> landmarks"
    assert not story.unnamed_media, f"{surface} has unnamed {story.unnamed_media}"
    unlabeled = [field for field in story.inputs if field not in story.labeled]
    assert not unlabeled, f"{surface} has inputs no label names: {unlabeled}"


@pytest.mark.parametrize("surface", OURS)
def test_one_h1_and_no_skipped_levels(member: Client, surface: str) -> None:
    story = page(member, surface)

    assert story.headings.count(1) == 1, f"{surface} has {story.headings.count(1)} h1s"
    assert all(after <= before + 1 for before, after in zip(story.headings, story.headings[1:])), (
        f"{surface} skips a heading level: {story.headings}"
    )


@pytest.mark.parametrize("surface", OURS)
def test_the_mechanics_hold(member: Client, surface: str) -> None:
    mechanics(page(member, surface), surface)


@pytest.mark.parametrize("surface", WRAPPED)
def test_the_wrapped_pages_mechanics_hold(client: Client, surface: str) -> None:
    """Anonymous on purpose: a session on the login page is a redirect home,
    and the test would be reading the wrong document."""
    mechanics(page(client, surface), surface)


def test_there_are_surfaces_to_check() -> None:
    assert OURS and WRAPPED
