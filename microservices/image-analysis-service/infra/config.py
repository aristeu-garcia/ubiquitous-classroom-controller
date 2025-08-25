import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


DEFATULT_DATE_FORMAT = "%Y-%m-%dT%H:%M:%SZ"
INTERVAL_BETWEEN_DETECTIONS = 3

@dataclass
class KafkaConfig:
    """Kafka configuration."""

    bootstrap_servers: List[str]
    topic_camera_images: str
    topic_professor_detection: str
    consumer_group_id: str

    @classmethod
    def from_env(cls) -> "KafkaConfig":
        """Create KafkaConfig from environment variables."""
        servers_str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        servers = [server.strip() for server in servers_str.split(",")]

        return cls(
            bootstrap_servers=servers,
            topic_camera_images=os.getenv("KAFKA_TOPIC_CAMERA_IMAGES", "camera-images"),
            topic_professor_detection=os.getenv(
                "KAFKA_TOPIC_PROFESSOR_DETECTION", "professor-detection"
            ),
            consumer_group_id=os.getenv(
                "KAFKA_CONSUMER_GROUP_ID", "image-analysis-group"
            ),
        )


@dataclass
class ModelConfig:
    """Model configuration."""

    model_path: str
    confidence_threshold: float
    device: str

    @classmethod
    def from_env(cls) -> "ModelConfig":
        """Create ModelConfig from environment variables."""
        return cls(
            model_path=os.getenv("MODEL_PATH", "src/models/ubiclass1.pt"),
            confidence_threshold=float(os.getenv("CONFIDENCE_THRESHOLD", "0.5")),
            device=os.getenv("DEVICE", "cpu"),  # or "cuda" if GPU available
        )


@dataclass    
class MongoDBConfig:
    """MongoDB configuration."""

    uri: str
    db_name: str

    @classmethod
    def from_env(cls) -> "MongoDBConfig":
        """Create MongoDBConfig from environment variables."""
        return cls(
            uri=os.getenv("MONGO_URI"),
            db_name=os.getenv("MONGO_DB_NAME"),
        )


@dataclass
class Config:
    """Main configuration class."""

    kafka: KafkaConfig
    model: ModelConfig
    mongo: MongoDBConfig

    @classmethod
    def from_env(cls) -> "Config":
        """Create Config from environment variables."""
        return cls(
            kafka=KafkaConfig.from_env(),
            model=ModelConfig.from_env(),
            mongo=MongoDBConfig.from_env(),
        )
