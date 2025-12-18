@echo off
REM ============================================================
REM Magnus Background Sync - Service Uninstallation
REM ============================================================

echo.
echo ============================================================
echo Magnus Background Sync - Service Uninstallation
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

set SCRIPT_DIR=%~dp0
set SERVICE_NAME=MagnusBackgroundSync

REM Check if NSSM is available (check local directory first, then PATH)
set NSSM_EXE=
if exist "%SCRIPT_DIR%nssm.exe" (
    set NSSM_EXE=%SCRIPT_DIR%nssm.exe
) else (
    where nssm >nul 2>&1
    if %errorLevel% equ 0 (
        set NSSM_EXE=nssm
    ) else (
        echo [ERROR] NSSM not found
        echo Please ensure nssm.exe is in the current directory
        echo.
        pause
        exit /b 1
    )
)

REM Check if service exists
sc query %SERVICE_NAME% >nul 2>&1
if %errorLevel% neq 0 (
    echo [INFO] Service '%SERVICE_NAME%' is not installed
    echo Nothing to uninstall
    echo.
    pause
    exit /b 0
)

echo [INFO] Service '%SERVICE_NAME%' found
echo.

REM Confirm uninstallation
choice /C YN /M "Are you sure you want to uninstall the service"
if errorlevel 2 (
    echo.
    echo Uninstallation cancelled
    pause
    exit /b 0
)

echo.
echo Stopping service...
"%NSSM_EXE%" stop %SERVICE_NAME%

echo Waiting for service to stop...
timeout /t 3 /nobreak >nul

echo.
echo Removing service...
"%NSSM_EXE%" remove %SERVICE_NAME% confirm

if %errorLevel% equ 0 (
    echo.
    echo ============================================================
    echo [SUCCESS] Service uninstalled successfully
    echo ============================================================
    echo.
    echo The background sync service has been removed.
    echo.
    echo To reinstall later, run: install_background_sync_service.bat
    echo.
    echo Note: Log files have NOT been deleted:
    echo   - background_sync.log
    echo   - background_sync_stdout.log
    echo   - background_sync_stderr.log
    echo.
    echo You can manually delete these files if needed.
    echo.
) else (
    echo.
    echo [ERROR] Failed to remove service
    echo Please check if NSSM is available and try again
    echo.
)

pause
