from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import PageCreate, PageRead, PageUpdate
from app.crud import crud_page
from app.db.session import get_db
from app.core.permissions import require_permission
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/pages", tags=["Pages"])

# -------------------------
# CREATE PAGE
# -------------------------
@router.post(
    "/",
    response_model=PageRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("content.create"))]
)
async def create_page(
    page_in: PageCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await crud_page.create(db, obj_in=page_in, performed_by=current_user.id)


# -------------------------
# LIST PAGES
# -------------------------
@router.get(
    "/",
    response_model=list[PageRead],
    dependencies=[Depends(require_permission("content.view"))]
)
async def list_pages(db: AsyncSession = Depends(get_db)):
    return await crud_page.get_all(db)


# -------------------------
# GET PAGE BY ID
# -------------------------
@router.get(
    "/{page_id}",
    response_model=PageRead,
    dependencies=[Depends(require_permission("content.view"))]
)
async def get_page(page_id: int, db: AsyncSession = Depends(get_db)):
    page = await crud_page.get(db, id=page_id)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return page


# -------------------------
# UPDATE PAGE
# -------------------------
@router.put(
    "/{page_id}",
    response_model=PageRead,
    dependencies=[Depends(require_permission("content.edit"))]
)
async def update_page(
    page_id: int,
    page_in: PageUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    page = await crud_page.get(db, id=page_id)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    return await crud_page.update(db, db_obj=page, obj_in=page_in, performed_by=current_user.id)


# -------------------------
# DELETE PAGE
# -------------------------
@router.delete(
    "/{page_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("content.delete"))]
)
async def delete_page(
    page_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    page = await crud_page.get(db, id=page_id)
    if not page:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Page not found")
    await crud_page.remove(db, id=page_id, performed_by=current_user.id)
