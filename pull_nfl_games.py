"""
Pull NFL Games from Kalshi and Run AI Predictions
Uses the public API endpoint for market data
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.kalshi_integration import KalshiIntegration
from src.kalshi_db_manager import KalshiDBManager
from src.kalshi_ai_evaluator import KalshiAIEvaluator
from datetime import datetime
import json

def main():
    print("="*80)
    print("KALSHI NFL GAMES - AI-POWERED ANALYSIS")
    print("="*80)
    print(f"Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

    # Initialize components
    print("\n[1/6] Initializing components...")
    kalshi = KalshiIntegration()
    db = KalshiDBManager()
    evaluator = KalshiAIEvaluator()
    print("    [OK] API client ready")
    print("    [OK] Database ready")
    print("    [OK] AI evaluator ready")

    # Fetch all markets
    print("\n[2/6] Fetching markets from Kalshi...")
    all_markets = kalshi.get_markets(limit=500, status='active')
    print(f"    [OK] Retrieved {len(all_markets)} total active markets")

    # Filter for NFL and College Football
    print("\n[3/6] Filtering for football markets...")
    nfl_markets = []
    college_markets = []

    # NFL keywords
    nfl_keywords = [
        'nfl', 'super bowl', 'playoffs', 'chiefs', 'bills', 'ravens',
        'packers', '49ers', 'cowboys', 'eagles', 'lions', 'rams',
        'dolphins', 'bengals', 'steelers', 'seahawks', 'buccaneers',
        'patriots', 'broncos', 'raiders', 'chargers', 'jets', 'colts',
        'jaguars', 'titans', 'cardinals', 'falcons', 'panthers', 'saints',
        'commanders', 'giants', 'bears', 'browns', 'texans', 'vikings'
    ]

    # College keywords
    college_keywords = [
        'college football', 'ncaa football', 'cfp', 'alabama', 'georgia',
        'ohio state', 'michigan', 'texas', 'clemson', 'oregon', 'penn state',
        'notre dame', 'usc', 'lsu', 'florida', 'tennessee', 'oklahoma'
    ]

    for market in all_markets:
        title = market.get('title', '').lower()
        ticker = market.get('ticker', '').lower()
        subtitle = market.get('subtitle', '').lower()

        combined = f"{title} {ticker} {subtitle}"

        # Check for NFL
        if any(keyword in combined for keyword in nfl_keywords):
            nfl_markets.append(market)
        # Check for college
        elif any(keyword in combined for keyword in college_keywords):
            college_markets.append(market)

    print(f"    [OK] Found {len(nfl_markets)} NFL markets")
    print(f"    [OK] Found {len(college_markets)} college football markets")

    if len(nfl_markets) == 0:
        print("\n    WARNING: No NFL markets found. This might be off-season.")
        print("    Showing all markets for debugging:")
        for i, market in enumerate(all_markets[:10], 1):
            print(f"      {i}. {market.get('title', 'N/A')}")

    # Store markets in database
    print("\n[4/6] Storing markets in database...")
    if nfl_markets:
        nfl_stored = db.store_markets(nfl_markets, 'nfl')
        print(f"    [OK] Stored {nfl_stored} NFL markets")

    if college_markets:
        college_stored = db.store_markets(college_markets, 'college')
        print(f"    [OK] Stored {college_stored} college markets")

    # Get active markets for AI analysis
    print("\n[5/6] Running AI predictions...")
    active_markets = db.get_active_markets()
    print(f"    [OK] Analyzing {len(active_markets)} active markets")

    if active_markets:
        # Generate predictions
        predictions = evaluator.evaluate_markets(active_markets)
        print(f"    [OK] Generated {len(predictions)} predictions")

        # Store predictions
        if predictions:
            stored = db.store_predictions(predictions)
            print(f"    [OK] Stored {stored} predictions in database")

            # Show top opportunities
            print("\n[6/6] TOP BETTING OPPORTUNITIES")
            print("="*80)

            # Get top opportunities
            top_opps = db.get_top_opportunities(limit=20)

            if top_opps:
                for i, opp in enumerate(top_opps, 1):
                    market_type = opp.get('market_type', 'N/A').upper()
                    title = opp.get('title', 'N/A')
                    predicted = opp.get('predicted_outcome', 'N/A').upper()
                    confidence = opp.get('confidence_score', 0)
                    edge = opp.get('edge_percentage', 0)
                    yes_price = opp.get('yes_price', 0)
                    recommended_action = opp.get('recommended_action', 'pass').upper()
                    stake = opp.get('recommended_stake_pct', 0)
                    reasoning = opp.get('reasoning', 'N/A')

                    # Color-code recommendation
                    action_symbol = {
                        'STRONG_BUY': '[STRONG BUY]',
                        'BUY': '[BUY]',
                        'HOLD': '[HOLD]',
                        'PASS': '[PASS]'
                    }.get(recommended_action, '[PASS]')

                    print(f"\n#{i} {action_symbol} [{market_type}] {title[:60]}")
                    print(f"    Predicted Outcome: {predicted}")
                    print(f"    Current Price: YES ${yes_price:.2f}")
                    print(f"    Confidence: {confidence:.1f}% | Edge: {edge:+.1f}%")
                    print(f"    Recommendation: {recommended_action} | Stake: {stake:.1f}%")
                    print(f"    Reasoning: {reasoning[:150]}")
            else:
                print("    No strong opportunities found at this time")
    else:
        print("    No active markets to analyze")

    # Show database stats
    print("\n" + "="*80)
    print("DATABASE STATISTICS")
    print("="*80)
    stats = db.get_stats()
    print(f"Total Markets: {stats['total_markets']}")
    print(f"Active Markets: {stats['active_markets']}")
    print(f"Markets by Type: {stats['markets_by_type']}")
    print(f"Total Predictions: {stats['total_predictions']}")

    print("\n" + "="*80)
    print("SUCCESS! NFL games data pulled and analyzed")
    print("="*80)
    print(f"Completed: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("\nNext steps:")
    print("1. Review top opportunities above")
    print("2. Launch dashboard: streamlit run dashboard.py")
    print("3. Navigate to Kalshi Sports Betting page")
    print("4. Place bets on Kalshi.com for opportunities you like")
    print("="*80)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nOperation cancelled by user")
    except Exception as e:
        print(f"\n\nERROR: {e}")
        import traceback
        traceback.print_exc()
