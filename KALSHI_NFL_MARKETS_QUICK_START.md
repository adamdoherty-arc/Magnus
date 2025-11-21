# Kalshi NFL Markets Dashboard - Quick Start Guide

## 5-Minute Setup

### Step 1: Install Dependencies

```bash
pip install streamlit pandas plotly psycopg2-binary
```

### Step 2: Set Database Password

```bash
# Windows
set DB_PASSWORD=your_postgres_password

# Mac/Linux
export DB_PASSWORD=your_postgres_password
```

### Step 3: Sync Market Data

```bash
python sync_kalshi_complete.py
```

### Step 4: Run Dashboard

```bash
streamlit run kalshi_nfl_markets_page.py
```

Dashboard opens at: `http://localhost:8501`

---

## Key Features at a Glance

### 🏈 Main Dashboard
- **View:** 581 NFL markets with AI predictions
- **Sort by:** Confidence, Edge %, Volume, Closing Soon
- **Display:** Cards or Table view

### 🔍 Filters (Sidebar)
- **Search:** Type team, player, or keyword
- **Teams:** Multi-select dropdown
- **Bet Types:** Spread, Total, Moneyline, Props, Parlays
- **Confidence:** Slider (0-100)
- **Edge:** Slider (-10% to +20%)
- **Timing:** Today, Tomorrow, This Week, This Month
- **Risk:** Low, Medium, High

### ⭐ Watchlist
- Click "⭐ Add to Watchlist" on any market
- Access from "⭐ Watchlist" tab
- Track favorite opportunities

### ⚖️ Compare Markets
- Select 2-4 markets
- Side-by-side metric comparison
- Visual charts (confidence, edge)

### 📊 Analytics
- Volume trends (top 10 markets)
- Confidence distribution
- Opportunity heatmap (team x bet type)
- Edge vs Confidence scatter plot

### 💾 Export
- CSV, JSON, or Excel format
- Includes all filtered markets
- Timestamped filename

---

## Common Workflows

### Find High-Confidence Opportunities

1. Set **Confidence** slider to 80
2. Set **Edge** slider to 5.0
3. Select **Risk**: Low
4. Click **Sort by**: Confidence
5. Review top results

### Track Specific Team

1. Open sidebar
2. Select team from **Teams** dropdown
3. View all markets for that team
4. Add promising ones to watchlist

### Compare Similar Markets

1. Find related markets (same game, different props)
2. Go to **⚖️ Compare** tab
3. Select markets from dropdown
4. Analyze metrics side-by-side

### Monitor Closing Soon

1. Select **Timing**: Today
2. Sort by **Closing Soon**
3. Review urgent opportunities
4. Add alerts (coming soon)

---

## Keyboard Shortcuts

- `Ctrl + R` - Refresh data (clear cache)
- `Ctrl + F` - Focus search box
- `Esc` - Close expanded card
- Arrow keys - Navigate pagination

---

## Understanding the Metrics

### Confidence Score (0-100)
- **80+** = High confidence (Low risk)
- **60-80** = Medium confidence
- **<60** = Low confidence (High risk)

### Edge Percentage
- **Positive** = Market mispricing in your favor
- **>5%** = Strong edge, good opportunity
- **Negative** = Avoid, market has advantage

### Risk Level
- **Low** = Confidence 80+
- **Medium** = Confidence 60-80
- **High** = Confidence <60

### Volume
- **>$1,000** = Liquid market, easy to trade
- **<$100** = Illiquid, may be hard to execute

---

## Troubleshooting

### No markets showing?
```bash
# Sync data first
python sync_kalshi_complete.py
```

### Charts not rendering?
```bash
pip install --upgrade plotly
```

### Database connection error?
```bash
# Check password is set
echo %DB_PASSWORD%  # Windows
echo $DB_PASSWORD   # Mac/Linux
```

### Slow performance?
- Enable pagination (set to 20 items/page)
- Clear filters if too restrictive
- Click "🔄 Refresh Data" to clear cache

---

## Tips & Tricks

1. **Use Search First:** Quickly narrow down markets before filtering
2. **Combine Filters:** Stack multiple filters for laser-focused results
3. **Watch the Metrics:** Top dashboard shows how many markets match
4. **Pagination:** Use table view for scanning many markets quickly
5. **Export Before Analysis:** Save filtered results for offline review
6. **Watchlist Everything:** Better to track too many than miss opportunities
7. **Check Analytics Tab:** Identify market trends before diving into details
8. **Mobile:** Sidebar auto-collapses, tap hamburger to open filters

---

## Integration with Main Dashboard

Add to your `dashboard.py`:

```python
import kalshi_nfl_markets_page

page_map = {
    "Home": home_page.show,
    "Kalshi NFL Markets": kalshi_nfl_markets_page.show,  # Add this line
    # ... other pages
}
```

---

## Sample Filter Combinations

### Conservative Investor
- Confidence: 85+
- Edge: 3.0+
- Risk: Low
- Volume: 1000+

### Aggressive Trader
- Confidence: 60+
- Edge: 8.0+
- Risk: Medium, High
- Timing: Today, Tomorrow

### Volume Trader
- Volume: 5000+
- Edge: Any positive
- Timing: This Week
- Sort: Volume

### Value Hunter
- Edge: 10.0+
- Confidence: Any
- Risk: Any
- Sort: Edge %

---

## Next Steps

1. ✅ Run dashboard and explore interface
2. ✅ Try different filter combinations
3. ✅ Add markets to watchlist
4. ✅ Compare similar opportunities
5. ✅ Review analytics for insights
6. ✅ Export data for further analysis

**Ready to find NFL prediction market opportunities!** 🏈🎯

---

## Resources

- **Full Documentation:** `KALSHI_NFL_MARKETS_PAGE_DOCUMENTATION.md`
- **Database Schema:** `src/kalshi_schema.sql`
- **API Evaluator:** `src/kalshi_ai_evaluator.py`
- **Sync Script:** `sync_kalshi_complete.py`

---

**Last Updated:** 2025-11-09
