@echo off
REM Quick launcher for Magnus Dashboard
echo ====================================
echo Magnus Trading Dashboard
echo ====================================
echo.
echo Starting Streamlit dashboard...
echo Dashboard will open at: http://localhost:8501
echo.
echo Press Ctrl+C to stop the dashboard
echo.

cd /d "%~dp0"
streamlit run dashboard.py

pause
