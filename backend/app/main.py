from fastapi import FastAPI

from app.core.config import get_settings
from app.core.exceptions import AppError, app_error_handler
from app.core.logging import configure_logging
from app.core.middleware import configure_middleware
from app.modules.accounts.router import router as accounts_router
from app.modules.communication.router import router as communication_router
from app.modules.contracts.router import router as contracts_router
from app.modules.delivery.router import router as delivery_router
from app.modules.marketplace.router import router as marketplace_router
from app.modules.moderation.router import router as moderation_router
from app.modules.payments.router import router as payments_router

settings = get_settings()
configure_logging()

app = FastAPI(
    title=settings.app_name,
    description="AES-GCM + RSA-OAEP encrypted freelance platform",
    version=settings.app_version,
)

configure_middleware(app)
app.add_exception_handler(AppError, app_error_handler)

app.include_router(accounts_router)
app.include_router(marketplace_router)
app.include_router(contracts_router)
app.include_router(communication_router)
app.include_router(delivery_router)
app.include_router(payments_router)
app.include_router(moderation_router)


@app.get("/health")
def health():
    return {"status": "ok"}
