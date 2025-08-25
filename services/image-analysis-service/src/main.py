import signal
import sys

from loguru import logger
from datetime import datetime, UTC

from detection_producer import ProfessorDetectionProducer
from image_consumer import ImageConsumer
from infra.config import Config, DEFATULT_DATE_FORMAT
from infra.db_manager import MongoDBManager
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
        self.mongo_db_manager = None

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running = False

    def _prepare_kafka_message(self, final_result: bool) -> dict:
        detected_at = datetime.now(UTC).strftime(DEFATULT_DATE_FORMAT)
        result = self.mongo_db_manager.get_email_by_label("teacher")

        if not result:
            logger.error("No data found in the database")
            return {}

        return {
            "detectedAt": detected_at,
            "email": result["email"],
            "action": "enter" if final_result else "leave",
        }

    def process_image_message(self, message_data: dict) -> bool:
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

        if detection_result["professor_detected"]:
            logger.info(
                f"Successfully processed image. Professor detected: {detection_result.get('professor_detected', False)}"
            )
            return True
        else:
            logger.info("Professor not detected in the image")
            return False

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
            self.mongo_db_manager = MongoDBManager(config=self.config.mongo)

            detection_window = []
            window_size = 5

            with self.consumer, self.producer:
                for message_data in self.consumer.consume_messages():
                    if not self.running:
                        logger.info("Stopping service due to shutdown signal")
                        break

                    professor_detected = self.process_image_message(message_data=message_data)
                    detection_window.append(professor_detected)

                    # Keep window size fixed
                    if len(detection_window) > window_size:
                        detection_window.pop(0)

                    # Only act if window is full
                    if len(detection_window) == window_size:
                        detected_count = sum(detection_window)
                        leave_count = window_size - detected_count

                        # Send event only if all in window are same and last event was different
                        if detected_count == window_size:
                            message = self._prepare_kafka_message(final_result=True)
                            self.producer.send_detection_event(message)
                            detection_window.clear()
                        elif leave_count == window_size:
                            message = self._prepare_kafka_message(final_result=False)
                            self.producer.send_detection_event(message)
                            detection_window.clear()

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
