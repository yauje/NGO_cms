# app/api/routes/settings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.schemas import SiteSettingCreate, SiteSettingRead, SiteSettingUpdate
from app.crud import crud_site_setting
from app.db.session import get_db
from app.core.permissions import require_permission
from app.core.auth_deps import get_current_user

router = APIRouter(prefix="/site-settings", tags=["Site Settings"])


# -------------------------
# LIST ALL SETTINGS (Admin)
# -------------------------
@router.get(
    "/",
    response_model=list[SiteSettingRead],
    dependencies=[Depends(require_permission("site.settings.view"))],
)
async def list_settings(db: AsyncSession = Depends(get_db)):
    """Return all site configuration settings (admin only)."""
    return await crud_site_setting.get_all(db)


# -------------------------
# GET ONE SETTING BY KEY (Admin)
# -------------------------
@router.get(
    "/{key}",
    response_model=SiteSettingRead,
    dependencies=[Depends(require_permission("site.settings.view"))],
)
async def get_setting(key: str, db: AsyncSession = Depends(get_db)):
    """Retrieve a specific setting by its unique key."""
    setting = await crud_site_setting.get(db, key=key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return setting


# -------------------------
# CREATE NEW SETTING (Admin)
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
    current_user=Depends(get_current_user),
):
    """Create a new configuration setting."""
    existing = await crud_site_setting.get(db, key=setting_in.key)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Setting with key '{setting_in.key}' already exists",
        )
    return await crud_site_setting.create(db, obj_in=setting_in, performed_by=current_user.id)


# -------------------------
# UPDATE EXISTING SETTING BY KEY (Admin)
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
    current_user=Depends(get_current_user),
):
    """Update an existing setting by its key."""
    setting = await crud_site_setting.get(db, key=key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    return await crud_site_setting.update(
        db, db_obj=setting, obj_in=setting_in, performed_by=current_user.id
    )


# -------------------------
# DELETE SETTING BY KEY (Admin)
# -------------------------
@router.delete(
    "/{key}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("site.settings.edit"))],
)
async def delete_setting(
    key: str,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Delete a setting by its key."""
    setting = await crud_site_setting.get(db, key=key)
    if not setting:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Setting not found")
    await crud_site_setting.remove(db, key=key, performed_by=current_user.id)


# -------------------------
# PUBLIC SETTINGS (No Auth)
# -------------------------
@router.get(
    "/public",
    response_model=dict,
    status_code=status.HTTP_200_OK,
)
async def get_public_settings(db: AsyncSession = Depends(get_db)):
    """Publicly accessible endpoint for the frontend site."""
    settings = await crud_site_setting.get_all(db)
    return {s.key: s.value for s in settings}


# -------------------------
# UPSERT SETTING BY KEY (Admin)
# -------------------------
@router.post(
    "/upsert/{key}",
    response_model=SiteSettingRead,
    dependencies=[Depends(require_permission("site.settings.edit"))],
)
async def upsert_setting(
    key: str,
    setting_in: SiteSettingUpdate,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """
    Create or update a setting by key.
    If the key exists, update the value; otherwise, create a new setting.
    """
    existing = await crud_site_setting.get(db, key=key)
    if existing:
        return await crud_site_setting.update(
            db, db_obj=existing, obj_in=setting_in, performed_by=current_user.id
        )

    # Key does not exist, create new
    new_setting = SiteSettingCreate(key=key, value=setting_in.value)
    return await crud_site_setting.create(db, obj_in=new_setting, performed_by=current_user.id)
