"""
Indian Currency Detection - Master Training Script
Runs both YOLO and CNN training pipelines.
"""
import os
import sys
import argparse

def main():
    parser = argparse.ArgumentParser(description="Train Indian Currency Detection Models")
    parser.add_argument("--model", choices=["cnn", "yolo", "all"], default="all",
                        help="Which model to train")
    parser.add_argument("--dataset", default="../Indian Currency Dataset",
                        help="Path to dataset")
    parser.add_argument("--output", default="../models",
                        help="Output directory for models")
    parser.add_argument("--epochs-cnn", type=int, default=30,
                        help="CNN training epochs")
    parser.add_argument("--epochs-yolo", type=int, default=50,
                        help="YOLO training epochs")

    args = parser.parse_args()

    os.environ["DATASET_PATH"] = args.dataset
    os.environ["OUTPUT_DIR"] = args.output

    print("=" * 60)
    print("🇮🇳 Indian Currency Detection - Model Training")
    print("=" * 60)

    if args.model in ["cnn", "all"]:
        print("\n" + "=" * 60)
        print("📦 Stage 1: Training CNN Classifier (ResNet50)")
        print("=" * 60)
        from training.train_cnn import main as train_cnn
        train_cnn()

    if args.model in ["yolo", "all"]:
        print("\n" + "=" * 60)
        print("📦 Stage 2: Training YOLO Detector (YOLOv8l)")
        print("=" * 60)
        from training.train_yolo import main as train_yolo
        train_yolo()

    print("\n" + "=" * 60)
    print("🎉 All training complete!")
    print("=" * 60)
    print(f"\nModels saved to: {os.path.abspath(args.output)}")
    print(f"  - currency_classifier.pth (CNN)")
    print(f"  - yolo_currency.pt (YOLO)")


if __name__ == "__main__":
    main()
