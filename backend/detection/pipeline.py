"""
Indian Currency Detection - YOLO-Only Detection Pipeline
Stage 1: YOLO Detection (denomination + bounding box)
Stage 2: OCR Verification (optional text validation)
"""
import os
import sys
import cv2
import time
import numpy as np
from typing import List

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config import settings
from detection.ocr_verification import perform_ocr_verification
from utils.preprocessing import bytes_to_cv2, cv2_to_bytes

# Currency denomination mapping
CLASS_TO_DENOMINATION = {0: 10, 1: 20, 2: 50, 3: 100, 4: 200, 5: 500, 6: 2000}


class CurrencyDetectionPipeline:
    """
    YOLO-only currency detection pipeline.
    Stage 1: YOLO detection (denomination + bounding box)
    Stage 2: OCR verification (optional, text-based validation)
    """

    def __init__(self):
        self.yolo_model = None
        self.confidence_threshold = settings.CONFIDENCE_THRESHOLD
        self._models_loaded = False
        print("🔧 Detection pipeline initialized (YOLO-only mode)")

    def load_models(self):
        """Load YOLO model only"""
        if self._models_loaded:
            return

        try:
            yolo_path = settings.YOLO_MODEL_PATH
            if os.path.exists(yolo_path):
                from ultralytics import YOLO
                self.yolo_model = YOLO(yolo_path)
                print("✅ YOLO model loaded")
            else:
                print(f"⚠️ YOLO model not found at {yolo_path}")
        except Exception as e:
            print(f"⚠️ YOLO model load error: {e}")

        self._models_loaded = True

    def detect_currency_region(self, image: np.ndarray) -> List[dict]:
        """
        Stage 1: Detect currency note regions using YOLO.
        Falls back to full-image region if YOLO finds nothing.
        """
        regions = []

        if self.yolo_model is not None:
            try:
                results = self.yolo_model(image, conf=0.3, verbose=False)
                for result in results:
                    boxes = result.boxes
                    if boxes is not None:
                        for box in boxes:
                            x1, y1, x2, y2 = map(int, box.xyxy[0].tolist())
                            conf = float(box.conf[0])
                            cls_id = int(box.cls[0]) if box.cls is not None else -1
                            yolo_denom = CLASS_TO_DENOMINATION.get(cls_id, 0)
                            regions.append({
                                "bbox": [x1, y1, x2, y2],
                                "confidence": conf,
                                "crop": image[y1:y2, x1:x2],
                                "yolo_denomination": yolo_denom,
                            })
            except Exception as e:
                print(f"⚠️ YOLO detection error: {e}")

        # Fallback: use entire image, denomination unknown
        if not regions:
            h, w = image.shape[:2]
            regions.append({
                "bbox": [0, 0, w, h],
                "confidence": 0.5,
                "crop": image.copy(),
                "yolo_denomination": 0,
            })

        return regions

    def verify_with_ocr(self, crop: np.ndarray, predicted_denomination: int) -> dict:
        """Stage 2: OCR verification (optional)"""
        try:
            image_bytes = cv2_to_bytes(crop)
            return perform_ocr_verification(image_bytes, predicted_denomination)
        except Exception as e:
            print(f"⚠️ OCR verification error: {e}")
            return {
                "ocr_text": "",
                "is_valid": False,
                "ocr_confidence": 0.0,
                "fake_indicators": ["OCR_ERROR"],
                "matched_text": "",
            }

    def make_final_decision(self, yolo_denomination: int, yolo_conf: float, ocr_result: dict) -> dict:
        """
        Final decision: YOLO is the sole source of denomination.
        OCR is used only for fake-note detection when available.
        """
        final_denom = yolo_denomination
        ocr_conf = ocr_result.get("ocr_confidence", 0.0)
        ocr_valid = ocr_result.get("is_valid", False)
        ocr_text = ocr_result.get("ocr_text", "")
        fake_indicators = ocr_result.get("fake_indicators", [])

        # Confidence: use YOLO confidence directly
        final_confidence = round(yolo_conf, 4)

        # Status
        if yolo_denomination == 0:
            status = "uncertain"
            final_confidence = 0.0
        elif ocr_valid:
            status = "confirmed"
            # Slight boost when OCR agrees
            final_confidence = min(0.99, yolo_conf * 0.85 + ocr_conf * 0.15)
        elif yolo_conf >= 0.85:
            status = "confirmed"
        elif yolo_conf >= 0.6:
            status = "probable"
        else:
            status = "uncertain"

        # Fake detection: only when OCR is actually working and raises real flags
        is_fake = False
        ocr_working = "OCR_UNAVAILABLE" not in fake_indicators and "NO_TEXT_DETECTED" not in fake_indicators and "OCR_ERROR" not in fake_indicators
        if ocr_working and len(fake_indicators) >= 2:
            is_fake = True

        return {
            "denomination": final_denom,
            "confidence": round(final_confidence, 4),
            "ocr_text": ocr_text[:200] if ocr_text else "",
            "is_fake": is_fake,
            "fake_indicators": fake_indicators,
            "status": status,
            "ocr_confidence": round(ocr_conf, 4),
        }

    def detect_single(self, image: np.ndarray) -> dict:
        """Run YOLO-only detection pipeline on a single image."""
        self.load_models()
        start_time = time.time()

        # Stage 1: YOLO detect
        regions = self.detect_currency_region(image)

        if not regions:
            return {
                "denomination": 0,
                "confidence": 0.0,
                "ocr_text": "",
                "is_fake": False,
                "status": "uncertain",
                "processing_time": time.time() - start_time,
                "error": "No currency detected",
            }

        # Best region = highest YOLO confidence
        best_region = max(regions, key=lambda r: r["confidence"])
        yolo_denom = best_region["yolo_denomination"]
        yolo_conf = best_region["confidence"]
        crop = best_region["crop"]

        print(f"  🔍 YOLO: ₹{yolo_denom} ({yolo_conf:.1%})")

        # Stage 2: OCR verification (skipped if no denomination detected)
        if yolo_denom > 0:
            ocr_result = self.verify_with_ocr(crop, yolo_denom)
        else:
            ocr_result = {
                "ocr_text": "", "is_valid": False,
                "ocr_confidence": 0.0, "fake_indicators": ["OCR_UNAVAILABLE"], "matched_text": ""
            }

        # Final decision
        final = self.make_final_decision(yolo_denom, yolo_conf, ocr_result)
        final["processing_time"] = round(time.time() - start_time, 3)
        final["bounding_box"] = {
            "x1": best_region["bbox"][0],
            "y1": best_region["bbox"][1],
            "x2": best_region["bbox"][2],
            "y2": best_region["bbox"][3],
        }

        return final

    def detect_multiple(self, image: np.ndarray) -> dict:
        """Detect multiple currency notes in a single image."""
        self.load_models()
        start_time = time.time()

        regions = self.detect_currency_region(image)
        detections = []
        total_value = 0

        for region in regions:
            yolo_denom = region["yolo_denomination"]
            yolo_conf = region["confidence"]
            crop = region["crop"]

            # OCR only when YOLO has a denomination
            if yolo_denom > 0:
                ocr_result = self.verify_with_ocr(crop, yolo_denom)
            else:
                ocr_result = {
                    "ocr_text": "", "is_valid": False,
                    "ocr_confidence": 0.0, "fake_indicators": ["OCR_UNAVAILABLE"], "matched_text": ""
                }

            final = self.make_final_decision(yolo_denom, yolo_conf, ocr_result)
            final["bounding_box"] = {
                "x1": region["bbox"][0],
                "y1": region["bbox"][1],
                "x2": region["bbox"][2],
                "y2": region["bbox"][3],
            }

            detections.append(final)
            if not final["is_fake"] and final["confidence"] >= self.confidence_threshold:
                total_value += final["denomination"]

        return {
            "detections": detections,
            "total_value": total_value,
            "total_notes": len(detections),
            "processing_time": round(time.time() - start_time, 3),
        }

    def detect_from_bytes(self, image_bytes: bytes) -> dict:
        """Detect from raw image bytes"""
        image = bytes_to_cv2(image_bytes)
        if image is None:
            return {"error": "Invalid image data", "denomination": 0, "confidence": 0.0}
        return self.detect_single(image)

    def detect_from_base64(self, base64_string: str) -> dict:
        """Detect from base64 encoded image"""
        from utils.preprocessing import base64_to_cv2
        image = base64_to_cv2(base64_string)
        if image is None:
            return {"error": "Invalid base64 image", "denomination": 0, "confidence": 0.0}
        return self.detect_single(image)


# Global pipeline instance
pipeline = CurrencyDetectionPipeline()
