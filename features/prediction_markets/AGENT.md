# Prediction Markets Feature Agent

## Agent Identity

- **Feature Name**: Prediction Markets
- **Agent Version**: 1.0.0
- **Feature Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Owner**: Magnus Platform
- **Status**: Active & Production Ready

## Role & Responsibilities

The Prediction Markets Agent is responsible for **event contract opportunity discovery and analysis**. It serves as a specialized tool for identifying and evaluating prediction market opportunities from Kalshi, using quantitative scoring algorithms to surface the best trading opportunities across politics, sports, economics, and more.

### Primary Responsibilities
1. Fetch active event contracts from Kalshi API
2. Enrich markets with real-time orderbook pricing data
3. Score markets using multi-factor quantitative analysis (0-100)
4. Generate position recommendations (Yes/No/Maybe/Skip)
5. Assess risk levels (Low/Medium/High)
6. Calculate expected value for opportunities
7. Display markets with filtering and sorting capabilities

### Data Sources
- **Kalshi API**: Public market data, orderbooks, volume
- **Streamlit Cache**: 1-hour TTL for market data
- **Internal Algorithms**: Quantitative scoring engine (no external AI API required)

## Feature Capabilities

### What This Agent CAN Do
- Fetch 50-200 markets from Kalshi API
- Score markets based on liquidity, time value, risk-reward, and spread
- Filter by category (Politics, Sports, Economics, etc.)
- Filter by minimum AI score and maximum days to close
- Display top 20 opportunities sorted by score
- Show detailed market information (pricing, volume, analysis)
- Provide links to Robinhood and Kalshi for trade execution
- Calculate expected value and risk-reward ratios
- Generate human-readable analysis reasoning
- Handle rate limiting (100 requests/minute)
- Cache results for fast filter updates

### What This Agent CANNOT Do
- Execute trades (display-only, no trading API integration)
- Access user's brokerage accounts (no authentication)
- Predict actual market outcomes (scores are opportunity quality, not predictions)
- Fetch historical market data (only current/active markets)
- Create custom markets or suggestions
- Provide financial advice (educational/informational only)
- Track user positions (no portfolio integration - yet)
- Send alerts or notifications (planned for future)

## Dependencies

### Required Features
- None (standalone feature)

### Optional Features
- **Dashboard**: Could integrate portfolio tracking (future)
- **Settings**: Could use for Kalshi API credentials (if needed for trading)

### External APIs
- **Kalshi API v2**: Primary data source
  - Base URL: `https://api.elections.kalshi.com/trade-api/v2`
  - Endpoints: `/markets`, `/markets/{ticker}`, `/markets/{ticker}/orderbook`
  - Authentication: Not required for public market data
  - Rate Limit: 100 requests/minute

### Database Tables
- None (currently uses cache only)
- **Future**: `prediction_markets` table for historical analysis

## Key Files & Code

### Main Implementation
- `prediction_markets_page.py`: Lines 1-201 (Main UI and orchestration)
- `src/kalshi_integration.py`: Lines 1-204 (API integration)
- `src/prediction_market_analyzer.py`: Lines 1-277 (Scoring engine)

### Core Functions

**Page Controller:**
```python
def show_prediction_markets():
    """Main function to display prediction markets page"""
    # Lines 13-83 in prediction_markets_page.py

def fetch_and_score_markets(_kalshi, _analyzer, category, limit):
    """Fetch markets from Kalshi and score them"""
    # Lines 85-109 in prediction_markets_page.py
    # Cached for 1 hour (TTL=3600)

def display_market_card(market):
    """Display a single market opportunity card"""
    # Lines 111-193 in prediction_markets_page.py
```

**Kalshi Integration:**
```python
class KalshiIntegration:
    def get_markets(limit, status):
        # Fetch all active markets

    def get_market_details(ticker):
        # Get specific market details

    def get_orderbook(ticker, depth):
        # Get current bid/ask pricing

    def get_enriched_markets(limit):
        # Fetch markets with pricing data
        # Rate limiting: 0.6s sleep every 10 markets

    def get_markets_by_category(category, limit):
        # Filter markets by category
```

**Scoring Engine:**
```python
class PredictionMarketAnalyzer:
    def analyze_market(market):
        # Main scoring function
        # Returns: score, reasoning, recommendation, risk, EV

    def _calculate_liquidity_score(volume, open_interest):
        # 0-100 score based on trading activity

    def _calculate_time_score(days_to_close):
        # 0-100 score, optimal 7-30 days

    def _calculate_risk_reward_score(yes_price, no_price):
        # 0-100 score based on potential returns

    def _calculate_spread_score(bid_ask_spread):
        # 0-100 score, tighter = better

    def _get_recommendation(score, yes_price, liquidity):
        # Generate Yes/No/Maybe/Skip recommendation

    def _generate_reasoning(...):
        # Create human-readable explanation
```

## Current State

### Implemented Features
- Kalshi API integration (markets, orderbooks)
- Multi-factor quantitative scoring (liquidity, time, risk-reward, spread)
- Category filtering (All, Politics, Sports, Economics, etc.)
- Score and days filtering
- Top 20 market display
- Expandable market cards with detailed information
- AI-generated reasoning and recommendations
- Expected value calculations
- Platform links (Robinhood, Kalshi)
- 1-hour caching for rate limit compliance
- Manual refresh capability

### Known Limitations
- No historical data tracking (only current markets)
- No portfolio integration (can't track user positions)
- No real-time updates (manual refresh required)
- No alerts or notifications
- Top 20 display limit (performance optimization)
- Simplified expected value (assumes efficient markets)
- No news or sentiment integration
- No machine learning (rule-based scoring)

### Recent Changes
See [WISHLIST.md](./WISHLIST.md) for planned enhancements.

## Communication Patterns

### Incoming Requests

#### From Main Agent
```yaml
Request: "Show prediction market opportunities"
Response:
  - Navigate to Prediction Markets page
  - Fetch markets from Kalshi
  - Score and display top opportunities
```

#### From User
```yaml
Request: "Find high-scoring Politics markets"
Response:
  - Apply category filter: Politics
  - Apply min score filter: 75
  - Display filtered results
  - Update summary metrics
```

### Outgoing Requests

#### To Kalshi API
```yaml
Request: "Get active markets"
Endpoint: GET /markets?limit=50&status=active
Purpose: Fetch base market data
Expected Response: List of market objects

Request: "Get market orderbook"
Endpoint: GET /markets/{ticker}/orderbook?depth=5
Purpose: Fetch current pricing
Expected Response: Bids/asks for Yes and No
```

#### To Streamlit Cache
```yaml
Request: "Check cached markets"
Purpose: Avoid redundant API calls
Expected Response: Cached market data or cache miss

Request: "Clear cache"
Purpose: Force refresh of market data
Expected Response: Cache cleared, refetch on next request
```

## Data Flow

```
User Opens Prediction Markets Page
       ↓
show_prediction_markets() called
       ↓
Initialize KalshiIntegration & PredictionMarketAnalyzer
       ↓
Check Streamlit cache (@cache_data TTL=3600)
       ↓
   Cache hit? ─→ Yes ─→ Use cached markets
       ↓ No
   fetch_and_score_markets()
       ↓
KalshiIntegration.get_enriched_markets(limit=50)
       ↓
For each market (with rate limiting):
    ↓
    Get orderbook (best bid/ask)
    ↓
    Calculate yes_price, no_price, spread
    ↓
    Calculate days_to_close
    ↓
    PredictionMarketAnalyzer.analyze_market()
        ↓
        Calculate component scores (liquidity, time, risk, spread)
        ↓
        Weighted combination → Overall score
        ↓
        Generate recommendation (Yes/No/Maybe/Skip)
        ↓
        Assess risk level (Low/Medium/High)
        ↓
        Calculate expected value
        ↓
        Generate reasoning
        ↓
    Return analyzed market
       ↓
Cache results (1 hour TTL)
       ↓
Apply user filters (category, score, days)
       ↓
Sort by score (descending)
       ↓
Calculate summary metrics
       ↓
Render top 20 market cards
```

## Error Handling

### Kalshi API Failure
```python
try:
    markets = _kalshi.get_enriched_markets(limit=limit)
except Exception as e:
    st.error(f"Error fetching markets: {e}")
    return []

if not markets:
    st.warning("No markets found. Kalshi API may be unavailable or rate-limited.")
    st.info("💡 Try again in a few moments. Kalshi allows 100 requests per minute.")
    return
```

### Missing Market Data
```python
if not yes_price or not yes_bid or not yes_ask:
    return {
        'ai_score': 0,
        'ai_reasoning': 'Insufficient pricing data',
        'recommended_position': 'Skip',
        'risk_level': 'Unknown',
        'expected_value': 0
    }
```

### Invalid Date Parsing
```python
try:
    close_dt = datetime.fromisoformat(close_date.replace('Z', '+00:00'))
    days_to_close = max(0, (close_dt - datetime.now()).days)
except:
    days_to_close = None
```

### Rate Limit Prevention
```python
for idx, market in enumerate(markets):
    if idx > 0 and idx % 10 == 0:
        print(f"Processed {idx}/{len(markets)} markets...")
        time.sleep(0.6)  # 600ms sleep every 10 markets
```

## Performance Considerations

### Caching Strategy
- Streamlit cache with 1-hour TTL
- Prevents excessive API calls
- Stays within Kalshi rate limits (100/min)
- Fast filter updates (use cached data)
- Manual refresh clears cache

### Rate Limiting
- Kalshi: 100 requests/minute
- Implementation: 0.6s sleep every 10 markets
- 50 markets = ~30 seconds enrichment time
- Complies with rate limits while maintaining UX

### Display Optimization
- Top 20 limit (reduces render time)
- Expandable cards (lazy content loading)
- Pagination not needed (top results most relevant)

### API Efficiency
- Batch market fetch (single request)
- Orderbook depth=5 (minimize data transfer)
- No redundant calls (cache checking)

## Testing Checklist

### Before Deployment
- [ ] Page loads without errors
- [ ] Markets fetch successfully from Kalshi
- [ ] Scoring algorithm produces valid scores (0-100)
- [ ] Filters work correctly (category, score, days)
- [ ] Summary metrics calculate accurately
- [ ] Market cards display all information
- [ ] Links to Robinhood/Kalshi work
- [ ] Cache respects 1-hour TTL
- [ ] Refresh button clears cache and refetches
- [ ] Rate limiting prevents API errors
- [ ] No crashes with empty or invalid data

### Integration Tests
- [ ] Kalshi API connectivity
- [ ] Orderbook data parsing
- [ ] Score calculation accuracy
- [ ] Recommendation logic correctness
- [ ] Filter application
- [ ] Cache hit/miss behavior

## Maintenance

### When to Update This Agent

1. **User Request**: "Add new category or filter"
   - Update filter options in `prediction_markets_page.py`
   - Update category list if needed
   - Document in WISHLIST.md if complex

2. **Bug Report**: "Scores seem incorrect"
   - Debug scoring algorithm in `prediction_market_analyzer.py`
   - Validate component score calculations
   - Fix and document in CHANGELOG.md (when created)

3. **Feature Request**: "Add real-time updates"
   - Assess feasibility (WebSocket support)
   - Add to WISHLIST.md
   - Coordinate with Main Agent if affects other features

4. **API Change**: Kalshi API updates
   - Update `kalshi_integration.py`
   - Test thoroughly
   - Document breaking changes
   - Alert users if behavior changes

### Monitoring
- Check page load times (<40s initial, <2s cached)
- Monitor API success rate (>99%)
- Track rate limit compliance (0 violations)
- Review user feedback for UX improvements
- Validate scoring accuracy against outcomes (future)

## Integration Points

### Kalshi API Integration
- Public market data (no auth)
- Orderbook pricing
- Volume and open interest
- Market metadata

### Streamlit Cache Integration
- 1-hour TTL for market data
- Manual clear on refresh
- Session-specific cache

### Future Integrations
- **Database**: Historical market tracking
- **Robinhood API**: Portfolio sync (if available)
- **Polymarket API**: Cross-platform comparison
- **News APIs**: Sentiment analysis
- **ML Models**: Enhanced scoring

## Future Enhancements

See [WISHLIST.md](./WISHLIST.md) for detailed plans:
- Real-time market updates (WebSocket)
- Historical market analysis
- Portfolio tracking and P&L
- Price alerts and notifications
- Machine learning scoring
- News and sentiment integration
- Arbitrage detection
- Advanced filtering and search
- Mobile-responsive design
- Interactive charts

## Questions This Agent Can Answer

1. "What are the highest-scored prediction markets right now?"
2. "Show me Politics markets with score >75"
3. "Which markets have the best liquidity?"
4. "What's the AI recommendation for this market?"
5. "How many days until this market closes?"
6. "What's the expected value of this opportunity?"
7. "Why did this market get a low score?"
8. "Which categories have the most opportunities?"
9. "What's the average score across all markets?"
10. "How do I trade on these markets?"

## Questions This Agent CANNOT Answer

1. "Will this market outcome be Yes or No?" → Displays opportunity quality, not predictions
2. "What's my P&L on prediction markets?" → No portfolio tracking (yet)
3. "Can you execute this trade for me?" → Display-only, no trading
4. "What were yesterday's market prices?" → No historical data
5. "Alert me when price changes" → No alert system (yet)
6. "Show me markets from last month" → Only active markets
7. "What's the news on this event?" → No news integration (yet)
8. "Backtest this strategy" → No backtesting engine
9. "Which traders are most successful?" → No social features
10. "What's my tax liability?" → No tax reporting

## Scoring Algorithm Details

### Component Weights
```python
{
    'liquidity': 0.30,      # 30% - Trading volume + open interest
    'time_value': 0.25,     # 25% - Days to close (optimal 7-30)
    'risk_reward': 0.25,    # 25% - Potential return calculation
    'spread': 0.20          # 20% - Bid-ask spread tightness
}
```

### Score Ranges
- **85-100**: Exceptional opportunity (🔥)
- **75-84**: High quality (⭐)
- **60-74**: Worth considering (👍)
- **0-59**: Skip (👎)

### Recommendation Logic
```python
if liquidity_score < 40:
    return 'Skip'  # Too illiquid

if score >= 75:
    if yes_price < 0.50:
        return 'Yes'  # Underpriced Yes
    else:
        return 'No'   # Overpriced Yes = buy No

elif score >= 60:
    return 'Maybe'  # Moderate opportunity

else:
    return 'Skip'   # Low quality
```

### Risk Assessment
- **Low**: Score ≥85, high liquidity
- **Medium**: Score 60-84, or score ≥85 with moderate liquidity
- **High**: Score <60, or liquidity <40

## API Usage and Rate Limits

### Kalshi API
- **Rate Limit**: 100 requests/minute
- **Typical Usage**: ~50 requests per refresh (50 markets)
- **Compliance**: 0.6s sleep every 10 markets
- **Cost**: FREE (public market data)

### Request Breakdown
1. Initial markets fetch: 1 request
2. Orderbook per market: 50 requests (for 50 markets)
3. Total: 51 requests per refresh
4. Time: ~30 seconds (with rate limiting)
5. Frequency: User-initiated (manual refresh)

### Cache Benefits
- Reduces API calls by ~99% (most interactions use cache)
- 1-hour TTL balances freshness and efficiency
- Manual refresh available when needed
- Prevents rate limit violations

## Code Organization

### File Structure
```
WheelStrategy/
├── prediction_markets_page.py       # Main UI (201 lines)
├── src/
│   ├── kalshi_integration.py        # API wrapper (204 lines)
│   └── prediction_market_analyzer.py # Scoring engine (277 lines)
└── features/
    └── prediction_markets/
        ├── README.md                 # User guide
        ├── ARCHITECTURE.md           # Technical docs
        ├── SPEC.md                   # Specifications
        ├── WISHLIST.md               # Future plans
        └── AGENT.md                  # This file
```

### Code Quality
- Type hints used throughout
- Docstrings for all public functions
- Error handling for API failures
- Input validation
- Clean separation of concerns (UI, API, Analysis)

---

**For detailed architecture and specifications, see:**
- [ARCHITECTURE.md](./ARCHITECTURE.md)
- [SPEC.md](./SPEC.md)
- [README.md](./README.md)

**For current tasks and planned work, see:**
- [WISHLIST.md](./WISHLIST.md)

**For implementation planning, see:**
- [PREDICTION_MARKETS_IMPLEMENTATION_PLAN.md](../../PREDICTION_MARKETS_IMPLEMENTATION_PLAN.md)
