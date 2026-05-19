import hashlib
from datetime import datetime

from sqlalchemy.orm import Session

from app.modules.accounts.models import RefreshToken, User


def get_user_by_email(db: Session, email: str) -> User | None:
    return db.query(User).filter(User.email == email).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    return db.get(User, user_id)


def create_user(db: Session, email: str, hashed_password: str) -> User:
    user = User(email=email, hashed_password=hashed_password)
    db.add(user)
    db.flush()
    return user


def save_refresh_token(db: Session, user_id: int, raw_token: str, expires_at: datetime) -> None:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    db.add(RefreshToken(user_id=user_id, token_hash=token_hash, expires_at=expires_at))


def get_refresh_token(db: Session, raw_token: str) -> RefreshToken | None:
    token_hash = hashlib.sha256(raw_token.encode()).hexdigest()
    return db.query(RefreshToken).filter(
        RefreshToken.token_hash == token_hash,
        RefreshToken.revoked.is_(False),
    ).first()


def revoke_refresh_token(db: Session, raw_token: str) -> None:
    token = get_refresh_token(db, raw_token)
    if token:
        token.revoked = True
