"""Check game dates between ESPN and Kalshi"""
from datetime import datetime
import pytz

# ESPN game time for Jets @ Patriots (already happened)
espn_game_time = "2025-11-14 01:15:00+00:00"
espn_dt = datetime.fromisoformat(espn_game_time.replace('+00:00', '+00:00'))

# Kalshi close time (from database)
kalshi_close_time = "2025-11-30 09:30:00-05:00"
kalshi_dt = datetime.fromisoformat(kalshi_close_time)

print("=" * 80)
print("DATE COMPARISON")
print("=" * 80)

print(f"\nESPN Game Time (Jets @ Patriots):")
print(f"  {espn_dt}")
print(f"  Status: Game already finished (Final)")

print(f"\nKalshi Market Close Time:")
print(f"  {kalshi_dt}")

print(f"\nDifference: {(kalshi_dt - espn_dt.replace(tzinfo=pytz.timezone('US/Eastern'))).days} days")

print("\n" + "=" * 80)
print("MATCHER DATE RANGE (±3 days from game time)")
print("=" * 80)

from datetime import timedelta
game_date = espn_dt.date()
date_start = game_date - timedelta(days=3)
date_end = game_date + timedelta(days=3)

print(f"\nMatcher searches for markets between:")
print(f"  Start: {date_start}")
print(f"  End: {date_end}")

print(f"\nKalshi market closes on: {kalshi_dt.date()}")
print(f"  Is within range? {date_start <= kalshi_dt.date() <= date_end}")

print("\n" + "=" * 80)
print("WHY MARKETS DON'T MATCH")
print("=" * 80)

print("""
The Jets @ Patriots game was on November 14, 2025.
Kalshi markets for "Washington at Miami" close on November 30, 2025.

This is for WEEK 12 games (Nov 16-17), not the Jets game (Week 11, Nov 14).

The Jets @ Patriots game already finished - there might be NO Kalshi
markets for it because:
1. The game is over
2. Markets for finished games are marked 'closed'
3. Matcher filters out status='closed' markets

We need to search for upcoming games (Week 12) not finished games (Week 11).
""")
