@echo off
echo ================================================================================
echo   FORCE REFRESH STREAMLIT - CLEARS ALL CACHES
echo ================================================================================
echo.
echo This script will:
echo   1. Kill all running Streamlit processes
echo   2. Clear Python __pycache__ files
echo   3. Clear Streamlit cache directory
echo   4. Restart Streamlit with a fresh start
echo.
pause

echo.
echo [1/4] Killing Streamlit processes...
taskkill /F /IM streamlit.exe 2>nul
taskkill /F /IM python.exe /FI "WINDOWTITLE eq streamlit*" 2>nul
timeout /t 2 >nul

echo.
echo [2/4] Clearing Python cache files...
for /d /r . %%d in (__pycache__) do @if exist "%%d" rd /s /q "%%d"
del /s /q *.pyc 2>nul
echo Python cache cleared!

echo.
echo [3/4] Clearing Streamlit cache directory...
if exist "%USERPROFILE%\.streamlit\cache" (
    rmdir /s /q "%USERPROFILE%\.streamlit\cache"
    echo Streamlit cache cleared!
) else (
    echo Streamlit cache directory not found (OK)
)

echo.
echo [4/4] Starting Streamlit...
echo.
echo ================================================================================
echo   IMPORTANT NEXT STEPS IN YOUR BROWSER:
echo ================================================================================
echo   1. Wait for browser to open
echo   2. Press Ctrl+Shift+R (Windows) or Cmd+Shift+R (Mac) for hard refresh
echo   3. Or press F12 -^> Right-click refresh -^> "Empty Cache and Hard Reload"
echo   4. Click "🔄 Force Refresh" button at top-left of the page
echo   5. Navigate to Sports Game Cards tab
echo.
echo   Your CSS changes should now be visible!
echo ================================================================================
echo.
pause

streamlit run dashboard.py --server.headless false

echo.
echo Streamlit has stopped. Press any key to exit.
pause >nul

