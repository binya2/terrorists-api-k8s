from typing import Annotated

from pydantic import BaseModel, Field


class DangerousTerrorists(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=20)]
    danger_rate: Annotated[int, Field(ge=0, le=10)]
    location: Annotated[str, Field(min_length=2, max_length=20)]
