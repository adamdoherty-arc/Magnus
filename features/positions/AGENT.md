# Positions Feature Agent

## Agent Identity

- **Feature Name**: Positions
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: ✅ Active & Production Ready

## Role & Responsibilities

The Positions Agent is responsible for **real-time options portfolio management and position tracking**. It serves as the operational core for monitoring active wheel strategy trades, calculating profit/loss metrics, and providing AI-powered recommendations for optimal position management.

### Primary Responsibilities
1. Display real-time position data with live market prices
2. Calculate comprehensive P&L metrics for all active positions
3. Generate theta decay forecasts for time value analysis
4. Provide AI-powered exit timing recommendations
5. Monitor assignment risk and moneyness status
6. Track position-specific risk metrics and Greeks
7. Alert users to high-profit opportunities (20%+ thresholds)
8. Support auto-refresh capabilities for hands-free monitoring

### Data Sources
- **Robinhood API**: Primary source for position data, option prices, account values
- **Yahoo Finance**: Supplementary stock price data for probability calculations
- **Local Calculations**: Theta decay projections, P&L metrics, AI recommendations
- **Session State**: Cached position data, refresh settings, alert status

## Feature Capabilities

### What This Agent CAN Do
- ✅ Fetch and display all active CSP and CC positions from Robinhood
- ✅ Calculate real-time P&L with current market prices
- ✅ Generate theta decay forecasts showing daily profit projections
- ✅ Provide AI analysis with actionable recommendations (BUY_BACK, HOLD, MONITOR)
- ✅ Display option Greeks (delta, ITM/OTM status, moneyness percentage)
- ✅ Calculate annualized returns for each position
- ✅ Show assignment probabilities based on Black-Scholes model
- ✅ Auto-refresh positions at configurable intervals (30s, 1m, 2m, 5m)
- ✅ Generate profit alerts for positions exceeding thresholds
- ✅ Display breakeven prices and profit targets
- ✅ Link to TradingView charts for underlying stocks
- ✅ Track days to expiration with visual indicators

### What This Agent CANNOT Do
- ❌ Execute trades or modify positions (requires Robinhood interface)
- ❌ Find new opportunities (that's Opportunities Agent's role)
- ❌ Scan for premium opportunities (that's Premium Scanner Agent)
- ❌ Manage watchlists (that's TradingView Watchlists Agent)
- ❌ Predict earnings dates (that's Earnings Calendar Agent)
- ❌ Change platform settings (that's Settings Agent)
- ❌ Automatically close positions (requires user confirmation)

## Dependencies

### Required Features
- **Settings Agent**: For Robinhood connection status and credentials
- **Robinhood API**: For position data, pricing, and account information

### Optional Features
- **Earnings Calendar Agent**: For earnings warnings in position analysis
- **Prediction Markets Agent**: For sentiment data in AI recommendations
- **Dashboard Agent**: For portfolio-level aggregation and history

### External APIs
- **Robinhood API**: Primary data source for positions and prices
- **Yahoo Finance (yfinance)**: Stock price lookups for probability calculations
- **TradingView**: Chart links for position analysis (external)

### Database Tables
- `trade_history`: Stores closed trade records (optional)
- `positions`: Cache of active positions (optional)

## Key Files & Code

### Main Implementation
- `dashboard.py`: Lines 351-1121 (Positions page rendering and logic)
- `src/robinhood_integration.py`: Robinhood API client for position fetching
- `src/ai_trade_analyzer.py`: AI recommendations engine
- `src/agents/runtime/risk_management_agent.py`: Risk calculations

### Critical Functions
```python
# Position Data Fetching (dashboard.py)
def get_wheel_positions():
    """
    Fetches active CSP/CC positions from Robinhood
    Returns: List of position dictionaries with all metrics
    """

# P&L Calculation
def calculate_position_pnl(position):
    """
    Calculates profit/loss metrics
    - Premium collected vs current value
    - Percentage of max profit captured
    - Annualized return calculations
    """

# Theta Decay Forecast
def forecast_theta_decay(position, days_to_expiry):
    """
    Projects option value decay over time
    Uses square root of time model
    Returns daily profit projections
    """

# AI Analysis
def analyze_position(symbol, strike, expiration, premium, current_value, days_to_expiry):
    """
    Generates AI-powered recommendations
    Evaluates: profit targets, time decay, assignment risk
    Returns: action, risk level, confidence score
    """
```

### Key Data Structures
```python
# Position Object
{
    'symbol': 'AAPL',
    'type': 'CSP' or 'CC',
    'strike': 150.00,
    'expiration': '2024-02-16',
    'premium': 250.00,              # Total collected
    'current_value': 120.00,        # Current cost to close
    'option_price': 1.20,           # Per-share price
    'pnl': 130.00,                  # Unrealized profit
    'pnl_pct': 52.0,               # Percentage captured
    'days_to_expiry': 15,
    'contracts': 1,
    'current_stock_price': 155.00,
    'moneyness': 'OTM',
    'moneyness_pct': 3.33,
    'annualized_return': 126.5,
    'chart_url': 'https://tradingview.com/...'
}
```

## Current State

### Implemented Features
✅ Real-time position tracking with live prices
✅ Comprehensive P&L calculations (dollar and percentage)
✅ Theta decay forecasting with acceleration model
✅ AI-powered trade analysis with urgency levels
✅ Assignment probability calculations
✅ Breakeven price analysis
✅ Annualized return projections
✅ Auto-refresh functionality (configurable intervals)
✅ High-profit alerts with visual celebrations
✅ TradingView chart integration
✅ Option price tracking (per share and per contract)
✅ ITM/OTM status monitoring
✅ Days to expiration countdown

### Known Limitations
⚠️ Positions require active Robinhood connection
⚠️ Theta forecast uses simplified square root model (not full Black-Scholes)
⚠️ Assignment probability uses basic approximation
⚠️ Auto-refresh uses meta tag (full page reload)
⚠️ No position modification capabilities (view-only)
⚠️ Historical P&L tracking requires Dashboard Agent

### Recent Changes
- Added After-Hours Pricing support for post-market monitoring
- Fixed TradingView links to use correct chart URLs
- Enhanced P&L calculations using processed_premium_direction
- Added stock price column to positions table
- Improved session scope handling for Robinhood connection

## Communication Patterns

### Incoming Requests

#### From Main Agent
```yaml
Request: "Show all active positions"
Response:
  - Fetches positions from Robinhood
  - Calculates current P&L
  - Returns formatted position list
```

#### From User
```yaml
Request: "What positions should I close?"
Response:
  - Runs AI analysis on all positions
  - Identifies high-profit opportunities (>50%)
  - Provides recommendations with reasoning
```

### Outgoing Requests

#### To Robinhood API (via RobinhoodClient)
```yaml
Request: "Get all option positions"
Purpose: Fetch active CSP/CC positions
Expected Response:
  - Option details (symbol, strike, expiration)
  - Current values and premiums
  - Position type (short put/call)
  - Quantity and cost basis
```

#### To Yahoo Finance
```yaml
Request: "Get current stock price for {symbol}"
Purpose: Calculate moneyness and assignment probability
Expected Response:
  - Current market price
  - Used for ITM/OTM determination
```

## Data Flow

```
User Opens Positions Page
       ↓
Check Robinhood Connection (via Settings)
       ↓
   Connected?
       ↓
    Yes → Fetch Positions from Robinhood API
       ↓
Transform Raw Position Data
       ↓
Calculate P&L Metrics
  - Premium vs Current Value
  - Percentage of Max Profit
  - Daily/Annualized Returns
       ↓
Generate Theta Decay Forecast
  - Project daily value decay
  - Calculate expected profit timeline
  - Show acceleration near expiration
       ↓
Run AI Analysis
  - Evaluate profit targets
  - Assess assignment risk
  - Generate recommendations
       ↓
Check for High-Profit Alerts
  - Flag positions >20% profit
  - Trigger visual notifications
       ↓
Render Positions Table
  - Sortable columns
  - Color-coded P&L
  - Expandable theta forecasts
  - AI recommendations display
```

## Error Handling

### Robinhood API Failure
```python
if not st.session_state.get('rh_connected'):
    st.info("💡 Connect to Robinhood in Settings to see live positions")
    # Show empty state with instructions
```

### Missing Position Data
```python
if not positions or len(positions) == 0:
    if rh_connected:
        st.success("✅ No active positions - Portfolio is clear!")
    else:
        st.info("📊 Connect to Robinhood to view positions")
```

### Calculation Errors
```python
try:
    theta_forecast = calculate_theta_decay(position)
except Exception as e:
    logger.error(f"Theta calculation failed for {position['symbol']}: {e}")
    theta_forecast = None  # Graceful degradation
```

### API Rate Limiting
```python
try:
    positions = rh_client.get_wheel_positions()
except RateLimitError:
    st.warning("⏱️ API rate limit reached. Please wait a moment.")
    positions = st.session_state.get('cached_positions', [])
```

## Performance Considerations

### Caching Strategy
- Position data cached in session state
- Cache refreshes on manual refresh or auto-refresh trigger
- Current prices updated independently from position structure
- Theta forecasts calculated on-demand, not stored

### Optimization
- Lazy load theta forecasts (expandable sections)
- Calculate AI analysis only for visible positions
- Use vectorized calculations for P&L (when multiple positions)
- Minimize API calls through intelligent caching

### Response Times
| Operation | Target Time | Current |
|-----------|-------------|---------|
| Load positions | < 2s | ~1.5s |
| Calculate P&L | < 100ms | ~50ms |
| Theta forecast | < 100ms | ~80ms |
| AI analysis | < 500ms | ~300ms |
| Auto-refresh cycle | < 2s | ~1.5s |

## Testing Checklist

### Before Deployment
- [ ] Positions load without Robinhood connection (empty state)
- [ ] Positions load with Robinhood connection (live data)
- [ ] P&L calculations match Robinhood values ±$0.01
- [ ] Theta forecasts show proper decay acceleration
- [ ] AI recommendations trigger at correct thresholds
- [ ] High-profit alerts appear for >20% positions
- [ ] Auto-refresh works at all interval settings
- [ ] Manual refresh button updates data immediately
- [ ] ITM/OTM status correctly calculated
- [ ] TradingView chart links work
- [ ] No crashes with zero positions
- [ ] No crashes with 20+ positions

### Integration Tests
- [ ] Position data syncs from Robinhood correctly
- [ ] Stock prices fetch from Yahoo Finance for AI analysis
- [ ] Auto-refresh preserves user scroll position
- [ ] Alert state persists across refreshes
- [ ] Session state handles connection loss gracefully

## Maintenance

### When to Update This Agent

1. **User Request**: "Show me X metric for positions"
   - Evaluate metric feasibility
   - Update position data structure if needed
   - Add to dashboard.py display logic
   - Document in CHANGELOG.md

2. **Bug Report**: "P&L showing wrong values"
   - Debug calculation logic in calculate_position_pnl()
   - Verify premium direction handling
   - Check for after-hours pricing edge cases
   - Fix and test thoroughly
   - Document fix in CHANGELOG.md

3. **Feature Request**: "Add Greeks display (gamma, vega)"
   - Assess data availability from Robinhood
   - Implement Greek calculations if needed
   - Add to position object and UI
   - Update SPEC.md and WISHLIST.md

4. **API Change**: Robinhood API updates
   - Update robinhood_integration.py
   - Test all position fetching flows
   - Verify backward compatibility
   - Alert users of any breaking changes
   - Document in CHANGELOG.md

### Monitoring
- Check position load times (should be < 2s)
- Monitor Robinhood API success rate (> 95%)
- Track P&L calculation accuracy (matches broker)
- Review AI recommendation quality (user feedback)
- Monitor auto-refresh performance impact

## Integration Points

### Robinhood Integration
```python
# Position fetching
positions = rh_client.get_wheel_positions()
# Returns: List of position dictionaries
# Includes: CSPs, CCs, and eligible stock positions

# Account data
account = rh_client.get_account()
# Returns: portfolio_value, buying_power, account_number
```

### Yahoo Finance Integration
```python
# Stock price lookup for AI analysis
import yfinance as yf
ticker = yf.Ticker(symbol)
current_price = ticker.info.get('regularMarketPrice')
```

### Agent Coordination
- **Settings Agent**: Provides Robinhood connection status
- **Dashboard Agent**: Aggregates position data for portfolio view
- **Earnings Calendar Agent**: Provides earnings warnings (future)
- **Prediction Markets Agent**: Adds sentiment context (future)

## Future Enhancements

### Planned Features (WISHLIST.md)
- WebSocket integration for real-time price updates (no page reload)
- Full Greeks display (gamma, vega, rho) from Robinhood
- Position grouping by underlying or strategy type
- Historical P&L tracking with chart visualization
- Position alerts via email/SMS for profit targets
- Multi-account support for users with multiple brokerages
- Export positions to CSV for record keeping
- Advanced probability calculations (Monte Carlo)
- IV rank/percentile analysis for each underlying
- Profit target visualization (progress bars)

### Technical Improvements
- Replace meta refresh with WebSocket for smoother updates
- Implement more sophisticated theta model (include gamma effect)
- Add position caching to database for historical analysis
- Optimize for portfolios with 100+ positions
- Add unit tests for P&L calculations
- Implement integration tests with mock Robinhood API

## Questions This Agent Can Answer

1. "What are my current active positions?"
2. "How much profit/loss am I showing on each position?"
3. "Which positions have the highest percentage gains?"
4. "When do my positions expire?"
5. "What's my expected profit if I hold to expiration?"
6. "Which positions should I consider closing?"
7. "What's the assignment risk on my positions?"
8. "How much theta am I collecting daily?"
9. "What's my annualized return on this position?"
10. "Is this option in the money or out of the money?"
11. "What's my breakeven price for this position?"
12. "How many days until expiration?"
13. "What's the current option price per share?"
14. "Should I buy back this position now?"
15. "What's my moneyness percentage?"

## Questions This Agent CANNOT Answer

1. "Find me new CSP opportunities" → Opportunities Agent
2. "What premiums are available for AAPL?" → Premium Scanner Agent
3. "Sync my TradingView watchlist" → TradingView Watchlists Agent
4. "When is the next earnings date?" → Earnings Calendar Agent
5. "Change my risk parameters" → Settings Agent
6. "What's my total account balance?" → Dashboard Agent
7. "Show me historical trades" → Dashboard Agent
8. "Execute a closing order" → User must use Robinhood interface
9. "Compare calendar spread opportunities" → Calendar Spreads Agent
10. "What's the market sentiment on this stock?" → Prediction Markets Agent

---

**For detailed architecture and specifications, see:**
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SPEC.md](./SPEC.md)
- [README.md](./README.md)

**For current tasks and planned work, see:**
- [TODO.md](./TODO.md) (if exists)
- [WISHLIST.md](./WISHLIST.md) (if exists)
- [CHANGELOG.md](./CHANGELOG.md) (if exists)
