from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import PageBlockCreate, PageBlockRead, PageBlockUpdate
from app.crud import crud_page_block
from app.db.session import get_db
from app.core.permissions import require_permission
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/page-blocks", tags=["Page Blocks"])


# -------------------------
# CREATE BLOCK
# -------------------------
@router.post(
    "/",
    response_model=PageBlockRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("content.create"))]
)
async def create_page_block(
    block_in: PageBlockCreate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    return await crud_page_block.create(db, obj_in=block_in, performed_by=current_user.id)


# -------------------------
# LIST BLOCKS (optionally filtered by page_id)
# -------------------------
@router.get(
    "/",
    response_model=list[PageBlockRead],
    dependencies=[Depends(require_permission("content.view"))]
)
async def list_page_blocks(page_id: int | None = None, db: AsyncSession = Depends(get_db)):
    if page_id:
        return await crud_page_block.get_by_page(db, page_id=page_id)
    return await crud_page_block.get_all(db)


# -------------------------
# GET BLOCK BY ID
# -------------------------
@router.get(
    "/{block_id}",
    response_model=PageBlockRead,
    dependencies=[Depends(require_permission("content.view"))]
)
async def get_page_block(block_id: int, db: AsyncSession = Depends(get_db)):
    block = await crud_page_block.get(db, id=block_id)
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    return block


# -------------------------
# UPDATE BLOCK
# -------------------------
@router.put(
    "/{block_id}",
    response_model=PageBlockRead,
    dependencies=[Depends(require_permission("content.edit"))]
)
async def update_page_block(
    block_id: int,
    block_in: PageBlockUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    block = await crud_page_block.get(db, id=block_id)
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    return await crud_page_block.update(db, db_obj=block, obj_in=block_in, performed_by=current_user.id)


# -------------------------
# DELETE BLOCK
# -------------------------
@router.delete(
    "/{block_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("content.delete"))]
)
async def delete_page_block(
    block_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    block = await crud_page_block.get(db, id=block_id)
    if not block:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Block not found")
    await crud_page_block.remove(db, id=block_id, performed_by=current_user.id)
