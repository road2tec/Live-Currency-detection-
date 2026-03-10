# 🇮🇳 Indian Currency Detection System

> AI-powered Indian currency detection and classification using **YOLOv8 + ResNet50 CNN + OCR Verification**.

## 🎯 Accuracy Target
- **Image Detection**: 97–99%
- **Live Camera**: 95–98%

## 🏗️ Architecture

```
Image → [YOLOv8 Detection] → [ResNet50 Classification] → [OCR Verification] → Final Result
```

### Multi-Stage Pipeline
1. **Stage 1 – YOLO Detection**: Detect currency note region in image (YOLOv8l)
2. **Stage 2 – CNN Classification**: Classify denomination using ResNet50
3. **Stage 3 – OCR Verification**: Validate text using Google Vision API
4. **Final Decision**: Confidence voting with minimum 0.85 threshold

## 📁 Project Structure

```
currency_detection/
├── backend/
│   ├── main.py                # FastAPI application
│   ├── config.py              # Configuration settings
│   ├── routes/
│   │   ├── auth.py            # Register & Login APIs
│   │   ├── detection.py       # Detection APIs
│   │   └── history.py         # History & Stats APIs
│   ├── detection/
│   │   ├── pipeline.py        # Main detection pipeline
│   │   ├── cnn_model.py       # ResNet50 classifier
│   │   └── ocr_verification.py # OCR validation
│   ├── training/
│   │   ├── train_cnn.py       # CNN training script
│   │   ├── train_yolo.py      # YOLO training script
│   │   └── train_all.py       # Master training script
│   ├── utils/
│   │   ├── auth.py            # JWT authentication
│   │   └── preprocessing.py   # Image preprocessing
│   └── database/
│       └── connection.py      # MongoDB connection
├── frontend/
│   ├── src/
│   │   ├── pages/             # React pages
│   │   ├── components/        # Reusable components
│   │   ├── services/          # API service layer
│   │   └── context/           # Auth context
│   └── package.json
├── models/                     # Trained model files
└── Indian Currency Dataset/    # Training dataset
    ├── 10/ 20/ 50/ 100/ 200/ 500/ 2000/
```

## 🛠️ Tech Stack

| Layer | Technology |
|-------|-----------|
| Frontend | React.js, Tailwind CSS, Vite |
| Backend | Python, FastAPI |
| AI Models | PyTorch, YOLOv8, ResNet50 |
| Computer Vision | OpenCV |
| OCR | Google Vision API |
| Database | MongoDB |
| Auth | JWT + bcrypt |

## 🚀 Quick Start

### Prerequisites
- Python 3.10+
- Node.js 18+
- MongoDB (running on localhost:27017)

### 1. Backend Setup

```bash
cd backend
pip install -r requirements.txt
```

### 2. Train Models

```bash
cd backend

# Train both models
python -m training.train_all --dataset "../Indian Currency Dataset" --output "../models"

# Or train individually
python -m training.train_cnn    # Train ResNet50 CNN
python -m training.train_yolo   # Train YOLOv8
```

### 3. Start Backend Server

```bash
cd backend
python main.py
# Server runs at http://localhost:8000
# API docs at http://localhost:8000/docs
```

### 4. Frontend Setup

```bash
cd frontend
npm install
npm run dev
# App runs at http://localhost:3000
```

## 📡 API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/register` | Register new user |
| POST | `/api/login` | Login & get JWT |
| POST | `/api/detect` | Upload image detection |
| POST | `/api/live-detect` | Live camera detection |
| POST | `/api/detect-multiple` | Multi-note detection |
| GET | `/api/history` | Detection history |
| GET | `/api/stats` | Detection statistics |
| DELETE | `/api/history/{id}` | Delete history item |
| DELETE | `/api/history` | Clear all history |

## 🧠 Detection Response Format

```json
{
  "denomination": 500,
  "confidence": 0.96,
  "ocr_text": "Reserve Bank of India ₹500",
  "is_fake": false,
  "status": "confirmed",
  "processing_time": 0.45
}
```

## 🔐 Authentication

- JWT-based authentication
- Passwords hashed with bcrypt
- Token included in Authorization header: `Bearer <token>`

## 📊 Supported Denominations

| Denomination | Class |
|-------------|-------|
| ₹10 | 0 |
| ₹20 | 1 |
| ₹50 | 2 |
| ₹100 | 3 |
| ₹200 | 4 |
| ₹500 | 5 |
| ₹2000 | 6 |

## 🔧 Image Preprocessing

1. Resize to target dimensions
2. Gaussian blur (mild denoising)
3. CLAHE contrast enhancement
4. Noise reduction (fastNlMeans)
5. Normalization (ImageNet stats)

## 📈 Training Augmentation

- Random rotation (±15°)
- Brightness/contrast changes
- Gaussian blur
- Random noise
- Zoom (0.9–1.1×)
- Perspective distortion
- Mosaic augmentation (YOLO)
- CutMix / MixUp

---

Built with ❤️ using PyTorch, FastAPI, React, and MongoDB.
