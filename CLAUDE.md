# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**AVA (Advanced Options Trading Platform)** - A comprehensive Streamlit-based trading dashboard for wheel strategy options trading (cash-secured puts and covered calls) with AI-powered analysis, real-time data synchronization, and multi-agent architecture.

The platform integrates with Robinhood, TradingView, and various prediction markets (Kalshi) to provide intelligent trading recommendations, position management, and risk analysis.

## Running the Application

### Start the Dashboard
```bash
# Windows
run_dashboard.bat

# Linux/Mac
streamlit run dashboard.py
```

The dashboard will open at `http://localhost:8501`

### Database Setup
The application uses PostgreSQL. Schema files are located in:
- `database_schema.sql` - Main options trading schema
- `src/xtrades_schema.sql` - XTrades integration
- `src/kalshi_schema.sql` - Kalshi prediction markets
- `src/analytics_schema.sql` - Analytics and performance tracking
- `src/ava/schema.sql` - AVA chatbot and conversation memory
- `src/supply_demand_schema.sql` - Supply/demand zone analysis

### Testing
```bash
# Run specific test files
python test_ai_agent_query.py
python test_ava_comprehensive_chatbot.py
python test_comprehensive_integration_live.py

# Test specific features
python test_positions_import.py
python test_xtrades_complete.py
python test_kalshi_auth.py
```

### Background Services
```bash
# Sync TradingView watchlists
python src/tradingview_api_sync.py

# Sync stock data daily
python sync_database_stocks_daily.py

# XTrades monitoring
python start_xtrades_monitor.py

# Kalshi real-time price sync
python sync_kalshi_prices_realtime.py

# NFL data pipeline
python src/nfl_realtime_sync.py
```

## Architecture

### Multi-Agent System
The platform uses an agent-based architecture for different responsibilities:

**Runtime Agents** (`src/agents/runtime/`):
- `market_data_agent.py` - Real-time market data monitoring
- `wheel_strategy_agent.py` - Options strategy analysis and recommendations
- `risk_management_agent.py` - Portfolio risk assessment
- `alert_agent.py` - Price alerts and notifications

**AI Research Agents** (`src/agents/ai_research/`):
- `fundamental_agent.py` - Fundamental analysis
- `technical_agent.py` - Technical indicators and charting
- `sentiment_agent.py` - News and sentiment analysis
- `options_agent.py` - Options-specific analysis
- `orchestrator.py` - Coordinates multi-agent research

**AVA Autonomous Agent** (`src/ava/`):
- `autonomous_agent.py` - Self-directed trading assistant
- `research_agent.py` - Deep research capabilities
- `webhook_server.py` - External integrations

### Page Structure
The dashboard is organized into modular pages (all in root directory):
- `dashboard.py` - Main entry point with navigation
- `positions_page_improved.py` - Active position management
- `comprehensive_strategy_page.py` - Strategy analysis hub
- `ai_options_agent_page.py` - AI-powered recommendations
- `options_analysis_page.py` - Detailed options analysis
- `calendar_spreads_page.py` - Calendar spread opportunities
- `prediction_markets_page.py` - Kalshi integration
- `kalshi_nfl_markets_page.py` - NFL prediction markets
- `xtrades_watchlists_page.py` - XTrades alert monitoring
- `supply_demand_zones_page.py` - Supply/demand analysis
- `ava_chatbot_page.py` - Conversational AI interface

### Core Services (`src/`)
- `robinhood_integration.py` - Robinhood API integration with rate limiting
- `tradingview_api_sync.py` - TradingView watchlist synchronization
- `enhanced_options_fetcher.py` - Options chain data fetching
- `csp_opportunities_finder.py` - Cash-secured put scanner
- `ai_trade_analyzer.py` - AI-powered trade analysis
- `config_manager.py` - Centralized configuration system
- `yfinance_utils.py` - Safe Yahoo Finance utilities

### Configuration System
All configuration lives in `config/`:
- `config/default.yaml` - General app settings, database, cache
- `config/pages.yaml` - Page-specific defaults and limits
- `config/features.yaml` - Feature flags and toggles
- `config/services.yaml` - External service configurations

Access configuration:
```python
from src.config_manager import get_config, get_page_config, is_feature_enabled

config = get_config()
db_pool_max = config.get("database.pool_max", 10)
page_config = get_page_config("ai_options_agent")
if is_feature_enabled("enable_ai_reasoning"):
    # Feature is enabled
```

Override with environment variables using `MAGNUS_SECTION_KEY` pattern:
```bash
export MAGNUS_DATABASE_POOL_MAX=20
export MAGNUS_FEATURES_ENABLE_DEBUG_MODE=true
```

### Data Layer Architecture
The platform uses a centralized data layer pattern:
- **Database Managers**: Each domain has a dedicated manager class (e.g., `TradingViewDBManager`, `KalshiDBManager`)
- **Connection Pooling**: PostgreSQL connections are pooled for efficiency
- **Caching**: Redis for frequently accessed data (TTL configured in `config/default.yaml`)
- **Real-time Sync**: Background services keep data fresh

## Critical Development Policies

### NO DUMMY DATA POLICY ⚠️
**CRITICAL**: This project MUST NEVER contain dummy, fake, sample, or test data.

❌ **NEVER**:
- Hardcoded fake balances (`current_balance = 100000`)
- Test trades in database (fake NVDA trades)
- Mock/dummy API returns
- Default values that look like real data

✅ **ALWAYS**:
- Check if data exists before displaying
- Show empty states: "Connect to Robinhood to see data"
- Use `0`, `None`, `[]`, or `{}` as defaults
- Pull real data from APIs
- Let users manually enter their own real data

See `NO_DUMMY_DATA_POLICY.md` for complete details.

### Feature Development Pattern
Each feature follows a standard structure in `features/`:
```
features/
  feature_name/
    README.md        - User-facing documentation
    ARCHITECTURE.md  - Technical architecture
    SPEC.md         - Detailed specification
    WISHLIST.md     - Enhancement ideas
    AGENT.md        - Agent-specific instructions
    TODO.md         - Task tracking
    CHANGELOG.md    - Version history
```

### Database Best Practices
1. **Schema First**: All schema changes start with SQL files, not code
2. **Migrations**: Document schema changes in feature changelogs
3. **Indexing**: Add indexes for frequently queried columns
4. **JSONB for Flexibility**: Use JSONB columns for extensible metadata
5. **Connection Pooling**: Always use pooled connections from managers

### AI/LLM Integration Patterns
The platform integrates multiple AI systems:

**Local Models** (Free):
- ChromaDB for vector storage and RAG
- Sentence transformers for embeddings
- Local reasoning via `src/ai/` modules

**External APIs** (Configured in `.env`):
- Claude API for advanced reasoning
- DeepSeek for cost-effective inference
- HuggingFace for specific models

**RAG System** (`src/rag/`):
- `embedding_pipeline.py` - Document embedding
- `rag_query_engine.py` - Query processing
- `recommendation_tracker.py` - Learning from outcomes

## Common Development Tasks

### Adding a New Page
1. Create `new_feature_page.py` in root directory
2. Import and integrate in `dashboard.py` navigation
3. Add page config to `config/pages.yaml`
4. Create feature documentation in `features/new_feature/`
5. Update navigation labels and icons

### Adding a New Database Table
1. Create or update schema file in `src/`
2. Add migration SQL in feature changelog
3. Create database manager class if needed
4. Update `DATABASE_SCHEMA.md` documentation
5. Add indexes for query performance

### Integrating a New Data Source
1. Create service class in `src/` (e.g., `new_source_integration.py`)
2. Add configuration to `config/services.yaml`
3. Implement rate limiting and error handling
4. Add caching layer via Redis
5. Create background sync service if needed
6. Document in appropriate feature README

### Working with Robinhood API
- Use `src/robinhood_integration.py` or `src/robinhood_rate_limited.py`
- Rate limits are enforced (60 requests/minute default)
- MFA is handled via environment variables (`ROBINHOOD_MFA_SECRET`)
- Always check connection before API calls
- Cache responses when appropriate

### TradingView Integration
- Session management via `src/get_tradingview_session.py`
- Watchlist sync: `src/tradingview_api_sync.py`
- Auto-refresh handles session expiration
- Supports multiple watchlists
- Database storage in `tradingview_watchlists` table

## File Organization

### Root Directory
- Main entry point: `dashboard.py`
- All page files: `*_page.py`, `*_page_*.py`
- Batch scripts: `run_*.bat`, `sync_*.py`
- Test files: `test_*.py`, `check_*.py`
- Documentation: `*.md` files

### `src/` Directory Structure
```
src/
  agents/          - Multi-agent systems
    runtime/       - Real-time trading agents
    ai_research/   - Research and analysis agents
  ai/              - AI/ML models and utilities
  ai_options_agent/ - Specialized options analysis
  analytics/       - Performance analytics
  api/             - FastAPI endpoints
  ava/             - AVA chatbot and autonomous agent
  components/      - Reusable UI components
  data/            - Data processing utilities
  kalshi*/         - Kalshi prediction market integration
  legion/          - Task management and QA system
  mfa/             - Multi-factor authentication
  notifications/   - Alert and notification services
  options_analysis/ - Options-specific analysis
  prediction_agent/ - Prediction market analysis
  qa/              - QA automation and testing
  rag/             - RAG system for AI learning
  services/        - Shared service layers
  strategies/      - Trading strategy implementations
  xtrades_monitor/ - XTrades alert monitoring
  zone_*/          - Supply/demand zone analysis
```

### Documentation Organization
- `docs/` - Comprehensive technical documentation
- `features/` - Feature-specific documentation
- Root `*.md` files - High-level guides and status

## Environment Variables

Required variables (`.env` file):
```bash
# Database
DB_HOST=localhost
DB_PORT=5432
DB_NAME=trading
DB_USER=postgres
DB_PASSWORD=your_password

# Robinhood (Optional)
ROBINHOOD_USERNAME=your@email.com
ROBINHOOD_PASSWORD=your_password
ROBINHOOD_MFA_SECRET=your_mfa_secret

# TradingView (Optional)
TRADINGVIEW_USERNAME=your@email.com
TRADINGVIEW_PASSWORD=your_password
TRADINGVIEW_SESSION_ID=auto_generated

# Kalshi (Optional)
KALSHI_EMAIL=your@email.com
KALSHI_PASSWORD=your_password

# Redis
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0

# AI Services (Optional)
CLAUDE_API_KEY=your_key
DEEPSEEK_API_KEY=your_key
HUGGINGFACE_TOKEN=your_token
```

## Dependencies

Core frameworks:
- **Streamlit** - Web UI framework
- **PostgreSQL** - Primary database
- **Redis** - Caching layer
- **Pandas** - Data manipulation
- **Plotly** - Interactive charts

AI/ML stack:
- **ChromaDB** - Vector database
- **Sentence Transformers** - Embeddings
- **Transformers** - HuggingFace models
- **Scikit-learn** - ML algorithms

Data sources:
- **yfinance** - Yahoo Finance data
- **robin-stocks** - Robinhood API
- **Selenium/Playwright** - Web automation
- **BeautifulSoup** - Web scraping

See `requirements.txt` for complete dependency list.

## Code Quality Standards

### Python Style
- Follow PEP 8 conventions
- Use type hints where beneficial
- Document complex functions with docstrings
- Keep functions focused and small

### Error Handling
- Always handle API failures gracefully
- Show user-friendly error messages
- Log errors for debugging
- Use try-except for external API calls

### Performance Considerations
- Cache expensive database queries (Redis)
- Use connection pooling for database
- Implement pagination for large datasets
- Lazy load data in Streamlit (use st.cache_data)

### Security Best Practices
- Never commit `.env` files (in `.gitignore`)
- Use environment variables for secrets
- Validate all user inputs
- Sanitize data before database insertion
- Use parameterized queries (prevent SQL injection)

## Streamlit-Specific Patterns

### State Management
```python
# Initialize session state
if 'key' not in st.session_state:
    st.session_state.key = default_value

# Update state
st.session_state.key = new_value
```

### Caching
```python
@st.cache_data(ttl=300)  # 5-minute cache
def fetch_expensive_data():
    # Expensive operation
    return data

@st.cache_resource
def get_database_connection():
    # Singleton resources
    return connection
```

### Layout Patterns
- Use `st.columns()` for side-by-side layouts
- Use `st.expander()` for collapsible sections
- Use `st.tabs()` for multi-section views
- Use `st.sidebar` for navigation and filters

## Testing Strategy

### Test Organization
- Unit tests: `test_*.py` in root
- Integration tests: `test_*_integration.py`
- Feature tests: Within feature directories
- End-to-end: `test_comprehensive_*.py`

### Critical Test Areas
1. **Database Operations**: Test all CRUD operations
2. **API Integrations**: Mock external APIs
3. **Data Processing**: Validate calculations
4. **UI Components**: Test Streamlit rendering
5. **Background Services**: Test sync services

## Troubleshooting

### Database Connection Issues
```bash
# Test PostgreSQL connection
psql -h localhost -U postgres -d trading

# Check if database exists
psql -l | grep trading
```

### Session/Cache Issues
```bash
# Clear Streamlit cache
# In browser: Press 'C' then 'Clear cache'

# Clear Redis cache
redis-cli FLUSHDB
```

### TradingView Session Expired
```bash
# Re-authenticate
python src/get_tradingview_session.py
# Updates TRADINGVIEW_SESSION_ID in .env automatically
```

### Robinhood Rate Limiting
- Check logs for rate limit errors
- Increase delays in `src/robinhood_rate_limited.py`
- Reduce concurrent requests

## Additional Resources

### Documentation
- Main README: `README.md`
- Database Schema: `DATABASE_SCHEMA.md`
- Quick Start: `QUICK_START.md`
- System Architecture: `system_architecture.md`
- Feature Index: `features/INDEX.md` (if exists)

### Getting Help
- Check feature-specific README in `features/`
- Review existing test files for examples
- Search documentation files for specific topics
- Review recent git commits for implementation patterns

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code improvements
- `docs/description` - Documentation updates

### Commit Messages
Follow the format:
```
Type: Brief description

Detailed explanation if needed

🤖 Generated with [Claude Code](https://claude.com/claude-code)

Co-Authored-By: Claude <noreply@anthropic.com>
```

Types: `feat`, `fix`, `refactor`, `docs`, `test`, `chore`

### Before Committing
1. Test your changes
2. Update relevant documentation
3. Follow NO_DUMMY_DATA_POLICY
4. Ensure code follows style guidelines
5. Update feature CHANGELOG if applicable
