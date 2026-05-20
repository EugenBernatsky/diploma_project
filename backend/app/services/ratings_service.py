from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.items_repository import find_item_by_id
from app.repositories.ratings_repository import (
    delete_rating,
    find_rating,
    insert_rating,
    update_rating,
)
from app.schemas.rating import RatingActionResponse, RatingPayload, UserRatingResponse


async def get_my_rating(user_id: str, item_id: str) -> UserRatingResponse:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    rating = await find_rating(user_id, item_id)
    if rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")

    return UserRatingResponse(
        item_id=item_id,
        score=rating["score"],
    )


async def create_rating(user_id: str, item_id: str, payload: RatingPayload) -> RatingActionResponse:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_rating = await find_rating(user_id, item_id)
    if existing_rating is not None:
        raise HTTPException(status_code=400, detail="Rating already exists")

    now = datetime.now(UTC)

    await insert_rating(
        user_id=user_id,
        item_id=item_id,
        score=payload.score,
        created_at=now,
        updated_at=now,
    )

    return RatingActionResponse(message="Rating created successfully")


async def edit_rating(user_id: str, item_id: str, payload: RatingPayload) -> RatingActionResponse:
    item = await find_item_by_id(item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    existing_rating = await find_rating(user_id, item_id)
    if existing_rating is None:
        raise HTTPException(status_code=404, detail="Rating not found")

    await update_rating(
        user_id=user_id,
        item_id=item_id,
        score=payload.score,
        updated_at=datetime.now(UTC),
    )

    return RatingActionResponse(message="Rating updated successfully")


async def remove_rating(user_id: str, item_id: str) -> RatingActionResponse:
    deleted = await delete_rating(user_id, item_id)

    if not deleted:
        raise HTTPException(status_code=404, detail="Rating not found")

    return RatingActionResponse(message="Rating deleted successfully")