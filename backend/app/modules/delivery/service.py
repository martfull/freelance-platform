import math

from sqlalchemy.orm import Session

from app.common.enums import KeyType
from app.core.exceptions import AppError, ConflictError
from app.modules.accounts import repository as accounts_repo
from app.modules.accounts.models import User
from app.modules.delivery import permissions
from app.modules.delivery import repository as repo
from app.modules.delivery.chunking import iter_chunks
from app.modules.delivery.local_storage import LocalStorage
from app.modules.delivery.schemas import CreateFileRequest, EncryptedFileChunkResponse, FileAssetResponse
from app.modules.security import aes_gcm, rsa_oaep
from app.modules.security.crypto_schemas import AES_GCM_ALGORITHM, CryptoError
from app.modules.security.encoding import from_base64, to_base64
from app.modules.security.hashing import canonical_json_bytes, sha256_bytes


def create_file(
    db: Session,
    contract_id: int,
    uploader: User,
    body: CreateFileRequest,
) -> FileAssetResponse:
    contract = permissions.require_contract_participant(db, contract_id, uploader.id)
    recipient_id = permissions.get_counterparty_id(contract, uploader.id)

    recipient_key = accounts_repo.get_active_user_key(db, recipient_id, KeyType.RSA_ENCRYPTION)
    if not recipient_key:
        raise ConflictError("Recipient has no active RSA encryption public key")

    file_bytes = _decode_file_data(body.file_data_base64)
    actual_hash = sha256_bytes(file_bytes)
    if actual_hash != body.sha256_hash:
        raise AppError(
            "SHA-256 mismatch; file rejected",
            details={"expected": body.sha256_hash, "actual": actual_hash},
        )

    data_key = aes_gcm.generate_aes_key()
    try:
        wrapped_key = rsa_oaep.wrap_key(recipient_key.public_key_pem, data_key)
    except CryptoError as exc:
        raise AppError("File key wrapping failed") from exc

    chunks_count = math.ceil(len(file_bytes) / body.chunk_size)
    file_asset = repo.create_file_asset(
        db,
        contract_id=contract.id,
        uploader_id=uploader.id,
        original_filename=body.original_filename,
        content_type=body.content_type,
        file_size=len(file_bytes),
        chunk_size=body.chunk_size,
        chunks_count=chunks_count,
        sha256_hash=actual_hash,
        encrypted_payload_algorithm=AES_GCM_ALGORITHM,
        wrapped_key=wrapped_key,
    )

    storage = LocalStorage()
    try:
        for chunk_index, chunk_bytes in iter_chunks(file_bytes, body.chunk_size):
            aad = build_chunk_aad(
                file_id=file_asset.id,
                contract_id=contract.id,
                uploader_id=uploader.id,
                recipient_id=recipient_id,
                chunk_index=chunk_index,
                file_sha256=actual_hash,
            )
            encrypted_payload = aes_gcm.encrypt(chunk_bytes, data_key, aad=aad)
            storage_path = _chunk_storage_path(contract.id, file_asset.id, chunk_index)
            storage.write_bytes(storage_path, from_base64(encrypted_payload.ciphertext))
            repo.create_file_chunk(
                db,
                file_id=file_asset.id,
                chunk_index=chunk_index,
                storage_path=storage_path,
                encrypted_payload=encrypted_payload,
                chunk_size=len(chunk_bytes),
            )
        repo.mark_completed(db, file_asset)
        db.commit()
    except (CryptoError, OSError, ValueError) as exc:
        repo.mark_failed(db, file_asset)
        db.commit()
        raise AppError("Encrypted file upload failed") from exc

    db.refresh(file_asset)
    return FileAssetResponse.model_validate(file_asset)


def list_contract_files(db: Session, contract_id: int, user: User) -> list[FileAssetResponse]:
    contract = permissions.require_contract_participant(db, contract_id, user.id)
    files = repo.list_contract_files(db, contract.id)
    return [FileAssetResponse.model_validate(file_asset) for file_asset in files]


def get_file(db: Session, file_id: int, user: User) -> FileAssetResponse:
    file_asset = permissions.require_file_access(db, file_id, user.id)
    return FileAssetResponse.model_validate(file_asset)


def list_encrypted_chunks(db: Session, file_id: int, user: User) -> list[EncryptedFileChunkResponse]:
    file_asset = permissions.require_file_access(db, file_id, user.id)
    chunks = repo.list_file_chunks(db, file_asset.id)
    storage = LocalStorage()
    return [
        EncryptedFileChunkResponse(
            id=chunk.id,
            file_id=chunk.file_id,
            chunk_index=chunk.chunk_index,
            nonce=chunk.nonce,
            ciphertext=to_base64(storage.read_bytes(chunk.storage_path)),
            tag=chunk.tag,
            chunk_size=chunk.chunk_size,
            created_at=chunk.created_at,
        )
        for chunk in chunks
    ]


def build_chunk_aad(
    file_id: int,
    contract_id: int,
    uploader_id: int,
    recipient_id: int,
    chunk_index: int,
    file_sha256: str,
) -> bytes:
    return canonical_json_bytes(
        {
            "file_id": file_id,
            "contract_id": contract_id,
            "uploader_id": uploader_id,
            "recipient_id": recipient_id,
            "chunk_index": chunk_index,
            "file_sha256": file_sha256,
        }
    )


def _decode_file_data(file_data_base64: str) -> bytes:
    try:
        file_bytes = from_base64(file_data_base64)
    except CryptoError as exc:
        raise AppError("Invalid base64 file data") from exc
    if not file_bytes:
        raise AppError("File must not be empty")
    return file_bytes


def _chunk_storage_path(contract_id: int, file_id: int, chunk_index: int) -> str:
    return f"contracts/{contract_id}/files/{file_id}/chunks/{chunk_index}.bin"
