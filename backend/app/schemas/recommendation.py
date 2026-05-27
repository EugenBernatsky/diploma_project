from __future__ import annotations

from pydantic import BaseModel, Field

from app.schemas.item import MediaItem


class RecommendationItem(BaseModel):
    item: MediaItem
    score: float = Field(ge=0)
    reason: str


class RecommendationSection(BaseModel):
    key: str
    title: str
    algorithm: str
    status: str
    items: list[RecommendationItem]


class RecommendationsResponse(BaseModel):
    sections: list[RecommendationSection]


class SimilarItemsResponse(BaseModel):
    source_item_id: str
    algorithm: str
    status: str
    items: list[RecommendationItem]
