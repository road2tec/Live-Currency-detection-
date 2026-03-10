@echo off
:: ============================================================
::  Indian Currency Detection - Windows Setup Script
::  Run this once on a new machine to get fully set up.
:: ============================================================

title Indian Currency Detection - Setup

echo.
echo ============================================================
echo   Indian Currency Detection System - Setup
echo ============================================================
echo.

:: ── Check Python ───────────────────────────────────────────
echo [1/6] Checking Python installation...
python --version 2>nul
IF ERRORLEVEL 1 (
    echo [ERROR] Python is not installed or not in PATH.
    echo         Please install Python 3.10.x from https://www.python.org/downloads/
    pause
    exit /b 1
)
echo       Python found!

:: ── Check Node.js ──────────────────────────────────────────
echo [2/6] Checking Node.js installation...
node --version 2>nul
IF ERRORLEVEL 1 (
    echo [ERROR] Node.js is not installed or not in PATH.
    echo         Please install Node.js 18+ from https://nodejs.org/
    pause
    exit /b 1
)
echo       Node.js found!

:: ── Check MongoDB ──────────────────────────────────────────
echo [3/6] Checking MongoDB...
mongod --version 2>nul
IF ERRORLEVEL 1 (
    echo [WARNING] MongoDB not found in PATH.
    echo           Make sure MongoDB is installed and running on localhost:27017
    echo           Download from: https://www.mongodb.com/try/download/community
) ELSE (
    echo       MongoDB found!
)

:: ── Backend Setup ──────────────────────────────────────────
echo.
echo [4/6] Setting up Backend (Python virtual environment)...
cd /d "%~dp0backend"

IF NOT EXIST "venv" (
    echo       Creating virtual environment...
    python -m venv venv
)
echo       Activating virtual environment...
call venv\Scripts\activate

echo       Installing Python dependencies (this may take a few minutes)...
pip install --upgrade pip
pip install -r requirements.txt
echo       Backend dependencies installed!

:: ── .env setup ─────────────────────────────────────────────
echo.
echo [5/6] Setting up environment configuration...
IF NOT EXIST ".env" (
    copy ".env.example" ".env"
    echo       Created .env from .env.example
    echo       [IMPORTANT] Please open backend\.env and fill in your credentials.
) ELSE (
    echo       .env already exists - skipping.
)

:: ── Frontend Setup ─────────────────────────────────────────
echo.
echo [6/6] Setting up Frontend (Node.js)...
cd /d "%~dp0frontend"
echo       Installing Node dependencies...
npm install
echo       Frontend dependencies installed!

:: ── Done ───────────────────────────────────────────────────
echo.
echo ============================================================
echo   Setup Complete!
echo ============================================================
echo.
echo  NEXT STEPS:
echo    1. Open backend\.env and fill in your credentials
echo       (MongoDB URI, Google Vision API Key, JWT Secret)
echo    2. Make sure MongoDB is running
echo    3. Run start.bat to launch the application
echo.
pause
