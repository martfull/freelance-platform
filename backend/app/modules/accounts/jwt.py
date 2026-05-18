import secrets
from datetime import datetime, timedelta, timezone

from jose import JWTError, jwt

from app.common.enums import SystemRole
from app.core.config import get_settings
from app.core.exceptions import AppError

settings = get_settings()

ALGORITHM = "HS256"


class AuthError(AppError):
    status_code = 401
    code = "UNAUTHORIZED"


def create_access_token(user_id: int, role: SystemRole) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return jwt.encode(
        {"sub": str(user_id), "role": role, "exp": expire, "type": "access"},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def create_refresh_token(user_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.refresh_token_expire_days)
    return jwt.encode(
        {"sub": str(user_id), "exp": expire, "type": "refresh", "jti": secrets.token_hex(16)},
        settings.secret_key,
        algorithm=ALGORITHM,
    )


def decode_access_token(token: str) -> dict:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "access":
            raise AuthError("Invalid token type")
        return payload
    except JWTError:
        raise AuthError("Invalid or expired token")


def decode_refresh_token(token: str) -> int:
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[ALGORITHM])
        if payload.get("type") != "refresh":
            raise AuthError("Invalid token type")
        return int(payload["sub"])
    except JWTError:
        raise AuthError("Invalid or expired token")
