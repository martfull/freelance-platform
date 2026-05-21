from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app.modules.security.crypto_schemas import CryptoError, WrappedKey
from app.modules.security.encoding import from_base64, to_base64


MIN_RSA_KEY_SIZE_BITS = 2048


def wrap_key(public_key_pem: str, data_key: bytes) -> WrappedKey:
    public_key = _load_rsa_public_key(public_key_pem)
    encrypted_key = public_key.encrypt(
        data_key,
        padding.OAEP(
            mgf=padding.MGF1(algorithm=hashes.SHA256()),
            algorithm=hashes.SHA256(),
            label=None,
        ),
    )
    return WrappedKey(encrypted_key=to_base64(encrypted_key))


def unwrap_key(private_key_pem: str, encrypted_key: str, password: bytes | None = None) -> bytes:
    private_key = _load_rsa_private_key(private_key_pem, password=password)
    encrypted_key_bytes = from_base64(encrypted_key)
    try:
        return private_key.decrypt(
            encrypted_key_bytes,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
    except ValueError as exc:
        raise CryptoError("RSA-OAEP key unwrap failed") from exc


def _load_rsa_public_key(public_key_pem: str) -> rsa.RSAPublicKey:
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    except ValueError as exc:
        raise CryptoError("Invalid RSA public key PEM") from exc

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise CryptoError("Only RSA public keys are supported")
    if public_key.key_size < MIN_RSA_KEY_SIZE_BITS:
        raise CryptoError("RSA public key must be at least 2048 bits")
    return public_key


def _load_rsa_private_key(private_key_pem: str, password: bytes | None = None) -> rsa.RSAPrivateKey:
    try:
        private_key = serialization.load_pem_private_key(private_key_pem.encode("utf-8"), password=password)
    except (TypeError, ValueError) as exc:
        raise CryptoError("Invalid RSA private key PEM") from exc

    if not isinstance(private_key, rsa.RSAPrivateKey):
        raise CryptoError("Only RSA private keys are supported")
    if private_key.key_size < MIN_RSA_KEY_SIZE_BITS:
        raise CryptoError("RSA private key must be at least 2048 bits")
    return private_key
