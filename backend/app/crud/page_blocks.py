# app/crud/page_blocks.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.page_block import PageBlock
from app.schemas.page_block import PageBlockCreate, PageBlockUpdate
from app.core.audit import record_audit_log


class CRUDPageBlock:
    # -------------------------
    # GET BY ID
    # -------------------------
    async def get(self, db: AsyncSession, id: int) -> Optional[PageBlock]:
        result = await db.execute(select(PageBlock).where(PageBlock.id == id))
        return result.scalars().first()

    # -------------------------
    # GET BY PAGE ID
    # -------------------------
    async def get_by_page(self, db: AsyncSession, page_id: int) -> List[PageBlock]:
        result = await db.execute(
            select(PageBlock)
            .where(PageBlock.page_id == page_id)
            .order_by(PageBlock.order.asc())
        )
        return result.scalars().all()

    # -------------------------
    # GET MULTIPLE
    # -------------------------
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[PageBlock]:
        result = await db.execute(
            select(PageBlock).order_by(PageBlock.created_at.desc()).offset(skip).limit(limit)
        )
        return result.scalars().all()

    # -------------------------
    # CREATE
    # -------------------------
    async def create(self, db: AsyncSession, obj_in: PageBlockCreate, performed_by: int | None = None) -> PageBlock:
        db_obj = PageBlock(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="create",
                resource_type="page_block",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # UPDATE
    # -------------------------
    async def update(self, db: AsyncSession, db_obj: PageBlock, obj_in: PageBlockUpdate, performed_by: int | None = None) -> PageBlock:
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
                resource_type="page_block",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # DELETE
    # -------------------------
    async def remove(self, db: AsyncSession, id: int, performed_by: int | None = None) -> Optional[PageBlock]:
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
                resource_type="page_block",
                resource_id=id,
            )

        return obj


# Singleton instance
crud_page_block = CRUDPageBlock()
