from sqlalchemy.orm import DeclarativeBase


class Base(DeclarativeBase):
    pass


try:
    from app.modules.accounts import models as accounts_models  # noqa: F401
    from app.modules.audit import models as audit_models  # noqa: F401
    from app.modules.communication import models as communication_models  # noqa: F401
    from app.modules.contracts import models as contracts_models  # noqa: F401
    from app.modules.delivery import models as delivery_models  # noqa: F401
    from app.modules.marketplace import models as marketplace_models  # noqa: F401
    from app.modules.moderation import models as moderation_models  # noqa: F401
    from app.modules.payments import models as payments_models  # noqa: F401
except ImportError:
    pass
