from sqlalchemy.orm import Session

from app.modules.communication.models import Message
from app.modules.security.crypto_schemas import EncryptedPayload, WrappedKey


def create_message(
    db: Session,
    contract_id: int,
    sender_id: int,
    recipient_id: int,
    encrypted_payload: EncryptedPayload,
    wrapped_key: WrappedKey,
) -> Message:
    message = Message(
        contract_id=contract_id,
        sender_id=sender_id,
        recipient_id=recipient_id,
        algorithm=encrypted_payload.algorithm,
        nonce=encrypted_payload.nonce,
        ciphertext=encrypted_payload.ciphertext,
        tag=encrypted_payload.tag,
        encrypted_key=wrapped_key.encrypted_key,
    )
    db.add(message)
    db.flush()
    return message


def list_contract_messages(db: Session, contract_id: int) -> list[Message]:
    return db.query(Message).filter(Message.contract_id == contract_id).order_by(Message.created_at.asc()).all()
