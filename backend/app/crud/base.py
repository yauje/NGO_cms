# app/crud/users.py
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.user import User
from app.schemas.user import UserCreate, UserUpdate
from app.crud.base import CRUDBase
from app.core.audit import record_audit_log


class CRUDUser(CRUDBase[User, UserCreate, UserUpdate]):
    # -------------------------
    # CREATE USER WITH AUDIT
    # -------------------------
    async def create(self, db: AsyncSession, obj_in: UserCreate, performed_by: Optional[int] = None) -> User:
        db_obj = await super().create(db, obj_in)

        # Record audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user=User(id=performed_by),
                action="create",
                resource_type="user",
                resource_id=db_obj.id,
            )

        return db_obj

    # -------------------------
    # UPDATE USER WITH AUDIT
    # -------------------------
    async def update(
        self, db: AsyncSession, db_obj: Optional[User] = None, *, id: Optional[int] = None, obj_in: UserUpdate, performed_by: Optional[int] = None
    ) -> User:
        updated_obj = await super().update(db, db_obj=db_obj, id=id, obj_in=obj_in)

        # Record audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user=User(id=performed_by),
                action="update",
                resource_type="user",
                resource_id=updated_obj.id,
            )

        return updated_obj

    # -------------------------
    # DELETE USER WITH AUDIT
    # -------------------------
    async def delete(self, db: AsyncSession, *, id: int, performed_by: Optional[int] = None) -> None:
        await super().delete(db, id=id)

        # Record audit log
        if performed_by:
            await record_audit_log(
                db=db,
                user=User(id=performed_by),
                action="delete",
                resource_type="user",
                resource_id=id,
            )


# Singleton CRUD instance
crud_user = CRUDUser(User)
