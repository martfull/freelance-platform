from sqlalchemy.orm import Session

from app.common.enums import OfferStatus, TaskStatus
from app.core.exceptions import AppError, ConflictError, NotFoundError, PermissionDeniedError
from app.modules.marketplace import repository as repo
from app.modules.marketplace.schemas import (
    CreateOfferRequest,
    CreateTaskRequest,
    OfferResponse,
    TaskResponse,
    UpdateTaskRequest,
)


def create_task(db: Session, creator_id: int, body: CreateTaskRequest) -> TaskResponse:
    task = repo.create_task(
        db, creator_id=creator_id, title=body.title, description=body.description,
        budget_amount=body.budget_amount, currency=body.currency,
    )
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


def get_task(db: Session, task_id: int) -> TaskResponse:
    task = repo.get_task(db, task_id)
    if not task:
        raise NotFoundError("Task not found")
    return TaskResponse.model_validate(task)


def list_tasks(db: Session, offset: int = 0, limit: int = 20) -> list[TaskResponse]:
    tasks = repo.list_open_tasks(db, offset=offset, limit=limit)
    return [TaskResponse.model_validate(t) for t in tasks]


def update_task(db: Session, task_id: int, user_id: int, body: UpdateTaskRequest) -> TaskResponse:
    task = repo.get_task(db, task_id)
    if not task:
        raise NotFoundError("Task not found")
    if task.creator_id != user_id:
        raise PermissionDeniedError("Only task owner can edit it")
    if task.status not in (TaskStatus.OPEN, TaskStatus.IN_NEGOTIATION):
        raise AppError("Task cannot be edited in its current status")
    repo.update_task(db, task, title=body.title, description=body.description, budget_amount=body.budget_amount)
    db.commit()
    db.refresh(task)
    return TaskResponse.model_validate(task)


def cancel_task(db: Session, task_id: int, user_id: int) -> None:
    task = repo.get_task(db, task_id)
    if not task:
        raise NotFoundError("Task not found")
    if task.creator_id != user_id:
        raise PermissionDeniedError("Only task owner can cancel it")
    if task.status == TaskStatus.CONTRACTED:
        raise AppError("Cannot cancel a task with an active contract")
    repo.set_task_status(db, task, TaskStatus.CANCELLED)
    db.commit()


def create_offer(db: Session, task_id: int, freelancer_id: int, body: CreateOfferRequest) -> OfferResponse:
    task = repo.get_task(db, task_id)
    if not task:
        raise NotFoundError("Task not found")
    if task.status not in (TaskStatus.OPEN, TaskStatus.IN_NEGOTIATION):
        raise AppError("Task is not open for offers")
    if task.creator_id == freelancer_id:
        raise PermissionDeniedError("Cannot create offer on your own task")
    if repo.get_pending_offer(db, task_id, freelancer_id):
        raise ConflictError("You already have a pending offer for this task")
    offer = repo.create_offer(
        db, task_id=task_id, freelancer_id=freelancer_id,
        message=body.message, proposed_amount=body.proposed_amount,
    )
    repo.set_task_status(db, task, TaskStatus.IN_NEGOTIATION)
    db.commit()
    db.refresh(offer)
    return OfferResponse.model_validate(offer)


def list_offers(db: Session, task_id: int, user_id: int) -> list[OfferResponse]:
    task = repo.get_task(db, task_id)
    if not task:
        raise NotFoundError("Task not found")
    if task.creator_id != user_id:
        raise PermissionDeniedError("Only task owner can view offers")
    offers = repo.list_offers_for_task(db, task_id)
    return [OfferResponse.model_validate(o) for o in offers]


def accept_offer(db: Session, offer_id: int, user_id: int):
    offer = repo.get_offer(db, offer_id)
    if not offer:
        raise NotFoundError("Offer not found")
    task = repo.get_task(db, offer.task_id)
    if task.creator_id != user_id:
        raise PermissionDeniedError("Only task owner can accept offers")
    if offer.status != OfferStatus.PENDING:
        raise AppError("Offer is no longer pending")
    repo.set_offer_status(db, offer, OfferStatus.ACCEPTED)
    repo.reject_other_offers(db, offer.task_id, offer.id)
    repo.set_task_status(db, task, TaskStatus.CONTRACTED)
    db.commit()
    db.refresh(offer)
    return offer


def withdraw_offer(db: Session, offer_id: int, user_id: int) -> None:
    offer = repo.get_offer(db, offer_id)
    if not offer:
        raise NotFoundError("Offer not found")
    if offer.freelancer_id != user_id:
        raise PermissionDeniedError("Only offer owner can withdraw it")
    if offer.status != OfferStatus.PENDING:
        raise AppError("Only pending offers can be withdrawn")
    repo.set_offer_status(db, offer, OfferStatus.WITHDRAWN)
    db.commit()
