#app/schemas/site_setting.py
from typing import Optional, Any
from datetime import datetime
from pydantic import BaseModel, Field

# NOTE: 'value' is handled as a str in Pydantic because the database stores it as TEXT, 
# even if the content is meant to be JSON or another format.

# --- SiteSettingBase: Shared fields for Creation and Update ---
class SiteSettingBase(BaseModel):
    """Base schema for SiteSetting data, containing only the value field."""
    
    value: str = Field(..., description="The configuration value associated with the key (stored as text).")

    class Config:
        # Essential for reading data directly from the SQLAlchemy ORM model
        from_attributes = True


# --- SiteSettingCreate: Used for creating a new setting ---
class SiteSettingCreate(SiteSettingBase):
    """Schema for creating a new SiteSetting instance, requires both key and value."""
    
    key: str = Field(..., max_length=100, description="The unique name/key for the configuration setting.")


# --- SiteSettingUpdate: Used for modifying an existing setting ---
class SiteSettingUpdate(BaseModel):
    """Schema for updating an existing SiteSetting instance (only value is needed in the payload)."""
    
    # Only the value is provided for an update payload; the key/id is passed in the URL.
    value: str = Field(..., description="The new configuration value.")
    
    class Config:
        from_attributes = True


# --- SiteSettingRead: Full representation including IDs and timestamp ---
class SiteSettingRead(SiteSettingBase):
    """Schema for reading/returning a SiteSetting instance, including database metadata."""
    
    id: int                           # Primary Key
    key: str = Field(..., max_length=100)
    updated_at: datetime
    
    class Config:
        from_attributes = True