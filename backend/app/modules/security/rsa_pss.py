from cryptography.exceptions import InvalidSignature
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa

from app.modules.security.crypto_schemas import CryptoError, SignatureMetadata, SignatureVerificationFailed
from app.modules.security.encoding import from_base64, to_base64
from app.modules.security.hashing import sha256_bytes


MIN_RSA_KEY_SIZE_BITS = 2048


def sign_payload(private_key_pem: str, payload: bytes, password: bytes | None = None) -> SignatureMetadata:
    private_key = _load_rsa_private_key(private_key_pem, password=password)
    signature = private_key.sign(
        payload,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.MAX_LENGTH,
        ),
        hashes.SHA256(),
    )
    return SignatureMetadata(
        payload_hash=sha256_bytes(payload),
        signature=to_base64(signature),
    )


def verify_signature(public_key_pem: str, payload: bytes, signature: str) -> bool:
    public_key = _load_rsa_public_key(public_key_pem)
    signature_bytes = from_base64(signature)
    try:
        public_key.verify(
            signature_bytes,
            payload,
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH,
            ),
            hashes.SHA256(),
        )
        return True
    except InvalidSignature as exc:
        raise SignatureVerificationFailed("RSA-PSS signature verification failed") from exc


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
