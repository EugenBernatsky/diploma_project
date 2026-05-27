from __future__ import annotations

import math


def normalize_scores(scores: dict[str, float]) -> dict[str, float]:
    if not scores:
        return {}

    cleaned_scores: dict[str, float] = {}

    for item_id, score in scores.items():
        try:
            value = float(score)
        except (TypeError, ValueError):
            value = 0.0

        if math.isnan(value) or math.isinf(value):
            value = 0.0

        cleaned_scores[item_id] = value

    positive_values = [
        value
        for value in cleaned_scores.values()
        if value > 0
    ]

    if not positive_values:
        return {
            item_id: 0.0
            for item_id in cleaned_scores
        }

    min_score = min(positive_values)
    max_score = max(positive_values)

    if max_score == min_score:
        return {
            item_id: 1.0 if score > 0 else 0.0
            for item_id, score in cleaned_scores.items()
        }

    normalized: dict[str, float] = {}

    for item_id, score in cleaned_scores.items():
        if score <= 0:
            normalized[item_id] = 0.0
        else:
            normalized[item_id] = (score - min_score) / (max_score - min_score)

    return normalized


def hybrid_rank(
    content_scores: dict[str, float],
    popularity_scores: dict[str, float],
    limit: int,
    content_weight: float = 0.70,
    popularity_weight: float = 0.30,
    candidate_item_ids: set[str] | None = None,
    exclude_item_ids: set[str] | None = None,
) -> list[tuple[str, float]]:
    normalized_content = normalize_scores(content_scores)
    normalized_popularity = normalize_scores(popularity_scores)

    candidate_ids = set(normalized_content) | set(normalized_popularity)

    if candidate_item_ids is not None:
        candidate_ids &= candidate_item_ids

    if exclude_item_ids:
        candidate_ids -= exclude_item_ids

    ranked: list[tuple[str, float]] = []

    for item_id in candidate_ids:
        score = (
            content_weight * normalized_content.get(item_id, 0.0)
            + popularity_weight * normalized_popularity.get(item_id, 0.0)
        )

        if score <= 0:
            continue

        ranked.append((item_id, score))

    ranked.sort(key=lambda item: item[1], reverse=True)

    return ranked[:limit]