# AVA Betting System - Quick Start Guide

**Status:** ✅ PRODUCTION READY
**Dashboard:** http://localhost:8507 → 🎯 AVA Betting Picks

---

## 🚀 Quick Start (30 seconds)

1. Open http://localhost:8507
2. Click "🎯 AVA Betting Picks" in sidebar
3. Wait ~30 seconds for analysis
4. Review Top 10 picks ranked by AI

---

## 📊 What You Get

**257 Games Analyzed**
- 123 NFL games (Weeks 11-18)
- 83 NCAA games (Weeks 11-16)
- 51 NBA games (Next 7 days)

**34 Betting Opportunities**
- Real Kalshi prediction market odds
- AI-powered analysis
- Expected value calculations
- Kelly Criterion bet sizing

---

## 🎯 How Rankings Work

```
Combined Score = (Win Probability × 60%) + (Expected Value × 40%)
```

**Balances:**
- 60% Safety (high confidence)
- 40% Profit (positive EV)

---

## 🟢 Confidence Levels

| Badge | Win Prob | Recommendation | Action |
|-------|----------|----------------|--------|
| 🟢 HIGH | ≥70% | STRONG BET | Bet with Kelly sizing |
| 🟡 MEDIUM | 60-69% | MODERATE BET | Small bet or pass |
| ⚪ LOW | <60% | PASS | Do not bet |

---

## 💰 Bet Sizing Example

**Game:** Buffalo Bills (70% win prob, 70¢ odds)
**Kelly:** 4.8%
**Bankroll:** $10,000

**Recommended Bet:** $480 × 0.25 = **$120**
(System uses 1/4 Kelly for safety)

---

## 📱 Three Tabs

1. **🏆 Top Picks** - Top 10 opportunities with full analysis
2. **📊 All Opportunities** - Complete data table + CSV download
3. **📈 Analytics** - Charts, insights, sport breakdown

---

## 🔬 What Gets Analyzed

**For Each Game:**
- Current game state (score, time)
- Kalshi prediction market odds
- Historical matchup data
- Team records and trends

**AI Calculates:**
- Win probability
- Expected value (EV)
- Kelly Criterion bet size
- Confidence score
- Betting recommendation

---

## 📋 Sample Top Pick

```
#1 - NFL: Minnesota Vikings @ Dallas Cowboys

Recommended Bet: Dallas Cowboys (96% win prob)
Kalshi Odds: 96¢
Expected Value: $96.00
Kelly Criterion: 6.2%
Confidence: HIGH
Score: 97.6

🚀 STRONG BET - High confidence with positive EV
```

---

## 🧪 Run Tests

```bash
python test_betting_system_simple.py
```

**Expected:**
- ✅ 257 games fetched
- ✅ 34 opportunities identified
- ✅ 19 ranked picks
- ✅ Top 5 displayed

---

## ⚡ Feature Parity

**All Sports Have:**
- ✅ Multi-period fetching
- ✅ Kalshi odds integration
- ✅ AI analysis
- ✅ Confidence badges
- ✅ Color-coded favorites
- ✅ Win probability bars
- ✅ Betting recommendations
- ✅ EV calculations
- ✅ Kelly Criterion sizing

---

## 📁 Key Files

**New:**
- `ava_betting_recommendations_page.py` - Main page
- `test_betting_system_simple.py` - Tests

**Modified:**
- `dashboard.py` - Added navigation
- `game_cards_visual_page.py` - NCAA multi-week
- `src/advanced_betting_ai_agent.py` - Decimal fix

---

## ⚠️ Important Notes

1. **Always verify odds** - Check Kalshi/Robinhood before betting
2. **Use bankroll management** - Never bet more than you can lose
3. **Track results** - Monitor actual vs expected performance
4. **Past ≠ Future** - No guarantees of profit

---

## 🎓 Learn More

- [AVA_BETTING_SYSTEM_COMPLETE_SUMMARY.md](AVA_BETTING_SYSTEM_COMPLETE_SUMMARY.md) - Full implementation details
- [AVA_BETTING_RECOMMENDATIONS_COMPLETE.md](AVA_BETTING_RECOMMENDATIONS_COMPLETE.md) - Technical documentation
- [AVA_BETTING_COMPLETE_WITH_NCAA.md](AVA_BETTING_COMPLETE_WITH_NCAA.md) - NCAA integration guide

---

**Ready to find the best betting opportunities? Open the dashboard and click "🎯 AVA Betting Picks"!**
