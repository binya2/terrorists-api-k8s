import logging
import os

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

MONGO_HOST = os.getenv("MONGO_HOST", "mongo-0.mongo")
MONGO_PORT = int(os.getenv("MONGO_PORT", 27017))
MONGO_USERNAME = os.getenv("MONGO_USERNAME", "admin")
MONGO_PASSWORD = os.getenv("MONGO_PASSWORD", "secretpass")
MONGO_DB = os.getenv("MONGO_DB", "threat_db")
MONGO_AUTH_SOURCE = os.getenv("MONGO_AUTH_SOURCE", "admin")


def get_db_connection():
    """Establishes and returns a MongoDB database connection."""
    uri = (
        f"mongodb://{MONGO_USERNAME}:{MONGO_PASSWORD}@"
        f"{MONGO_HOST}:{MONGO_PORT}/?authSource={MONGO_AUTH_SOURCE}"
    )
    try:
        client = MongoClient(uri, serverSelectionTimeoutMS=2000)
        client.admin.command('ping')
        logger.info("Successfully connected to MongoDB")
        return client[MONGO_DB]
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        logger.error(f"Failed to connect to MongoDB: {e}")
        return None


def mongodb_check_connection() -> bool:
    return get_db_connection() is not None


def insert_threats(data: list):
    db = get_db_connection()
    if db is None:
        raise ConnectionFailure("Database unavailable")
    collection = db["top_threats"]
    if data:
        result = collection.insert_many([item.copy() for item in data])
        logger.info(f"Inserted {len(result.inserted_ids)} documents into top_threats")
        return len(result.inserted_ids)
    return 0
