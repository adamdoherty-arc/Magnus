"""Test Agent Management in Streamlit context"""
import streamlit as st

st.set_page_config(page_title="Agent Management Test", layout="wide")

st.title("Agent Management Page Test")

# Test the import exactly as in dashboard.py
try:
    import agent_management_page
    AGENT_MANAGEMENT_AVAILABLE = True
    st.success(f"agent_management_page imported successfully")
except ImportError as e:
    AGENT_MANAGEMENT_AVAILABLE = False
    st.error(f"Failed to import agent_management_page: {e}")

st.write(f"**AGENT_MANAGEMENT_AVAILABLE:** {AGENT_MANAGEMENT_AVAILABLE}")

if AGENT_MANAGEMENT_AVAILABLE:
    st.write("**Testing main() function:**")

    if st.button("Run Agent Management Page"):
        try:
            # This is what dashboard.py does
            from agent_management_page import main
            main()
        except Exception as e:
            st.error(f"Error running main(): {e}")
            import traceback
            st.code(traceback.format_exc())
else:
    st.error("Agent Management page not available")
