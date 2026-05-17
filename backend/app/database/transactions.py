from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.orm import Session


@contextmanager
def atomic(db: Session) -> Iterator[Session]:
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
