# Development Test Pages

This directory contains Streamlit test pages that are used during development but should not appear in production navigation.

## Test Pages

1. **test_components_page.py** - Component testing and UI prototyping
2. **test_kalshi_nfl_markets_page.py** - Kalshi NFL markets integration testing
3. **test_streamlit_comprehensive_page.py** - Comprehensive Streamlit functionality tests

## Running Test Pages

To run a test page during development:

```bash
# From the Magnus root directory
streamlit run dev_tests/test_components_page.py

# Or for any other test page
streamlit run dev_tests/test_[page_name].py
```

## Note

These pages are intentionally kept in a separate directory to:
- Keep them out of the production navigation sidebar
- Maintain them for development and debugging purposes
- Provide a clear separation between production and test code

Do not move these files back to the root directory as they will appear in the production navigation.
