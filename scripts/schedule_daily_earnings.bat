@echo off
cd /d "C:\code\Magnus"
call venv\Scripts\activate
python scripts\daily_earnings_automation.py >> logs\earnings_automation.log 2>&1
