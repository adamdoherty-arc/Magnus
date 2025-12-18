@echo off
echo ============================================
echo AVA - FRESH DEPLOY TO RENDER
echo ============================================
echo.
echo This script will:
echo 1. Deploy the master schema (70+ tables)
echo 2. Set up all views, functions, and indexes
echo 3. Initialize configuration data
echo.
echo ⚠️  Use this for FIRST-TIME setup on Render
echo    For updates, use restore_to_render.bat
echo.

pause

REM Set PostgreSQL bin path
set PG_BIN="C:\Program Files\PostgreSQL\16\bin"

echo.
echo ============================================
echo Render PostgreSQL Connection
echo ============================================
echo.
echo Go to your Render dashboard:
echo 1. Open https://dashboard.render.com
echo 2. Click your PostgreSQL database
echo 3. Copy "External Connection String"
echo.

set /p RENDER_URL="Paste your Render connection string: "

if "%RENDER_URL%"=="" (
    echo ❌ No connection string provided
    pause
    exit /b 1
)

echo.
echo 🚀 Deploying AVA master schema to Render...
echo.

REM Deploy schema
%PG_BIN%\psql "%RENDER_URL%" -f render_master_schema.sql

if %ERRORLEVEL% EQU 0 (
    echo.
    echo ============================================
    echo ✅ DEPLOYMENT SUCCESSFUL!
    echo ============================================
    echo.
    echo 🎉 AVA database schema deployed to Render!
    echo.
    echo 📊 Deployed:
    echo    - 70+ tables
    echo    - 10+ views
    echo    - 5+ functions/triggers
    echo    - 40+ indexes
    echo.
    echo 📝 Next steps:
    echo 1. Update .env: python scripts/update_env_for_render.py
    echo 2. Test connection: scripts\test_render_connection.bat
    echo 3. Migrate data: scripts\restore_to_render.bat
    echo.
) else (
    echo.
    echo ❌ Deployment failed!
    echo 💡 Check:
    echo    - Connection string is correct
    echo    - Database exists on Render
    echo    - Network connection is stable
    echo.
    echo ⚠️  If database already has tables, you may see errors
    echo    This is normal - the schema uses IF NOT EXISTS
)

pause
