import base64
from io import BytesIO
from pathlib import Path

import cv2
import numpy as np
from loguru import logger
from PIL import Image
from ultralytics import YOLO

from infra.config import ModelConfig


class ProfessorDetector:
    """Professor detection using YOLO model."""

    def __init__(self, config: ModelConfig):
        """Initialize the professor detector.

        Args:
            config: Model configuration
        """
        self.config = config
        self.model = None
        self._load_model()

    def _load_model(self) -> None:
        """Load the YOLO model."""
        try:
            model_path = Path(self.config.model_path)
            if not model_path.exists():
                raise FileNotFoundError(f"Model file not found: {model_path}")

            self.model = YOLO(str(model_path))
            logger.info(f"Model loaded successfully from {model_path}")

        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            raise

    def _decode_base64_image(self, base64_string: str) -> np.ndarray:
        """Decode base64 string to OpenCV image format.

        Args:
            base64_string: Base64 encoded image string

        Returns:
            Image as numpy array in BGR format
        """
        try:
            # Remove data URL prefix if present
            if "," in base64_string:
                base64_string = base64_string.split(",")[1]

            # Decode base64 to bytes
            image_bytes = base64.b64decode(base64_string)

            # Convert bytes to PIL Image
            pil_image = Image.open(BytesIO(image_bytes))

            # Convert PIL to OpenCV format (RGB to BGR)
            cv_image = cv2.cvtColor(np.array(pil_image), cv2.COLOR_RGB2BGR)

            return cv_image

        except Exception as e:
            logger.error(f"Failed to decode base64 image: {e}")
            raise

    def _detect_professor(self, image: np.ndarray) -> bool:
        """Detect professor in the image.

        Args:
            image: Image as numpy array

        Returns:
            Tuple of (professor_detected, detections_list)
        """
        if self.model is None:
            logger.error("Model is not loaded")
            return False, []

        try:
            results = self.model(image, conf=self.config.confidence_threshold)
            professor_detected = False

            for result in results:
                if result.boxes is not None:
                    for box in result.boxes:
                        confidence = float(box.conf[0])
                        class_id = int(box.cls[0])
                        class_name = (
                            self.model.names[class_id]
                            if class_id < len(self.model.names)
                            else "unknown"
                        )

                        if (
                            "teacher" in class_name.lower()
                            and confidence >= self.config.confidence_threshold
                        ):
                            professor_detected = True

            return professor_detected

        except Exception as e:
            logger.error(f"Error during professor detection: {e}")
            return False, []

    def analyze_image_from_base64(self, base64_image: str) -> dict:
        """Analyze image from base64 string for professor detection.

        Args:
            base64_image: Base64 encoded image string

        Returns:
            Analysis result dictionary
        """
        try:
            image = self._decode_base64_image(base64_image)
            professor_detected = self._detect_professor(image)

            result = {
                "professor_detected": professor_detected,
                "image_shape": {
                    "height": image.shape[0],
                    "width": image.shape[1],
                    "channels": image.shape[2],
                },
            }

            return result

        except Exception as e:
            logger.error(f"Error analyzing image: {e}")
            return {}
