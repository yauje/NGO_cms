from typing import Dict, Set, Union, List
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from app.db.models.user import User

# FIX 1: Import the base dependency from the dedicated file (auth_deps.py)
# This breaks the circular dependency: permissions -> auth -> auth_deps
from app.core.auth_deps import get_current_user


# -------------------------
# All available permissions (Renamed to prevent confusion with ROLE_PERMISSIONS)
# -------------------------
PERMISSION_DESCRIPTIONS: Dict[str, str] = {
    "users.view": "View user accounts",
    "users.create": "Create new users",
    "users.edit": "Edit existing users",
    "users.delete": "Delete users",
    "users.manage_roles": "Manage user roles",
    "content.view": "View content",
    "content.create": "Create content",
    "content.edit": "Edit content",
    "content.delete": "Delete content",
    "content.publish": "Publish content",
    "content.revise": "Revise content",
    "media.view": "View media",
    "media.upload": "Upload media",
    "media.delete": "Delete media",
    "site.settings.view": "View site settings",
    "site.settings.edit": "Edit site settings",
    "analytics.view": "View analytics",
    "public.view": "View public content",
}

# -------------------------
# Role → allowed permissions (Using the set of keys from descriptions for "admin")
# -------------------------
ROLE_PERMISSIONS: Dict[str, Set[str]] = {
    "admin": set(PERMISSION_DESCRIPTIONS.keys()),
    "editor": {
        "content.view", "content.create", "content.edit", "content.delete",
        "content.publish", "content.revise",
        "media.view", "media.upload", "media.delete",
        "analytics.view",
        "public.view",
    },
    "public": {"public.view"},
}

# -------------------------
# Helper functions
# -------------------------
@lru_cache(maxsize=32)
def get_role_permissions(role: str) -> Set[str]:
    # NOTE: The self-import "from .permissions import get_role_permissions" was removed
    return ROLE_PERMISSIONS.get(role, set())

def get_role_permissions_verbose(role: str) -> Dict[str, str]:
    perms = get_role_permissions(role)
    # Use the correctly named dictionary
    return {p: PERMISSION_DESCRIPTIONS[p] for p in perms if p in PERMISSION_DESCRIPTIONS}


# -------------------------
# FastAPI dependency
# -------------------------
def require_permission(permission: Union[str, List[str]]): # Return type is `callable` not `Depends`
    perms = {permission} if isinstance(permission, str) else set(permission)

    # FIX 2: Correctly define the inner dependency function to take the Depends
    # as an argument. This is the standard, non-lazy method.
    def dep(current_user: User = Depends(get_current_user)) -> User:
        
        # The following lazy import/call is WRONG and was removed:
        # from app.api.routes.auth import get_current_user
        # current_user: User = Depends(get_current_user)()

        if current_user is None: # This check is redundant if get_current_user raises HTTPException, but harmless
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )

        role_perms = get_role_permissions(current_user.role)
        if perms.isdisjoint(role_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission(s) {list(perms)} required",
            )
        return current_user

    # When using a function factory for a dependency, you return the inner function (dep),
    # not Depends(dep). The caller uses Depends(require_permission(...)).
    return dep