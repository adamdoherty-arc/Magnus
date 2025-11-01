@echo off
REM Daily Trade Sync Batch File
REM This file runs the Python sync script
REM Can be scheduled with Windows Task Scheduler

echo.
echo ============================================================
echo Magnus Daily Trade Sync
echo ============================================================
echo.

cd /d "C:\Code\WheelStrategy"

python daily_trade_sync.py >> logs\trade_sync.log 2>&1

echo.
echo Sync completed! Check logs\trade_sync.log for details
echo.

REM Keep window open for 5 seconds to see results
timeout /t 5 /nobreak
