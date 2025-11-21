"""Test agent management page import and initialization"""
import sys
import traceback
import io
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

print("=" * 60)
print("Testing Agent Management Page Import")
print("=" * 60)

# Test 1: Import the module
print("\n1. Testing module import...")
try:
    import agent_management_page
    print("[OK] agent_management_page imported successfully")
    AGENT_MANAGEMENT_AVAILABLE = True
except ImportError as e:
    print(f"[FAIL] Failed to import agent_management_page: {e}")
    traceback.print_exc()
    AGENT_MANAGEMENT_AVAILABLE = False

# Test 2: Check if main function exists
print("\n2. Checking for main() function...")
if AGENT_MANAGEMENT_AVAILABLE:
    if hasattr(agent_management_page, 'main'):
        print("[OK] main() function exists")
    else:
        print("[FAIL] main() function not found")

# Test 3: Import dependencies
print("\n3. Testing dependencies...")
try:
    from src.ava.core.agent_registry import AgentRegistry
    print("[OK] AgentRegistry imported")
except Exception as e:
    print(f"[FAIL] AgentRegistry import failed: {e}")

try:
    from src.ava.core.agent_learning import AgentLearningSystem
    print("[OK] AgentLearningSystem imported")
except Exception as e:
    print(f"[FAIL] AgentLearningSystem import failed: {e}")

try:
    from src.ava.core.agent_base import BaseAgent
    print("[OK] BaseAgent imported")
except Exception as e:
    print(f"[FAIL] BaseAgent import failed: {e}")

try:
    from src.ava.core.agent_initializer import ensure_agents_initialized, get_registry
    print("[OK] agent_initializer imported")
except Exception as e:
    print(f"[FAIL] agent_initializer import failed: {e}")

# Test 4: Try to initialize agents
print("\n4. Testing agent initialization...")
try:
    from src.ava.core.agent_initializer import ensure_agents_initialized, get_registry
    ensure_agents_initialized()
    registry = get_registry()
    agents = registry.get_all_agents()
    print(f"[OK] Agents initialized: {len(agents)} agents found")

    if len(agents) > 0:
        print(f"\nFirst 5 agents:")
        for agent in agents[:5]:
            if agent:
                print(f"  - {agent.name}: {agent.description[:50]}...")
except Exception as e:
    print(f"[FAIL] Agent initialization failed: {e}")
    traceback.print_exc()

print("\n" + "=" * 60)
print(f"AGENT_MANAGEMENT_AVAILABLE: {AGENT_MANAGEMENT_AVAILABLE}")
print("=" * 60)
