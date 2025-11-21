#!/usr/bin/env python3
"""Check actual watchlist data in database"""

import psycopg2
from dotenv import load_dotenv
import os

load_dotenv()

conn = psycopg2.connect(
    host=os.getenv('DB_HOST', 'localhost'),
    port=os.getenv('DB_PORT', '5432'),
    user=os.getenv('DB_USER', 'postgres'),
    password=os.getenv('DB_PASSWORD', 'postgres123!'),
    database=os.getenv('DB_NAME', 'magnus')
)
cur = conn.cursor()

print("=" * 80)
print("WATCHLIST DATABASE CHECK")
print("=" * 80)

# Check watchlists table
print("\n1. All watchlists:")
cur.execute("""
    SELECT id, name, source, created_at, updated_at
    FROM tv_watchlists
    ORDER BY name
""")

watchlists = cur.fetchall()
print(f"   Found {len(watchlists)} watchlists")

for wl in watchlists:
    print(f"   - ID: {wl[0]}, Name: '{wl[1]}', Source: {wl[2]}, "
          f"Created: {wl[3]}, Updated: {wl[4]}")

# Count symbols per watchlist
print("\n2. Symbol counts per watchlist:")
cur.execute("""
    SELECT w.id, w.name, COUNT(ws.symbol) as symbol_count
    FROM tv_watchlists w
    LEFT JOIN tv_watchlist_symbols ws ON w.id = ws.watchlist_id
    GROUP BY w.id, w.name
    ORDER BY w.name
""")

counts = cur.fetchall()
for row in counts:
    print(f"   - {row[1]}: {row[2]} symbols")

# Check if NVDA watchlist exists with symbols
print("\n3. NVDA watchlist details:")
cur.execute("""
    SELECT ws.symbol
    FROM tv_watchlist_symbols ws
    JOIN tv_watchlists w ON ws.watchlist_id = w.id
    WHERE w.name = 'NVDA'
    ORDER BY ws.symbol
""")

nvda_symbols = cur.fetchall()
print(f"   Found {len(nvda_symbols)} symbols")
if nvda_symbols:
    print(f"   First 20 symbols: {[s[0] for s in nvda_symbols[:20]]}")

# Check total symbols
print("\n4. Total symbols in tv_watchlist_symbols:")
cur.execute("SELECT COUNT(*) FROM tv_watchlist_symbols")
total = cur.fetchone()[0]
print(f"   Total: {total:,}")

# Check if watchlist name is case-sensitive
print("\n5. Checking for case variations:")
cur.execute("""
    SELECT DISTINCT name
    FROM tv_watchlists
    WHERE LOWER(name) LIKE '%nvda%'
""")
matches = cur.fetchall()
print(f"   Watchlists with 'nvda' in name: {[m[0] for m in matches]}")

cur.close()
conn.close()

print("\n" + "=" * 80)
