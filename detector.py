"""
detector.py — Wraps Roboflow inference to detect card labels from an image.
"""

import base64
import tempfile
import logging
import cv2
import numpy as np
from inference import get_model
import supervision as sv

from config import ROBOFLOW_API_KEY, ROBOFLOW_MODEL_ID

log = logging.getLogger(__name__)

# Load model once at startup so we don't re-init on every request
_model = None


def _get_model():
    global _model
    if _model is None:
        log.info(f"Loading Roboflow model: {ROBOFLOW_MODEL_ID}")
        _model = get_model(model_id=ROBOFLOW_MODEL_ID, api_key=ROBOFLOW_API_KEY)
    return _model


def detect_cards(image_b64: str) -> list[str]:
    """
    Decode a base64 JPEG, run Roboflow inference, return a list of
    card labels like ['As', 'Kd', '2h'].
    """
    # Decode base64 → numpy image
    img_bytes = base64.b64decode(image_b64)
    img_array = np.frombuffer(img_bytes, dtype=np.uint8)
    frame = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    if frame is None:
        raise ValueError("Could not decode image from base64 data")

    model = _get_model()
    results = model.infer(frame)[0]
    detections = sv.Detections.from_inference(results)

    cards = [results.predictions[i].class_name for i in range(len(detections))]

    # Deduplicate (same card detected twice from overlapping boxes)
    seen = set()
    unique = []
    for c in cards:
        if c not in seen:
            seen.add(c)
            unique.append(c)

    log.info(f"Detected {len(unique)} cards: {unique}")
    return unique
