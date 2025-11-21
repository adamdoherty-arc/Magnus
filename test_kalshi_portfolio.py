"""
Test script to pull Kalshi prediction market positions
Since Robinhood uses Kalshi for prediction markets, your positions should be here.
"""

from src.kalshi_client import KalshiClient
from dotenv import load_dotenv
import json

load_dotenv()

def main():
    print("\n" + "="*80)
    print("KALSHI PORTFOLIO POSITIONS TEST")
    print("="*80)

    # Initialize client
    client = KalshiClient()

    # Login
    print("\n[LOGIN] Logging into Kalshi...")
    if not client.login():
        print("\n[ERROR] Login failed!")
        print("\n[TIP] Make sure you have KALSHI_EMAIL and KALSHI_PASSWORD in your .env file")
        print("      If you're accessing Robinhood prediction markets, they use Kalshi.")
        return

    print("[SUCCESS] Login successful!")

    # Get balance
    print("\n[BALANCE] Fetching account balance...")
    balance = client.get_portfolio_balance()

    if balance:
        cash = balance.get('balance', 0) / 100
        portfolio_value = balance.get('payout', 0) / 100
        print(f"   Cash Balance: ${cash:,.2f}")
        print(f"   Portfolio Value: ${portfolio_value:,.2f}")
        print(f"   Total: ${cash + portfolio_value:,.2f}")
    else:
        print("   [ERROR] Could not fetch balance")

    # Get positions
    print("\n[POSITIONS] Fetching portfolio positions...")
    positions = client.get_portfolio_positions()

    if not positions:
        print("   [INFO] No active positions found")
        print("   (Only non-zero positions are shown)")
    else:
        print(f"   Found {len(positions)} active positions:")
        print("\n" + "="*80)

        for i, pos in enumerate(positions, 1):
            ticker = pos.get('ticker', 'Unknown')
            position = pos.get('position', 0)
            exposure = pos.get('market_exposure', 0) / 100
            realized_pnl = pos.get('realized_pnl', 0) / 100
            unrealized_pnl = pos.get('rest_pnl', 0) / 100
            total_pnl = realized_pnl + unrealized_pnl

            # PnL color coding
            pnl_symbol = "🟢" if total_pnl >= 0 else "🔴"

            print(f"\n{i}. {ticker}")
            print(f"   Position: {position} contracts")
            print(f"   Exposure: ${exposure:,.2f}")
            print(f"   {pnl_symbol} Total P&L: ${total_pnl:+,.2f}")
            print(f"      Realized: ${realized_pnl:+,.2f}")
            print(f"      Unrealized: ${unrealized_pnl:+,.2f}")

    # Get enhanced positions with market details
    print("\n📈 Fetching enhanced positions with market details...")
    print("   (This may take a moment...)")

    enhanced = client.get_all_positions_with_details()

    if enhanced:
        print(f"\n   Enhanced {len(enhanced)} positions:")
        print("\n" + "="*80)

        for i, pos in enumerate(enhanced, 1):
            title = pos.get('title', 'Unknown Market')
            ticker = pos.get('ticker', 'Unknown')
            position = pos.get('position', 0)
            yes_price = pos.get('yes_price', 0)
            no_price = pos.get('no_price', 0)
            status = pos.get('status', 'unknown')
            category = pos.get('category', 'unknown')
            unrealized_pnl = pos.get('rest_pnl', 0) / 100

            pnl_symbol = "🟢" if unrealized_pnl >= 0 else "🔴"

            print(f"\n{i}. {title}")
            print(f"   Ticker: {ticker}")
            print(f"   Category: {category}")
            print(f"   Status: {status}")
            print(f"   Position: {position} contracts")
            print(f"   Current Prices: YES {yes_price}¢ / NO {no_price}¢")
            print(f"   {pnl_symbol} Unrealized P&L: ${unrealized_pnl:+,.2f}")

    # Get recent fills (trade history)
    print("\n📜 Fetching recent fills (last 10 trades)...")
    fills_data = client.get_fills(limit=10)
    fills = fills_data.get('fills', [])

    if not fills:
        print("   ℹ️  No recent fills found")
    else:
        print(f"\n   Found {len(fills)} recent fills:")
        print("\n" + "="*80)

        for i, fill in enumerate(fills, 1):
            ticker = fill.get('ticker', 'Unknown')
            side = fill.get('purchased_side', 'Unknown')
            action = fill.get('action', 'unknown')
            count = fill.get('count', 0)
            price = fill.get('price', 0)
            created_time = fill.get('created_time', 'Unknown')

            # Format timestamp
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_time.replace('Z', '+00:00'))
                time_str = dt.strftime('%Y-%m-%d %H:%M')
            except:
                time_str = created_time

            action_symbol = "🟢" if action == 'buy' else "🔴"

            print(f"\n{i}. {ticker}")
            print(f"   {action_symbol} {action.upper()} {count} {side} @ {price}¢")
            print(f"   Time: {time_str}")

    print("\n" + "="*80)
    print("PORTFOLIO TEST COMPLETE!")
    print("="*80)

    # Save to file for reference
    if positions:
        output = {
            'balance': balance,
            'positions': positions,
            'enhanced_positions': enhanced,
            'recent_fills': fills
        }

        with open('kalshi_portfolio_snapshot.json', 'w') as f:
            json.dump(output, f, indent=2)

        print("\n💾 Portfolio snapshot saved to: kalshi_portfolio_snapshot.json")

if __name__ == "__main__":
    main()
