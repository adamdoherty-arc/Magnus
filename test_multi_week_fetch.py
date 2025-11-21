"""
Test multi-week NFL game fetching
"""
from src.espn_live_data import ESPNLiveData
import logging

logging.basicConfig(level=logging.INFO)

espn = ESPNLiveData()
all_games = []

print("Fetching NFL games from multiple weeks...")
print("=" * 60)

for week in range(11, 19):
    games = espn.get_scoreboard(week=week)
    if games:
        all_games.extend(games)
        print(f"Week {week}: {len(games)} games")

print("=" * 60)
print(f"\nTotal games across all weeks: {len(all_games)}")

# Count by status
scheduled = [g for g in all_games if g.get('status') == 'STATUS_SCHEDULED']
live = [g for g in all_games if g.get('is_live')]
final = [g for g in all_games if g.get('is_completed')]

print(f"  • Upcoming scheduled games: {len(scheduled)}")
print(f"  • Live games: {len(live)}")
print(f"  • Final games: {len(final)}")

print("\nSample upcoming games:")
for i, game in enumerate(scheduled[:5], 1):
    print(f"  {i}. {game['away_team']} @ {game['home_team']}")
    print(f"     Time: {game['game_time']}")
