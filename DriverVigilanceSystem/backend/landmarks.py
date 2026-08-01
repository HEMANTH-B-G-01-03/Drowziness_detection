"""
landmarks.py
Facial landmark detection using dlib's 68-point predictor.

Computes:
    - EAR  (Eye Aspect Ratio)   -> used to detect eye closure / drowsiness
    - MAR  (Mouth Aspect Ratio) -> used to detect yawning
    - Head pose (pitch/yaw/roll approximation) -> used to detect head-down /
      distraction

Requires the pretrained dlib landmark model file:
    shape_predictor_68_face_landmarks.dat
Download from:
    http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
Place it in the backend/ directory (or update MODEL_PATH below).
"""

import os
import numpy as np
import cv2

try:
    import dlib
    DLIB_AVAILABLE = True
except ImportError:
    DLIB_AVAILABLE = False

MODEL_PATH = os.path.join(os.path.dirname(__file__), "shape_predictor_68_face_landmarks.dat")

# 68-point landmark indices (standard dlib scheme)
LEFT_EYE = list(range(36, 42))
RIGHT_EYE = list(range(42, 48))
MOUTH = list(range(48, 68))

# 3D model reference points for head pose estimation
MODEL_3D_POINTS = np.array([
    (0.0, 0.0, 0.0),          # Nose tip
    (0.0, -330.0, -65.0),     # Chin
    (-225.0, 170.0, -135.0),  # Left eye left corner
    (225.0, 170.0, -135.0),   # Right eye right corner
    (-150.0, -150.0, -125.0),  # Left mouth corner
    (150.0, -150.0, -125.0),  # Right mouth corner
], dtype="double")


class LandmarkDetector:
    def __init__(self, model_path: str = MODEL_PATH):
        if not DLIB_AVAILABLE:
            raise ImportError(
                "dlib is not installed. Run: pip install dlib"
            )
        if not os.path.exists(model_path):
            raise FileNotFoundError(
                f"Landmark model not found at {model_path}. "
                "Download shape_predictor_68_face_landmarks.dat from dlib.net "
                "and place it in the backend/ directory."
            )
        self.detector = dlib.get_frontal_face_detector()
        self.predictor = dlib.shape_predictor(model_path)

    @staticmethod
    def _shape_to_np(shape):
        coords = np.zeros((68, 2), dtype="int")
        for i in range(68):
            coords[i] = (shape.part(i).x, shape.part(i).y)
        return coords

    @staticmethod
    def eye_aspect_ratio(eye_points):
        """EAR = (|p2-p6| + |p3-p5|) / (2 * |p1-p4|)"""
        a = np.linalg.norm(eye_points[1] - eye_points[5])
        b = np.linalg.norm(eye_points[2] - eye_points[4])
        c = np.linalg.norm(eye_points[0] - eye_points[3])
        return (a + b) / (2.0 * c) if c != 0 else 0.0

    @staticmethod
    def mouth_aspect_ratio(mouth_points):
        """MAR based on vertical / horizontal mouth distances."""
        a = np.linalg.norm(mouth_points[2] - mouth_points[10])   # 51,59
        b = np.linalg.norm(mouth_points[4] - mouth_points[8])    # 53,57
        c = np.linalg.norm(mouth_points[0] - mouth_points[6])    # 48,54
        return (a + b) / (2.0 * c) if c != 0 else 0.0

    def estimate_head_pose(self, landmarks, frame_shape):
        """Rough head pose estimation using solvePnP."""
        image_points = np.array([
            landmarks[30],  # Nose tip
            landmarks[8],   # Chin
            landmarks[36],  # Left eye left corner
            landmarks[45],  # Right eye right corner
            landmarks[48],  # Left mouth corner
            landmarks[54],  # Right mouth corner
        ], dtype="double")

        h, w = frame_shape[:2]
        focal_length = w
        center = (w / 2, h / 2)
        camera_matrix = np.array([
            [focal_length, 0, center[0]],
            [0, focal_length, center[1]],
            [0, 0, 1],
        ], dtype="double")
        dist_coeffs = np.zeros((4, 1))

        success, rotation_vec, _ = cv2.solvePnP(
            MODEL_3D_POINTS, image_points, camera_matrix, dist_coeffs,
            flags=cv2.SOLVEPNP_ITERATIVE,
        )
        if not success:
            return {"pitch": 0.0, "yaw": 0.0, "roll": 0.0}

        rmat, _ = cv2.Rodrigues(rotation_vec)
        sy = np.sqrt(rmat[0, 0] ** 2 + rmat[1, 0] ** 2)
        pitch = np.degrees(np.arctan2(-rmat[2, 0], sy))
        yaw = np.degrees(np.arctan2(rmat[1, 0], rmat[0, 0]))
        roll = np.degrees(np.arctan2(rmat[2, 1], rmat[2, 2]))
        return {"pitch": float(pitch), "yaw": float(yaw), "roll": float(roll)}

    def process_frame(self, frame):
        """
        Returns a dict with EAR, MAR, head pose, and face-found flag
        for the largest detected face in the frame.
        """
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = self.detector(gray, 0)

        if len(faces) == 0:
            return {"face_found": False, "ear": None, "mar": None, "head_pose": None}

        face = max(faces, key=lambda r: r.width() * r.height())
        shape = self.predictor(gray, face)
        coords = self._shape_to_np(shape)

        left_ear = self.eye_aspect_ratio(coords[LEFT_EYE])
        right_ear = self.eye_aspect_ratio(coords[RIGHT_EYE])
        ear = (left_ear + right_ear) / 2.0

        mar = self.mouth_aspect_ratio(coords[MOUTH])
        head_pose = self.estimate_head_pose(coords, frame.shape)

        return {
            "face_found": True,
            "ear": round(float(ear), 4),
            "mar": round(float(mar), 4),
            "head_pose": head_pose,
            "landmarks": coords.tolist(),
        }


# Thresholds used elsewhere (risk.py) for interpreting EAR/MAR values
EAR_DROWSY_THRESHOLD = 0.22
MAR_YAWN_THRESHOLD = 0.6
HEAD_YAW_DISTRACTED_THRESHOLD = 25.0  # degrees
