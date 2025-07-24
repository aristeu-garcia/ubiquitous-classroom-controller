import json
from datetime import datetime
from typing import Any, Generator

from kafka import KafkaConsumer
from kafka.errors import KafkaError
from loguru import logger

from infra.config import KafkaConfig, Config


class ImageConsumer:
    """Kafka consumer for camera images."""

    def __init__(self, config: KafkaConfig):
        """Initialize the Kafka consumer.

        Args:
            config: Kafka configuration
        """
        self.config = config
        self.consumer = None
        self._initialize_consumer()

    def _initialize_consumer(self) -> None:
        """Initialize the Kafka consumer."""
        try:
            self.consumer = KafkaConsumer(
                self.config.topic_camera_images,
                bootstrap_servers=self.config.bootstrap_servers,
                value_deserializer=lambda v: json.loads(v.decode("utf-8")),
                key_deserializer=lambda k: k.decode("utf-8") if k else None,
                enable_auto_commit=True,
                auto_offset_reset="latest",  # Start from latest messages
                group_id=self.config.consumer_group_id,
            )
            logger.info(
                f"Kafka consumer initialized for topic '{self.config.topic_camera_images}'"
            )

        except Exception as e:
            logger.error(f"Failed to initialize Kafka consumer: {e}")
            raise

    def consume_messages(self) -> Generator[dict[str, Any], Any, None]:
        """Consume messages from Kafka topic.

        Yields:
            Dict: Message data containing image information
        """
        if not self.consumer:
            logger.error("Consumer is not initialized")
            return

        logger.info("Starting to consume messages...")

        try:
            for message in self.consumer:
                message_data = {
                    "key": message.key,
                    "value": message.value,
                    "timestamp": message.timestamp,
                    "received_at": datetime.now().isoformat(),
                }

                logger.info(
                    f"Received message from partition {message.partition}, offset {message.offset}"
                )
                yield message_data

        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {e}")
        except KafkaError as e:
            logger.error(f"Kafka error while consuming messages: {e}")
        except Exception as e:
            logger.error(f"Unexpected error while consuming messages: {e}")

    def close(self) -> None:
        """Close the Kafka consumer."""
        if self.consumer:
            self.consumer.close()
            logger.info("Kafka consumer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()


if __name__ == "__main__":
    config = Config.from_env().kafka
    consumer = ImageConsumer(config)

    try:
        for message in consumer.consume_messages():
            logger.info(f"Consumed message: {message}")
    except KeyboardInterrupt:
        logger.info("Consumer stopped by user")
    finally:
        consumer.close()
        logger.info("Consumer closed")
