@echo off
REM Background Sync Agent Startup Script
REM Starts the continuous Robinhood position sync service

echo ======================================
echo Magnus Background Sync Agent
echo ======================================
echo.
echo Starting background sync service...
echo Syncing Robinhood positions every 5 minutes
echo.
echo Press Ctrl+C to stop the service
echo.
echo Logs will be written to: background_sync.log
echo ======================================
echo.

REM Activate virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
)

REM Start the background sync agent
python -m src.services.background_sync_agent

echo.
echo Background Sync Agent stopped.
pause
