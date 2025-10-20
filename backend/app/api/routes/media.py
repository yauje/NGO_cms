from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, status
from sqlalchemy.ext.asyncio import AsyncSession
from app.schemas.media import MediaCreate, MediaRead
from app.crud import crud_media
from app.db.session import get_db
from app.core.permissions import require_permission
from app.core.auth_deps import get_current_user
from app.core.audit import record_audit_log
import shutil
from datetime import datetime
import os
import uuid

router = APIRouter(prefix="/media", tags=["Media"])

# ----------------------------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------------------------

# Absolute path resolution (prevents working-directory bugs)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
MEDIA_DIR = os.path.join(BASE_DIR, "static", "uploads")
os.makedirs(MEDIA_DIR, exist_ok=True)

# Accepted MIME types for uploads
ALLOWED_MIME_PREFIXES = (
    "image/",            # e.g. image/png, image/jpeg
    "video/",            # e.g. video/mp4
    "audio/",            # e.g. audio/mpeg, audio/wav
    "application/pdf",   # e.g. PDFs
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    "application/vnd.ms-excel",
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    "text/plain",        # e.g. .txt files
)

# Max upload size (bytes)
MAX_FILE_SIZE = 20 * 1024 * 1024  # 20 MB


# ----------------------------------------------------------------------
# UPLOAD MEDIA FILE
# ----------------------------------------------------------------------
@router.post(
    "/",
    response_model=MediaRead,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_permission("media.upload"))],
)
async def upload_file(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Upload a media file and save its metadata."""

    # --- Validate file type ---
    if not file.content_type or not file.content_type.startswith(ALLOWED_MIME_PREFIXES):
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {file.content_type}. Allowed types: images, videos, audio, PDFs, docs, text, spreadsheets.",
        )

    # --- Prepare unique filename to prevent collisions ---
    unique_name = f"{uuid.uuid4().hex[:12]}_{file.filename.lower()}"
    file_path = os.path.join(MEDIA_DIR, unique_name)

    # --- Save file to disk ---
    try:
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
    finally:
        file.file.close()

    # --- Check file size after save ---
    file_size = os.path.getsize(file_path)
    if file_size > MAX_FILE_SIZE:
        os.remove(file_path)
        raise HTTPException(
            status_code=400,
            detail=f"File too large ({file_size / 1024 / 1024:.2f} MB). Max allowed is {MAX_FILE_SIZE / 1024 / 1024:.0f} MB.",
        )

    # --- Prepare DB record ---
    media_in = MediaCreate(
        filename=unique_name,
        url=f"/static/uploads/{unique_name}",
        mimetype=file.content_type,
        filesize_bytes=file_size,
        uploaded_by_user_id=current_user.id,
    )

    # --- Store in DB ---
    media_obj = await crud_media.create(db, obj_in=media_in, performed_by=current_user.id)

    # --- Record audit log ---
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="upload",
        resource_type="media",
        resource_id=media_obj.id,
    )

    return media_obj


# ----------------------------------------------------------------------
# LIST MEDIA
# ----------------------------------------------------------------------
@router.get(
    "/",
    response_model=list[MediaRead],
    dependencies=[Depends(require_permission("media.view"))],
)
async def list_media(db: AsyncSession = Depends(get_db)):
    """List all uploaded media files."""
    return await crud_media.get_multi(db)


# ----------------------------------------------------------------------
# DELETE MEDIA FILE
# ----------------------------------------------------------------------
@router.delete(
    "/{media_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_permission("media.delete"))],
)
async def delete_media(
    media_id: int,
    db: AsyncSession = Depends(get_db),
    current_user=Depends(get_current_user),
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
    await crud_media.delete(db, id=media_id, performed_by=current_user.id)

    # Record audit log
    await record_audit_log(
        db=db,
        user_id=current_user.id,
        action="delete",
        resource_type="media",
        resource_id=media_id,
    )

    return None
