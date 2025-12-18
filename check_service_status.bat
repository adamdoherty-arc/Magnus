@echo off
REM ============================================================
REM Magnus Background Sync - Service Status Check
REM ============================================================

echo.
echo ============================================================
echo Magnus Background Sync - Service Status
echo ============================================================
echo.

set SERVICE_NAME=MagnusBackgroundSync

REM Check if service exists
sc query %SERVICE_NAME% >nul 2>&1
if %errorLevel% neq 0 (
    echo [ERROR] Service '%SERVICE_NAME%' is not installed
    echo.
    echo To install the service, run: install_background_sync_service.bat
    echo.
    pause
    exit /b 1
)

REM Show detailed service status
echo Service Status:
echo ============================================================
sc query %SERVICE_NAME%

echo.
echo.
echo Service Configuration:
echo ============================================================
sc qc %SERVICE_NAME%

echo.
echo.
echo Recent Log Entries (last 20 lines):
echo ============================================================
if exist "background_sync.log" (
    powershell -Command "Get-Content background_sync.log -Tail 20"
) else (
    echo [INFO] Log file not found yet (service may not have started)
)

echo.
echo ============================================================
echo Management Commands:
echo ============================================================
echo   Start service:   nssm start %SERVICE_NAME%
echo   Stop service:    nssm stop %SERVICE_NAME%
echo   Restart service: nssm restart %SERVICE_NAME%
echo   View logs:       type background_sync.log
echo.
pause
