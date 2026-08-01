import cv2
import dlib
import numpy as np
import torch
import math
import time
import pygame
from scipy.spatial import distance as dist
import threading
import os
from ultralytics import YOLO

# ── colours (BGR) ──────────────────────────────────────────────────────────────
BLUE   = (255, 0,   0)
GREEN  = (0,   255, 0)
RED    = (0,   0,   255)
WHITE  = (255, 255, 255)
YELLOW = (0,   255, 255)   # cyan-yellow in BGR = (0,255,255)
BLUE_TEXT = (255, 0, 0)    # pure blue for Nose Aspect Ratio label

# ── audio ──────────────────────────────────────────────────────────────────────
pygame.mixer.init()

sounds = {
    'eye':     ('./eye_alert.mp3',   10),
    'look':    ('./look_ahead.mp3',  10),
    'rest':    ('./take_rest.mp3',   15),
    'phone':   ('./phone_alert.mp3', 15),
    'welcome': ('./welcomeengl.mp3',  0),
}
last_played = {key: 0 for key in sounds}


def play_sound(sound_key):
    try:
        audio_file, delay = sounds[sound_key]
        current_time = time.time()
        if current_time - last_played[sound_key] > delay:
            if os.path.exists(audio_file):
                print(f"Playing sound: {sound_key}")
                pygame.mixer.music.load(audio_file)
                pygame.mixer.music.play()
                last_played[sound_key] = current_time
            else:
                print(f"[ERROR] Audio file not found: {audio_file}")
    except Exception as e:
        print(f"[ERROR] Sound issue: {e}")


def sound_thread(sound_key):
    t = threading.Thread(target=play_sound, args=(sound_key,))
    t.daemon = True
    t.start()


# ── models ─────────────────────────────────────────────────────────────────────
print("[INFO] loading facial landmark predictor...")
detector  = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor('./shape_predictor_81_face_landmarks (1).dat')

print("[INFO] loading YOLO model...")
weights_path = os.path.abspath("weights/yolov5m.pt")
model  = YOLO(weights_path)
device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
model.to(device)

# ── 3-D head model ─────────────────────────────────────────────────────────────
model_points = np.array([
    (  0.0,    0.0,   0.0),   # nose tip
    (-30.0, -125.0, -30.0),   # left  eye corner
    ( 30.0, -125.0, -30.0),   # right eye corner
    (-60.0,  -70.0, -60.0),   # left  mouth corner
    ( 60.0,  -70.0, -60.0),   # right mouth corner
    (  0.0, -330.0, -65.0),   # chin
])


# ── geometry helpers ───────────────────────────────────────────────────────────
def isRotationMatrix(R):
    Rt = np.transpose(R)
    I  = np.identity(3, dtype=R.dtype)
    return np.linalg.norm(I - np.dot(Rt, R)) < 1e-6


def rotationMatrixToEulerAngles(R):
    assert isRotationMatrix(R)
    sy       = math.sqrt(R[0, 0] ** 2 + R[1, 0] ** 2)
    singular = sy < 1e-6
    if not singular:
        x = math.atan2(R[2, 1], R[2, 2])
        y = math.atan2(-R[2, 0], sy)
        z = math.atan2(R[1, 0], R[0, 0])
    else:
        x = math.atan2(-R[1, 2], R[1, 1])
        y = math.atan2(-R[2, 0], sy)
        z = 0
    return np.array([x, y, z])


def get_camera_matrix(size):
    focal_length = size[1]
    center       = (size[1] / 2, size[0] / 2)
    return np.array(
        [[focal_length, 0, center[0]],
         [0, focal_length, center[1]],
         [0, 0,            1        ]],
        dtype="double",
    )


def getHeadTiltAndCoords(size, image_points, frame_height):
    camera_matrix = get_camera_matrix(size)
    dist_coeffs   = np.zeros((4, 1))
    _, rotation_vector, translation_vector = cv2.solvePnP(
        model_points, image_points, camera_matrix, dist_coeffs,
        flags=cv2.SOLVEPNP_ITERATIVE,
    )
    nose_end_point2D, _ = cv2.projectPoints(
        np.array([(0.0, 0.0, 1000.0)]),
        rotation_vector, translation_vector, camera_matrix, dist_coeffs,
    )
    rotation_matrix, _ = cv2.Rodrigues(rotation_vector)
    head_tilt_degree   = abs(
        np.array([-180]) -
        np.rad2deg([rotationMatrixToEulerAngles(rotation_matrix)[0]])
    )
    starting_point      = (int(image_points[0][0]), int(image_points[0][1]))
    ending_point        = (int(nose_end_point2D[0][0][0]), int(nose_end_point2D[0][0][1]))
    ending_point_alternate = (ending_point[0], frame_height // 2)
    return head_tilt_degree, starting_point, ending_point, ending_point_alternate


def eye_aspect_ratio(eye):
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    return (A + B) / (2.0 * C)


def mouth_aspect_ratio(mouth):
    A = dist.euclidean(mouth[2],  mouth[10])
    B = dist.euclidean(mouth[4],  mouth[8])
    C = dist.euclidean(mouth[0],  mouth[6])
    return (A + B) / (2.0 * C)


def nose_aspect_ratio(nose):
    vertical_distance = dist.euclidean(nose[0], nose[2])
    depth_distance    = dist.euclidean(nose[0], nose[1])
    return depth_distance / vertical_distance


def calculate_head_angle(eye_left, eye_right, nose_tip):
    eye_center  = (eye_left + eye_right) / 2
    v_nose      = nose_tip - eye_center
    v_horiz     = (eye_right - eye_left).astype(float)
    v_horiz[1]  = 0
    v_n = v_nose  / np.linalg.norm(v_nose)
    v_h = v_horiz / np.linalg.norm(v_horiz)
    return np.degrees(np.arccos(np.clip(np.dot(v_n, v_h), -1.0, 1.0)))


# ── frame-level counters ───────────────────────────────────────────────────────
COUNTER1      = 0
COUNTER2      = 0
COUNTER3      = 0
repeat_counter = 0

sound_thread('welcome')


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN FUNCTION – drop-in replacement for the Flask integration
# ══════════════════════════════════════════════════════════════════════════════
def process_frame(img):
    """
    Processes a single BGR frame exactly like the raw cv2 loop does and
    returns (annotated_frame, status_data) for the Flask/frontend pipeline.

    Visual output matches the reference screenshot:
      • Blue  bounding-box  around detected face
      • White dots          on all 81 facial landmarks
      • White convexHull    around each eye
      • Green convexHull    around mouth
      • Red   line          nose → green head-direction line
      • Blue  line          nose → alternate end-point  (vertical)
      • Yellow text         EAR / MAR / Head Angle / Head Tilt  (top-left)
      • Blue  bold text     Nose Aspect Ratio                    (top-left)
      • Green box + label   if cell-phone detected
      • Red   alert text    above face for Eyes Closed / Yawning / Look Ahead
    """
    global COUNTER1, COUNTER2, COUNTER3, repeat_counter

    # default status sent back to the frontend
    status_data = {
        "alert":      "Normal",
        "risk":       10,
        "eye_status": "Alert",
        "phone":      "Not Detected",
    }

    gray  = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = detector(gray, 0)

    # ── no face detected ───────────────────────────────────────────────────────
    if len(faces) == 0:
        sound_thread("look")
        status_data["alert"] = "Look Ahead"

    # ── phone detection (YOLO) ─────────────────────────────────────────────────
    results    = model(img)
    detections = results[0].boxes.data
    for detection in detections:
        if int(detection[5]) == 67:          # class 67 = cell phone
            x1, y1, x2, y2 = (
                int(detection[0]), int(detection[1]),
                int(detection[2]), int(detection[3]),
            )
            conf = detection[4]

            # green bounding box + label  (matches raw cv2)
            cv2.rectangle(img, (x1, y1), (x2, y2), GREEN, 2)
            cv2.putText(
                img, f'Cell Phone {conf:.2f}',
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, GREEN, 2,
            )
            current_time = time.strftime('%H:%M:%S')
            print("driver is using cell phone", current_time)

            status_data["phone"] = "Detected"
            status_data["alert"] = "Phone Detected"
            status_data["risk"]  = 80

            COUNTER2 += 1
            if COUNTER2 >= 3:
                cv2.putText(
                    img, "Put away your phone!",
                    (x1, y1 - 30),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, RED, 2,
                )
                sound_thread("phone")
                COUNTER2 = 0

    # ── per-face processing ────────────────────────────────────────────────────
    for face in faces:
        landmarks        = predictor(gray, face)
        landmarks_points = np.array([(p.x, p.y) for p in landmarks.parts()])

        x, y, w, h = face.left(), face.top(), face.width(), face.height()

        # ── BLUE face bounding box ─────────────────────────────────────────────
        cv2.rectangle(img, (x, y), (x + w, y + h), BLUE, 2)

        # ── WHITE landmark dots ────────────────────────────────────────────────
        for point in landmarks_points:
            cv2.circle(img, (point[0], point[1]), 2, WHITE, -1)

        # ── eye regions & convexHull (WHITE) ──────────────────────────────────
        left_eye  = landmarks_points[36:42]
        right_eye = landmarks_points[42:48]
        cv2.drawContours(img, [cv2.convexHull(left_eye)],  -1, WHITE, 1)
        cv2.drawContours(img, [cv2.convexHull(right_eye)], -1, WHITE, 1)

        ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

        # ── mouth convexHull (GREEN) ───────────────────────────────────────────
        mouth = landmarks_points[48:68]
        cv2.drawContours(img, [cv2.convexHull(mouth)], -1, GREEN, 1)
        mar = mouth_aspect_ratio(mouth)

        # ── nose aspect ratio ──────────────────────────────────────────────────
        nose_points = [
            landmarks_points[27],
            landmarks_points[30],
            landmarks_points[33],
        ]
        nar = nose_aspect_ratio(nose_points)

        # ── head angle ────────────────────────────────────────────────────────
        eye_left  = landmarks_points[36]
        eye_right = landmarks_points[45]
        nose_tip  = landmarks_points[33]
        head_angle = calculate_head_angle(
            np.array(eye_left),
            np.array(eye_right),
            np.array(nose_tip),
        )

        # ── head tilt (solvePnP) ───────────────────────────────────────────────
        image_points = np.array([
            landmarks_points[30],  # nose tip
            landmarks_points[36],  # left  eye corner
            landmarks_points[45],  # right eye corner
            landmarks_points[48],  # left  mouth corner
            landmarks_points[54],  # right mouth corner
            landmarks_points[8],   # chin
        ], dtype="double")

        size         = img.shape
        frame_height = img.shape[0]
        head_tilt_degree, start_point, end_point, end_point_alt = \
            getHeadTiltAndCoords(size, image_points, frame_height)

        # ── on-screen metrics  (YELLOW text, matching reference image) ─────────
        # Row order from screenshot: EAR, MAR, Head Angle, [NAR in BLUE], Head Tilt
        cv2.putText(img, f'EAR: {ear:.2f}',
                    (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW, 2)
        cv2.putText(img, f'MAR: {mar:.2f}',
                    (10, 55), cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW, 2)
        cv2.putText(img, f'Head Angle: {head_angle:.2f}',
                    (10, 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW, 2)
        # Nose Aspect Ratio → BLUE bold text (matches screenshot)
        cv2.putText(img, f'Nose Aspect Ratio: {nar:.2f}',
                    (10, 105), cv2.FONT_HERSHEY_SIMPLEX, 0.7, BLUE_TEXT, 2)
        cv2.putText(img, f'Head Tilt: {head_tilt_degree[0]:.2f} degrees',
                    (10, 130), cv2.FONT_HERSHEY_SIMPLEX, 0.7, YELLOW, 2)

        # ── pose direction lines ───────────────────────────────────────────────
        # Green line  : nose → head-direction end-point
        cv2.line(img, start_point, end_point,     GREEN, 2)
        # Red line    : nose → alternate end-point (vertical guide)
        cv2.line(img, start_point, end_point_alt, RED,   2)
        # Blue line   : nose → alternate end-point (second pass, matches raw code)
        cv2.line(img, start_point, end_point_alt, BLUE,  2)

        # ── drowsiness / alert logic ───────────────────────────────────────────
        # Eyes closed
        if ear < 0.29:
            status_data["eye_status"] = "Drowsy"
            status_data["alert"]      = "Eyes Closed"
            status_data["risk"]       = 90
            cv2.putText(img, "Eyes Closed!",
                        (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 2)
            COUNTER1 += 1
            if COUNTER1 >= 4:
                sound_thread("eye")
                repeat_counter += 1
                COUNTER1 = 0
                if repeat_counter >= 3:
                    sound_thread("rest")
                    repeat_counter = 0
                    cv2.putText(img, "Eyes Closed 3 times!",
                                (x, y - 20), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 2)
        else:
            COUNTER1       = 0
            repeat_counter = 0

        # Yawning
        if mar > 0.6:
            status_data["alert"] = "Yawning"
            status_data["risk"]  = 70
            sound_thread("rest")
            cv2.putText(img, "Yawning!",
                        (x, y - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 2)

        # Head turned away
        if head_angle < 75 or head_angle > 110:
            status_data["alert"] = "Look Ahead"
            status_data["risk"]  = 60
            cv2.putText(img, "Look Ahead!",
                        (x, y - 80), cv2.FONT_HERSHEY_SIMPLEX, 0.7, RED, 2)
            COUNTER3 += 1
            if COUNTER3 >= 6:
                sound_thread("look")
                COUNTER3 = 0
        else:
            COUNTER3 = 0

    return img, status_data


# ── optional: run standalone (no Flask) for quick testing ─────────────────────
if __name__ == "__main__":
    print("[INFO] initializing camera...")
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FPS, 30)

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        annotated, status = process_frame(frame)
        cv2.imshow("Video Stream", annotated)
        print(status)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()