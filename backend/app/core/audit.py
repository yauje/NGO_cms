# app/core/audit.py

from datetime import datetime
from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.db.models.user import User
from app.crud.audit_logs import crud_audit_log
from app.schemas.audit_log import AuditLogCreate
from app.core.auth_deps import get_current_user  # <- use core, not routes


async def record_audit_log(
    action: str,
    resource_type: str,
    resource_id: int,
    db: AsyncSession,
    user: User | None = None,
):
    """
    Record an audit log entry.

    Args:
        action (str): The performed action ("create", "update", "delete", etc.)
        resource_type (str): Type of the resource (e.g. "user", "page", "setting").
        resource_id (int): ID of the affected resource.
        db (AsyncSession): Database session (FastAPI dependency).
        user (User | None): The acting user (optional). If not provided, raise error.
    """

    if not user:
        raise ValueError("User must be provided when recording audit logs manually.")

    audit_entry = AuditLogCreate(
        user_id=user.id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
    )

    await crud_audit_log.create(db, obj_in=audit_entry)


# ────────────────────────────────
# Dependency wrapper (optional)
# ────────────────────────────────
async def audit_logger(
    action: str,
    resource_type: str,
    resource_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Dependency wrapper for inline usage inside routes.

    Example:
        @router.post("/", dependencies=[Depends(audit_logger("create", "page", 1))])
    """
    await record_audit_log(
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        db=db,
        user=current_user,
    )
