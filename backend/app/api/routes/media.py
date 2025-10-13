from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas import MediaRead
from app.crud import crud_media
from app.db.session import get_db
from app.core.permissions import require_permission
from app.core.auth_deps import get_current_user
from app.core.audit import record_audit_log
import shutil
from datetime import datetime
import os

router = APIRouter(prefix="/media", tags=["Media"])

MEDIA_DIR = "app/static/uploads"
os.makedirs(MEDIA_DIR, exist_ok=True)


# -------------------------
# UPLOAD MEDIA FILE
# -------------------------
@router.post(
    "/",
    response_model=MediaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("media.upload"))],
)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Upload a media file and save its metadata."""
    file_path = os.path.join(MEDIA_DIR, file.filename)

    # Save file to disk
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Prepare DB record
    data = {
        "filename": file.filename,
        "url": f"/static/uploads/{file.filename}",
        "mimetype": file.content_type,
        "filesize_bytes": os.path.getsize(file_path),
        "uploaded_at": datetime.utcnow(),
    }

    media_obj = await crud_media.create(db, obj_in=data)

    # Record audit log
    await record_audit_log(
        db=db,
        user=current_user,
        action="upload",
        resource_type="media",
        resource_id=media_obj.id,
    )

    return media_obj


# -------------------------
# LIST ALL MEDIA FILES
# -------------------------
@router.get(
    "/",
    response_model=list[MediaRead],
    dependencies=[Depends(require_permission("media.view"))],
)
async def list_media(db: AsyncSession = Depends(get_db)):
    """List all uploaded media files."""
    return await crud_media.get_all(db)


# -------------------------
# DELETE MEDIA FILE
# -------------------------
@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("media.delete"))],
)
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user = Depends(get_current_user),
):
    """Delete a media file both from DB and disk."""
    media = await crud_media.get(db, id=media_id)
    if not media:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Media not found")

    # Remove file from disk if it exists
    file_path = os.path.join(MEDIA_DIR, media.filename)
    if os.path.exists(file_path):
        os.remove(file_path)

    # Remove metadata from DB
    await crud_media.delete(db, id=media_id)

    # Record audit log
    await record_audit_log(
        db=db,
        user=current_user,
        action="delete",
        resource_type="media",
        resource_id=media_id,
    )
    return None
