# app/crud/media.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.media import Media
from app.schemas.media import MediaCreate
from app.core.audit import record_audit_log


class CRUDMedia:
    # -------------------------
    # GET BY ID
    # -------------------------
    async def get(self, db: AsyncSession, id: int) -> Optional[Media]:
        result = await db.execute(select(Media).where(Media.id == id))
        return result.scalars().first()

    # -------------------------
    # GET MULTIPLE
    # -------------------------
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Media]:
        result = await db.execute(
            select(Media).order_by(Media.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # -------------------------
    # CREATE
    # -------------------------
    async def create(self, db: AsyncSession, obj_in: MediaCreate, performed_by: int | None = None) -> Media:
        db_obj = Media(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="create",
                resource_type="media",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # DELETE
    # -------------------------
    async def remove(self, db: AsyncSession, id: int, performed_by: int | None = None) -> Optional[Media]:
        obj = await self.get(db, id)
        if not obj:
            return None

        await db.delete(obj)
        await db.commit()

        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="delete",
                resource_type="media",
                resource_id=id,
            )

        return obj


# Singleton CRUD instance
crud_media = CRUDMedia()
