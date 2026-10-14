"""What a taxpayer still needs, read off the model rather than tracked."""

from collections.abc import Callable

import pytest

from scaffolding.data.models import Account, Contract, Taxpayer
from scaffolding.exceptions import DomainRefusal
from scaffolding.service.domain.access import use_cases as access
from tests.conftest import MakeCertificate
from tests.recipes.base import Maker

pytestmark = pytest.mark.django_db


def named(books: Taxpayer) -> set[str]:
    return {gap.what for gap in access.gaps(taxpayer=books.pk)}


def test_a_fresh_taxpayer_is_missing_everything() -> None:
    taxpayer = Taxpayer.objects.register(tax_id="20123456789")

    assert named(taxpayer) == {"certificado de ARCA", "punto de venta", "contrato activo", "cuentas"}


def test_a_punto_de_venta_closes_its_own_gap() -> None:
    taxpayer = Taxpayer.objects.register(tax_id="20123456789", punto_venta_exportacion=5)

    assert "punto de venta" not in named(taxpayer)


def test_a_certificate_closes_its_own_gap(make_certificate: Callable[[str], tuple[bytes, bytes]]) -> None:
    taxpayer = Taxpayer.objects.register(tax_id="20123456789")
    taxpayer.install_certificate(*make_certificate("20123456789"))

    assert "certificado de ARCA" not in named(taxpayer)


def test_a_contract_closes_its_own_gap(taxpayer: Taxpayer, make_contract: Maker[Contract]) -> None:
    make_contract(taxpayer=taxpayer)

    assert "contrato activo" not in named(taxpayer)


def test_an_inactive_contract_does_not(taxpayer: Taxpayer, make_contract: Maker[Contract]) -> None:
    """The projection and drafting both want exactly one *active* one."""
    make_contract(taxpayer=taxpayer, is_active=False)

    assert "contrato activo" in named(taxpayer)


def test_an_account_closes_its_own_gap(taxpayer: Taxpayer, make_account: Maker[Account]) -> None:
    make_account(taxpayer=taxpayer)

    assert "cuentas" not in named(taxpayer)


def test_every_gap_says_what_it_blocks_and_where_to_fix_it() -> None:
    """A gap nobody can act on is a complaint, not a prompt."""
    taxpayer = Taxpayer.objects.register(tax_id="20123456789")

    for gap in access.gaps(taxpayer=taxpayer.pk):
        assert gap.blocks
        assert gap.model


def test_what_a_gap_blocks_reads_as_a_verb() -> None:
    """Both shells print it as "sin eso no podés {blocks}", so a noun phrase there
    is ungrammatical - "no podés la proyección" shipped once."""
    taxpayer = Taxpayer.objects.register(tax_id="20123456789")

    for gap in access.gaps(taxpayer=taxpayer.pk):
        assert gap.blocks.split()[0].endswith(("ar", "er", "ir")), f"`{gap.blocks}` does not start with an infinitive"


def test_the_certificate_installs_through_the_domain(taxpayer: Taxpayer, make_certificate: MakeCertificate) -> None:
    certificate, key = make_certificate("20123456789")

    access.install_certificate(taxpayer=taxpayer.pk, certificate=certificate, key=key)

    assert Taxpayer.objects.get(pk=taxpayer.pk).has_certificate


def test_a_foreign_cuits_certificate_is_refused(taxpayer: Taxpayer, make_certificate: MakeCertificate) -> None:
    certificate, key = make_certificate("27999999999")

    with pytest.raises(DomainRefusal, match="27999999999"):
        access.install_certificate(taxpayer=taxpayer.pk, certificate=certificate, key=key)
    assert not Taxpayer.objects.get(pk=taxpayer.pk).has_certificate


def test_last_reads_name_a_dash_for_what_is_not_loaded() -> None:
    taxpayer = Taxpayer.objects.register(tax_id="20123456789")

    last = access.last_reads(taxpayer=taxpayer.pk)

    assert (last.ipc, last.market, last.experiment, last.movements) == (None, None, None, None)
