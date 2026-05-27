from datetime import datetime
from typing import Literal

from pydantic import BaseModel


InteractionType = Literal[
    "item_view",
    "trailer_click",
    "external_link_click",
]


InteractionSource = Literal[
    "catalog",
    "search",
    "recommendations",
    "similar_items",
    "favorites",
    "statuses",
    "home",
    "item_page",
    "profile",
    "forum",
    "other",
]


class InteractionCreate(BaseModel):
    item_id: str
    interaction_type: InteractionType
    source: InteractionSource = "other"


class InteractionResponse(BaseModel):
    id: str
    item_id: str
    interaction_type: InteractionType
    source: InteractionSource
    created_at: datetime


class InteractionActionResponse(BaseModel):
    message: str