# utils/role_check_util.py

# WARNING: Hardcoded tokens for development/testing only.
# TODO: Replace static tokens with dynamic role management (JWT/OAuth) in future versions.

ROLE_TOKENS = {
    "ABC123": "super_admin",
    "DEF456": "post_admin",
    "VIEW789": "viewer"
}

def check_role(token: str) -> str:
    return ROLE_TOKENS.get(token, "unauthorized")
