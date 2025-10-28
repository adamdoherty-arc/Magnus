# PowerShell Run Script for Wheel Strategy Trading System

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "STARTING WHEEL STRATEGY TRADING SYSTEM" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Check if venv exists
if (!(Test-Path "venv")) {
    Write-Host "Virtual environment not found. Running setup first..." -ForegroundColor Yellow
    & .\setup.ps1
}

# Activate virtual environment
Write-Host "Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Check if Redis is running
Write-Host "Checking Redis..." -ForegroundColor Yellow
try {
    $redisTest = redis-cli ping 2>&1
    if ($redisTest -eq "PONG") {
        Write-Host "✓ Redis is running" -ForegroundColor Green
    } else {
        throw "Redis not responding"
    }
} catch {
    Write-Host "Starting Redis in background..." -ForegroundColor Yellow
    Start-Process redis-server -WindowStyle Hidden
    Start-Sleep -Seconds 2
}

# Setup database if needed
Write-Host "Checking PostgreSQL database..." -ForegroundColor Yellow
$dbCheck = python -c "import psycopg2; conn = psycopg2.connect(host='localhost', database='wheel_strategy', user='postgres', password='postgres123!'); conn.close(); print('ok')" 2>&1

if ($dbCheck -ne "ok") {
    Write-Host "Setting up database..." -ForegroundColor Yellow
    python setup_database.py
    if ($LASTEXITCODE -ne 0) {
        Write-Host ""
        Write-Host "WARNING: Database setup failed. System will use Redis only." -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "✓ Database connected" -ForegroundColor Green
}

Write-Host ""
Write-Host "Starting Wheel Strategy System..." -ForegroundColor Green
Write-Host "========================================"
python start.py

Read-Host "Press Enter to exit"