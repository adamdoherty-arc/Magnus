"""Clean up dummy data from Xtrades database"""

import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()

print("=" * 80)
print("XTRADES DUMMY DATA CLEANUP")
print("=" * 80)

# Database connection
db_params = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'magnus'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD')
}

try:
    conn = psycopg2.connect(**db_params)
    cursor = conn.cursor()

    print("\n1. Checking for dummy profiles...")
    cursor.execute("""
        SELECT id, username, display_name, total_trades_scraped
        FROM xtrades_profiles
        ORDER BY id
    """)
    profiles = cursor.fetchall()

    if profiles:
        print(f"\n   Found {len(profiles)} profiles:")
        dummy_profile_ids = []
        for profile_id, username, display_name, trades in profiles:
            print(f"   - ID: {profile_id}, Username: {username}, Display: {display_name}, Trades: {trades}")
            # Identify dummy profiles
            if username in ['traderJoe', 'optionsGuru', 'wheelKing']:
                dummy_profile_ids.append(profile_id)
                print(f"     [!] DUMMY PROFILE DETECTED")
    else:
        print("   No profiles found")

    print("\n2. Checking for trades...")
    cursor.execute("""
        SELECT COUNT(*) FROM xtrades_trades
    """)
    trade_count = cursor.fetchone()[0]
    print(f"   Total trades: {trade_count}")

    if trade_count > 0:
        cursor.execute("""
            SELECT t.id, p.username, t.ticker, t.strategy, t.strike_price, t.entry_price
            FROM xtrades_trades t
            JOIN xtrades_profiles p ON t.profile_id = p.id
            ORDER BY t.id
            LIMIT 20
        """)
        trades = cursor.fetchall()
        print(f"\n   First {len(trades)} trades:")
        for trade_id, username, ticker, strategy, strike, premium in trades:
            print(f"   - ID: {trade_id}, Profile: {username}, {ticker} {strategy} ${premium} ${strike}")

    # Delete dummy data if found
    if dummy_profile_ids:
        print(f"\n3. Deleting dummy data...")
        print(f"   Dummy profile IDs: {dummy_profile_ids}")

        # Delete trades first (foreign key constraint)
        for profile_id in dummy_profile_ids:
            cursor.execute("DELETE FROM xtrades_trades WHERE profile_id = %s", (profile_id,))
            deleted_trades = cursor.rowcount
            print(f"   - Deleted {deleted_trades} trades from profile ID {profile_id}")

        # Delete profiles
        cursor.execute("DELETE FROM xtrades_profiles WHERE id = ANY(%s)", (dummy_profile_ids,))
        deleted_profiles = cursor.rowcount
        print(f"   - Deleted {deleted_profiles} dummy profiles")

        # Delete dummy sync logs
        cursor.execute("DELETE FROM xtrades_sync_log WHERE profiles_synced IN (2, 3)")
        deleted_logs = cursor.rowcount
        print(f"   - Deleted {deleted_logs} dummy sync logs")

        # Commit changes
        conn.commit()
        print("\n   [OK] Dummy data deleted successfully!")
    else:
        print("\n3. No dummy data found - database is clean!")

    # Show final state
    print("\n4. Final verification...")
    cursor.execute("SELECT COUNT(*) FROM xtrades_profiles")
    final_profiles = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM xtrades_trades")
    final_trades = cursor.fetchone()[0]

    print(f"   Profiles remaining: {final_profiles}")
    print(f"   Trades remaining: {final_trades}")

    cursor.close()
    conn.close()

    print("\n" + "=" * 80)
    print("CLEANUP COMPLETE")
    print("=" * 80)

except Exception as e:
    print(f"\n[ERROR] {e}")
    import traceback
    traceback.print_exc()
