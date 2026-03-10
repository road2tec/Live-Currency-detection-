"""
Indian Currency Detection - CNN Training Pipeline
Trains ResNet50 classifier on the Indian Currency Dataset.
"""
import os
import sys

# Fix Unicode output on Windows terminals (cp1252 can't handle emoji)
if sys.stdout.encoding and sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except Exception:
        pass

import time
import copy
import json
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, random_split
from torchvision import transforms, datasets
from pathlib import Path

# Add parent directory
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from detection.cnn_model import CurrencyClassifier

# ─── Configuration ─────────────────────────────────────────
DATASET_PATH = os.environ.get("DATASET_PATH", "../Indian Currency Dataset")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "../models")
BATCH_SIZE = 16  # Larger batch = fewer iterations per epoch
NUM_EPOCHS = 3   # Fast training; pretrained backbone converges quickly
LEARNING_RATE = 0.002
NUM_CLASSES = 7
IMAGE_SIZE = 128  # Smaller images = much faster on CPU
TRAIN_SPLIT = 0.8
VAL_SPLIT = 0.1
TEST_SPLIT = 0.1

# Class mapping
CLASS_NAMES = ["10", "20", "50", "100", "200", "500", "2000"]
CLASS_TO_IDX = {name: idx for idx, name in enumerate(CLASS_NAMES)}


def get_data_transforms():
    """Get training and validation data transforms with light augmentation for speed."""
    train_transforms = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.RandomRotation(degrees=10),
        transforms.ColorJitter(brightness=0.2, contrast=0.2),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    val_transforms = transforms.Compose([
        transforms.Resize((IMAGE_SIZE, IMAGE_SIZE)),
        transforms.ToTensor(),
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

    return train_transforms, val_transforms


def load_dataset(dataset_path: str):
    """Load and split dataset into train/val/test."""
    print(f"📂 Loading dataset from: {dataset_path}")

    train_transforms, val_transforms = get_data_transforms()

    # Load full dataset with train transforms
    full_dataset = datasets.ImageFolder(root=dataset_path, transform=train_transforms)

    print(f"📊 Total images: {len(full_dataset)}")
    print(f"📊 Classes: {full_dataset.classes}")
    print(f"📊 Class to idx: {full_dataset.class_to_idx}")

    # Split dataset
    total_size = len(full_dataset)
    train_size = int(TRAIN_SPLIT * total_size)
    val_size = int(VAL_SPLIT * total_size)
    test_size = total_size - train_size - val_size

    train_dataset, val_dataset, test_dataset = random_split(
        full_dataset, [train_size, val_size, test_size],
        generator=torch.Generator().manual_seed(42)
    )

    # Apply validation transforms to val and test sets
    val_dataset_proper = datasets.ImageFolder(root=dataset_path, transform=val_transforms)
    val_indices = val_dataset.indices
    test_indices = test_dataset.indices

    print(f"📊 Train: {train_size} | Val: {val_size} | Test: {test_size}")

    # pin_memory only useful with CUDA
    use_pin = torch.cuda.is_available()

    # Create dataloaders
    train_loader = DataLoader(train_dataset, batch_size=BATCH_SIZE, shuffle=True,
                              num_workers=0, pin_memory=use_pin, drop_last=True)
    val_loader = DataLoader(
        torch.utils.data.Subset(val_dataset_proper, val_indices),
        batch_size=BATCH_SIZE, shuffle=False, num_workers=0, pin_memory=use_pin
    )
    test_loader = DataLoader(
        torch.utils.data.Subset(val_dataset_proper, test_indices),
        batch_size=BATCH_SIZE, shuffle=False, num_workers=0, pin_memory=use_pin
    )

    return train_loader, val_loader, test_loader, full_dataset.classes


def train_model(train_loader, val_loader, classes, device):
    """Train the ResNet50 CNN model."""
    num_classes = len(classes)
    model = CurrencyClassifier(num_classes=num_classes, pretrained=True)
    model = model.to(device)

    # Loss and optimizer
    criterion = nn.CrossEntropyLoss(label_smoothing=0.1)
    optimizer = optim.AdamW(
        filter(lambda p: p.requires_grad, model.parameters()),
        lr=LEARNING_RATE, weight_decay=1e-4
    )

    # Simple learning rate scheduler
    scheduler = optim.lr_scheduler.StepLR(optimizer, step_size=2, gamma=0.5)

    best_model_wts = copy.deepcopy(model.state_dict())
    best_acc = 0.0
    best_epoch = 0
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}

    print(f"\n🚀 Starting training for {NUM_EPOCHS} epochs on {device}")
    print("=" * 60)

    for epoch in range(NUM_EPOCHS):
        epoch_start = time.time()

        # ─── Training Phase ────────────────────────
        model.train()
        running_loss = 0.0
        running_corrects = 0
        total_samples = 0

        for batch_idx, (inputs, labels) in enumerate(train_loader):
            inputs = inputs.to(device)
            labels = labels.to(device)

            optimizer.zero_grad()
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            loss.backward()

            # Gradient clipping
            torch.nn.utils.clip_grad_norm_(model.parameters(), max_norm=1.0)

            optimizer.step()

            _, preds = torch.max(outputs, 1)
            running_loss += loss.item() * inputs.size(0)
            running_corrects += torch.sum(preds == labels.data).item()
            total_samples += inputs.size(0)

        scheduler.step()

        train_loss = running_loss / total_samples
        train_acc = running_corrects / total_samples

        # ─── Validation Phase ──────────────────────
        model.eval()
        val_loss = 0.0
        val_corrects = 0
        val_total = 0

        with torch.no_grad():
            for inputs, labels in val_loader:
                inputs = inputs.to(device)
                labels = labels.to(device)

                outputs = model(inputs)
                loss = criterion(outputs, labels)

                _, preds = torch.max(outputs, 1)
                val_loss += loss.item() * inputs.size(0)
                val_corrects += torch.sum(preds == labels.data).item()
                val_total += inputs.size(0)

        val_loss = val_loss / max(val_total, 1)
        val_acc = val_corrects / max(val_total, 1)

        # Record history
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["train_acc"].append(train_acc)
        history["val_acc"].append(val_acc)

        epoch_time = time.time() - epoch_start
        lr = optimizer.param_groups[0]["lr"]

        print(
            f"Epoch [{epoch+1:02d}/{NUM_EPOCHS}] "
            f"Train Loss: {train_loss:.4f} Acc: {train_acc:.4f} | "
            f"Val Loss: {val_loss:.4f} Acc: {val_acc:.4f} | "
            f"LR: {lr:.6f} | Time: {epoch_time:.1f}s"
        )

        # Save best model
        if val_acc > best_acc:
            best_acc = val_acc
            best_epoch = epoch + 1
            best_model_wts = copy.deepcopy(model.state_dict())
            print(f"  ✅ New best model! Accuracy: {best_acc:.4f}")

    print("=" * 60)
    print(f"🏆 Best Val Accuracy: {best_acc:.4f} at epoch {best_epoch}")

    # Load best weights
    model.load_state_dict(best_model_wts)
    return model, history


def evaluate_model(model, test_loader, classes, device):
    """Evaluate model on test set."""
    model.eval()
    correct = 0
    total = 0
    class_correct = {c: 0 for c in classes}
    class_total = {c: 0 for c in classes}

    with torch.no_grad():
        for inputs, labels in test_loader:
            inputs = inputs.to(device)
            labels = labels.to(device)

            outputs = model(inputs)
            _, predicted = torch.max(outputs, 1)

            total += labels.size(0)
            correct += (predicted == labels).sum().item()

            for i in range(labels.size(0)):
                label = classes[labels[i]]
                pred = classes[predicted[i]]
                class_total[label] = class_total.get(label, 0) + 1
                if label == pred:
                    class_correct[label] = class_correct.get(label, 0) + 1

    overall_acc = correct / max(total, 1)
    print(f"\n📊 Test Results:")
    print(f"   Overall Accuracy: {overall_acc:.4f} ({correct}/{total})")
    print(f"\n   Per-class accuracy:")
    for cls in classes:
        cls_acc = class_correct[cls] / max(class_total[cls], 1)
        print(f"   ₹{cls}: {cls_acc:.4f} ({class_correct[cls]}/{class_total[cls]})")

    return overall_acc


def save_model(model, output_dir, history, classes):
    """Save trained model and training history."""
    os.makedirs(output_dir, exist_ok=True)

    model_path = os.path.join(output_dir, "currency_classifier.pth")
    torch.save({
        "model_state_dict": model.state_dict(),
        "classes": classes,
        "class_to_idx": {cls: idx for idx, cls in enumerate(classes)},
        "num_classes": len(classes),
    }, model_path)
    print(f"💾 Model saved to: {model_path}")

    # Save training history
    history_path = os.path.join(output_dir, "training_history.json")
    with open(history_path, "w") as f:
        json.dump(history, f, indent=2)
    print(f"📄 History saved to: {history_path}")


def main():
    """Main training pipeline."""
    print("=" * 60)
    print("🇮🇳 Indian Currency Detection - CNN Training Pipeline")
    print("=" * 60)

    # Set device
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    print(f"🔧 Device: {device}")
    if device.type == "cuda":
        print(f"   GPU: {torch.cuda.get_device_name(0)}")
        print(f"   Memory: {torch.cuda.get_device_properties(0).total_mem / 1e9:.1f} GB")

    # Resolve dataset path
    dataset_path = os.path.abspath(DATASET_PATH)
    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at: {dataset_path}")
        print("   Set DATASET_PATH environment variable or place dataset at ../Indian Currency Dataset")
        sys.exit(1)

    output_dir = os.path.abspath(OUTPUT_DIR)

    # Load data
    train_loader, val_loader, test_loader, classes = load_dataset(dataset_path)

    # Train
    model, history = train_model(train_loader, val_loader, classes, device)

    # Evaluate
    test_acc = evaluate_model(model, test_loader, classes, device)

    # Save
    save_model(model, output_dir, history, classes)

    print(f"\n🎉 Training complete! Test accuracy: {test_acc:.4f}")
    print(f"📁 Model saved to: {output_dir}/currency_classifier.pth")


if __name__ == "__main__":
    main()
