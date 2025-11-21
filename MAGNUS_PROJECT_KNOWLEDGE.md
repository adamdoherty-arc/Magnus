
# Magnus Project Comprehensive Knowledge

## Project Overview
{
  "name": "Magnus",
  "description": "Advanced Options Trading Dashboard with AI-Powered Analysis",
  "version": "2.0",
  "purpose": "Wheel strategy options trading with comprehensive analysis tools",
  "core_capabilities": [
    "Options trading analysis and tracking",
    "Wheel strategy (CSP and CC) optimization",
    "Real-time market data integration",
    "AI-powered position recommendations",
    "Multi-source data aggregation",
    "Autonomous trading agents",
    "Financial assistant (AVA)",
    "Prediction markets integration",
    "Technical analysis tools"
  ],
  "key_integrations": [
    {
      "name": "Robinhood",
      "purpose": "Live positions and trading execution",
      "status": "Active"
    },
    {
      "name": "TradingView",
      "purpose": "Watchlist sync and chart analysis",
      "status": "Active"
    },
    {
      "name": "XTrades",
      "purpose": "Professional trader signals and alerts",
      "status": "Active"
    },
    {
      "name": "Kalshi",
      "purpose": "Prediction markets and event contracts",
      "status": "Active"
    },
    {
      "name": "ChromaDB",
      "purpose": "RAG knowledge base and semantic search",
      "status": "Active"
    }
  ],
  "architecture": {
    "frontend": "Streamlit multi-page application",
    "backend": "Python services layer",
    "database": "PostgreSQL with multiple schemas",
    "ai_engine": "RAG + LLM (Claude, local models)",
    "deployment": "Local development, containerizable"
  }
}

## Core Features (14 major features)

### Dashboard
**File:** dashboard.py
**Description:** Main overview showing portfolio balance, P&L, and key metrics
**Capabilities:**
  - Portfolio balance tracking with forecast
  - Recent positions summary
  - Quick navigation to all pages
  - Real-time data refresh

### Positions Page
**File:** positions_page_improved.py
**Description:** Live tracking of all open option positions from Robinhood
**Capabilities:**
  - Real-time position data from Robinhood
  - Greeks calculation and display
  - P&L tracking per position
  - Risk metrics and analysis
  - Position action recommendations

### Opportunities Finder
**File:** src/csp_opportunities_finder.py
**Description:** Finds high-quality CSP (Cash-Secured Put) opportunities
**Capabilities:**
  - Scans for optimal CSP opportunities
  - Filters by IV percentile, delta, premium
  - Earnings calendar integration
  - Supply/demand zone analysis
  - Quality scoring algorithm

### Premium Scanner
**File:** premium_scanner_page.py
**Description:** Analyzes premium flows and institutional money
**Capabilities:**
  - Options flow analysis
  - Unusual options activity detection
  - Institutional order tracking
  - Smart money indicators

### AI Options Agent
**File:** ai_options_agent_page.py
**Description:** AI-powered position recommendations
**Capabilities:**
  - Autonomous position analysis
  - Entry/exit recommendations
  - Risk assessment
  - Market context integration
  - Backtesting capabilities

### Comprehensive Strategy
**File:** comprehensive_strategy_page.py
**Description:** Advanced multi-factor analysis for option strategies
**Capabilities:**
  - Technical analysis integration
  - Supply/demand zones
  - Volume profile analysis
  - Smart money indicators
  - Multi-expiration analysis

### Database Scan
**File:** database_scan_page.py
**Description:** Bulk options scanning across entire market
**Capabilities:**
  - Full market options scan
  - Custom filter creation
  - Historical data analysis
  - Pattern recognition

### XTrades Integration
**File:** xtrades_watchlists_page.py
**Description:** Professional trader alerts and signals
**Capabilities:**
  - Real-time alert monitoring
  - Alert filtering and categorization
  - Performance tracking
  - Watchlist synchronization

### Earnings Calendar
**File:** earnings_calendar_page.py
**Description:** Track and avoid earnings events
**Capabilities:**
  - Upcoming earnings tracking
  - Historical earnings moves
  - Integration with positions
  - Risk warning system

### Calendar Spreads
**File:** calendar_spreads_page.py
**Description:** AI-powered calendar spread analysis
**Capabilities:**
  - Calendar spread opportunity finding
  - AI-driven analysis
  - Time decay optimization
  - Greeks analysis for spreads

### Prediction Markets
**File:** prediction_markets_page.py
**Description:** Kalshi prediction markets integration
**Capabilities:**
  - NFL game predictions
  - Multi-sector event contracts
  - AI probability analysis
  - Live odds tracking

### Supply/Demand Zones
**File:** supply_demand_zones_page.py
**Description:** Technical analysis with institutional levels
**Capabilities:**
  - Zone detection algorithm
  - Historical zone performance
  - Integration with options pricing
  - Smart money tracking

### AVA Financial Assistant
**File:** src/ava/ava_nlp_handler.py
**Description:** Natural language financial assistant
**Capabilities:**
  - Natural language queries
  - Portfolio analysis
  - Position recommendations
  - Market insights
  - RAG-powered knowledge retrieval
  - Telegram bot interface

### Task Management
**File:** enhancement_qa_management_page.py
**Description:** Development task tracking with QA
**Capabilities:**
  - Task creation and tracking
  - Multi-agent QA sign-offs
  - Legion project integration
  - Progress monitoring

## Database Architecture
{
  "main_database": "magnus",
  "schemas": [
    {
      "name": "development_tasks",
      "purpose": "Task management and tracking",
      "key_tables": [
        "development_tasks",
        "qa_agent_sign_offs",
        "qa_tasks"
      ]
    },
    {
      "name": "xtrades",
      "purpose": "XTrades alerts and monitoring",
      "key_tables": [
        "alerts",
        "alert_metadata",
        "profiles",
        "watchlists"
      ]
    },
    {
      "name": "earnings",
      "purpose": "Earnings calendar and history",
      "key_tables": [
        "earnings_calendar",
        "earnings_history"
      ]
    },
    {
      "name": "kalshi",
      "purpose": "Prediction markets data",
      "key_tables": [
        "markets",
        "market_tickers",
        "market_prices"
      ]
    },
    {
      "name": "options_data",
      "purpose": "Options market data cache",
      "key_tables": [
        "options_chains",
        "stock_prices",
        "iv_percentiles"
      ]
    },
    {
      "name": "supply_demand",
      "purpose": "Technical analysis zones",
      "key_tables": [
        "supply_demand_zones",
        "zone_performance"
      ]
    },
    {
      "name": "position_recommendations",
      "purpose": "AI position recommendations",
      "key_tables": [
        "recommendations",
        "recommendation_performance"
      ]
    }
  ]
}

## API Integrations
[
  {
    "service": "Robinhood Integration",
    "module": "src/robin_stocks_integration.py",
    "endpoints": [
      "get_open_option_positions()",
      "get_option_market_data()",
      "place_option_order()",
      "get_account_profile()"
    ],
    "authentication": "OAuth tokens in .env"
  },
  {
    "service": "TradingView Sync",
    "module": "src/tradingview_api_sync.py",
    "endpoints": [
      "sync_watchlists()",
      "get_watchlist_symbols()",
      "add_symbol_to_watchlist()"
    ],
    "authentication": "Session cookies"
  },
  {
    "service": "XTrades Scraper",
    "module": "src/xtrades_scraper.py",
    "endpoints": [
      "scrape_alerts()",
      "get_followed_profiles()",
      "sync_watchlists()"
    ],
    "authentication": "Browser automation with session"
  },
  {
    "service": "Kalshi API",
    "module": "src/kalshi_client.py",
    "endpoints": [
      "get_markets()",
      "get_market_orderbook()",
      "place_order()"
    ],
    "authentication": "API key in .env"
  },
  {
    "service": "RAG Service",
    "module": "src/rag/rag_service.py",
    "endpoints": [
      "query(question)",
      "add_document()",
      "get_relevant_context()"
    ],
    "authentication": "Local ChromaDB"
  }
]

## Common Tasks
[
  {
    "task": "Check Portfolio Balance",
    "steps": [
      "Query development_tasks table for balance tracking",
      "Use portfolio_balance_tracker.py",
      "Access dashboard.py main page"
    ],
    "data_source": "Robinhood API + local cache"
  },
  {
    "task": "Find CSP Opportunities",
    "steps": [
      "Run csp_opportunities_finder.py",
      "Filter by IV > 30%, delta 0.15-0.35",
      "Check earnings calendar for conflicts",
      "Verify supply/demand zones"
    ],
    "data_source": "Options data + yfinance + earnings"
  },
  {
    "task": "Analyze Position",
    "steps": [
      "Get position from Robinhood",
      "Calculate Greeks and P&L",
      "Check technical levels",
      "Get AI recommendation"
    ],
    "data_source": "Robinhood + AI Options Agent"
  },
  {
    "task": "Monitor XTrades Alerts",
    "steps": [
      "Check xtrades database for new alerts",
      "Filter by profile/strategy",
      "Analyze alert quality",
      "Track performance"
    ],
    "data_source": "XTrades scraper + database"
  },
  {
    "task": "Query Project Knowledge",
    "steps": [
      "Use RAG service query()",
      "Provide natural language question",
      "Get relevant documentation chunks",
      "Synthesize answer"
    ],
    "data_source": "ChromaDB knowledge base"
  }
]

## AI/ML Capabilities
{
  "rag_system": {
    "description": "Retrieval-Augmented Generation knowledge base",
    "collections": [
      "magnus_knowledge (project documentation)",
      "qa_*_expertise (agent-specific knowledge)"
    ],
    "capabilities": [
      "Semantic search across documentation",
      "Context-aware Q&A",
      "Code reference retrieval",
      "Best practices lookup"
    ]
  },
  "ai_agents": {
    "description": "Autonomous AI agents for various tasks",
    "agents": [
      {
        "name": "code-reviewer",
        "purpose": "Code quality review",
        "threshold": "80%"
      },
      {
        "name": "security-auditor",
        "purpose": "Security vulnerability detection",
        "threshold": "85%"
      },
      {
        "name": "test-automator",
        "purpose": "Test coverage review",
        "threshold": "75%"
      },
      {
        "name": "ai-options-agent",
        "purpose": "Trading recommendations",
        "threshold": "Variable"
      }
    ]
  },
  "position_recommendations": {
    "description": "AI-powered position analysis",
    "models": [
      "Technical analysis ML",
      "Options pricing models",
      "Risk assessment algorithms"
    ],
    "data_sources": [
      "Historical price data",
      "Options Greeks",
      "Volume and IV data",
      "Supply/demand zones"
    ]
  },
  "prediction_markets": {
    "description": "AI-enhanced prediction market analysis",
    "capabilities": [
      "Probability assessment",
      "Value opportunity detection",
      "Multi-factor analysis",
      "Historical pattern recognition"
    ]
  }
}
