from decimal import Decimal

from sqlalchemy.orm import Session

from app.common.enums import Currency
from app.modules.contracts.models import Contract


def create_contract(db: Session, task_id: int, client_id: int, freelancer_id: int,
                    amount: Decimal, currency: Currency) -> Contract:
    contract = Contract(
        task_id=task_id, client_id=client_id, freelancer_id=freelancer_id,
        amount=amount, currency=currency,
    )
    db.add(contract)
    db.flush()
    return contract


def get_contract(db: Session, contract_id: int) -> Contract | None:
    return db.get(Contract, contract_id)


def list_contracts_for_user(db: Session, user_id: int) -> list[Contract]:
    return db.query(Contract).filter(
        (Contract.client_id == user_id) | (Contract.freelancer_id == user_id)
    ).all()


def save(db: Session, contract: Contract) -> Contract:
    db.flush()
    return contract
