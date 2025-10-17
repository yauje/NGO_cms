#app/schemas/page.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict
from typing import Optional


class PageBase(BaseModel):
    slug: str
    title: str
    is_published: bool = False


class PageCreate(PageBase):
    pass


class PageUpdate(BaseModel):
    title: Optional[str] = None
    slug: Optional[str] = None
    is_published: Optional[bool] = None


class PageRead(PageBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
