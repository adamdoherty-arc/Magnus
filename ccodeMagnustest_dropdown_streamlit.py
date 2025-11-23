"""Test dropdown in real Streamlit environment"""
import sys
sys.path.insert(0, r'c:\code\Magnus')

import streamlit as st
from src.components.stock_dropdown import StockDropdown
from src.ai_options_agent.ai_options_db_manager import AIOptionsDBManager

st.set_page_config(page_title="Dropdown Test", layout="wide")

st.title("Stock Dropdown Test")

# Clear cache button
if st.button("🔄 Clear Cache"):
    st.cache_data.clear()
    st.rerun()


# Initialize components
db_manager = AIOptionsDBManager()
dropdown = StockDropdown(db_manager)

# Test 1: Check database
st.subheader("Test 1: Database Check")
stocks_df = dropdown._get_stock_list()
st.write(f"Records in database: {len(stocks_df)}")
if len(stocks_df) > 0:
    st.write("Sample stocks:")
    st.dataframe(stocks_df.head(10))
else:
    st.error("No stocks found in database!")


# Test 2: Dropdown
st.subheader("Test 2: Stock Dropdown")
selected = dropdown.render(
    label="Select Stock",
    key="test_dropdown",
    show_metadata=True
)

if selected:
    st.success(f"Selected: {selected}")
else:
    st.info("No stock selected")
