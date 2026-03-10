"""
Indian Currency Detection - Configuration Module
"""
import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    # MongoDB
    MONGO_URI: str = os.getenv("MONGO_URI", "mongodb://localhost:27017/currency_detection")
    DB_NAME: str = os.getenv("DB_NAME", "currency_detection")

    # JWT
    SECRET_KEY: str = os.getenv("SECRET_KEY", "your-super-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    # Google Vision API
    GOOGLE_VISION_API_KEY: str = os.getenv("GOOGLE_VISION_API_KEY", "")

    # Model Paths
    YOLO_MODEL_PATH: str = os.getenv("YOLO_MODEL_PATH", "../models/yolo_currency.pt")
    CNN_MODEL_PATH: str = os.getenv("CNN_MODEL_PATH", "../models/currency_classifier.pth")

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Upload
    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")
    MAX_FILE_SIZE: int = int(os.getenv("MAX_FILE_SIZE", "10485760"))

    # Detection
    CONFIDENCE_THRESHOLD: float = float(os.getenv("CONFIDENCE_THRESHOLD", "0.85"))

    # Currency classes
    CURRENCY_CLASSES: list = [10, 20, 50, 100, 200, 500, 2000]

    # OCR Patterns
    OCR_PATTERNS: dict = {
        10: ["₹10", "TEN RUPEES", "Reserve Bank of India"],
        20: ["₹20", "TWENTY RUPEES", "Reserve Bank of India"],
        50: ["₹50", "FIFTY RUPEES", "Reserve Bank of India"],
        100: ["₹100", "ONE HUNDRED RUPEES", "Reserve Bank of India"],
        200: ["₹200", "TWO HUNDRED RUPEES", "Reserve Bank of India"],
        500: ["₹500", "FIVE HUNDRED RUPEES", "Reserve Bank of India"],
        2000: ["₹2000", "TWO THOUSAND RUPEES", "Reserve Bank of India"],
    }

    class Config:
        env_file = ".env"
        extra = "allow"


settings = Settings()
