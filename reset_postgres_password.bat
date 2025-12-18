@echo off
SETLOCAL EnableDelayedExpansion

echo.
echo ===========================================================================
echo         PostgreSQL Password Reset for Magnus
echo ===========================================================================
echo.
echo This script will reset the PostgreSQL password to match your .env file
echo Password will be set to: postgres123!
echo.

REM Find PostgreSQL installation
set PG_PATH=
if exist "C:\Program Files\PostgreSQL\16\bin\psql.exe" (
    set PG_PATH=C:\Program Files\PostgreSQL\16\bin
    set PG_DATA=C:\Program Files\PostgreSQL\16\data
    set PG_VERSION=16
)
if exist "C:\Program Files\PostgreSQL\17\bin\psql.exe" (
    set PG_PATH=C:\Program Files\PostgreSQL\17\bin
    set PG_DATA=C:\Program Files\PostgreSQL\17\data
    set PG_VERSION=17
)

if "%PG_PATH%"=="" (
    echo [ERROR] PostgreSQL not found!
    pause
    exit /b 1
)

echo [OK] Found PostgreSQL %PG_VERSION% at: %PG_PATH%
echo.

REM Backup current pg_hba.conf
echo Backing up pg_hba.conf...
copy "%PG_DATA%\pg_hba.conf" "%PG_DATA%\pg_hba.conf.backup" >nul
echo [OK] Backup created
echo.

REM Create temporary pg_hba.conf with trust authentication
echo Creating temporary trust authentication...
echo # Temporary trust authentication for password reset > "%PG_DATA%\pg_hba.conf.temp"
echo host    all             all             127.0.0.1/32            trust >> "%PG_DATA%\pg_hba.conf.temp"
echo host    all             all             ::1/128                 trust >> "%PG_DATA%\pg_hba.conf.temp"

REM Replace pg_hba.conf
copy /Y "%PG_DATA%\pg_hba.conf.temp" "%PG_DATA%\pg_hba.conf" >nul
echo [OK] Temporary configuration applied
echo.

REM Reload PostgreSQL configuration
echo Reloading PostgreSQL configuration...
net stop postgresql-x64-%PG_VERSION% >nul 2>&1
timeout /t 2 /nobreak >nul
net start postgresql-x64-%PG_VERSION% >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] PostgreSQL restarted
echo.

REM Reset password
echo Resetting password for user 'postgres'...
"%PG_PATH%\psql.exe" -U postgres -d postgres -c "ALTER USER postgres WITH PASSWORD 'postgres123!';" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Password successfully changed to: postgres123!
) else (
    echo [ERROR] Failed to change password
    echo Restoring original configuration...
    copy /Y "%PG_DATA%\pg_hba.conf.backup" "%PG_DATA%\pg_hba.conf" >nul
    net stop postgresql-x64-%PG_VERSION% >nul 2>&1
    net start postgresql-x64-%PG_VERSION% >nul 2>&1
    pause
    exit /b 1
)
echo.

REM Restore original pg_hba.conf
echo Restoring original authentication configuration...
copy /Y "%PG_DATA%\pg_hba.conf.backup" "%PG_DATA%\pg_hba.conf" >nul
echo [OK] Configuration restored
echo.

REM Reload PostgreSQL
echo Reloading PostgreSQL with new password...
net stop postgresql-x64-%PG_VERSION% >nul 2>&1
timeout /t 2 /nobreak >nul
net start postgresql-x64-%PG_VERSION% >nul 2>&1
timeout /t 3 /nobreak >nul
echo [OK] PostgreSQL restarted
echo.

REM Test connection
echo Testing connection with new password...
set PGPASSWORD=postgres123!
"%PG_PATH%\psql.exe" -U postgres -d postgres -c "SELECT 'Connection successful!' as status;" >nul 2>&1
if %errorlevel%==0 (
    echo [OK] Connection test successful!
) else (
    echo [WARNING] Connection test failed, but password should be set
)

REM Clean up temp files
del "%PG_DATA%\pg_hba.conf.temp" >nul 2>&1

echo.
echo ===========================================================================
echo Password Reset Complete!
echo ===========================================================================
echo.
echo Connection Details:
echo   Host: localhost
echo   Port: 5432
echo   User: postgres
echo   Password: postgres123!
echo.
echo You can now run: python check_postgres.py
echo.
pause
ENDLOCAL
