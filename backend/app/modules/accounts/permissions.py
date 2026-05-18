from fastapi import Depends

from app.common.enums import SystemRole
from app.core.exceptions import PermissionDeniedError
from app.modules.accounts.dependencies import get_current_user
from app.modules.accounts.models import User


def require_role(*roles: SystemRole):
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if current_user.system_role not in roles:
            raise PermissionDeniedError("Insufficient permissions")
        return current_user
    return dependency


require_moderator = require_role(SystemRole.MODERATOR, SystemRole.ADMIN)
require_admin = require_role(SystemRole.ADMIN)
