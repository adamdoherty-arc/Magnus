#!/usr/bin/env python3
"""Debug AI Agent Query - Find why it returns 0 results"""

import sys
import os
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.ai_options_agent.ai_options_db_manager import AIOptionsDBManager
from src.data.options_queries import get_premium_opportunities
import psycopg2
from dotenv import load_dotenv

load_dotenv()

def main():
    print("=" * 80)
    print("AI AGENT QUERY DEBUG")
    print("=" * 80)

    db_manager = AIOptionsDBManager()

    # Test 1: Check watchlist symbols
    print("\n1. Checking NVDA watchlist...")
    watchlist_name = "NVDA"
    symbols = db_manager.get_watchlist_symbols(watchlist_name)
    print(f"   Found {len(symbols)} symbols in watchlist: {watchlist_name}")
    if symbols:
        print(f"   First 10 symbols: {symbols[:10]}")
    else:
        print("   ERROR: No symbols found!")

    # Test 2: Check if stock_premiums has data
    print("\n2. Checking stock_premiums table...")
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        port=os.getenv('DB_PORT', '5432'),
        user=os.getenv('DB_USER', 'postgres'),
        password=os.getenv('DB_PASSWORD', 'postgres123!'),
        database=os.getenv('DB_NAME', 'magnus')
    )
    cur = conn.cursor()

    # Count total premiums
    cur.execute("SELECT COUNT(*) FROM stock_premiums")
    total_premiums = cur.fetchone()[0]
    print(f"   Total premiums in database: {total_premiums:,}")

    # Count premiums for watchlist symbols
    if symbols:
        cur.execute("""
            SELECT COUNT(*)
            FROM stock_premiums
            WHERE symbol = ANY(%s)
        """, (symbols,))
        watchlist_premiums = cur.fetchone()[0]
        print(f"   Premiums for watchlist symbols: {watchlist_premiums:,}")

        # Check specific symbol
        test_symbol = symbols[0]
        cur.execute("""
            SELECT COUNT(*), MIN(dte), MAX(dte), MIN(delta), MAX(delta)
            FROM stock_premiums
            WHERE symbol = %s
        """, (test_symbol,))
        row = cur.fetchone()
        print(f"   Example symbol '{test_symbol}':")
        print(f"     Count: {row[0]}, DTE range: {row[1]}-{row[2]}, Delta range: {row[3]:.3f} to {row[4]:.3f}")

    # Test 3: Test centralized data layer query
    print("\n3. Testing get_premium_opportunities()...")
    filters = {
        'min_delta': -0.45,
        'max_delta': -0.15,
        'min_dte': 20,
        'max_dte': 40,
        'min_premium_pct': 0.5,
        'min_annual_return': 0,
        'min_volume': 10,
        'min_open_interest': 50,
        'limit': 400
    }

    try:
        opportunities = get_premium_opportunities(filters)
        print(f"   Query returned {len(opportunities)} total opportunities")

        if opportunities:
            # Filter by watchlist symbols
            filtered = [opp for opp in opportunities if opp.get('symbol') in symbols]
            print(f"   After filtering by watchlist: {len(filtered)} opportunities")

            if filtered:
                print(f"\n   Top 3 opportunities:")
                for i, opp in enumerate(filtered[:3]):
                    print(f"     {i+1}. {opp['symbol']} - ${opp.get('strike_price', 0):.2f} "
                          f"strike, DTE={opp.get('dte', 0)}, "
                          f"Delta={opp.get('delta', 0):.3f}, "
                          f"Premium=${opp.get('premium', 0)/100:.2f}")
        else:
            print("   ERROR: Query returned 0 results!")

    except Exception as e:
        print(f"   ERROR: {e}")
        import traceback
        traceback.print_exc()

    # Test 4: Direct query with exact UI parameters
    print("\n4. Testing direct SQL query with UI parameters...")
    cur.execute("""
        SELECT
            symbol,
            strike_price,
            dte,
            delta,
            premium,
            annual_return
        FROM stock_premiums
        WHERE symbol = ANY(%s)
            AND dte BETWEEN 20 AND 40
            AND delta BETWEEN -0.45 AND -0.15
            AND premium >= 100
            AND volume >= 10
            AND open_interest >= 50
        ORDER BY annual_return DESC
        LIMIT 10
    """, (symbols,))

    direct_results = cur.fetchall()
    print(f"   Direct query returned {len(direct_results)} results")

    if direct_results:
        print(f"   Top results:")
        for row in direct_results:
            print(f"     {row[0]} - ${row[1]:.2f} strike, DTE={row[2]}, "
                  f"Delta={row[3]:.3f}, Premium=${row[4]/100:.2f}, "
                  f"Annual={row[5]:.1f}%")

    # Test 5: Check analyze_watchlist method
    print("\n5. Testing analyze_watchlist()...")
    from src.ai_options_agent.options_analysis_agent import OptionsAnalysisAgent

    agent = OptionsAnalysisAgent(db_manager=db_manager)
    analyses = agent.analyze_watchlist(
        watchlist_name="NVDA",
        dte_range=(20, 40),
        delta_range=(-0.45, -0.15),
        min_premium=100.0,
        limit=200,
        use_llm=False
    )

    print(f"   analyze_watchlist() returned {len(analyses)} results")

    if analyses:
        # Check scores
        scores = [a['final_score'] for a in analyses]
        print(f"   Score range: {min(scores):.0f} - {max(scores):.0f}")
        print(f"   Scores >= 50: {len([s for s in scores if s >= 50])}")
        print(f"   Scores >= 100: {len([s for s in scores if s >= 100])}")

        print(f"\n   Top 3 analyses:")
        for i, analysis in enumerate(analyses[:3]):
            print(f"     {i+1}. {analysis['symbol']} - Score: {analysis['final_score']}/100")
            print(f"        Recommendation: {analysis['recommendation']}")

    cur.close()
    conn.close()

    print("\n" + "=" * 80)
    print("DEBUG COMPLETE")
    print("=" * 80)

if __name__ == "__main__":
    main()
