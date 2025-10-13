from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import AuditLogRead
from app.crud import crud_audit_log
from app.db.session import get_db
from app.core.permissions import require_permission

router = APIRouter(prefix="/audit-logs", tags=["Audit Logs"])


# -------------------------
# LIST ALL AUDIT LOGS
# -------------------------
@router.get(
    "/",
    response_model=list[AuditLogRead],
    dependencies=[Depends(require_permission(["analytics.view", "audit.view"]))],
)
async def list_audit_logs(db: AsyncSession = Depends(get_db)):
    """Return a list of all audit log entries."""
    logs = await crud_audit_log.get_all(db)
    if not logs:
        # Optional: You can return 204 if you prefer no-content for empty result
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No audit logs found")
    return logs
