import signal
import sys
import time
from threading import Event

from camera import CameraCapture
from kafka_producer import CameraImageProducer
from loguru import logger

from infra.config import Config


class CameraService:
    """Main camera service class."""

    def __init__(self):
        """Initialize the camera service."""
        self.config = Config.from_env()
        self.running = Event()
        self.camera_capture = None
        self.kafka_producer = None

        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info(f"Received signal {signum}, shutting down gracefully...")
        self.running.clear()

    def start(self) -> None:
        """Start the camera service."""
        logger.info("Starting camera service...")

        try:
            self.camera_capture = CameraCapture(config=self.config.camera)
            self.kafka_producer = CameraImageProducer(
                kafka_config=self.config.kafka,
                camera_config=self.config.camera
            )

            # Start capture loop
            with self.camera_capture, self.kafka_producer:
                self.running.set()
                self._capture_loop()

        except Exception as e:
            logger.error(f"Failed to start camera service: {e}")
            sys.exit(1)
        finally:
            logger.info("Camera service stopped")

    def _capture_loop(self) -> None:
        """Main capture loop."""
        logger.info("Starting capture loop...")

        consecutive_failures = 0
        max_consecutive_failures = 5

        while self.running.is_set():
            try:
                encoded_image = self.camera_capture.capture_frame()

                if encoded_image is None:
                    consecutive_failures += 1
                    logger.warning(
                        f"Frame capture failed ({consecutive_failures}/{max_consecutive_failures})"
                    )

                    if consecutive_failures >= max_consecutive_failures:
                        logger.error(
                            "Too many consecutive capture failures, stopping service"
                        )
                        break

                    time.sleep(1)  # Wait before retrying
                    continue

                # Reset failure counter on successful capture
                consecutive_failures = 0
                success = self.kafka_producer.send_image_message(
                    encoded_image=encoded_image
                )

                if success:
                    logger.debug("Image captured and sent successfully")
                else:
                    logger.warning("Failed to send image to Kafka")

                # Wait for next capture
                time.sleep(self.config.camera.capture_interval)

            except KeyboardInterrupt:
                logger.info("Received keyboard interrupt, stopping...")
                break


def main() -> None:
    """Main entry point."""
    logger.info("Initializing UbiClass Camera Service...")

    service = CameraService()
    service.start()


if __name__ == "__main__":
    main()
