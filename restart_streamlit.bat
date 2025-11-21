@echo off
echo ========================================
echo RESTARTING STREAMLIT DASHBOARD
echo ========================================
echo.
echo This will:
echo 1. Kill any existing Streamlit processes
echo 2. Start fresh Streamlit server
echo.
echo Press Ctrl+C to stop the dashboard
echo.
pause

REM Kill existing Streamlit processes
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /FI "WINDOWTITLE eq streamlit*" 2>nul
timeout /t 2 /nobreak >nul

REM Start Streamlit
cd /d "%~dp0"
streamlit run dashboard.py

pause

