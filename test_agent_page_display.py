"""Test if agent management page displays agents correctly"""
import sys
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Agent Management Page Display Test")
print("=" * 60)

# Test the exact flow that happens when the page loads
print("\n1. Importing agent_management_page...")
try:
    import agent_management_page
    print("[OK] Import successful")
except Exception as e:
    print(f"[FAIL] Import failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n2. Testing ensure_agents_initialized()...")
try:
    from src.ava.core.agent_initializer import ensure_agents_initialized, get_registry
    ensure_agents_initialized()
    print("[OK] Agents initialized")
except Exception as e:
    print(f"[FAIL] Initialization failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n3. Getting registry and agents...")
try:
    registry = get_registry()
    all_agents = registry.get_all_agents()
    print(f"[OK] Registry has {len(all_agents)} agents")
except Exception as e:
    print(f"[FAIL] Failed to get agents: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n4. Listing all agents:")
if len(all_agents) == 0:
    print("[ERROR] No agents found in registry!")
    print("\nDebugging info:")
    print(f"  - Registry object: {registry}")
    print(f"  - Registry type: {type(registry)}")
    print(f"  - Agent names: {registry.list_agent_names()}")
else:
    print(f"[OK] Found {len(all_agents)} agents:\n")
    for i, agent in enumerate(all_agents, 1):
        if agent:
            print(f"  {i:2d}. {agent.name:30s} - {agent.description[:60]}")
        else:
            print(f"  {i:2d}. [None/Invalid]")

print("\n5. Testing get_agent() method...")
try:
    if len(all_agents) > 0 and all_agents[0]:
        first_agent_name = all_agents[0].name
        retrieved = registry.get_agent(first_agent_name)
        if retrieved:
            print(f"[OK] Successfully retrieved agent: {first_agent_name}")
        else:
            print(f"[FAIL] get_agent() returned None for: {first_agent_name}")
except Exception as e:
    print(f"[FAIL] get_agent() error: {e}")

print("\n" + "=" * 60)
if len(all_agents) > 0:
    print(f"[SUCCESS] Page should display {len(all_agents)} agents")
else:
    print("[FAILURE] Page will show NO agents")
print("=" * 60)
