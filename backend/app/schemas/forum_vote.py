from typing import Literal

from pydantic import BaseModel


ForumVoteTargetType = Literal["thread", "post"]
ForumVoteValue = Literal[1, -1]


class ForumVotePayload(BaseModel):
    value: ForumVoteValue


class ForumVoteResponse(BaseModel):
    target_type: ForumVoteTargetType
    target_id: str
    current_vote: int | None
    score: int
    message: str


class ForumMyVoteResponse(BaseModel):
    target_type: ForumVoteTargetType
    target_id: str
    current_vote: int | None