# Magnus Trading Platform - Feature Documentation Index

Welcome to the Magnus Trading Platform feature documentation. This index provides links to detailed documentation for all 8 navigation features.

## Navigation Features

Magnus includes 8 comprehensive features for managing your options trading strategies. Each feature has detailed documentation including usage guides, architecture details, specifications, and future enhancements.

### 1. Dashboard

**Main portfolio overview and performance tracking**

The Dashboard is your command center, providing real-time portfolio metrics, trade history tracking, balance forecasts, and AI-powered analysis.

- [User Guide](./dashboard/README.md) - How to use the Dashboard
- [Architecture](./dashboard/ARCHITECTURE.md) - Technical implementation details
- [Specifications](./dashboard/SPEC.md) - Detailed feature specifications
- [Wishlist](./dashboard/WISHLIST.md) - Planned enhancements

**Key Features:**
- Real-time account balance and buying power
- Trade history with P&L tracking
- Balance forecast timeline (best/expected/worst case)
- Individual position forecasts
- Theta decay profit projections
- AI trade analysis and recommendations

---

### 2. Opportunities

**Discover new trading opportunities**

Find high-quality cash-secured put and covered call opportunities with AI-powered scoring and risk assessment.

- [User Guide](./opportunities/README.md) - How to find opportunities
- [Architecture](./opportunities/ARCHITECTURE.md) - Technical implementation
- [Specifications](./opportunities/SPEC.md) - Feature specifications
- [Wishlist](./opportunities/WISHLIST.md) - Future enhancements

**Key Features:**
- Cash-secured put opportunity scanner
- Covered call finder for existing positions
- Score-based ranking system
- Risk assessment for each opportunity
- Customizable filters
- Real-time market data integration

---

### 3. Positions

**Manage active options positions**

Track and manage your active options positions with real-time updates, profit/loss tracking, and AI-powered recommendations.

- [User Guide](./positions/README.md) - How to manage positions
- [Architecture](./positions/ARCHITECTURE.md) - Technical design
- [Specifications](./positions/SPEC.md) - Feature details
- [Wishlist](./positions/WISHLIST.md) - Planned features

**Key Features:**
- Real-time P&L tracking
- Theta decay forecasting (daily projections)
- AI trade analysis with actionable recommendations
- Live option price monitoring
- Assignment probability calculations
- Auto-refresh capabilities
- Position-specific risk metrics

---

### 4. Premium Scanner

**Advanced options premium screening**

Scan for high-premium options opportunities with multi-expiration support and advanced filtering capabilities.

- [User Guide](./premium_scanner/README.md) - How to use the scanner
- [Architecture](./premium_scanner/ARCHITECTURE.md) - Implementation details
- [Specifications](./premium_scanner/SPEC.md) - Scanner specifications
- [Wishlist](./premium_scanner/WISHLIST.md) - Future enhancements

**Key Features:**
- Multi-expiration scanning (7d, 14d, 30d, 45d DTE)
- Volatility filters (IV levels)
- Return calculations (monthly & annualized)
- Volume screening for liquidity
- Price range filters
- Premium percentage thresholds
- Sortable results table

---

### 5. TradingView Watchlists

**Sync and analyze TradingView watchlists**

Automatically synchronize your TradingView watchlists and perform premium analysis on all symbols.

- [User Guide](./tradingview_watchlists/README.md) - Setup and usage
- [Architecture](./tradingview_watchlists/ARCHITECTURE.md) - Integration design
- [Specifications](./tradingview_watchlists/SPEC.md) - Feature specifications
- [Wishlist](./tradingview_watchlists/WISHLIST.md) - Planned improvements

**Key Features:**
- Automatic watchlist synchronization
- Auto-refresh session management
- Support for multiple watchlists
- Complete premium analysis
- Symbol import/export
- Real-time price updates
- Earnings date integration

---

### 6. Database Scan

**Manage and scan your stock database**

Add stocks to your PostgreSQL database and scan for the best premium opportunities across all stored symbols.

- [User Guide](./database_scan/README.md) - How to use database scanning
- [Architecture](./database_scan/ARCHITECTURE.md) - Database design
- [Specifications](./database_scan/SPEC.md) - Feature details
- [Wishlist](./database_scan/WISHLIST.md) - Future features

**Key Features:**
- Bulk stock addition to database
- Comprehensive premium scanning
- Analytics by sector and price range
- Historical data management
- Symbol validation
- Duplicate detection
- Database optimization tools

---

### 7. Earnings Calendar

**Track upcoming earnings dates**

Monitor earnings dates for stocks in your watchlists and positions to avoid unwanted risk during earnings events.

- [User Guide](./earnings_calendar/README.md) - Earnings tracking guide
- [Architecture](./earnings_calendar/ARCHITECTURE.md) - System design
- [Specifications](./earnings_calendar/SPEC.md) - Feature specifications
- [Wishlist](./earnings_calendar/WISHLIST.md) - Planned enhancements

**Key Features:**
- Upcoming earnings date tracking
- Automatic risk warnings for positions
- Integration with position management
- Real-time earnings data sync
- Earnings date visualization
- Historical earnings data
- Notification system

---

### 8. Settings

**Configure the platform**

Manage all platform settings including Robinhood integration, strategy parameters, and system configuration.

- [User Guide](./settings/README.md) - Configuration guide
- [Architecture](./settings/ARCHITECTURE.md) - Settings management
- [Specifications](./settings/SPEC.md) - Configuration options
- [Wishlist](./settings/WISHLIST.md) - Future settings

**Key Features:**
- Robinhood account integration
- Strategy parameters (max price, DTE, risk limits)
- Alert settings and notifications
- TradingView API configuration
- Database connection management
- Security settings
- Display preferences

---

## Documentation Structure

Each feature includes **seven types of documentation**:

1. **README.md** - User-focused guide with step-by-step instructions, screenshots, and troubleshooting
2. **ARCHITECTURE.md** - Technical implementation details for developers
3. **SPEC.md** - Detailed feature specifications and requirements
4. **WISHLIST.md** - Planned enhancements and future features
5. **AGENT.md** - AI agent documentation: capabilities, responsibilities, communication patterns
6. **TODO.md** - Current tasks, priorities, known issues, and technical debt
7. **CHANGELOG.md** - Version history and notable changes following Keep a Changelog format

## Additional Resources

### Project Documentation

- [Main README](../README.md) - Project overview and quick start
- [Installation Guide](../README.md#installation) - Setup instructions
- [Contributing Guide](../CONTRIBUTING.md) - Contribution guidelines

### Technical Documentation

- [Database Schema](../DATABASE_SCHEMA.md) - Complete database documentation
- [API Specifications](../api_specifications.md) - API endpoint details
- [System Architecture](../system_architecture.md) - Overall system design

### Setup Guides

- [PostgreSQL Setup](../POSTGRES_SETUP.md) - Database configuration
- [Robinhood Setup](../ROBINHOOD_SETUP.md) - Broker integration
- [TradingView Sync](../TRADINGVIEW_SYNC_README.md) - Watchlist integration

### Policies and Standards

- [NO_DUMMY_DATA_POLICY](../NO_DUMMY_DATA_POLICY.md) - Critical development policy
- [Options Trading Guide](../README_OPTIONS_GUIDE.md) - Educational resource

### Multi-Agent System

- [MAIN_AGENT.md](../MAIN_AGENT.md) - Main orchestrator agent documentation
- [Feature Agents](./dashboard/AGENT.md) - Each feature has a specialized agent (AGENT.md in each folder)


### 9. Calendar Spreads

**AI-Powered Time Decay Profit Finder**

Discover optimal calendar spread opportunities using advanced AI scoring. Profit from time decay differentials with limited risk.

- [User Guide](./calendar_spreads/README.md) - Understanding calendar spreads
- [Architecture](./calendar_spreads/ARCHITECTURE.md) - AI scoring engine & Greeks calculations
- [Specifications](./calendar_spreads/SPEC.md) - Max profit/loss formulas & requirements
- [Wishlist](./calendar_spreads/WISHLIST.md) - Auto-roll, backtesting, advanced features
- [Agent](./calendar_spreads/AGENT.md) - Agent capabilities & coordination
- [TODO](./calendar_spreads/TODO.md) - Current tasks & priorities
- [Changelog](./calendar_spreads/CHANGELOG.md) - Version history

**Key Features:**
- TradingView watchlist integration
- AI-powered spread scoring (0-100)
- Max profit/loss calculations
- Theta differential analysis
- Implied volatility filtering (<30% ideal)
- ATM strike selection
- Optimal timing (30-45 DTE short, 60-90 DTE long)
- Step-by-step entry instructions
- Score distribution visualization

**Strategy Focus:**
- Profit from time decay (theta)
- Best in low IV, range-bound markets
- Limited risk (max loss = net debit)
- Neutral market outlook

---

### 10. Prediction Markets

**AI-Powered Event Contract Analysis**

Discover high-quality event contract opportunities from Kalshi with quantitative scoring. Trade on real-world events with defined outcomes.

- [User Guide](./prediction_markets/README.md) - Understanding prediction markets
- [Architecture](./prediction_markets/ARCHITECTURE.md) - Kalshi integration & AI scoring
- [Specifications](./prediction_markets/SPEC.md) - Scoring algorithm & data models
- [Wishlist](./prediction_markets/WISHLIST.md) - Real-time updates, ML scoring, portfolio tracking
- [Agent](./prediction_markets/AGENT.md) - Agent capabilities & communication
- [TODO](./prediction_markets/TODO.md) - Current priorities & technical debt
- [Changelog](./prediction_markets/CHANGELOG.md) - Version history

**Key Features:**
- 8 market categories (Politics, Sports, Economics, Crypto, Companies, Tech, Climate, World)
- AI-powered scoring (0-100) with 4-component analysis
- Liquidity score (volume analysis)
- Time value optimization (7-30 day sweet spot)
- Risk-reward potential calculation
- Spread quality assessment
- Smart position recommendations (Yes/No/Maybe/Skip)
- Detailed reasoning for each market
- Expected value calculations

**Strategy Focus:**
- Event-based trading (binary outcomes)
- Quantitative analysis with AI
- Smart timing (days to close optimization)
- Risk management with spread analysis

---

## Quick Navigation

### By User Type

**New Users:**
1. Start with [Main README](../README.md) for installation
2. Review [Dashboard User Guide](./dashboard/README.md)
3. Set up [Robinhood Integration](./settings/README.md#robinhood-integration)
4. Explore [Opportunities](./opportunities/README.md)

**Active Traders:**
1. [Positions](./positions/README.md) - Manage active trades
2. [Premium Scanner](./premium_scanner/README.md) - Find new opportunities
3. [Earnings Calendar](./earnings_calendar/README.md) - Avoid earnings risk

**Developers:**
1. [Contributing Guide](../CONTRIBUTING.md)
2. Review [ARCHITECTURE.md](./dashboard/ARCHITECTURE.md) files
3. Check [SPEC.md](./dashboard/SPEC.md) for requirements
4. Follow [NO_DUMMY_DATA_POLICY](../NO_DUMMY_DATA_POLICY.md)

### By Task

**Setting Up the Platform:**
- [Installation Guide](../README.md#installation)
- [Database Setup](../POSTGRES_SETUP.md)
- [Settings Configuration](./settings/README.md)

**Finding Trades:**
- [Opportunities Scanner](./opportunities/README.md)
- [Premium Scanner](./premium_scanner/README.md)
- [TradingView Watchlists](./tradingview_watchlists/README.md)

**Managing Positions:**
- [Positions Dashboard](./positions/README.md)
- [Trade History](./dashboard/README.md#trade-history)
- [AI Recommendations](./positions/README.md#ai-analysis)

**Risk Management:**
- [Earnings Calendar](./earnings_calendar/README.md)
- [Position Risk Metrics](./positions/README.md#risk-analysis)
- [Portfolio Forecasts](./dashboard/README.md#balance-forecasts)

## Feature Comparison

| Feature | Data Source | Real-time | AI Analysis | Export | Agent |
|---------|-------------|-----------|-------------|--------|-------|
| Dashboard | Robinhood + DB | Yes | Yes | CSV | [✓](./dashboard/AGENT.md) |
| Opportunities | yfinance + DB | Yes | Yes | CSV | [✓](./opportunities/AGENT.md) |
| Positions | Robinhood | Yes | Yes | CSV | [✓](./positions/AGENT.md) |
| Premium Scanner | yfinance | Yes | Score-based | CSV | [✓](./premium_scanner/AGENT.md) |
| TradingView Watchlists | TradingView API | Yes | No | CSV | [✓](./tradingview_watchlists/AGENT.md) |
| Database Scan | PostgreSQL | No | No | CSV | [✓](./database_scan/AGENT.md) |
| Earnings Calendar | Robinhood + APIs | Daily | No | CSV | [✓](./earnings_calendar/AGENT.md) |
| Calendar Spreads | yfinance + DB | Yes | Yes | CSV | [✓](./calendar_spreads/AGENT.md) |
| Prediction Markets | Kalshi API | Cached (1h) | Yes | CSV | [✓](./prediction_markets/AGENT.md) |
| Settings | .env + DB | N/A | N/A | N/A | [✓](./settings/AGENT.md) |

## Support

### Getting Help

If you need assistance:

1. Check the relevant feature documentation
2. Review [Troubleshooting sections](./dashboard/README.md#troubleshooting)
3. Search [GitHub Issues](https://github.com/yourusername/WheelStrategy/issues)
4. Create a new issue with details

### Feedback

We welcome feedback on documentation:

- Documentation issues: Create a GitHub issue with "docs" label
- Suggestions: Use GitHub Discussions
- Typos/errors: Submit a PR with fixes

## Multi-Agent Architecture

Magnus uses a sophisticated **multi-agent system** where each feature has its own specialized AI agent that maintains context, tracks changes, and coordinates with other agents.

### Main Orchestrator Agent

The [MAIN_AGENT.md](../MAIN_AGENT.md) serves as the central intelligence that:

- **Routes requests** to appropriate feature agents
- **Coordinates multi-feature workflows** (e.g., finding opportunities while avoiding earnings)
- **Maintains platform-wide context** (positions, watchlists, trade history)
- **Ensures data consistency** across all features
- **Monitors system health** and feature dependencies

### Feature-Specific Agents

Each of the 10 features has its own agent documented in `AGENT.md`:

| Feature | Agent Location | Primary Responsibility |
|---------|----------------|------------------------|
| Dashboard | [dashboard/AGENT.md](./dashboard/AGENT.md) | Portfolio visualization & performance tracking |
| Opportunities | [opportunities/AGENT.md](./opportunities/AGENT.md) | Finding new CSP/CC trading opportunities |
| Positions | [positions/AGENT.md](./positions/AGENT.md) | Real-time position tracking & management |
| Premium Scanner | [premium_scanner/AGENT.md](./premium_scanner/AGENT.md) | Multi-expiration options scanning |
| TradingView Watchlists | [tradingview_watchlists/AGENT.md](./tradingview_watchlists/AGENT.md) | Watchlist synchronization & analysis |
| Database Scan | [database_scan/AGENT.md](./database_scan/AGENT.md) | Market-wide database scanning |
| Earnings Calendar | [earnings_calendar/AGENT.md](./earnings_calendar/AGENT.md) | Earnings tracking & risk warnings |
| Calendar Spreads | [calendar_spreads/AGENT.md](./calendar_spreads/AGENT.md) | Time decay spread opportunities |
| Prediction Markets | [prediction_markets/AGENT.md](./prediction_markets/AGENT.md) | Event contract analysis (Kalshi) |
| Settings | [settings/AGENT.md](./settings/AGENT.md) | Platform configuration & auth |

### Agent Communication Protocol

Agents communicate through a structured protocol managed by the Main Agent:

```
User Request → Main Agent
              ↓
      Analyze & Route
              ↓
   Delegate to Feature Agent(s)
              ↓
   Gather cross-feature data if needed
              ↓
   Aggregate responses
              ↓
   Return coordinated result → User
```

### Example Multi-Agent Workflow

**User Request**: "Find the best CSP opportunity from my watchlist avoiding earnings"

```yaml
Workflow:
  1. Main Agent receives request
  2. TradingView Watchlists Agent → Retrieves symbols
  3. Premium Scanner Agent → Scans for high premiums
  4. Earnings Calendar Agent → Filters out earnings risks
  5. Prediction Markets Agent → Adds sentiment scores
  6. Main Agent → Ranks and returns top 5 opportunities
```

### Agent Capabilities

Each `AGENT.md` file documents:

- ✅ **What the agent CAN do** (specific capabilities)
- ❌ **What the agent CANNOT do** (boundaries)
- 🔗 **Dependencies** (other agents, APIs, databases)
- 📡 **Communication patterns** (request/response formats)
- 🎯 **Questions it can answer** (routing guide)
- 🔄 **Data flow** (how information moves)
- ⚠️ **Error handling** (failure scenarios)
- 📊 **Performance metrics** (monitoring targets)

### Change Tracking

Every agent maintains awareness of changes through:

- **TODO.md** - Current priorities and tasks
- **CHANGELOG.md** - Version history and updates
- **WISHLIST.md** - Planned future enhancements

When any feature is updated:
1. Feature agent updates its TODO.md and CHANGELOG.md
2. Main Agent detects the change
3. Dependent features are notified if needed
4. Cross-feature impacts are coordinated

### Benefits of the Multi-Agent System

1. **Separation of Concerns**: Each feature has clear boundaries and responsibilities
2. **Robust Context**: Agents maintain deep knowledge of their domain
3. **Coordinated Workflows**: Complex tasks span multiple features seamlessly
4. **Change Awareness**: All agents stay synchronized with current state
5. **Scalability**: New features can be added as new agents
6. **Maintainability**: Clear documentation of what each component does

### Working with Agents

**For Users:**
- Ask questions naturally - the Main Agent routes to the right feature
- Complex requests automatically coordinate multiple features
- Get consistent, context-aware responses

**For Developers:**
- Consult the appropriate AGENT.md before making changes
- Update TODO.md with new tasks
- Document changes in CHANGELOG.md
- Coordinate with Main Agent for cross-feature impacts

## Version Information

- **Current Version**: 1.0.0
- **Last Updated**: 2025-11-01
- **Features**: 10 navigation pages
- **Documentation Pages**: 70 (7 per feature)
- **Agent System**: Main Orchestrator + 10 Feature Agents

---

## Agent System Quick Reference

### When Working on a Feature

1. **Read** the feature's `AGENT.md` to understand its role
2. **Check** the `TODO.md` for current priorities
3. **Review** the `CHANGELOG.md` for recent changes
4. **Consult** `WISHLIST.md` for future direction
5. **Update** all three when making changes

### When Requesting Changes

1. **Identify** which feature(s) are involved
2. **Check** if multiple agents need coordination
3. **Verify** dependencies in AGENT.md files
4. **Ensure** no conflicts with current TODOs
5. **Document** impacts across features

### When Adding New Features

1. **Create** feature folder with all 7 documentation files
2. **Write** comprehensive AGENT.md
3. **Register** with Main Agent's feature registry
4. **Document** dependencies and integration points
5. **Update** this INDEX.md with the new feature

---

**Happy Trading!**

For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md)

For agent system questions, see [MAIN_AGENT.md](../MAIN_AGENT.md)
