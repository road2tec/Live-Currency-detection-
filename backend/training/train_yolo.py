"""
Indian Currency Detection - YOLOv8 Training Pipeline
Trains YOLOv8l for currency note detection (localization).
"""
import os
import sys
import shutil
import random
import yaml
from pathlib import Path
from PIL import Image

# ─── Configuration ─────────────────────────────────────────
DATASET_PATH = os.environ.get("DATASET_PATH", "../Indian Currency Dataset")
OUTPUT_DIR = os.environ.get("OUTPUT_DIR", "../models")
YOLO_DATASET_DIR = os.environ.get("YOLO_DATASET_DIR", "../yolo_dataset")
EPOCHS = 20
IMAGE_SIZE = 416
BATCH_SIZE = 32
MODEL_VARIANT = "yolov8n.pt"  # Nano variant for faster training

# Class names
CLASS_NAMES = ["10", "20", "50", "100", "200", "500", "2000"]


def prepare_yolo_dataset(source_dir: str, output_dir: str, train_split: float = 0.85):
    """
    Convert ImageFolder dataset to YOLO format.
    Since we have classification images (single note per image), we create bounding
    boxes that cover the entire image (the note occupies most of the frame).
    """
    print("📁 Preparing YOLO dataset...")

    source_path = Path(source_dir)
    output_path = Path(output_dir)

    # Create directory structure
    for split in ["train", "val"]:
        (output_path / split / "images").mkdir(parents=True, exist_ok=True)
        (output_path / split / "labels").mkdir(parents=True, exist_ok=True)

    all_images = []

    for class_idx, class_name in enumerate(CLASS_NAMES):
        class_dir = source_path / class_name
        if not class_dir.exists():
            print(f"  ⚠️ Class directory not found: {class_dir}")
            continue

        for img_file in class_dir.iterdir():
            if img_file.suffix.lower() in [".jpg", ".jpeg", ".png", ".bmp", ".webp"]:
                all_images.append((img_file, class_idx, class_name))

    # Shuffle and split
    random.seed(42)
    random.shuffle(all_images)

    split_idx = int(len(all_images) * train_split)
    train_images = all_images[:split_idx]
    val_images = all_images[split_idx:]

    print(f"  Train: {len(train_images)} | Val: {len(val_images)}")

    # Process images
    for split, images in [("train", train_images), ("val", val_images)]:
        for idx, (img_path, class_idx, class_name) in enumerate(images):
            try:
                # Copy image
                new_name = f"{class_name}_{idx:05d}{img_path.suffix}"
                dest_img = output_path / split / "images" / new_name
                shutil.copy2(img_path, dest_img)

                # Create YOLO format label (full image bounding box)
                # For currency notes that fill most of the image:
                # center_x, center_y, width, height (normalized 0-1)
                # Slightly smaller bbox to simulate detection margins
                label_name = f"{class_name}_{idx:05d}.txt"
                dest_label = output_path / split / "labels" / label_name

                # Use a tight bounding box (note occupies ~85-95% of frame)
                cx, cy, w, h = 0.5, 0.5, 0.90, 0.90
                with open(dest_label, "w") as f:
                    f.write(f"{class_idx} {cx} {cy} {w} {h}\n")

            except Exception as e:
                print(f"  ⚠️ Error processing {img_path}: {e}")

    # Create data.yaml
    data_yaml = {
        "path": str(output_path.absolute()),
        "train": "train/images",
        "val": "val/images",
        "names": {i: name for i, name in enumerate(CLASS_NAMES)},
        "nc": len(CLASS_NAMES),
    }

    yaml_path = output_path / "data.yaml"
    with open(yaml_path, "w") as f:
        yaml.dump(data_yaml, f, default_flow_style=False)

    print(f"  ✅ Dataset prepared at: {output_path}")
    print(f"  📄 Config: {yaml_path}")

    return str(yaml_path)


def train_yolo(data_yaml: str, output_dir: str):
    """Train YOLOv8 model."""
    from ultralytics import YOLO

    print(f"\n🚀 Starting YOLOv8 training...")
    print(f"   Model: {MODEL_VARIANT}")
    print(f"   Epochs: {EPOCHS}")
    print(f"   Image Size: {IMAGE_SIZE}")
    print(f"   Batch Size: {BATCH_SIZE}")

    # Load pretrained YOLOv8 large
    model = YOLO(MODEL_VARIANT)

    # Train
    results = model.train(
        data=data_yaml,
        epochs=EPOCHS,
        imgsz=IMAGE_SIZE,
        batch=BATCH_SIZE,
        name="currency_detection",
        project=output_dir,
        patience=10,
        save=True,
        save_period=10,
        device="0" if __import__("torch").cuda.is_available() else "cpu",
        workers=0,
        pretrained=True,
        optimizer="AdamW",
        lr0=0.001,
        lrf=0.01,
        momentum=0.937,
        weight_decay=0.0005,
        warmup_epochs=3,
        warmup_momentum=0.8,
        box=7.5,
        cls=0.5,
        hsv_h=0.015,
        hsv_s=0.7,
        hsv_v=0.4,
        degrees=10.0,
        translate=0.1,
        scale=0.5,
        shear=2.0,
        perspective=0.0001,
        flipud=0.3,
        fliplr=0.5,
        mosaic=1.0,
        mixup=0.1,
        copy_paste=0.1,
    )

    # Copy best model to output
    best_model_src = Path(output_dir) / "currency_detection" / "weights" / "best.pt"
    best_model_dst = Path(output_dir) / "yolo_currency.pt"

    if best_model_src.exists():
        shutil.copy2(best_model_src, best_model_dst)
        print(f"✅ Best model saved to: {best_model_dst}")
    else:
        # Try last.pt
        last_model_src = Path(output_dir) / "currency_detection" / "weights" / "last.pt"
        if last_model_src.exists():
            shutil.copy2(last_model_src, best_model_dst)
            print(f"✅ Model saved to: {best_model_dst}")

    return results


def main():
    """Main YOLO training pipeline."""
    print("=" * 60)
    print("🇮🇳 Indian Currency Detection - YOLOv8 Training Pipeline")
    print("=" * 60)

    dataset_path = os.path.abspath(DATASET_PATH)
    output_dir = os.path.abspath(OUTPUT_DIR)
    yolo_dataset_dir = os.path.abspath(YOLO_DATASET_DIR)

    if not os.path.exists(dataset_path):
        print(f"❌ Dataset not found at: {dataset_path}")
        sys.exit(1)

    os.makedirs(output_dir, exist_ok=True)

    # Step 1: Prepare YOLO dataset
    data_yaml = prepare_yolo_dataset(dataset_path, yolo_dataset_dir)

    # Step 2: Train YOLO
    results = train_yolo(data_yaml, output_dir)

    print(f"\n🎉 YOLO training complete!")
    print(f"📁 Model saved to: {output_dir}/yolo_currency.pt")


if __name__ == "__main__":
    main()
