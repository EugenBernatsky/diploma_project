from datetime import UTC, datetime

from fastapi import HTTPException

from app.repositories.interactions_repository import (
    find_interactions_by_user,
    insert_interaction,
)
from app.repositories.items_repository import find_item_by_id
from app.schemas.interaction import (
    InteractionActionResponse,
    InteractionCreate,
    InteractionResponse,
    InteractionType,
)


def _map_doc_to_interaction_response(doc: dict) -> InteractionResponse:
    return InteractionResponse(
        id=str(doc["_id"]),
        item_id=str(doc["item_id"]),
        interaction_type=doc["interaction_type"],
        source=doc.get("source"),
        value=doc["value"],
        created_at=doc["created_at"],
    )


async def create_interaction(
    user_id: str,
    payload: InteractionCreate,
) -> InteractionActionResponse:
    item = await find_item_by_id(payload.item_id)
    if item is None:
        raise HTTPException(status_code=404, detail="Item not found")

    await insert_interaction(
        user_id=user_id,
        item_id=payload.item_id,
        interaction_type=payload.interaction_type,
        source=payload.source,
        value=payload.value,
        created_at=datetime.now(UTC),
    )

    return InteractionActionResponse(message="Interaction saved successfully")


async def get_my_interactions(
    user_id: str,
    interaction_type: InteractionType | None = None,
    item_id: str | None = None,
    limit: int = 100,
) -> list[InteractionResponse]:
    docs = await find_interactions_by_user(
        user_id=user_id,
        interaction_type=interaction_type,
        item_id=item_id,
        limit=limit,
    )

    return [_map_doc_to_interaction_response(doc) for doc in docs]