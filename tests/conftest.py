from collections.abc import Mapping
from datetime import UTC, date, datetime, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Protocol

import pytest
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.x509.oid import NameOID
from django.core.management import call_command
from django.tasks import Task, TaskResult
from rest_framework.test import APIClient

from scaffolding.data.enums import Role
from scaffolding.data.models import BaseUser, NavPoint, Parameter, Scenario, Taxpayer
from scaffolding.interface.adapter.bills.registry import LAYOUTS
from scaffolding.service.domain.setup.use_cases import import_bundle, starter

pytest_plugins = ["tests.recipes", "tests.fixtures"]


@pytest.fixture
def taxpayer(db: None) -> Taxpayer:
    """One taxpayer's books. Everything a test creates belongs here by default."""
    return Taxpayer.objects.register(tax_id="20123456789", punto_venta_exportacion=5)


@pytest.fixture
def other_taxpayer(db: None) -> Taxpayer:
    """A second set, which must never be visible from the first."""
    return Taxpayer.objects.register(tax_id="27987654321", punto_venta_exportacion=3)


@pytest.fixture
def user(db: None) -> BaseUser:
    """A login. The person and the books hang off it in later tasks."""
    return BaseUser.objects.create_user("owner@example.com")


@pytest.fixture
def other_user(db: None) -> BaseUser:
    """A second login, which must never see the first one's books."""
    return BaseUser.objects.create_user("other@example.com")


@pytest.fixture
def owner(user: BaseUser, taxpayer: Taxpayer) -> BaseUser:
    """`user`, owning `books` and looking at them."""
    user.join(taxpayer, role=Role.OWNER)
    user.look_at(taxpayer)
    return user


@pytest.fixture
def api(owner: BaseUser) -> APIClient:
    """Authenticated, owning `books`, with those books active."""
    client = APIClient()
    client.force_login(owner)
    return client


class RunTask(Protocol):
    """`run_task`: enqueue a task, drain one worker pass, return the final result."""

    def __call__(self, task: Task, *args: object, **kwargs: object) -> TaskResult: ...


@pytest.fixture
def run_task() -> RunTask:
    """Enqueue a task, drain one worker pass, and return its final result.

    The database backend queues instead of running; this fixture is the test's
    worker. One `db_worker --batch` pass drains whatever was enqueued.
    """

    def _run(task: Task, *args: object, **kwargs: object) -> TaskResult:
        result = task.enqueue(*args, **kwargs)
        call_command("db_worker", batch=True, verbosity=0)
        return task.get_result(result.id)

    return _run


@pytest.fixture
def other_api(other_user: BaseUser, other_taxpayer: Taxpayer) -> APIClient:
    """A second login on a second set of books - the isolation tests' other half."""
    other_user.join(other_taxpayer, role=Role.OWNER)
    other_user.look_at(other_taxpayer)
    client = APIClient()
    client.force_login(other_user)
    return client


class MakeCertificate(Protocol):
    """`certificate_pair` below, as the type the fixture's consumers name."""

    def __call__(
        self, cuit: str = "", *, valid_days: int = 365, starting: datetime | None = None
    ) -> tuple[bytes, bytes]: ...


@pytest.fixture
def make_certificate() -> MakeCertificate:
    """Build a throwaway certificate and key, optionally for a given CUIT.

    Generated rather than committed: a fixture certificate on disk is one more
    thing that expires, and the real key lives in etc/secrets/ where the tests
    must not be able to reach it.
    """

    def build(cuit: str = "", *, valid_days: int = 365, starting: datetime | None = None) -> tuple[bytes, bytes]:
        return certificate_pair(cuit, valid_days=valid_days, starting=starting)

    return build


@pytest.fixture
def certificate(tmp_path: Path) -> tuple[Path, Path]:
    """The same pair, written to disk, for the CMS signing tests."""
    pem, key_pem = certificate_pair()
    cert_path, key_path = tmp_path / "test.pem", tmp_path / "test.key"
    cert_path.write_bytes(pem)
    key_path.write_bytes(key_pem)
    return cert_path, key_path


def certificate_pair(cuit: str = "", *, valid_days: int = 365, starting: datetime | None = None) -> tuple[bytes, bytes]:
    """A self-signed certificate and its key, in PEM.

    `cuit` goes where ARCA puts it - the subject's serialNumber - so the upload
    check can be exercised against a certificate shaped like a real one.
    """
    key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    attributes = [x509.NameAttribute(NameOID.COMMON_NAME, "test")]
    if cuit:
        attributes.append(x509.NameAttribute(NameOID.SERIAL_NUMBER, f"CUIT {cuit}"))
    name = x509.Name(attributes)
    now = starting or datetime(2026, 1, 1, tzinfo=UTC)
    cert = (
        x509.CertificateBuilder()
        .subject_name(name)
        .issuer_name(name)
        .public_key(key.public_key())
        .serial_number(x509.random_serial_number())
        .not_valid_before(now)
        .not_valid_after(now + timedelta(days=valid_days))
        .sign(key, hashes.SHA256())
    )
    return (
        cert.public_bytes(serialization.Encoding.PEM),
        key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.PKCS8,
            encryption_algorithm=serialization.NoEncryption(),
        ),
    )


# What one invented household declares about itself: loans it asks after, a cut order, a
# regularization window. The market's own figures come from `loadreference`.
DECLARED: list[tuple[str, str, Mapping[str, object]]] = [
    ("dolar_real", "2026-10-08", {"real": ["-0.15", "0"]}),
    ("loan:personal chico", "2026-09-17", {"amount": "5000000", "currency": "ARS", "months": 12, "tna": "0.85"}),
    ("loan:generico", "2026-10-08", {"amount": "100000000", "currency": "ARS", "months": 36, "tna": "0.55"}),
    ("loan:personal grande", "2026-09-17", {"amount": "15000000", "currency": "ARS", "months": 24, "tna": "0.75"}),
    ("loan:prendario auto", "2026-09-17", {"amount": "20000", "currency": "USD", "months": 36, "tna": "0.55"}),
    (
        "regularization",
        "2026-09-17",
        {
            "backlog": {"from": "2024-08-01", "to": "2026-08-31"},
            "declared_periods": [{"from": "2025-09-01", "months": 12}],
            "series": {"from": "2026-10-01", "months": 30},
            "scale_from": "2026-09-01",
            "rolling_horizon": 28,
        },
    ),
    ("stairs", "2026-09-17", {"months": 42}),
    ("cuts", "2026-10-07", {"order": ["goteo", "suscripcion", "grande"]}),
]


@pytest.fixture
def declared_scenarios(taxpayer: Taxpayer) -> None:
    """The declared parameter sets a model reads: the market's, loaded the way an operator loads
    them, and an invented household's own, declared the way an owner declares them."""
    call_command("loadreference")
    for name, on, payload in DECLARED:
        Parameter.objects.declare(
            taxpayer_id=taxpayer.pk, name=name, date=date.fromisoformat(on), payload=dict(payload)
        )


@pytest.fixture
def starter_setup(taxpayer: Taxpayer) -> None:
    """The neutral starter pack imported for the taxpayer: the vocabulary, the bank's own words
    and the bill layouts - what a first run has after `scaffolding setup starter`."""
    import_bundle(taxpayer=taxpayer.pk, bundle=starter(), parsers=set(LAYOUTS))


@pytest.fixture
def galicia_offer() -> None:
    """A Galicia quote table in force on 2026-10-06, the day the certificates were read."""
    Scenario.objects.record(
        name="deposit:GALICIA_PF", date=date(2026, 10, 6), payload={"quotes": {"30": "0.23", "60": "0.195"}}
    )


@pytest.fixture
def fima_series() -> tuple[tuple[date, Decimal], ...]:
    """Three valores de cuotaparte of the Fima, from the app's own movements."""
    points = (
        (date(2026, 9, 29), Decimal("85.329721")),
        (date(2026, 9, 30), Decimal("85.369393")),
        (date(2026, 10, 2), Decimal("85.450731")),
    )
    for on, value in points:
        NavPoint.objects.record(fund="FIMA", on=on, value=value)
    return points
