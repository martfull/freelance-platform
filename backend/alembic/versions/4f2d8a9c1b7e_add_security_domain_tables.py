"""add security domain tables

Revision ID: 4f2d8a9c1b7e
Revises: 116ff2a535e2
Create Date: 2026-05-21 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision: str = "4f2d8a9c1b7e"
down_revision: Union[str, None] = "116ff2a535e2"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


currency_enum = postgresql.ENUM("USD", "EUR", "UAH", "PLN", name="currency", create_type=False)


def upgrade() -> None:
    op.create_table(
        "user_keys",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("key_type", sa.Enum("RSA_ENCRYPTION", "RSA_SIGNING", name="keytype"), nullable=False),
        sa.Column("public_key_pem", sa.Text(), nullable=False),
        sa.Column("private_key_reference", sa.Text(), nullable=True),
        sa.Column("status", sa.Enum("ACTIVE", "ROTATED", "REVOKED", name="keystatus"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("rotated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_user_keys_user_id"), "user_keys", ["user_id"], unique=False)

    op.create_table(
        "messages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("sender_id", sa.Integer(), nullable=False),
        sa.Column("recipient_id", sa.Integer(), nullable=False),
        sa.Column("algorithm", sa.String(length=32), nullable=False),
        sa.Column("nonce", sa.Text(), nullable=False),
        sa.Column("ciphertext", sa.Text(), nullable=False),
        sa.Column("tag", sa.Text(), nullable=False),
        sa.Column("encrypted_key", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["recipient_id"], ["users.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["sender_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_messages_contract_id"), "messages", ["contract_id"], unique=False)
    op.create_index(op.f("ix_messages_recipient_id"), "messages", ["recipient_id"], unique=False)
    op.create_index(op.f("ix_messages_sender_id"), "messages", ["sender_id"], unique=False)

    op.create_table(
        "file_assets",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("uploader_id", sa.Integer(), nullable=False),
        sa.Column("original_filename", sa.String(length=255), nullable=False),
        sa.Column("content_type", sa.String(length=255), nullable=True),
        sa.Column("file_size", sa.BigInteger(), nullable=False),
        sa.Column("chunk_size", sa.Integer(), nullable=False),
        sa.Column("chunks_count", sa.Integer(), nullable=False),
        sa.Column("sha256_hash", sa.String(length=64), nullable=False),
        sa.Column("algorithm", sa.String(length=32), nullable=False),
        sa.Column("encrypted_key", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("INITIALIZED", "UPLOADING", "COMPLETED", "FAILED", "REJECTED", name="filestatus"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["uploader_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_file_assets_contract_id"), "file_assets", ["contract_id"], unique=False)
    op.create_index(op.f("ix_file_assets_uploader_id"), "file_assets", ["uploader_id"], unique=False)

    op.create_table(
        "file_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("file_id", sa.Integer(), nullable=False),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.Text(), nullable=False),
        sa.Column("nonce", sa.Text(), nullable=False),
        sa.Column("tag", sa.Text(), nullable=False),
        sa.Column("chunk_size", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["file_id"], ["file_assets.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("file_id", "chunk_index", name="uq_file_chunks_file_index"),
    )
    op.create_index(op.f("ix_file_chunks_file_id"), "file_chunks", ["file_id"], unique=False)

    op.create_table(
        "escrow_accounts",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("available_balance", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("held_balance", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", currency_enum, nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )

    op.create_table(
        "escrow_transactions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=True),
        sa.Column("payer_id", sa.Integer(), nullable=True),
        sa.Column("receiver_id", sa.Integer(), nullable=True),
        sa.Column("amount", sa.Numeric(precision=12, scale=2), nullable=False),
        sa.Column("currency", currency_enum, nullable=False),
        sa.Column(
            "type",
            sa.Enum("DEPOSIT", "HOLD", "RELEASE", "REFUND", "ADJUSTMENT", name="escrowtransactiontype"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("PENDING", "COMPLETED", "FAILED", name="escrowtransactionstatus"),
            nullable=False,
        ),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["payer_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["receiver_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_escrow_transactions_contract_id"), "escrow_transactions", ["contract_id"], unique=False)
    op.create_index(op.f("ix_escrow_transactions_payer_id"), "escrow_transactions", ["payer_id"], unique=False)
    op.create_index(op.f("ix_escrow_transactions_receiver_id"), "escrow_transactions", ["receiver_id"], unique=False)

    op.create_table(
        "disputes",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("contract_id", sa.Integer(), nullable=False),
        sa.Column("opened_by_id", sa.Integer(), nullable=False),
        sa.Column("moderator_id", sa.Integer(), nullable=True),
        sa.Column("reason", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.Enum("OPEN", "UNDER_REVIEW", "RESOLVED", "REJECTED", name="disputestatus"),
            nullable=False,
        ),
        sa.Column("resolution", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["contract_id"], ["contracts.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["moderator_id"], ["users.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["opened_by_id"], ["users.id"], ondelete="RESTRICT"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_disputes_contract_id"), "disputes", ["contract_id"], unique=False)
    op.create_index(op.f("ix_disputes_moderator_id"), "disputes", ["moderator_id"], unique=False)
    op.create_index(op.f("ix_disputes_opened_by_id"), "disputes", ["opened_by_id"], unique=False)

    op.create_table(
        "audit_logs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("actor_id", sa.Integer(), nullable=True),
        sa.Column("entity_type", sa.String(length=64), nullable=False),
        sa.Column("entity_id", sa.Integer(), nullable=False),
        sa.Column("action", sa.String(length=64), nullable=False),
        sa.Column("payload_hash", sa.String(length=64), nullable=False),
        sa.Column("signature", sa.Text(), nullable=True),
        sa.Column("ip_address", sa.String(length=45), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.ForeignKeyConstraint(["actor_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_audit_logs_actor_id"), "audit_logs", ["actor_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_id"), "audit_logs", ["entity_id"], unique=False)
    op.create_index(op.f("ix_audit_logs_entity_type"), "audit_logs", ["entity_type"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_audit_logs_entity_type"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_entity_id"), table_name="audit_logs")
    op.drop_index(op.f("ix_audit_logs_actor_id"), table_name="audit_logs")
    op.drop_table("audit_logs")

    op.drop_index(op.f("ix_disputes_opened_by_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_moderator_id"), table_name="disputes")
    op.drop_index(op.f("ix_disputes_contract_id"), table_name="disputes")
    op.drop_table("disputes")

    op.drop_index(op.f("ix_escrow_transactions_receiver_id"), table_name="escrow_transactions")
    op.drop_index(op.f("ix_escrow_transactions_payer_id"), table_name="escrow_transactions")
    op.drop_index(op.f("ix_escrow_transactions_contract_id"), table_name="escrow_transactions")
    op.drop_table("escrow_transactions")
    op.drop_table("escrow_accounts")

    op.drop_index(op.f("ix_file_chunks_file_id"), table_name="file_chunks")
    op.drop_table("file_chunks")

    op.drop_index(op.f("ix_file_assets_uploader_id"), table_name="file_assets")
    op.drop_index(op.f("ix_file_assets_contract_id"), table_name="file_assets")
    op.drop_table("file_assets")

    op.drop_index(op.f("ix_messages_sender_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_recipient_id"), table_name="messages")
    op.drop_index(op.f("ix_messages_contract_id"), table_name="messages")
    op.drop_table("messages")

    op.drop_index(op.f("ix_user_keys_user_id"), table_name="user_keys")
    op.drop_table("user_keys")

    sa.Enum(name="disputestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="escrowtransactionstatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="escrowtransactiontype").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="filestatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="keystatus").drop(op.get_bind(), checkfirst=True)
    sa.Enum(name="keytype").drop(op.get_bind(), checkfirst=True)
