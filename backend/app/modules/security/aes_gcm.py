import os

from cryptography.exceptions import InvalidTag
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from app.modules.security.crypto_schemas import CryptoError, EncryptedPayload, IntegrityCheckFailed
from app.modules.security.encoding import from_base64, to_base64

AES_256_KEY_SIZE_BYTES = 32
AES_GCM_NONCE_SIZE_BYTES = 12
AES_GCM_TAG_SIZE_BYTES = 16


def generate_aes_key(size_bytes: int = AES_256_KEY_SIZE_BYTES) -> bytes:
    if size_bytes != AES_256_KEY_SIZE_BYTES:
        raise CryptoError("AES key size must be 32 bytes")
    return os.urandom(size_bytes)


def generate_nonce() -> bytes:
    return os.urandom(AES_GCM_NONCE_SIZE_BYTES)


def encrypt(plaintext: bytes, key: bytes, aad: bytes | None = None) -> EncryptedPayload:
    _validate_key(key)
    nonce = generate_nonce()
    aesgcm = AESGCM(key)
    ciphertext_with_tag = aesgcm.encrypt(nonce, plaintext, aad)
    ciphertext = ciphertext_with_tag[:-AES_GCM_TAG_SIZE_BYTES]
    tag = ciphertext_with_tag[-AES_GCM_TAG_SIZE_BYTES:]
    return EncryptedPayload(
        nonce=to_base64(nonce),
        ciphertext=to_base64(ciphertext),
        tag=to_base64(tag),
    )


def decrypt(payload: EncryptedPayload, key: bytes, aad: bytes | None = None) -> bytes:
    _validate_key(key)
    nonce = from_base64(payload.nonce)
    ciphertext = from_base64(payload.ciphertext)
    tag = from_base64(payload.tag)

    if len(nonce) != AES_GCM_NONCE_SIZE_BYTES:
        raise CryptoError("AES-GCM nonce must be 12 bytes")
    if len(tag) != AES_GCM_TAG_SIZE_BYTES:
        raise CryptoError("AES-GCM tag must be 16 bytes")

    aesgcm = AESGCM(key)
    try:
        return aesgcm.decrypt(nonce, ciphertext + tag, aad)
    except InvalidTag as exc:
        raise IntegrityCheckFailed("AES-GCM integrity check failed") from exc


def _validate_key(key: bytes) -> None:
    if len(key) != AES_256_KEY_SIZE_BYTES:
        raise CryptoError("AES key size must be 32 bytes")
