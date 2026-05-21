from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.common.enums import FileStatus
from app.modules.delivery.models import FileAsset, FileChunk
from app.modules.security.crypto_schemas import EncryptedPayload, WrappedKey


def create_file_asset(
    db: Session,
    contract_id: int,
    uploader_id: int,
    original_filename: str,
    content_type: str | None,
    file_size: int,
    chunk_size: int,
    chunks_count: int,
    sha256_hash: str,
    encrypted_payload_algorithm: str,
    wrapped_key: WrappedKey,
) -> FileAsset:
    file_asset = FileAsset(
        contract_id=contract_id,
        uploader_id=uploader_id,
        original_filename=original_filename,
        content_type=content_type,
        file_size=file_size,
        chunk_size=chunk_size,
        chunks_count=chunks_count,
        sha256_hash=sha256_hash,
        algorithm=encrypted_payload_algorithm,
        encrypted_key=wrapped_key.encrypted_key,
        status=FileStatus.UPLOADING,
    )
    db.add(file_asset)
    db.flush()
    return file_asset


def get_file_asset(db: Session, file_id: int) -> FileAsset | None:
    return db.get(FileAsset, file_id)


def list_contract_files(db: Session, contract_id: int) -> list[FileAsset]:
    return db.query(FileAsset).filter(FileAsset.contract_id == contract_id).order_by(FileAsset.created_at.desc()).all()


def create_file_chunk(
    db: Session,
    file_id: int,
    chunk_index: int,
    storage_path: str,
    encrypted_payload: EncryptedPayload,
    chunk_size: int,
) -> FileChunk:
    chunk = FileChunk(
        file_id=file_id,
        chunk_index=chunk_index,
        storage_path=storage_path,
        nonce=encrypted_payload.nonce,
        tag=encrypted_payload.tag,
        chunk_size=chunk_size,
    )
    db.add(chunk)
    db.flush()
    return chunk


def list_file_chunks(db: Session, file_id: int) -> list[FileChunk]:
    return db.query(FileChunk).filter(FileChunk.file_id == file_id).order_by(FileChunk.chunk_index.asc()).all()


def mark_completed(db: Session, file_asset: FileAsset) -> FileAsset:
    file_asset.status = FileStatus.COMPLETED
    file_asset.completed_at = datetime.now(timezone.utc)
    db.flush()
    return file_asset


def mark_failed(db: Session, file_asset: FileAsset) -> FileAsset:
    file_asset.status = FileStatus.FAILED
    db.flush()
    return file_asset
