# AI Prediction Duplicate Bug - Debug in Progress

**Date**: 2025-11-18
**Status**: 🔍 **DEBUGGING**

---

## 🐛 Issue Reported

User provided screenshot showing **all NCAA games displaying identical predictions**:

| Game | Consensus | Breakdown |
|------|-----------|-----------|
| Akron @ Bowling Green | 54% | 57% sports, 54% neural, 52% XGBoost |
| Massachusetts @ Ohio | 54% | 57%, 54%, 52% |
| Ohio @ Western Michigan | 54% | 57%, 54%, 52% |

**User Quote**: *"All the NCAA games have the same AI score which is impossible so somethign is wrong"*

This is clearly a bug - three different matchups cannot have identical predictions.

---

## 🔍 Investigation Approach

### Hypothesis
The caching system (either Streamlit's `@st.cache_data` or the predictor's internal cache) may be returning the same cached prediction for different games due to:
1. **Cache key collision** - Different games generating the same cache key
2. **Team name normalization issue** - Team names being modified causing wrong matches
3. **Predictor internal cache bug** - Cache not properly keyed by team names

### Cache Flow

```
User loads NCAA game card
   ↓
get_sports_prediction_cached(game_id, sport_filter, home_team, away_team, date)
   ↓ (Streamlit cache with these 5 parameters as key)
predictor.predict_winner(home_team, away_team, game_date)
   ↓
Predictor creates cache key: f"{sport_name}:{home_team}:{away_team}:{date}"
   ↓
Predictor checks internal cache
   ↓ (If hit, returns cached prediction)
Return prediction
```

---

## 🛠️ Debug Logging Added

### 1. `game_cards_visual_page.py` (Lines 921-965)

**Added logs in `get_sports_prediction_cached()`**:

```python
# BEFORE calling predictor
logger.info(f"🔍 get_sports_prediction_cached called: game_id={game_id}, {away_team} @ {home_team}, date={game_date_str}")

# AFTER getting prediction
if prediction:
    winner = prediction.get('winner', 'unknown')
    prob = prediction.get('probability', 0)
    logger.info(f"✅ Prediction for {away_team} @ {home_team}: {winner} wins with {prob:.1%}")
else:
    logger.warning(f"❌ No prediction returned for {away_team} @ {home_team}")
```

### 2. `src/prediction_agents/base_predictor.py` (Lines 196-201)

**Added logs in `get_cached_prediction()`**:

```python
if age < 3600:  # Cache is fresh
    winner = cached['prediction'].get('winner', 'unknown')
    prob = cached['prediction'].get('probability', 0)
    self.logger.info(f"💾 CACHE HIT: {cache_key} → {winner} ({prob:.1%})")
    return cached['prediction']
else:
    self.logger.info(f"⏰ CACHE EXPIRED: {cache_key} (age: {age:.0f}s)")
```

### 3. `src/prediction_agents/base_predictor.py` (Lines 213-215)

**Added logs in `cache_prediction()`**:

```python
winner = prediction.get('winner', 'unknown')
prob = prediction.get('probability', 0)
self.logger.info(f"💽 CACHING NEW: {cache_key} → {winner} ({prob:.1%})")
```

---

## 📊 What the Logs Will Show

When you load the NCAA games page, logs will show:

### Normal Behavior (Expected):
```
🔍 get_sports_prediction_cached called: game_id=123, Akron @ Bowling Green, date=2025-11-18
💽 CACHING NEW: NCAA Football:Bowling Green:Akron:2025-11-18 → Bowling Green (57.3%)
✅ Prediction for Akron @ Bowling Green: Bowling Green wins with 57.3%

🔍 get_sports_prediction_cached called: game_id=124, Massachusetts @ Ohio, date=2025-11-18
💽 CACHING NEW: NCAA Football:Ohio:Massachusetts:2025-11-18 → Ohio (61.2%)
✅ Prediction for Massachusetts @ Ohio: Ohio wins with 61.2%

🔍 get_sports_prediction_cached called: game_id=125, Ohio @ Western Michigan, date=2025-11-18
💽 CACHING NEW: NCAA Football:Western Michigan:Ohio:2025-11-18 → Western Michigan (52.8%)
✅ Prediction for Ohio @ Western Michigan: Western Michigan wins with 52.8%
```

### Bug Behavior (What might be happening):
```
🔍 get_sports_prediction_cached called: game_id=123, Akron @ Bowling Green, date=2025-11-18
💽 CACHING NEW: NCAA Football:Bowling Green:Akron:2025-11-18 → Bowling Green (54.0%)
✅ Prediction for Akron @ Bowling Green: Bowling Green wins with 54.0%

🔍 get_sports_prediction_cached called: game_id=124, Massachusetts @ Ohio, date=2025-11-18
💾 CACHE HIT: NCAA Football:Bowling Green:Akron:2025-11-18 → Bowling Green (54.0%)  ⚠️ WRONG!
✅ Prediction for Massachusetts @ Ohio: Bowling Green wins with 54.0%  ⚠️ WRONG TEAM!

🔍 get_sports_prediction_cached called: game_id=125, Ohio @ Western Michigan, date=2025-11-18
💾 CACHE HIT: NCAA Football:Bowling Green:Akron:2025-11-18 → Bowling Green (54.0%)  ⚠️ WRONG!
✅ Prediction for Ohio @ Western Michigan: Bowling Green wins with 54.0%  ⚠️ WRONG TEAM!
```

If we see cache hits for different games, that's the smoking gun showing the cache key collision.

---

## 🧪 Next Steps

### To Continue Debugging:

1. **Refresh browser** and navigate to the **Game Cards** page
2. Select **NCAA** tab
3. **Check browser console** or Streamlit logs for debug output
4. Look for these patterns:
   - ✅ All games showing **different cache keys** = Good (cache working correctly)
   - ❌ Multiple games showing **same cache key** = Bug found (cache collision)
   - ❌ Predictions showing **wrong team names** = Team normalization issue

### If Cache Keys Are Correct:

The issue might be in Streamlit's `@st.cache_data` decorator. We may need to:
- Disable Streamlit caching temporarily
- Add team names explicitly to cache key parameters
- Check if `game_id` is `None` for some games

### If Team Names Are Being Modified:

Check for team name normalization functions that might be:
- Converting "Ohio" → "Ohio State" or similar
- Removing/adding prefixes
- Aliasing team names

---

## 📝 Files Modified

| File | Lines | Change |
|------|-------|--------|
| `game_cards_visual_page.py` | 921-965 | Added debug logs to `get_sports_prediction_cached()` |
| `src/prediction_agents/base_predictor.py` | 196-201 | Added cache hit/expire logs to `get_cached_prediction()` |
| `src/prediction_agents/base_predictor.py` | 213-215 | Added caching logs to `cache_prediction()` |

---

## 🎯 Current Status

**Dashboard URL**: http://localhost:8505

**Action Required**:
1. Refresh browser and navigate to NCAA games
2. Open browser console (F12) or check Streamlit logs
3. Look for prediction logs with 🔍 💾 💽 ✅ emojis
4. Report back what you see in the logs

The debug logs will show exactly what's happening:
- Which games are being predicted
- What cache keys are being generated
- Whether predictions are coming from cache or being calculated fresh
- If any cache collisions are occurring

---

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
