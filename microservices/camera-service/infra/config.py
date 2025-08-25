import os
from dataclasses import dataclass
from typing import List

from dotenv import load_dotenv

load_dotenv()


@dataclass
class KafkaConfig:
    """Kafka configuration."""

    bootstrap_servers: List[str]
    topic_camera_images: str

    @classmethod
    def from_env(cls) -> "KafkaConfig":
        """Create KafkaConfig from environment variables."""
        servers_str = os.getenv("KAFKA_BOOTSTRAP_SERVERS", "localhost:9092")
        servers = [server.strip() for server in servers_str.split(",")]

        return cls(
            bootstrap_servers=servers,
            topic_camera_images=os.getenv("KAFKA_TOPIC_CAMERA_IMAGES", "camera-images"),
        )


@dataclass
class CameraConfig:
    """Camera configuration."""

    camera_index: int
    capture_interval: int
    image_quality: int
    image_width: int
    image_height: int

    @classmethod
    def from_env(cls) -> "CameraConfig":
        """Create CameraConfig from environment variables."""
        return cls(
            camera_index=int(os.getenv("CAMERA_INDEX", "0")),
            capture_interval=int(os.getenv("CAPTURE_INTERVAL", "5")),
            image_quality=int(os.getenv("IMAGE_QUALITY", "80")),
            image_width=int(os.getenv("IMAGE_WIDTH", "640")),
            image_height=int(os.getenv("IMAGE_HEIGHT", "480")),
        )


@dataclass
class Config:
    """Main configuration class."""

    kafka: KafkaConfig
    camera: CameraConfig

    @classmethod
    def from_env(cls) -> "Config":
        """Create Config from environment variables."""
        return cls(
            kafka=KafkaConfig.from_env(),
            camera=CameraConfig.from_env(),
        )
