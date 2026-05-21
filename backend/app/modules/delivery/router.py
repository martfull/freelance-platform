from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.accounts.dependencies import get_current_user
from app.modules.accounts.models import User
from app.modules.delivery import service
from app.modules.delivery.schemas import CreateFileRequest, EncryptedFileChunkResponse, FileAssetResponse

router = APIRouter(prefix="/delivery", tags=["delivery"])


@router.post("/contracts/{contract_id}/files", response_model=FileAssetResponse, status_code=201)
def create_file(
    contract_id: int,
    body: CreateFileRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_file(db, contract_id, current_user, body)


@router.get("/contracts/{contract_id}/files", response_model=list[FileAssetResponse])
def list_contract_files(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_contract_files(db, contract_id, current_user)


@router.get("/files/{file_id}", response_model=FileAssetResponse)
def get_file(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get_file(db, file_id, current_user)


@router.get("/files/{file_id}/chunks", response_model=list[EncryptedFileChunkResponse])
def list_encrypted_chunks(
    file_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_encrypted_chunks(db, file_id, current_user)
