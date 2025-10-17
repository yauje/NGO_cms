#app/schemas/__init__.py

from app.schemas.user import (
    UserBase,
    UserCreate,
    UserUpdate,
    UserRead,
)

from app.schemas.page import (
    PageBase,
    PageCreate,
    PageUpdate,
    PageRead,
)

from app.schemas.page_block import (
    PageBlockBase,
    PageBlockCreate,
    PageBlockUpdate,
    PageBlockRead,
)

from app.schemas.media import (
    MediaBase,
    MediaCreate,
    MediaRead,
)

from app.schemas.site_setting import (
    SiteSettingBase,
    SiteSettingCreate,
    SiteSettingUpdate,
    SiteSettingRead,
)

from app.schemas.audit_log import (
    AuditLogBase,
    AuditLogCreate,
    AuditLogRead,
)

__all__ = [
    # User
    "UserBase", "UserCreate", "UserUpdate", "UserRead",
    # Page
    "PageBase", "PageCreate", "PageUpdate", "PageRead",
    # Page Blocks
    "PageBlockBase", "PageBlockCreate", "PageBlockUpdate", "PageBlockRead",
    # Media
    "MediaBase", "MediaCreate", "MediaRead",
    # Site Settings
    "SiteSettingBase", "SiteSettingCreate", "SiteSettingUpdate", "SiteSettingRead",
    # Audit Logs
    "AuditLogBase", "AuditLogCreate", "AuditLogRead",
]
