@echo off
echo ================================================================================
echo GAME WATCHLIST MONITOR
echo ================================================================================
echo.
echo Starting background monitoring service...
echo Updates will be sent to Telegram every 5 minutes
echo.
echo Press Ctrl+C to stop
echo.
echo ================================================================================
echo.

python game_watchlist_monitor.py --interval 5

pause
