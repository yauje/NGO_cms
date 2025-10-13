from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class PageRevisionBase(BaseModel):
    content: str


class PageRevisionCreate(PageRevisionBase):
    page_id: int
    created_by_id: int


class PageRevisionRead(PageRevisionBase):
    id: int
    page_id: int
    created_by_id: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
