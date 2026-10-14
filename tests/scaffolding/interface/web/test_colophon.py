"""The colophon: the sources and names the books used to cite inline."""

import pytest
from django.test import Client
from django.urls import reverse

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, Taxpayer

pytestmark = pytest.mark.django_db


@pytest.fixture
def member(client: Client, user: BaseUser, taxpayer: Taxpayer) -> Client:
    user.open_admin()
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    client.force_login(user)
    return client


def test_the_colophon_holds_the_sources_and_names(member: Client) -> None:
    body = member.get(reverse("colophon")).content.decode()

    assert "Warren" in body and "All Your Worth" in body
    assert "Tufte" in body
    assert "36%" in body
    assert "backreporting-devengado" in body
    assert "sin decidir" in body and "sin-agrupar" in body


def test_the_colophon_names_the_inflation_model_and_sources(member: Client) -> None:
    """The model, briefly: measured IPC past, a driver band forward - and sources."""
    body = member.get(reverse("colophon")).content.decode()

    assert "Inflación" in body
    assert "INDEC" in body and "datos.gob.ar" in body
    assert "Fisher" in body
    assert "tu canasta" in body
    assert "REM" in body and "BCRA" in body
    assert "https://www.bcra.gob.ar/todos-relevamiento-de-expectativas-de-mercado-rem/" in body


def test_the_books_link_to_the_colophon_instead_of_citing(member: Client) -> None:
    """The citations moved out of the prose; the link stayed behind."""
    colophon = reverse("colophon")
    movimientos = member.get(reverse("movimientos")).content.decode()
    inversiones = member.get(reverse("inversiones")).content.decode()

    assert f'href="{colophon}"' in movimientos
    assert f'href="{colophon}"' in inversiones
    assert "All Your Worth" not in movimientos
    assert "docs/BUDGET.md" not in movimientos and "docs/BUDGET.md" not in inversiones
    assert "backreporting-devengado" not in inversiones
