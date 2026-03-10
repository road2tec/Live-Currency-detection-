"""
Indian Currency Detection - Pydantic Models
"""
from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List
from datetime import datetime


# ─── Auth Models ───────────────────────────────────────────
class UserRegister(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    email: str = Field(..., min_length=5, max_length=100)
    password: str = Field(..., min_length=6, max_length=128)


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: str
    name: str
    email: str
    created_at: datetime


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse


# ─── Detection Models ─────────────────────────────────────
class DetectionResult(BaseModel):
    denomination: int
    confidence: float
    ocr_text: Optional[str] = None
    is_fake: bool = False
    fake_indicators: Optional[List[str]] = None
    bounding_box: Optional[dict] = None
    method: str = "cnn"


class MultiDetectionResult(BaseModel):
    detections: List[DetectionResult]
    total_value: int
    total_notes: int
    processing_time: float


class DetectionHistoryItem(BaseModel):
    id: Optional[str] = None
    user_id: str
    image_path: Optional[str] = None
    prediction: int
    confidence: float
    ocr_text: Optional[str] = None
    is_fake: bool = False
    detection_type: str = "upload"  # upload or live
    date: datetime = Field(default_factory=datetime.utcnow)


class DetectionHistoryResponse(BaseModel):
    id: str
    prediction: int
    confidence: float
    ocr_text: Optional[str] = None
    is_fake: bool = False
    detection_type: str
    date: datetime
