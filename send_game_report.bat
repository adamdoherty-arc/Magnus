@echo off
echo ================================================================================
echo EMAIL GAME REPORT SENDER
echo ================================================================================
echo.
echo Sending daily game report via email...
echo.

cd /d %~dp0
call venv\Scripts\activate

python -c "from src.email_game_reports import send_daily_report; success = send_daily_report(); print('Report sent!' if success else 'Failed to send report')"

echo.
pause
