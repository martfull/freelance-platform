import base64
import binascii

from app.modules.security.crypto_schemas import CryptoError


def to_base64(value: bytes) -> str:
    return base64.b64encode(value).decode("ascii")


def from_base64(value: str) -> bytes:
    try:
        return base64.b64decode(value.encode("ascii"), validate=True)
    except (binascii.Error, UnicodeEncodeError) as exc:
        raise CryptoError("Invalid base64 value") from exc
