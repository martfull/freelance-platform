from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, Field

from app.common.enums import Currency, OfferStatus, TaskStatus


class CreateTaskRequest(BaseModel):
    title: str = Field(min_length=5, max_length=255)
    description: str = Field(min_length=10)
    budget_amount: Decimal = Field(gt=0, decimal_places=2)
    currency: Currency = Currency.USD


class UpdateTaskRequest(BaseModel):
    title: str | None = Field(default=None, min_length=5, max_length=255)
    description: str | None = Field(default=None, min_length=10)
    budget_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)


class TaskResponse(BaseModel):
    id: int
    creator_id: int
    title: str
    description: str
    budget_amount: Decimal
    currency: Currency
    status: TaskStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class CreateOfferRequest(BaseModel):
    message: str | None = Field(default=None, max_length=2000)
    proposed_amount: Decimal | None = Field(default=None, gt=0, decimal_places=2)


class OfferResponse(BaseModel):
    id: int
    task_id: int
    freelancer_id: int
    message: str | None
    proposed_amount: Decimal | None
    status: OfferStatus
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
