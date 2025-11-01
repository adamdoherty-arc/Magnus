# Changelog

All notable changes to the Prediction Markets feature will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Planned
- Portfolio tracking for prediction market positions
- Historical performance tracking per category
- Custom alert thresholds for high-score markets
- Market comparison tools (side-by-side analysis)
- Expected value calculator with custom probabilities
- Integration with external prediction market platforms
- Social sentiment analysis for market validation
- Machine learning price prediction models

## [1.1.0] - 2025-10-30

### Fixed
- **CRITICAL: Cache TTL Increased**
  - Increased cache time-to-live to avoid Kalshi rate limiting
  - Changed from 15-minute to 60-minute cache duration
  - Prevents API rate limit errors (100 requests/minute)
  - Improved reliability during high-frequency refreshes
  - Better user experience with fewer rate limit warnings

## [1.0.1] - 2025-10-29

### Fixed
- **Streamlit Caching Error**
  - Fixed caching decorator issues
  - Resolved function signature problems
  - Corrected data serialization for cache
  - Eliminated random cache-related crashes

## [1.0.0] - 2025-10-29

### Added
- **AI-Powered Market Scoring System**
  - Quantitative analysis scoring 0-100 for each market
  - Multi-factor evaluation algorithm
  - Automated recommendation engine (Yes/No/Skip/Maybe)
  - Risk level assessment (Low/Medium/High)
- **Comprehensive Market Coverage**
  - **Politics**: Elections, legislation, appointments
  - **Sports**: NFL, NBA, MLB, MMA, Tennis, Golf
  - **Economics**: Fed rates, CPI, GDP, employment
  - **Crypto**: Bitcoin price levels, ETF approvals
  - **Companies**: Earnings, M&A, product launches
  - **Tech & Science**: AI milestones, space launches
  - **Climate**: Temperature records, weather events
  - **World**: International events, geopolitics
- **Real-Time Market Data Integration**
  - Kalshi API integration (100 requests/minute)
  - Current Yes/No pricing from orderbook
  - 24-hour trading volume tracking
  - Open interest metrics
  - Bid-ask spread analysis
  - Days to market close calculation
  - Contract resolution date tracking
- **Intelligent Filtering System**
  - Category filter (All, Politics, Sports, Economics, etc.)
  - Minimum AI score threshold slider (default: 60)
  - Maximum days to close input (default: 90)
  - High-quality market identification (Score >75)
  - Real-time filter application
- **AI Scoring Algorithm**
  - **Liquidity Score**: 24h volume and spread quality
  - **Time Value Score**: Days to close optimization
  - **Risk-Reward Score**: Pricing efficiency analysis
  - **Spread Quality Score**: Bid-ask tightness
  - Composite scoring (0-100 scale)
- **Market Card Display**
  - Color-coded emoji indicators (🔥⭐👍👎)
  - AI score prominently displayed
  - Category and days to close
  - Market title and description
  - Expandable detailed view
- **Detailed Market Information**
  - **Pricing Section**: Yes/No contract prices
  - **Volume & Liquidity**: 24h volume, spread percentage
  - **Recommendation**: Position (Yes/No/Skip/Maybe)
  - **AI Analysis**: Detailed reasoning and factors
  - **Expected Value**: Positive/negative percentage
  - **Action Buttons**: View on Robinhood/Kalshi
  - **Market Details**: Ticker, category, close date, description
- **Summary Metrics Dashboard**
  - Total markets fetched count
  - High-quality markets (>75 score)
  - Average score across filtered results
  - Currently showing count
- **Score Interpretation Guide**
  - 85-100 (Fire): Exceptional opportunity
  - 75-84 (Star): High quality
  - 60-74 (Thumbs Up): Worth considering
  - <60 (Thumbs Down): Skip
- **Position Recommendations**
  - **Yes**: Buy Yes contracts (market underpriced)
  - **No**: Buy No contracts (market overpriced)
  - **Maybe**: Consider with manual analysis
  - **Skip**: Avoid (poor fundamentals)
- **External Platform Integration**
  - Direct links to Robinhood app
  - Direct links to Kalshi market pages
  - Opens in new tabs for parallel analysis
  - Platform comparison capability
- **Market Education**
  - Binary outcome contract explanation
  - Pricing mechanics tutorial
  - Trading strategies documentation
  - Risk factors disclosure
- **Caching System**
  - 60-minute cache TTL to avoid rate limits
  - Automatic cache invalidation
  - Manual refresh capability
  - Last updated timestamp display
- **No OpenAI Dependency**
  - Pure quantitative analysis
  - Rule-based recommendation engine
  - No external AI API calls required
  - Fully deterministic scoring

### Technical Implementation
- **Kalshi API Integration**
  - RESTful API calls to `api.elections.kalshi.com`
  - Authentication-free public data access
  - JSON response parsing
  - Error handling for API failures
- **Scoring Engine**
  - Liquidity factor (volume-based)
  - Time value factor (days to close)
  - Risk-reward calculation (price efficiency)
  - Spread quality measurement
  - Weighted composite scoring
- **Data Flow**
  1. Fetch markets from Kalshi API
  2. Parse orderbook data
  3. Calculate scoring factors
  4. Generate recommendations
  5. Apply user filters
  6. Render market cards
- **Performance**
  - API call latency: 1-2 seconds
  - Caching reduces repeated calls
  - 60-minute cache duration
  - Real-time filtering (no API calls)
  - Efficient data structures
- **User Interface**
  - Streamlit-based responsive design
  - Expandable market cards
  - Color-coded visual hierarchy
  - Filter controls at top
  - Summary metrics row
  - Scrollable market list

### Risk Disclosures
- **Market Risks**: Low liquidity, wide spreads, information asymmetry
- **Operational Risks**: Settlement disputes, platform issues, regulatory changes
- **Behavioral Risks**: Overconfidence, recency bias, confirmation bias
- Maximum loss: Purchase price of contract
- No margin or leveraged trading
- Cash-settled binary outcomes

### Educational Resources
- Prediction market theory explanation
- Trading strategies guide (4 strategies)
- Risk management best practices
- FAQ with 10+ common questions
- CFTC regulatory guidance links
- Platform comparison (Robinhood vs Kalshi)

### Use Cases
- **Political Betting**: Election outcomes, legislation
- **Sports Wagering**: Game outcomes, player props
- **Economic Forecasting**: Fed decisions, macro events
- **Event Trading**: Binary outcome speculation
- **Portfolio Hedging**: Tail risk protection

### Configuration
- Default min score: 60
- Default max days: 90
- Cache TTL: 60 minutes (3600 seconds)
- API rate limit: 100 requests/minute
- Default category: All

[1.1.0]: https://github.com/yourusername/WheelStrategy/compare/prediction-markets-v1.0.1...prediction-markets-v1.1.0
[1.0.1]: https://github.com/yourusername/WheelStrategy/compare/prediction-markets-v1.0.0...prediction-markets-v1.0.1
[1.0.0]: https://github.com/yourusername/WheelStrategy/releases/tag/prediction-markets-v1.0.0
