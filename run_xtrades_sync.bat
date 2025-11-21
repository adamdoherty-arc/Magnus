@echo off
REM ============================================================================
REM Xtrades Background Sync Service Launcher
REM ============================================================================
REM
REM This script launches the Xtrades background sync service that automatically
REM fetches new alerts from followed traders every 5 minutes.
REM
REM Usage:
REM   - Double-click to run with default settings (5-minute interval)
REM   - Edit SYNC_INTERVAL below to change frequency
REM   - Press Ctrl+C to stop the service
REM
REM Requirements:
REM   - Python 3.8+ installed
REM   - PostgreSQL database running
REM   - .env file configured with DATABASE_URL and XTRADES credentials
REM ============================================================================

title Xtrades Background Sync Service

echo.
echo ============================================================================
echo  XTRADES BACKGROUND SYNC SERVICE
echo ============================================================================
echo.
echo  This service will automatically sync Xtrades alerts every 5 minutes.
echo  Keep this window open to continue syncing.
echo.
echo  Press Ctrl+C at any time to stop the service.
echo ============================================================================
echo.

REM Configuration
set SYNC_INTERVAL=5

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    echo [INFO] Activating virtual environment...
    call venv\Scripts\activate.bat
)

REM Check Python installation
python --version >nul 2>&1
if errorlevel 1 (
    echo [ERROR] Python is not installed or not in PATH
    echo [ERROR] Please install Python 3.8 or higher
    pause
    exit /b 1
)

REM Check if .env file exists
if not exist .env (
    echo [ERROR] .env file not found
    echo [ERROR] Please create .env file with DATABASE_URL and XTRADES credentials
    pause
    exit /b 1
)

REM Install required packages if needed
echo [INFO] Checking dependencies...
pip install -q schedule psycopg2-binary python-dotenv selenium undetected-chromedriver beautifulsoup4

REM Run the sync service
echo.
echo [INFO] Starting Xtrades sync service with %SYNC_INTERVAL%-minute interval...
echo.

python src\ava\xtrades_background_sync.py --interval %SYNC_INTERVAL%

REM If script exits, pause to see error messages
echo.
echo [INFO] Sync service has stopped.
echo.
pause
