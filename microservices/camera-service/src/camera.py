import base64
import io

import cv2
from loguru import logger
from PIL import Image

from infra.config import CameraConfig


class CameraCapture:
    """Handles camera capture operations."""

    def __init__(self, config: CameraConfig):
        """Initialize camera capture.

        Args:
            config: Camera configuration
        """
        self.config = config
        self.capture: cv2.VideoCapture | None = None
        self._initialize_camera()

    def _initialize_camera(self) -> None:
        """Initialize the camera."""
        try:
            self.capture = cv2.VideoCapture(self.config.camera_index)

            if not self.capture.isOpened():
                raise RuntimeError(f"Could not open camera {self.config.camera_index}")

            # Set camera resolution
            self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, self.config.image_width)
            self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, self.config.image_height)

            logger.info(f"Camera {self.config.camera_index} initialized successfully")

        except Exception as e:
            logger.error(f"Failed to initialize camera: {e}")
            raise

    def capture_frame(self) -> str | None:
        """Capture a frame from the camera.

        Returns:
            Tuple of (frame_array, base64_encoded_image) or None if capture failed
        """
        if not self.capture or not self.capture.isOpened():
            logger.error("Camera is not initialized or opened")
            return None

        try:
            frame_captured, frame = self.capture.read()

            if not frame_captured:
                logger.warning("Failed to capture frame")
                return None

            # Convert BGR to RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Convert to PIL Image for encoding
            pil_image = Image.fromarray(frame_rgb)

            # Encode to base64
            buffer = io.BytesIO()
            pil_image.save(buffer, format="JPEG", quality=self.config.image_quality)
            encoded_image = base64.b64encode(buffer.getvalue()).decode("utf-8")

            return encoded_image

        except Exception as e:
            logger.error(f"Error capturing frame: {e}")
            return None

    def release(self) -> None:
        """Release camera resources."""
        if self.capture:
            self.capture.release()
            logger.info("Camera resources released")

    def __enter__(self):
        """Context manager entry."""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.release()
