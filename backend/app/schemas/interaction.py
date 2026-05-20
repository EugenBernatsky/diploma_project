from datetime import datetime
from typing import Literal

from pydantic import BaseModel, Field


InteractionType = Literal[
    "view",
    "open_details",
    "search_click",
    "recommendation_click",
]

InteractionSource = Literal[
    "catalog",
    "search",
    "recommendations",
    "favorites",
    "statuses",
    "other",
]


class InteractionCreate(BaseModel):
    item_id: str
    interaction_type: InteractionType
    source: InteractionSource | None = None
    value: int = Field(default=1, ge=1, le=10)


class InteractionResponse(BaseModel):
    id: str
    item_id: str
    interaction_type: InteractionType
    source: InteractionSource | None
    value: int
    created_at: datetime


class InteractionActionResponse(BaseModel):
    message: str