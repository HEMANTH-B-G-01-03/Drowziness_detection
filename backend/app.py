
# from flask import Flask, Response, jsonify
# from flask_cors import CORS
# import cv2
# from ultralytics import YOLO

# app = Flask(__name__)
# CORS(app)

# # LOAD YOLO MODEL
# model = YOLO("yolov8n.pt")

# camera = cv2.VideoCapture(0)

# current_status = {
#     "alert": "Normal",
#     "risk": 10,
#     "eye_status": "Alert",
#     "phone": "Not Detected"
# }


# def generate_frames():
#     global current_status

#     while True:
#         success, frame = camera.read()

#         if not success:
#             break

#         # YOLO DETECTION
#         results = model(frame)

#         phone_detected = False

#         for r in results:
#             boxes = r.boxes

#             for box in boxes:
#                 cls = int(box.cls[0])

#                 label = model.names[cls]

#                 if label == "cell phone":

#                     phone_detected = True

#                     current_status["alert"] = "Driver Using Phone"
#                     current_status["risk"] = 75
#                     current_status["phone"] = "Detected"

#                     x1, y1, x2, y2 = map(int, box.xyxy[0])

#                     cv2.rectangle(
#                         frame,
#                         (x1, y1),
#                         (x2, y2),
#                         (0, 0, 255),
#                         3
#                     )

#                     cv2.putText(
#                         frame,
#                         "PHONE DETECTED",
#                         (x1, y1 - 10),
#                         cv2.FONT_HERSHEY_SIMPLEX,
#                         1,
#                         (0, 0, 255),
#                         2
#                     )

#         if not phone_detected:
#             current_status["alert"] = "Normal"
#             current_status["risk"] = 10
#             current_status["phone"] = "Not Detected"

#         # ENCODE FRAME
#         ret, buffer = cv2.imencode('.jpg', frame)

#         frame = buffer.tobytes()

#         yield (
#             b'--frame\r\n'
#             b'Content-Type: image/jpeg\r\n\r\n' +
#             frame +
#             b'\r\n'
#         )


# @app.route('/video_feed')
# def video_feed():
#     return Response(
#         generate_frames(),
#         mimetype='multipart/x-mixed-replace; boundary=frame'
#     )


# @app.route('/status')
# def status():
#     return jsonify(current_status)


# if __name__ == "__main__":
#     app.run(debug=True)



# replace the above code because it was only detecting phone usage 

from flask import Flask, Response, jsonify
from flask_cors import CORS
import cv2

from SafeDriveVisionV0 import process_frame

app = Flask(__name__)
CORS(app)

camera = cv2.VideoCapture(0)

latest_status = {
    "alert": "Normal",
    "risk": 10,
    "eye_status": "Alert",
    "phone": "Not Detected"
}


def generate_frames():

    global latest_status

    while True:

        success, frame = camera.read()

        if not success:
            break

        processed_frame, status = process_frame(frame)

        latest_status = status

        ret, buffer = cv2.imencode('.jpg', processed_frame)

        frame = buffer.tobytes()

        yield (
            b'--frame\r\n'
            b'Content-Type: image/jpeg\r\n\r\n' +
            frame +
            b'\r\n'
        )


@app.route('/video_feed')
def video_feed():

    return Response(
        generate_frames(),
        mimetype='multipart/x-mixed-replace; boundary=frame'
    )


@app.route('/status')
def status():

    return jsonify(latest_status)


@app.route('/')
def home():

    return "AI Driver Monitoring Backend Running!"


if __name__ == "__main__":

    app.run(debug=True)