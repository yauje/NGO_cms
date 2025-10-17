#app/schemas/page_block.py
from datetime import datetime
from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, Dict


class PageBlockBase(BaseModel):
    page_id: int
    type: str = Field(..., description="Block type, e.g. text, image, hero, gallery, custom")
    content: Dict = Field(..., description="Flexible JSON structure storing block data")
    order: int = Field(0, description="Position of the block on the page")


class PageBlockCreate(PageBlockBase):
    created_by_id: int = Field(..., description="ID of the user who created the block")


class PageBlockUpdate(BaseModel):
    type: Optional[str] = None
    content: Optional[Dict] = None
    order: Optional[int] = None


class PageBlockRead(PageBlockBase):
    id: int
    created_by_id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
