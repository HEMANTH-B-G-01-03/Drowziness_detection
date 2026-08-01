"""
evaluate.py
Evaluates a trained multi-label DriverVigilanceCNN checkpoint on the test
dataset. Reports both per-class metrics (precision/recall/F1 for "alert",
"distracted", "drowsy" independently) AND multi-label-specific metrics
(exact-match/subset accuracy, Hamming loss) so you can see how well the
model handles images where more than one class is simultaneously true.

Usage:
    python evaluate.py --data-root ../dataset --model-path ../models/cnn_driver.pth
"""

import argparse
import torch
import numpy as np
from torch.utils.data import DataLoader
from sklearn.metrics import (
    precision_score,
    recall_score,
    f1_score,
    hamming_loss,
    accuracy_score,
    multilabel_confusion_matrix,
    classification_report,
)

from cnn_model import DriverVigilanceCNN, CLASS_NAMES, CLASS_THRESHOLDS
from train import MultiLabelImageDataset, get_transforms

DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")


def load_model(model_path):
    checkpoint = torch.load(model_path, map_location=DEVICE)
    classes = checkpoint.get("classes", CLASS_NAMES)
    thresholds = checkpoint.get("thresholds", CLASS_THRESHOLDS)
    model = DriverVigilanceCNN(num_classes=len(classes)).to(DEVICE)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    return model, classes, thresholds


def evaluate(data_root, model_path):
    model, classes, thresholds = load_model(model_path)
    _, eval_tf = get_transforms()

    test_dataset = MultiLabelImageDataset(f"{data_root}/test", classes, transform=eval_tf)
    test_loader = DataLoader(test_dataset, batch_size=32, shuffle=False)

    threshold_arr = np.array([thresholds[c] for c in classes])

    all_probs, all_labels = [], []
    with torch.no_grad():
        for images, labels in test_loader:
            images = images.to(DEVICE)
            logits = model(images)
            probs = torch.sigmoid(logits).cpu().numpy()
            all_probs.append(probs)
            all_labels.append(labels.numpy())

    all_probs = np.concatenate(all_probs, axis=0)
    all_labels = np.concatenate(all_labels, axis=0)
    all_preds = (all_probs >= threshold_arr).astype(int)
    all_labels = all_labels.astype(int)

    # ---- Multi-label-specific metrics ----
    exact_match_acc = accuracy_score(all_labels, all_preds)   # subset accuracy
    hamming = hamming_loss(all_labels, all_preds)              # fraction of wrong labels

    # ---- Per-class / aggregate metrics ----
    precision_macro = precision_score(all_labels, all_preds, average="macro", zero_division=0)
    recall_macro = recall_score(all_labels, all_preds, average="macro", zero_division=0)
    f1_macro = f1_score(all_labels, all_preds, average="macro", zero_division=0)

    cm_per_class = multilabel_confusion_matrix(all_labels, all_preds)

    print("========== Multi-Label Evaluation Results ==========")
    print(f"Exact-match (subset) accuracy: {exact_match_acc:.4f}  "
          f"(all classes correct simultaneously)")
    print(f"Hamming loss                 : {hamming:.4f}  (lower is better)")
    print(f"Macro Precision               : {precision_macro:.4f}")
    print(f"Macro Recall                  : {recall_macro:.4f}")
    print(f"Macro F1-score                : {f1_macro:.4f}")

    print("\nPer-class confusion matrices (format: [[TN, FP], [FN, TP]]):")
    for i, cls in enumerate(classes):
        print(f"  {cls}:\n{cm_per_class[i]}")

    print("\nDetailed per-class classification report:")
    print(classification_report(all_labels, all_preds, target_names=classes, zero_division=0))

    # Count how many test images had more than one true label active,
    # and how many predictions correctly captured that co-occurrence.
    multi_label_true = (all_labels.sum(axis=1) > 1)
    if multi_label_true.sum() > 0:
        co_occurrence_acc = accuracy_score(
            all_labels[multi_label_true], all_preds[multi_label_true]
        )
        print(f"\nImages with 2+ true classes active: {int(multi_label_true.sum())}")
        print(f"Exact-match accuracy on those multi-class images: {co_occurrence_acc:.4f}")
    else:
        print("\nNo test images with 2+ simultaneous true classes were found "
              "(add '+'-joined folders like 'distracted+drowsy' to test this).")

    return {
        "exact_match_accuracy": exact_match_acc,
        "hamming_loss": hamming,
        "precision_macro": precision_macro,
        "recall_macro": recall_macro,
        "f1_macro": f1_macro,
        "confusion_matrices": {cls: cm_per_class[i].tolist() for i, cls in enumerate(classes)},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Evaluate multi-label Driver Vigilance CNN")
    parser.add_argument("--data-root", type=str, default="../dataset")
    parser.add_argument("--model-path", type=str, default="../models/cnn_driver.pth")
    args = parser.parse_args()

    evaluate(args.data_root, args.model_path)