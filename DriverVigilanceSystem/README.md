# Advanced Driver Vigilance System using Deep Learning and Computer Vision

Real-time driver drowsiness/distraction/phone-usage monitoring: custom
PyTorch CNN + dlib facial landmarks + YOLO phone detection → live risk score
→ Flask backend → React dashboard, with Pygame audio alerts.

📖 **Full setup, training, and usage instructions: [`docs/README.md`](docs/README.md)**

## Quick start

```bash
# Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
python app.py            # http://localhost:5000

# Frontend (separate terminal)
cd frontend
npm install
npm start                # http://localhost:3000
```

See [`docs/README.md`](docs/README.md) for dataset preparation, training
(`train.py`), evaluation (`evaluate.py`), audio alert setup, and
troubleshooting.
