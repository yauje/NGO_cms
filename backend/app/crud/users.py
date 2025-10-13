# app/crud/users.py
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.core.audit import record_audit_log


class CRUDUser:
    # -------------------------
    # GET BY ID
    # -------------------------
    async def get(self, db: AsyncSession, id: int) -> Optional[User]:
        result = await db.execute(select(User).where(User.id == id))
        return result.scalars().first()

    # -------------------------
    # GET BY EMAIL
    # -------------------------
    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        result = await db.execute(select(User).where(User.email == email))
        return result.scalars().first()

    # -------------------------
    # LIST MULTIPLE USERS
    # -------------------------
    async def get_multi(self, db: AsyncSession, skip: int = 0, limit: int = 100) -> List[User]:
        result = await db.execute(select(User).offset(skip).limit(limit))
        return result.scalars().all()

    # -------------------------
    # CREATE USER
    # -------------------------
    async def create(self, db: AsyncSession, obj_in: UserCreate, performed_by: int | None = None) -> User:
        db_obj = User(**obj_in.model_dump())
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Record audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="create",
                resource_type="user",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # UPDATE USER
    # -------------------------
    async def update(
        self, db: AsyncSession, db_obj: User, obj_in: UserUpdate, performed_by: int | None = None
    ) -> User:
        update_data = obj_in.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(db_obj, field, value)
        db.add(db_obj)
        await db.commit()
        await db.refresh(db_obj)

        # Record audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="update",
                resource_type="user",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # DELETE USER
    # -------------------------
    async def remove(self, db: AsyncSession, id: int, performed_by: int | None = None) -> Optional[User]:
        obj = await self.get(db, id)
        if not obj:
            return None
        await db.delete(obj)
        await db.commit()

        # Record audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user_id=performed_by,
                action="delete",
                resource_type="user",
                resource_id=id,
            )

        return obj


# Singleton CRUD instance
crud_user = CRUDUser()
