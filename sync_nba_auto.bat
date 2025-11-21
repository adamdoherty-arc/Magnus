@echo off
REM Auto-sync NBA Kalshi odds every 15 minutes
REM Run this as a Windows scheduled task

cd C:\Code\Legion\repos\ava
python sync_nba_prices.py

REM Log the sync
echo [%date% %time%] NBA odds synced >> nba_sync.log
