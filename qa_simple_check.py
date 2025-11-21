"""Simple QA Check - ASCII only"""

import sys
sys.path.insert(0, 'c:\\Code\\WheelStrategy')

import psycopg2
import pandas as pd

def connect_db():
    return psycopg2.connect('dbname=magnus user=postgres password=postgres123! host=localhost')

print("="*80)
print("MAGNUS DASHBOARD - COMPREHENSIVE QA CHECK")
print("="*80)

# 1. Database Tables Check
print("\n1. DATABASE TABLES")
print("-"*80)

conn = connect_db()
cur = conn.cursor()

tables = [
    'stocks', 'stock_data', 'stock_premiums', 'tv_watchlists',
    'tv_watchlist_symbols', 'trade_history', 'earnings_events',
    'options_flow', 'sector_analysis', 'positions'
]

table_status = {}
for table in tables:
    cur.execute(f"SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = '{table}')")
    exists = cur.fetchone()[0]

    if exists:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        status = "OK"
    else:
        count = 0
        status = "MISSING"

    table_status[table] = {'status': status, 'count': count}
    print(f"  {table:30s} {status:10s} {count:>8} rows")

# 2. Data Coverage Check
print("\n2. DATA COVERAGE")
print("-"*80)

cur.execute("SELECT COUNT(*) FROM stocks")
total_stocks = cur.fetchone()[0]
print(f"  Total stocks in database: {total_stocks}")

cur.execute("SELECT COUNT(DISTINCT symbol) FROM stock_premiums")
stocks_with_options = cur.fetchone()[0]
print(f"  Stocks with options data: {stocks_with_options}")

coverage_pct = (stocks_with_options / total_stocks * 100) if total_stocks > 0 else 0
print(f"  Options data coverage: {coverage_pct:.1f}%")

# 3. Watchlists Check
print("\n3. TRADINGVIEW WATCHLISTS")
print("-"*80)

cur.execute("SELECT COUNT(*) FROM tv_watchlists")
watchlist_count = cur.fetchone()[0]
print(f"  Total watchlists: {watchlist_count}")

cur.execute("SELECT COUNT(DISTINCT symbol) FROM tv_watchlist_symbols")
unique_symbols = cur.fetchone()[0]
print(f"  Unique symbols across all watchlists: {unique_symbols}")

# Get top 5 watchlists
cur.execute("""
    SELECT w.name, COUNT(s.symbol) as cnt
    FROM tv_watchlists w
    LEFT JOIN tv_watchlist_symbols s ON w.id = s.watchlist_id
    GROUP BY w.id, w.name
    ORDER BY cnt DESC
    LIMIT 5
""")
print("\n  Top 5 Watchlists:")
for name, cnt in cur.fetchall():
    print(f"    - {name}: {cnt} symbols")

# 4. Options Data Quality
print("\n4. OPTIONS DATA QUALITY")
print("-"*80)

cur.execute("""
    SELECT
        COUNT(*) as total,
        COUNT(DISTINCT symbol) as symbols,
        MIN(dte) as min_dte,
        MAX(dte) as max_dte,
        AVG(premium) as avg_premium
    FROM stock_premiums
    WHERE premium > 0
""")
result = cur.fetchone()
print(f"  Total option contracts: {result[0]}")
print(f"  Unique symbols: {result[1]}")
print(f"  DTE range: {result[2]} to {result[3]} days")
print(f"  Average premium: ${result[4]:.2f}" if result[4] else "  Average premium: N/A")

# 5. CSP Opportunities (30-day, delta 0.25-0.40)
print("\n5. CSP OPPORTUNITIES (30-DAY)")
print("-"*80)

cur.execute("""
    SELECT COUNT(*), COUNT(DISTINCT symbol)
    FROM stock_premiums
    WHERE dte BETWEEN 28 AND 32
        AND ABS(delta) BETWEEN 0.25 AND 0.40
        AND premium > 0
""")
opps, symbols = cur.fetchone()
print(f"  30-day opportunities available: {opps}")
print(f"  Unique symbols with 30-day options: {symbols}")

# 6. Sector Analysis
print("\n6. SECTOR ANALYSIS")
print("-"*80)

if table_status['sector_analysis']['status'] == 'OK':
    cur.execute("SELECT COUNT(*) FROM sector_analysis WHERE stock_count > 0")
    sector_count = cur.fetchone()[0]
    print(f"  Sectors analyzed: {sector_count}")

    cur.execute("""
        SELECT sector, stock_count, avg_monthly_return
        FROM sector_analysis
        WHERE stock_count > 0
        ORDER BY overall_score DESC
        LIMIT 3
    """)
    print("\n  Top 3 Sectors:")
    for sector, stocks, ret in cur.fetchall():
        print(f"    - {sector}: {stocks} stocks, {ret:.2f}% monthly return")
else:
    print("  [NOT CONFIGURED] Run migration to enable sector analysis")

# 7. Premium Options Flow
print("\n7. PREMIUM OPTIONS FLOW")
print("-"*80)

if table_status['options_flow']['status'] == 'OK':
    cur.execute("SELECT COUNT(*), MAX(flow_date) FROM options_flow")
    flow_count, last_date = cur.fetchone()
    print(f"  Flow records in database: {flow_count}")
    print(f"  Most recent flow data: {last_date}")
else:
    print("  [NOT CONFIGURED] Run migration to enable premium flow tracking")

# 8. Earnings Calendar
print("\n8. EARNINGS CALENDAR")
print("-"*80)

if table_status['earnings_events']['status'] == 'OK':
    cur.execute("SELECT COUNT(*) FROM earnings_events")
    earnings_count = cur.fetchone()[0]
    print(f"  Earnings events in database: {earnings_count}")

    cur.execute("""
        SELECT COUNT(*)
        FROM earnings_events
        WHERE earnings_date >= CURRENT_DATE
            AND earnings_date <= CURRENT_DATE + INTERVAL '30 days'
    """)
    upcoming = cur.fetchone()[0]
    print(f"  Upcoming earnings (next 30 days): {upcoming}")
else:
    print("  [NOT CONFIGURED] Initialize earnings calendar in the UI")

# 9. Trade History
print("\n9. TRADE HISTORY")
print("-"*80)

cur.execute("SELECT COUNT(*) FROM trade_history")
trades_count = cur.fetchone()[0]
print(f"  Historical trades: {trades_count}")

if trades_count > 0:
    cur.execute("""
        SELECT
            COUNT(DISTINCT symbol),
            SUM(CASE WHEN status = 'closed' THEN 1 ELSE 0 END),
            SUM(profit_loss)
        FROM trade_history
    """)
    symbols, closed, total_pl = cur.fetchone()
    print(f"  Unique symbols traded: {symbols}")
    print(f"  Closed trades: {closed}")
    print(f"  Total P/L: ${total_pl:.2f}" if total_pl else "  Total P/L: $0.00")

# Summary Score
print("\n"+"="*80)
print("HEALTH SCORE CALCULATION")
print("="*80)

# Calculate health score (0-10)
score_components = {
    'Database Tables': 10 if sum(1 for t in table_status.values() if t['status'] == 'OK') >= 8 else 5,
    'Stock Data': 10 if total_stocks >= 1000 else (total_stocks / 100),
    'Options Coverage': (coverage_pct / 10) if coverage_pct > 0 else 0,
    'Watchlists': 10 if watchlist_count >= 5 else (watchlist_count * 2),
    'CSP Opportunities': 10 if opps >= 50 else (opps / 5),
    'Trade History': 10 if trades_count >= 10 else (trades_count if trades_count > 0 else 0)
}

total_score = sum(score_components.values())
max_score = 60
health_score = (total_score / max_score) * 10

print(f"\nComponent Scores:")
for component, score in score_components.items():
    print(f"  {component:25s}: {score:.1f}/10")

print(f"\nOVERALL HEALTH SCORE: {health_score:.1f}/10.0")

if health_score >= 9.0:
    status_msg = "EXCELLENT - Dashboard fully operational"
elif health_score >= 7.0:
    status_msg = "GOOD - Most features working, minor gaps"
elif health_score >= 5.0:
    status_msg = "FAIR - Core features work, needs data sync"
else:
    status_msg = "POOR - Requires setup and data sync"

print(f"Status: {status_msg}")

# Critical Issues
print("\n"+"="*80)
print("CRITICAL ISSUES")
print("="*80)

critical_issues = []

if table_status['sector_analysis']['status'] == 'MISSING':
    critical_issues.append("Sector Analysis tables not created - run migration")

if table_status['options_flow']['status'] == 'MISSING':
    critical_issues.append("Premium Options Flow tables not created - run migration")

if coverage_pct < 10:
    critical_issues.append(f"Low options data coverage ({coverage_pct:.1f}%) - sync more watchlist data")

if opps < 20:
    critical_issues.append(f"Limited CSP opportunities ({opps}) - sync 30-day options data")

if critical_issues:
    for i, issue in enumerate(critical_issues, 1):
        print(f"  {i}. {issue}")
else:
    print("  No critical issues found!")

cur.close()
conn.close()

print("\n"+"="*80)
print("QA CHECK COMPLETE")
print("="*80)
