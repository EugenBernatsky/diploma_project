from __future__ import annotations

from collections import defaultdict

import numpy as np
from scipy import sparse

from app.ml.recommendations.model_store import RecommendationArtifacts


STATUS_WEIGHTS = {
    "completed": 3.0,
    "in_progress": 2.0,
    "planned": 1.0,
    "dropped": -3.0,
}

# Актуальні interaction types з app/schemas/interaction.py:
# - item_view
# - trailer_click
# - external_link_click
INTERACTION_WEIGHTS = {
    "item_view": 0.3,
    "trailer_click": 1.2,
    "external_link_click": 1.5,
}

# Source не є окремим типом взаємодії, але він допомагає краще оцінити силу сигналу.
# Наприклад, клік із recommendations важливіший, ніж звичайний перегляд із catalog.
SOURCE_WEIGHTS = {
    "catalog": 1.0,
    "search": 1.2,
    "recommendations": 1.5,
    "similar_items": 1.3,
    "favorites": 1.0,
    "statuses": 1.0,
    "home": 1.0,
    "item_page": 1.2,
    "profile": 0.8,
    "forum": 0.7,
    "other": 1.0,
}


def _safe_float(value, default: float = 0.0) -> float:
    try:
        return float(value)
    except (TypeError, ValueError):
        return default


def _rating_weight(score: int | float) -> float:
    score_value = _safe_float(score)

    if score_value >= 9:
        return 5.0
    if score_value >= 7:
        return 3.5
    if score_value >= 5:
        return 1.0

    # За планом Stage 1 низькі оцінки мають бути негативним сигналом.
    return -2.0


class ContentRecommendationModel:
    def __init__(self, artifacts: RecommendationArtifacts):
        self.artifacts = artifacts
        self.item_index = {
            item_id: index
            for index, item_id in enumerate(artifacts.item_ids)
        }

    def similar_items(
        self,
        item_id: str,
        limit: int = 12,
        exclude_item_ids: set[str] | None = None,
    ) -> list[tuple[str, float]]:
        if item_id not in self.item_index:
            return []

        exclude = set(exclude_item_ids or set())
        exclude.add(item_id)

        index = self.item_index[item_id]
        query_vector = self.artifacts.item_matrix[index]

        scores = self.artifacts.item_matrix @ query_vector.T
        scores_array = np.asarray(scores.toarray()).ravel()

        return self._top_items(
            scores_array=scores_array,
            limit=limit,
            exclude_item_ids=exclude,
        )

    def personalized_items(
        self,
        user_signals: dict,
        limit: int = 30,
        exclude_item_ids: set[str] | None = None,
    ) -> list[tuple[str, float]]:
        weighted_items = self._collect_weighted_items(user_signals)

        positive_items = {
            item_id: weight
            for item_id, weight in weighted_items.items()
            if weight > 0 and item_id in self.item_index
        }

        if not positive_items:
            return []

        vectors = []
        weights = []

        for item_id, weight in positive_items.items():
            vectors.append(self.artifacts.item_matrix[self.item_index[item_id]])
            weights.append(weight)

        stacked = sparse.vstack(vectors)
        weights_array = np.asarray(weights, dtype=float)

        user_vector = (
            stacked.multiply(weights_array[:, None]).sum(axis=0)
            / weights_array.sum()
        )
        user_vector = sparse.csr_matrix(user_vector)

        scores = self.artifacts.item_matrix @ user_vector.T

        # ВАЖЛИВО:
        # Тут треба .toarray(), інакше np.asarray(scores) може повернути object-array
        # зі sparse matrix всередині, а не нормальний масив float.
        scores_array = np.asarray(scores.toarray()).ravel()

        exclude = set(exclude_item_ids or set())

        # Не рекомендуємо айтеми, з якими користувач уже взаємодіяв.
        # Це базове Stage 1-фільтрування, щоб не повертати те саме.
        exclude.update(weighted_items.keys())

        return self._top_items(
            scores_array=scores_array,
            limit=limit,
            exclude_item_ids=exclude,
        )

    def _top_items(
        self,
        scores_array: np.ndarray,
        limit: int,
        exclude_item_ids: set[str],
    ) -> list[tuple[str, float]]:
        ranked_indexes = np.argsort(scores_array)[::-1]
        result: list[tuple[str, float]] = []

        for index in ranked_indexes:
            item_id = self.artifacts.item_ids[int(index)]
            score = float(scores_array[int(index)])

            if item_id in exclude_item_ids:
                continue

            if score <= 0:
                continue

            result.append((item_id, score))

            if len(result) >= limit:
                break

        return result

    def _collect_weighted_items(self, user_signals: dict) -> dict[str, float]:
        weights: dict[str, float] = defaultdict(float)

        for rating in user_signals.get("ratings", []):
            item_id = rating.get("item_id")
            if item_id is None:
                continue

            weights[str(item_id)] += _rating_weight(rating.get("score", 0))

        for favorite in user_signals.get("favorites", []):
            item_id = favorite.get("item_id")
            if item_id is None:
                continue

            weights[str(item_id)] += 4.0

        for status_doc in user_signals.get("statuses", []):
            item_id = status_doc.get("item_id")
            if item_id is None:
                continue

            status = str(status_doc.get("status"))
            weights[str(item_id)] += STATUS_WEIGHTS.get(status, 0.0)

        for interaction in user_signals.get("interactions", []):
            item_id = interaction.get("item_id")
            if item_id is None:
                continue

            interaction_type = str(interaction.get("interaction_type"))
            source = str(interaction.get("source") or "other")

            base_weight = INTERACTION_WEIGHTS.get(interaction_type, 0.1)
            source_weight = SOURCE_WEIGHTS.get(source, 1.0)

            weights[str(item_id)] += base_weight * source_weight

        return dict(weights)