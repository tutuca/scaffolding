"""The ARCA certificate: checked before it is trusted, encrypted before stored.

Whoever holds the private key can issue fiscal documents in the taxpayer's name.
The encryption buys one thing: a copy that leaks without `.env` leaks no usable
key. The encrypted volume the database sits on is still the outer defence.
"""

from cryptography.fernet import Fernet, InvalidToken
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric.types import PublicKeyTypes
from cryptography.x509 import NameOID, load_pem_x509_certificate
from django.conf import settings
from django.utils import timezone

from scaffolding.exceptions import DomainRefusal


def cipher() -> Fernet:
    """The one place the encryption key is read."""
    if not settings.SECRETS_ENCRYPTION_KEY:
        raise DomainRefusal("Falta SECRETS_ENCRYPTION_KEY en .env; sin eso no se guarda un certificado.")
    return Fernet(settings.SECRETS_ENCRYPTION_KEY.encode())


def encrypt(plaintext: bytes) -> bytes:
    return cipher().encrypt(plaintext)


def decrypt(ciphertext: bytes) -> bytes:
    try:
        return cipher().decrypt(ciphertext)
    except InvalidToken as exc:
        raise DomainRefusal(
            "No se puede descifrar la clave guardada: cambió SECRETS_ENCRYPTION_KEY. Volvé a subir el certificado."
        ) from exc


def public_bytes(key: PublicKeyTypes) -> bytes:
    """One public key as bytes. Serialized rather than compared as numbers,
    which only some key types support."""
    return key.public_bytes(serialization.Encoding.DER, serialization.PublicFormat.SubjectPublicKeyInfo)


def certificate_cuit(certificate: bytes) -> str:
    """The CUIT from the subject's serialNumber, as ARCA writes it. Empty when
    absent, which is unknown rather than wrong."""
    values = load_pem_x509_certificate(certificate).subject.get_attributes_for_oid(NameOID.SERIAL_NUMBER)
    return str(values[0].value).removeprefix("CUIT").strip() if values else ""


def validate(certificate: bytes, key: bytes, *, expected_cuit: str) -> None:
    """Refuse anything WSAA would refuse later, and less clearly.

    The CUIT check earns its place alone: the wrong one fails at login with a
    message that explains nothing.
    """
    try:
        parsed = load_pem_x509_certificate(certificate)
    except ValueError as exc:
        raise DomainRefusal("Eso no es un certificado PEM válido.") from exc

    try:
        private = serialization.load_pem_private_key(key, password=None)
    except (ValueError, TypeError) as exc:
        raise DomainRefusal("Esa no es una clave privada PEM sin contraseña.") from exc

    if public_bytes(private.public_key()) != public_bytes(parsed.public_key()):
        raise DomainRefusal("La clave no corresponde al certificado.")

    if not (parsed.not_valid_before_utc <= timezone.now() <= parsed.not_valid_after_utc):
        raise DomainRefusal(f"El certificado no está vigente: vence {parsed.not_valid_after_utc:%Y-%m-%d}.")

    found = certificate_cuit(certificate)
    if expected_cuit and found != expected_cuit:
        raise DomainRefusal(f"El certificado declara el CUIT {found or 'ninguno'}, no {expected_cuit}.")
