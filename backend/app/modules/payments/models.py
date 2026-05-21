from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.common.enums import Currency, EscrowTransactionStatus, EscrowTransactionType
from app.database.base import Base


class EscrowAccount(Base):
    __tablename__ = "escrow_accounts"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"), nullable=False, unique=True)
    available_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    held_balance: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False, default=0)
    currency: Mapped[Currency] = mapped_column(Enum(Currency), nullable=False, default=Currency.USD)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )


class EscrowTransaction(Base):
    __tablename__ = "escrow_transactions"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int | None] = mapped_column(ForeignKey("contracts.id", ondelete="SET NULL"), index=True)
    payer_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    receiver_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), index=True)
    amount: Mapped[Decimal] = mapped_column(Numeric(12, 2), nullable=False)
    currency: Mapped[Currency] = mapped_column(Enum(Currency), nullable=False)
    type: Mapped[EscrowTransactionType] = mapped_column(Enum(EscrowTransactionType), nullable=False)
    status: Mapped[EscrowTransactionStatus] = mapped_column(
        Enum(EscrowTransactionStatus), nullable=False, default=EscrowTransactionStatus.PENDING
    )
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    signature: Mapped[str | None] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
