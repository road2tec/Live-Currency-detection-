# 🇮🇳 Live Indian Currency Detection System

An AI-powered Indian Currency Detection system using **YOLOv8**, **ResNet50 CNN**, and **OCR Verification**.  
Supports both **image upload** and **live webcam detection**.

---

## 🧰 Tech Stack

| Layer       | Technology                         |
|-------------|-------------------------------------|
| Frontend    | React 18 + Vite + TailwindCSS       |
| Backend     | FastAPI (Python 3.10)               |
| AI Models   | YOLOv8 + ResNet50 CNN               |
| OCR         | Google Vision API                   |
| Database    | MongoDB                             |
| Auth        | JWT (JSON Web Tokens)               |

---

## ✅ Prerequisites

Install the following **before** running setup:

| Software      | Version     | Download Link                                      |
|---------------|-------------|-----------------------------------------------------|
| Python        | 3.10.x      | https://www.python.org/downloads/                  |
| Node.js       | 18+         | https://nodejs.org/                                |
| MongoDB       | 6.x         | https://www.mongodb.com/try/download/community     |
| Git           | Latest      | https://git-scm.com/downloads                      |

> **⚠️ Important:** During Python installation, make sure to check **"Add Python to PATH"**.

---

## � Quick Setup (Windows)

### Step 1 — Clone the Repository
```bash
git clone https://github.com/road2tec/Live-Currency-detection-
cd Live-Currency-detection-
```

### Step 2 — Run Setup Script
Double-click `setup.bat` OR run in terminal:
```bash
setup.bat
```
This will:
- Create a Python virtual environment
- Install all backend Python packages
- Install all frontend Node packages
- Create your `.env` file from the template

### Step 3 — Configure Environment Variables
Open `backend/.env` and fill in your credentials:

```env
MONGO_URI=mongodb://localhost:27017/currency_detection
SECRET_KEY=your-random-secret-key-here
GOOGLE_VISION_API_KEY=your-google-vision-api-key
```

See the [Environment Variables](#-environment-variables) section below for details.

### Step 4 — Start MongoDB
Make sure MongoDB is running on your machine:
```bash
# If installed as a service it starts automatically.
# Otherwise run:
mongod --dbpath C:\data\db
```

### Step 5 — Launch the Application
Double-click `start.bat` OR run:
```bash
start.bat
```

The application will open:
- 🌐 **Frontend**: http://localhost:5173
- ⚙️ **Backend API**: http://localhost:8000
- 📄 **API Docs**: http://localhost:8000/docs

---

## 🔧 Manual Setup (Step-by-Step)

If you prefer to run things manually:

### Backend
```bash
cd backend
python -m venv venv
venv\Scripts\activate        # Windows
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd frontend
npm install
npm run dev
```

---

## 🔐 Environment Variables

Copy `backend/.env.example` → `backend/.env` and fill in the values:

| Variable                       | Description                                  | Default                                |
|-------------------------------|----------------------------------------------|----------------------------------------|
| `MONGO_URI`                   | MongoDB connection string                    | `mongodb://localhost:27017/currency_detection` |
| `DB_NAME`                     | MongoDB database name                        | `currency_detection`                   |
| `SECRET_KEY`                  | JWT signing key (keep secret!)               | *(must be changed)*                    |
| `ALGORITHM`                   | JWT algorithm                                | `HS256`                                |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Login session duration in minutes            | `1440` (24 hours)                      |
| `GOOGLE_VISION_API_KEY`       | Google Cloud Vision API key for OCR          | *(required for OCR)*                   |
| `YOLO_MODEL_PATH`             | Path to the YOLO model file                  | `../models/yolo_currency.pt`           |
| `CNN_MODEL_PATH`              | Path to the CNN classifier model file        | `../models/currency_classifier.pth`    |
| `HOST`                        | Backend server host                          | `0.0.0.0`                              |
| `PORT`                        | Backend server port                          | `8000`                                 |
| `UPLOAD_DIR`                  | Directory for uploaded images                | `./uploads`                            |
| `MAX_FILE_SIZE`               | Max upload size in bytes                     | `10485760` (10 MB)                     |
| `CONFIDENCE_THRESHOLD`        | Minimum AI confidence to accept a detection  | `0.85`                                 |

> **💡 Tip:** Generate a strong `SECRET_KEY` by running: `python -c "import secrets; print(secrets.token_hex(32))"`

---

## 🗂️ Project Structure

```
Live-Currency-detection-/
│
├── backend/                    # FastAPI Python backend
│   ├── .env.example            # ← Copy this to .env and fill in credentials
│   ├── .env                    # ← Your actual credentials (NOT committed to Git)
│   ├── requirements.txt        # Python dependencies (pinned versions)
│   ├── main.py                 # FastAPI app entry point
│   ├── config.py               # App configuration loader
│   ├── database/               # MongoDB connection
│   ├── detection/              # AI detection pipeline (YOLO + CNN + OCR)
│   ├── models/                 # Pydantic schemas
│   ├── routes/                 # API route handlers
│   │   ├── auth.py             # Register / Login
│   │   ├── detection.py        # Image & live detection
│   │   └── history.py          # Detection history & stats
│   ├── training/               # Model training scripts
│   └── uploads/                # Uploaded images (auto-created)
│
├── frontend/                   # React + Vite frontend
│   ├── src/                    # React source code
│   ├── package.json            # Node.js dependencies (pinned versions)
│   └── vite.config.js          # Vite configuration
│
├── models/                     # Trained AI model files
│   ├── yolo_currency.pt        # YOLOv8 detection model
│   └── currency_classifier.pth # ResNet50 CNN classifier model
│
├── .gitignore                  # Git ignore rules
├── setup.bat                   # One-click setup script (Windows)
├── start.bat                   # One-click launch script (Windows)
└── README.md                   # This file
```

---

## � Features

- 📷 **Image Upload Detection** — Upload any photo of Indian currency
- 🎥 **Live Webcam Detection** — Real-time currency detection via camera
- 🔐 **User Authentication** — Register/login with JWT-secured sessions
- 📊 **Detection History** — View past detections and statistics
- 🤖 **Multi-Stage AI Pipeline** — YOLOv8 → CNN Classifier → OCR Verification
- 💵 **Supports all denominations** — ₹10, ₹20, ₹50, ₹100, ₹200, ₹500, ₹2000

---

## � Troubleshooting

| Issue | Solution |
|-------|----------|
| `python` not found | Reinstall Python and check "Add to PATH" during install |
| `node` not found | Reinstall Node.js and restart terminal |
| MongoDB connection failed | Start MongoDB service or run `mongod` manually |
| Model file not found | Ensure `models/yolo_currency.pt` and `models/currency_classifier.pth` exist |
| Port 8000 already in use | Change `PORT=8001` in `.env` and update frontend API URL |
| Google Vision API error | Check your `GOOGLE_VISION_API_KEY` in `.env` |

---

## 📞 Support

For any issues, contact the development team.
