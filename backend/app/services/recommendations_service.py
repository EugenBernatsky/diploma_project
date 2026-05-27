from __future__ import annotations

import math

from fastapi import HTTPException

from app.ml.recommendations.content_model import ContentRecommendationModel
from app.ml.recommendations.hybrid_ranker import hybrid_rank
from app.ml.recommendations.model_store import load_recommendation_artifacts
from app.repositories.items_repository import find_item_by_id
from app.repositories.recommendations_repository import (
    find_items_by_string_ids,
    find_recommendation_items,
    find_user_recommendation_signals,
    get_collaborative_data_stats,
    get_popularity_scores,
)
from app.schemas.item import Category
from app.schemas.recommendation import (
    RecommendationItem,
    RecommendationSection,
    RecommendationsResponse,
    SimilarItemsResponse,
)
from app.services.items_service import _map_doc_to_media_item


def _map_recommendation_items(
    docs_by_id: dict[str, dict],
    ranked_items: list[tuple[str, float]],
    reason: str,
) -> list[RecommendationItem]:
    result: list[RecommendationItem] = []

    for item_id, score in ranked_items:
        doc = docs_by_id.get(item_id)

        if doc is None:
            continue

        result.append(
            RecommendationItem(
                item=_map_doc_to_media_item(doc),
                score=round(float(score), 4),
                reason=reason,
            )
        )

    return result


def _has_user_history(user_signals: dict) -> bool:
    return any(
        user_signals.get(key)
        for key in ("ratings", "favorites", "statuses", "interactions")
    )


def _build_excluded_item_ids(user_signals: dict) -> set[str]:
    excluded: set[str] = set()

    # Якщо користувач уже оцінював item — не рекомендуємо його повторно.
    for rating in user_signals.get("ratings", []):
        item_id = rating.get("item_id")

        if item_id is not None:
            excluded.add(str(item_id))

    # Favorites теж вже відомі користувачу.
    for favorite in user_signals.get("favorites", []):
        item_id = favorite.get("item_id")

        if item_id is not None:
            excluded.add(str(item_id))

    # Будь-який статус означає, що item уже є в списках користувача.
    for status_doc in user_signals.get("statuses", []):
        item_id = status_doc.get("item_id")

        if item_id is not None:
            excluded.add(str(item_id))

    # Interactions — слабший сигнал, але для Stage 2 краще не дублювати
    # те, що користувач уже відкривав/клікав.
    for interaction in user_signals.get("interactions", []):
        item_id = interaction.get("item_id")

        if item_id is not None:
            excluded.add(str(item_id))

    return excluded


def _build_external_popularity_scores(items: list[dict]) -> dict[str, float]:
    scores: dict[str, float] = {}

    for doc in items:
        item_id = str(doc["_id"])

        rating_average = (
            doc.get("tmdb_vote_average")
            or doc.get("book_rating_average")
            or 0
        )

        ratings_count = (
            doc.get("tmdb_vote_count")
            or doc.get("book_ratings_count")
            or 0
        )

        try:
            rating_average_value = float(rating_average or 0)
        except (TypeError, ValueError):
            rating_average_value = 0.0

        try:
            ratings_count_value = float(ratings_count or 0)
        except (TypeError, ValueError):
            ratings_count_value = 0.0

        # rating_average: якість
        # log(count): легкий boost за популярність, але без дикого перекосу
        count_boost = math.log1p(max(ratings_count_value, 0.0))

        scores[item_id] = rating_average_value + count_boost

    return scores


def _merge_popularity_scores(
    internal_scores: dict[str, float],
    external_scores: dict[str, float],
    candidate_item_ids: set[str],
) -> dict[str, float]:
    merged: dict[str, float] = {}

    for item_id in candidate_item_ids:
        internal_score = internal_scores.get(item_id, 0.0)
        external_score = external_scores.get(item_id, 0.0)

        # Internal behavior важливіший, але external rating потрібен,
        # коли на сайті ще мало користувацьких даних.
        merged[item_id] = internal_score + external_score

    return merged


def _rank_popular_items(
    popularity_scores: dict[str, float],
    limit: int,
    candidate_item_ids: set[str],
    exclude_item_ids: set[str] | None = None,
) -> list[tuple[str, float]]:
    excluded = exclude_item_ids or set()

    ranked = [
        (item_id, score)
        for item_id, score in popularity_scores.items()
        if item_id in candidate_item_ids
        and item_id not in excluded
        and score > 0
    ]

    ranked.sort(key=lambda item: item[1], reverse=True)

    return ranked[:limit]


async def get_personal_recommendations(
    user_id: str,
    limit: int = 30,
    category: Category | None = None,
) -> RecommendationsResponse:
    limit = max(1, min(limit, 50))

    items = await find_recommendation_items(
        limit=5000,
        category=category,
    )

    docs_by_id = {
        str(doc["_id"]): doc
        for doc in items
    }

    candidate_item_ids = set(docs_by_id)

    internal_popularity_scores = await get_popularity_scores()
    external_popularity_scores = _build_external_popularity_scores(items)

    popularity_scores = _merge_popularity_scores(
        internal_scores=internal_popularity_scores,
        external_scores=external_popularity_scores,
        candidate_item_ids=candidate_item_ids,
    )

    user_signals = await find_user_recommendation_signals(user_id)
    has_history = _has_user_history(user_signals)
    excluded_item_ids = _build_excluded_item_ids(user_signals)

    popular_ranked = _rank_popular_items(
        popularity_scores=popularity_scores,
        limit=limit,
        candidate_item_ids=candidate_item_ids,
        exclude_item_ids=excluded_item_ids if has_history else set(),
    )

    sections: list[RecommendationSection] = []

    based_on_preferences_items: list[RecommendationItem]
    based_on_preferences_status: str
    based_on_preferences_algorithm: str
    based_on_preferences_reason: str

    try:
        artifacts = load_recommendation_artifacts()
        model = ContentRecommendationModel(artifacts)

        if not has_history:
            based_on_preferences_items = _map_recommendation_items(
                docs_by_id=docs_by_id,
                ranked_items=popular_ranked,
                reason="Cold start fallback: not enough user actions yet, so popular and well-rated items are shown.",
            )
            based_on_preferences_status = "cold_start_fallback"
            based_on_preferences_algorithm = "popularity_fallback"
        else:
            content_ranked = model.personalized_items(
                user_signals=user_signals,
                limit=limit * 5,
                exclude_item_ids=excluded_item_ids,
            )

            content_scores = {
                item_id: score
                for item_id, score in content_ranked
                if item_id in candidate_item_ids
                and item_id not in excluded_item_ids
            }

            hybrid_ranked = hybrid_rank(
                content_scores=content_scores,
                popularity_scores=popularity_scores,
                limit=limit,
                content_weight=0.70,
                popularity_weight=0.30,
                candidate_item_ids=candidate_item_ids,
                exclude_item_ids=excluded_item_ids,
            )

            if hybrid_ranked:
                based_on_preferences_reason = (
                    "Hybrid recommendation based on your ratings, favorites, statuses, "
                    "interactions and item popularity."
                )
                based_on_preferences_status = "personalized"
                based_on_preferences_algorithm = "hybrid_content_popularity"
                based_on_preferences_items = _map_recommendation_items(
                    docs_by_id=docs_by_id,
                    ranked_items=hybrid_ranked,
                    reason=based_on_preferences_reason,
                )
            else:
                based_on_preferences_reason = (
                    "Fallback: user actions exist, but there are not enough suitable unseen items."
                )
                based_on_preferences_status = "personalized_fallback"
                based_on_preferences_algorithm = "popularity_fallback"
                based_on_preferences_items = _map_recommendation_items(
                    docs_by_id=docs_by_id,
                    ranked_items=popular_ranked,
                    reason=based_on_preferences_reason,
                )

    except FileNotFoundError:
        based_on_preferences_items = _map_recommendation_items(
            docs_by_id=docs_by_id,
            ranked_items=popular_ranked,
            reason="Model artifacts are missing, so the system uses popularity fallback.",
        )
        based_on_preferences_status = "model_not_trained"
        based_on_preferences_algorithm = "popularity_fallback"

    sections.append(
        RecommendationSection(
            key="based_on_preferences",
            title="Based on your preferences",
            algorithm=based_on_preferences_algorithm,
            status=based_on_preferences_status,
            items=based_on_preferences_items,
        )
    )

    sections.append(
        RecommendationSection(
            key="popular_now",
            title="Popular on MediaCompass",
            algorithm="popularity_score",
            status="available" if popular_ranked else "unavailable",
            items=_map_recommendation_items(
                docs_by_id=docs_by_id,
                ranked_items=popular_ranked,
                reason="Popular among MediaCompass users or highly rated by external sources.",
            ),
        )
    )

    collaborative_stats = await get_collaborative_data_stats()

    sections.append(
        RecommendationSection(
            key="similar_users",
            title="Based on users with similar tastes",
            algorithm="collaborative_filtering",
            status=(
                "available"
                if collaborative_stats["is_available"]
                else "waiting_for_more_user_data"
            ),
            items=[],
        )
    )

    return RecommendationsResponse(sections=sections)


async def get_similar_items(
    item_id: str,
    limit: int = 12,
    category: Category | None = None,
) -> SimilarItemsResponse:
    limit = max(1, min(limit, 30))

    source_item = await find_item_by_id(item_id)

    if source_item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    effective_category: Category | None = category

    if effective_category is None:
        effective_category = source_item.get("category")

    try:
        artifacts = load_recommendation_artifacts()
        model = ContentRecommendationModel(artifacts)

        ranked = model.similar_items(
            item_id=item_id,
            limit=limit * 3,
        )

        docs = await find_items_by_string_ids(
            [ranked_item_id for ranked_item_id, _ in ranked],
            category=effective_category,
        )

        docs_by_id = {
            str(doc["_id"]): doc
            for doc in docs
        }

        filtered_ranked = [
            (ranked_item_id, score)
            for ranked_item_id, score in ranked
            if ranked_item_id in docs_by_id
        ][:limit]

        items = _map_recommendation_items(
            docs_by_id=docs_by_id,
            ranked_items=filtered_ranked,
            reason="Similar genre, description, category and metadata.",
        )

        status = "available" if items else "unavailable"

    except FileNotFoundError:
        items = []
        status = "model_not_trained"

    return SimilarItemsResponse(
        source_item_id=item_id,
        algorithm="content_based_similarity",
        status=status,
        items=items,
    )