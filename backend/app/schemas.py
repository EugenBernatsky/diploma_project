from typing import Literal

from pydantic import BaseModel


Category = Literal["movie", "series", "book"]


class MediaItem(BaseModel):
    id: int
    title: str
    category: Category
    year: int
    genres: list[str]
    description: str