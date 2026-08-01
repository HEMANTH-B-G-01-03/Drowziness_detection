"""
train.py
Trains the DriverVigilanceCNN as a MULTI-LABEL classifier so it can detect
multiple driver states at once (e.g. "distracted" AND "drowsy" together),
instead of being forced to pick a single winning class like a softmax model.

Usage:
    python train.py --epochs 10 --batch-size 32 --lr 0.0005

Dataset layout (multi-label folder convention):
    Folder names are one or more class names joined with "+", so a single
    image can be labeled with multiple classes at once by placing it in a
    combo folder:

        dataset/train/alert/*.jpg                  -> [alert]
        dataset/train/distracted/*.jpg              -> [distracted]
        dataset/train/drowsy/*.jpg                  -> [drowsy]
        dataset/train/distracted+drowsy/*.jpg       -> [distracted, drowsy]   (NEW)

    Plain single-class folders (as used previously) still work exactly as
    before — this is fully backward compatible. Add "+"-joined folders only
    for images that genuinely show more than one state at once.
"""

import os
import argparse
import copy
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import transforms
from PIL import Image

from cnn_model import DriverVigilanceCNN, CLASS_NAMES, CLASS_THRESHOLDS

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
VALID_EXTENSIONS = {".jpg", ".jpeg", ".png", ".bmp", ".webp"}


class MultiLabelImageDataset(Dataset):
    """
    Scans `root_dir` for class-name (or "class1+class2"-combo-name)
    subfolders and builds a multi-hot label vector per image, so a single
    image can carry more than one active class label.
    """

    def __init__(self, root_dir, class_names, transform=None):
        self.transform = transform
        self.class_names = class_names
        self.samples = []  # list of (filepath, multi_hot_label_list)

        if not os.path.isdir(root_dir):
            return

        for folder_name in sorted(os.listdir(root_dir)):
            folder_path = os.path.join(root_dir, folder_name)
            if not os.path.isdir(folder_path):
                continue

            # "distracted+drowsy" -> ["distracted", "drowsy"]
            labels_in_folder = [c.strip().lower() for c in folder_name.split("+")]
            unknown = [c for c in labels_in_folder if c not in class_names]
            if unknown:
                print(f"[dataset] Skipping folder '{folder_name}': "
                      f"unrecognized class(es) {unknown}. "
                      f"Expected some combination of {class_names}.")
                continue

            multi_hot = [1.0 if c in labels_in_folder else 0.0 for c in class_names]

            for filename in os.listdir(folder_path):
                ext = os.path.splitext(filename)[1].lower()
                if ext in VALID_EXTENSIONS:
                    self.samples.append((os.path.join(folder_path, filename), multi_hot))

    def __len__(self):
        return len(self.samples)

    def __getitem__(self, idx):
        filepath, label = self.samples[idx]
        image = Image.open(filepath).convert("RGB")
        if self.transform:
            image = self.transform(image)
        label_tensor = torch.tensor(label, dtype=torch.float32)
        return image, label_tensor


def get_transforms():
    train_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.RandomHorizontalFlip(p=0.3),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225]),
    ])
    eval_tf = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406],
                              std=[0.229, 0.224, 0.225]),
    ])
    return train_tf, eval_tf


def build_dataloaders(data_root: str, batch_size: int, class_names):
    train_tf, eval_tf = get_transforms()
    train_dir = os.path.join(data_root, "train")
    test_dir = os.path.join(data_root, "test")

    full_train = MultiLabelImageDataset(train_dir, class_names, transform=train_tf)

    has_test_images = os.path.isdir(test_dir) and len(
        MultiLabelImageDataset(test_dir, class_names)
    ) > 0

    if has_test_images:
        train_dataset = full_train
        test_dataset = MultiLabelImageDataset(test_dir, class_names, transform=eval_tf)
    else:
        # Auto 80/20 split from the train folder
        total = len(full_train)
        train_len = int(0.8 * total)
        test_len = total - train_len
        train_dataset, test_dataset = random_split(full_train, [train_len, test_len])

    train_loader = DataLoader(train_dataset, batch_size=batch_size, shuffle=True, num_workers=2)
    test_loader = DataLoader(test_dataset, batch_size=batch_size, shuffle=False, num_workers=2)

    return train_loader, test_loader


def multi_label_accuracy(probs, labels, thresholds_tensor):
    """Subset (exact-match) accuracy AND mean per-label accuracy."""
    preds = (probs >= thresholds_tensor).float()
    exact_match = (preds == labels).all(dim=1).float().mean().item()
    per_label_acc = (preds == labels).float().mean().item()
    return exact_match, per_label_acc


def train_model(epochs, batch_size, lr, data_root, save_path):
    class_names = CLASS_NAMES
    train_loader, test_loader = build_dataloaders(data_root, batch_size, class_names)
    print(f"Classes: {class_names}")
    print(f"Training on device: {DEVICE}")
    print(f"Train samples: {len(train_loader.dataset)} | Test samples: {len(test_loader.dataset)}")

    model = DriverVigilanceCNN(num_classes=len(class_names)).to(DEVICE)

    # BCEWithLogitsLoss: treats each class as an independent binary problem,
    # which is exactly what multi-label classification needs (unlike
    # CrossEntropyLoss, which assumes classes are mutually exclusive).
    criterion = nn.BCEWithLogitsLoss()
    optimizer = optim.Adam(model.parameters(), lr=lr)
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=5, gamma=0.5)

    thresholds_tensor = torch.tensor(
        [CLASS_THRESHOLDS[c] for c in class_names], device=DEVICE
    )

    best_acc = 0.0
    best_weights = copy.deepcopy(model.state_dict())

    for epoch in range(epochs):
        # ---- Training phase ----
        model.train()
        running_loss, exact_correct, total = 0.0, 0, 0

        for images, labels in train_loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)

            optimizer.zero_grad()
            logits = model(images)                       # raw logits
            loss = criterion(logits, labels)              # BCEWithLogitsLoss
            loss.backward()
            optimizer.step()

            running_loss += loss.item() * images.size(0)
            probs = torch.sigmoid(logits)
            exact_match, _ = multi_label_accuracy(probs, labels, thresholds_tensor)
            exact_correct += exact_match * images.size(0)
            total += images.size(0)

        train_loss = running_loss / total
        train_exact_acc = exact_correct / total

        # ---- Validation phase ----
        val_exact_acc, val_label_acc, val_loss = evaluate_epoch(
            model, test_loader, criterion, thresholds_tensor
        )

        scheduler.step()

        print(f"Epoch [{epoch+1}/{epochs}] "
              f"Train Loss: {train_loss:.4f} Train ExactAcc: {train_exact_acc:.4f} | "
              f"Val Loss: {val_loss:.4f} Val ExactAcc: {val_exact_acc:.4f} "
              f"Val PerLabelAcc: {val_label_acc:.4f}")

        if val_exact_acc > best_acc:
            best_acc = val_exact_acc
            best_weights = copy.deepcopy(model.state_dict())

    model.load_state_dict(best_weights)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)
    torch.save({
        "model_state_dict": model.state_dict(),
        "classes": class_names,
        "thresholds": CLASS_THRESHOLDS,
        "multi_label": True,
    }, save_path)
    print(f"Best validation exact-match accuracy: {best_acc:.4f}")
    print(f"Model saved to: {save_path}")


def evaluate_epoch(model, loader, criterion, thresholds_tensor):
    model.eval()
    running_loss, exact_correct, label_correct, total = 0.0, 0, 0, 0
    with torch.no_grad():
        for images, labels in loader:
            images, labels = images.to(DEVICE), labels.to(DEVICE)
            logits = model(images)
            loss = criterion(logits, labels)
            running_loss += loss.item() * images.size(0)

            probs = torch.sigmoid(logits)
            exact_match, per_label_acc = multi_label_accuracy(probs, labels, thresholds_tensor)
            exact_correct += exact_match * images.size(0)
            label_correct += per_label_acc * images.size(0)
            total += images.size(0)

    return exact_correct / total, label_correct / total, running_loss / total


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Train multi-label Driver Vigilance CNN")
    parser.add_argument("--epochs", type=int, default=10)
    parser.add_argument("--batch-size", type=int, default=32)
    parser.add_argument("--lr", type=float, default=5e-4)
    parser.add_argument("--data-root", type=str, default="../dataset")
    parser.add_argument("--save-path", type=str, default="../models/cnn_driver.pth")
    args = parser.parse_args()

    train_model(
        epochs=args.epochs,
        batch_size=args.batch_size,
        lr=args.lr,
        data_root=args.data_root,
        save_path=args.save_path,
    )