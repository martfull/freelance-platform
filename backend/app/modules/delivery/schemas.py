from datetime import datetime

from pydantic import BaseModel, Field, field_validator

from app.common.enums import FileStatus
from app.modules.security.crypto_schemas import AES_GCM_ALGORITHM, RSA_OAEP_ALGORITHM


class CreateFileRequest(BaseModel):
    original_filename: str = Field(min_length=1, max_length=255)
    content_type: str | None = Field(default=None, max_length=255)
    file_data_base64: str = Field(min_length=1)
    sha256_hash: str = Field(min_length=64, max_length=64)
    chunk_size: int = Field(default=1024 * 1024, ge=1, le=10 * 1024 * 1024)

    @field_validator("original_filename")
    @classmethod
    def filename_must_not_be_blank(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("Filename must not be blank")
        return normalized

    @field_validator("sha256_hash")
    @classmethod
    def sha256_must_be_hex(cls, value: str) -> str:
        normalized = value.lower()
        if any(char not in "0123456789abcdef" for char in normalized):
            raise ValueError("SHA-256 hash must be lowercase hex")
        return normalized


class FileAssetResponse(BaseModel):
    id: int
    contract_id: int
    uploader_id: int
    original_filename: str
    content_type: str | None
    file_size: int
    chunk_size: int
    chunks_count: int
    sha256_hash: str
    algorithm: str
    key_algorithm: str = RSA_OAEP_ALGORITHM
    encrypted_key: str
    status: FileStatus
    created_at: datetime
    completed_at: datetime | None

    model_config = {"from_attributes": True}


class EncryptedFileChunkResponse(BaseModel):
    id: int
    file_id: int
    chunk_index: int
    algorithm: str = AES_GCM_ALGORITHM
    nonce: str
    ciphertext: str
    tag: str
    chunk_size: int
    created_at: datetime

    model_config = {"from_attributes": True}
