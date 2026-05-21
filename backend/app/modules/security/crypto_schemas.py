from pydantic import BaseModel, Field


AES_GCM_ALGORITHM = "AES-GCM"
RSA_OAEP_ALGORITHM = "RSA-OAEP-SHA256"
RSA_PSS_ALGORITHM = "RSA-PSS-SHA256"
SHA256_ALGORITHM = "SHA-256"


class CryptoError(ValueError):
    pass


class IntegrityCheckFailed(CryptoError):
    pass


class SignatureVerificationFailed(CryptoError):
    pass


class EncryptedPayload(BaseModel):
    algorithm: str = AES_GCM_ALGORITHM
    nonce: str = Field(min_length=1)
    ciphertext: str = Field(min_length=1)
    tag: str = Field(min_length=1)


class WrappedKey(BaseModel):
    algorithm: str = RSA_OAEP_ALGORITHM
    encrypted_key: str = Field(min_length=1)


class SignatureMetadata(BaseModel):
    algorithm: str = RSA_PSS_ALGORITHM
    payload_hash: str = Field(min_length=64, max_length=64)
    signature: str = Field(min_length=1)
