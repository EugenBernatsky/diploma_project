from pydantic import BaseModel


class FavoriteActionResponse(BaseModel):
    message: str