from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import DisputeStatus
from app.database.base import Base


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(
        ForeignKey("contracts.id", ondelete="CASCADE"), nullable=False, index=True
    )
    opened_by_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="RESTRICT"), nullable=False, index=True)
    moderator_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DisputeStatus] = mapped_column(Enum(DisputeStatus), nullable=False, default=DisputeStatus.OPEN)
    resolution: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))
