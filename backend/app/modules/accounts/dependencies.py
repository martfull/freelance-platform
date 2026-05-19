from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.accounts import repository as repo
from app.modules.accounts.jwt import AuthError, decode_access_token
from app.modules.accounts.models import User

_bearer = HTTPBearer()


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer),
    db: Session = Depends(get_db),
) -> User:
    payload = decode_access_token(credentials.credentials)
    user = repo.get_user_by_id(db, int(payload["sub"]))
    if not user or not user.is_active:
        raise AuthError("User not found or inactive")
    return user
