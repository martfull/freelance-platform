from datetime import datetime

from pydantic import BaseModel, Field

from app.modules.security.crypto_schemas import RSA_OAEP_ALGORITHM


class CreateMessageRequest(BaseModel):
    plaintext: str = Field(min_length=1, max_length=10000)


class EncryptedMessageResponse(BaseModel):
    id: int
    contract_id: int
    sender_id: int
    recipient_id: int
    algorithm: str
    key_algorithm: str = RSA_OAEP_ALGORITHM
    nonce: str
    ciphertext: str
    tag: str
    encrypted_key: str
    created_at: datetime

    model_config = {"from_attributes": True}
