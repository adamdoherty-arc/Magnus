#!/usr/bin/env python3
"""Test positions page import after langchain fixes"""

import sys
sys.path.insert(0, 'c:/Code/WheelStrategy')

print("=" * 80)
print("Testing Positions Page Import After Langchain Fix")
print("=" * 80)

try:
    print("\n1. Importing positions_page_improved...")
    from positions_page_improved import show_positions_page
    print("   ✅ SUCCESS: positions_page_improved imported without errors")
    print(f"   ✅ show_positions_page function exists: {callable(show_positions_page)}")

    print("\n2. Importing recovery_strategies_tab...")
    from src.recovery_strategies_tab import display_recovery_strategies_tab
    print("   ✅ SUCCESS: recovery_strategies_tab imported without errors")

    print("\n3. Importing AIOptionsAdvisor...")
    from src.ai_options_advisor import AIOptionsAdvisor
    print("   ✅ SUCCESS: AIOptionsAdvisor imported without errors")
    print(f"   ✅ AIOptionsAdvisor class exists: {callable(AIOptionsAdvisor)}")

    print("\n" + "=" * 80)
    print("✅ ALL IMPORTS SUCCESSFUL - Positions page should work now!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}: {e}")
    import traceback
    print("\nFull traceback:")
    traceback.print_exc()
    print("\n" + "=" * 80)
    print("❌ IMPORT FAILED - There are still issues to fix")
    print("=" * 80)
