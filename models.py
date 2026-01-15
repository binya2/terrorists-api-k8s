from typing import Annotated, List

from pydantic import BaseModel, Field


class Terrorist(BaseModel):
    name: Annotated[str, Field(..., min_length=2, max_length=20)]
    location: Annotated[str, Field(..., min_length=2, max_length=20)]
    danger_rate: Annotated[int, Field(..., ge=0, le=10, description="Danger rate between 1 and 10")]


class TopThreatsResponse(BaseModel):
    top: List[Terrorist]
    count: int
