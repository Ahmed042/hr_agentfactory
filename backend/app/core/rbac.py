"""Role-Based Access Control (RBAC) decorators"""
from functools import wraps
from fastapi import HTTPException, Depends
from app.core.auth import get_current_user
from app.models.user import User

# Permission matrix: role -> allowed actions
ROLE_PERMISSIONS = {
    "admin": {
        "candidates": ["create", "read", "update", "delete"],
        "employees": ["create", "read", "update", "delete"],
        "departments": ["create", "read", "update", "delete"],
        "payroll": ["create", "read", "update", "delete", "generate", "send"],
        "interviews": ["create", "read", "update", "delete"],
        "jobs": ["create", "read", "update", "delete"],
        "leaves": ["create", "read", "update", "delete", "approve"],
        "documents": ["create", "read", "delete"],
        "analytics": ["read"],
        "settings": ["read", "update"],
        "webhooks": ["create", "read", "delete"],
        "users": ["create", "read", "update", "delete"],
    },
    "hr_manager": {
        "candidates": ["create", "read", "update"],
        "employees": ["create", "read", "update"],
        "departments": ["read"],
        "payroll": ["read", "generate"],
        "interviews": ["create", "read", "update"],
        "jobs": ["create", "read", "update"],
        "leaves": ["create", "read", "update", "approve"],
        "documents": ["create", "read"],
        "analytics": ["read"],
        "settings": ["read"],
    },
    "recruiter": {
        "candidates": ["create", "read", "update"],
        "employees": ["read"],
        "departments": ["read"],
        "payroll": [],
        "interviews": ["create", "read", "update"],
        "jobs": ["create", "read", "update"],
        "leaves": ["create", "read"],
        "documents": ["create", "read"],
        "analytics": ["read"],
    },
    "viewer": {
        "candidates": ["read"],
        "employees": ["read"],
        "departments": ["read"],
        "payroll": ["read"],
        "interviews": ["read"],
        "jobs": ["read"],
        "leaves": ["read"],
        "documents": ["read"],
        "analytics": ["read"],
    },
}


def require_permission(resource: str, action: str):
    """Dependency that checks if the current user has permission for a resource+action"""
    def permission_checker(current_user: User = Depends(get_current_user)):
        role_perms = ROLE_PERMISSIONS.get(current_user.role, {})
        resource_perms = role_perms.get(resource, [])

        if action not in resource_perms:
            raise HTTPException(
                status_code=403,
                detail=f"Insufficient permissions. Role '{current_user.role}' cannot '{action}' on '{resource}'.",
            )
        return current_user

    return permission_checker


def check_permission(user: User, resource: str, action: str) -> bool:
    """Check if a user has permission (non-raising version)"""
    role_perms = ROLE_PERMISSIONS.get(user.role, {})
    resource_perms = role_perms.get(resource, [])
    return action in resource_perms
