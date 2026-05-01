
# # import torch
# # import cv2
# # import numpy as np
# # from torchvision import transforms, models
# # import torch.nn as nn

# # # 🏷️ Classes (IMPORTANT - SAME ORDER)
# # class_names = ['alert', 'distracted', 'drowsy']

# # # 🧠 Load Model
# # model = models.mobilenet_v2(pretrained=False)
# # model.classifier[1] = nn.Linear(model.last_channel, len(class_names))
# # model.load_state_dict(torch.load("driver_model.pth"))
# # model.eval()

# # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# # model = model.to(device)

# # # 🔄 Transform
# # transform = transforms.Compose([
# #     transforms.ToPILImage(),
# #     transforms.Resize((224, 224)),
# #     transforms.ToTensor()
# # ])

# # # 🎥 Camera
# # cap = cv2.VideoCapture(0)

# # while True:
# #     ret, frame = cap.read()
# #     if not ret:
# #         break

# #     img = transform(frame).unsqueeze(0).to(device)

# #     with torch.no_grad():
# #         outputs = model(img)
# #         _, pred = torch.max(outputs, 1)

# #     label = class_names[pred.item()]

# #     # 📢 Display
# #     cv2.putText(frame, f"{label}", (50, 50),
# #                 cv2.FONT_HERSHEY_SIMPLEX, 1,
# #                 (0, 0, 255), 2)

# #     cv2.imshow("AI Driver Monitor", frame)

# #     if cv2.waitKey(1) & 0xFF == ord('q'):
# #         break

# # cap.release()
# # cv2.destroyAllWindows()


# import torch
# import torch.nn as nn
# from torchvision import transforms, models
# from PIL import Image
# import os
# import random

# # 📂 Classes (same as training)
# class_names = ['alert', 'distracted', 'drowzy']

# # 🧠 Load model
# model = models.mobilenet_v2(pretrained=False)
# model.classifier[1] = nn.Linear(model.last_channel, len(class_names))
# model.load_state_dict(torch.load("best_model.pth", weights_only=True))
# model.eval()

# # 🚀 Device
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# model = model.to(device)

# # 🔄 Transform
# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# # 📂 Dataset path
# base_path = "datasets/val"

# # 🎯 Choose class to test (change if needed)
# test_class = "drowsy"   # alert / distracted / drowsy

# folder_path = os.path.join(base_path, test_class)

# # 📸 Get all images
# images = os.listdir(folder_path)

# # 🔥 Pick 5 random images
# sample_images = random.sample(images, 5)

# print(f"\nTesting on class: {test_class}\n")

# for img_name in sample_images:
#     img_path = os.path.join(folder_path, img_name)

#     # Load image
#     image = Image.open(img_path).convert("RGB")
#     image = transform(image).unsqueeze(0).to(device)

#     # 🔮 Prediction
#     with torch.no_grad():
#         outputs = model(image)
#         probs = torch.softmax(outputs, dim=1)
#         _, pred = torch.max(outputs, 1)

#     pred_class = class_names[pred.item()]
#     confidence = probs[0][pred.item()].item() * 100

#     # ⚠️ Risk Score
#     if pred_class == "alert":
#         risk = 10
#     elif pred_class == "distracted":
#         risk = 60
#     else:
#         risk = 90

#     print("=================================")
#     print(f"Image      : {img_name}")
#     print(f"Actual     : {test_class}")
#     print(f"Prediction : {pred_class}")
#     print(f"Confidence : {confidence:.2f}%")
#     print(f"Risk Score : {risk}")






import cv2
import dlib
import numpy as np
import torch
from ultralytics import YOLO
import pygame
import time
import threading

# 🔊 INIT SOUND
pygame.mixer.init()

sounds = {
    "drowsy": "eye_alert.mp3",
    "phone": "phone_alert.mp3",
    "tilt": "look_ahead.mp3",
    "pull_over": "pull_over.mp3"
}

def play_sound(key):
    try:
        pygame.mixer.music.load(sounds[key])
        pygame.mixer.music.play()
    except:
        pass

def sound_thread(key):
    threading.Thread(target=play_sound, args=(key,), daemon=True).start()

# 🧠 DLIB
detector = dlib.get_frontal_face_detector()
predictor = dlib.shape_predictor("shape_predictor_81_face_landmarks.dat")

# 🤖 YOLO
yolo = YOLO("weights/yolov5m.pt")

# 🎥 CAMERA
cap = cv2.VideoCapture(0)

# 📊 COUNTERS
blink_counter = 0
eye_close_frames = 0
BLINK_THRESHOLD = 4
EAR_THRESHOLD = 0.22

# 👁️ EAR FUNCTION
def eye_aspect_ratio(eye):
    A = np.linalg.norm(np.array(eye[1]) - np.array(eye[5]))
    B = np.linalg.norm(np.array(eye[2]) - np.array(eye[4]))
    C = np.linalg.norm(np.array(eye[0]) - np.array(eye[3]))
    return (A + B) / (2.0 * C)

# 🧠 HEAD TILT
def head_tilt_angle(nose, left_eye, right_eye):
    dx = right_eye[0] - left_eye[0]
    dy = right_eye[1] - left_eye[1]
    angle = np.degrees(np.arctan2(dy, dx))
    return angle

print("🚀 System Started")

while True:
    ret, frame = cap.read()
    if not ret:
        break

    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
    faces = detector(gray)

    # 📱 YOLO PHONE DETECTION
    results = yolo(frame)
    detections = results[0].boxes.data

    for det in detections:
        cls = int(det[5])
        if cls == 67:  # phone
            x1, y1, x2, y2 = map(int, det[:4])
            cv2.rectangle(frame, (x1,y1),(x2,y2),(0,0,255),2)
            cv2.putText(frame, "PHONE DETECTED", (x1,y1-10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,255),2)
            sound_thread("phone")

    for face in faces:
        landmarks = predictor(gray, face)
        points = [(landmarks.part(i).x, landmarks.part(i).y) for i in range(68)]

        left_eye = points[36:42]
        right_eye = points[42:48]
        nose = points[30]

        ear = (eye_aspect_ratio(left_eye) + eye_aspect_ratio(right_eye)) / 2.0

        # 👁️ EYE CLOSE DETECTION
        if ear < EAR_THRESHOLD:
            eye_close_frames += 1
        else:
            if eye_close_frames > 0:
                blink_counter += 1
            eye_close_frames = 0

        # 🚨 PULL OVER ALERT
        if blink_counter >= BLINK_THRESHOLD:
            cv2.putText(frame, "⚠️ PULL OVER!", (50,100),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),3)
            sound_thread("pull_over")
            blink_counter = 0

        # 😴 DROWSY ALERT
        if ear < EAR_THRESHOLD:
            cv2.putText(frame, "DROWSY", (50,50),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (0,0,255),2)
            sound_thread("drowsy")

        # 🧠 HEAD TILT
        angle = head_tilt_angle(nose, left_eye[0], right_eye[3])
        if abs(angle) > 15:
            cv2.putText(frame, "HEAD TILT", (50,150),
                        cv2.FONT_HERSHEY_SIMPLEX, 1, (255,0,0),2)
            sound_thread("tilt")

        # DISPLAY EAR
        cv2.putText(frame, f"EAR: {ear:.2f}", (300,50),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,255,0),2)

    cv2.imshow("Driver Monitoring System", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
