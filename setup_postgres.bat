@echo off
echo Setting up PostgreSQL for Wheel Strategy System...
echo.

REM Check if PostgreSQL is installed
where psql >nul 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo PostgreSQL is not installed or not in PATH.
    echo Please install PostgreSQL from: https://www.postgresql.org/download/windows/
    echo After installation, add PostgreSQL bin folder to PATH
    echo Typically: C:\Program Files\PostgreSQL\15\bin
    pause
    exit /b 1
)

echo PostgreSQL found.
echo.

REM Set default password if not provided
if "%PGPASSWORD%"=="" (
    set PGPASSWORD=postgres
    echo Using default password: postgres
)

REM Create database
echo Creating database 'wheel_strategy'...
psql -U postgres -c "CREATE DATABASE wheel_strategy;" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo Database created successfully.
) else (
    echo Database might already exist or there was an error.
)
echo.

REM Install TimescaleDB extension
echo Installing TimescaleDB extension...
psql -U postgres -d wheel_strategy -c "CREATE EXTENSION IF NOT EXISTS timescaledb CASCADE;" 2>nul
if %ERRORLEVEL% EQU 0 (
    echo TimescaleDB extension installed.
) else (
    echo TimescaleDB might not be installed. Install from: https://www.timescale.com/
)
echo.

REM Run schema
echo Running database schema...
if exist database_schema.sql (
    psql -U postgres -d wheel_strategy -f database_schema.sql
    if %ERRORLEVEL% EQU 0 (
        echo Schema created successfully!
    ) else (
        echo Error creating schema. Check database_schema.sql for issues.
    )
) else (
    echo database_schema.sql not found!
)

echo.
echo Setup complete!
echo.
echo Connection details:
echo   Host: localhost
echo   Port: 5432
echo   Database: wheel_strategy
echo   User: postgres
echo   Password: %PGPASSWORD%
echo.
echo Update config.json with these details.
pause