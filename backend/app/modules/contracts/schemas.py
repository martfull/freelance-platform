from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel

from app.common.enums import ContractStatus, Currency


class ContractResponse(BaseModel):
    id: int
    task_id: int
    client_id: int
    freelancer_id: int
    amount: Decimal
    currency: Currency
    status: ContractStatus
    client_confirmed_at: datetime | None
    freelancer_confirmed_at: datetime | None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
