from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import UserCreate, UserRead, UserUpdate
from app.crud import crud_user
from app.db.session import get_db
from app.core.permissions import require_permission
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/users", tags=["Users"])

# -------------------------
# CREATE USER
# -------------------------
@router.post(
    "/", 
    response_model=UserRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("users.create"))]
)
async def create_user(
    user_in: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await crud_user.create(db, obj_in=user_in, performed_by=current_user.id)


# -------------------------
# LIST USERS
# -------------------------
@router.get(
    "/", 
    response_model=list[UserRead],
    dependencies=[Depends(require_permission("users.view"))]
)
async def list_users(db: AsyncSession = Depends(get_db)):
    return await crud_user.get_multi(db)


# -------------------------
# GET USER BY ID
# -------------------------
@router.get(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permission("users.view"))]
)
async def get_user(user_id: int, db: AsyncSession = Depends(get_db)):
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


# -------------------------
# UPDATE USER
# -------------------------
@router.put(
    "/{user_id}",
    response_model=UserRead,
    dependencies=[Depends(require_permission("users.edit"))]
)
async def update_user(
    user_id: int,
    user_in: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    return await crud_user.update(db, db_obj=user, obj_in=user_in, performed_by=current_user.id)


# -------------------------
# DELETE USER
# -------------------------
@router.delete(
    "/{user_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("users.delete"))],
)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    user = await crud_user.get(db, id=user_id)
    if not user:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    
    await crud_user.remove(db, id=user_id, performed_by=current_user.id)
