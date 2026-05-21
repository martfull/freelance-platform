from datetime import datetime

from pydantic import BaseModel, EmailStr, Field, field_validator

from app.common.enums import KeyStatus, KeyType, SystemRole


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str

    @field_validator("password")
    @classmethod
    def password_min_length(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Password must be at least 8 characters")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class RefreshRequest(BaseModel):
    refresh_token: str


class TokenResponse(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str = "bearer"


class UserResponse(BaseModel):
    id: int
    email: str
    system_role: SystemRole
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


class RegisterUserKeyRequest(BaseModel):
    key_type: KeyType
    public_key_pem: str = Field(min_length=64)

    @field_validator("public_key_pem")
    @classmethod
    def public_key_must_be_pem(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized.startswith("-----BEGIN PUBLIC KEY-----"):
            raise ValueError("Public key must be PEM encoded")
        if not normalized.endswith("-----END PUBLIC KEY-----"):
            raise ValueError("Public key must be PEM encoded")
        return normalized


class UserKeyResponse(BaseModel):
    id: int
    user_id: int
    key_type: KeyType
    public_key_pem: str
    status: KeyStatus
    created_at: datetime
    rotated_at: datetime | None

    model_config = {"from_attributes": True}


class PublicUserKeysResponse(BaseModel):
    user_id: int
    keys: list[UserKeyResponse]
