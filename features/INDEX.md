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

Each feature includes four types of documentation:

1. **README.md** - User-focused guide with step-by-step instructions, screenshots, and troubleshooting
2. **ARCHITECTURE.md** - Technical implementation details for developers
3. **SPEC.md** - Detailed feature specifications and requirements
4. **WISHLIST.md** - Planned enhancements and future features

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


### 9. Calendar Spreads

**AI-Powered Time Decay Profit Finder**

Discover optimal calendar spread opportunities using advanced AI scoring. Profit from time decay differentials with limited risk.

- [User Guide](./calendar_spreads/README.md) - Understanding calendar spreads
- [Architecture](./calendar_spreads/ARCHITECTURE.md) - AI scoring engine & Greeks calculations
- [Specifications](./calendar_spreads/SPEC.md) - Max profit/loss formulas & requirements
- [Wishlist](./calendar_spreads/WISHLIST.md) - Auto-roll, backtesting, advanced features

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

| Feature | Data Source | Real-time | AI Analysis | Export |
|---------|-------------|-----------|-------------|--------|
| Dashboard | Robinhood + DB | Yes | Yes | CSV |
| Opportunities | yfinance + DB | Yes | Yes | CSV |
| Positions | Robinhood | Yes | Yes | CSV |
| Premium Scanner | yfinance | Yes | Score-based | CSV |
| TradingView Watchlists | TradingView API | Yes | No | CSV |
| Database Scan | PostgreSQL | No | No | CSV |
| Earnings Calendar | Robinhood + APIs | Daily | No | CSV |
| Settings | .env + DB | N/A | N/A | N/A |

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

## Version Information

- **Current Version**: 1.0.0
- **Last Updated**: 2025-10-28
- **Features**: 8 navigation pages
- **Documentation Pages**: 32 (4 per feature)

---

**Happy Trading!**

For questions or contributions, see [CONTRIBUTING.md](../CONTRIBUTING.md)
