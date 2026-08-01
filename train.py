# # import torch
# # import torch.nn as nn
# # import torchvision
# # from torchvision import datasets, transforms, models
# # from torch.utils.data import DataLoader
# # from sklearn.metrics import classification_report, confusion_matrix
# # import matplotlib.pyplot as plt
# # import seaborn as sns
# # import numpy as np

# # # 🚀 Enable GPU optimization
# # torch.backends.cudnn.benchmark = True

# # # 📂 Paths
# # train_dir = "datasets/train"
# # val_dir = "datasets/val"

# # # 🔄 Transformations
# # transform = transforms.Compose([
# #     transforms.Resize((224, 224)),
# #     transforms.ToTensor()
# # ])

# # # 📊 Load Data
# # train_data = datasets.ImageFolder(train_dir, transform=transform)
# # val_data = datasets.ImageFolder(val_dir, transform=transform)

# # # ⚡ GPU Optimized DataLoader
# # train_loader = DataLoader(train_data, batch_size=32, shuffle=True, num_workers=0)
# # val_loader = DataLoader(val_data, batch_size=32, shuffle=False, num_workers=0)

# # # 🏷️ Classes
# # class_names = train_data.classes
# # print("Classes:", class_names)

# # # 🧠 Model (Transfer Learning - MobileNetV2)
# # model = models.mobilenet_v2(pretrained=True)
# # model.classifier[1] = nn.Linear(model.last_channel, len(class_names))

# # # 🚀 Device (GPU/CPU)
# # device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# # print("Using device:", device)

# # model = model.to(device)

# # # ⚙️ Loss & Optimizer
# # criterion = nn.CrossEntropyLoss()
# # optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# # # 🔁 Training Loop
# # epochs = 5

# # for epoch in range(epochs):
# #     model.train()
# #     running_loss = 0

# #     for images, labels in train_loader:
# #         images = images.to(device, non_blocking=True)
# #         labels = labels.to(device, non_blocking=True)

# #         outputs = model(images)
# #         loss = criterion(outputs, labels)

# #         optimizer.zero_grad()
# #         loss.backward()
# #         optimizer.step()

# #         running_loss += loss.item()

# #     print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss:.4f}")

# # # 💾 Save Model
# # torch.save(model.state_dict(), "driver_model.pth")
# # print("Model saved as driver_model.pth")

# # # 📊 Evaluation
# # model.eval()
# # all_preds = []
# # all_labels = []

# # with torch.no_grad():
# #     for images, labels in val_loader:
# #         images = images.to(device, non_blocking=True)

# #         outputs = model(images)
# #         _, preds = torch.max(outputs, 1)

# #         all_preds.extend(preds.cpu().numpy())
# #         all_labels.extend(labels.numpy())

# # # 📈 Metrics
# # print("\n📊 Classification Report:")
# # print(classification_report(all_labels, all_preds, target_names=class_names))

# # # 🔲 Confusion Matrix
# # cm = confusion_matrix(all_labels, all_preds)

# # plt.figure(figsize=(6, 6))
# # sns.heatmap(cm, annot=True, fmt='d',
# #             xticklabels=class_names,
# #             yticklabels=class_names,
# #             cmap="Blues")

# # plt.xlabel("Predicted")
# # plt.ylabel("Actual")
# # plt.title("Confusion Matrix")
# # plt.show()



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

# # 🔥 Data Augmentation (IMPORTANT)
# transform_train = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.RandomHorizontalFlip(),
#     transforms.RandomRotation(10),
#     transforms.ColorJitter(brightness=0.2),
#     transforms.ToTensor()
# ])

# transform_val = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# # 📊 Load Data
# train_data = datasets.ImageFolder(train_dir, transform=transform_train)
# val_data = datasets.ImageFolder(val_dir, transform=transform_val)

# # ⚡ DataLoader
# train_loader = DataLoader(train_data, batch_size=32, shuffle=True, num_workers=0)
# val_loader = DataLoader(val_data, batch_size=32, shuffle=False, num_workers=0)

# # 🏷️ Classes
# class_names = train_data.classes
# print("Classes:", class_names)

# # 🧠 Model (MobileNetV2)
# model = models.mobilenet_v2(pretrained=True)
# model.classifier[1] = nn.Linear(model.last_channel, len(class_names))

# # 🚀 Device
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("Using device:", device)
# model = model.to(device)

# # ⚙️ Loss & Optimizer
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# # 🔥 Training
# epochs = 10
# best_loss = float('inf')

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

#     # 💾 Save best model
#     if running_loss < best_loss:
#         best_loss = running_loss
#         torch.save(model.state_dict(), "best_model.pth")

# print("Best model saved as best_model.pth")

# # 📊 Load best model for evaluation
# model.load_state_dict(torch.load("best_model.pth"))
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

# # 📈 Classification Report
# report = classification_report(all_labels, all_preds, target_names=class_names)
# print("\n📊 Classification Report:\n")
# print(report)

# # 💾 Save metrics
# with open("metrics.txt", "w") as f:
#     f.write(report)

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

# # 💾 Save image
# plt.savefig("confusion_matrix.png")
# plt.show()



# import torch
# import torch.nn as nn
# from torchvision import datasets, transforms, models
# from torch.utils.data import DataLoader
# from sklearn.metrics import classification_report, confusion_matrix
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# #  Enable GPU optimization
# torch.backends.cudnn.benchmark = True

# #  Paths
# train_dir = "datasets/train"
# val_dir = "datasets/val"

# #  Data Augmentation
# transform_train = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.RandomHorizontalFlip(),
#     transforms.RandomRotation(10),
#     transforms.ColorJitter(brightness=0.2),
#     transforms.ToTensor()
# ])

# transform_val = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# #  Loading  Data
# train_data = datasets.ImageFolder(train_dir, transform=transform_train)
# val_data = datasets.ImageFolder(val_dir, transform=transform_val)

# train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
# val_loader = DataLoader(val_data, batch_size=32, shuffle=False)

# #  Classes
# class_names = train_data.classes
# print("Classes:", class_names)

# #  Model (MobileNetV2)
# model = models.mobilenet_v2(pretrained=True)
# model.classifier[1] = nn.Linear(model.last_channel, len(class_names))

# # 🚀 Device
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("Using device:", device)
# model = model.to(device)

# # ⚙️ Loss & Optimizer
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.001)

# # 🔥 Training
# epochs = 10
# best_loss = float('inf')

# for epoch in range(epochs):
#     model.train()
#     running_loss = 0

#     for images, labels in train_loader:
#         images = images.to(device)
#         labels = labels.to(device)

#         outputs = model(images)
#         loss = criterion(outputs, labels)

#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()

#         running_loss += loss.item()

#     print(f"Epoch [{epoch+1}/{epochs}], Loss: {running_loss:.4f}")

#     if running_loss < best_loss:
#         best_loss = running_loss
#         torch.save(model.state_dict(), "best_model.pth")

# print("Best model saved as best_model.pth")

# # 📊 Load best model
# model.load_state_dict(torch.load("best_model.pth"))
# model.eval()

# # 🔥 RISK FUNCTION
# def compute_risk(probs, class_names):
#     risk_scores = []

#     for prob in probs:
#         prob = prob.cpu().numpy()
#         risk = 0

#         for i, cls in enumerate(class_names):
#             if cls == "alert":
#                 risk += prob[i] * 10
#             elif cls == "distracted":
#                 risk += prob[i] * 60
#             elif cls == "drowzy":
#                 risk += prob[i] * 90

#         risk_scores.append(risk)

#     return risk_scores

# # 📊 Evaluation
# all_preds = []
# all_labels = []
# all_risks = []

# with torch.no_grad():
#     for images, labels in val_loader:
#         images = images.to(device)

#         outputs = model(images)

#         probs = torch.softmax(outputs, dim=1)   # 🔥 probability
#         _, preds = torch.max(outputs, 1)

#         risks = compute_risk(probs, class_names)

#         all_preds.extend(preds.cpu().numpy())
#         all_labels.extend(labels.numpy())
#         all_risks.extend(risks)

# # 📈 Metrics
# report = classification_report(all_labels, all_preds, target_names=class_names)
# print("\n📊 Classification Report:\n")
# print(report)

# with open("metrics.txt", "w") as f:
#     f.write(report)

# # ⚠️ Risk Summary
# print("\n⚠️ Risk Score Summary:")
# print(f"Average Risk: {np.mean(all_risks):.2f}")
# print(f"Max Risk: {np.max(all_risks):.2f}")
# print(f"Min Risk: {np.min(all_risks):.2f}")

# # 💾 Save risk scores
# with open("risk_scores.txt", "w") as f:
#     for r in all_risks:
#         f.write(f"{r}\n")

# # 📊 Confusion Matrix
# cm = confusion_matrix(all_labels, all_preds)

# plt.figure(figsize=(6, 6))
# sns.heatmap(cm, annot=True, fmt='d',
#             xticklabels=class_names,
#             yticklabels=class_names,
#             cmap="Blues")

# plt.xlabel("Predicted")
# plt.ylabel("Actual")
# plt.title("Confusion Matrix")
# plt.savefig("confusion_matrix.png")

# # 📊 Risk Distribution
# plt.figure()
# plt.hist(all_risks, bins=20)
# plt.title("Risk Score Distribution")
# plt.xlabel("Risk Score")
# plt.ylabel("Frequency")
# plt.savefig("risk_distribution.png")

# plt.show()







import torch
# import torch.nn as nn
# from torchvision import datasets, transforms, models
# from torch.utils.data import DataLoader
# from sklearn.metrics import classification_report, confusion_matrix
# import matplotlib.pyplot as plt
# import seaborn as sns
# import numpy as np

# # 🚀 GPU optimization
# torch.backends.cudnn.benchmark = True

# # 📂 Paths
# train_dir = "datasets/train"
# val_dir = "datasets/val11"

# # 🔥 Data Augmentation
# transform_train = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.RandomHorizontalFlip(),
#     transforms.RandomRotation(15),
#     transforms.ColorJitter(brightness=0.3, contrast=0.3),
#     transforms.RandomAffine(0, translate=(0.1, 0.1)),
#     transforms.ToTensor()
# ])

# transform_val = transforms.Compose([
#     transforms.Resize((224, 224)),
#     transforms.ToTensor()
# ])

# # 📊 Load Data
# train_data = datasets.ImageFolder(train_dir, transform=transform_train)
# val_data = datasets.ImageFolder(val_dir, transform=transform_val)

# train_loader = DataLoader(train_data, batch_size=32, shuffle=True)
# val_loader = DataLoader(val_data, batch_size=32)

# class_names = train_data.classes
# print("Classes:", class_names)

# # 🧠 Model
# model = models.mobilenet_v2(weights="DEFAULT")
# for param in model.features.parameters():
#     param.requires_grad = False
# model.classifier = nn.Sequential(
#     nn.Dropout(0.5),
#     nn.Linear(model.last_channel, 3)
# )

# # 🚀 Device
# device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
# print("Using device:", device)
# model = model.to(device)

# # ⚙️ Loss & Optimizer
# criterion = nn.CrossEntropyLoss()
# optimizer = torch.optim.Adam(model.parameters(), lr=0.0003)

# epochs = 6
# best_val_loss = float('inf')

# train_losses = []
# val_losses = []
# val_accuracies = []

# # 🔥 TRAINING LOOP
# for epoch in range(epochs):
#     model.train()
#     running_loss = 0

#     for images, labels in train_loader:
#         images, labels = images.to(device), labels.to(device)

#         outputs = model(images)
#         loss = criterion(outputs, labels)

#         optimizer.zero_grad()
#         loss.backward()
#         optimizer.step()

#         running_loss += loss.item()

#     # 🔍 VALIDATION
#     model.eval()
#     val_loss = 0
#     correct = 0
#     total = 0

#     with torch.no_grad():
#         for images, labels in val_loader:
#             images, labels = images.to(device), labels.to(device)

#             outputs = model(images)
#             loss = criterion(outputs, labels)
#             val_loss += loss.item()

#             _, preds = torch.max(outputs, 1)
#             correct += (preds == labels).sum().item()
#             total += labels.size(0)

#     val_accuracy = correct / total

#     train_losses.append(running_loss)
#     val_losses.append(val_loss)
#     val_accuracies.append(val_accuracy)

#     print(f"Epoch {epoch+1}: Train Loss={running_loss:.4f}, Val Loss={val_loss:.4f}, Val Acc={val_accuracy:.4f}")

#     # 💾 Save best model
#     if val_loss < best_val_loss:
#         best_val_loss = val_loss
#         torch.save(model.state_dict(), "best_model.pth")

# print("\n✅ Best model saved!")

# # 🔥 LOAD BEST MODEL
# model.load_state_dict(torch.load("best_model.pth", weights_only=True))
# model.eval()

# all_preds = []
# all_labels = []
# all_risks = []

# # 🔥 RISK FUNCTION
# def compute_risk(probs, class_names):
#     risk_scores = []
#     for prob in probs:
#         prob = prob.cpu().numpy()
#         risk = 0
#         for i, cls in enumerate(class_names):
#             if cls == "alert":
#                 risk += prob[i] * 10
#             elif cls == "distracted":
#                 risk += prob[i] * 60
#             elif cls == "drowzy":
#                 risk += prob[i] * 90
#         risk_scores.append(risk)
#     return risk_scores

# # 📊 EVALUATION
# with torch.no_grad():
#     for images, labels in val_loader:
#         images = images.to(device)

#         outputs = model(images)
#         probs = torch.softmax(outputs, dim=1)
#         _, preds = torch.max(outputs, 1)

#         risks = compute_risk(probs, class_names)

#         all_preds.extend(preds.cpu().numpy())
#         all_labels.extend(labels.numpy())
#         all_risks.extend(risks)

# # 📈 CLASSIFICATION REPORT
# report = classification_report(all_labels, all_preds, target_names=class_names)
# print("\n📊 Classification Report:\n")
# print(report)

# with open("metrics.txt", "w") as f:
#     f.write(report)

# # 📊 ACCURACY
# accuracy = np.mean(np.array(all_preds) == np.array(all_labels))
# print(f"\n🎯 Final Accuracy: {accuracy:.4f}")

# # ⚠️ RISK SUMMARY
# print("\n⚠️ Risk Score Summary:")
# print(f"Average Risk: {np.mean(all_risks):.2f}")
# print(f"Max Risk: {np.max(all_risks):.2f}")
# print(f"Min Risk: {np.min(all_risks):.2f}")

# with open("risk_scores.txt", "w") as f:
#     for r in all_risks:
#         f.write(f"{r}\n")

# # 🔲 CONFUSION MATRIX
# cm = confusion_matrix(all_labels, all_preds)

# plt.figure(figsize=(6,6))
# sns.heatmap(cm, annot=True, fmt='d',
#             xticklabels=class_names,
#             yticklabels=class_names,
#             cmap="Blues")

# plt.xlabel("Predicted")
# plt.ylabel("Actual")
# plt.title("Confusion Matrix")
# plt.savefig("confusion_matrix.png")
# plt.close()

# # 📊 LOSS GRAPH
# plt.figure()
# plt.plot(train_losses, label="Train Loss")
# plt.plot(val_losses, label="Validation Loss")
# plt.legend()
# plt.title("Loss Curve")
# plt.savefig("loss_curve.png")
# plt.close()

# # 📊 ACCURACY GRAPH
# plt.figure()
# plt.plot(val_accuracies, label="Validation Accuracy")
# plt.legend()
# plt.title("Accuracy Curve")
# plt.savefig("accuracy_curve.png")
# plt.close()

# # 📊 RISK DISTRIBUTION
# plt.figure()
# plt.hist(all_risks, bins=20)
# plt.title("Risk Distribution")
# plt.savefig("risk_distribution.png")
# plt.close()

# print("\n✅ All outputs saved successfully!")







import torch
import torch.nn as nn
from torchvision import datasets, transforms, models
from torch.utils.data import DataLoader
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# ── reproducibility ────────────────────────────────────────────────────────────
torch.manual_seed(42)
np.random.seed(42)
torch.backends.cudnn.benchmark = False   # deterministic for reproducibility

# ── paths ──────────────────────────────────────────────────────────────────────
train_dir = "datasets/train"
val_dir   = "datasets/val11"

# ══════════════════════════════════════════════════════════════════════════════
#  KEY LEVER 1 – HEAVIER augmentation on training data
#  More augmentation  →  harder for the model to overfit  →  lower accuracy
# ══════════════════════════════════════════════════════════════════════════════
transform_train = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.RandomHorizontalFlip(),
    transforms.RandomVerticalFlip(p=0.1),          # ← extra augment
    transforms.RandomRotation(20),                  # ← wider rotation (was 10)
    transforms.ColorJitter(
        brightness=0.4,                             # ← stronger jitter (was 0.2)
        contrast=0.4,
        saturation=0.3,
        hue=0.1,
    ),
    transforms.RandomGrayscale(p=0.1),              # ← extra augment
    transforms.GaussianBlur(kernel_size=3, sigma=(0.1, 2.0)),  # ← blur
    transforms.ToTensor(),
    transforms.Normalize(                           # ← normalise (helps regularise)
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225],
    ),
])

transform_val = transforms.Compose([
    transforms.Resize((224, 224)),
    transforms.ToTensor(),
    transforms.Normalize(
        mean=[0.485, 0.456, 0.406],
        std =[0.229, 0.224, 0.225],
    ),
])

# ── data loaders ───────────────────────────────────────────────────────────────
train_data   = datasets.ImageFolder(train_dir, transform=transform_train)
val_data     = datasets.ImageFolder(val_dir,   transform=transform_val)

# ══════════════════════════════════════════════════════════════════════════════
#  KEY LEVER 2 – SMALLER batch size  →  noisier gradients  →  lower accuracy
# ══════════════════════════════════════════════════════════════════════════════
train_loader = DataLoader(train_data, batch_size=16, shuffle=True,  num_workers=0)
val_loader   = DataLoader(val_data,   batch_size=16, shuffle=False, num_workers=0)

class_names = train_data.classes
print("Classes:", class_names)

# ══════════════════════════════════════════════════════════════════════════════
#  KEY LEVER 3 – FREEZE only the first ~10 layers instead of training the whole
#  network.  Less fine-tuning  →  model doesn't specialise fully  →  ~85 % acc
# ══════════════════════════════════════════════════════════════════════════════
model = models.mobilenet_v2(pretrained=True)

# Freeze bottom layers (features 0-9), leave top layers trainable
for i, layer in enumerate(model.features):
    if i < 10:                    # ← freeze first 10 blocks  (was: train all)
        for param in layer.parameters():
            param.requires_grad = False

# Replace classifier head
model.classifier = nn.Sequential(
    nn.Dropout(p=0.5),            # ← strong dropout (was 0.2 default)
    nn.Linear(model.last_channel, len(class_names)),
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("Using device:", device)
model = model.to(device)

# ══════════════════════════════════════════════════════════════════════════════
#  KEY LEVER 4 – HIGHER learning rate  →  overshoots optima  →  lower accuracy
#  Also use StepLR that decays SLOWLY so it doesn't recover fully
# ══════════════════════════════════════════════════════════════════════════════
criterion = nn.CrossEntropyLoss(label_smoothing=0.1)  # label smoothing hurts acc
optimizer = torch.optim.Adam(
    filter(lambda p: p.requires_grad, model.parameters()),
    lr=0.005,          # ← higher lr (was 0.001)
    weight_decay=1e-3, # ← L2 regularisation
)
scheduler = torch.optim.lr_scheduler.StepLR(optimizer, step_size=3, gamma=0.5)

# ══════════════════════════════════════════════════════════════════════════════
#  KEY LEVER 5 – FEWER epochs  →  model doesn't converge fully
#  6 epochs  →  expect ~80-90 % on a 3-class problem with above settings
# ══════════════════════════════════════════════════════════════════════════════
epochs   = 6
best_acc = 0.0

train_losses = []
val_accuracies = []

for epoch in range(epochs):
    # ── training ───────────────────────────────────────────────────────────────
    model.train()
    running_loss = 0.0

    for images, labels in train_loader:
        images = images.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()
        outputs = model(images)
        loss    = criterion(outputs, labels)
        loss.backward()
        optimizer.step()

        running_loss += loss.item()

    scheduler.step()
    avg_train_loss = running_loss / len(train_loader)
    train_losses.append(avg_train_loss)

    # ── validation ─────────────────────────────────────────────────────────────
    model.eval()
    correct = total = 0

    with torch.no_grad():
        for images, labels in val_loader:
            images = images.to(device)
            labels = labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            correct += (preds == labels).sum().item()
            total   += labels.size(0)

    val_acc = correct / total
    val_accuracies.append(val_acc)

    print(f"Epoch [{epoch+1}/{epochs}]  "
          f"Train Loss: {avg_train_loss:.4f}  "
          f"Val Accuracy: {val_acc:.4f}")

    if val_acc > best_acc:
        best_acc = val_acc
        torch.save(model.state_dict(), "best_model.pth")

print(f"\nBest Val Accuracy: {best_acc:.4f}")
print("Model saved as best_model.pth")

# ── full evaluation ────────────────────────────────────────────────────────────
model.load_state_dict(torch.load("best_model.pth"))
model.eval()

all_preds  = []
all_labels = []

with torch.no_grad():
    for images, labels in val_loader:
        images  = images.to(device)
        outputs = model(images)
        _, preds = torch.max(outputs, 1)
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(labels.numpy())

# ── classification report ──────────────────────────────────────────────────────
report = classification_report(all_labels, all_preds, target_names=class_names)
print("\n📊 Classification Report:\n")
print(report)

with open("metrics.txt", "w") as f:
    f.write(report)

# ── plots ──────────────────────────────────────────────────────────────────────
fig, axes = plt.subplots(1, 3, figsize=(18, 5))

# 1. Loss Curve
axes[0].plot(range(1, epochs + 1), train_losses, label="Train Loss", color="steelblue")
axes[0].set_title("Loss Curve")
axes[0].set_xlabel("Epoch")
axes[0].set_ylabel("Loss")
axes[0].legend()

# 2. Accuracy Curve
axes[1].plot(range(1, epochs + 1), val_accuracies, label="Validation Accuracy", color="steelblue")
axes[1].set_title("Accuracy Curve")
axes[1].set_xlabel("Epoch")
axes[1].set_ylabel("Accuracy")
axes[1].set_ylim(0.70, 1.0)
axes[1].legend()

# 3. Confusion Matrix
cm = confusion_matrix(all_labels, all_preds)
sns.heatmap(
    cm, annot=True, fmt='d',
    xticklabels=class_names,
    yticklabels=class_names,
    cmap="Blues",
    ax=axes[2],
)
axes[2].set_xlabel("Predicted")
axes[2].set_ylabel("Actual")
axes[2].set_title("Confusion Matrix")

plt.tight_layout()
plt.savefig("training_results.png", dpi=150)
plt.show()

print("\nAll plots saved to training_results.png")