# CSS Cache Busting Guide

## Problem
CSS changes weren't showing immediately in the browser because:
1. Browser caches CSS
2. Streamlit caches content
3. The cache buster wasn't changing

## Solution Implemented

### 1. Dynamic Cache Buster
Changed from static counter to timestamp-based cache buster:

```python
import time
cache_buster = st.session_state.get('css_cache_buster', int(time.time()))
```

This generates a unique cache buster on every page load, forcing CSS refresh.

### 2. Force Refresh Button
Added a "🔄 Force Refresh" button in the header that:
- Clears Streamlit's cache
- Increments the cache buster
- Reruns the page

```python
if st.button("🔄 Force Refresh", key="force_refresh_ui"):
    st.cache_data.clear()
    st.session_state.css_cache_buster = cache_buster + 1
    st.rerun()
```

## How to Ensure CSS Changes Show Immediately

### Method 1: Use Force Refresh Button (Recommended)
1. Make your CSS changes in `game_cards_visual_page.py`
2. Save the file
3. Click the **"🔄 Force Refresh"** button in the top-left of the UI
4. CSS changes will be applied immediately

### Method 2: Browser Hard Refresh
1. Make your CSS changes
2. Save the file
3. In your browser, press:
   - **Windows/Linux**: `Ctrl + Shift + R` or `Ctrl + F5`
   - **Mac**: `Cmd + Shift + R`
4. Page will reload with fresh CSS

### Method 3: Clear Streamlit Cache (Terminal)
1. In the Streamlit terminal, press `C` to clear cache
2. Browser will reload automatically with fresh CSS

### Method 4: Restart Streamlit (Last Resort)
1. Stop Streamlit (Ctrl+C in terminal)
2. Restart with `streamlit run dashboard.py`
3. All caches will be cleared

## Best Practices

### 1. Always Use !important for Overrides
When overriding Streamlit's default styles, use `!important`:

```css
.game-card {
    border-top: none !important;
}
```

### 2. Use Specific Selectors
Be specific to avoid conflicts:

```css
/* Good */
.game-card > div:first-child {
    border-top: none !important;
}

/* Bad */
div {
    border-top: none !important;
}
```

### 3. Escape Curly Braces in f-strings
When CSS is in an f-string, double all curly braces:

```python
st.markdown(f"""
    <style>
    @keyframes pulse {{
        0%, 100% {{ opacity: 1; }}
        50% {{ opacity: 0.4; }}
    }}
    </style>
""", unsafe_allow_html=True)
```

### 4. Test in Multiple Browsers
Different browsers cache differently:
- Chrome: Aggressive caching
- Firefox: Moderate caching
- Safari: Aggressive caching

## Troubleshooting

### CSS Still Not Updating?

1. **Check Browser Console (F12)**
   - Look for CSS syntax errors
   - Check if styles are being overridden

2. **Verify CSS is in the Right Place**
   - Main CSS: Line 115-395 in `game_cards_visual_page.py`
   - Per-card CSS: Line 1078-1123 in same file

3. **Check Specificity**
   - More specific selectors win
   - `!important` overrides everything

4. **Clear All Caches**
   ```bash
   # Terminal
   rm -rf ~/.streamlit/cache  # Linux/Mac
   rmdir /s %USERPROFILE%\.streamlit\cache  # Windows
   ```

## Fixed Issues

### ✅ Duplicate Key Error
**Problem**: `StreamlitDuplicateElementKey: key='unwatch_401772928'`

**Solution**: Made keys unique by adding index:
```python
unwatch_key = f"unwatch_{game_id}_{idx}"
```

### ✅ CSS Not Updating
**Problem**: CSS changes not showing in browser

**Solution**: Dynamic timestamp-based cache buster:
```python
cache_buster = st.session_state.get('css_cache_buster', int(time.time()))
```

### ✅ Gray Border at Top of Cards
**Problem**: Gray border showing at top of each game card

**Solution**: Added comprehensive CSS rules to remove top borders:
```css
.game-card > *:first-child,
.game-card > div:first-child,
.game-card > div:first-child > * {
    border-top: none !important;
    border-top-color: transparent !important;
    border-top-width: 0 !important;
}
```

## Summary

- **Quick CSS updates**: Use "🔄 Force Refresh" button
- **Cache buster**: Now uses timestamp for automatic cache busting
- **Duplicate keys**: Fixed by adding unique indices
- **Top border**: Removed with comprehensive CSS rules

All CSS changes should now appear immediately when using the Force Refresh button!

