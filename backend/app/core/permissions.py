from typing import Dict, Set, Union, List
from functools import lru_cache
from fastapi import Depends, HTTPException, status
from app.db.models.user import User

from app.core.auth_deps import get_current_user


# -------------------------
# All available permissions 
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
# Role → allowed permissions
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
    return ROLE_PERMISSIONS.get(role, set())

def get_role_permissions_verbose(role: str) -> Dict[str, str]:
    perms = get_role_permissions(role)
    return {p: PERMISSION_DESCRIPTIONS[p] for p in perms if p in PERMISSION_DESCRIPTIONS}


# -------------------------
# FastAPI dependency (Enhanced with Role Guard)
# -------------------------
def require_permission(permission: Union[str, List[str]]):
    perms = {permission} if isinstance(permission, str) else set(permission)

    def dep(current_user: User = Depends(get_current_user)) -> User:
        
        # This check for None is largely redundant since get_current_user raises 401,
        # but it keeps the flow clear.
        if current_user is None:
             raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not authenticated",
            )
        
        # --- ENHANCEMENT: Role Guard to avoid AttributeError ---
        # Checks if the 'role' attribute exists and is not None/empty string.
        # This protects against possible bad data from the database.
        if not getattr(current_user, "role", None):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED, 
                detail="User has no role assigned"
            )

        role_perms = get_role_permissions(current_user.role)
        
        # Check if the required permissions are NOT entirely disjoint from the user's role permissions
        if perms.isdisjoint(role_perms):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Permission(s) {list(perms)} required",
            )
            
        return current_user

    return dep