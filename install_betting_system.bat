@echo off
echo ================================================================================
echo BETTING SYSTEM DEPENDENCIES INSTALLER
echo ================================================================================
echo.
echo Installing required packages for real-time betting analysis...
echo.

cd /d %~dp0
call venv\Scripts\activate

echo Installing streamlit-autorefresh (for auto-refresh)...
pip install streamlit-autorefresh

echo.
echo Installing python-telegram-bot (for alerts)...
pip install python-telegram-bot

echo.
echo ================================================================================
echo INSTALLATION COMPLETE!
echo ================================================================================
echo.
echo Next steps:
echo 1. Add your TELEGRAM_CHAT_ID to .env file
echo 2. Run: start_betting_sync.bat
echo 3. Open dashboard: http://localhost:8501
echo.
echo See REALTIME_BETTING_SYSTEM_GUIDE.md for full instructions
echo.
pause
