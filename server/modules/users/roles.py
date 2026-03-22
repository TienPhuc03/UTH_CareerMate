VALID_USER_ROLES = {"candidate", "recruiter", "admin"}
LEGACY_USER_ROLE_ALIASES = {
    "student": "candidate",
}


def normalize_user_role(role: str | None) -> str | None:
    if role is None:
        return None

    normalized = role.strip().lower()
    return LEGACY_USER_ROLE_ALIASES.get(normalized, normalized)
