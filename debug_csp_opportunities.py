"""Debug script for CSP Opportunities"""
import sys
sys.path.insert(0, 'c:\\Code\\WheelStrategy')

from src.tradingview_db_manager import TradingViewDBManager

def check_data():
    """Check what data exists for position symbols"""
    tv_manager = TradingViewDBManager()
    conn = tv_manager.get_connection()
    cur = conn.cursor()

    symbols = ['BMNR', 'UPST', 'CIFR', 'HIMS']

    print("=" * 80)
    print("CHECKING STOCK_PREMIUMS COLUMNS FIRST")
    print("=" * 80)

    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'stock_premiums'
        ORDER BY ordinal_position
    """)

    columns = cur.fetchall()
    print("\nColumns in stock_premiums table:")
    for col_name, col_type in columns:
        print(f"  - {col_name}: {col_type}")

    print("\n" + "=" * 80)
    print("CHECKING OPTIONS DATA FOR CURRENT POSITION SYMBOLS")
    print("=" * 80)

    # Check if data exists
    for symbol in symbols:
        cur.execute("""
            SELECT COUNT(*) FROM stock_premiums
            WHERE symbol = %s
        """, (symbol,))
        count = cur.fetchone()[0]
        print(f"\n{symbol}: {count} rows in stock_premiums")

        if count > 0:
            # Check if 30-day options exist (WITHOUT option_type filter)
            cur.execute("""
                SELECT COUNT(*) FROM stock_premiums
                WHERE symbol = %s AND dte BETWEEN 28 AND 32
            """, (symbol,))
            dte_count = cur.fetchone()[0]
            print(f"  - 30-day options: {dte_count}")

            # Check delta range (for puts - negative delta)
            cur.execute("""
                SELECT COUNT(*) FROM stock_premiums
                WHERE symbol = %s
                    AND dte BETWEEN 28 AND 32
                    AND delta BETWEEN -0.35 AND -0.25
            """, (symbol,))
            delta_count = cur.fetchone()[0]
            print(f"  - With delta -0.35 to -0.25: {delta_count}")

    print("\n" + "=" * 80)
    print("CHECKING STOCK_PREMIUMS COLUMNS")
    print("=" * 80)

    cur.execute("""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_name = 'stock_premiums'
        ORDER BY ordinal_position
    """)

    columns = cur.fetchall()
    for col_name, col_type in columns:
        print(f"{col_name}: {col_type}")

    print("\n" + "=" * 80)
    print("TESTING CSP OPPORTUNITIES QUERY")
    print("=" * 80)

    # Test the actual query (WITHOUT option_type since it doesn't exist)
    # We assume negative delta = puts
    query = """
        SELECT DISTINCT ON (sp.symbol)
            sp.symbol,
            sd.current_price as stock_price,
            sp.strike_price,
            sp.expiration_date,
            sp.dte,
            sp.premium,
            sp.delta,
            sp.monthly_return,
            sp.implied_volatility as iv,
            sp.bid,
            sp.ask,
            sp.volume,
            sp.open_interest as oi,
            (sp.strike_price - (sp.premium / 100)) as breakeven
        FROM stock_premiums sp
        LEFT JOIN stock_data sd ON sp.symbol = sd.symbol
        WHERE sp.symbol = ANY(%s)
            AND sp.dte BETWEEN %s AND %s
            AND sp.delta BETWEEN %s AND %s
            AND sp.delta < 0
            AND sp.premium > 0
        ORDER BY sp.symbol, ABS(sp.delta - %s) ASC
    """

    try:
        cur.execute(query, (
            symbols,
            28, 32,
            -0.35, -0.25,
            -0.30
        ))

        rows = cur.fetchall()
        print(f"\nQuery returned {len(rows)} opportunities")

        if rows:
            print("\nResults:")
            for row in rows:
                print(f"  {row[0]}: Strike ${row[2]:.2f}, DTE={row[4]}, Premium=${row[5]:.2f}, Delta={row[6]:.3f}")
        else:
            print("\nNo results found!")

    except Exception as e:
        print(f"\nQuery FAILED with error: {e}")
        import traceback
        traceback.print_exc()

    cur.close()
    conn.close()

if __name__ == "__main__":
    check_data()
