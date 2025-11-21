# Critical Bugs Found - Game Cards Page

## Date: November 16, 2025
## Status: IDENTIFIED - FIXING NOW

---

## Bug #1: AI Confidence Showing 5000% Instead of 50%

**Root Cause**: Double multiplication
- AI Agent returns confidence as 0-100 (line 368 in `advanced_betting_ai_agent.py`)
- Display code multiplies by 100 AGAIN (line 671 in `game_cards_visual_page.py`)
- Result: 50 × 100 = 5000%

**Fix Required**:
```python
# BEFORE (WRONG):
st.metric("Confidence", f"{confidence*100:.1f}%")

# AFTER (CORRECT):
st.metric("Confidence", f"{confidence:.1f}%")
```

---

## Bug #2: Win Probability May Have Same Issue

**Need to Check**: Is win_probability 0-1 or 0-100?
- Line 669: `f"{win_prob*100:.1f}%"`
- If AI returns 50.0 (not 0.5), this would show 5000%

**Investigation Needed**: Check AI agent return format

---

## Bug #3: Kalshi Odds Not Displaying

**Root Cause**: Data not being fetched or enriched properly
- Line 683-692 has the display code
- Condition: `if kalshi_odds:` may be False
- ESPN games may not have `kalshi_odds` field populated

**Possible Issues**:
1. `enrich_games_with_kalshi_odds()` not working
2. Kalshi data not synced
3. No Kalshi markets for these games

**Debug Steps**:
1. Check if ESPN games have kalshi_odds field
2. Verify enrichment function is called
3. Add fallback message: "No Kalshi odds available"

---

## Bug #4: Green Hover Has No Explanation

**Root Cause**: No legend or tooltip
- CSS hover effect changes border to green (#4CAF50)
- No user indication of what this means

**Fix Required**:
- Add legend above cards
- Or add tooltip on hover
- Or remove confusing hover effect

**Recommended**:
```
Legend: 🟢 Hover = Highlight | 📍 Watch | 📱 Telegram
```

---

## Bug #5: Watch Tracking Unclear

**Root Cause**: Telegram toggle hidden by default
- Only appears AFTER checking "Watch This Game"
- Users don't know Telegram notifications exist

**Fix Required**:
- Show Telegram option immediately
- Or add help text: "Click to enable Telegram updates"
- Or combine into one control

---

## Bug #6: Expected Value Always +0.00%

**Root Cause**: AI calculation returning 0
- Line 672: `st.metric("Expected Value", f"{ev:+.2f}%")`
- AI agent returning 0 for all games

**Possible Causes**:
1. market_odds = 0.5 (default) for all games
2. No Kalshi odds = no edge = 0 EV
3. Calculation error in `_calculate_expected_value()`

---

## Bug #7: Pagination Count Wrong

**Issue**: "Showing 1-12 of 15 games"
- If there are 15 games total
- Page 1 shows 1-12
- Page 2 would show 13-15 (only 3 games)

**Not a bug, but UX could be improved**

---

## Bug #8: "Best Money-Making" Sort Doesn't Work

**Root Cause**: AI predictions disabled for performance
- Line 544: `sort_by = filter_settings.get('sort_by', '💰 Best Money-Making')`
- Line 554-558: Simplified sorting - just shows live first

**Issue**: Users select "Best Money-Making" but get "Live First" instead

**Fix Required**: Either
1. Remove AI-based sort options
2. Re-enable AI sorting with async loading
3. Add note: "(Unavailable - showing live games first)"

---

## Summary of Fixes Needed:

1. ✅ **Remove `*100` from confidence display**
2. ✅ **Check win_probability format**
3. ✅ **Debug Kalshi odds enrichment**
4. ✅ **Add legend for green hover**
5. ✅ **Always show Telegram toggle**
6. ✅ **Fix Expected Value calculation**
7. ✅ **Update sort options or add disclaimer**
8. ✅ **Add fallback for missing Kalshi data**

---

## Testing Checklist After Fixes:

- [ ] Confidence shows 50.0% not 5000.0%
- [ ] Win Probability shows 50.0% not 5000.0%
- [ ] Expected Value shows meaningful numbers
- [ ] Kalshi odds visible (or "Not available")
- [ ] Green hover has explanation
- [ ] Telegram toggle always visible
- [ ] Sort options work or are disabled
- [ ] All AI metrics make sense
