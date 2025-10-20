from datetime import datetime
from pydantic import BaseModel, ConfigDict


class MediaBase(BaseModel):
    filename: str
    url: str                    # replaced `filepath` with `url`
    mimetype: str
    filesize_bytes: int         # added this to match DB model


class MediaCreate(MediaBase):
    uploaded_by_user_id: int    # corrected key name to match model field


class MediaRead(MediaBase):
    id: int
    uploaded_by_user_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
