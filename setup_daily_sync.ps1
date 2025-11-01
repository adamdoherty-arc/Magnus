# PowerShell Script to Setup Daily Trade Sync Task
# Run this script as Administrator to create the scheduled task
# The task will run daily at 4:30 PM ET (after market close)

$ErrorActionPreference = "Stop"

# Configuration
$TaskName = "Magnus_Daily_Trade_Sync"
$ScriptPath = $PSScriptRoot
$PythonScript = Join-Path $ScriptPath "daily_trade_sync.py"
$LogPath = Join-Path $ScriptPath "logs"

# Get Python executable path
$PythonExe = (Get-Command python).Source

if (-not $PythonExe) {
    Write-Host "ERROR: Python not found in PATH" -ForegroundColor Red
    Write-Host "Please ensure Python is installed and added to PATH" -ForegroundColor Red
    exit 1
}

Write-Host "=" -repeat 60 -ForegroundColor Cyan
Write-Host "Magnus Trading Platform - Daily Trade Sync Setup" -ForegroundColor Cyan
Write-Host "=" -repeat 60 -ForegroundColor Cyan
Write-Host ""
Write-Host "Configuration:" -ForegroundColor Yellow
Write-Host "  Task Name:    $TaskName"
Write-Host "  Python:       $PythonExe"
Write-Host "  Script:       $PythonScript"
Write-Host "  Schedule:     Daily at 4:30 PM ET"
Write-Host "  Log Location: $LogPath"
Write-Host ""

# Check if task already exists
$ExistingTask = Get-ScheduledTask -TaskName $TaskName -ErrorAction SilentlyContinue

if ($ExistingTask) {
    Write-Host "Existing task found. Removing..." -ForegroundColor Yellow
    Unregister-ScheduledTask -TaskName $TaskName -Confirm:$false
    Write-Host "Old task removed." -ForegroundColor Green
}

# Create logs directory
if (-not (Test-Path $LogPath)) {
    New-Item -ItemType Directory -Path $LogPath | Out-Null
    Write-Host "Created logs directory: $LogPath" -ForegroundColor Green
}

# Create the scheduled task action
$Action = New-ScheduledTaskAction `
    -Execute $PythonExe `
    -Argument "`"$PythonScript`"" `
    -WorkingDirectory $ScriptPath

# Create the trigger (Daily at 4:30 PM ET)
# Note: Adjust timezone if needed
$Trigger = New-ScheduledTaskTrigger -Daily -At "4:30 PM"

# Create task settings
$Settings = New-ScheduledTaskSettingsSet `
    -AllowStartIfOnBatteries `
    -DontStopIfGoingOnBatteries `
    -StartWhenAvailable `
    -RunOnlyIfNetworkAvailable `
    -ExecutionTimeLimit (New-TimeSpan -Minutes 15)

# Task principal (run as current user)
$Principal = New-ScheduledTaskPrincipal `
    -UserId $env:USERNAME `
    -LogonType S4U `
    -RunLevel Limited

# Register the task
try {
    Register-ScheduledTask `
        -TaskName $TaskName `
        -Action $Action `
        -Trigger $Trigger `
        -Settings $Settings `
        -Principal $Principal `
        -Description "Automatically syncs closed trades from Robinhood to Magnus database daily at 4:30 PM ET" `
        | Out-Null

    Write-Host ""
    Write-Host "=" -repeat 60 -ForegroundColor Green
    Write-Host "SUCCESS! Daily sync task created" -ForegroundColor Green
    Write-Host "=" -repeat 60 -ForegroundColor Green
    Write-Host ""
    Write-Host "The task will run automatically every day at 4:30 PM ET" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "To manage the task:" -ForegroundColor Yellow
    Write-Host "  - Open Task Scheduler (taskschd.msc)"
    Write-Host "  - Look for: $TaskName"
    Write-Host "  - Right-click to run manually, disable, or modify"
    Write-Host ""
    Write-Host "To test the sync now, run:" -ForegroundColor Yellow
    Write-Host "  python daily_trade_sync.py" -ForegroundColor White
    Write-Host ""
    Write-Host "Logs will be saved to:" -ForegroundColor Yellow
    Write-Host "  $LogPath" -ForegroundColor White
    Write-Host ""

} catch {
    Write-Host ""
    Write-Host "=" -repeat 60 -ForegroundColor Red
    Write-Host "ERROR: Failed to create scheduled task" -ForegroundColor Red
    Write-Host "=" -repeat 60 -ForegroundColor Red
    Write-Host ""
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Try running this script as Administrator" -ForegroundColor Yellow
    exit 1
}
