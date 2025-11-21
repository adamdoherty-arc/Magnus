# Options Analysis - Quick Start Guide

## Overview

The **Options Analysis** page combines AI Options Agent (screening) and Comprehensive Strategy (deep analysis) into ONE streamlined interface with current positions integration.

---

## What's New?

### ✅ Unified Interface
- **One page** instead of two separate pages
- **Three-panel layout**: Selection → Analysis → Context
- **Seamless workflow**: Scan → Select → Analyze → Execute

### ✅ Current Positions Integration
- **New selection mode**: "Current Positions"
- Pulls your open options from Robinhood
- Analyze if your current strategy is still optimal
- Get recommendations: KEEP, ADJUST, or CLOSE

### ✅ AVA Chatbot Integration
- Ask AVA to find opportunities: *"Find CSP opportunities in NVDA watchlist"*
- Request analysis: *"What's the best strategy for AAPL?"*
- Check positions: *"Analyze my TSLA position"*
- Natural language commands built-in

---

## How to Use

### 1. Access the Page

Run the dashboard and navigate to **Options Analysis**:

```bash
streamlit run dashboard.py --server.port 8502
```

Then go to: **Options Analysis** in the sidebar

---

### 2. Select a Stock

**Four Ways to Select:**

#### Option A: Manual Entry
1. Choose "Manual Entry"
2. Type a symbol (e.g., AAPL)
3. Click "Analyze All Strategies"

#### Option B: From Watchlist
1. Choose "Watchlist"
2. Select a watchlist (e.g., NVDA)
3. Pick a symbol from dropdown
4. Click "Analyze All Strategies"

#### Option C: From Database
1. Choose "Database Search"
2. Select from available stocks
3. Click "Analyze All Strategies"

#### Option D: Current Positions ⭐ NEW
1. Choose "Current Positions"
2. Select one of your active positions
3. See current P&L, Greeks, DTE
4. Click "Analyze Position Strategies"
5. Get recommendation: KEEP/ADJUST/CLOSE

---

### 3. Run a Scan (Optional)

**To find opportunities across multiple stocks:**

1. Set filters in left panel:
   - DTE Range (e.g., 20-40 days)
   - Delta Range (e.g., -0.45 to -0.15)
   - Min Premium (e.g., $100)
   - Min Score (e.g., 50/100)

2. Click **"Run Scan"**

3. Review results in left panel

4. Click any result to load full analysis

---

### 4. Analyze Strategies

**When you select a stock or scan result:**

1. Center panel shows market environment:
   - Volatility regime (LOW/MEDIUM/HIGH)
   - Trend (BULLISH/BEARISH/SIDEWAYS)
   - IV percentile

2. All 10 strategies are ranked:
   - Cash-Secured Put
   - Iron Condor
   - Poor Man's Covered Call
   - Bull Put Spread
   - Bear Call Spread
   - Covered Call
   - Calendar Spread
   - Diagonal Spread
   - Long Straddle
   - Short Strangle

3. Top 3 strategies shown with:
   - Score (0-100)
   - Win rate
   - Best-case scenario
   - Risk profile

4. Multi-model AI consensus (optional):
   - Claude Sonnet 4.5
   - Gemini Pro
   - DeepSeek

---

### 5. Use AVA Chatbot

**AVA can run analyses for you!**

**Examples:**

```
You: "Find CSP opportunities in my NVDA watchlist"
AVA: → Runs scan → Returns top 5 with scores

You: "What's the best strategy for AAPL?"
AVA: → Analyzes AAPL → Shows top 3 strategies

You: "Analyze my TSLA position"
AVA: → Loads your TSLA position → Gives KEEP/ADJUST/CLOSE recommendation

You: "Show me calendar spreads on SPY"
AVA: → Filters to calendar spread → Shows analysis
```

---

## Understanding Results

### Scan Results

**Each opportunity shows:**
- **Symbol**: Stock ticker
- **Score**: 0-100 (based on 5 criteria)
- **Strike**: Option strike price
- **DTE**: Days to expiration
- **Premium**: Premium in dollars

**Score Breakdown:**
- **Fundamental** (20%): P/E, market cap, sector
- **Technical** (20%): Price trends
- **Greeks** (20%): Delta, IV, theta
- **Risk** (25%): Max loss, breakeven
- **Sentiment** (15%): Market sentiment

**Recommendations:**
- **STRONG BUY**: Score 75-100
- **BUY**: Score 60-74
- **HOLD**: Score 50-59
- **AVOID**: Score < 50

### Strategy Analysis

**Each strategy shows:**
- **Score**: Suitability for current market (0-100)
- **Win Rate**: Historical success rate
- **Best When**: Optimal market conditions
- **Risk Profile**: Conservative/Moderate/Aggressive

**Market Environment:**
- **Volatility**: LOW (IV < 30%) | MEDIUM (30-60%) | HIGH (> 60%)
- **Trend**: BULLISH | SIDEWAYS | BEARISH
- **Market Regime**: Bull Market | Bear Market | Range-Bound

### Position Recommendations

**For current positions:**
- **KEEP**: Current strategy is still optimal, P&L acceptable
- **ADJUST**: Consider rolling or modifying (e.g., close and reopen with different strike/expiry)
- **CLOSE**: Exit position (strategy no longer suitable or significant loss)

---

## Workflow Examples

### Example 1: Weekly CSP Scan

**Goal**: Find 3-5 CSP opportunities for the week

1. Select "Watchlist" → Choose "NVDA"
2. Set filters: DTE 20-40, Delta -0.30 to -0.20, Premium $100+
3. Click "Run Scan"
4. Review top 10 results sorted by score
5. Click top 3 to analyze each
6. Compare strategy rankings
7. Execute best opportunities

**Time**: 5 minutes

---

### Example 2: Position Health Check

**Goal**: Review all current positions monthly

1. Select "Current Positions"
2. For each position:
   - View current P&L and Greeks
   - Click "Analyze Position Strategies"
   - Review recommendation (KEEP/ADJUST/CLOSE)
   - See alternative strategies
3. Take action on ADJUST or CLOSE recommendations

**Time**: 2 minutes per position

---

### Example 3: New Stock Deep Dive

**Goal**: Research a stock you're interested in

1. Select "Manual Entry" → Enter "AAPL"
2. Review auto-filled data (price, IV, fundamentals)
3. Click "Analyze All Strategies"
4. Review market environment
5. See all 10 strategies ranked
6. Read multi-model AI consensus
7. Pick best strategy for execution

**Time**: 3 minutes

---

### Example 4: AVA Voice Command

**Goal**: Quick analysis while multitasking

1. Open AVA chatbot (always visible at top)
2. Type or speak: *"Find opportunities in my Investment watchlist"*
3. AVA returns top 5 with scores
4. Click any to see full analysis
5. Execute trade

**Time**: 1 minute

---

## Performance Targets

✅ **Page Load**: < 2 seconds
✅ **Scan Execution** (100 stocks): < 1 second
✅ **Strategy Analysis**: < 500ms
✅ **Greeks Calculation**: < 200ms
✅ **Multi-Model Consensus**: < 5 seconds

---

## Tips & Tricks

### Tip 1: Save Time with Scan Presets
**Create your favorite filter combinations:**
- Conservative CSPs: Delta -0.20 to -0.10, DTE 30-45
- High Premium: Min $200, DTE 20-30
- Earnings Plays: DTE 5-15, High IV stocks

### Tip 2: Use Positions Mode Weekly
**Every Monday morning:**
- Review all positions
- Check if strategies still optimal
- Roll losing positions before they expire worthless

### Tip 3: Compare Strategies
**When analyzing:**
- Don't just pick #1 strategy
- Compare top 3 scores
- Consider your risk tolerance
- Check if consensus agrees

### Tip 4: Leverage AVA for Speed
**AVA is fastest for:**
- Quick scans ("find opportunities")
- Single stock analysis ("analyze TSLA")
- Position checks ("my AAPL position")

---

## Troubleshooting

### Issue: "No positions found"
**Solution**:
1. Ensure Robinhood credentials in `.env`
2. Check you have open options positions
3. Log in to Robinhood manually first

### Issue: "Could not fetch data for [symbol]"
**Solution**:
1. Verify symbol is correct (e.g., "AAPL" not "Apple")
2. Check stock is in database
3. Try different symbol

### Issue: "Scan returns 0 results"
**Solution**:
1. Loosen filters (wider DTE/delta range)
2. Lower min premium threshold
3. Lower min score threshold
4. Check watchlist has symbols

### Issue: "Strategies not loading"
**Solution**:
1. Check internet connection (for LLM calls)
2. Verify LLM providers configured
3. Try without multi-model consensus
4. Refresh page

---

## What Happened to Old Pages?

### AI Options Agent Page → Archived
**All features merged into Options Analysis:**
- Batch screening ✅
- Multi-criteria scoring ✅
- LLM reasoning ✅
- Watchlist support ✅

### Comprehensive Strategy Page → Archived
**All features merged into Options Analysis:**
- 10 strategy evaluation ✅
- Market environment analysis ✅
- Multi-model AI consensus ✅
- Auto-fill from database ✅

**Old pages moved to:**
- `ai_options_agent_page.py.old`
- `comprehensive_strategy_page.py.old`

---

## What's Next?

### Coming Soon:
- [ ] P&L visualization charts (payoff diagrams)
- [ ] Real-time Greeks updates
- [ ] Unusual options flow detection
- [ ] Earnings calendar integration
- [ ] IV rank/percentile charts
- [ ] Backtesting results
- [ ] Export to CSV/PDF
- [ ] Mobile-responsive design

---

## Need Help?

1. **Click "Help" in right panel** - Built-in quick reference
2. **Ask AVA** - *"How do I use Options Analysis?"*
3. **Review examples** - See workflow examples above
4. **Check documentation** - See `UNIFIED_OPTIONS_ANALYSIS_PLAN.md`

---

## Summary

**One Page. Three Panels. Four Selection Modes. Ten Strategies. Unlimited Possibilities.**

**Left Panel** → Find opportunities (scan)
**Center Panel** → Analyze strategies (deep dive)
**Right Panel** → Context (stats, performance)
**AVA Chat** → Natural language commands

**Result:** Faster decisions, better trades, integrated workflow.

Enjoy! 🚀
