@echo off
echo ================================================================================
echo CLEARING STREAMLIT CACHE AND STARTING DASHBOARD
echo ================================================================================
echo.
echo Step 1: Killing any running Streamlit processes...
taskkill /F /IM streamlit.exe 2>nul
timeout /t 2 >nul

echo.
echo Step 2: Clearing Python cache files...
del /s /q __pycache__ 2>nul
del /s /q *.pyc 2>nul

echo.
echo Step 3: Starting fresh Streamlit dashboard...
echo.
echo ================================================================================
echo IMPORTANT: Once dashboard opens, do this:
echo 1. Press 'C' key in browser
echo 2. Click 'Clear cache'
echo 3. Navigate to: Sports Game Cards - NFL tab
echo 4. You should now see Kalshi odds displayed!
echo ================================================================================
echo.
streamlit run dashboard.py --server.headless false
