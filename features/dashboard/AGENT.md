# Dashboard Feature Agent

## Agent Identity

- **Feature Name**: Dashboard
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The Dashboard Agent is responsible for **portfolio visualization and performance tracking**. It serves as the central hub for monitoring trading activity, analyzing historical performance, and forecasting future outcomes.

### Primary Responsibilities
1. Display real-time portfolio status (balance, buying power, positions)
2. Manage and track complete trade history
3. Generate balance forecasts with best/expected/worst scenarios
4. Calculate theta decay projections for active positions
5. Provide AI-powered trade analysis and recommendations
6. Track performance metrics (win rate, average P/L, ROI)

### Data Sources
- **Robinhood API**: Account data, positions, real-time values
- **PostgreSQL**: Trade history, performance metrics
- **Redis**: Cached market data, session state
- **Local Calculations**: Forecasts, theta decay, probabilities

## Feature Capabilities

### What This Agent CAN Do
- ✅ Display real-time account balance and buying power
- ✅ Show all active cash-secured put positions
- ✅ Track complete trade history with P/L calculations
- ✅ Generate expiration-based balance forecasts
- ✅ Calculate theta decay profit projections
- ✅ Provide AI recommendations for position management
- ✅ Show cumulative P/L over time
- ✅ Calculate annualized returns for closed trades
- ✅ Display position-specific risk metrics
- ✅ Forecast assignment probabilities

### What This Agent CANNOT Do
- ❌ Execute trades (requires user action + Robinhood)
- ❌ Modify positions (that's Positions Agent's role)
- ❌ Find new opportunities (that's Opportunities Agent)
- ❌ Scan for premiums (that's Premium Scanner Agent)
- ❌ Manage watchlists (that's TradingView Agent)
- ❌ Change settings (that's Settings Agent)

## Dependencies

### Required Features
- **Positions Agent**: For active position data
- **Settings Agent**: For Robinhood connection status

### Optional Features
- **Earnings Calendar Agent**: For earnings warnings in forecasts
- **Prediction Markets Agent**: For sentiment data in analysis

### External APIs
- **Robinhood API**: Primary data source
- **yfinance**: Stock price lookups for probability calculations

### Database Tables
- `trade_history`: Stores all trade records
- `positions`: Cache of active positions (optional)

## Key Files & Code

### Main Implementation
- `dashboard.py`: Lines 124-349 (Dashboard page rendering)
- `src/agents/runtime/risk_management_agent.py`: Risk calculations
- `src/ai_trade_analyzer.py`: AI recommendations

### Database Queries
```sql
-- Get trade history
SELECT * FROM trade_history
WHERE user_id = ?
ORDER BY trade_date DESC;

-- Calculate P/L summary
SELECT
  SUM(net_profit) as total_pl,
  COUNT(*) as total_trades,
  AVG(net_profit) as avg_pl
FROM trade_history
WHERE status = 'closed';
```

## Current State

### Implemented Features
✅ Portfolio status overview (balance, buying power, premium collected)
✅ Trade history tracking with manual entry/close
✅ Balance forecast timeline with expiration-based projections
✅ Individual position forecasts with theta decay
✅ AI trade analysis with HIGH/MEDIUM/LOW urgency
✅ Assignment probability calculations
✅ Breakeven price analysis
✅ Annualized return calculations
✅ Cumulative P/L visualization

### Known Limitations
⚠️ Trade history requires manual entry (auto-sync planned)
⚠️ Forecasts assume simplified probabilities (70% expire worthless)
⚠️ Assignment probability uses basic Black-Scholes approximation
⚠️ Historical performance only shows completed trades

### Recent Changes
See [CHANGELOG.md](./CHANGELOG.md) for detailed history.

## Communication Patterns

### Incoming Requests

#### From Main Agent
```yaml
Request: "Show portfolio overview"
Response:
  - Account balance: $XX,XXX
  - Buying power: $XX,XXX
  - Active positions: N
  - Premium collected: $X,XXX
  - Capital at risk: $XX,XXX
```

#### From User
```yaml
Request: "What's my performance this month?"
Response:
  - Query trade_history for current month
  - Calculate total P/L, win rate, average trade
  - Return formatted metrics
```

### Outgoing Requests

#### To Positions Agent
```yaml
Request: "Get all active CSP positions"
Purpose: Display in portfolio overview
Expected Response: List of position objects with:
  - symbol, strike, expiration
  - premium, current_value, P&L
  - days_to_expiry
```

#### To Robinhood API (via Settings)
```yaml
Request: "Get account data"
Purpose: Display real-time balance
Expected Response:
  - portfolio_value
  - buying_power
  - account_number
```

## Data Flow

```
User Opens Dashboard
       ↓
Dashboard Agent Loads
       ↓
Check Robinhood Connection (via Settings Agent)
       ↓
   Connected?
       ↓
    Yes → Fetch Account Data + Positions
       ↓
Calculate Forecasts (theta, assignment prob, etc.)
       ↓
Load Trade History from PostgreSQL
       ↓
Generate AI Recommendations
       ↓
Render Dashboard UI
```

## Error Handling

### Robinhood API Failure
```python
if not st.session_state.get('rh_connected'):
    st.info("💡 Connect to Robinhood in Settings to see real data")
    # Show empty state / sample UI
```

### Database Connection Error
```python
try:
    trade_history = load_trades_from_db()
except Exception as e:
    st.error(f"Failed to load trade history: {e}")
    trade_history = []
```

### Missing Position Data
```python
if not positions:
    if rh_connected:
        st.warning("No positions found")
    else:
        st.info("No active positions")
```

## Performance Considerations

### Caching Strategy
- Cache account data for 30 seconds
- Cache positions for 60 seconds
- Recalculate forecasts only when positions change
- Trade history cached until manual refresh

### Optimization
- Lazy load trade history (paginated)
- Calculate metrics on-demand
- Use SQL aggregations for summaries
- Memoize expensive calculations

## Testing Checklist

### Before Deployment
- [ ] Dashboard loads without Robinhood connection
- [ ] Dashboard loads with Robinhood connection
- [ ] Balance forecasts calculate correctly
- [ ] Theta decay projections show proper acceleration
- [ ] AI recommendations trigger at correct thresholds
- [ ] Trade history P/L matches actual values
- [ ] No crashes with empty data
- [ ] Performance acceptable with 100+ trades

### Integration Tests
- [ ] Positions data syncs correctly from Positions Agent
- [ ] Account data updates when Settings changed
- [ ] Trade history persists to database
- [ ] Forecasts update when positions close

## Maintenance

### When to Update This Agent

1. **User Request**: "Show me X metric on dashboard"
   - Update dashboard.py
   - Update TODO.md with requirement
   - Document in CHANGELOG.md when complete

2. **Bug Report**: "Forecast showing wrong values"
   - Debug calculation logic
   - Fix and test
   - Document fix in CHANGELOG.md

3. **Feature Request**: "Add weekly P/L breakdown"
   - Assess feasibility
   - Add to WISHLIST.md or TODO.md
   - Coordinate with Main Agent if affects other features

4. **API Change**: Robinhood API updates
   - Update API integration code
   - Test thoroughly
   - Document breaking changes in CHANGELOG.md
   - Alert Main Agent of impacts

### Monitoring
- Check dashboard load times (should be < 2s)
- Monitor database query performance
- Track API call frequency (stay under rate limits)
- Review user feedback for UX improvements

## Integration Points

### Robinhood Integration
- Account balance and buying power
- Active positions with current values
- Option chain data for price lookups

### Database Integration
- Trade history storage and retrieval
- Performance metrics aggregation
- Historical P/L tracking

### Agent Coordination
- **Positions Agent**: Source of truth for active positions
- **Settings Agent**: Manages Robinhood connection
- **Earnings Calendar Agent**: Provides earnings warnings
- **Prediction Markets Agent**: Adds sentiment context

## Future Enhancements

See [WISHLIST.md](./WISHLIST.md) for planned features:
- Auto-sync trade history from Robinhood
- Advanced forecasting with Monte Carlo simulation
- Performance analytics (Sharpe ratio, max drawdown)
- Portfolio rebalancing suggestions
- Tax-loss harvesting identification
- Benchmark comparisons (SPY, QQQ)

## Questions This Agent Can Answer

1. "What's my current portfolio value?"
2. "How much buying power do I have?"
3. "What's my total P/L this month?"
4. "When do my positions expire?"
5. "What's my expected balance next week?"
6. "Which positions should I close?"
7. "What's my win rate?"
8. "How much theta am I collecting daily?"
9. "What's my annualized return?"
10. "What's my risk exposure?"

## Questions This Agent CANNOT Answer

1. "Find me new opportunities" → Opportunities Agent
2. "What premiums are available?" → Premium Scanner Agent
3. "Sync my TradingView watchlist" → TradingView Watchlists Agent
4. "When is earnings for AAPL?" → Earnings Calendar Agent
5. "Change my risk parameters" → Settings Agent

---

**For detailed architecture and specifications, see:**
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SPEC.md](./SPEC.md)
- [README.md](./README.md)

**For current tasks and planned work, see:**
- [TODO.md](./TODO.md)
- [WISHLIST.md](./WISHLIST.md)
- [CHANGELOG.md](./CHANGELOG.md)
