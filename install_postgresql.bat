@echo off
SETLOCAL EnableDelayedExpansion

echo.
echo ===========================================================================
echo                   POSTGRESQL INSTALLATION FOR MAGNUS
echo ===========================================================================
echo.

REM Check if PostgreSQL is already installed
where psql >nul 2>&1
if %errorlevel%==0 (
    echo [OK] PostgreSQL is already installed!
    psql --version
    echo.
    goto SETUP_DB
)

REM Check if installer exists
if not exist "C:\Users\New User\Downloads\postgresql-17-windows-x64.exe" (
    echo [ERROR] PostgreSQL installer not found!
    echo Please wait for download to complete or download from:
    echo https://www.enterprisedb.com/downloads/postgres-postgresql-downloads
    echo.
    pause
    exit /b 1
)

echo PostgreSQL installer found.
echo.
echo ===========================================================================
echo Installing PostgreSQL 17...
echo ===========================================================================
echo.
echo This will install PostgreSQL with the following settings:
echo   - Installation Directory: C:\Program Files\PostgreSQL\17
echo   - Data Directory: C:\Program Files\PostgreSQL\17\data
echo   - Port: 5432
echo   - Superuser: postgres
echo   - Password: postgres123!
echo   - Database: magnus
echo.
echo The installation will take 2-5 minutes...
echo.

REM Run PostgreSQL installer in unattended mode
"C:\Users\New User\Downloads\postgresql-17-windows-x64.exe" ^
    --mode unattended ^
    --unattendedmodeui minimal ^
    --superpassword "postgres123!" ^
    --servicename "postgresql-x64-17" ^
    --serviceaccount "NT AUTHORITY\NETWORK SERVICE" ^
    --serverport 5432 ^
    --enable-components server,pgAdmin,commandlinetools ^
    --disable-components stackbuilder ^
    --datadir "C:\Program Files\PostgreSQL\17\data" ^
    --extract-only 0

if %errorlevel% neq 0 (
    echo [ERROR] Installation failed!
    echo Please run the installer manually: C:\Users\New User\Downloads\postgresql-17-windows-x64.exe
    pause
    exit /b 1
)

echo.
echo [OK] PostgreSQL installed successfully!
echo.

REM Add PostgreSQL to PATH
setx PATH "%PATH%;C:\Program Files\PostgreSQL\17\bin" /M >nul 2>&1
set PATH=%PATH%;C:\Program Files\PostgreSQL\17\bin

REM Wait for service to start
echo Waiting for PostgreSQL service to start...
timeout /t 10 /nobreak >nul

:SETUP_DB
echo.
echo ===========================================================================
echo Setting up Magnus database...
echo ===========================================================================
echo.

REM Set password for psql (from .env file)
set PGPASSWORD=postgres123!

REM Create magnus database (primary database from .env)
echo Creating 'magnus' database...
psql -U postgres -c "CREATE DATABASE magnus;" 2>nul
if %errorlevel%==0 (
    echo [OK] Database 'magnus' created
) else (
    echo [INFO] Database 'magnus' may already exist
)

REM Create wheel_strategy database (legacy compatibility)
echo Creating 'wheel_strategy' database...
psql -U postgres -c "CREATE DATABASE wheel_strategy;" 2>nul
if %errorlevel%==0 (
    echo [OK] Database 'wheel_strategy' created
) else (
    echo [INFO] Database 'wheel_strategy' may already exist
)

REM Create magnus_trading database (if used by other features)
echo Creating 'magnus_trading' database...
psql -U postgres -c "CREATE DATABASE magnus_trading;" 2>nul
if %errorlevel%==0 (
    echo [OK] Database 'magnus_trading' created
) else (
    echo [INFO] Database 'magnus_trading' may already exist
)

REM Check if schema file exists and apply to magnus database
if exist "database_schema.sql" (
    echo.
    echo Applying database schema to 'magnus' database...
    psql -U postgres -d magnus -f database_schema.sql
    if %errorlevel%==0 (
        echo [OK] Schema applied to 'magnus' database
    ) else (
        echo [WARNING] Schema application had errors
    )

    echo Applying database schema to 'wheel_strategy' database...
    psql -U postgres -d wheel_strategy -f database_schema.sql
    if %errorlevel%==0 (
        echo [OK] Schema applied to 'wheel_strategy' database
    ) else (
        echo [WARNING] Schema application had errors
    )
)

echo.
echo ===========================================================================
echo PostgreSQL Setup Complete!
echo ===========================================================================
echo.
echo Connection Details (matching .env file):
echo   Host: localhost
echo   Port: 5432
echo   Databases: magnus (primary), wheel_strategy, magnus_trading
echo   Username: postgres
echo   Password: postgres123!
echo.
echo Your .env file is already configured with:
echo   DATABASE_URL=postgresql://postgres:postgres123!@localhost:5432/magnus
echo.
echo You can now run the Magnus dashboard:
echo   streamlit run dashboard.py
echo.
pause
ENDLOCAL
