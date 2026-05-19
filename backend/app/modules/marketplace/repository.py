from decimal import Decimal

from sqlalchemy.orm import Session

from app.common.enums import OfferStatus, TaskStatus
from app.modules.marketplace.models import Offer, Task


def create_task(db: Session, creator_id: int, title: str, description: str,
                budget_amount: Decimal, currency: str) -> Task:
    task = Task(creator_id=creator_id, title=title, description=description,
                budget_amount=budget_amount, currency=currency)
    db.add(task)
    db.flush()
    return task


def get_task(db: Session, task_id: int) -> Task | None:
    return db.get(Task, task_id)


def list_open_tasks(db: Session, offset: int = 0, limit: int = 20) -> list[Task]:
    return db.query(Task).filter(Task.status == TaskStatus.OPEN).offset(offset).limit(limit).all()


def update_task(db: Session, task: Task, **fields) -> Task:
    for key, value in fields.items():
        if value is not None:
            setattr(task, key, value)
    return task


def set_task_status(db: Session, task: Task, status: TaskStatus) -> Task:
    task.status = status
    return task


def create_offer(db: Session, task_id: int, freelancer_id: int,
                 message: str | None, proposed_amount: Decimal | None) -> Offer:
    offer = Offer(task_id=task_id, freelancer_id=freelancer_id,
                  message=message, proposed_amount=proposed_amount)
    db.add(offer)
    db.flush()
    return offer


def get_offer(db: Session, offer_id: int) -> Offer | None:
    return db.get(Offer, offer_id)


def list_offers_for_task(db: Session, task_id: int) -> list[Offer]:
    return db.query(Offer).filter(Offer.task_id == task_id).all()


def get_pending_offer(db: Session, task_id: int, freelancer_id: int) -> Offer | None:
    return db.query(Offer).filter(
        Offer.task_id == task_id,
        Offer.freelancer_id == freelancer_id,
        Offer.status == OfferStatus.PENDING,
    ).first()


def set_offer_status(db: Session, offer: Offer, status: OfferStatus) -> Offer:
    offer.status = status
    return offer


def reject_other_offers(db: Session, task_id: int, accepted_offer_id: int) -> None:
    db.query(Offer).filter(
        Offer.task_id == task_id,
        Offer.id != accepted_offer_id,
        Offer.status == OfferStatus.PENDING,
    ).update({"status": OfferStatus.REJECTED})
