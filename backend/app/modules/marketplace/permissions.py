from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.modules.accounts.dependencies import get_current_user
from app.modules.accounts.models import User
from app.modules.marketplace import repository as repo
from app.core.exceptions import NotFoundError, PermissionDeniedError


def get_own_task(task_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = repo.get_task(db, task_id)
    if not task:
        raise NotFoundError("Task not found")
    if task.creator_id != current_user.id:
        raise PermissionDeniedError("Only task owner can perform this action")
    return task
