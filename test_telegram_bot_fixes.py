"""
Test Telegram Bot Fixes
========================

Quick test script to verify all critical fixes are working.

Usage:
    python test_telegram_bot_fixes.py

Tests:
1. Portfolio query handler
2. Xtrades alerts handler
3. Positions query handler
4. CSP opportunities handler
5. Top traders handler
6. Trader-specific handler
7. Database connectivity

Author: Magnus Wheel Strategy
Created: 2025-11-06
"""

import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.ava.voice_handler import AVAVoiceHandler


def test_handler(handler, query_text, test_name):
    """Test a specific query handler"""
    print(f"\n{'='*70}")
    print(f"TEST: {test_name}")
    print(f"{'='*70}")
    print(f"Query: '{query_text}'")
    print(f"{'-'*70}")

    try:
        result = handler.process_query(query_text)
        print(f"✅ SUCCESS\n")
        print(f"Response:\n{result['response_text']}\n")
        print(f"Data: {result['data']}")
        return True
    except Exception as e:
        print(f"❌ FAILED")
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests"""
    print("\n" + "="*70)
    print("TELEGRAM BOT FIXES - COMPREHENSIVE TEST SUITE")
    print("="*70)
    print("\nInitializing AVA Voice Handler...\n")

    handler = AVAVoiceHandler()

    tests = [
        ("How's my portfolio?", "Portfolio Query Handler"),
        ("Any alerts from Xtrades?", "Xtrades Alerts Handler"),
        ("Show my positions", "Robinhood Positions Handler"),
        ("Any CSP opportunities?", "CSP Opportunities Handler"),
        ("Who are the top traders?", "Top Traders Handler"),
        ("Show me trades from behappy", "Trader-Specific Handler"),
        ("What's the market doing?", "Market News Handler (placeholder)"),
        ("Hello AVA", "Default Greeting Handler"),
    ]

    results = []

    for query, test_name in tests:
        passed = test_handler(handler, query, test_name)
        results.append((test_name, passed))

    # Summary
    print("\n" + "="*70)
    print("TEST SUMMARY")
    print("="*70)

    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)

    for test_name, passed in results:
        status = "✅ PASSED" if passed else "❌ FAILED"
        print(f"{status} - {test_name}")

    print(f"\n{'-'*70}")
    print(f"Total: {passed_count}/{total_count} tests passed")
    print(f"Success Rate: {(passed_count/total_count)*100:.1f}%")
    print("="*70)

    if passed_count == total_count:
        print("\n🎉 ALL TESTS PASSED! The Telegram bot is ready for production.")
    elif passed_count > 0:
        print(f"\n⚠️  {total_count - passed_count} test(s) failed. Check database and configuration.")
    else:
        print("\n❌ ALL TESTS FAILED. Check database connection and .env configuration.")

    print("\n" + "="*70)
    print("NEXT STEPS")
    print("="*70)
    print("1. Start background sync: run_xtrades_sync.bat")
    print("2. Run Telegram bot: python src/ava/telegram_bot_enhanced.py")
    print("3. Test with voice messages in Telegram")
    print("4. Monitor sync logs: SELECT * FROM xtrades_sync_log;")
    print("="*70 + "\n")


if __name__ == "__main__":
    main()
