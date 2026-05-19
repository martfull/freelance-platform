from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.database.session import get_db
from app.modules.accounts.dependencies import get_current_user
from app.modules.accounts.models import User
from app.modules.contracts import repository as repo


def get_participant_contract(
    contract_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    contract = repo.get_contract(db, contract_id)
    if not contract:
        raise NotFoundError("Contract not found")
    if current_user.id not in (contract.client_id, contract.freelancer_id):
        raise PermissionDeniedError("Not a contract participant")
    return contract
