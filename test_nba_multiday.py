"""Test NBA multi-day game fetching"""
from src.espn_nba_live_data import ESPNNBALiveData
from datetime import datetime, timedelta

nba = ESPNNBALiveData()
today = datetime.now()
total = 0

print("Fetching NBA games for next 7 days...")
for i in range(7):
    date = today + timedelta(days=i)
    date_str = date.strftime('%Y%m%d')
    games = nba.get_scoreboard(date=date_str)
    total += len(games)
    print(f'{date_str}: {len(games)} games')

print(f'\nTotal over 7 days: {total} games')
