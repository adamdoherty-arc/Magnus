"""
Update NFL Elo Ratings Based on Current 2024-2025 Season Records
================================================================

This script updates Elo ratings to match current team performance.
Prevents AI from making backwards predictions.
"""

import json
import os
from datetime import datetime

# Current NFL records (as of Nov 19, 2024 - Week 12)
NFL_RECORDS_2024 = {
    'Kansas City Chiefs': (10, 1),
    'Detroit Lions': (9, 2),
    'Buffalo Bills': (9, 2),
    'New England Patriots': (3, 9),
    'Cincinnati Bengals': (4, 7),
    'Philadelphia Eagles': (8, 3),
    'Minnesota Vikings': (8, 3),
    'Green Bay Packers': (8, 3),
    'Baltimore Ravens': (7, 4),
    'Pittsburgh Steelers': (7, 4),
    'Los Angeles Chargers': (7, 4),
    'Washington Commanders': (7, 5),
    'Arizona Cardinals': (6, 5),
    'Denver Broncos': (6, 5),
    'Seattle Seahawks': (5, 5),
    'Tampa Bay Buccaneers': (5, 6),
    'Los Angeles Rams': (5, 6),
    'San Francisco 49ers': (5, 6),
    'Indianapolis Colts': (5, 6),
    'Houston Texans': (7, 5),
    'Miami Dolphins': (4, 6),
    'Atlanta Falcons': (6, 5),
    'Chicago Bears': (4, 7),
    'Dallas Cowboys': (3, 7),
    'New Orleans Saints': (4, 7),
    'Cleveland Browns': (2, 8),
    'Carolina Panthers': (3, 8),
    'New York Jets': (3, 8),
    'Tennessee Titans': (2, 8),
    'Las Vegas Raiders': (2, 9),
    'Jacksonville Jaguars': (2, 9),
    'New York Giants': (2, 9),
}

def calculate_elo_from_record(wins, losses, base_elo=1500):
    """Calculate Elo rating based on win-loss record."""
    total_games = wins + losses
    if total_games == 0:
        return base_elo
    
    win_rate = wins / total_games
    elo = base_elo + (win_rate - 0.5) * 400
    
    if wins >= 8:
        elo += 20
    elif wins <= 3:
        elo -= 20
    
    return round(elo)

new_ratings = {}
for team, (wins, losses) in NFL_RECORDS_2024.items():
    new_ratings[team] = calculate_elo_from_record(wins, losses)

sorted_teams = sorted(new_ratings.items(), key=lambda x: x[1], reverse=True)

print("="*80)
print("NFL ELO RATINGS UPDATE - 2024 Week 12")
print("="*80)
print(f"\n{'Rank':<6}{'Team':<35}{'Record':<12}{'Elo':<8}")
print("-"*80)

for rank, (team, elo) in enumerate(sorted_teams, 1):
    wins, losses = NFL_RECORDS_2024[team]
    record = f"{wins}-{losses}"
    print(f"{rank:<6}{team:<35}{record:<12}{elo:<8}")

print("\n" + "="*80)
print("KEY FIX: Patriots vs Bengals")
print("="*80)
print(f"Patriots: {NFL_RECORDS_2024['New England Patriots'][0]}-{NFL_RECORDS_2024['New England Patriots'][1]} -> {new_ratings['New England Patriots']} Elo")
print(f"Bengals:  {NFL_RECORDS_2024['Cincinnati Bengals'][0]}-{NFL_RECORDS_2024['Cincinnati Bengals'][1]} -> {new_ratings['Cincinnati Bengals']} Elo")

# Save
ratings_file = 'src/data/nfl_elo_ratings.json'
os.makedirs('src/data', exist_ok=True)

with open(ratings_file, 'w') as f:
    json.dump(new_ratings, f, indent=2)

print(f"\nSUCCESS: Saved to {ratings_file}")
