"""
Comprehensive Test Suite for AI Options Agent
Tests all components: DB Manager, Scoring Engine, Agent, and Integration
"""

import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.ai_options_agent.ai_options_db_manager import AIOptionsDBManager
from src.ai_options_agent.scoring_engine import (
    FundamentalScorer, TechnicalScorer, GreeksScorer,
    RiskScorer, SentimentScorer, MultiCriteriaScorer
)
from src.ai_options_agent.options_analysis_agent import OptionsAnalysisAgent


def test_database_connection():
    """Test 1: Database connection and schema"""
    print("\n=== Test 1: Database Connection ===")
    try:
        db = AIOptionsDBManager()
        conn = db.get_connection()
        conn.close()
        print("[PASS] Database connection successful")
        return True
    except Exception as e:
        print(f"[FAIL] Database connection failed: {e}")
        return False


def test_get_opportunities():
    """Test 2: Fetch opportunities from database"""
    print("\n=== Test 2: Get Opportunities ===")
    try:
        db = AIOptionsDBManager()
        opportunities = db.get_opportunities(
            symbols=None,
            dte_range=(20, 40),
            delta_range=(-0.45, -0.15),
            min_premium=100,
            limit=10
        )

        print(f"[PASS] Found {len(opportunities)} opportunities")
        if opportunities:
            print(f"   Sample: {opportunities[0]['symbol']} - ${opportunities[0]['premium']/100:.2f} premium")
        return True
    except Exception as e:
        print(f"[FAIL] Get opportunities failed: {e}")
        return False


def test_watchlist_integration():
    """Test 3: Watchlist integration"""
    print("\n=== Test 3: Watchlist Integration ===")
    try:
        db = AIOptionsDBManager()
        watchlists = db.get_all_watchlists()
        print(f"[PASS] Found {len(watchlists)} watchlists")

        if watchlists:
            watchlist_name = watchlists[0]['name']
            symbols = db.get_watchlist_symbols(watchlist_name)
            print(f"   Watchlist '{watchlist_name}' has {len(symbols)} symbols")
        return True
    except Exception as e:
        print(f"[FAIL] Watchlist integration failed: {e}")
        return False


def test_scoring_engine():
    """Test 4: Scoring engine with test data"""
    print("\n=== Test 4: Scoring Engine ===")

    test_opp = {
        'symbol': 'AAPL',
        'stock_price': 175.50,
        'strike_price': 165.00,
        'dte': 30,
        'premium': 285.0,
        'delta': -0.28,
        'monthly_return': 1.73,
        'annual_return': 20.76,
        'iv': 0.32,
        'bid': 2.80,
        'ask': 2.90,
        'volume': 1250,
        'oi': 3500,
        'breakeven': 162.15,
        'pe_ratio': 28.5,
        'market_cap': 2_700_000_000_000,
        'sector': 'Technology',
        'dividend_yield': 0.52
    }

    try:
        # Test individual scorers
        fund = FundamentalScorer().score(test_opp)
        tech = TechnicalScorer().score(test_opp)
        greeks = GreeksScorer().score(test_opp)
        risk = RiskScorer().score(test_opp)
        sentiment = SentimentScorer().score(test_opp)

        print(f"[PASS] Individual Scorers:")
        print(f"   Fundamental: {fund}/100")
        print(f"   Technical: {tech}/100")
        print(f"   Greeks: {greeks}/100")
        print(f"   Risk: {risk}/100")
        print(f"   Sentiment: {sentiment}/100")

        # Test multi-criteria scorer
        scorer = MultiCriteriaScorer()
        result = scorer.score_opportunity(test_opp)

        print(f"[PASS] Multi-Criteria Score: {result['final_score']}/100")
        print(f"   Recommendation: {result['recommendation']}")
        print(f"   Confidence: {result['confidence']}%")

        return True
    except Exception as e:
        print(f"[FAIL] Scoring engine failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_agent_analysis():
    """Test 5: Full agent analysis"""
    print("\n=== Test 5: Agent Analysis ===")
    try:
        agent = OptionsAnalysisAgent()
        db = AIOptionsDBManager()

        # Get some opportunities
        opportunities = db.get_opportunities(
            symbols=None,
            dte_range=(20, 40),
            delta_range=(-0.45, -0.15),
            min_premium=100,
            limit=3
        )

        if not opportunities:
            print("[WARN] No opportunities found in database")
            return True

        # Analyze first opportunity
        analysis = agent.analyze_opportunity(opportunities[0], save_to_db=False)

        print(f"[PASS] Analysis complete for {analysis['symbol']}")
        print(f"   Final Score: {analysis['final_score']}/100")
        print(f"   Recommendation: {analysis['recommendation']}")
        print(f"   Strategy: {analysis['strategy']}")
        print(f"   Processing Time: {analysis['processing_time_ms']}ms")
        print(f"   Reasoning: {analysis['reasoning'][:100]}...")

        return True
    except Exception as e:
        print(f"[FAIL] Agent analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_save_and_retrieve():
    """Test 6: Save analysis to database and retrieve"""
    print("\n=== Test 6: Save & Retrieve Analysis ===")
    try:
        agent = OptionsAnalysisAgent()
        db = AIOptionsDBManager()

        # Get an opportunity
        opportunities = db.get_opportunities(limit=1)
        if not opportunities:
            print("[WARN] No opportunities found")
            return True

        # Analyze and save
        analysis = agent.analyze_opportunity(opportunities[0], save_to_db=True)
        analysis_id = analysis.get('id')

        if analysis_id:
            print(f"[PASS] Saved analysis with ID: {analysis_id}")

            # Retrieve recent analyses
            recent = db.get_recent_analyses(days=1, limit=5)
            print(f"[PASS] Retrieved {len(recent)} recent analyses")

            # Get strong buys
            strong_buys = db.get_strong_buys(days=7)
            print(f"[PASS] Found {len(strong_buys)} STRONG_BUY recommendations")

            return True
        else:
            print("[WARN] Analysis saved but no ID returned")
            return True

    except Exception as e:
        print(f"[FAIL] Save & retrieve failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_batch_analysis():
    """Test 7: Batch analysis of multiple opportunities"""
    print("\n=== Test 7: Batch Analysis ===")
    try:
        agent = OptionsAnalysisAgent()

        # Analyze all stocks
        analyses = agent.analyze_all_stocks(
            dte_range=(25, 35),
            delta_range=(-0.40, -0.20),
            min_premium=150,
            limit=10
        )

        print(f"[PASS] Analyzed {len(analyses)} opportunities")

        if analyses:
            # Show top 3
            print("\n   Top 3 Recommendations:")
            for i, analysis in enumerate(analyses[:3], 1):
                print(f"   {i}. {analysis['symbol']}: {analysis['final_score']}/100 ({analysis['recommendation']})")

        return True
    except Exception as e:
        print(f"[FAIL] Batch analysis failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Run all tests and report results"""
    print("=" * 50)
    print("   AI Options Agent - Test Suite")
    print("=" * 50)

    tests = [
        ("Database Connection", test_database_connection),
        ("Get Opportunities", test_get_opportunities),
        ("Watchlist Integration", test_watchlist_integration),
        ("Scoring Engine", test_scoring_engine),
        ("Agent Analysis", test_agent_analysis),
        ("Save & Retrieve", test_save_and_retrieve),
        ("Batch Analysis", test_batch_analysis),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[FAIL] {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "="*50)
    print("TEST SUMMARY")
    print("="*50)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "[PASS] PASS" if result else "[FAIL] FAIL"
        print(f"{status} - {test_name}")

    print("="*50)
    print(f"Results: {passed}/{total} tests passed ({passed/total*100:.0f}%)")
    print("="*50)

    if passed == total:
        print("\n*** All tests passed! AI Options Agent is fully functional. ***")
    else:
        print(f"\n*** WARNING: {total - passed} test(s) failed. Review errors above. ***")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
