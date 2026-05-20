from pydantic import BaseModel, Field


class RatingPayload(BaseModel):
    score: int = Field(ge=1, le=10)


class RatingActionResponse(BaseModel):
    message: str


class UserRatingResponse(BaseModel):
    item_id: str
    score: int