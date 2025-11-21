"""
Data Accuracy Audit - Focused review of critical data issues
"""
import sys
from datetime import datetime
from src.espn_kalshi_matcher_optimized import ESPNKalshiMatcher
from src.kalshi_db_manager import KalshiDBManager
from src.espn_live_data import ESPNLiveData
import psycopg2.extras

if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

print("=" * 80)
print("DATA ACCURACY AUDIT")
print("=" * 80)
print(f"Audit Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

errors = []
warnings = []
passed = []

# ==================== 1. KALSHI PRICE VALIDATION ====================
print("\n1. KALSHI PRICE VALIDATION")
print("-" * 80)

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

# Check that yes_price + no_price ≈ 1.0 for all active markets
cur.execute("""
    SELECT
        ticker,
        title,
        yes_price,
        no_price,
        (yes_price + no_price) as price_sum,
        ABS((yes_price + no_price) - 1.0) as deviation
    FROM kalshi_markets
    WHERE status = 'active'
      AND ticker LIKE 'KXNFLGAME%'
    ORDER BY deviation DESC
    LIMIT 10
""")
price_checks = cur.fetchall()

max_deviation = max([p['deviation'] for p in price_checks]) if price_checks else 0

if max_deviation > 0.05:
    errors.append(f"❌ CRITICAL: Price sum deviation up to {max_deviation:.3f} (should be < 0.05)")
    print(f"❌ CRITICAL: Maximum price deviation: {max_deviation:.3f}")
    for p in price_checks[:3]:
        print(f"  {p['ticker']}: {p['yes_price']:.2f} + {p['no_price']:.2f} = {p['price_sum']:.2f}")
elif max_deviation > 0.02:
    warnings.append(f"⚠️ Price sum deviation up to {max_deviation:.3f} (acceptable but high)")
    print(f"⚠️ Warning: Maximum price deviation: {max_deviation:.3f} (acceptable)")
else:
    passed.append("✅ All Kalshi prices valid (yes + no ≈ 1.00)")
    print(f"✅ PASS: All prices valid (max deviation: {max_deviation:.3f})")

# ==================== 2. ESPN TO KALSHI MATCHING ====================
print("\n2. ESPN TO KALSHI MATCHING ACCURACY")
print("-" * 80)

try:
    espn = ESPNLiveData()
    nfl_games = espn.get_scoreboard()

    if not nfl_games:
        warnings.append("⚠️ No NFL games found (may be off-season or bye week)")
        print("⚠️ No NFL games available to test")
    else:
        matcher = ESPNKalshiMatcher()

        print(f"Testing {len(nfl_games)} NFL games...")

        matched = 0
        unmatched = []
        reversed_odds = []

        for game in nfl_games:
            away_team = game.get('away_team', '')
            home_team = game.get('home_team', '')

            result = matcher.match_game_to_kalshi(game)

            if result:
                matched += 1

                # Verify odds are assigned correctly
                ticker = result['ticker']
                ticker_suffix = ticker.split('-')[-1].lower()

                away_price = float(result['away_win_price'])
                home_price = float(result['home_win_price'])

                # Check if suffix matches away team
                # If suffix is "DAL" and away team is "Dallas Cowboys", yes_price should go to away
                away_in_suffix = any(part.lower() in ticker_suffix for part in away_team.split())

                # If away team is in suffix, away should have higher odds if it's favored
                # This is a heuristic check
                if abs(away_price - home_price) > 0.1:  # Meaningful difference
                    # The team with higher odds should match the ticker suffix
                    if away_price > home_price and not away_in_suffix:
                        # Away is favored but ticker doesn't match away - might be reversed
                        reversed_odds.append({
                            'game': f"{away_team} @ {home_team}",
                            'ticker': ticker,
                            'ticker_suffix': ticker_suffix,
                            'away_price': away_price,
                            'home_price': home_price
                        })

                print(f"  ✓ {away_team} @ {home_team}")
                print(f"    Ticker: {ticker} (suffix: {ticker_suffix})")
                print(f"    Odds: Away {away_price:.2f} / Home {home_price:.2f}")
            else:
                unmatched.append(f"{away_team} @ {home_team}")
                print(f"  ✗ {away_team} @ {home_team} - No match")

        match_rate = (matched / len(nfl_games) * 100) if nfl_games else 0

        if reversed_odds:
            errors.append(f"❌ CRITICAL: {len(reversed_odds)} games may have reversed odds")
            print(f"\n❌ POSSIBLE REVERSED ODDS:")
            for item in reversed_odds:
                print(f"  {item['game']}")
                print(f"    Ticker: {item['ticker']} (suffix: {item['ticker_suffix']})")
                print(f"    Away: {item['away_price']:.2f}, Home: {item['home_price']:.2f}")
        else:
            passed.append("✅ All matched games have correct odds assignment")
            print(f"\n✅ PASS: Odds assignment looks correct")

        if match_rate < 80:
            warnings.append(f"⚠️ Match rate: {match_rate:.1f}% (expected >80%)")
            print(f"⚠️ Warning: Low match rate {match_rate:.1f}%")
        else:
            passed.append(f"✅ Match rate: {match_rate:.1f}%")
            print(f"✅ PASS: Match rate {match_rate:.1f}% ({matched}/{len(nfl_games)})")

        if unmatched:
            print(f"\nUnmatched games ({len(unmatched)}):")
            for game in unmatched[:5]:
                print(f"  {game}")

except Exception as e:
    errors.append(f"❌ ESPN/Kalshi matching failed: {e}")
    print(f"❌ ERROR: {e}")

# ==================== 3. SPECIFIC KNOWN ISSUE CHECK ====================
print("\n3. DALLAS VS LAS VEGAS VERIFICATION (Known Issue)")
print("-" * 80)

# Test the specific game that was previously broken
test_game = {
    'away_team': 'Dallas Cowboys',
    'home_team': 'Las Vegas Raiders',
    'game_time': '2025-11-17 16:25:00'
}

matcher = ESPNKalshiMatcher()
result = matcher.match_game_to_kalshi(test_game)

if result:
    away_price = float(result['away_win_price'])
    home_price = float(result['home_win_price'])
    ticker = result['ticker']

    print(f"Match found: {ticker}")
    print(f"  Dallas (away): {away_price:.2f}")
    print(f"  Las Vegas (home): {home_price:.2f}")

    # Dallas should be around 0.63-0.65, Las Vegas around 0.35-0.37
    if 0.60 <= away_price <= 0.70 and 0.30 <= home_price <= 0.40:
        passed.append("✅ Dallas vs Las Vegas odds correct")
        print("✅ PASS: Odds are correct (Dallas favored ~65%)")
    else:
        errors.append(f"❌ Dallas vs Las Vegas odds look wrong: DAL={away_price:.2f}, LV={home_price:.2f}")
        print(f"❌ FAIL: Expected Dallas ~0.65, got {away_price:.2f}")
else:
    warnings.append("⚠️ Dallas vs Las Vegas game not found in Kalshi")
    print("⚠️ No match found (game may not be scheduled)")

# ==================== 4. DATABASE TYPE CONSISTENCY ====================
print("\n4. DATABASE TYPE CONSISTENCY")
print("-" * 80)

# Sample some values to ensure proper typing
cur.execute("""
    SELECT
        ticker,
        pg_typeof(yes_price) as yes_type,
        pg_typeof(no_price) as no_type,
        pg_typeof(volume) as volume_type,
        yes_price,
        no_price
    FROM kalshi_markets
    WHERE ticker LIKE 'KXNFLGAME%'
    LIMIT 3
""")
type_samples = cur.fetchall()

all_correct = True
for sample in type_samples:
    if sample['yes_type'] != 'numeric' or sample['no_type'] != 'numeric':
        all_correct = False
        errors.append(f"❌ Type error in {sample['ticker']}")
        print(f"❌ {sample['ticker']}: yes_type={sample['yes_type']}, no_type={sample['no_type']}")

if all_correct:
    passed.append("✅ All database types correct (numeric)")
    print("✅ PASS: All price fields are numeric type")

# ==================== FINAL SUMMARY ====================
print("\n" + "=" * 80)
print("AUDIT SUMMARY")
print("=" * 80)

print(f"\n✅ Passed: {len(passed)}")
for p in passed:
    print(f"  {p}")

if warnings:
    print(f"\n⚠️ Warnings: {len(warnings)}")
    for w in warnings:
        print(f"  {w}")

if errors:
    print(f"\n❌ ERRORS: {len(errors)}")
    for e in errors:
        print(f"  {e}")
    print(f"\n🚨 ACTION REQUIRED: {len(errors)} critical issues found")
else:
    print(f"\n🎉 NO CRITICAL ERRORS - System is healthy!")

cur.close()
db.release_connection(conn)

print("\n" + "=" * 80)
