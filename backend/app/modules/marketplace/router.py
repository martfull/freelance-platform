from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.accounts.dependencies import get_current_user
from app.modules.accounts.models import User
from app.modules.marketplace import service
from app.modules.marketplace.schemas import (
    CreateOfferRequest,
    CreateTaskRequest,
    OfferResponse,
    TaskResponse,
    UpdateTaskRequest,
)

router = APIRouter(prefix="/marketplace", tags=["marketplace"])


@router.get("/tasks", response_model=list[TaskResponse])
def list_tasks(
    offset: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    db: Session = Depends(get_db),
):
    return service.list_tasks(db, offset=offset, limit=limit)


@router.post("/tasks", response_model=TaskResponse, status_code=201)
def create_task(
    body: CreateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_task(db, current_user.id, body)


@router.get("/tasks/{task_id}", response_model=TaskResponse)
def get_task(task_id: int, db: Session = Depends(get_db)):
    return service.get_task(db, task_id)


@router.patch("/tasks/{task_id}", response_model=TaskResponse)
def update_task(
    task_id: int,
    body: UpdateTaskRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.update_task(db, task_id, current_user.id, body)


@router.delete("/tasks/{task_id}", status_code=204)
def cancel_task(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.cancel_task(db, task_id, current_user.id)


@router.get("/tasks/{task_id}/offers", response_model=list[OfferResponse])
def list_offers(
    task_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.list_offers(db, task_id, current_user.id)


@router.post("/tasks/{task_id}/offers", response_model=OfferResponse, status_code=201)
def create_offer(
    task_id: int,
    body: CreateOfferRequest,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    return service.create_offer(db, task_id, current_user.id, body)


@router.post("/offers/{offer_id}/accept", status_code=201)
def accept_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    from app.modules.contracts import service as contracts_service
    offer = service.accept_offer(db, offer_id, current_user.id)
    return contracts_service.create_from_offer(db, offer)


@router.post("/offers/{offer_id}/withdraw", status_code=204)
def withdraw_offer(
    offer_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    service.withdraw_offer(db, offer_id, current_user.id)
