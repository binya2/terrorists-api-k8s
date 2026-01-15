import os
from typing import Annotated

from pydantic import BaseModel, Field


class DangerousTerrorists(BaseModel):
    name: Annotated[str, Field(min_length=2, max_length=20)]
    danger_rate: Annotated[int, Field(ge=0, le=10)]
    location: Annotated[str, Field(min_length=2, max_length=20)]


class MongoConfig(BaseModel):
    """Configuration for MongoDB connection."""
    host: str = os.getenv("MONGO_HOST", "mongo-0.mongo")
    port: int = os.getenv("MONGO_PORT", 27017)
    username: str = os.getenv("MONGO_USERNAME", "admin")
    password: str = os.getenv("MONGO_PASSWORD", "secretpass")
    database: str = os.getenv("MONGO_DB", "top_threats")
    auth_source: str = os.getenv("MONGO_AUTH_SOURCE", "admin")
    collection: str = os.getenv("MONGO_COLLECTION", "terrorists")
