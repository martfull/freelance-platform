from datetime import datetime, timedelta, timezone

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from sqlalchemy.orm import Session

from app.common.enums import KeyStatus, KeyType
from app.core.config import get_settings
from app.core.exceptions import AppError, ConflictError, NotFoundError
from app.modules.accounts import repository as repo
from app.modules.accounts.jwt import (
    AuthError,
    create_access_token,
    create_refresh_token,
    decode_refresh_token,
)
from app.modules.accounts.models import User
from app.modules.accounts.password import hash_password, verify_password
from app.modules.accounts.schemas import PublicUserKeysResponse, TokenResponse, UserKeyResponse, UserResponse

settings = get_settings()


def register(db: Session, email: str, password: str) -> UserResponse:
    if repo.get_user_by_email(db, email):
        raise ConflictError("Email already registered")
    user = repo.create_user(db, email=email, hashed_password=hash_password(password))
    db.commit()
    db.refresh(user)
    return UserResponse.model_validate(user)


def login(db: Session, email: str, password: str) -> TokenResponse:
    user = repo.get_user_by_email(db, email)
    if not user or not verify_password(password, user.hashed_password):
        raise AuthError("Invalid email or password")
    if not user.is_active:
        raise AuthError("Account is inactive")
    return _issue_tokens(db, user)


def refresh(db: Session, raw_token: str) -> TokenResponse:
    user_id = decode_refresh_token(raw_token)
    stored = repo.get_refresh_token(db, raw_token)
    if not stored or stored.expires_at < datetime.now(timezone.utc):
        raise AuthError("Refresh token is invalid or expired")
    repo.revoke_refresh_token(db, raw_token)
    user = repo.get_user_by_id(db, user_id)
    if not user or not user.is_active:
        raise AuthError("User not found or inactive")
    return _issue_tokens(db, user)


def logout(db: Session, raw_token: str) -> None:
    repo.revoke_refresh_token(db, raw_token)
    db.commit()


def register_user_key(
    db: Session,
    user: User,
    key_type: KeyType,
    public_key_pem: str,
) -> UserKeyResponse:
    _validate_rsa_public_key(public_key_pem)

    active_key = repo.get_active_user_key(db, user.id, key_type)
    if active_key:
        active_key.status = KeyStatus.ROTATED
        active_key.rotated_at = datetime.now(timezone.utc)

    key = repo.create_user_key(db, user_id=user.id, key_type=key_type, public_key_pem=public_key_pem)
    db.commit()
    db.refresh(key)
    return UserKeyResponse.model_validate(key)


def list_my_keys(db: Session, user: User) -> list[UserKeyResponse]:
    keys = repo.list_user_keys(db, user.id)
    return [UserKeyResponse.model_validate(key) for key in keys]


def get_public_keys(db: Session, user_id: int) -> PublicUserKeysResponse:
    user = repo.get_user_by_id(db, user_id)
    if not user:
        raise NotFoundError("User not found")

    keys = repo.list_user_keys(db, user_id, active_only=True)
    return PublicUserKeysResponse(
        user_id=user_id,
        keys=[UserKeyResponse.model_validate(key) for key in keys],
    )


def _issue_tokens(db: Session, user: User) -> TokenResponse:
    access = create_access_token(user.id, user.system_role)
    refresh_raw = create_refresh_token(user.id)
    expires_at = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    repo.save_refresh_token(db, user.id, refresh_raw, expires_at)
    db.commit()
    return TokenResponse(access_token=access, refresh_token=refresh_raw)


def _validate_rsa_public_key(public_key_pem: str) -> None:
    try:
        public_key = serialization.load_pem_public_key(public_key_pem.encode("utf-8"))
    except ValueError as exc:
        raise AppError("Invalid public key PEM") from exc

    if not isinstance(public_key, rsa.RSAPublicKey):
        raise AppError("Only RSA public keys are supported")

    if public_key.key_size < 2048:
        raise AppError("RSA public key must be at least 2048 bits")
