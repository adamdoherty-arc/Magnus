@echo off
echo ================================================================================
echo REAL-TIME BETTING SYNC SERVICE
echo ================================================================================
echo.
echo Starting betting opportunities sync (runs every 5 minutes)...
echo Press Ctrl+C to stop
echo.

cd /d %~dp0
call venv\Scripts\activate

python src/realtime_betting_sync.py

pause
