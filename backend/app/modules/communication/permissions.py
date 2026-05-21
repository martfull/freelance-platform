from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.modules.contracts import repository as contracts_repo
from app.modules.contracts.models import Contract


def require_contract_participant(db: Session, contract_id: int, user_id: int) -> Contract:
    contract = contracts_repo.get_contract(db, contract_id)
    if not contract:
        raise NotFoundError("Contract not found")
    if user_id not in (contract.client_id, contract.freelancer_id):
        raise PermissionDeniedError("Not a contract participant")
    return contract


def get_counterparty_id(contract: Contract, user_id: int) -> int:
    if contract.client_id == user_id:
        return contract.freelancer_id
    if contract.freelancer_id == user_id:
        return contract.client_id
    raise PermissionDeniedError("Not a contract participant")
