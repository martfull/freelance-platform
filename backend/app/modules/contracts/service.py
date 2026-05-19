from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.common.enums import ContractStatus
from app.core.exceptions import AppError, ConflictError, NotFoundError, PermissionDeniedError
from app.modules.contracts import repository as repo
from app.modules.contracts import state_machine
from app.modules.contracts.schemas import ContractResponse
from app.modules.marketplace import repository as marketplace_repo
from app.modules.marketplace.models import Offer


def create_from_offer(db: Session, offer: Offer) -> ContractResponse:
    task = marketplace_repo.get_task(db, offer.task_id)
    contract = repo.create_contract(
        db,
        task_id=task.id,
        client_id=task.creator_id,
        freelancer_id=offer.freelancer_id,
        amount=offer.proposed_amount or task.budget_amount,
        currency=task.currency,
    )
    db.commit()
    db.refresh(contract)
    return ContractResponse.model_validate(contract)


def confirm(db: Session, contract_id: int, user_id: int) -> ContractResponse:
    contract = repo.get_contract(db, contract_id)
    if not contract:
        raise NotFoundError("Contract not found")
    if contract.status != ContractStatus.PENDING_CONFIRMATION:
        raise AppError("Contract is not awaiting confirmation")

    now = datetime.now(timezone.utc)
    if contract.client_id == user_id:
        if contract.client_confirmed_at:
            raise ConflictError("Already confirmed")
        contract.client_confirmed_at = now
    elif contract.freelancer_id == user_id:
        if contract.freelancer_confirmed_at:
            raise ConflictError("Already confirmed")
        contract.freelancer_confirmed_at = now
    else:
        raise PermissionDeniedError("Not a contract participant")

    if contract.client_confirmed_at and contract.freelancer_confirmed_at:
        state_machine.transition(contract, ContractStatus.ACTIVE)

    repo.save(db, contract)
    db.commit()
    db.refresh(contract)
    return ContractResponse.model_validate(contract)


def cancel(db: Session, contract_id: int, user_id: int) -> ContractResponse:
    contract = repo.get_contract(db, contract_id)
    if not contract:
        raise NotFoundError("Contract not found")
    if user_id not in (contract.client_id, contract.freelancer_id):
        raise PermissionDeniedError("Not a contract participant")
    state_machine.transition(contract, ContractStatus.CANCELLED)
    repo.save(db, contract)
    db.commit()
    db.refresh(contract)
    return ContractResponse.model_validate(contract)


def get(db: Session, contract_id: int, user_id: int) -> ContractResponse:
    contract = repo.get_contract(db, contract_id)
    if not contract:
        raise NotFoundError("Contract not found")
    if user_id not in (contract.client_id, contract.freelancer_id):
        raise PermissionDeniedError("Not a contract participant")
    return ContractResponse.model_validate(contract)


def list_my(db: Session, user_id: int) -> list[ContractResponse]:
    contracts = repo.list_contracts_for_user(db, user_id)
    return [ContractResponse.model_validate(c) for c in contracts]
