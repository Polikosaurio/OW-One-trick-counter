@echo off
REM OW2 One Trick Counter - Launcher
REM v.0.0.0

echo Starting OW2 One Trick Counter...

cd /d "%~dp0"

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+
    pause
    exit /b 1
)

REM Check dependencies
pip show customtkinter >nul 2>&1
if errorlevel 1 (
    echo Installing dependencies...
    pip install -r requirements.txt
)

REM Launch application
python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Application failed to start
    pause
)