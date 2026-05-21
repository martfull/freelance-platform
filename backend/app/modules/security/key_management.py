from dataclasses import dataclass

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa

from app.modules.security.crypto_schemas import CryptoError


DEFAULT_RSA_KEY_SIZE_BITS = 2048
RSA_PUBLIC_EXPONENT = 65537


@dataclass(frozen=True)
class RSAKeyPair:
    private_key_pem: str
    public_key_pem: str


def generate_rsa_private_key(key_size: int = DEFAULT_RSA_KEY_SIZE_BITS) -> rsa.RSAPrivateKey:
    if key_size < DEFAULT_RSA_KEY_SIZE_BITS:
        raise CryptoError("RSA key size must be at least 2048 bits")
    return rsa.generate_private_key(
        public_exponent=RSA_PUBLIC_EXPONENT,
        key_size=key_size,
    )


def serialize_private_key(
    private_key: rsa.RSAPrivateKey,
    password: bytes | None = None,
) -> str:
    encryption_algorithm: serialization.KeySerializationEncryption
    if password:
        encryption_algorithm = serialization.BestAvailableEncryption(password)
    else:
        encryption_algorithm = serialization.NoEncryption()

    private_key_bytes = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=encryption_algorithm,
    )
    return private_key_bytes.decode("utf-8")


def serialize_public_key(public_key: rsa.RSAPublicKey) -> str:
    public_key_bytes = public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    )
    return public_key_bytes.decode("utf-8")


def generate_rsa_key_pair(
    key_size: int = DEFAULT_RSA_KEY_SIZE_BITS,
    private_key_password: bytes | None = None,
) -> RSAKeyPair:
    private_key = generate_rsa_private_key(key_size=key_size)
    return RSAKeyPair(
        private_key_pem=serialize_private_key(private_key, password=private_key_password),
        public_key_pem=serialize_public_key(private_key.public_key()),
    )
