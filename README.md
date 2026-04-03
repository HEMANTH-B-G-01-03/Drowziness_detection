# 🚗 SafeDriveVision

## 📌 Project Description

SafeDriveVision is a computer vision-based project designed to enhance road safety by detecting dangerous driver behaviors in real time.
🎓 Developed by Hemanth Masters Student at BMS College Of Engineering 

It uses deep learning and computer vision techniques to identify:

* 📱 Phone usage while driving
* 😴 Driver drowsiness
* ⚠️ Unsafe behavior with real-time alerts

---

## ✨ Features

* **Phone Detection** using YOLOv5
* **Drowsiness Detection** using facial landmarks
* **Real-Time Alerts** using audio warnings
* **2D + 3D Face Analysis**

---

## ⚙️ System Requirements

Make sure your system has:

* Python **3.9 (Recommended)**
* Git
* Webcam
* Windows / Linux

---

## 🧩 Installation (Step-by-Step)

### 1️⃣ Clone the Repository

```bash
git clone https://github.com/Boubker10/SafeDriveVision.git
cd SafeDriveVision
```

---

### 2️⃣ Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

#### Windows:

```bash
venv\Scripts\activate
```

---

### 3️⃣ Upgrade pip

```bash
python -m pip install --upgrade pip setuptools wheel
```

---

### 4️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

---

### ⚠️ If installation fails (common fix)

Install manually:

```bash
pip install numpy opencv-python mediapipe scipy matplotlib pyyaml Pillow tqdm scikit-image scikit-learn onnxruntime playsound==1.2.2 imutils
```

---

### 5️⃣ Install PyTorch

```bash
pip install torch torchvision torchaudio
```

---

### 6️⃣ Install dlib (Important)

```bash
pip install cmake
pip install dlib
```

👉 If it fails:

* Install **Visual Studio Build Tools**
* Enable **C++ build tools**
* Then retry

---

## 📥 Required Model Download

Download YOLOv5 model:

👉 https://github.com/ultralytics/yolov5/releases/download/v5.0/yolov5m.pt

Place it inside:

```
SafeDriveVision/weights/
```

---

## ⚠️ Important Fix (Very Important)

Rename this file:

```
shape_predictor_81_face_landmarks (1).dat
```

➡️ TO:

```
shape_predictor_81_face_landmarks.dat
```

---

## 🚀 How to Run

### ✅ Step 1 (Recommended First)

```bash
python SafeDriveVisionV0.py
```

---

### ✅ Step 2 (2D Sparse Mode)

```bash
python SafeDriveVision.py --onnx
```

---

### ✅ Step 3 (3D Face Mode)

```bash
python SafeDriveVision.py --onnx --opt 3d
```

---

## 🎥 Webcam Test (If camera not working)

just Create one python file named as  `camtest.py`:

```python
import cv2

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    cv2.imshow("Camera", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
```

Run:

```bash
python camtest.py
```

---

## ❗ Common Errors & Fixes

### 🔴 ModuleNotFoundError

Install missing package:

```bash
pip install <module-name>
```

---

### 🔴 yolov5m.pt not found

➡️ Place file inside `weights/` folder

---

### 🔴 dlib installation error

➡️ Install:

* cmake
* Visual Studio Build Tools

---

### 🔴 Camera not opening

➡️ Check webcam using `camtest.py`

---

## 📚 Reference

* Based on: https://github.com/cleardusk/3DDFA

---

## 👨‍💻 Author

* Boubker → https://github.com/Boubker10

---

## 🤝 Contributions

Feel free to fork, improve, and create pull requests 🚀

---

## ⭐ Support

If you like this project, give it a ⭐ on GitHub!
