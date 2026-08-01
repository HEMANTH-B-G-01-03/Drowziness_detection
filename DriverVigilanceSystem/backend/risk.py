"""
risk.py
Combines multi-label CNN classification, facial landmark metrics
(EAR/MAR/head pose), and phone-detection results into a single 0-100
driver "risk score", plus a discrete status label and the list of
alerts to fire.

Because the CNN is now MULTI-LABEL (see cnn_model.py / train.py), more than
one class can be active at once (e.g. "distracted" AND "drowsy" together).
This module's CNN-risk contribution reflects that by summing weighted
contributions from every class that crosses its threshold, instead of only
looking at a single "winning" class.
"""

from Drowziness_detection.DriverVigilanceSystem.backend.landmarks import EAR_DROWSY_THRESHOLD, MAR_YAWN_THRESHOLD, HEAD_YAW_DISTRACTED_THRESHOLD

# Weights for each signal source (must sum to 1.0)
WEIGHTS = {
    "cnn": 0.45,
    "eye": 0.25,
    "head_pose": 0.15,
    "phone": 0.15,
}

# Risk points contributed per CNN class when it is active (probability
# above its threshold). "alert" intentionally contributes ~0 risk; it's
# only meaningful as the *absence* of the other two.
CNN_CLASS_RISK_WEIGHT = {
    "alert": 0,
    "distracted": 55,
    "drowsy": 85,
}

RISK_LEVELS = [
    (0, 30, "Safe"),
    (30, 60, "Caution"),
    (60, 85, "Warning"),
    (85, 101, "Critical"),
]


def classify_risk_level(score: float) -> str:
    for low, high, label in RISK_LEVELS:
        if low <= score < high:
            return label
    return "Unknown"


def compute_cnn_risk_score(cnn_prediction: dict) -> float:
    """
    cnn_prediction (multi-label) is expected to look like:
        {
          "active_classes": ["distracted", "drowsy"],   # classes above threshold
          "probs": {"alert": 0.04, "distracted": 0.81, "drowsy": 0.77},
        }

    Multiple simultaneously-active classes each contribute their own
    weighted risk, summed together (capped at 100) — this is what lets the
    system flag "distracted AND drowsy" as riskier than either alone.
    """
    probs = cnn_prediction.get("probs", {})
    if not probs:
        # Backward-compatible fallback for old single-label-style input:
        # {"class": "drowsy", "confidence": 0.9}
        cls = cnn_prediction.get("class", "alert")
        conf = cnn_prediction.get("confidence", 0.5)
        return CNN_CLASS_RISK_WEIGHT.get(cls, 20) * conf + 10 * (1 - conf)

    total = 0.0
    for cls, weight in CNN_CLASS_RISK_WEIGHT.items():
        prob = probs.get(cls, 0.0)
        total += weight * prob

    return min(total, 100.0)


def compute_risk_score(cnn_prediction: dict, landmark_result: dict, phone_result: dict) -> dict:
    """
    cnn_prediction: multi-label dict, see compute_cnn_risk_score() docstring.
    landmark_result: output of LandmarkDetector.process_frame()
    phone_result: output of PhoneDetector.detect_phone()
    """
    # ---- CNN component (handles multiple simultaneous classes) ----
    cnn_score = compute_cnn_risk_score(cnn_prediction)

    # ---- Eye (EAR) component ----
    eye_score = 0
    if landmark_result and landmark_result.get("face_found") and landmark_result.get("ear") is not None:
        ear = landmark_result["ear"]
        if ear < EAR_DROWSY_THRESHOLD:
            eye_score = min(100, (EAR_DROWSY_THRESHOLD - ear) / EAR_DROWSY_THRESHOLD * 200)
        mar = landmark_result.get("mar", 0)
        if mar and mar > MAR_YAWN_THRESHOLD:
            eye_score = max(eye_score, 60)  # yawning bumps risk
    elif landmark_result and not landmark_result.get("face_found"):
        eye_score = 40  # no face visible is itself a mild risk signal

    # ---- Head pose component ----
    head_score = 0
    if landmark_result and landmark_result.get("head_pose"):
        yaw = abs(landmark_result["head_pose"].get("yaw", 0))
        pitch = abs(landmark_result["head_pose"].get("pitch", 0))
        max_angle = max(yaw, pitch)
        if max_angle > HEAD_YAW_DISTRACTED_THRESHOLD:
            head_score = min(100, (max_angle - HEAD_YAW_DISTRACTED_THRESHOLD) * 2)

    # ---- Phone component ----
    phone_score = 0
    if phone_result and phone_result.get("phone_detected"):
        phone_score = 80 + 20 * phone_result.get("confidence", 0)
        phone_score = min(phone_score, 100)

    total_score = (
        WEIGHTS["cnn"] * cnn_score
        + WEIGHTS["eye"] * eye_score
        + WEIGHTS["head_pose"] * head_score
        + WEIGHTS["phone"] * phone_score
    )
    total_score = round(min(max(total_score, 0), 100), 2)
    level = classify_risk_level(total_score)

    # ---- Alerts: independent conditions, so multiple can fire together ----
    alerts_to_fire = []

    cnn_active = set(cnn_prediction.get("active_classes", []))
    if "drowsy" in cnn_active or eye_score >= 60:
        alerts_to_fire.append("drowsy")
    if "distracted" in cnn_active or head_score >= 50:
        alerts_to_fire.append("distracted")
    if phone_score >= 70:
        alerts_to_fire.append("phone")
    if total_score >= 85:
        alerts_to_fire.append("critical")

    return {
        "risk_score": total_score,
        "risk_level": level,
        "components": {
            "cnn_score": round(cnn_score, 2),
            "eye_score": round(eye_score, 2),
            "head_score": round(head_score, 2),
            "phone_score": round(phone_score, 2),
        },
        "alerts": alerts_to_fire,
    }