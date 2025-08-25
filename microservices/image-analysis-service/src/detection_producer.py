import json
import time
from datetime import datetime, UTC

from loguru import logger

from kafka import KafkaProducer
from kafka.errors import KafkaError
from infra.config import KafkaConfig, DEFATULT_DATE_FORMAT, INTERVAL_BETWEEN_DETECTIONS


class ProfessorDetectionProducer:
    """Kafka producer for professor detection events."""

    def __init__(self, config: KafkaConfig):
        """Initialize the Kafka producer.

        Args:
            config: Kafka configuration
        """
        self.config = config
        self.producer = None
        self._initialize_producer()

    def _initialize_producer(self) -> None:
        """Initialize the Kafka producer."""
        try:
            self.producer = KafkaProducer(
                bootstrap_servers=self.config.bootstrap_servers,
                value_serializer=lambda v: json.dumps(v).encode("utf-8"),
                key_serializer=lambda k: k.encode("utf-8") if k else None,
                acks="all",  # Wait for all replicas to acknowledge
                retries=3,  # Retry failed sends
                retry_backoff_ms=300,
                max_in_flight_requests_per_connection=1,  # Ensure ordering
            )
            logger.info("Professor detection producer initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize Kafka producer: {e}")
            raise

    def send_detection_event(self, message: dict) -> None:
        """Send professor detection event to Kafka topic."""
        if not self.producer:
            logger.error("Producer is not initialized")
            return False
        
        if not message:
            logger.error("Empty message, not sending to Kafka")
            return False

        try:
            key = datetime.now(UTC).strftime(DEFATULT_DATE_FORMAT)

            future = self.producer.send(
                topic=self.config.topic_professor_detection, key=key, value=message
            )

            # Wait for the message to be sent
            record_metadata = future.get(timeout=10)

            logger.info(
                f"Detection event sent successfully to topic '{record_metadata.topic}'"
            )

            time.sleep(INTERVAL_BETWEEN_DETECTIONS)  # Throttle sending

        except KafkaError as e:
            logger.error(f"Kafka error while sending detection event: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error while sending detection event: {e}")
            return False

    def close(self) -> None:
        """Close the Kafka producer."""
        if self.producer:
            self.producer.flush()  # Ensure all messages are sent
            self.producer.close()
            logger.info("Professor detection producer closed")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
