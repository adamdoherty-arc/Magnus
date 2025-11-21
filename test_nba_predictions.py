"""Test NBA AI predictions with fallback system"""
from src.espn_nba_live_data import ESPNNBALiveData
from datetime import datetime

nba = ESPNNBALiveData()
games = nba.get_scoreboard(date='20251119')

if games:
    game = games[0]
    print(f"Sample NBA Game: {game['away_team']} @ {game['home_team']}")
    print(f"Away Record: {game.get('away_record', 'N/A')}")
    print(f"Home Record: {game.get('home_record', 'N/A')}")

    # Test record parsing
    def parse_record(record_str):
        try:
            if '-' in record_str:
                wins, losses = record_str.split('-')
                total = int(wins) + int(losses)
                if total > 0:
                    return int(wins) / total
        except:
            pass
        return 0.5

    away_record = game.get('away_record', '')
    home_record = game.get('home_record', '')

    away_win_pct = parse_record(away_record)
    home_win_pct = parse_record(home_record)

    # Adjust for home court
    home_win_pct_adj = home_win_pct * 1.08

    # Normalize
    total_pct = away_win_pct + home_win_pct_adj
    away_odds = (away_win_pct / total_pct) * 100 if total_pct > 0 else 50
    home_odds = (home_win_pct_adj / total_pct) * 100 if total_pct > 0 else 50

    print(f"\nCalculated AI Prediction:")
    print(f"  Away ({game['away_team']}): {away_odds:.1f}% win probability")
    print(f"  Home ({game['home_team']}): {home_odds:.1f}% win probability")

    if home_odds > away_odds:
        print(f"\n✅ Predicted Winner: {game['home_team']} ({home_odds:.1f}%)")
    else:
        print(f"\n✅ Predicted Winner: {game['away_team']} ({away_odds:.1f}%)")
else:
    print("No NBA games found for 2025-11-19")
