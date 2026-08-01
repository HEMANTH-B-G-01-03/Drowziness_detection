# """
# app.py
# Flask server that:
#   1. Captures webcam frames (server-side OpenCV capture) OR accepts frames
#      posted from the frontend as base64 JPEG.
#   2. Runs the CNN classifier + facial landmark analysis + YOLO phone
#      detection on each frame.
#   3. Computes a combined risk score and triggers audio alerts.
#   4. Streams results back to the React frontend as JSON (REST) and via a
#      raw MJPEG endpoint for the live video feed.

# Run:
#     python app.py
# Server starts on http://localhost:5000
# """

# import base64
# import io
# import threading
# import time

# import cv2
# import numpy as np
# import torch
# from flask import Flask, Response, jsonify, request
# from flask_cors import CORS
# from torchvision import transforms

# from cnn_model import DriverVigilanceCNN, CLASS_NAMES, CLASS_THRESHOLDS
# from risk import compute_risk_score
# from alerts import get_alert_manager

# app = Flask(__name__)
# CORS(app)

# DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# MODEL_PATH = "../models/cnn_driver.pth"

# # ---------------------------------------------------------------------------
# # Model loading (CNN). Landmark detector / phone detector are optional and
# # loaded lazily so the server still starts even without dlib model files or
# # YOLO weights present (useful for first-run / demo purposes).
# # ---------------------------------------------------------------------------
# cnn_model = None
# cnn_thresholds = CLASS_THRESHOLDS  # overwritten with checkpoint's saved thresholds if present
# landmark_detector = None
# phone_detector = None
# alert_manager = None

# eval_transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor(),
#     transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
# ])


# def load_cnn_model():
#     global cnn_model, cnn_thresholds
#     try:
#         checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
#         classes = checkpoint.get("classes", CLASS_NAMES)
#         model = DriverVigilanceCNN(num_classes=len(classes)).to(DEVICE)
#         model.load_state_dict(checkpoint["model_state_dict"])
#         model.eval()
#         cnn_model = model
#         cnn_thresholds = checkpoint.get("thresholds", CLASS_THRESHOLDS)
#         print(f"[app] Loaded CNN model from {MODEL_PATH} "
#               f"(multi_label={checkpoint.get('multi_label', False)})")
#     except Exception as e:
#         print(f"[app] WARNING: could not load trained model ({e}). "
#               f"Using an untrained model for demo purposes. Run train.py first.")
#         cnn_model = DriverVigilanceCNN(num_classes=len(CLASS_NAMES)).to(DEVICE)
#         cnn_model.eval()
#         cnn_thresholds = CLASS_THRESHOLDS


# def load_landmark_detector():
#     global landmark_detector
#     try:
#         from landmarks import LandmarkDetector
#         landmark_detector = LandmarkDetector()
#         print("[app] Landmark detector ready.")
#     except Exception as e:
#         print(f"[app] Landmark detector unavailable: {e}")
#         landmark_detector = None


# def load_phone_detector():
#     global phone_detector
#     try:
#         from yolo_phone import get_phone_detector
#         phone_detector = get_phone_detector()
#         print("[app] Phone detector ready.")
#     except Exception as e:
#         print(f"[app] Phone detector unavailable: {e}")
#         phone_detector = None


# def load_alert_manager():
#     global alert_manager
#     try:
#         alert_manager = get_alert_manager()
#         print("[app] Alert manager ready.")
#     except Exception as e:
#         print(f"[app] Alert manager unavailable (no audio device?): {e}")
#         alert_manager = None


# load_cnn_model()
# load_landmark_detector()
# load_phone_detector()
# load_alert_manager()

# # ---------------------------------------------------------------------------
# # Webcam capture (server-side). Runs in a background thread so /video_feed
# # can stream MJPEG while /api/status returns the latest analysis as JSON.
# # ---------------------------------------------------------------------------
# camera = None
# latest_frame = None
# latest_result = {"status": "initializing"}
# capture_lock = threading.Lock()
# running = False


# def classify_frame(frame_bgr):
#     """
#     Runs the multi-label CNN on a single BGR OpenCV frame.

#     Returns independent per-class probabilities (each 0-1, NOT summing to 1)
#     plus the list of classes currently above their decision threshold, so
#     multiple states (e.g. "distracted" AND "drowsy") can be reported at once
#     instead of forcing a single winning class.
#     """
#     rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
#     tensor = eval_transform(torch.from_numpy(rgb).permute(2, 0, 1).float() / 255.0)
#     tensor = tensor.unsqueeze(0).to(DEVICE)

#     with torch.no_grad():
#         logits = cnn_model(tensor)
#         probs = torch.sigmoid(logits)[0].cpu().numpy()

#     probs_dict = {CLASS_NAMES[i]: float(p) for i, p in enumerate(probs)}
#     active_classes = [
#         cls for cls, p in probs_dict.items() if p >= cnn_thresholds.get(cls, 0.5)
#     ]

#     # Convenience "primary" class for any UI that still wants a single label
#     # to headline (defaults to the highest-probability class).
#     primary_idx = int(np.argmax(probs))
#     primary_class = CLASS_NAMES[primary_idx] if primary_idx < len(CLASS_NAMES) else "unknown"

#     return {
#         "class": primary_class,                 # backward-compatible single-label field
#         "confidence": float(probs[primary_idx]),
#         "probs": probs_dict,                     # independent, per-class probabilities
#         "active_classes": active_classes,        # NEW: can contain more than one class
#     }


# def analyze_frame(frame_bgr):
#     """Runs the full pipeline (CNN + landmarks + phone) on one frame."""
#     cnn_pred = classify_frame(frame_bgr)

#     landmark_result = None
#     if landmark_detector is not None:
#         try:
#             landmark_result = landmark_detector.process_frame(frame_bgr)
#         except Exception as e:
#             landmark_result = {"face_found": False, "error": str(e)}

#     phone_result = None
#     if phone_detector is not None:
#         try:
#             phone_result = phone_detector.detect_phone(frame_bgr)
#         except Exception as e:
#             phone_result = {"phone_detected": False, "error": str(e)}

#     risk_result = compute_risk_score(cnn_pred, landmark_result or {}, phone_result or {})

#     # Fire audio alerts (best-effort; ignored if no audio device present)
#     if alert_manager is not None:
#         for alert_type in risk_result["alerts"]:
#             alert_manager.play(alert_type)

#     return {
#         "timestamp": time.time(),
#         "cnn_prediction": cnn_pred,
#         "landmarks": {
#             "face_found": (landmark_result or {}).get("face_found", False),
#             "ear": (landmark_result or {}).get("ear"),
#             "mar": (landmark_result or {}).get("mar"),
#             "head_pose": (landmark_result or {}).get("head_pose"),
#         },
#         "phone_detection": {
#             "phone_detected": (phone_result or {}).get("phone_detected", False),
#             "confidence": (phone_result or {}).get("confidence", 0.0),
#         },
#         "risk": risk_result,
#     }


# def capture_loop(source=0):
#     """Background thread: continuously grabs frames + runs analysis."""
#     global camera, latest_frame, latest_result, running
#     camera = cv2.VideoCapture(source)
#     running = True

#     while running:
#         success, frame = camera.read()
#         if not success:
#             time.sleep(0.1)
#             continue

#         with capture_lock:
#             latest_frame = frame.copy()

#         try:
#             result = analyze_frame(frame)
#             with capture_lock:
#                 latest_result = result
#         except Exception as e:
#             with capture_lock:
#                 latest_result = {"error": str(e), "timestamp": time.time()}

#         time.sleep(0.05)  # ~20 FPS cap for inference loop

#     camera.release()


# def gen_mjpeg():
#     while True:
#         with capture_lock:
#             frame = latest_frame.copy() if latest_frame is not None else None
#         if frame is None:
#             time.sleep(0.1)
#             continue
#         ok, buffer = cv2.imencode(".jpg", frame)
#         if not ok:
#             continue
#         yield (b"--frame\r\n"
#                b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


# # ---------------------------------------------------------------------------
# # REST API routes
# # ---------------------------------------------------------------------------

# @app.route("/api/start", methods=["POST"])
# def start_capture():
#     global running
#     if running:
#         return jsonify({"message": "Capture already running"}), 200
#     source = request.json.get("source", 0) if request.is_json else 0
#     thread = threading.Thread(target=capture_loop, args=(source,), daemon=True)
#     thread.start()
#     return jsonify({"message": "Capture started"}), 200


# @app.route("/api/stop", methods=["POST"])
# def stop_capture():
#     global running
#     running = False
#     return jsonify({"message": "Capture stopped"}), 200


# @app.route("/api/status", methods=["GET"])
# def get_status():
#     with capture_lock:
#         return jsonify(latest_result)


# @app.route("/api/analyze_frame", methods=["POST"])
# def analyze_uploaded_frame():
#     """
#     Accepts a base64-encoded JPEG frame from the frontend (e.g., captured via
#     the browser's webcam using <video>/<canvas>) and returns the analysis
#     JSON directly, without needing server-side camera access.

#     Expected JSON body: { "image": "data:image/jpeg;base64,...." }
#     """
#     data = request.get_json(force=True)
#     image_b64 = data.get("image", "")
#     if "," in image_b64:
#         image_b64 = image_b64.split(",", 1)[1]

#     img_bytes = base64.b64decode(image_b64)
#     np_arr = np.frombuffer(img_bytes, np.uint8)
#     frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

#     if frame is None:
#         return jsonify({"error": "Could not decode image"}), 400

#     result = analyze_frame(frame)
#     return jsonify(result)


# @app.route("/video_feed")
# def video_feed():
#     return Response(gen_mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame")


# @app.route("/api/health", methods=["GET"])
# def health():
#     return jsonify({
#         "status": "ok",
#         "model_loaded": cnn_model is not None,
#         "landmark_detector_loaded": landmark_detector is not None,
#         "phone_detector_loaded": phone_detector is not None,
#         "device": str(DEVICE),
#     })


# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)


"""
app.py
Flask server that:
  1. Captures webcam frames (server-side OpenCV capture) OR accepts frames
     posted from the frontend as base64 JPEG.
  2. Runs the CNN classifier + facial landmark analysis + YOLO phone
     detection on each frame.
  3. Computes a combined risk score and triggers audio alerts.
  4. Streams results back to the React frontend as JSON (REST) and via a
     raw MJPEG endpoint for the live video feed.

Run:
    python app.py
Server starts on http://localhost:5000
"""

import base64
import io
import threading
import time

import cv2
import numpy as np
import torch
from PIL import Image
from flask import Flask, Response, jsonify, request
from flask_cors import CORS
from torchvision import transforms

from cnn_model import DriverVigilanceCNN, CLASS_NAMES, CLASS_THRESHOLDS
from Drowziness_detection.DriverVigilanceSystem.backend.risk import compute_risk_score
from Drowziness_detection.DriverVigilanceSystem.backend.alerts import get_alert_manager

app = Flask(__name__)
CORS(app)

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
MODEL_PATH = "../models/cnn_driver.pth"

# ---------------------------------------------------------------------------
# Model loading (CNN). Landmark detector / phone detector are optional and
# loaded lazily so the server still starts even without dlib model files or
# YOLO weights present (useful for first-run / demo purposes).
# ---------------------------------------------------------------------------
cnn_model = None
cnn_thresholds = CLASS_THRESHOLDS  # overwritten with checkpoint's saved thresholds if present
landmark_detector = None
phone_detector = None
alert_manager = None

eval_transform = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
])


def load_cnn_model():
    global cnn_model, cnn_thresholds
    try:
        checkpoint = torch.load(MODEL_PATH, map_location=DEVICE)
        classes = checkpoint.get("classes", CLASS_NAMES)
        model = DriverVigilanceCNN(num_classes=len(classes)).to(DEVICE)
        model.load_state_dict(checkpoint["model_state_dict"])
        model.eval()
        cnn_model = model
        cnn_thresholds = checkpoint.get("thresholds", CLASS_THRESHOLDS)
        print(f"[app] Loaded CNN model from {MODEL_PATH} "
              f"(multi_label={checkpoint.get('multi_label', False)})")
    except Exception as e:
        print(f"[app] WARNING: could not load trained model ({e}). "
              f"Using an untrained model for demo purposes. Run train.py first.")
        cnn_model = DriverVigilanceCNN(num_classes=len(CLASS_NAMES)).to(DEVICE)
        cnn_model.eval()
        cnn_thresholds = CLASS_THRESHOLDS


def load_landmark_detector():
    global landmark_detector
    try:
        from Drowziness_detection.DriverVigilanceSystem.backend.landmarks import LandmarkDetector
        landmark_detector = LandmarkDetector()
        print("[app] Landmark detector ready.")
    except Exception as e:
        print(f"[app] Landmark detector unavailable: {e}")
        landmark_detector = None


def load_phone_detector():
    global phone_detector
    try:
        from Drowziness_detection.DriverVigilanceSystem.backend.yolo_phone import get_phone_detector
        phone_detector = get_phone_detector()
        print("[app] Phone detector ready.")
    except Exception as e:
        print(f"[app] Phone detector unavailable: {e}")
        phone_detector = None


def load_alert_manager():
    global alert_manager
    try:
        alert_manager = get_alert_manager()
        print("[app] Alert manager ready.")
    except Exception as e:
        print(f"[app] Alert manager unavailable (no audio device?): {e}")
        alert_manager = None


load_cnn_model()
load_landmark_detector()
load_phone_detector()
load_alert_manager()

# ---------------------------------------------------------------------------
# Webcam capture (server-side). Runs in a background thread so /video_feed
# can stream MJPEG while /api/status returns the latest analysis as JSON.
# ---------------------------------------------------------------------------
camera = None
latest_frame = None
latest_result = {"status": "initializing"}
capture_lock = threading.Lock()
running = False


def classify_frame(frame_bgr):
    """
    Runs the multi-label CNN on a single BGR OpenCV frame.

    Returns independent per-class probabilities (each 0-1, NOT summing to 1)
    plus the list of classes currently above their decision threshold, so
    multiple states (e.g. "distracted" AND "drowsy") can be reported at once
    instead of forcing a single winning class.
    """
    rgb = cv2.cvtColor(frame_bgr, cv2.COLOR_BGR2RGB)
    pil_image = Image.fromarray(rgb)  # eval_transform (Resize -> ToTensor -> Normalize)
    tensor = eval_transform(pil_image)  # expects a PIL Image / ndarray, NOT a Tensor
    tensor = tensor.unsqueeze(0).to(DEVICE)

    with torch.no_grad():
        logits = cnn_model(tensor)
        probs = torch.sigmoid(logits)[0].cpu().numpy()

    probs_dict = {CLASS_NAMES[i]: float(p) for i, p in enumerate(probs)}
    active_classes = [
        cls for cls, p in probs_dict.items() if p >= cnn_thresholds.get(cls, 0.5)
    ]

    # Convenience "primary" class for any UI that still wants a single label
    # to headline (defaults to the highest-probability class).
    primary_idx = int(np.argmax(probs))
    primary_class = CLASS_NAMES[primary_idx] if primary_idx < len(CLASS_NAMES) else "unknown"

    return {
        "class": primary_class,                 # backward-compatible single-label field
        "confidence": float(probs[primary_idx]),
        "probs": probs_dict,                     # independent, per-class probabilities
        "active_classes": active_classes,        # NEW: can contain more than one class
    }


def analyze_frame(frame_bgr):
    """Runs the full pipeline (CNN + landmarks + phone) on one frame."""
    cnn_pred = classify_frame(frame_bgr)

    landmark_result = None
    if landmark_detector is not None:
        try:
            landmark_result = landmark_detector.process_frame(frame_bgr)
        except Exception as e:
            landmark_result = {"face_found": False, "error": str(e)}

    phone_result = None
    if phone_detector is not None:
        try:
            phone_result = phone_detector.detect_phone(frame_bgr)
        except Exception as e:
            phone_result = {"phone_detected": False, "error": str(e)}

    risk_result = compute_risk_score(cnn_pred, landmark_result or {}, phone_result or {})

    # Fire audio alerts (best-effort; ignored if no audio device present)
    if alert_manager is not None:
        for alert_type in risk_result["alerts"]:
            alert_manager.play(alert_type)

    return {
        "timestamp": time.time(),
        "cnn_prediction": cnn_pred,
        "landmarks": {
            "face_found": (landmark_result or {}).get("face_found", False),
            "ear": (landmark_result or {}).get("ear"),
            "mar": (landmark_result or {}).get("mar"),
            "head_pose": (landmark_result or {}).get("head_pose"),
        },
        "phone_detection": {
            "phone_detected": (phone_result or {}).get("phone_detected", False),
            "confidence": (phone_result or {}).get("confidence", 0.0),
        },
        "risk": risk_result,
    }


def capture_loop(source=0):
    """Background thread: continuously grabs frames + runs analysis."""
    global camera, latest_frame, latest_result, running
    camera = cv2.VideoCapture(source)
    running = True

    while running:
        success, frame = camera.read()
        if not success:
            time.sleep(0.1)
            continue

        with capture_lock:
            latest_frame = frame.copy()

        try:
            result = analyze_frame(frame)
            with capture_lock:
                latest_result = result
        except Exception as e:
            print(f"[app] ERROR during frame analysis: {e}")
            with capture_lock:
                latest_result = {"error": str(e), "timestamp": time.time()}

        time.sleep(0.05)  # ~20 FPS cap for inference loop

    camera.release()


def gen_mjpeg():
    while True:
        with capture_lock:
            frame = latest_frame.copy() if latest_frame is not None else None
        if frame is None:
            time.sleep(0.1)
            continue
        ok, buffer = cv2.imencode(".jpg", frame)
        if not ok:
            continue
        yield (b"--frame\r\n"
               b"Content-Type: image/jpeg\r\n\r\n" + buffer.tobytes() + b"\r\n")


# ---------------------------------------------------------------------------
# REST API routes
# ---------------------------------------------------------------------------

@app.route("/api/start", methods=["POST"])
def start_capture():
    global running
    if running:
        return jsonify({"message": "Capture already running"}), 200
    source = request.json.get("source", 0) if request.is_json else 0
    thread = threading.Thread(target=capture_loop, args=(source,), daemon=True)
    thread.start()
    return jsonify({"message": "Capture started"}), 200


@app.route("/api/stop", methods=["POST"])
def stop_capture():
    global running
    running = False
    return jsonify({"message": "Capture stopped"}), 200


@app.route("/api/status", methods=["GET"])
def get_status():
    with capture_lock:
        return jsonify(latest_result)


@app.route("/api/analyze_frame", methods=["POST"])
def analyze_uploaded_frame():
    """
    Accepts a base64-encoded JPEG frame from the frontend (e.g., captured via
    the browser's webcam using <video>/<canvas>) and returns the analysis
    JSON directly, without needing server-side camera access.

    Expected JSON body: { "image": "data:image/jpeg;base64,...." }
    """
    data = request.get_json(force=True)
    image_b64 = data.get("image", "")
    if "," in image_b64:
        image_b64 = image_b64.split(",", 1)[1]

    img_bytes = base64.b64decode(image_b64)
    np_arr = np.frombuffer(img_bytes, np.uint8)
    frame = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)

    if frame is None:
        return jsonify({"error": "Could not decode image"}), 400

    result = analyze_frame(frame)
    return jsonify(result)


@app.route("/video_feed")
def video_feed():
    return Response(gen_mjpeg(), mimetype="multipart/x-mixed-replace; boundary=frame")


@app.route("/api/health", methods=["GET"])
def health():
    return jsonify({
        "status": "ok",
        "model_loaded": cnn_model is not None,
        "landmark_detector_loaded": landmark_detector is not None,
        "phone_detector_loaded": phone_detector is not None,
        "device": str(DEVICE),
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)