from fastapi import HTTPException

ROLE_TOKENS = {
    "ABC123": "super_admin",
    "DEF456": "post_admin",
    "VIEW789": "viewer"
}

ROLE_HIERARCHY = {
    "super_admin": 3,
    "post_admin": 2,
    "viewer": 1
}

def check_role(token: str) -> str:
    role = ROLE_TOKENS.get(token)
    if not role:
        raise HTTPException(status_code=401, detail="Unauthorized: Invalid admin token")
    return role

def has_permission(role: str, required_role: str) -> bool:
    return ROLE_HIERARCHY.get(role, 0) >= ROLE_HIERARCHY.get(required_role, 0)
