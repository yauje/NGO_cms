from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class MediaBase(BaseModel):
    filename: str
    filepath: str
    mimetype: str


class MediaCreate(MediaBase):
    uploaded_by_id: int


class MediaRead(MediaBase):
    id: int
    uploaded_by_id: int
    uploaded_at: datetime

    model_config = ConfigDict(from_attributes=True)
