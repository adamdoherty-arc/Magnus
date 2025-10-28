# PowerShell Setup Script for Wheel Strategy Trading System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "WHEEL STRATEGY TRADING SYSTEM SETUP" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if Python is installed
try {
    $pythonVersion = python --version 2>&1
    Write-Host "✓ Python found: $pythonVersion" -ForegroundColor Green
} catch {
    Write-Host "ERROR: Python is not installed or not in PATH" -ForegroundColor Red
    Write-Host "Please install Python 3.9+ from https://www.python.org/"
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host ""
Write-Host "[1/4] Creating virtual environment..." -ForegroundColor Yellow
if (!(Test-Path "venv")) {
    python -m venv venv
    Write-Host "✓ Virtual environment created." -ForegroundColor Green
} else {
    Write-Host "✓ Virtual environment already exists." -ForegroundColor Green
}

Write-Host ""
Write-Host "[2/4] Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

Write-Host ""
Write-Host "[3/4] Upgrading pip..." -ForegroundColor Yellow
python -m pip install --upgrade pip --quiet

Write-Host ""
Write-Host "[4/4] Installing requirements..." -ForegroundColor Yellow

# Install packages one by one to handle failures gracefully
$packages = @(
    "fastapi",
    "uvicorn[standard]",
    "pydantic",
    "python-dotenv",
    "pandas",
    "numpy",
    "yfinance",
    "requests",
    "redis",
    "psycopg2-binary",
    "streamlit",
    "plotly",
    "loguru",
    "aiohttp"
)

$failed = @()
foreach ($package in $packages) {
    Write-Host "  Installing $package..." -NoNewline
    $output = python -m pip install $package 2>&1
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✓" -ForegroundColor Green
    } else {
        Write-Host " ✗" -ForegroundColor Red
        $failed += $package
    }
}

if ($failed.Count -gt 0) {
    Write-Host ""
    Write-Host "Warning: Some packages failed to install:" -ForegroundColor Yellow
    $failed | ForEach-Object { Write-Host "  - $_" -ForegroundColor Yellow }
    Write-Host "System may still work with reduced functionality." -ForegroundColor Yellow
}

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "SETUP COMPLETE!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "To start the system:" -ForegroundColor Yellow
Write-Host "  1. Run: .\venv\Scripts\Activate.ps1" -ForegroundColor White
Write-Host "  2. Run: python start.py" -ForegroundColor White
Write-Host ""
Write-Host "Or just run: .\run.ps1" -ForegroundColor Green
Write-Host ""
Read-Host "Press Enter to continue"