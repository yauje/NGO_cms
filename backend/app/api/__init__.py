from fastapi import APIRouter
from app.api.routes import users, pages, page_blocks, media, settings, audit_logs, auth

api_router = APIRouter(prefix="/api")

# Include sub-routers
api_router.include_router(users.router, prefix="/users", tags=["Users"])
api_router.include_router(pages.router, prefix="/pages", tags=["Pages"])
api_router.include_router(page_blocks.router, prefix="/page-blocks", tags=["Page Blocks"])
api_router.include_router(media.router, prefix="/media", tags=["Media"])
api_router.include_router(settings.router, prefix="/settings", tags=["Settings"])
api_router.include_router(audit_logs.router, prefix="/audit-logs", tags=["Audit Logs"])
api_router.include_router(auth.router, prefix="/auth", tags=["Auth"])
        