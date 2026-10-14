"""Who ARCA thinks you are, and what proves it.

A remote account, the same shape as allauth's `SocialAccount` - which is why the
ARCA certificate lives here and the Google refresh token lives there, and
neither on `BaseUser`. Every owned row points at this table.
"""

from typing import TYPE_CHECKING

from django.db import models
from django.utils import timezone

from scaffolding.data import secrets
from scaffolding.exceptions import DomainRefusal

from .base import TimeStampedModel
from .membership import Membership

if TYPE_CHECKING:
    from .user import BaseUser

# ARCA's CUIT is eleven digits. Dashes are how people write it, never how it is stored.
CUIT_LENGTH = 11


def normalized_cuit(value: str) -> str:
    """`20-12345678-9` and `20123456789` are the same CUIT. Refuses anything else."""
    digits = value.replace("-", "").replace(" ", "")
    if not (digits.isdigit() and len(digits) == CUIT_LENGTH):
        raise DomainRefusal(f"Un CUIT tiene {CUIT_LENGTH} dígitos; recibí {value!r}.")
    return digits


class TaxpayerQuerySet(models.QuerySet["Taxpayer"]):
    # Factories

    def register(self, *, tax_id: str, punto_venta_exportacion: int | None = None) -> Taxpayer:
        """Register a set of books. Refuses a CUIT already here.

        Not `get_or_create`: claiming a CUIT would otherwise be a way into books
        someone else registered. An existing owner invites instead.
        """
        cuit = normalized_cuit(tax_id)
        if punto_venta_exportacion is not None and punto_venta_exportacion <= 0:
            raise DomainRefusal("El punto de venta es un número positivo asignado por ARCA.")
        if self.filter(tax_id=cuit).exists():
            raise DomainRefusal(f"El CUIT {cuit} ya está registrado. Pedile acceso a quien lo administra.")
        return self.create(tax_id=cuit, punto_venta_exportacion=punto_venta_exportacion)


# django-stubs needs the Manager declared outside the model body.
TaxpayerManager = models.Manager.from_queryset(TaxpayerQuerySet)


class Taxpayer(TimeStampedModel):
    """One CUIT's books."""

    # Globally unique: a CUIT identifies one taxpayer in the world.
    tax_id = models.CharField(max_length=CUIT_LENGTH, unique=True)
    # From the padrón constancia, not typed: reading it needs the certificate.
    legal_name = models.CharField(max_length=200, blank=True)
    # WSFEX's parameter tables do not enumerate these, so it is typed.
    punto_venta_exportacion = models.PositiveSmallIntegerField(null=True, blank=True)

    # Only the key is encrypted; the certificate is public. Bytes rather than
    # files, so they commit with the row - invariant 7's argument again.
    arca_certificate = models.BinaryField(blank=True, default=b"", editable=False)
    arca_key_encrypted = models.BinaryField(blank=True, default=b"", editable=False)
    certificate_installed_on = models.DateTimeField(null=True, blank=True)

    # Created by `scaffolding archive`, never typed: `drive.file` only reaches
    # what this app made.
    drive_archive_folder = models.CharField(max_length=120, blank=True)

    objects = TaxpayerManager()

    class Meta:
        ordering = ["tax_id"]
        db_table = "taxpayer"

    # Mutators

    def invite(self, user: BaseUser, *, role: str, invited_by: BaseUser | None = None) -> Membership:
        """The other end of `BaseUser.join`; both call the same factory."""
        return Membership.objects.grant(user=user, taxpayer=self, role=role, invited_by=invited_by)

    def install_certificate(self, certificate: bytes, key: bytes) -> None:
        """Validate the pair against this CUIT, then store it - the key encrypted.

        Replacing is the same call: they expire every couple of years.
        """
        secrets.validate(certificate, key, expected_cuit=self.tax_id)
        self.arca_certificate = certificate
        self.arca_key_encrypted = secrets.encrypt(key)
        self.certificate_installed_on = timezone.now()
        self.save(update_fields=["arca_certificate", "arca_key_encrypted", "certificate_installed_on", "updated_on"])

    def record_archive_folder(self, folder: str) -> None:
        """Remember the Drive folder the archive created.

        Losing it means a second folder, not a second look at the first: under
        `drive.file` the app cannot see a folder it did not make.
        """
        self.drive_archive_folder = folder
        self.save(update_fields=["drive_archive_folder", "updated_on"])

    def record_registration(self, *, legal_name: str) -> None:
        """What the padrón constancia said. A lookup, never typed."""
        self.legal_name = legal_name
        self.save(update_fields=["legal_name", "updated_on"])

    # Queries

    def certificate_material(self) -> tuple[bytes, bytes]:
        """The pair, decrypted, for WSAA. A method, not a property: it decrypts."""
        if not self.has_certificate:
            raise DomainRefusal(f"{self.tax_id} todavía no tiene certificado de ARCA.")
        return bytes(self.arca_certificate), secrets.decrypt(bytes(self.arca_key_encrypted))

    # Properties

    @property
    def has_certificate(self) -> bool:
        """Absent is a stage of onboarding, not a broken state."""
        return bool(self.arca_certificate and self.arca_key_encrypted)

    def __str__(self) -> str:
        return f"{self.tax_id} - {self.legal_name}" if self.legal_name else self.tax_id
