from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import ContractStatus, Currency
from app.database.base import Base


class Contract(Base):
    __tablename__ = "contracts"

    id: Mapped[int] = mapped_column(primary_key=True)
    task_id: Mapped[int] = mapped_column(ForeignKey("tasks.id", ondelete="RESTRICT"), nullable=False, index=True)
    client_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    freelancer_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[Currency] = mapped_column(Enum(Currency), nullable=False)
    status: Mapped[ContractStatus] = mapped_column(
        Enum(ContractStatus), nullable=False, default=ContractStatus.PENDING_CONFIRMATION, index=True
    )
    client_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    freelancer_confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )
