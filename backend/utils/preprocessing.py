"""
Indian Currency Detection - Image Preprocessing Utilities
"""
import cv2
import numpy as np
from PIL import Image
import io


def preprocess_image(image: np.ndarray, target_size: tuple = (224, 224)) -> np.ndarray:
    """
    Full preprocessing pipeline for currency detection.
    Steps: Resize -> Gaussian Blur -> CLAHE -> Noise Reduction -> Normalize
    """
    # Step 1: Resize
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    # Step 2: Convert to LAB for CLAHE
    lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
    l_channel, a_channel, b_channel = cv2.split(lab)

    # Step 3: CLAHE contrast enhancement
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)

    # Step 4: Merge back
    enhanced_lab = cv2.merge([l_enhanced, a_channel, b_channel])
    enhanced = cv2.cvtColor(enhanced_lab, cv2.COLOR_LAB2BGR)

    # Step 5: Gaussian blur (mild - preserves features)
    blurred = cv2.GaussianBlur(enhanced, (3, 3), 0)

    # Step 6: Noise reduction
    denoised = cv2.fastNlMeansDenoisingColored(blurred, None, 6, 6, 7, 21)

    # Step 7: Normalize to [0, 1]
    normalized = denoised.astype(np.float32) / 255.0

    return normalized


def preprocess_for_yolo(image: np.ndarray, target_size: int = 640) -> np.ndarray:
    """Preprocess image for YOLO detection"""
    h, w = image.shape[:2]
    scale = target_size / max(h, w)
    new_w, new_h = int(w * scale), int(h * scale)
    resized = cv2.resize(image, (new_w, new_h), interpolation=cv2.INTER_LINEAR)

    # Pad to square
    canvas = np.full((target_size, target_size, 3), 114, dtype=np.uint8)
    pad_h = (target_size - new_h) // 2
    pad_w = (target_size - new_w) // 2
    canvas[pad_h:pad_h + new_h, pad_w:pad_w + new_w] = resized

    return canvas


def preprocess_for_cnn(image: np.ndarray, target_size: tuple = (224, 224)) -> np.ndarray:
    """Preprocess image for CNN classification"""
    resized = cv2.resize(image, target_size, interpolation=cv2.INTER_AREA)

    # CLAHE enhancement
    lab = cv2.cvtColor(resized, cv2.COLOR_BGR2LAB)
    l_channel, a, b = cv2.split(lab)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    l_enhanced = clahe.apply(l_channel)
    enhanced = cv2.merge([l_enhanced, a, b])
    enhanced = cv2.cvtColor(enhanced, cv2.COLOR_LAB2BGR)

    # Normalize for PyTorch (ImageNet stats)
    normalized = enhanced.astype(np.float32) / 255.0
    mean = np.array([0.485, 0.456, 0.406])
    std = np.array([0.229, 0.224, 0.225])
    normalized = (normalized - mean) / std

    # HWC -> CHW
    normalized = np.transpose(normalized, (2, 0, 1))

    return normalized


def bytes_to_cv2(image_bytes: bytes) -> np.ndarray:
    """Convert bytes to OpenCV image"""
    nparr = np.frombuffer(image_bytes, np.uint8)
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image


def cv2_to_bytes(image: np.ndarray, ext: str = ".jpg") -> bytes:
    """Convert OpenCV image to bytes"""
    _, buffer = cv2.imencode(ext, image)
    return buffer.tobytes()


def base64_to_cv2(base64_string: str) -> np.ndarray:
    """Convert base64 string to OpenCV image"""
    import base64
    img_data = base64.b64decode(base64_string)
    return bytes_to_cv2(img_data)
