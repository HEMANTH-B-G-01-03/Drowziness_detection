# """
# yolo_phone.py
# Uses a YOLO object-detection model (via the `ultralytics` package) to detect
# if the driver is holding/using a mobile phone.

# Requires:
#     pip install ultralytics

# The default pretrained YOLOv8n (COCO) model already includes a "cell phone"
# class (COCO class id 67), so no custom training is strictly required to get
# started. For production use, fine-tune YOLO on a driver-specific phone-usage
# dataset for better accuracy.
# """

# import os

# try:
#     from ultralytics import YOLO
#     ULTRALYTICS_AVAILABLE = True
# except ImportError:
#     ULTRALYTICS_AVAILABLE = False

# COCO_PHONE_CLASS_ID = 67  # "cell phone" in the standard COCO label set
# DEFAULT_WEIGHTS = os.environ.get("YOLO_WEIGHTS", "yolov8n.pt")


# class PhoneDetector:
#     def __init__(self, weights_path: str = DEFAULT_WEIGHTS, conf_threshold: float = 0.4):
#         if not ULTRALYTICS_AVAILABLE:
#             raise ImportError(
#                 "ultralytics is not installed. Run: pip install ultralytics"
#             )
#         self.model = YOLO(weights_path)
#         self.conf_threshold = conf_threshold

#     def detect_phone(self, frame):
#         """
#         Runs YOLO inference on a single BGR frame (numpy array).
#         Returns dict: { phone_detected: bool, confidence: float, boxes: [...] }
#         """
#         results = self.model.predict(source=frame, verbose=False, conf=self.conf_threshold)

#         phone_detected = False
#         best_conf = 0.0
#         boxes = []

#         for result in results:
#             for box in result.boxes:
#                 cls_id = int(box.cls[0])
#                 conf = float(box.conf[0])
#                 if cls_id == COCO_PHONE_CLASS_ID:
#                     phone_detected = True
#                     best_conf = max(best_conf, conf)
#                     xyxy = box.xyxy[0].tolist()
#                     boxes.append({"bbox": xyxy, "confidence": conf})

#         return {
#             "phone_detected": phone_detected,
#             "confidence": round(best_conf, 4),
#             "boxes": boxes,
#         }


# class MockPhoneDetector:
#     """
#     Fallback detector used when `ultralytics`/YOLO weights are unavailable
#     (e.g., quick local demo without downloading model weights). Always
#     reports no phone detected so the rest of the pipeline still runs.
#     """

#     def detect_phone(self, frame):
#         return {"phone_detected": False, "confidence": 0.0, "boxes": []}


# def get_phone_detector():
#     """Factory that gracefully falls back to a mock detector if YOLO/ultralytics
#     isn't available in the current environment."""
#     try:
#         return PhoneDetector()
#     except Exception as e:
#         print(f"[yolo_phone] Falling back to MockPhoneDetector: {e}")
#         return MockPhoneDetector()


"""
yolo_phone.py
Uses a YOLO object-detection model (via the `ultralytics` package) to detect
if the driver is holding/using a mobile phone.

Requires:
    pip install ultralytics

The default pretrained YOLOv8n (COCO) model already includes a "cell phone"
class (COCO class id 67), so no custom training is strictly required to get
started. For production use, fine-tune YOLO on a driver-specific phone-usage
dataset for better accuracy.
"""

import os

try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

COCO_PHONE_CLASS_ID = 67  # "cell phone" in the standard COCO label set
DEFAULT_WEIGHTS = os.environ.get("YOLO_WEIGHTS", "yolov8n.pt")


class PhoneDetector:
    def __init__(self, weights_path: str = DEFAULT_WEIGHTS, conf_threshold: float = 0.4):
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError(
                "ultralytics is not installed. Run: pip install ultralytics"
            )
        self.model = YOLO(weights_path)
        self.conf_threshold = conf_threshold

    def detect_phone(self, frame):
        """
        Runs YOLO inference on a single BGR frame (numpy array).
        Returns dict: { phone_detected: bool, confidence: float, boxes: [...] }
        """
        results = self.model.predict(source=frame, verbose=False, conf=self.conf_threshold)

        phone_detected = False
        best_conf = 0.0
        boxes = []

        for result in results:
            for box in result.boxes:
                cls_id = int(box.cls[0])
                conf = float(box.conf[0])
                if cls_id == COCO_PHONE_CLASS_ID:
                    phone_detected = True
                    best_conf = max(best_conf, conf)
                    xyxy = box.xyxy[0].tolist()
                    boxes.append({"bbox": xyxy, "confidence": conf})

        return {
            "phone_detected": phone_detected,
            "confidence": round(best_conf, 4),
            "boxes": boxes,
        }


class MockPhoneDetector:
    """
    Fallback detector used when `ultralytics`/YOLO weights are unavailable
    (e.g., quick local demo without downloading model weights). Always
    reports no phone detected so the rest of the pipeline still runs.
    """

    def detect_phone(self, frame):
        return {"phone_detected": False, "confidence": 0.0, "boxes": []}


def get_phone_detector():
    """Factory that gracefully falls back to a mock detector if YOLO/ultralytics
    isn't available in the current environment."""
    try:
        return PhoneDetector()
    except Exception as e:
        print(f"[yolo_phone] Falling back to MockPhoneDetector: {e}")
        return MockPhoneDetector()