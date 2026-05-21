from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.accounts.dependencies import get_current_user
from app.modules.accounts.models import User
from app.modules.communication import service
from app.modules.communication.schemas import CreateMessageRequest, EncryptedMessageResponse

router = APIRouter(prefix="/communication", tags=["communication"])


@router.post("/contracts/{contract_id}/messages", response_model=EncryptedMessageResponse, status_code=201)
def create_message(
    contract_id: int,
    body: CreateMessageRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_message(db, contract_id, current_user, body)


@router.get("/contracts/{contract_id}/messages", response_model=list[EncryptedMessageResponse])
def list_messages(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_contract_messages(db, contract_id, current_user)
