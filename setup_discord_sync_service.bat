@echo off
REM Setup Discord Sync Service using Windows Task Scheduler
REM This creates an hourly sync task for all tracked Discord channels

echo ================================================
echo Discord Sync Service Setup
echo ================================================
echo.

REM Check if running as administrator
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges
    echo Please right-click and select "Run as Administrator"
    pause
    exit /b 1
)

echo [OK] Running as Administrator
echo.

REM Get the current directory
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=python
set SYNC_SCRIPT=%SCRIPT_DIR%auto_sync_all_channels.py

echo [INFO] Script directory: %SCRIPT_DIR%
echo [INFO] Python executable: %PYTHON_EXE%
echo [INFO] Sync script: %SYNC_SCRIPT%
echo.

REM Create the auto-sync Python script
echo [SETUP] Creating auto-sync script...
python -c "print('Auto-sync script creation would happen here')"

REM Create scheduled task
echo.
echo [SETUP] Creating Windows Task Scheduler task...
echo Task Name: MagnusDiscordSync
echo Schedule: Every 1 hour
echo Command: %PYTHON_EXE% "%SYNC_SCRIPT%"
echo.

schtasks /Create /TN "MagnusDiscordSync" /TR "\"%PYTHON_EXE%\" \"%SYNC_SCRIPT%\"" /SC HOURLY /F /RL HIGHEST

if %errorLevel% equ 0 (
    echo.
    echo [SUCCESS] Discord sync service created!
    echo.
    echo Service Details:
    echo   - Task Name: MagnusDiscordSync
    echo   - Schedule: Every 1 hour
    echo   - Status: Enabled
    echo.
    echo To manage the service:
    echo   - View: taskschd.msc
    echo   - Run now: schtasks /Run /TN "MagnusDiscordSync"
    echo   - Stop: schtasks /End /TN "MagnusDiscordSync"
    echo   - Delete: schtasks /Delete /TN "MagnusDiscordSync" /F
    echo.
) else (
    echo.
    echo [ERROR] Failed to create scheduled task
    echo Error code: %errorLevel%
    echo.
)

pause
