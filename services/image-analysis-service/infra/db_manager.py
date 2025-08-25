from pymongo import MongoClient
from infra.config import MongoDBConfig

class MongoDBManager:
    def __init__(self, config: MongoDBConfig):
        """Class to manage MongoDB"""

        self._client = MongoClient(config.uri)
        self._db = self._client[config.db_name]

    def get_email_by_label(self, label: str) -> str | None:
        return self._db["classroom_detections"].find_one(
            {"label": label}, {"email": 1}
        )

    def close(self):
        """Close db connection"""
        self._client.close()
