# app/crud/pages.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.page import Page
from app.schemas.page import PageCreate, PageUpdate
from app.core.audit import record_audit_log


class CRUDPage:
    # -------------------------
    # GET BY ID
    # -------------------------
    async def get(self, db: AsyncSession, id: int) -> Optional[Page]:
        result = await db.execute(select(Page).where(Page.id == id))
        return result.scalars().first()

    # -------------------------
    # GET BY SLUG
    # -------------------------
    async def get_by_slug(self, db: AsyncSession, slug: str) -> Optional[Page]:
        result = await db.execute(select(Page).where(Page.slug == slug))
        return result.scalars().first()

    # -------------------------
    # GET MULTIPLE
    # -------------------------
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[Page]:
        result = await db.execute(
            select(Page).order_by(Page.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # -------------------------
    # CREATE
    # -------------------------
    async def create(self, db: AsyncSession, obj_in: PageCreate, performed_by: int | None = None) -> Page:
        db_obj = Page(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="create",
                resource_type="page",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # UPDATE
    # -------------------------
    async def update(self, db: AsyncSession, db_obj: Page, obj_in: PageUpdate, performed_by: int | None = None) -> Page:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="update",
                resource_type="page",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # DELETE
    # -------------------------
    async def remove(self, db: AsyncSession, id: int, performed_by: int | None = None) -> Optional[Page]:
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
                resource_type="page",
                resource_id=id,
            )

        return obj


# Singleton CRUD instance
crud_page = CRUDPage()
