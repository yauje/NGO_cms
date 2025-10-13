# app/crud/settings.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.site_setting import SiteSetting
from app.schemas.site_setting import SiteSettingCreate, SiteSettingUpdate
from app.core.audit import record_audit_log


class CRUDSiteSetting:
    # -------------------------
    # GET BY KEY
    # -------------------------
    async def get(self, db: AsyncSession, key: str) -> Optional[SiteSetting]:
        result = await db.execute(select(SiteSetting).where(SiteSetting.key == key))
        return result.scalars().first()

    # -------------------------
    # GET ALL SETTINGS
    # -------------------------
    async def get_all(self, db: AsyncSession) -> List[SiteSetting]:
        result = await db.execute(select(SiteSetting))
        return result.scalars().all()

    # -------------------------
    # CREATE SETTING
    # -------------------------
    async def create(
        self, db: AsyncSession, obj_in: SiteSettingCreate, performed_by: int | None = None
    ) -> SiteSetting:
        db_obj = SiteSetting(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="create",
                resource_type="site_setting",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # UPDATE SETTING
    # -------------------------
    async def update(
        self, db: AsyncSession, db_obj: SiteSetting, obj_in: SiteSettingUpdate, performed_by: int | None = None
    ) -> SiteSetting:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)

        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="update",
                resource_type="site_setting",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # DELETE SETTING
    # -------------------------
    async def remove(
        self, db: AsyncSession, key: str, performed_by: int | None = None
    ) -> Optional[SiteSetting]:
        obj = await self.get(db, key)
        if not obj:
            return None

        await db.delete(obj)
        await db.commit()

        # Audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="delete",
                resource_type="site_setting",
                resource_id=obj.id,
            )

        return obj


# Singleton instance
crud_site_setting = CRUDSiteSetting()
