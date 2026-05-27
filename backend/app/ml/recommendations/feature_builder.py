from __future__ import annotations


def _as_list(value) -> list[str]:
    if value is None:
        return []
    if isinstance(value, list):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _localized_text(localized: dict | None) -> list[str]:
    if not isinstance(localized, dict):
        return []

    parts: list[str] = []
    for content in localized.values():
        if not isinstance(content, dict):
            continue
        for key in ("title", "description", "tagline"):
            value = content.get(key)
            if value:
                parts.append(str(value))
    return parts


def build_item_feature_text(item: dict) -> str:
    """Create one searchable text string for a media item.

    The same function is used during training and during recommendation serving.
    This keeps production features consistent with saved model artifacts.
    """

    parts: list[str] = []

    for key in (
        "title",
        "category",
        "year",
        "description",
        "original_title",
        "original_name",
        "original_language",
        "tagline",
        "content_status",
        "subtitle",
        "publisher",
        "published_date",
        "saleability",
        "viewability",
        "access_view_status",
    ):
        value = item.get(key)
        if value is not None and str(value).strip():
            parts.append(str(value))

    for key in (
        "genres",
        "production_countries",
        "episode_run_time",
        "networks",
        "authors",
    ):
        parts.extend(_as_list(item.get(key)))

    localized = item.get("localized")
    parts.extend(_localized_text(localized))

    return " ".join(parts).lower()
