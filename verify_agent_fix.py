"""Quick verification that agents will display correctly"""
import streamlit as st

st.set_page_config(page_title="Agent Fix Verification", layout="wide")

st.title("🔍 Agent Management Fix Verification")

# Import the fixed page
try:
    from agent_management_page import get_initialized_registry
    st.success("✅ Successfully imported get_initialized_registry()")
except ImportError as e:
    st.error(f"❌ Import failed: {e}")
    st.stop()

# Get the cached registry
st.write("## Testing Cached Registry")
try:
    registry = get_initialized_registry()
    agents = registry.get_all_agents()
    agent_count = len(agents)

    if agent_count > 0:
        st.success(f"✅ SUCCESS: {agent_count} agents loaded and cached!")

        st.write("### All Agents:")
        for i, agent in enumerate(agents, 1):
            if agent:
                st.write(f"{i}. **{agent.name}** - {agent.description[:80]}")
    else:
        st.error("❌ FAILED: No agents in registry")

except Exception as e:
    st.error(f"❌ Error: {e}")
    import traceback
    with st.expander("Error Details"):
        st.code(traceback.format_exc())

st.write("---")
st.write("**Test the actual page:** Click 'Agent Management' in the dashboard sidebar")
