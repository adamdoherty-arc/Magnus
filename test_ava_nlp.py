"""
Test AVA NLP Handler
====================

Test the natural language understanding with various queries
"""

import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from src.ava.nlp_handler import NaturalLanguageHandler

def test_nlp_queries():
    """Test various natural language queries"""
    print("=" * 60)
    print("Testing AVA Natural Language Understanding")
    print("=" * 60)
    print()

    handler = NaturalLanguageHandler()

    # Test queries with expected intents
    test_cases = [
        ("How's my portfolio?", "portfolio"),
        ("What positions do I have?", "positions"),
        ("Show me the best opportunities", "opportunities"),
        ("Any good trades for NVDA?", "opportunities"),
        ("What are you working on?", "tasks"),
        ("Are you online?", "status"),
        ("Help me", "help"),
        ("TradingView alerts", "tradingview"),
        ("Who am I following on Xtrades?", "xtrades"),
        ("What's my balance?", "portfolio"),
        ("Show positions", "positions"),
    ]

    passed = 0
    failed = 0

    for query, expected_intent in test_cases:
        print(f"Query: \"{query}\"")
        print(f"Expected: {expected_intent}")

        result = handler.parse_intent(query)

        actual_intent = result['intent']
        confidence = result['confidence']
        model = result['model_used']
        cost = result['cost']

        # Check if intent matches
        if actual_intent == expected_intent:
            status = "✅ PASS"
            passed += 1
        else:
            status = "❌ FAIL"
            failed += 1

        print(f"Result: {status}")
        print(f"  Intent: {actual_intent}")
        print(f"  Confidence: {confidence:.2f}")
        print(f"  Model: {model}")
        print(f"  Cost: ${cost:.4f}")

        if result.get('entities', {}).get('tickers'):
            print(f"  Tickers: {', '.join(result['entities']['tickers'])}")

        print()

    print("=" * 60)
    print(f"Results: {passed} passed, {failed} failed out of {len(test_cases)} tests")
    print(f"Success rate: {(passed/len(test_cases)*100):.1f}%")
    print("=" * 60)

    return passed, failed

def test_context_awareness():
    """Test context tracking"""
    print("\n" + "=" * 60)
    print("Testing Context Awareness")
    print("=" * 60)
    print()

    handler = NaturalLanguageHandler()

    # First query
    query1 = "Show me opportunities for NVDA"
    result1 = handler.parse_intent(query1)
    print(f"Query 1: \"{query1}\"")
    print(f"  Intent: {result1['intent']}")
    print(f"  Entities: {result1.get('entities', {})}")
    print()

    # Second query with context
    context = {
        'previous_intent': result1['intent'],
        'previous_entities': result1.get('entities', {})
    }

    query2 = "What about TSLA?"
    result2 = handler.parse_intent(query2, context=context)
    print(f"Query 2: \"{query2}\" (with context)")
    print(f"  Previous context: {context}")
    print(f"  Intent: {result2['intent']}")
    print(f"  Entities: {result2.get('entities', {})}")
    print()

def test_fallback():
    """Test fallback keyword matching"""
    print("\n" + "=" * 60)
    print("Testing Fallback Mechanism")
    print("=" * 60)
    print()

    handler = NaturalLanguageHandler()

    # Test fallback directly
    queries = [
        "portfolio",
        "positions",
        "opportunities",
        "help"
    ]

    for query in queries:
        result = handler.fallback_intent_detection(query)
        print(f"Query: \"{query}\"")
        print(f"  Fallback Intent: {result['intent']}")
        print(f"  Confidence: {result['confidence']:.2f}")
        print(f"  Model: {result['model_used']}")
        print()

if __name__ == "__main__":
    try:
        # Test basic intent detection
        passed, failed = test_nlp_queries()

        # Test context awareness
        test_context_awareness()

        # Test fallback
        test_fallback()

        print("\n✅ All tests completed!")

        if failed > 0:
            print(f"⚠️  Warning: {failed} test(s) failed")
            sys.exit(1)
        else:
            print("🎉 All tests passed!")
            sys.exit(0)

    except KeyboardInterrupt:
        print("\n\n⚠️  Tests interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error running tests: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
