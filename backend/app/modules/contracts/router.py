from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.accounts.dependencies import get_current_user
from app.modules.accounts.models import User
from app.modules.contracts import service
from app.modules.contracts.schemas import ContractResponse

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("/my", response_model=list[ContractResponse])
def list_my(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    return service.list_my(db, current_user.id)


@router.get("/{contract_id}", response_model=ContractResponse)
def get_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.get(db, contract_id, current_user.id)


@router.post("/{contract_id}/confirm", response_model=ContractResponse)
def confirm(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.confirm(db, contract_id, current_user.id)


@router.post("/{contract_id}/cancel", response_model=ContractResponse)
def cancel(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.cancel(db, contract_id, current_user.id)
