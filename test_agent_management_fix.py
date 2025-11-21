"""
Test Agent Management Page - Verify encoding fix
"""
import sys

# Test encoding setup
if sys.platform == 'win32':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
        sys.stderr.reconfigure(encoding='utf-8')
    except:
        pass

print("=" * 80)
print("🔍 TESTING AGENT MANAGEMENT PAGE ENCODING")
print("=" * 80)

try:
    # Test emoji printing
    print("\n✅ Testing emoji output:")
    print("  🔍 Magnifying glass")
    print("  🤖 Robot")
    print("  ✅ Check mark")
    print("  ❌ Cross mark")
    print("  ⚠️ Warning")

    print("\n✅ Emoji printing works!")

    # Test agent initialization
    print("\n🔍 Testing agent initialization:")
    from src.ava.core.agent_initializer import ensure_agents_initialized, get_registry

    ensure_agents_initialized()
    registry = get_registry()

    agent_count = len(registry.get_all_agents())
    print(f"  ✅ Found {agent_count} agents in registry")

    if agent_count > 0:
        print(f"\n✅ Sample agents:")
        for i, agent in enumerate(registry.get_all_agents()[:5]):
            print(f"  {i+1}. {agent.name}")

    print("\n" + "=" * 80)
    print("✅ ALL TESTS PASSED - Agent Management page should work!")
    print("=" * 80)

except Exception as e:
    print(f"\n❌ ERROR: {e}")
    import traceback
    traceback.print_exc()
    print("\n" + "=" * 80)
    print("❌ TEST FAILED")
    print("=" * 80)
