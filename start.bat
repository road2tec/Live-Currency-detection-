@echo off
:: ============================================================
::  Indian Currency Detection - Application Launcher
::  Run this every time you want to start the application.
:: ============================================================

title Indian Currency Detection - Launcher

echo.
echo ============================================================
echo   Indian Currency Detection System - Starting...
echo ============================================================
echo.

:: ── Start Backend ──────────────────────────────────────────
echo Starting Backend server (FastAPI on port 8000)...
cd /d "%~dp0backend"
start "Currency Detection - Backend" cmd /k "call venv\Scripts\activate && python main.py"

:: Wait 3 seconds for backend to start
timeout /t 3 /nobreak >nul

:: ── Start Frontend ─────────────────────────────────────────
echo Starting Frontend server (React on port 5173)...
cd /d "%~dp0frontend"
start "Currency Detection - Frontend" cmd /k "npm run dev"

echo.
echo ============================================================
echo  Application is starting!
echo  Backend  : http://localhost:8000
echo  Frontend : http://localhost:5173
echo  API Docs : http://localhost:8000/docs
echo ============================================================
echo.
echo  Close the two terminal windows to stop the application.
pause
