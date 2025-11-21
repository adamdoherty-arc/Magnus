# NCAA Kalshi Integration - Quick Reference

**Last Updated**: 2025-11-18
**Status**: 🟡 Partially Fixed (50% error rate in NCAA markets)

---

## Critical Findings Summary

### Database Analysis Results

- **NCAA Football Game Markets**: 30 markets found (Kalshi DOES offer NCAA football games)
- **Parsing Error Rate**: **50.0%** (15 out of 30 markets have incorrect team names)
- **Team Matching Success**: **20%** (2 out of 10 test games matched, both with wrong team names)

### Confirmed Issues

1. **Multi-Word Team Parsing**: Still broken in NCAA markets
   - "Bowling Green" → parsed as "Bowling"
   - "Western Michigan" → parsed as "Michigan"
   - "Northern Illinois" → parsed as "Northern"
   - "San Diego St." → parsed as "San"
   - "Boise St." → parsed as "St."

2. **Database Corruption**: Existing NCAA markets have incorrect team names stored

3. **Matcher Coverage**: Only 14.2% of FBS teams have predefined variations

---

## Problem Examples from Live Data

### Example 1: Bowling Green Game
```
ESPN: Akron @ Bowling Green
Kalshi Market: "Akron at Bowling Green Winner?"
Parsed in DB: Akron @ Bowling ❌ WRONG
Impact: Cannot match odds to correct team
```

### Example 2: Western Michigan Game
```
ESPN: Western Michigan @ Northern Illinois
Kalshi Market: "Western Michigan at Northern Illinois Winner?"
Parsed in DB: Michigan @ Northern ❌ WRONG
Impact: Would match to Michigan instead of Western Michigan
```

### Example 3: State School Collision
```
Kalshi Market: "Boise St. at San Diego St. Winner?"
Parsed in DB: St. @ San ❌ CATASTROPHIC
Impact: Both teams are just fragments, cannot match at all
```

---

## Multi-Word NCAA Teams Affected

### High Priority (State Schools) - 22 Teams

| Team Name | Common Parsing Error | Impact |
|-----------|---------------------|--------|
| Ohio State | "State" | 🔴 Collision with all State schools |
| Michigan State | "State" or "Michigan" | 🔴 Matches wrong Michigan team |
| Penn State | "State" | 🔴 Collision |
| Florida State | "State" | 🔴 Collision |
| Boise State | "St." | 🔴 Collision |
| San Jose State | "San" or "State" | 🔴 Double collision |
| San Diego State | "San" or "State" | 🔴 Double collision |
| Mississippi State | "State" | 🔴 Collision |
| Kansas State | "State" | 🔴 Collision |
| Oklahoma State | "State" | 🔴 Collision |
| Arizona State | "State" | 🔴 Collision |
| Iowa State | "State" | 🔴 Collision |
| Arkansas State | "State" | 🔴 Collision |
| NC State | "State" | 🔴 Collision |
| + 8 more State schools | "State" | 🔴 All collide |

### Medium Priority (Tech Schools) - 4 Teams

| Team Name | Parsing Error | Impact |
|-----------|---------------|--------|
| Georgia Tech | "Tech" | 🟡 Collision |
| Virginia Tech | "Tech" | 🟡 Collision |
| Texas Tech | "Tech" | 🟡 Collision |
| Louisiana Tech | "Tech" | 🟡 Collision |

### Other Multi-Word Teams - 30+ Teams

Examples: Air Force, Boston College, North Carolina, South Carolina, Middle Tennessee, Western Michigan, Northern Illinois, Coastal Carolina, etc.

---

## Root Cause Analysis

### Issue 1: `_extract_teams()` Method

**File**: `src/kalshi_db_manager.py`, Lines 255-396

**Problem**: The regex-based extraction works for simple patterns but fails on multi-word team names because:

1. Splits on "at" → gets "Boise St." and "San Diego St."
2. `clean_team_name()` removes trailing "St." as punctuation
3. Returns "Boise" and "San Diego" (partially correct)
4. Then further splits "San Diego" → "San"

**Current Success Rate**: 83.3% on test cases, but only 50% on real NCAA markets

### Issue 2: `get_team_variations()` Method

**File**: `src/espn_kalshi_matcher.py`, Lines 84-110

**Problem**: Generates collision-prone variations:

```python
# For "Michigan State":
parts = team_name.split()
variations.append(parts[-1])  # Adds "State" ❌
variations.append(' '.join(parts[:-1]))  # Adds "Michigan" ❌
```

This creates false matches:
- "Michigan State" matches "Michigan"
- "Michigan State" matches any other "State" school

### Issue 3: Limited Predefined Variations

**File**: `src/espn_kalshi_matcher.py`, Lines 56-77

**Coverage**: Only 19 out of 134 FBS teams (14.2%)

Missing variations for:
- All MAC teams (Bowling Green, Western Michigan, etc.)
- All Sun Belt teams (Coastal Carolina, Georgia Southern, etc.)
- Most Mountain West teams (Boise State, San Diego State, etc.)
- Many G5 conference teams

---

## Immediate Fixes Needed

### Fix 1: Enhance Team Database Import in `_extract_teams()`

**Priority**: 🔴 CRITICAL

**Current Code** (Lines 285-306):
```python
try:
    from src.nfl_team_database import NFL_TEAMS
    # Builds all_team_names
except ImportError:
    pass

try:
    from src.ncaa_team_database import NCAA_TEAMS
    all_team_names.update(NCAA_TEAMS.keys())
except ImportError:
    pass
```

**Issue**: Import failures silently pass, leaving `all_team_names` empty

**Fix**: Make NCAA import mandatory and log errors:
```python
try:
    from src.ncaa_team_database import NCAA_TEAMS
    all_team_names.update(NCAA_TEAMS.keys())
    logger.info(f"Loaded {len(NCAA_TEAMS)} NCAA teams for validation")
except ImportError as e:
    logger.error(f"Failed to import NCAA teams: {e}")
    # Still continue with partial matching
```

### Fix 2: Add Abbreviation Handling

**Priority**: 🔴 CRITICAL

NCAA uses "St." abbreviation heavily. Add normalization:

```python
def normalize_abbreviations(name: str) -> str:
    """Expand common abbreviations in team names."""
    # Map abbreviations to full words
    abbr_map = {
        r'\bSt\.\s': 'State ',
        r'\bSt\b': 'State',
        r'\bTech\b': 'Tech',  # Keep as-is
    }

    normalized = name
    for pattern, replacement in abbr_map.items():
        normalized = re.sub(pattern, replacement, normalized, flags=re.IGNORECASE)

    return normalized
```

Apply before extraction:
```python
title = normalize_abbreviations(title)
home_team, away_team = db._extract_teams(title)
```

### Fix 3: Prevent Single-Word Fragments

**Priority**: 🔴 CRITICAL

Add validation to reject ambiguous results:

```python
def is_valid_team_name(name: str, all_team_names: set) -> bool:
    """Check if extracted name is valid, not just a fragment."""
    if not name:
        return False

    # Reject known collision words
    AMBIGUOUS_WORDS = {'state', 'tech', 'college', 'st', 'st.', 'force',
                       'san', 'new', 'carolina', 'michigan', 'florida',
                       'utah', 'tennessee', 'washington', 'northern',
                       'southern', 'eastern', 'western'}

    if name.lower() in AMBIGUOUS_WORDS:
        return False

    # Require at least 2 characters
    if len(name) < 2:
        return False

    # Prefer full match in database
    if all_team_names and name not in all_team_names:
        # Check if it's a substring of a full name
        for full_name in all_team_names:
            if name.lower() in full_name.lower() and len(full_name) > len(name):
                return False  # It's probably a partial match

    return True
```

### Fix 4: Expand CFB Variations (Top 50 Teams)

**Priority**: 🟡 HIGH

Add the most common NCAA teams to `CFB_TEAM_VARIATIONS`:

```python
CFB_TEAM_VARIATIONS = {
    # Existing 19 teams...

    # Add State schools
    'Michigan State Spartans': ['Michigan State', 'Spartans', 'MSU', 'Mich St', 'Michigan St'],
    'Florida State Seminoles': ['Florida State', 'Seminoles', 'FSU', 'Fla State', 'Florida St'],
    'Boise State Broncos': ['Boise State', 'Broncos', 'BSU', 'Boise St'],
    'San Diego State Aztecs': ['San Diego State', 'Aztecs', 'SDSU', 'San Diego St'],
    'Kansas State Wildcats': ['Kansas State', 'Wildcats', 'KSU', 'K-State', 'Kansas St'],
    'Oklahoma State Cowboys': ['Oklahoma State', 'Cowboys', 'OKST', 'Oklahoma St', 'Ok State'],
    'Arizona State Sun Devils': ['Arizona State', 'Sun Devils', 'ASU', 'Arizona St'],
    'Iowa State Cyclones': ['Iowa State', 'Cyclones', 'ISU', 'Iowa St'],
    'Mississippi State Bulldogs': ['Mississippi State', 'Bulldogs', 'MSST', 'Miss State', 'Mississippi St'],
    'NC State Wolfpack': ['NC State', 'Wolfpack', 'NCST', 'N.C. State'],

    # Add Tech schools
    'Georgia Tech Yellow Jackets': ['Georgia Tech', 'Yellow Jackets', 'GT', 'Ga Tech'],
    'Virginia Tech Hokies': ['Virginia Tech', 'Hokies', 'VT', 'Va Tech'],
    'Texas Tech Red Raiders': ['Texas Tech', 'Red Raiders', 'TTU', 'Tex Tech'],
    'Louisiana Tech Bulldogs': ['Louisiana Tech', 'Bulldogs', 'LT', 'La Tech'],

    # Add MAC teams
    'Bowling Green Falcons': ['Bowling Green', 'Falcons', 'BGSU', 'BG'],
    'Western Michigan Broncos': ['Western Michigan', 'Broncos', 'WMU', 'W Michigan'],
    'Northern Illinois Huskies': ['Northern Illinois', 'Huskies', 'NIU', 'N Illinois'],
    'Central Michigan Chippewas': ['Central Michigan', 'Chippewas', 'CMU', 'C Michigan'],

    # Add others
    'Air Force Falcons': ['Air Force', 'Falcons', 'AFA'],
    'Boston College Eagles': ['Boston College', 'Eagles', 'BC'],
    'Coastal Carolina Chanticleers': ['Coastal Carolina', 'Chanticleers', 'CCU'],
    # ... continue for top 50-75 teams
}
```

---

## Testing Checklist

### Before Fix
- ✅ 30 NCAA football markets in database
- ✅ 50% error rate (15/30 markets have wrong team names)
- ✅ Matched 2/10 games (both with wrong teams)

### After Fix (Expected)
- [ ] Re-sync all NCAA markets with fixed code
- [ ] Error rate < 5%
- [ ] Match rate > 90%
- [ ] All "State" schools parse correctly
- [ ] All "Tech" schools parse correctly

### Test Cases

```python
# Run these tests after implementing fixes
test_cases = [
    ('Boise St. at San Diego St. Winner?', 'Boise State', 'San Diego State'),
    ('Western Michigan at Northern Illinois Winner?', 'Western Michigan', 'Northern Illinois'),
    ('Akron at Bowling Green Winner?', 'Akron', 'Bowling Green'),
    ('Virginia Tech at Florida St. Winner?', 'Virginia Tech', 'Florida State'),
    ('Mississippi St. at Missouri Winner?', 'Mississippi State', 'Missouri'),
    ('Louisiana Tech at Washington St. Winner?', 'Louisiana Tech', 'Washington State'),
]
```

---

## Database Migration Script

### Clean and Re-Parse NCAA Markets

```sql
-- 1. Identify corrupted NCAA markets
SELECT ticker, title, home_team, away_team
FROM kalshi_markets
WHERE (ticker LIKE 'KXNCAAFGAME%' OR ticker LIKE 'KXCFBGAME%')
  AND (
      home_team IN ('State', 'St.', 'Tech', 'San', 'New', 'Carolina', 'Michigan', 'Northern', 'Southern')
      OR away_team IN ('State', 'St.', 'Tech', 'San', 'New', 'Carolina', 'Michigan', 'Northern', 'Southern')
      OR home_team IS NULL
      OR away_team IS NULL
  );

-- 2. Reset team names for re-parsing
UPDATE kalshi_markets
SET home_team = NULL, away_team = NULL
WHERE ticker LIKE 'KXNCAAFGAME%' OR ticker LIKE 'KXCFBGAME%';

-- 3. After code fix, re-run sync to re-parse teams
-- python sync_kalshi_markets.py --sport ncaa --force-reparse
```

---

## Impact on AI Predictions

### Current State
- AI predictions for "Michigan State" cannot match Kalshi odds because DB has "State" or "Michigan"
- Elo ratings lookup fails due to team name mismatch
- Edge calculations are wrong for affected games
- Betting recommendations are unreliable for 50% of NCAA games

### After Fix
- Accurate team name matching for >95% of games
- Elo ratings align correctly
- AI predictions match correct Kalshi markets
- Reliable betting recommendations

---

## Files to Modify

1. **`src/kalshi_db_manager.py`**
   - Line 255-396: Enhance `_extract_teams()`
   - Add abbreviation normalization
   - Add validation logic

2. **`src/espn_kalshi_matcher.py`**
   - Line 56-77: Expand `CFB_TEAM_VARIATIONS`
   - Line 84-110: Fix `get_team_variations()`

3. **`src/ncaa_team_database.py`**
   - No changes needed (already comprehensive)

---

## Estimated Effort

- **Code Changes**: 4 hours
- **Testing**: 2 hours
- **Database Migration**: 1 hour
- **Validation**: 1 hour
- **Total**: 1 day

---

## Success Metrics

- [ ] NCAA parsing error rate < 5%
- [ ] ESPN-to-Kalshi matching rate > 90%
- [ ] Zero "State" or "Tech" fragments in database
- [ ] All AI predictions align with correct teams
- [ ] No false positive betting opportunities

---

**Next Steps**: Implement Fix 1, Fix 2, and Fix 3 immediately. Test on 30 existing NCAA markets. Run migration script. Validate with live ESPN data.

**Owner**: Data Scientist Agent → Hand off to Backend Engineer
**Priority**: 🔴 CRITICAL (affects 50% of NCAA markets)
