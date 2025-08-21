import signal
import sys

from loguru import logger

from detection_producer import ProfessorDetectionProducer
from image_consumer import ImageConsumer
from infra.config import Config
from professor_detector import ProfessorDetector


class ImageAnalysisService:
    """Main service for analyzing images and detecting professor presence."""

    def __init__(self):
        """Initialize the image analysis service."""
        self.config = Config.from_env()
        self.running = False
        self.detector = None
        self.consumer = None
        self.producer = None

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def process_image_message(self, message_data: dict) -> None:
        """Process a single image message.

        Args:
            message_data: Message data from Kafka consumer
        """
        message_value = message_data.get("value", {})

        if "image_data" not in message_value:
            logger.warning("Message does not contain image_data field")
            return

        base64_image = message_value["image_data"]
        camera_id = message_value.get("camera_index", "unknown")

        logger.info(
            f"Processing image from camera {camera_id}"
        )

        detection_result = self.detector.analyze_image_from_base64(base64_image)

        # Send detection event to Kafka
        success = self.producer.send_detection_event(
            detection_data=detection_result,
            original_message_key=message_data.get("key"),
        )

        if success:
            logger.info(
                f"Successfully processed image. Professor detected: {detection_result.get('professor_detected', False)}"
            )
        else:
            logger.error("Failed to send detection event to Kafka")

    def run(self) -> None:
        """Run the image analysis service."""
        logger.info("Starting Image Analysis Service...")
        logger.info(f"Consuming from topic: {self.config.kafka.topic_camera_images}")
        logger.info(
            f"Publishing to topic: {self.config.kafka.topic_professor_detection}"
        )
        logger.info(f"Model path: {self.config.model.model_path}")
        logger.info(f"Confidence threshold: {self.config.model.confidence_threshold}")

        self.running = True

        try:
            # Initialize components
            self.detector = ProfessorDetector(config=self.config.model)
            self.consumer = ImageConsumer(config=self.config.kafka)
            self.producer = ProfessorDetectionProducer(config=self.config.kafka)

            with self.consumer, self.producer:
                for message_data in self.consumer.consume_messages():
                    if not self.running:
                        logger.info("Stopping service due to shutdown signal")
                        break

                    self.process_image_message(message_data=message_data)

        except KeyboardInterrupt:
            logger.info("Service interrupted by user")
        except Exception as e:
            logger.error(f"Failed to start Image Analysis Service: {e}")
            sys.exit(1)
        finally:
            logger.info("Image Analysis Service stopped")


def main():
    """Main entry point for the application."""

    service = ImageAnalysisService()
    service.run()


if __name__ == "__main__":
    main()
