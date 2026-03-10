"""
Indian Currency Detection - Detection Routes
"""
import os
import uuid
import base64
from datetime import datetime
from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, Body
from typing import Optional

from config import settings
from models.schemas import DetectionResult, MultiDetectionResult
from utils.auth import get_current_user
from detection.pipeline import pipeline
from database.connection import get_database

router = APIRouter(prefix="/api", tags=["Detection"])


@router.post("/detect")
async def detect_currency(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Upload image detection endpoint.
    Runs the full multi-stage detection pipeline.
    """
    # Validate file
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    # Read image bytes
    image_bytes = await file.read()
    if len(image_bytes) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Save uploaded image
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    # Run detection pipeline
    result = pipeline.detect_from_bytes(image_bytes)

    # Save to history
    db = get_database()
    if db is not None:
        history_doc = {
            "user_id": current_user["user_id"],
            "image_path": filename,
            "prediction": result.get("denomination", 0),
            "confidence": result.get("confidence", 0.0),
            "ocr_text": result.get("ocr_text", ""),
            "is_fake": result.get("is_fake", False),
            "detection_type": "upload",
            "date": datetime.utcnow(),
        }
        await db.detection_history.insert_one(history_doc)

    return {
        "success": True,
        "data": {
            "denomination": result.get("denomination", 0),
            "confidence": result.get("confidence", 0.0),
            "ocr_text": result.get("ocr_text", ""),
            "is_fake": result.get("is_fake", False),
            "fake_indicators": result.get("fake_indicators", []),
            "processing_time": result.get("processing_time", 0),
            "bounding_box": result.get("bounding_box", {}),
            "status": result.get("status", "unknown"),
            "cnn_confidence": result.get("cnn_confidence", 0.0),
            "ocr_confidence": result.get("ocr_confidence", 0.0),
        },
    }


@router.post("/live-detect")
async def live_detect_currency(
    body: dict = Body(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Live camera detection endpoint.
    Accepts base64-encoded frame from webcam.
    """
    frame_data = body.get("frame", "")
    if not frame_data:
        raise HTTPException(status_code=400, detail="No frame data provided")

    # Remove data URL prefix if present
    if "base64," in frame_data:
        frame_data = frame_data.split("base64,")[1]

    # Run detection
    result = pipeline.detect_from_base64(frame_data)

    # Save to history (less frequently for live detection)
    db = get_database()
    if db is not None and result.get("confidence", 0) > settings.CONFIDENCE_THRESHOLD:
        history_doc = {
            "user_id": current_user["user_id"],
            "image_path": "",
            "prediction": result.get("denomination", 0),
            "confidence": result.get("confidence", 0.0),
            "ocr_text": result.get("ocr_text", ""),
            "is_fake": result.get("is_fake", False),
            "detection_type": "live",
            "date": datetime.utcnow(),
        }
        await db.detection_history.insert_one(history_doc)

    return {
        "success": True,
        "data": {
            "denomination": result.get("denomination", 0),
            "confidence": result.get("confidence", 0.0),
            "ocr_text": result.get("ocr_text", ""),
            "is_fake": result.get("is_fake", False),
            "processing_time": result.get("processing_time", 0),
            "bounding_box": result.get("bounding_box", {}),
            "status": result.get("status", "unknown"),
        },
    }


@router.post("/detect-multiple")
async def detect_multiple_currencies(
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    """
    Multi-note detection endpoint.
    Detects multiple currency notes in a single image.
    """
    if not file.content_type or not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File must be an image")

    image_bytes = await file.read()
    if len(image_bytes) > settings.MAX_FILE_SIZE:
        raise HTTPException(status_code=400, detail="File too large (max 10MB)")

    # Save image
    upload_dir = os.path.abspath(settings.UPLOAD_DIR)
    os.makedirs(upload_dir, exist_ok=True)
    filename = f"{uuid.uuid4().hex}_{file.filename}"
    filepath = os.path.join(upload_dir, filename)
    with open(filepath, "wb") as f:
        f.write(image_bytes)

    # Run multi-detection
    from utils.preprocessing import bytes_to_cv2
    image = bytes_to_cv2(image_bytes)
    result = pipeline.detect_multiple(image)

    # Save to history
    db = get_database()
    if db is not None:
        for det in result.get("detections", []):
            history_doc = {
                "user_id": current_user["user_id"],
                "image_path": filename,
                "prediction": det.get("denomination", 0),
                "confidence": det.get("confidence", 0.0),
                "ocr_text": det.get("ocr_text", ""),
                "is_fake": det.get("is_fake", False),
                "detection_type": "multi",
                "date": datetime.utcnow(),
            }
            await db.detection_history.insert_one(history_doc)

    return {
        "success": True,
        "data": result,
    }
