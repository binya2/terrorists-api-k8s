from typing import List

from pymongo import MongoClient
from pymongo.errors import ConnectionFailure, ServerSelectionTimeoutError
from pymongo.ssl_match_hostname import CertificateError

from models import MongoConfig, DangerousTerrorists


def _connect():
    db = MongoConfig()
    uri = f"mongodb://{db.username}:{db.password}@{db.host}:{db.port}/"
    # uri = f"mongodb://localhost:27017/"
    try:
        client = MongoClient(uri)
        client.admin.command('ping')
        database = client[db.database]
        collection = database[db.collection]
        return collection
    except (ConnectionFailure, ServerSelectionTimeoutError) as e:
        return None


mongodb = _connect()


def get_db():
    global mongodb
    """Returns the database instance."""
    if mongodb is None:
        mongodb = _connect()
    return mongodb.top_threats.terrorists


def mongodb_check_connection() -> bool:
    """Checks if the connection to MongoDB is alive."""
    global mongodb
    try:
        if get_db() is not None:
            mongodb.admin.command('ping')
            return True
        return False
    except (ConnectionFailure, ServerSelectionTimeoutError):
        return False


def mongodb_add_many(terrorists: List[DangerousTerrorists]) -> bool | None:
    try:
        db = get_db()
        for terrorist in terrorists:
            result = db.insert_one(terrorist.model_dump())
            print(str(result.inserted_id))
        return True
    except Exception as e:
        raise CertificateError()
