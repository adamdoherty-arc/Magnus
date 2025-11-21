# VERIFICATION CHECKLIST - Comprehensive Strategy Page Bug Fix

## Pre-Test Setup
- [ ] Navigate to `c:\Code\WheelStrategy`
- [ ] Run: `streamlit run dashboard.py`
- [ ] Click "Comprehensive Strategy Analysis" in sidebar

## Test 1: AAPL → HIMS Switch (Critical Bug Fix)
**This is the exact bug that was reported - MUST PASS**

### Steps:
1. [ ] Select "TradingView Watchlist" as data source
2. [ ] Select "AAPL" from dropdown
3. [ ] Verify AAPL data loads:
   - [ ] Current Price: ~$227.50 (or current AAPL price)
   - [ ] Sector: Technology
   - [ ] Strike Price: ~$215 (or similar AAPL strike)
4. [ ] Switch dropdown to "HIMS"
5. [ ] **CRITICAL CHECK** - Verify HIMS data loads:
   - [ ] Current Price: ~$45.60 (NOT $227!) ✅
   - [ ] Sector: Healthcare (NOT Technology!) ✅
   - [ ] Strike Price: ~$43 (NOT $215!) ✅

**Expected Result:** ALL fields should show HIMS data, NOT AAPL data

**Bug Behavior (if not fixed):** Would show AAPL's $227 price for HIMS

---

## Test 2: Multiple Symbol Switches
**Ensures no stale data across multiple changes**

### Steps:
1. [ ] Select "AAPL"
   - [ ] Verify AAPL data correct
2. [ ] Select "TSLA"
   - [ ] Verify TSLA data correct (NOT AAPL data)
3. [ ] Select "NVDA"
   - [ ] Verify NVDA data correct (NOT TSLA or AAPL data)
4. [ ] Select "AAPL" again
   - [ ] Verify AAPL data correct (fresh load)

**Expected Result:** Each symbol shows its own unique data

---

## Test 3: Manual Override Isolation
**Ensures manual edits don't leak between symbols**

### Steps:
1. [ ] Select "AAPL"
2. [ ] Enable "Manually Edit Auto-Filled Values"
3. [ ] Change "Current Price" to $999.99
4. [ ] Verify price shows $999.99
5. [ ] Switch to "HIMS"
6. [ ] **CHECK**: HIMS price should be ~$45.60 (NOT $999.99!)
7. [ ] Switch back to "AAPL"
8. [ ] **CHECK**: AAPL price should be ~$227 (reset, NOT $999.99)

**Expected Result:** Manual edits don't persist across symbol changes

---

## Test 4: Options Data Updates
**Ensures options chain data updates correctly**

### Steps:
1. [ ] Select "AAPL"
2. [ ] Note the strike prices shown (e.g., $215, $220, $225)
3. [ ] Switch to "HIMS"
4. [ ] **CHECK**: Strike prices update to HIMS range (e.g., $40, $43, $45)
5. [ ] **CHECK**: Delta values update to HIMS deltas
6. [ ] **CHECK**: Premium values update to HIMS premiums

**Expected Result:** All options data updates to match selected symbol

---

## Test 5: Sector Dropdown
**Ensures sector selector updates correctly**

### Steps:
1. [ ] Select "AAPL" (Technology sector)
2. [ ] Verify "Sector" dropdown shows "Technology"
3. [ ] Switch to "HIMS" (Healthcare sector)
4. [ ] **CHECK**: "Sector" dropdown shows "Healthcare" (NOT Technology!)
5. [ ] Switch to "XOM" (Energy sector, if available)
6. [ ] **CHECK**: "Sector" dropdown shows "Energy"

**Expected Result:** Sector dropdown reflects the selected symbol's sector

---

## Test 6: 52-Week High/Low
**Ensures price range data updates**

### Steps:
1. [ ] Select "AAPL"
2. [ ] Note 52-week high/low (e.g., $198 - $237)
3. [ ] Switch to "HIMS"
4. [ ] **CHECK**: 52-week high/low updates (e.g., $38 - $52)
5. [ ] Values should be HIMS-specific, NOT AAPL values

**Expected Result:** 52-week range updates to match selected symbol

---

## Test 7: Database Stocks Source
**Ensures fix works with all data sources**

### Steps:
1. [ ] Change data source to "Database Stocks"
2. [ ] Select any stock from dropdown
3. [ ] Verify data loads correctly
4. [ ] Select different stock
5. [ ] Verify data updates correctly (no stale data)

**Expected Result:** Fix works regardless of data source

---

## Test 8: Manual Input Source
**Ensures manual input still works**

### Steps:
1. [ ] Change data source to "Manual Input"
2. [ ] Type "MSFT" and press Enter
3. [ ] Verify MSFT data loads
4. [ ] Type "GOOGL" and press Enter
5. [ ] Verify GOOGL data loads (NOT MSFT data)

**Expected Result:** Manual input updates correctly

---

## PASS/FAIL Criteria

### CRITICAL TESTS (Must Pass)
- [ ] **Test 1**: AAPL → HIMS shows HIMS data (NOT AAPL)
- [ ] **Test 2**: Multiple switches show correct data
- [ ] **Test 4**: Options data updates per symbol

### IMPORTANT TESTS (Should Pass)
- [ ] **Test 3**: Manual edits don't leak
- [ ] **Test 5**: Sector updates correctly
- [ ] **Test 6**: Price ranges update

### OPTIONAL TESTS (Nice to Have)
- [ ] **Test 7**: Database source works
- [ ] **Test 8**: Manual input works

---

## If Tests Fail

### Common Issues:
1. **Stale data showing**: Refresh browser (Ctrl+F5)
2. **Widget not updating**: Clear Streamlit cache (hamburger menu → Clear cache)
3. **Old code running**: Restart Streamlit server

### Troubleshooting Steps:
```bash
# Stop dashboard (Ctrl+C in terminal)
# Clear Python cache
cd c:\Code\WheelStrategy
del /S /Q __pycache__
del /S /Q *.pyc

# Restart dashboard
streamlit run dashboard.py
```

---

## Success Criteria

✅ **ALL CRITICAL TESTS PASS** = Bug is fixed
⚠️ **1-2 TESTS FAIL** = Needs debugging
❌ **3+ TESTS FAIL** = Fix incomplete

---

## Final Verification

- [ ] Bug Fix Complete: All critical tests pass
- [ ] No Regressions: Existing features still work
- [ ] Performance: No noticeable slowdown
- [ ] User Experience: Data updates feel instant

**Tested By:** _________________
**Date:** _________________
**Result:** PASS / FAIL
**Notes:** _______________________________________
