"""
Indian Currency Detection - OCR Verification Module
Uses Google Vision API (primary) or pytesseract (local fallback) for text extraction.
"""
import requests
import base64
import re
import cv2
import numpy as np
from typing import Optional, Tuple, List
from config import settings

# Try to import pytesseract for local OCR fallback
try:
    import pytesseract
    from PIL import Image
    import io
    # Common Tesseract install path on Windows
    import os
    _tess_paths = [
        r"C:\Program Files\Tesseract-OCR\tesseract.exe",
        r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    ]
    for _p in _tess_paths:
        if os.path.exists(_p):
            pytesseract.pytesseract.tesseract_cmd = _p
            break
    TESSERACT_AVAILABLE = True
except ImportError:
    TESSERACT_AVAILABLE = False


# Denomination patterns for validation
DENOMINATION_PATTERNS = {
    10:   [r"₹\s*10(?!\d)", r"TEN\s*RUPEES", r"(?<![\d])10(?![\d])", r"दस\s*रुपये"],
    20:   [r"₹\s*20(?!\d)", r"TWENTY\s*RUPEES", r"(?<![\d])20(?![\d])", r"बीस\s*रुपये"],
    50:   [r"₹\s*50(?!\d)", r"FIFTY\s*RUPEES", r"(?<![\d])50(?![\d])", r"पचास\s*रुपये"],
    100:  [r"₹\s*100(?!\d)", r"ONE\s*HUNDRED\s*RUPEES", r"(?<![\d])100(?![\d])", r"एक\s*सौ\s*रुपये"],
    200:  [r"₹\s*200(?!\d)", r"TWO\s*HUNDRED\s*RUPEES", r"(?<![\d])200(?![\d])", r"दो\s*सौ\s*रुपये"],
    500:  [r"₹\s*500(?!\d)", r"FIVE\s*HUNDRED\s*RUPEES", r"(?<![\d])500(?![\d])", r"पाँच\s*सौ\s*रुपये"],
    2000: [r"₹\s*2000(?!\d)", r"TWO\s*THOUSAND\s*RUPEES", r"(?<![\d])2000(?![\d])", r"दो\s*हज़ार\s*रुपये"],
}

RBI_PATTERNS = [
    r"RESERVE\s*BANK\s*OF\s*INDIA",
    r"भारतीय\s*रिज़र्व\s*बैंक",
    r"RBI",
    r"GUARANTEED\s*BY\s*THE\s*CENTRAL\s*GOVERNMENT",
    r"I\s*PROMISE\s*TO\s*PAY",
]


def extract_text_google_vision(image_bytes: bytes) -> Optional[str]:
    """
    Extract text from image using Google Vision API
    """
    api_key = settings.GOOGLE_VISION_API_KEY
    if not api_key:
        return None

    url = f"https://vision.googleapis.com/v1/images:annotate?key={api_key}"

    # Encode image to base64
    image_b64 = base64.b64encode(image_bytes).decode("utf-8")

    payload = {
        "requests": [
            {
                "image": {"content": image_b64},
                "features": [{"type": "TEXT_DETECTION", "maxResults": 10}],
            }
        ]
    }

    try:
        response = requests.post(url, json=payload, timeout=3)
        response.raise_for_status()
        result = response.json()

        if "responses" in result and result["responses"]:
            annotations = result["responses"][0].get("textAnnotations", [])
            if annotations:
                return annotations[0].get("description", "")
    except requests.exceptions.Timeout:
        print("⚠️ Google Vision API timeout")
    except Exception as e:
        print(f"⚠️ Google Vision API error: {e}")

    return None


def _score_ocr_text(text: str) -> int:
    """Score OCR text quality by counting alphabetic characters and currency keywords."""
    if not text:
        return 0
    alpha = sum(1 for c in text if c.isalpha())
    keywords = ["RUPEE", "RESERVE", "BANK", "INDIA", "PROMISE", "PAY", "BEARER",
                 "TEN", "TWENTY", "FIFTY", "HUNDRED", "THOUSAND", "RBI"]
    bonus = sum(50 for kw in keywords if kw in text.upper())
    return alpha + bonus


def extract_text_fallback(image_bytes: bytes) -> Optional[str]:
    """
    Local OCR fallback using pytesseract (Tesseract OCR).
    Tries multiple preprocessing strategies and picks the best result.
    """
    if not TESSERACT_AVAILABLE:
        return None
    try:
        # Decode image
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        if img is None:
            return None

        # Upscale small images for better OCR
        h, w = img.shape[:2]
        scale = max(1.0, 1500 / max(h, w))
        if scale > 1.0:
            img = cv2.resize(img, (int(w * scale), int(h * scale)), interpolation=cv2.INTER_CUBIC)

        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        # Tesseract is very slow. Only use the best 2 strategies with 1 PSM mode to save time.
        candidates = []
        
        # Strategy 1: CLAHE contrast enhancement (best for dark/uneven lighting)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        candidates.append(enhanced)

        # Strategy 2: Otsu threshold (best for high-contrast prints)
        _, otsu = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        candidates.append(otsu)

        best_text = ""
        best_score = 0

        for processed in candidates:
            pil_img = Image.fromarray(processed)
            config = "--psm 11 -l eng" # sparse text mode is best for currency
            text = pytesseract.image_to_string(pil_img, config=config).strip()
            score = _score_ocr_text(text)
            if score > best_score:
                best_score = score
                best_text = text

        if best_text:
            print(f"✅ Tesseract OCR extracted ({best_score} score): {repr(best_text[:100])}")
            return best_text
    except Exception as e:
        print(f"⚠️ Tesseract OCR error: {e}")
    return None


def validate_denomination_ocr(ocr_text: str, predicted_denomination: int) -> Tuple[bool, float, str]:
    """
    Validate predicted denomination against OCR text.

    Returns:
        (is_valid, ocr_confidence, matched_text)
    """
    if not ocr_text:
        return False, 0.0, ""

    text_upper = ocr_text.upper()
    matched_patterns = []
    ocr_confidence = 0.0

    # Check for RBI patterns (authenticity indicator)
    rbi_found = False
    for pattern in RBI_PATTERNS:
        if re.search(pattern, text_upper, re.IGNORECASE):
            rbi_found = True
            ocr_confidence += 0.2
            matched_patterns.append("RBI_VERIFIED")
            break

    # Check denomination patterns
    if predicted_denomination in DENOMINATION_PATTERNS:
        for pattern in DENOMINATION_PATTERNS[predicted_denomination]:
            if re.search(pattern, ocr_text, re.IGNORECASE):
                ocr_confidence += 0.3
                matched_patterns.append(pattern)

    # Check for conflicting denominations
    conflicting = False
    for denom, patterns in DENOMINATION_PATTERNS.items():
        if denom != predicted_denomination:
            for pattern in patterns[:2]:  # Check main patterns only
                if re.search(pattern, ocr_text, re.IGNORECASE):
                    # Make sure it's not a substring match
                    if denom == 100 and predicted_denomination == 2000:
                        continue  # "100" can appear as part of number context
                    conflicting = True
                    ocr_confidence -= 0.2
                    break

    # Cap confidence
    ocr_confidence = max(0.0, min(1.0, ocr_confidence))

    is_valid = ocr_confidence >= 0.3 and not conflicting
    matched_text = " | ".join(matched_patterns) if matched_patterns else ""

    return is_valid, ocr_confidence, matched_text


def detect_fake_indicators(ocr_text: str, predicted_denomination: int) -> List[str]:
    """
    Detect potential fake note indicators from OCR text.
    """
    indicators = []

    if not ocr_text:
        indicators.append("NO_TEXT_DETECTED")
        return indicators

    text_upper = ocr_text.upper()

    # Check if RBI text is present
    rbi_found = any(re.search(p, text_upper, re.IGNORECASE) for p in RBI_PATTERNS)
    if not rbi_found:
        indicators.append("MISSING_RBI_TEXT")

    # Check for denomination text
    denom_found = False
    if predicted_denomination in DENOMINATION_PATTERNS:
        for pattern in DENOMINATION_PATTERNS[predicted_denomination]:
            if re.search(pattern, ocr_text, re.IGNORECASE):
                denom_found = True
                break

    if not denom_found:
        indicators.append("DENOMINATION_TEXT_MISMATCH")

    # Check for spelling errors in common currency text
    expected_words = ["RESERVE", "BANK", "INDIA", "RUPEES", "PROMISE", "PAY", "BEARER"]
    found_partial = sum(1 for w in expected_words if w in text_upper)
    if found_partial < 2:
        indicators.append("INSUFFICIENT_CURRENCY_TEXT")

    return indicators


def perform_ocr_verification(image_bytes: bytes, predicted_denomination: int) -> dict:
    """
    Complete OCR verification pipeline.

    Returns:
        {
            "ocr_text": str,
            "is_valid": bool,
            "ocr_confidence": float,
            "fake_indicators": list,
            "matched_text": str
        }
    """
    # Extract text
    ocr_text = extract_text_google_vision(image_bytes)

    if ocr_text is None:
        ocr_text = extract_text_fallback(image_bytes)

    # Detect if OCR text is just noise/garbage
    # Require: score >= 50 AND at least one known currency keyword
    if ocr_text:
        score = _score_ocr_text(ocr_text)
        currency_keywords = ["RUPEE", "RESERVE", "BANK", "INDIA", "PROMISE", "PAY",
                             "BEARER", "TEN", "TWENTY", "FIFTY", "HUNDRED", "THOUSAND", "RBI"]
        has_keyword = any(kw in ocr_text.upper() for kw in currency_keywords)
        if score < 50 or not has_keyword:
            print(f"  🗑️ Discarding garbage OCR text (score={score}, has_keyword={has_keyword}): {repr(ocr_text[:40])}")
            ocr_text = None  # Discard garbage

    if ocr_text is None:
        return {
            "ocr_text": "",
            "is_valid": False,
            "ocr_confidence": 0.0,
            "fake_indicators": ["OCR_UNAVAILABLE"],
            "matched_text": "",
        }

    # Validate denomination
    is_valid, ocr_confidence, matched_text = validate_denomination_ocr(ocr_text, predicted_denomination)

    # Check for fake indicators
    fake_indicators = detect_fake_indicators(ocr_text, predicted_denomination)

    return {
        "ocr_text": ocr_text.strip()[:500],  # Limit text length
        "is_valid": is_valid,
        "ocr_confidence": ocr_confidence,
        "fake_indicators": fake_indicators,
        "matched_text": matched_text,
    }
