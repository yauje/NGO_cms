# app/core/permissions.py
from typing import Set, Union, List
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from app.api.routes.auth import get_current_user
from app.db.models.user import User



# 1. Canonical source of truth ----------------------------------------------
PERMISSIONS: dict[str, Set[str]] = {
    "admin": {
        # Users
        "users.view", "users.create", "users.edit", "users.delete", "users.manage_roles",
        # Content
        "content.view", "content.create", "content.edit", "content.delete",
        "content.publish", "content.revise",
        # Media
        "media.view", "media.upload", "media.delete",
        # Site settings
        "site.settings.view", "site.settings.edit",
        # Analytics
        "analytics.view",
        # Public access
        "public.view",
    },
    "editor": {
        "content.view", "content.create", "content.edit", "content.delete",
        "content.publish", "content.revise",
        "media.view", "media.upload", "media.delete",
        "analytics.view",
        "public.view",
    },
    "public": {
        "public.view",
    },
}

# 2. Internal helper --------------------------------------------------------
@lru_cache(maxsize=32)
def _role_permissions(role: str) -> Set[str]:
    """Cached lookup for role permissions."""
    return PERMISSIONS.get(role, set())

# 3. Main dependency --------------------------------------------------------
def require_permission(
    permission: Union[str, List[str]]
) -> Depends:
    """
    Route-level permission dependency.

    Usage:
        @router.get("/pages", dependencies=[Depends(require_permission("content.view"))])
        async def list_pages(user: User = Depends(require_permission("content.view"))):
            ...
    """
    perms = {permission} if isinstance(permission, str) else set(permission)

    def dep(current_user: User = Depends(get_current_user)) -> User:
        if current_user is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        role_perms = _role_permissions(current_user.role)
        if perms.isdisjoint(role_perms):  # User must have at least one permission
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission(s) {list(perms)} required",
            )
        return current_user

    return dep
