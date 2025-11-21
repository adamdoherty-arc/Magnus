"""
Quick Data Verification Script
Checks that Kalshi data is synced correctly
"""
import sys
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

from src.kalshi_db_manager import KalshiDBManager

db = KalshiDBManager()
conn = db.get_connection()
cur = conn.cursor()

print("\n" + "="*80)
print("KALSHI DATA VERIFICATION")
print("="*80)

# 1. Count markets by type
cur.execute("SELECT market_type, COUNT(*) FROM kalshi_markets GROUP BY market_type")
print("\n1. MARKETS BY TYPE:")
total = 0
for row in cur.fetchall():
    count = row[1]
    total += count
    print(f"   {row[0]}: {count:,} markets")
print(f"   TOTAL: {total:,} markets")

# 2. Check for combo bets (should be ZERO)
cur.execute("SELECT COUNT(*) FROM kalshi_markets WHERE title LIKE '%,%'")
combos = cur.fetchone()[0]
print(f"\n2. COMBO BETS (should be 0): {combos}")
if combos > 0:
    print("   ERROR: Found combo bets that should have been filtered!")

# 3. Sample valid markets
cur.execute("""
    SELECT title, market_type, yes_price
    FROM kalshi_markets
    WHERE title NOT LIKE '%,%'
    ORDER BY created_at DESC
    LIMIT 10
""")
print("\n3. SAMPLE MARKETS (recent, non-combos):")
for row in cur.fetchall():
    title = row[0][:60]
    market_type = row[1]
    yes_price = row[2] if row[2] else 0
    print(f"   [{market_type}] {title} | Yes: {yes_price}%")

# 4. Check predictions
cur.execute("SELECT COUNT(*) FROM kalshi_predictions")
pred_count = cur.fetchone()[0]
print(f"\n4. AI PREDICTIONS: {pred_count}")

# 5. Check price history
cur.execute("SELECT COUNT(*) FROM kalshi_price_history")
price_count = cur.fetchone()[0]
print(f"\n5. PRICE SNAPSHOTS: {price_count}")

# 6. Check sync log
cur.execute("SELECT COUNT(*), MAX(sync_time) FROM kalshi_sync_log")
log_row = cur.fetchone()
print(f"\n6. SYNC HISTORY: {log_row[0]} syncs")
if log_row[1]:
    print(f"   Last sync: {log_row[1]}")

cur.close()
db.release_connection(conn)

print("\n" + "="*80)
if combos == 0 and total > 0:
    print("STATUS: PASS - Data looks clean!")
else:
    print("STATUS: ISSUES FOUND - See above")
print("="*80 + "\n")
