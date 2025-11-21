"""Diagnostic test to check agent management page availability in dashboard context"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Dashboard Agent Management Diagnostic")
print("=" * 60)

# Simulate the exact import sequence from dashboard.py
print("\n1. Testing import sequence (as in dashboard.py)...")

# Import Agent Management Page (exactly as in dashboard.py lines 40-44)
try:
    import agent_management_page
    AGENT_MANAGEMENT_AVAILABLE = True
    print("[OK] agent_management_page imported successfully")
except ImportError as e:
    AGENT_MANAGEMENT_AVAILABLE = False
    print(f"[FAIL] Failed to import agent_management_page: {e}")
    import traceback
    traceback.print_exc()

print(f"\nAGENT_MANAGEMENT_AVAILABLE = {AGENT_MANAGEMENT_AVAILABLE}")

if AGENT_MANAGEMENT_AVAILABLE:
    print("\n2. Checking main() function...")
    if hasattr(agent_management_page, 'main'):
        print("[OK] main() function exists and is callable")

        print("\n3. Checking imports inside agent_management_page...")
        try:
            # These are imported in agent_management_page.py
            from src.ava.core.agent_registry import AgentRegistry
            from src.ava.core.agent_learning import AgentLearningSystem
            from src.ava.core.agent_base import BaseAgent
            from src.ava.core.agent_initializer import ensure_agents_initialized, get_registry
            print("[OK] All required imports available")
        except Exception as e:
            print(f"[FAIL] Import error: {e}")
            import traceback
            traceback.print_exc()
    else:
        print("[FAIL] main() function not found")
else:
    print("\n[FAIL] Cannot proceed - agent_management_page not available")

print("\n" + "=" * 60)
print("DIAGNOSTIC COMPLETE")
print("=" * 60)

if AGENT_MANAGEMENT_AVAILABLE:
    print("\n[SUCCESS] Agent Management Page should be available in dashboard")
    print("If it's not showing in the UI, check:")
    print("1. Is the button visible in the sidebar under 'AVA Management'?")
    print("2. What happens when you click the button?")
    print("3. Are there any errors in the browser console or Streamlit terminal?")
else:
    print("\n[ERROR] Agent Management Page is NOT available")
    print("This explains why it's not showing in the UI")
