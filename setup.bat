@echo off
echo ========================================
echo WHEEL STRATEGY TRADING SYSTEM SETUP
echo ========================================
echo.

REM Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python is not installed or not in PATH
    echo Please install Python 3.9+ from https://www.python.org/
    pause
    exit /b 1
)

echo [1/4] Creating virtual environment...
if not exist "venv" (
    python -m venv venv
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo.
echo [2/4] Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo [3/4] Upgrading pip...
python -m pip install --upgrade pip

echo.
echo [4/4] Installing requirements...
python -m pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo WARNING: Some packages failed to install, but continuing...
)

echo.
echo ========================================
echo SETUP COMPLETE!
echo ========================================
echo.
echo To start the system:
echo   1. Run: venv\Scripts\activate
echo   2. Run: python start.py
echo.
echo Or just run: run.bat
echo.
pause