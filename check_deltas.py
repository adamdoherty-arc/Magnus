"""Check actual delta values"""
import sys
sys.path.insert(0, 'c:\\Code\\WheelStrategy')

from src.tradingview_db_manager import TradingViewDBManager

tv_manager = TradingViewDBManager()
conn = tv_manager.get_connection()
cur = conn.cursor()

symbols = ['BMNR', 'UPST', 'CIFR', 'HIMS']

print("=" * 80)
print("CHECKING ACTUAL DELTA VALUES FOR 30-DAY OPTIONS")
print("=" * 80)

for symbol in symbols:
    print(f"\n{symbol}:")
    cur.execute("""
        SELECT strike_price, dte, delta, premium, strike_type
        FROM stock_premiums
        WHERE symbol = %s
            AND dte BETWEEN 20 AND 40
        ORDER BY dte, delta
    """, (symbol,))

    rows = cur.fetchall()
    if rows:
        for strike, dte, delta, premium, strike_type in rows:
            delta_val = float(delta) if delta else 0
            print(f"  DTE={dte}, Strike=${strike:.2f}, Delta={delta_val:.3f}, Premium=${premium:.2f}, Type={strike_type}")
    else:
        print("  No data found!")

cur.close()
conn.close()
