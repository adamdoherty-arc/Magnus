@echo off
REM ============================================================
REM Magnus Background Sync - Windows Service Installation
REM ============================================================
REM
REM This script installs the background sync agent as a Windows service
REM using NSSM (Non-Sucking Service Manager)
REM
REM Prerequisites:
REM   1. NSSM must be downloaded and in PATH or current directory
REM   2. Run this script as Administrator
REM ============================================================

echo.
echo ============================================================
echo Magnus Background Sync - Service Installation
echo ============================================================
echo.

REM Check for Administrator privileges
net session >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] This script requires Administrator privileges
    echo Please right-click and select "Run as Administrator"
    echo.
    pause
    exit /b 1
)

echo [OK] Running with Administrator privileges
echo.

REM Set paths
set SCRIPT_DIR=%~dp0
set PYTHON_EXE=%SCRIPT_DIR%venv\Scripts\python.exe
set WORK_DIR=%SCRIPT_DIR%
set SERVICE_NAME=MagnusBackgroundSync

REM Check if Python exists
if not exist "%PYTHON_EXE%" (
    echo [ERROR] Python not found at: %PYTHON_EXE%
    echo Please ensure virtual environment is set up correctly
    echo.
    pause
    exit /b 1
)

echo [OK] Found Python at: %PYTHON_EXE%
echo.

REM Check if NSSM is available (check local directory first, then PATH)
set NSSM_EXE=
if exist "%SCRIPT_DIR%nssm.exe" (
    set NSSM_EXE=%SCRIPT_DIR%nssm.exe
    echo [OK] Found NSSM in current directory
) else (
    where nssm >nul 2>&1
    if %errorLevel% equ 0 (
        set NSSM_EXE=nssm
        echo [OK] Found NSSM in PATH
    ) else (
        echo [ERROR] NSSM not found
        echo.
        echo Please download NSSM from: https://nssm.cc/download
        echo.
        echo Options:
        echo   1. Download nssm-2.24.zip from https://nssm.cc/download
        echo   2. Extract nssm.exe from win64 folder
        echo   3. Either:
        echo      - Copy nssm.exe to this directory (%SCRIPT_DIR%)
        echo      - OR add NSSM to your system PATH
        echo.
        echo Then run this script again
        echo.
        pause
        exit /b 1
    )
)
echo.

REM Check if service already exists
sc query %SERVICE_NAME% >nul 2>&1
if %errorLevel% equ 0 (
    echo [WARNING] Service '%SERVICE_NAME%' already exists
    echo.
    choice /C YN /M "Do you want to remove and reinstall the service"
    if errorlevel 2 (
        echo Installation cancelled
        pause
        exit /b 0
    )

    echo.
    echo Stopping existing service...
    "%NSSM_EXE%" stop %SERVICE_NAME%
    timeout /t 2 /nobreak >nul

    echo Removing existing service...
    "%NSSM_EXE%" remove %SERVICE_NAME% confirm
    timeout /t 2 /nobreak >nul
    echo [OK] Existing service removed
    echo.
)

echo Installing service...
echo.

REM Install the service
"%NSSM_EXE%" install %SERVICE_NAME% "%PYTHON_EXE%" "-m src.services.background_sync_agent"

if %errorLevel% neq 0 (
    echo [ERROR] Failed to install service
    pause
    exit /b 1
)

echo [OK] Service installed
echo.

REM Configure service
echo Configuring service...

REM Set working directory
"%NSSM_EXE%" set %SERVICE_NAME% AppDirectory "%WORK_DIR%"

REM Set description
"%NSSM_EXE%" set %SERVICE_NAME% Description "Magnus Background Position Sync Service - Syncs Robinhood positions every 5 minutes"

REM Set display name
"%NSSM_EXE%" set %SERVICE_NAME% DisplayName "Magnus Background Sync"

REM Set startup type to automatic
"%NSSM_EXE%" set %SERVICE_NAME% Start SERVICE_AUTO_START

REM Set log files
"%NSSM_EXE%" set %SERVICE_NAME% AppStdout "%WORK_DIR%background_sync_stdout.log"
"%NSSM_EXE%" set %SERVICE_NAME% AppStderr "%WORK_DIR%background_sync_stderr.log"

REM Set restart behavior (restart on failure)
"%NSSM_EXE%" set %SERVICE_NAME% AppExit Default Restart
"%NSSM_EXE%" set %SERVICE_NAME% AppRestartDelay 5000

echo [OK] Service configured
echo.

echo Starting service...
"%NSSM_EXE%" start %SERVICE_NAME%

if %errorLevel% neq 0 (
    echo [WARNING] Failed to start service automatically
    echo You can start it manually with: "%NSSM_EXE%" start %SERVICE_NAME%
) else (
    echo [OK] Service started successfully
)

echo.
timeout /t 3 /nobreak >nul

REM Show service status
echo.
echo ============================================================
echo Service Status:
echo ============================================================
sc query %SERVICE_NAME%

echo.
echo ============================================================
echo Service Installed Successfully!
echo ============================================================
echo.
echo Service Name: %SERVICE_NAME%
echo Display Name: Magnus Background Sync
echo Startup Type: Automatic (starts on boot)
echo Working Directory: %WORK_DIR%
echo.
echo Logs:
echo   - Main log: background_sync.log
echo   - Stdout: background_sync_stdout.log
echo   - Stderr: background_sync_stderr.log
echo.
echo Management Commands:
echo   - Check status:  sc query %SERVICE_NAME%
echo   - Start service: nssm start %SERVICE_NAME%
echo   - Stop service:  nssm stop %SERVICE_NAME%
echo   - Restart:       nssm restart %SERVICE_NAME%
echo   - Remove:        nssm remove %SERVICE_NAME% confirm
echo.
echo The service will now sync Robinhood positions every 5 minutes
echo automatically, even when you're not logged in!
echo.
echo ============================================================
pause
