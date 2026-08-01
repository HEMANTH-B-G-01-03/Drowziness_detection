"""
cnn_model.py
Custom PyTorch CNN for MULTI-LABEL Driver Vigilance Classification.

Unlike a single-label softmax classifier (which forces exactly one class to
"win"), this model treats each class as an INDEPENDENT binary decision, so
it can correctly detect combinations like "distracted AND drowsy" at the
same time, instead of being forced to pick just one.

Classes (each with its own independent probability, NOT mutually exclusive):
    0 -> Alert
    1 -> Distracted
    2 -> Drowsy

Architecture:
    4 convolutional blocks (Conv2d -> BatchNorm -> ReLU -> MaxPool)
    followed by 3 fully-connected layers with dropout and a final linear
    layer producing RAW LOGITS (no activation applied in forward()).

Why raw logits from forward()?
    nn.BCEWithLogitsLoss (used in train.py) expects raw logits and applies
    sigmoid internally in a numerically-stable way. Applying sigmoid inside
    forward() as well would double-apply it and break training. Use
    `predict_proba()` (or `torch.sigmoid(model(x))`) whenever you need
    actual probabilities for inference/serving.
"""

import torch
import torch.nn as nn
import torch.nn.functional as F


class DriverVigilanceCNN(nn.Module):
    """Custom multi-label CNN built from scratch (NOT a pretrained backbone)."""

    def __init__(self, num_classes: int = 3, input_size: int = 224):
        super(DriverVigilanceCNN, self).__init__()

        # ---- Convolutional Block 1 ----
        self.conv1 = nn.Conv2d(in_channels=3, out_channels=32, kernel_size=3, padding=1)
        self.bn1 = nn.BatchNorm2d(32)
        self.pool1 = nn.MaxPool2d(kernel_size=2, stride=2)  # 224 -> 112

        # ---- Convolutional Block 2 ----
        self.conv2 = nn.Conv2d(in_channels=32, out_channels=64, kernel_size=3, padding=1)
        self.bn2 = nn.BatchNorm2d(64)
        self.pool2 = nn.MaxPool2d(kernel_size=2, stride=2)  # 112 -> 56

        # ---- Convolutional Block 3 ----
        self.conv3 = nn.Conv2d(in_channels=64, out_channels=128, kernel_size=3, padding=1)
        self.bn3 = nn.BatchNorm2d(128)
        self.pool3 = nn.MaxPool2d(kernel_size=2, stride=2)  # 56 -> 28

        # ---- Convolutional Block 4 ----
        self.conv4 = nn.Conv2d(in_channels=128, out_channels=256, kernel_size=3, padding=1)
        self.bn4 = nn.BatchNorm2d(256)
        self.pool4 = nn.MaxPool2d(kernel_size=2, stride=2)  # 28 -> 14

        # Feature map size after 4 poolings: input_size / 16
        feat_dim = input_size // 16
        self.flatten_dim = 256 * feat_dim * feat_dim

        # ---- Fully Connected Layers ----
        self.fc1 = nn.Linear(self.flatten_dim, 512)
        self.dropout1 = nn.Dropout(0.5)

        self.fc2 = nn.Linear(512, 128)
        self.dropout2 = nn.Dropout(0.3)

        # Final layer -> raw logits, one per class (independent, not softmax)
        self.fc3 = nn.Linear(128, num_classes)

    def forward(self, x):
        x = self.pool1(F.relu(self.bn1(self.conv1(x))))
        x = self.pool2(F.relu(self.bn2(self.conv2(x))))
        x = self.pool3(F.relu(self.bn3(self.conv3(x))))
        x = self.pool4(F.relu(self.bn4(self.conv4(x))))

        x = x.view(x.size(0), -1)  # flatten

        x = F.relu(self.fc1(x))
        x = self.dropout1(x)

        x = F.relu(self.fc2(x))
        x = self.dropout2(x)

        logits = self.fc3(x)  # raw logits, shape [batch, num_classes]
        return logits

    def predict_proba(self, x):
        """Returns independent per-class probabilities via sigmoid (each in
        [0, 1], NOT summing to 1 — multiple classes can be simultaneously
        high, e.g. distracted=0.81 AND drowsy=0.77 at once)."""
        with torch.no_grad():
            logits = self.forward(x)
            return torch.sigmoid(logits)


CLASS_NAMES = ["alert", "distracted", "drowsy"]

# Per-class decision threshold for turning a probability into a boolean
# "is this class active right now" flag. Tune per class if one is too
# trigger-happy or too conservative once you have real validation data.
CLASS_THRESHOLDS = {
    "alert": 0.5,
    "distracted": 0.5,
    "drowsy": 0.5,
}


if __name__ == "__main__":
    # quick sanity check
    model = DriverVigilanceCNN(num_classes=3)
    dummy = torch.randn(2, 3, 224, 224)
    logits = model(dummy)
    probs = model.predict_proba(dummy)
    print("Logits shape:", logits.shape)      # expected: [2, 3]
    print("Probabilities (independent, per class):")
    print(probs)
    print("Row sums (NOTE: not expected to equal 1, unlike softmax):", probs.sum(dim=1))