"""
🇮🇳 Indian Currency Detection - FastAPI Backend
Multi-stage AI pipeline: YOLOv8 + ResNet50 CNN + OCR Verification

Author: AI Currency Detection System
"""
import os
import sys
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

# Add current directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from config import settings
from database.connection import connect_to_mongo, close_mongo_connection
from routes.auth import router as auth_router
from routes.detection import router as detection_router
from routes.history import router as history_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan: startup and shutdown events"""
    # Startup
    print("=" * 60)
    print("🇮🇳 Indian Currency Detection System - Starting Up (YOLO-only)")
    print("=" * 60)

    # Connect to MongoDB
    await connect_to_mongo()

    # Pre-load AI models
    print("🤖 Loading AI models...")
    from detection.pipeline import pipeline
    try:
        pipeline.load_models()
    except Exception as e:
        print(f"⚠️ Model loading warning: {e}")
        print("   Models will load on first detection request")

    # Create upload directory
    os.makedirs(os.path.abspath(settings.UPLOAD_DIR), exist_ok=True)

    print("✅ Server ready!")
    print(f"📡 API: http://localhost:{settings.PORT}")
    print(f"📡 Docs: http://localhost:{settings.PORT}/docs")
    print("=" * 60)

    yield

    # Shutdown
    await close_mongo_connection()
    print("👋 Server shut down")


# Create FastAPI app
app = FastAPI(
    title="Indian Currency Detection API",
    description="AI-powered Indian Currency Detection using YOLOv8 + ResNet50 CNN + OCR",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173", "http://127.0.0.1:3000", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files for uploads
uploads_dir = os.path.abspath(settings.UPLOAD_DIR)
os.makedirs(uploads_dir, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=uploads_dir), name="uploads")

# Include routers
app.include_router(auth_router)
app.include_router(detection_router)
app.include_router(history_router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "🇮🇳 Indian Currency Detection API",
        "version": "1.0.0",
        "status": "running",
        "endpoints": {
            "docs": "/docs",
            "register": "POST /api/register",
            "login": "POST /api/login",
            "detect": "POST /api/detect",
            "live_detect": "POST /api/live-detect",
            "history": "GET /api/history",
            "stats": "GET /api/stats",
        },
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    from detection.pipeline import pipeline
    return {
        "status": "healthy",
        "models_loaded": pipeline._models_loaded,
        "mode": "yolo_only",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host=settings.HOST,
        port=settings.PORT,
        reload=False,
        log_level="info",
    )
