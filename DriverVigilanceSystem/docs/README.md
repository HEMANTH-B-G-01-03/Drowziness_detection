# Advanced Driver Vigilance System using Deep Learning and Computer Vision

A real-time driver monitoring system that combines a custom-trained CNN,
dlib facial-landmark analysis (eye/mouth aspect ratio + head pose), and YOLO
phone detection to compute a live **driver risk score** and trigger audio
alerts (Wake Up / Look Ahead / Phone Alert / Take Rest). A Flask backend runs
the AI pipeline; a React dashboard visualizes it in real time.

```
DriverVigilanceSystem/
├── backend/            Flask server + AI pipeline (PyTorch, dlib, YOLO)
├── frontend/            React dashboard (Dashboard, VideoFeed, StatusPanel)
├── models/               Trained CNN checkpoint (cnn_driver.pth)
├── dataset/              train/ test/ validation/ image folders + preprocess.py
├── audio/                 Alert .wav files (wake_up, look_ahead, phone_alert, take_rest)
└── docs/                   This README
```

---

## 1. Prerequisites

| Requirement | Notes |
|---|---|
| Python 3.9–3.11 | For the backend / AI pipeline |
| Node.js 16+ / npm | For the React frontend |
| Webcam | For live monitoring |
| GPU (recommended) | CUDA-capable GPU dramatically speeds up training; CPU works for inference/demo but is slower |
| CMake + a C++ compiler | Required to build `dlib` on some platforms |

**Hardware requirements**
- **Minimum (inference/demo only):** 4-core CPU, 8 GB RAM, integrated webcam. Expect ~5–10 FPS on CPU.
- **Recommended (training):** NVIDIA GPU with ≥6 GB VRAM (e.g., RTX 3060 or better), 16 GB RAM, CUDA 11.8+ and cuDNN installed.
- Training on CPU is possible for small datasets but will be significantly slower (hours vs. minutes per run).

---

## 2. Installation

### 2.1 Clone / unzip the project
```bash
cd DriverVigilanceSystem
```

### 2.2 Backend setup
```bash
cd backend
python -m venv venv
source venv/bin/activate        # On Windows: venv\Scripts\activate

pip install -r requirements.txt
```

> **dlib note:** `pip install dlib` requires CMake and a C++ build toolchain.
> - **Windows:** install [Visual Studio Build Tools](https://visualstudio.microsoft.com/visual-cpp-build-tools/) and [CMake](https://cmake.org/download/).
> - **macOS:** `brew install cmake`
> - **Linux:** `sudo apt-get install cmake build-essential`

Download the dlib 68-point facial landmark model and place it in `backend/`:
```bash
curl -O http://dlib.net/files/shape_predictor_68_face_landmarks.dat.bz2
bzip2 -d shape_predictor_68_face_landmarks.dat.bz2
```

YOLO phone detection uses `ultralytics`; the first run will auto-download
`yolov8n.pt` pretrained COCO weights. If `ultralytics`/weights aren't
available, `yolo_phone.py` automatically falls back to a mock detector so the
rest of the app still runs.

### 2.3 Frontend setup
```bash
cd ../frontend
npm install
cp .env.example .env   # adjust REACT_APP_API_URL if needed
```

---

## 3. Preparing the Dataset

Place raw images into:
```
dataset/train/alert/       dataset/test/alert/       dataset/validation/alert/
dataset/train/distracted/  dataset/test/distracted/  dataset/validation/distracted/
dataset/train/drowsy/      dataset/test/drowsy/      dataset/validation/drowsy/
```

Then clean/resize everything to 224×224:
```bash
cd dataset
python preprocess.py --root . --size 224
```

See `dataset/README.md` for suggested public data sources and class
definitions.

---

## 4. Training the CNN

```bash
cd backend
python train.py --epochs 10 --batch-size 32 --lr 0.0005
```

- Loads images via `torchvision.datasets.ImageFolder`.
- Automatically performs an 80/20 train/test split if `dataset/test/` has no
  images yet (otherwise uses the existing `test/` folder directly).
- Applies resize(224×224) + normalization + light augmentation.
- Trains the custom `DriverVigilanceCNN` (see `cnn_model.py`) for the given
  number of epochs, tracking the best validation accuracy.
- Saves the best-performing weights to `../models/cnn_driver.pth`.

A placeholder (untrained) `cnn_driver.pth` is included so the app runs
out-of-the-box for demo purposes — **retrain on real data before relying on
its predictions.**

---

## 5. Evaluating the Model

```bash
cd backend
python evaluate.py --data-root ../dataset --model-path ../models/cnn_driver.pth
```

Prints Accuracy, Precision, Recall, F1-score (macro-averaged), a confusion
matrix, and a full per-class classification report.

---

## 6. Running the Backend

```bash
cd backend
python app.py
```

Starts the Flask server on `http://localhost:5000` with:
- `POST /api/start` — starts server-side webcam capture + inference loop
- `POST /api/stop` — stops server-side capture
- `GET  /api/status` — latest JSON analysis (CNN prediction, EAR/MAR, head
  pose, phone detection, risk score, active alerts)
- `POST /api/analyze_frame` — analyze a single base64-JPEG frame (used by
  the frontend's "Browser Webcam" mode)
- `GET  /video_feed` — MJPEG stream of the raw camera feed (server capture mode)
- `GET  /api/health` — health check / component status

---

## 7. Running the Frontend

```bash
cd frontend
npm start
```

Opens the React dashboard at `http://localhost:3000`. It polls
`/api/status` every 500ms and renders:
- **Dashboard.js** — current driver state, animated risk-score meter, active
  alerts, class probability breakdown
- **VideoFeed.js** — live camera feed (server-side MJPEG stream, or
  browser-captured frames sent to `/api/analyze_frame`)
- **StatusPanel.js** — EAR/MAR/head-pose readouts, phone-detection status,
  and per-signal risk contribution breakdown

---

## 8. Audio Alerts

`alerts.py` uses Pygame's mixer to play `.wav` files from `audio/`:

| File | Triggered when |
|---|---|
| `wake_up.wav` | Eyes closed / EAR below threshold (drowsy) |
| `look_ahead.wav` | Head turned away from the road (distracted) |
| `phone_alert.wav` | A phone is detected in-frame |
| `take_rest.wav` | Overall risk score stays critical (≥85) |

Placeholder tone files are included; swap in your own recorded voice alerts
for production use. A 4-second cooldown per alert type prevents audio spam.

---

## 9. Example Usage

1. Start the backend: `python app.py`
2. Start the frontend: `npm start`
3. In the dashboard, click **Start Server Capture** (or switch to **Browser
   Webcam** mode).
4. Watch the **Risk Score** meter, **Eye & Head Status**, and **Phone
   Detection** panels update in real time as the CNN + landmark + YOLO
   pipeline processes each frame.
5. When drowsiness, distraction, or phone use is detected, the corresponding
   audio alert plays and a warning badge appears in the dashboard.

*(Screenshots: add your own captured screenshots of the running dashboard
here, e.g. `docs/screenshot_dashboard.png`.)*

---

## 10. Troubleshooting

- **`dlib` fails to build** — ensure CMake and a C++ compiler are installed
  (see §2.2), or use a prebuilt wheel: `pip install dlib-binary` (community
  wheel, x86-64 only).
- **No `shape_predictor_68_face_landmarks.dat`** — the backend will log a
  warning and disable landmark analysis (EAR/MAR/head pose) while still
  serving CNN predictions.
- **No CUDA GPU** — training/inference automatically falls back to CPU
  (`torch.cuda.is_available()` check in `train.py` / `app.py`).
- **CORS errors in the browser** — confirm `flask-cors` is installed and the
  backend is running on the same host/port configured in `frontend/.env`.
- **Webcam not found** — check `/api/start` request body `{"source": 0}`;
  try `1`, `2`, etc. for other connected cameras, or use "Browser Webcam"
  mode instead of server-side capture.
