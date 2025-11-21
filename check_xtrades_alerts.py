"""
Check Xtrades Alerts in Database
================================
"""

import psycopg2
import os
import sys
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

conn = psycopg2.connect(os.getenv('DATABASE_URL'))
cur = conn.cursor()

# Total alerts and stats
cur.execute('SELECT COUNT(*) as total, COUNT(DISTINCT ticker) as unique_tickers, MAX(alert_timestamp) as latest FROM xtrades_trades')
stats = cur.fetchone()
print('\n' + '='*80)
print('DATABASE STATS:')
print('='*80)
print(f'Total alerts: {stats[0]}')
print(f'Unique tickers: {stats[1]}')
print(f'Latest alert: {stats[2]}')

# Recent alerts
print('\n' + '='*80)
print('LATEST 20 ALERTS:')
print('='*80)
cur.execute('''
    SELECT ticker, strategy, action, entry_price, strike_price,
           TO_CHAR(alert_timestamp, 'YYYY-MM-DD HH24:MI') as time
    FROM xtrades_trades
    ORDER BY alert_timestamp DESC
    LIMIT 20
''')

for row in cur.fetchall():
    ticker = row[0] or 'N/A'
    strategy = row[1] or 'N/A'
    action = row[2] or 'N/A'
    entry = row[3] or 0
    strike = row[4] or 0
    time = row[5]
    print(f'  {time} | {ticker:6s} | {strategy:10s} | {action:8s} | Entry:${entry:7.2f} | Strike:${strike:7.2f}')

# Count by profile
print('\n' + '='*80)
print('ALERTS BY PROFILE:')
print('='*80)
cur.execute('''
    SELECT p.username, p.display_name, COUNT(t.id) as alert_count
    FROM xtrades_profiles p
    LEFT JOIN xtrades_trades t ON p.id = t.profile_id
    GROUP BY p.id, p.username, p.display_name
    ORDER BY alert_count DESC
''')

for row in cur.fetchall():
    print(f'  {row[1] or row[0]:25s} | {row[2]} alerts')

cur.close()
conn.close()
print('\n')
