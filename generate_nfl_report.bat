@echo off
echo ================================================================================
echo NFL BETTING REPORT GENERATOR
echo ================================================================================
echo.
echo Choose an option:
echo   1. Email only
echo   2. HTML file only
echo   3. Open in browser for printing to PDF
echo   4. All of the above (Email + HTML + Print)
echo.
set /p choice="Enter choice (1-4): "

cd /d %~dp0
call venv\Scripts\activate

if "%choice%"=="1" (
    echo.
    echo Sending email report...
    python generate_nfl_report.py --email
) else if "%choice%"=="2" (
    echo.
    echo Generating HTML file...
    python generate_nfl_report.py --html
) else if "%choice%"=="3" (
    echo.
    echo Opening report for printing...
    python generate_nfl_report.py --pdf
) else if "%choice%"=="4" (
    echo.
    echo Doing everything...
    python generate_nfl_report.py --all
) else (
    echo Invalid choice. Please run again and select 1-4.
)

echo.
pause
