# import torch
# import torch.nn as nn
# import torchvision
# from torchvision import datasets, transforms, models
# from torch.utils.data import DataLoader
# from sklearn.metrics import classification_report, confusion_matrix
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# # 🚀 Enable GPU optimization
# torch.backends.cudnn.benchmark = True

# # 📂 Paths
# train_dir = "datasets/train"
# val_dir = "datasets/val"

# # 🔄 Transformations
# transform = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# # 📊 Load Data
# train_data = datasets.ImageFolder(train_dir, transform=transform)
# val_data = datasets.ImageFolder(val_dir, transform=transform)

# # ⚡ GPU Optimized DataLoader
# train_loader = DataLoader(train_data, batch_size=32, shuffle=True, num_workers=0)
# val_loader = DataLoader(val_data, batch_size=32, shuffle=False, num_workers=0)

# # 🏷️ Classes
# class_names = train_data.classes
# print("Classes:", class_names)

# # 🧠 Model (Transfer Learning - MobileNetV2)
# model = models.mobilenet_v2(pretrained=True)
# model.classifier[1] = nn.Linear(model.last_channel, len(class_names))

# # 🚀 Device (GPU/CPU)
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("Using device:", device)

# model = model.to(device)

# # ⚙️ Loss & Optimizer
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# # 🔁 Training Loop
# epochs = 5

# for epoch in range(epochs):
#     model.train()
#     running_loss = 0

#     for images, labels in train_loader:
#         images = images.to(device, non_blocking=True)
#         labels = labels.to(device, non_blocking=True)

#         outputs = model(images)
#         loss = criterion(outputs, labels)

#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()

#         running_loss += loss.item()

#     print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss:.4f}")

# # 💾 Save Model
# torch.save(model.state_dict(), "driver_model.pth")
# print("Model saved as driver_model.pth")

# # 📊 Evaluation
# model.eval()
# all_preds = []
# all_labels = []

# with torch.no_grad():
#     for images, labels in val_loader:
#         images = images.to(device, non_blocking=True)

#         outputs = model(images)
#         _, preds = torch.max(outputs, 1)

#         all_preds.extend(preds.cpu().numpy())
#         all_labels.extend(labels.numpy())

# # 📈 Metrics
# print("\n📊 Classification Report:")
# print(classification_report(all_labels, all_preds, target_names=class_names))

# # 🔲 Confusion Matrix
# cm = confusion_matrix(all_labels, all_preds)

# plt.figure(figsize=(6, 6))
# sns.heatmap(cm, annot=True, fmt='d',
#             xticklabels=class_names,
#             yticklabels=class_names,
#             cmap="Blues")

# plt.xlabel("Predicted")
# plt.ylabel("Actual")
# plt.title("Confusion Matrix")
# plt.show()



import torch
import torch.nn as nn
import torchvision
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# 🚀 Enable GPU optimization
torch.backends.cudnn.benchmark = True

# 📂 Paths
train_dir = "datasets/train"
val_dir = "datasets/val"

# 🔥 Data Augmentation (IMPORTANT)
transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomRotation(10),
    transforms.ColorJitter(brightness=0.2),
    transforms.ToTensor()
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor()
])

# 📊 Load Data
train_data = datasets.ImageFolder(train_dir, transform=transform_train)
val_data = datasets.ImageFolder(val_dir, transform=transform_val)

# ⚡ DataLoader
train_loader = DataLoader(train_data, batch_size=32, shuffle=True, num_workers=0)
val_loader = DataLoader(val_data, batch_size=32, shuffle=False, num_workers=0)

# 🏷️ Classes
class_names = train_data.classes
print("Classes:", class_names)

# 🧠 Model (MobileNetV2)
model = models.mobilenet_v2(pretrained=True)
model.classifier[1] = nn.Linear(model.last_channel, len(class_names))

# 🚀 Device
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)
model = model.to(device)

# ⚙️ Loss & Optimizer
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# 🔥 Training
epochs = 10
best_loss = float('inf')

for epoch in range(epochs):
    model.train()
    running_loss = 0

    for images, labels in train_loader:
        images = images.to(device, non_blocking=True)
        labels = labels.to(device, non_blocking=True)

        outputs = model(images)
        loss = criterion(outputs, labels)

        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss:.4f}")

    # 💾 Save best model
    if running_loss < best_loss:
        best_loss = running_loss
        torch.save(model.state_dict(), "best_model.pth")

print("Best model saved as best_model.pth")

# 📊 Load best model for evaluation
model.load_state_dict(torch.load("best_model.pth"))
model.eval()

all_preds = []
all_labels = []

with torch.no_grad():
    for images, labels in val_loader:
        images = images.to(device, non_blocking=True)

        outputs = model(images)
        _, preds = torch.max(outputs, 1)

        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.numpy())

# 📈 Classification Report
report = classification_report(all_labels, all_preds, target_names=class_names)
print("\n📊 Classification Report:\n")
print(report)

# 💾 Save metrics
with open("metrics.txt", "w") as f:
    f.write(report)

# 🔲 Confusion Matrix
cm = confusion_matrix(all_labels, all_preds)

plt.figure(figsize=(6, 6))
sns.heatmap(cm, annot=True, fmt='d',
            xticklabels=class_names,
            yticklabels=class_names,
            cmap="Blues")

plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix")

# 💾 Save image
plt.savefig("confusion_matrix.png")
plt.show()
