from sqlalchemy.orm import Session

from app.core.exceptions import NotFoundError, PermissionDeniedError
from app.modules.contracts import repository as contracts_repo
from app.modules.contracts.models import Contract
from app.modules.delivery import repository as delivery_repo
from app.modules.delivery.models import FileAsset


def require_contract_participant(db: Session, contract_id: int, user_id: int) -> Contract:
    contract = contracts_repo.get_contract(db, contract_id)
    if not contract:
        raise NotFoundError("Contract not found")
    if user_id not in (contract.client_id, contract.freelancer_id):
        raise PermissionDeniedError("Not a contract participant")
    return contract


def require_file_access(db: Session, file_id: int, user_id: int) -> FileAsset:
    file_asset = delivery_repo.get_file_asset(db, file_id)
    if not file_asset:
        raise NotFoundError("File not found")
    require_contract_participant(db, file_asset.contract_id, user_id)
    return file_asset


def get_counterparty_id(contract: Contract, user_id: int) -> int:
    if contract.client_id == user_id:
        return contract.freelancer_id
    if contract.freelancer_id == user_id:
        return contract.client_id
    raise PermissionDeniedError("Not a contract participant")
