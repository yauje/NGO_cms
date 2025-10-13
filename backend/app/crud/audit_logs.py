from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional

from app.db.models.audit_log import AuditLog
from app.schemas import AuditLogCreate, AuditLogRead


class CRUDAuditLog:
    async def create(self, db: AsyncSession, obj_in: AuditLogCreate) -> AuditLog:
        """Create a new audit log entry."""
        audit_log = AuditLog(**obj_in.model_dump())
        db.add(audit_log)
        await db.commit()
        await db.refresh(audit_log)
        return audit_log

    async def get_all(self, db: AsyncSession) -> List[AuditLog]:
        """Retrieve all audit logs."""
        result = await db.execute(select(AuditLog).order_by(AuditLog.timestamp.desc()))
        return result.scalars().all()

    async def get_by_user(self, db: AsyncSession, user_id: int) -> List[AuditLog]:
        """Retrieve all logs performed by a specific user."""
        result = await db.execute(
            select(AuditLog)
            .where(AuditLog.user_id == user_id)
            .order_by(AuditLog.timestamp.desc())
        )
        return result.scalars().all()

    async def get_by_resource(
        self, db: AsyncSession, resource_type: str, resource_id: int
    ) -> List[AuditLog]:
        """Retrieve all logs related to a specific resource."""
        result = await db.execute(
            select(AuditLog)
            .where(
                AuditLog.resource_type == resource_type,
                AuditLog.resource_id == resource_id,
            )
            .order_by(AuditLog.timestamp.desc())
        )
        return result.scalars().all()

    async def delete(self, db: AsyncSession, log_id: int) -> Optional[AuditLog]:
        """Delete an audit log (admin-only action)."""
        result = await db.execute(select(AuditLog).where(AuditLog.id == log_id))
        audit_log = result.scalar_one_or_none()
        if audit_log:
            await db.delete(audit_log)
            await db.commit()
        return audit_log


# Instantiate the CRUD object
crud_audit_log = CRUDAuditLog()
