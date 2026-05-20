from app.core.profile_defaults import DEFAULT_AVATAR_ID, VALID_AVATAR_IDS


def resolve_avatar_id(value: str | None) -> str:
    if value in VALID_AVATAR_IDS:
        return value
    return DEFAULT_AVATAR_ID