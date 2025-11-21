@echo off
REM Quick launcher for Xtrades scraper (recommended version)
echo ====================================
echo Xtrades Scraper - Quick Launch
echo ====================================
echo.
echo This will open Chrome for you to:
echo 1. Log in with Discord
echo 2. Click "Following" tab
echo 3. Turn OFF the toggle
echo.
echo The script will auto-continue after 3 minutes.
echo.
pause

cd /d "%~dp0"
python scrape_following_final.py

pause
