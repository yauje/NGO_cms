from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SiteSettingCreate, SiteSettingRead, SiteSettingUpdate
from app.crud import crud_site_setting
from app.db.session import get_db
from app.core.permissions import require_permission
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/site-settings", tags=["Site Settings"])

# -------------------------
# LIST ALL SETTINGS
# -------------------------
@router.get(
    "/",
    response_model=list[SiteSettingRead],
    dependencies=[Depends(require_permission("site.settings.view"))],
)
async def list_settings(db: AsyncSession = Depends(get_db)):
    return await crud_site_setting.get_all(db)


# -------------------------
# GET ONE SETTING BY KEY
# -------------------------
@router.get(
    "/{key}",
    response_model=SiteSettingRead,
    dependencies=[Depends(require_permission("site.settings.view"))],
)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    setting = await crud_site_setting.get_by_key(db, key=key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return setting


# -------------------------
# CREATE NEW SETTING
# -------------------------
@router.post(
    "/",
    response_model=SiteSettingRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("site.settings.edit"))],
)
async def create_setting(
    setting_in: SiteSettingCreate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    return await crud_site_setting.create(db, obj_in=setting_in, performed_by=current_user.id)


# -------------------------
# UPDATE EXISTING SETTING BY KEY
# -------------------------
@router.put(
    "/{key}",
    response_model=SiteSettingRead,
    dependencies=[Depends(require_permission("site.settings.edit"))],
)
async def update_setting(
    key: str,
    setting_in: SiteSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    setting = await crud_site_setting.get_by_key(db, key=key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
        
    return await crud_site_setting.update(db, db_obj=setting, obj_in=setting_in, performed_by=current_user.id)


# -------------------------
# DELETE SETTING BY KEY
# -------------------------
@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("site.settings.edit"))],
)
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    setting = await crud_site_setting.get_by_key(db, key=key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
        
    await crud_site_setting.remove(db, key=key, performed_by=current_user.id)
