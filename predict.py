
import torch
import cv2
import numpy as np
from torchvision import transforms, models
import torch.nn as nn

# 🏷️ Classes (IMPORTANT - SAME ORDER)
class_names = ['alert', 'distracted', 'drowsy']

# 🧠 Load Model
model = models.mobilenet_v2(pretrained=False)
model.classifier[1] = nn.Linear(model.last_channel, len(class_names))
model.load_state_dict(torch.load("driver_model.pth"))
model.eval()

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = model.to(device)

# 🔄 Transform
transform = transforms.Compose([
    transforms.ToPILImage(),
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# 🎥 Camera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    img = transform(frame).unsqueeze(0).to(device)

    with torch.no_grad():
        outputs = model(img)
        _, pred = torch.max(outputs, 1)

    label = class_names[pred.item()]

    # 📢 Display
    cv2.putText(frame, f"{label}", (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1,
                (0, 0, 255), 2)

    cv2.imshow("AI Driver Monitor", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
