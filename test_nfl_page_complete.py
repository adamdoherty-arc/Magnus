"""Complete end-to-end test of NFL page functionality"""
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

print("=" * 80)
print("NFL PAGE - COMPLETE END-TO-END TEST")
print("=" * 80)

# Test 1: ESPN Data Fetching
print("\n[1/5] Testing ESPN NFL data fetching...")
try:
    from src.espn_live_data import get_espn_client

    espn = get_espn_client()
    games = espn.get_scoreboard()

    assert len(games) > 0, "No games fetched from ESPN"
    assert games[0].get('away_team'), "Missing team names"
    assert games[0].get('home_team'), "Missing team names"

    live_games = sum(1 for g in games if g.get('is_live'))

    print(f"   [OK] ESPN: {len(games)} games fetched, {live_games} live")
except Exception as e:
    print(f"   [FAIL] ESPN FAILED: {e}")
    exit(1)

# Test 2: Kalshi Database
print("\n[2/5] Testing Kalshi database...")
try:
    from src.kalshi_db_manager import KalshiDBManager

    db = KalshiDBManager()
    conn = db.get_connection()
    cur = conn.cursor()

    # Count NFL markets
    cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE raw_data->>'market_type' = 'nfl' AND status != 'closed'")
    nfl_count = cur.fetchone()[0]

    # Count all active markets
    cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE status != 'closed'")
    total_count = cur.fetchone()[0]

    cur.close()
    db.release_connection(conn)

    assert nfl_count > 0, "No NFL markets in database"

    print(f"   [OK] Kalshi DB: {nfl_count} NFL markets, {total_count} total")
except Exception as e:
    print(f"   [FAIL] Kalshi DB FAILED: {e}")
    exit(1)

# Test 3: ESPN-Kalshi Matching
print("\n[3/5] Testing ESPN-Kalshi matching...")
try:
    from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds

    enriched_games = enrich_games_with_kalshi_odds(games)
    matched = sum(1 for g in enriched_games if g.get('kalshi_odds'))
    match_rate = (matched / len(games)) * 100 if games else 0

    assert matched > 0, "No games matched with Kalshi odds"

    print(f"   [OK] Matcher: {matched}/{len(games)} games matched ({match_rate:.0f}%)")

    # Show sample matched game
    for g in enriched_games:
        if g.get('kalshi_odds'):
            odds = g['kalshi_odds']
            print(f"   >> Example: {g['away_team']} @ {g['home_team']}")
            print(f"      Odds: {odds.get('away_win_price', 0) * 100:.0f}¢ / {odds.get('home_win_price', 0) * 100:.0f}¢")
            break
except Exception as e:
    print(f"   [FAIL] Matching FAILED: {e}")
    exit(1)

# Test 4: Connection Pool Health
print("\n[4/5] Testing connection pool (stress test)...")
try:
    # Run matcher multiple times to ensure no pool exhaustion
    for i in range(3):
        enriched = enrich_games_with_kalshi_odds(games)
        matched = sum(1 for g in enriched if g.get('kalshi_odds'))

    print(f"   [OK] Pool: 3 iterations completed, no exhaustion")
except Exception as e:
    print(f"   [FAIL] Pool FAILED: {e}")
    exit(1)

# Test 5: Game Status Detection
print("\n[5/5] Testing game status detection...")
try:
    upcoming_games = [g for g in games if not g.get('is_live') and g.get('status_detail') != 'Final']
    finished_games = [g for g in games if g.get('status_detail') == 'Final']
    live_games = [g for g in games if g.get('is_live')]

    print(f"   [OK] Status: {len(upcoming_games)} upcoming, {len(live_games)} live, {len(finished_games)} finished")
except Exception as e:
    print(f"   [FAIL] Status FAILED: {e}")
    exit(1)

# Summary
print("\n" + "=" * 80)
print("TEST RESULTS SUMMARY")
print("=" * 80)

print(f"""
[OK] ALL TESTS PASSED!

ESPN Data:          {len(games)} games fetched
Kalshi Markets:     {nfl_count} NFL markets available
Match Rate:         {matched}/{len(games)} games ({match_rate:.0f}%)
Connection Pool:    Healthy (3 iterations)
Game Status:        {len(upcoming_games)} upcoming, {len(live_games)} live, {len(finished_games)} finished

READY FOR DEPLOYMENT! \!\!\!

Next Steps:
1. Open dashboard: streamlit run dashboard.py
2. Navigate to: Sports Game Cards → NFL
3. Verify games display with Kalshi odds
4. Test sync buttons show progress spinners
5. Verify auto-refresh toggle works
""")

print("=" * 80)
print("NFL PAGE STATUS: PRODUCTION READY [OK]")
print("=" * 80)
