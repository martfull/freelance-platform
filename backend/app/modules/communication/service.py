from sqlalchemy.orm import Session

from app.common.enums import KeyType
from app.core.exceptions import AppError, ConflictError
from app.modules.accounts import repository as accounts_repo
from app.modules.accounts.models import User
from app.modules.communication import permissions
from app.modules.communication import repository as repo
from app.modules.communication.schemas import CreateMessageRequest, EncryptedMessageResponse
from app.modules.security import aes_gcm, rsa_oaep
from app.modules.security.crypto_schemas import CryptoError
from app.modules.security.hashing import canonical_json_bytes


def create_message(
    db: Session,
    contract_id: int,
    sender: User,
    body: CreateMessageRequest,
) -> EncryptedMessageResponse:
    contract = permissions.require_contract_participant(db, contract_id, sender.id)
    recipient_id = permissions.get_counterparty_id(contract, sender.id)

    recipient_key = accounts_repo.get_active_user_key(db, recipient_id, KeyType.RSA_ENCRYPTION)
    if not recipient_key:
        raise ConflictError("Recipient has no active RSA encryption public key")

    aad = build_message_aad(contract_id=contract.id, sender_id=sender.id, recipient_id=recipient_id)
    data_key = aes_gcm.generate_aes_key()

    try:
        encrypted_payload = aes_gcm.encrypt(body.plaintext.encode("utf-8"), data_key, aad=aad)
        wrapped_key = rsa_oaep.wrap_key(recipient_key.public_key_pem, data_key)
    except CryptoError as exc:
        raise AppError("Message encryption failed") from exc

    message = repo.create_message(
        db,
        contract_id=contract.id,
        sender_id=sender.id,
        recipient_id=recipient_id,
        encrypted_payload=encrypted_payload,
        wrapped_key=wrapped_key,
    )
    db.commit()
    db.refresh(message)
    return EncryptedMessageResponse.model_validate(message)


def list_contract_messages(db: Session, contract_id: int, user: User) -> list[EncryptedMessageResponse]:
    contract = permissions.require_contract_participant(db, contract_id, user.id)
    messages = repo.list_contract_messages(db, contract.id)
    return [EncryptedMessageResponse.model_validate(message) for message in messages]


def build_message_aad(contract_id: int, sender_id: int, recipient_id: int) -> bytes:
    return canonical_json_bytes(
        {
            "contract_id": contract_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
        }
    )
