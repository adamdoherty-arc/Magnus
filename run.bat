@echo off
echo ========================================
echo STARTING WHEEL STRATEGY TRADING SYSTEM
echo ========================================
echo.

REM Check if venv exists
if not exist "venv" (
    echo Virtual environment not found. Running setup first...
    call setup.bat
)

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Check if Redis is running
echo Checking Redis...
redis-cli ping >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Starting Redis in background...
    start /B redis-server
    timeout /t 2 >nul
)

REM Setup database if needed
echo Checking PostgreSQL database...
python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='wheel_strategy', user='postgres', password='postgres123!'); conn.close()" 2>nul
if %ERRORLEVEL% NEQ 0 (
    echo Setting up database...
    python setup_database.py
    if %ERRORLEVEL% NEQ 0 (
        echo.
        echo WARNING: Database setup failed. System will use Redis only.
        echo.
    )
)

echo.
echo Starting Wheel Strategy System...
echo ========================================
python start.py

pause