import json
from datetime import datetime

from kafka import KafkaProducer
from kafka.errors import KafkaError
from loguru import logger

from infra.config import KafkaConfig, CameraConfig


class CameraImageProducer:
    """Kafka producer for camera images."""

    def __init__(self, kafka_config: KafkaConfig, camera_config: CameraConfig):
        """Initialize the Kafka producer.

        Args:
            config: Kafka configuration
        """
        self.kafka_config = kafka_config
        self.camera_config = camera_config
        self.producer = None
        self._initialize_producer()

    def _initialize_producer(self) -> None:
        """Initialize the Kafka producer."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.kafka_config.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",  # Wait for all replicas to acknowledge
                retries=3,  # Retry failed sends
                retry_backoff_ms=300,
                max_in_flight_requests_per_connection=1,  # Ensure ordering
                compression_type="gzip",  # Compress large image data
            )
            logger.info("Kafka producer initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

    def send_image_message(self, encoded_image: str) -> bool:
        """Send image message to Kafka topic.

        Args:
            message: Image message dictionary

        Returns:
            True if message was sent successfully, False otherwise
        """
        if not self.producer:
            logger.error("Producer is not initialized")
            return False

        try:
            message = {
                "timestamp": datetime.now().isoformat(),
                "service_name": "camera-service",
                "camera_index": self.camera_config.camera_index,
                "image_data": encoded_image,
                "image_format": "JPEG",
                "image_quality": self.camera_config.image_quality,
                "image_width": self.camera_config.image_width,
                "image_height": self.camera_config.image_height,
                "encoding": "base64",
            }

            key = message["timestamp"]

            future = self.producer.send(
                topic=self.kafka_config.topic_camera_images, key=key, value=message
            )

            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)

            logger.info(
                f"Image message sent successfully to topic '{record_metadata.topic}'"
            )

            return True

        except KafkaError as e:
            logger.error(f"Kafka error while sending message: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending message: {e}")
            return False

    def close(self) -> None:
        """Close the Kafka producer."""
        if self.producer:
            self.producer.flush()  # Ensure all messages are sent
            self.producer.close()
            logger.info("Kafka producer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
