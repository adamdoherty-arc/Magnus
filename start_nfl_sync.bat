@echo off
REM ========================================================================
REM NFL Real-Time Sync Starter Script
REM ========================================================================
REM Description: Starts the NFL real-time data pipeline background service
REM Usage: Double-click this file or run from command line
REM ========================================================================

echo.
echo ============================================================
echo    NFL REAL-TIME SYNC ENGINE
echo ============================================================
echo.
echo Starting NFL data pipeline...
echo.
echo Features:
echo   - Live game scores (every 5 seconds)
echo   - Play-by-play tracking
echo   - Kalshi market monitoring
echo   - Telegram notifications
echo   - Injury reports
echo.
echo Press Ctrl+C to stop
echo.
echo ============================================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM Activate virtual environment if it exists
if exist venv\Scripts\activate.bat (
    call venv\Scripts\activate.bat
)

REM Run the sync engine
python src/nfl_realtime_sync.py

pause
