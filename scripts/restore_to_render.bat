@echo off
echo ============================================
echo AVA - Restore Database to Render
echo ============================================
echo.

REM Set PostgreSQL bin path
set PG_BIN="C:\Program Files\PostgreSQL\16\bin"

echo 🔍 Looking for latest backup...
echo.

REM Find the latest backup file
for /f "delims=" %%i in ('dir /b /o-d backups\ava_backup_*.sql 2^>nul') do (
    set LATEST_BACKUP=backups\%%i
    goto :found
)

echo ❌ No backup files found in backups\ folder
echo 💡 Run backup_database.bat first to create a backup
pause
exit /b 1

:found
echo ✅ Found latest backup: %LATEST_BACKUP%
echo.

REM Get file size
for %%A in (%LATEST_BACKUP%) do set SIZE=%%~zA
set /a SIZE_MB=%SIZE% / 1024 / 1024
echo 📊 Backup size: %SIZE_MB% MB
echo.

echo ============================================
echo DEPLOYMENT OPTIONS
echo ============================================
echo.
echo 1. Fresh Deploy (Recommended) - Deploy clean schema + data
echo 2. Data Restore Only - Restore backup from local database
echo.

set /p DEPLOY_TYPE="Choose option (1 or 2): "

if "%DEPLOY_TYPE%"=="1" (
    set SCHEMA_FILE=render_master_schema.sql
    goto :deploy_fresh
)

if "%DEPLOY_TYPE%"=="2" (
    goto :restore_backup
)

echo ❌ Invalid option
pause
exit /b 1

:deploy_fresh
echo.
echo 🏗️  FRESH DEPLOY MODE
echo ============================================
echo This will:
echo 1. Deploy master schema (70+ tables, views, functions)
echo 2. Then restore your data from backup
echo.

echo ============================================
echo Render PostgreSQL Connection
echo ============================================
echo.
echo Go to your Render dashboard:
echo 1. Open https://dashboard.render.com
echo 2. Click on your PostgreSQL database
echo 3. Copy the "External Connection String"
echo.
echo It looks like:
echo postgresql://user:pass@dpg-xxx.oregon-postgres.render.com/dbname
echo.

set /p RENDER_URL="Paste your Render connection string: "

if "%RENDER_URL%"=="" (
    echo ❌ No connection string provided
    pause
    exit /b 1
)

echo.
:restore_backup
echo 🚀 Starting migration to Render...
echo ⏱️  This may take 30-60 seconds depending on data size...
echo.

REM If fresh deploy, deploy schema first
if "%DEPLOY_TYPE%"=="1" (
    echo 📋 Step 1/2: Deploying master schema...
    %PG_BIN%\psql "%RENDER_URL%" -f %SCHEMA_FILE%
    if %ERRORLEVEL% NEQ 0 (
        echo ❌ Schema deployment failed!
        pause
        exit /b 1
    )
    echo ✅ Schema deployed successfully
    echo.
)

REM Restore data
echo 📋 Step 2/2: Restoring data...
%PG_BIN%\psql "%RENDER_URL%" -f %LATEST_BACKUP%

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✅ MIGRATION COMPLETE!
    echo ============================================
    echo.
    echo 🎉 Your database is now on Render!
    echo.
    echo 📝 Next steps:
    echo 1. Update your .env file with Render credentials
    echo 2. Run: update_env_for_render.bat
    echo.
    echo Your Render connection string:
    echo %RENDER_URL%
    echo.
) else (
    echo.
    echo ❌ Migration failed!
    echo 💡 Check:
    echo    - Connection string is correct
    echo    - Database exists on Render
    echo    - Network connection is stable
)

pause
