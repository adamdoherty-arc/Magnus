"""
Test AVA's Enhanced Project Knowledge
=====================================

Verifies that AVA can answer questions about Magnus project.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from src.ava.enhanced_project_handler import EnhancedProjectHandler

def test_project_knowledge():
    """Test AVA's project knowledge capabilities"""
    print("=" * 80)
    print("AVA PROJECT KNOWLEDGE TEST")
    print("=" * 80)
    print()

    handler = EnhancedProjectHandler()

    test_questions = [
        {
            'question': "What features does Magnus have?",
            'expected_keywords': ['dashboard', 'positions', 'opportunities', 'AI']
        },
        {
            'question': "How do I find CSP opportunities?",
            'expected_keywords': ['csp_opportunities', 'filter', 'IV', 'delta']
        },
        {
            'question': "Where is the database schema?",
            'expected_keywords': ['schema', 'development_tasks', 'xtrades']
        },
        {
            'question': "What integrations does Magnus have?",
            'expected_keywords': ['Robinhood', 'TradingView', 'XTrades', 'Kalshi']
        },
        {
            'question': "How does the AI agent work?",
            'expected_keywords': ['ai_options_agent', 'recommendations', 'analysis']
        }
    ]

    results = []

    for i, test in enumerate(test_questions, 1):
        print(f"\n[Test {i}] {test['question']}")
        print("-" * 80)

        result = handler.answer_project_question(test['question'])

        if result['success']:
            answer = result['answer'].lower()
            keywords_found = sum(1 for kw in test['expected_keywords'] if kw.lower() in answer)
            coverage = (keywords_found / len(test['expected_keywords'])) * 100

            print(f"[OK] Answer generated")
            print(f"[Coverage] {keywords_found}/{len(test['expected_keywords'])} expected keywords found ({coverage:.0f}%)")
            print(f"\n{result['answer'][:300]}...")

            results.append({
                'question': test['question'],
                'success': True,
                'coverage': coverage,
                'model': result['model_used']
            })
        else:
            print(f"[ERROR] {result.get('error', 'Unknown error')}")
            print(f"[Fallback] {result['answer'][:200]}...")

            results.append({
                'question': test['question'],
                'success': False,
                'coverage': 0,
                'model': 'fallback'
            })

    # Summary
    print("\n" + "=" * 80)
    print("TEST SUMMARY")
    print("=" * 80)

    successful = sum(1 for r in results if r['success'])
    avg_coverage = sum(r['coverage'] for r in results) / len(results) if results else 0

    print(f"\nTests Run: {len(results)}")
    print(f"Successful: {successful}/{len(results)}")
    print(f"Average Keyword Coverage: {avg_coverage:.1f}%")

    print("\n[RESULT]", end=" ")
    if successful == len(results) and avg_coverage >= 50:
        print("PASS - AVA has good project knowledge")
    elif successful >= len(results) * 0.7:
        print("PARTIAL - AVA has basic project knowledge")
    else:
        print("NEEDS IMPROVEMENT - More indexing required")

    print("\n" + "=" * 80)


def test_feature_lookup():
    """Test specific feature lookups"""
    print("\n" + "=" * 80)
    print("FEATURE LOOKUP TEST")
    print("=" * 80)
    print()

    handler = EnhancedProjectHandler()

    features = ["positions page", "CSP opportunities", "premium scanner"]

    for feature in features:
        print(f"\n[Lookup] {feature}")
        print("-" * 80)

        result = handler.get_feature_info(feature)
        if result['success']:
            print(f"[OK] {result['answer'][:250]}...")
        else:
            print(f"[Fallback] {result['answer'][:150]}...")

    print("\n" + "=" * 80)


if __name__ == "__main__":
    test_project_knowledge()
    test_feature_lookup()
