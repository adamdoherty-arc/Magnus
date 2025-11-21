"""
Legion Feature Spec Agents - AI Specifications for Every Magnus Feature
=========================================================================

This module provides AI agent specifications for every feature in the Magnus platform.
Each spec agent understands:
- Feature architecture
- Database schema
- API endpoints
- Business logic
- Dependencies
- Best practices

Purpose: Enable Legion to properly understand each Magnus feature for intelligent task creation
and autonomous code generation without breaking existing functionality.

Usage:
    from src.legion.feature_spec_agents import FeatureSpecRegistry

    registry = FeatureSpecRegistry()
    spec = registry.get_feature_spec("dashboard")
    context = spec.get_context_for_task("Add new metric to portfolio display")
"""

from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from enum import Enum


class FeatureCategory(Enum):
    """Feature categories for organization"""
    CORE = "core"  # Essential trading features
    ANALYTICS = "analytics"  # Analysis and research
    AUTOMATION = "automation"  # Automated systems
    INTEGRATION = "integration"  # External integrations
    INFRASTRUCTURE = "infrastructure"  # Platform infrastructure


@dataclass
class DatabaseSchema:
    """Database schema information for a feature"""
    tables: List[str] = field(default_factory=list)
    views: List[str] = field(default_factory=list)
    functions: List[str] = field(default_factory=list)
    schema_file: Optional[str] = None


@dataclass
class APIEndpoint:
    """API endpoint specification"""
    path: str
    method: str
    description: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    response_schema: Dict[str, Any] = field(default_factory=dict)


@dataclass
class FeatureSpec:
    """
    Complete specification for a Magnus feature.

    This provides all context needed by Legion to understand the feature
    and make intelligent decisions about task creation and implementation.
    """

    # Basic information
    name: str
    category: FeatureCategory
    description: str
    entry_point: str  # Main file (e.g., "dashboard.py")

    # Architecture
    database_schema: DatabaseSchema
    api_endpoints: List[APIEndpoint] = field(default_factory=list)
    dependencies: List[str] = field(default_factory=list)  # Other features this depends on

    # Implementation details
    key_files: List[str] = field(default_factory=list)
    components: List[str] = field(default_factory=list)  # Streamlit components
    services: List[str] = field(default_factory=list)  # Backend services

    # Documentation
    spec_file: str = ""  # Path to SPEC.md
    architecture_file: str = ""  # Path to ARCHITECTURE.md
    readme_file: str = ""  # Path to README.md

    # Business logic patterns
    coding_patterns: List[str] = field(default_factory=list)
    best_practices: List[str] = field(default_factory=list)
    anti_patterns: List[str] = field(default_factory=list)  # What NOT to do

    # Testing
    test_files: List[str] = field(default_factory=list)
    test_patterns: List[str] = field(default_factory=list)

    def get_context_for_task(self, task_description: str) -> str:
        """
        Generate contextual information for Legion based on a task description.

        This helps Legion understand what files to touch, patterns to follow,
        and potential issues to avoid.
        """
        context = f"""
# Feature Context: {self.name}

## Task Description
{task_description}

## Feature Overview
{self.description}

## Key Files to Consider
{chr(10).join(f"- {file}" for file in self.key_files)}

## Database Schema
Tables: {', '.join(self.database_schema.tables) if self.database_schema.tables else 'None'}
Views: {', '.join(self.database_schema.views) if self.database_schema.views else 'None'}

## Dependencies
{chr(10).join(f"- {dep}" for dep in self.dependencies) if self.dependencies else "- None (independent feature)"}

## Coding Patterns to Follow
{chr(10).join(f"- {pattern}" for pattern in self.coding_patterns)}

## Best Practices
{chr(10).join(f"- {practice}" for practice in self.best_practices)}

## Anti-Patterns (DO NOT)
{chr(10).join(f"- {anti}" for anti in self.anti_patterns)}

## Documentation References
- Specification: {self.spec_file}
- Architecture: {self.architecture_file}
- User Guide: {self.readme_file}
"""
        return context


class FeatureSpecRegistry:
    """
    Central registry of all Magnus feature specifications.

    This is the single source of truth for Legion to understand the Magnus platform.
    """

    def __init__(self):
        self.features: Dict[str, FeatureSpec] = {}
        self._initialize_all_features()

    def _initialize_all_features(self):
        """Initialize specs for all Magnus features"""

        # 1. DASHBOARD
        self.features["dashboard"] = FeatureSpec(
            name="Dashboard",
            category=FeatureCategory.CORE,
            description="Main portfolio overview with real-time metrics, trade history, balance forecasts, and AI recommendations",
            entry_point="dashboard.py",
            database_schema=DatabaseSchema(
                tables=["portfolio_balances", "trade_history", "positions"],
                views=["v_portfolio_summary", "v_trade_metrics"],
                schema_file="src/schema.sql"
            ),
            api_endpoints=[
                APIEndpoint(
                    path="/api/portfolio/balance",
                    method="GET",
                    description="Get current portfolio balance from Robinhood"
                ),
                APIEndpoint(
                    path="/api/trades/history",
                    method="GET",
                    description="Get historical trades with P&L"
                )
            ],
            dependencies=["robinhood_integration", "ai_research"],
            key_files=[
                "dashboard.py",
                "src/robinhood_client.py",
                "src/portfolio_balance_tracker.py",
                "src/portfolio_balance_display.py"
            ],
            components=["portfolio_status", "trade_history_form", "balance_forecast_timeline"],
            services=["robinhood_client", "portfolio_tracker"],
            spec_file="features/dashboard/SPEC.md",
            architecture_file="features/dashboard/ARCHITECTURE.md",
            readme_file="features/dashboard/README.md",
            coding_patterns=[
                "Use st.cache_data for expensive API calls",
                "Store balances in PostgreSQL with timestamps",
                "Calculate forecasts based on position expirations",
                "Update UI with st.rerun() after database changes"
            ],
            best_practices=[
                "Cache Robinhood API responses (60s TTL)",
                "Validate all trade inputs before database insert",
                "Use transaction blocks for multi-table updates",
                "Format currency with $ and 2 decimal places",
                "Show loading spinners for slow operations"
            ],
            anti_patterns=[
                "DON'T call Robinhood API on every page refresh",
                "DON'T calculate balances in UI layer (use database views)",
                "DON'T expose API keys in code or logs",
                "DON'T ignore error handling for network failures"
            ],
            test_files=["test_dashboard_display.py", "test_portfolio_tracker.py"]
        )

        # 2. OPPORTUNITIES
        self.features["opportunities"] = FeatureSpec(
            name="Opportunities",
            category=FeatureCategory.CORE,
            description="Discover high-quality CSP and covered call opportunities with AI scoring",
            entry_point="opportunities_page.py",
            database_schema=DatabaseSchema(
                tables=["opportunities", "stocks", "options_chain"],
                views=["v_csp_opportunities", "v_covered_call_opportunities"],
                schema_file="src/opportunities_schema.sql"
            ),
            dependencies=["robinhood_integration", "ai_research"],
            key_files=[
                "opportunities_page.py",
                "src/csp_opportunities_finder.py",
                "src/options_data_fetcher.py"
            ],
            components=["opportunity_scanner", "filters_sidebar", "results_table"],
            services=["csp_finder", "options_fetcher"],
            spec_file="features/opportunities/SPEC.md",
            architecture_file="features/opportunities/ARCHITECTURE.md",
            readme_file="features/opportunities/README.md",
            coding_patterns=[
                "Score opportunities 0-100 based on multiple factors",
                "Filter by IV percentile, volume, premium %",
                "Show Greeks (Delta, Theta, Vega) for each opportunity",
                "Calculate returns as monthly % and annualized %"
            ],
            best_practices=[
                "Refresh options data before scanning",
                "Use realistic filters (avoid illiquid options)",
                "Show assignment probability prominently",
                "Include earnings date warnings",
                "Sort by score descending by default"
            ],
            anti_patterns=[
                "DON'T recommend options with volume < 10",
                "DON'T ignore bid-ask spread (affects real returns)",
                "DON'T show expired or near-expiration options (<7 DTE)",
                "DON'T calculate returns without factoring in risk"
            ],
            test_files=["test_csp_finder.py", "test_opportunities_scoring.py"]
        )

        # 3. POSITIONS
        self.features["positions"] = FeatureSpec(
            name="Positions",
            category=FeatureCategory.CORE,
            description="Manage active options positions with real-time P&L, theta decay, and AI recommendations",
            entry_point="positions_page_improved.py",
            database_schema=DatabaseSchema(
                tables=["positions", "options_quotes"],
                views=["v_active_positions", "v_position_metrics"],
                schema_file="src/positions_schema.sql"
            ),
            dependencies=["robinhood_integration", "ai_research"],
            key_files=[
                "positions_page_improved.py",
                "src/robinhood_client.py",
                "src/options_greeks_calculator.py"
            ],
            components=["positions_table", "theta_decay_chart", "ai_analysis_panel"],
            services=["robinhood_client", "greeks_calculator"],
            spec_file="features/positions/SPEC.md",
            architecture_file="features/positions/ARCHITECTURE.md",
            readme_file="features/positions/README.md",
            coding_patterns=[
                "Fetch positions from Robinhood API",
                "Calculate real-time P&L = (premium_collected - current_price) * 100 * quantity",
                "Project theta decay daily until expiration",
                "Show AI recommendations for each position"
            ],
            best_practices=[
                "Auto-refresh positions every 60 seconds (optional)",
                "Color-code P&L (green=profit, red=loss)",
                "Show days to expiration prominently",
                "Calculate assignment probability based on moneyness",
                "Warn when position is ITM or near expiration"
            ],
            anti_patterns=[
                "DON'T assume positions are always CSPs (support all option types)",
                "DON'T hardcode refresh intervals (make configurable)",
                "DON'T show stale data without timestamp",
                "DON'T calculate Greeks in UI (use service layer)"
            ],
            test_files=["test_positions_import.py", "test_rh_positions_data.py"]
        )

        # 4. PREMIUM_SCANNER
        self.features["premium_scanner"] = FeatureSpec(
            name="Premium Scanner",
            category=FeatureCategory.ANALYTICS,
            description="Advanced options premium screening with multi-expiration support",
            entry_point="premium_scanner_page.py",
            database_schema=DatabaseSchema(
                tables=["premium_scans", "options_chain"],
                schema_file="src/premium_schema.sql"
            ),
            dependencies=["options_data"],
            key_files=[
                "premium_scanner_page.py",
                "src/premium_scanner_service.py",
                "src/options_chain_fetcher.py"
            ],
            components=["scanner_filters", "expiration_tabs", "results_grid"],
            services=["premium_scanner", "options_fetcher"],
            spec_file="features/premium_scanner/SPEC.md",
            architecture_file="features/premium_scanner/ARCHITECTURE.md",
            readme_file="features/premium_scanner/README.md",
            coding_patterns=[
                "Support multiple DTE ranges (7d, 14d, 30d, 45d)",
                "Filter by IV level, volume, price range",
                "Calculate monthly and annualized returns",
                "Sort by premium % or score"
            ],
            best_practices=[
                "Show bid/ask spread prominently",
                "Filter out illiquid options automatically",
                "Include Greeks in results",
                "Cache scan results (5-min TTL)",
                "Export results to CSV"
            ],
            anti_patterns=[
                "DON'T scan entire market (too slow, use watchlists)",
                "DON'T ignore open interest (liquidity indicator)",
                "DON'T show options with wide spreads (>10% of premium)",
                "DON'T use stale IV data (refresh before scan)"
            ],
            test_files=["test_premium_scanner.py"]
        )

        # 5. TRADINGVIEW_WATCHLISTS
        self.features["tradingview_watchlists"] = FeatureSpec(
            name="TradingView Watchlists",
            category=FeatureCategory.INTEGRATION,
            description="Sync TradingView watchlists and perform premium analysis on symbols",
            entry_point="xtrades_watchlists_page.py",
            database_schema=DatabaseSchema(
                tables=["tradingview_watchlists", "watchlist_symbols"],
                views=["v_watchlist_analysis"],
                schema_file="src/tradingview_schema.sql"
            ),
            dependencies=["tradingview_api", "premium_scanner"],
            key_files=[
                "xtrades_watchlists_page.py",
                "src/tradingview_api_sync.py",
                "src/watchlist_sync_service.py"
            ],
            components=["watchlist_selector", "sync_button", "symbol_grid"],
            services=["tradingview_sync", "watchlist_manager"],
            spec_file="features/tradingview_watchlists/SPEC.md",
            architecture_file="features/tradingview_watchlists/ARCHITECTURE.md",
            readme_file="features/tradingview_watchlists/README.md",
            coding_patterns=[
                "Authenticate with TradingView using session cookies",
                "Fetch watchlists via API",
                "Store symbols in PostgreSQL for analysis",
                "Run premium analysis on all watchlist symbols"
            ],
            best_practices=[
                "Refresh session automatically when expired",
                "Support multiple watchlists",
                "Show sync status and timestamp",
                "Handle network errors gracefully",
                "Cache watchlist data (30-min TTL)"
            ],
            anti_patterns=[
                "DON'T sync on every page load (expensive)",
                "DON'T expose TradingView credentials in logs",
                "DON'T ignore rate limits from TradingView API",
                "DON'T delete watchlists without user confirmation"
            ],
            test_files=["test_tradingview_sync.py", "test_watchlist_integration.py"]
        )

        # 6. DATABASE_SCAN
        self.features["database_scan"] = FeatureSpec(
            name="Database Scan",
            category=FeatureCategory.CORE,
            description="Manage stock database and scan for premium opportunities",
            entry_point="database_scan_page.py",
            database_schema=DatabaseSchema(
                tables=["stocks", "scan_results"],
                views=["v_scan_analytics"],
                schema_file="src/stock_data_schema.sql"
            ),
            dependencies=["options_data"],
            key_files=[
                "database_scan_page.py",
                "src/stock_data_sync.py",
                "src/database_scanner.py"
            ],
            components=["add_stocks_form", "scan_button", "analytics_dashboard"],
            services=["stock_manager", "database_scanner"],
            spec_file="features/database_scan/SPEC.md",
            architecture_file="features/database_scan/ARCHITECTURE.md",
            readme_file="features/database_scan/README.md",
            coding_patterns=[
                "Add stocks in bulk (comma-separated or file upload)",
                "Validate symbols against market data API",
                "Store stock metadata (sector, market cap, etc.)",
                "Scan all stocks for premium opportunities"
            ],
            best_practices=[
                "Deduplicate symbols before adding",
                "Validate symbols exist before scanning",
                "Show scan progress indicator",
                "Group analytics by sector and price range",
                "Optimize database with indexes on symbol"
            ],
            anti_patterns=[
                "DON'T add invalid symbols to database",
                "DON'T scan without recent options data",
                "DON'T block UI during long scans (use async)",
                "DON'T ignore duplicate detection"
            ],
            test_files=["test_database_sync.py", "test_stock_validation.py"]
        )

        # 7. EARNINGS_CALENDAR
        self.features["earnings_calendar"] = FeatureSpec(
            name="Earnings Calendar",
            category=FeatureCategory.ANALYTICS,
            description="Track upcoming earnings dates to avoid unwanted risk",
            entry_point="earnings_calendar_page.py",
            database_schema=DatabaseSchema(
                tables=["earnings_dates"],
                views=["v_upcoming_earnings"],
                schema_file="src/earnings_schema.sql"
            ),
            dependencies=["stocks", "positions"],
            key_files=[
                "earnings_calendar_page.py",
                "src/earnings_fetcher.py"
            ],
            components=["calendar_view", "alerts_list", "position_warnings"],
            services=["earnings_fetcher"],
            spec_file="features/earnings_calendar/SPEC.md",
            architecture_file="features/earnings_calendar/ARCHITECTURE.md",
            readme_file="features/earnings_calendar/README.md",
            coding_patterns=[
                "Fetch earnings dates from financial data API",
                "Cross-reference with active positions",
                "Warn when position expires after earnings",
                "Calculate days until earnings"
            ],
            best_practices=[
                "Update earnings dates daily",
                "Highlight positions at risk (expires after earnings)",
                "Show estimated earnings move (%)",
                "Sort by date ascending",
                "Color-code by urgency (red=<7 days)"
            ],
            anti_patterns=[
                "DON'T use stale earnings data (refresh daily)",
                "DON'T ignore time of day (morning vs after-hours)",
                "DON'T assume all positions are at risk (check expiry)",
                "DON'T hardcode earnings dates (they change)"
            ],
            test_files=["test_earnings_fetcher.py"]
        )

        # 8. CALENDAR_SPREADS
        self.features["calendar_spreads"] = FeatureSpec(
            name="Calendar Spreads",
            category=FeatureCategory.CORE,
            description="Analyze and execute calendar spread strategies with AI recommendations",
            entry_point="calendar_spreads_page.py",
            database_schema=DatabaseSchema(
                tables=["calendar_spreads", "spread_analysis"],
                views=["v_calendar_opportunities"],
                schema_file="src/calendar_spreads_schema.sql"
            ),
            dependencies=["options_data", "ai_research"],
            key_files=[
                "calendar_spreads_page.py",
                "src/calendar_spread_analyzer.py",
                "src/ai_spread_evaluator.py"
            ],
            components=["spread_builder", "analysis_panel", "ai_recommendations"],
            services=["spread_analyzer", "ai_evaluator"],
            spec_file="features/calendar_spreads/SPEC.md",
            architecture_file="features/calendar_spreads/ARCHITECTURE.md",
            readme_file="features/calendar_spreads/README.md",
            coding_patterns=[
                "Build spreads with long and short legs",
                "Calculate net debit/credit",
                "Analyze IV skew between expirations",
                "Get AI evaluation of spread quality"
            ],
            best_practices=[
                "Show breakeven points clearly",
                "Calculate max profit and max loss",
                "Include Greeks for both legs",
                "Warn about pin risk near expiration",
                "Use AI to evaluate spread vs market conditions"
            ],
            anti_patterns=[
                "DON'T build spreads without checking liquidity",
                "DON'T ignore IV differences (key to calendar spreads)",
                "DON'T execute without understanding risk profile",
                "DON'T skip commission calculations"
            ],
            test_files=["test_calendar_spread_analyzer.py", "test_ai_spread_evaluator.py"]
        )

        # 9. PREDICTION_MARKETS
        self.features["prediction_markets"] = FeatureSpec(
            name="Prediction Markets",
            category=FeatureCategory.INTEGRATION,
            description="Integrate Kalshi prediction markets for event-driven trading insights",
            entry_point="prediction_markets_page.py",
            database_schema=DatabaseSchema(
                tables=["kalshi_markets", "kalshi_positions", "kalshi_events"],
                views=["v_active_markets", "v_market_analysis"],
                schema_file="src/kalshi_schema.sql"
            ),
            dependencies=["kalshi_api", "ai_research"],
            key_files=[
                "prediction_markets_page.py",
                "kalshi_nfl_markets_page.py",
                "src/kalshi_integration.py",
                "src/kalshi_client.py",
                "src/kalshi_db_manager.py",
                "src/kalshi_ai_evaluator.py"
            ],
            components=["markets_grid", "event_calendar", "ai_analysis", "nfl_games_cards"],
            services=["kalshi_client", "kalshi_manager", "kalshi_ai"],
            spec_file="features/prediction_markets/SPEC.md",
            architecture_file="features/prediction_markets/ARCHITECTURE.md",
            readme_file="features/prediction_markets/README.md",
            coding_patterns=[
                "Fetch markets from Kalshi API",
                "Store market data with real-time updates",
                "Cross-reference with stock events (earnings, Fed meetings, etc.)",
                "Use AI to evaluate market mispricing",
                "Display NFL game predictions with game cards"
            ],
            best_practices=[
                "Refresh market data frequently (5-min intervals)",
                "Show yes/no probabilities clearly",
                "Calculate implied probabilities vs AI estimates",
                "Highlight arbitrage opportunities",
                "Track positions separately from options",
                "Use visual cards for NFL games"
            ],
            anti_patterns=[
                "DON'T mix prediction market logic with options logic",
                "DON'T ignore Kalshi rate limits",
                "DON'T assume all markets are tradeable (check status)",
                "DON'T forget to convert prices (0-100 format)"
            ],
            test_files=["test_kalshi_integration.py", "test_kalshi_ai.py", "test_kalshi_nfl_markets_page.py"]
        )

        # 10. AI_RESEARCH
        self.features["ai_research"] = FeatureSpec(
            name="AI Research Assistant",
            category=FeatureCategory.ANALYTICS,
            description="AI-powered stock research with fundamental, technical, sentiment, and options analysis",
            entry_point="ai_research_page.py",
            database_schema=DatabaseSchema(
                tables=["research_cache", "ai_analysis"],
                views=["v_recent_analysis"],
                schema_file="src/ai_research_schema.sql"
            ),
            dependencies=["ai_services", "market_data"],
            key_files=[
                "ai_research_page.py",
                "src/ai/research_orchestrator.py",
                "src/agents/ai_research/fundamental_agent.py",
                "src/agents/ai_research/technical_agent.py",
                "src/agents/ai_research/sentiment_agent.py",
                "src/agents/ai_research/options_agent.py"
            ],
            components=["symbol_input", "analysis_tabs", "ai_recommendations"],
            services=["research_orchestrator", "fundamental_agent", "technical_agent", "sentiment_agent", "options_agent"],
            spec_file="features/ai_research/SPEC.md",
            architecture_file="features/ai_research/ARCHITECTURE.md",
            readme_file="features/ai_research/README.md",
            coding_patterns=[
                "Use multi-agent architecture (4 specialized agents)",
                "Cache analysis results (1-hour TTL)",
                "Score each dimension 0-100",
                "Provide overall rating and actionable recommendation",
                "Include position-specific advice"
            ],
            best_practices=[
                "Run agents in parallel for speed",
                "Combine scores into overall rating",
                "Show reasoning for recommendations",
                "Include time-sensitive factors (earnings, events)",
                "Cache expensive API calls",
                "Use FREE LLM services (Groq, Gemini, DeepSeek)"
            ],
            anti_patterns=[
                "DON'T run analysis without recent data",
                "DON'T ignore context (user's position, risk tolerance)",
                "DON'T provide recommendations without reasoning",
                "DON'T use stale cached data for time-sensitive decisions",
                "DON'T waste money on expensive LLMs (use FREE tiers)"
            ],
            test_files=["test_ai_research.py", "test_agents.py"]
        )

        # 11. SETTINGS
        self.features["settings"] = FeatureSpec(
            name="Settings",
            category=FeatureCategory.INFRASTRUCTURE,
            description="Configure Robinhood and TradingView API credentials and preferences",
            entry_point="settings_page.py",
            database_schema=DatabaseSchema(
                tables=["user_settings"],
                schema_file="src/settings_schema.sql"
            ),
            dependencies=[],
            key_files=[
                "settings_page.py",
                "src/settings_manager.py"
            ],
            components=["credentials_form", "preferences_form", "test_connections"],
            services=["settings_manager"],
            spec_file="features/settings/SPEC.md",
            architecture_file="features/settings/ARCHITECTURE.md",
            readme_file="features/settings/README.md",
            coding_patterns=[
                "Store credentials securely (encrypted in .env)",
                "Test API connections on save",
                "Validate credentials before storing",
                "Show connection status indicators"
            ],
            best_practices=[
                "NEVER log credentials",
                "Encrypt sensitive data",
                "Provide clear setup instructions",
                "Test connections immediately",
                "Show helpful error messages"
            ],
            anti_patterns=[
                "DON'T store credentials in plain text",
                "DON'T commit .env file to git",
                "DON'T expose API keys in UI or logs",
                "DON'T save without validation"
            ],
            test_files=["test_settings.py", "test_security_fixes.py"]
        )

        # 12. ENHANCEMENT_AGENT
        self.features["enhancement_agent"] = FeatureSpec(
            name="Enhancement Agent",
            category=FeatureCategory.AUTOMATION,
            description="Autonomous agent system for continuous platform improvement",
            entry_point="enhancement_manager_page.py",
            database_schema=DatabaseSchema(
                tables=["development_tasks", "task_execution_log", "task_verification", "task_files"],
                views=["v_active_tasks", "v_feature_progress", "v_agent_workload"],
                schema_file="src/task_management_schema.sql"
            ),
            dependencies=[],
            key_files=[
                "enhancement_manager_page.py",
                "src/task_manager.py",
                "src/task_db_manager.py",
                "src/ava/autonomous_agent.py",
                "start_autonomous_agent.py"
            ],
            components=["task_list", "agent_status", "progress_dashboard"],
            services=["task_manager", "autonomous_agent"],
            spec_file="features/enhancement_agent/SPEC.md",
            architecture_file="features/enhancement_agent/ARCHITECTURE.md",
            readme_file="features/enhancement_agent/README.md",
            coding_patterns=[
                "Store tasks in PostgreSQL with status workflow",
                "Route tasks to specialized agents",
                "Log all execution activity",
                "Track file changes per task",
                "Verify completed tasks with QA"
            ],
            best_practices=[
                "Use database triggers for automatic timestamps",
                "Check dependencies before starting tasks",
                "Rate limit agent execution (safety)",
                "Budget control for API costs",
                "Human approval gates for critical changes"
            ],
            anti_patterns=[
                "DON'T run tasks without dependency checking",
                "DON'T ignore failed tasks (log and retry)",
                "DON'T execute without safety limits",
                "DON'T skip verification step"
            ],
            test_files=["test_task_management_system.py", "verify_task_schema.py"]
        )

    def get_feature_spec(self, feature_name: str) -> Optional[FeatureSpec]:
        """Get feature specification by name (case-insensitive)"""
        feature_name_lower = feature_name.lower().replace(" ", "_").replace("-", "_")
        return self.features.get(feature_name_lower)

    def get_all_features(self) -> List[FeatureSpec]:
        """Get all feature specifications"""
        return list(self.features.values())

    def get_features_by_category(self, category: FeatureCategory) -> List[FeatureSpec]:
        """Get all features in a specific category"""
        return [spec for spec in self.features.values() if spec.category == category]

    def find_features_by_keyword(self, keyword: str) -> List[FeatureSpec]:
        """Find features whose description contains keyword"""
        keyword_lower = keyword.lower()
        return [
            spec for spec in self.features.values()
            if keyword_lower in spec.description.lower() or keyword_lower in spec.name.lower()
        ]

    def get_feature_dependencies(self, feature_name: str) -> List[FeatureSpec]:
        """Get all features that a given feature depends on"""
        spec = self.get_feature_spec(feature_name)
        if not spec:
            return []

        return [
            self.get_feature_spec(dep)
            for dep in spec.dependencies
            if self.get_feature_spec(dep) is not None
        ]

    def generate_legion_context(self, task: str) -> str:
        """
        Generate comprehensive context for Legion based on a task description.

        This analyzes the task and provides all relevant feature contexts.
        """
        # Simple keyword matching to identify relevant features
        relevant_features = []

        task_lower = task.lower()
        for feature in self.features.values():
            # Check if feature name or key components mentioned in task
            if (feature.name.lower() in task_lower or
                any(comp.lower() in task_lower for comp in feature.components) or
                any(keyword in task_lower for keyword in feature.description.lower().split()[:10])):
                relevant_features.append(feature)

        # If no specific features identified, provide general context
        if not relevant_features:
            relevant_features = [self.features["dashboard"]]  # Default to dashboard context

        context = f"""
# Legion Context Generation for Magnus Platform

## Task Description
{task}

## Relevant Features Identified
{chr(10).join(f"- {spec.name}: {spec.description}" for spec in relevant_features)}

---

"""
        # Add detailed context for each relevant feature
        for spec in relevant_features:
            context += spec.get_context_for_task(task)
            context += "\n---\n\n"

        # Add cross-feature dependencies
        all_deps = set()
        for spec in relevant_features:
            all_deps.update(spec.dependencies)

        if all_deps:
            context += f"""
## Cross-Feature Dependencies
The following features may also be affected:
{chr(10).join(f"- {dep}" for dep in all_deps)}

**Recommendation:** Review these dependent features when making changes.
"""

        return context


# Convenience function for Legion integration
def get_context_for_legion(task_description: str) -> str:
    """
    Quick function to get context for Legion.

    Usage in Legion:
        from src.legion.feature_spec_agents import get_context_for_legion
        context = get_context_for_legion("Add new metric to dashboard showing daily theta")
    """
    registry = FeatureSpecRegistry()
    return registry.generate_legion_context(task_description)


if __name__ == "__main__":
    # Test the registry
    print("="*80)
    print("MAGNUS FEATURE SPEC AGENTS - TEST")
    print("="*80)

    registry = FeatureSpecRegistry()

    print(f"\n✅ Loaded {len(registry.features)} features:")
    for name in sorted(registry.features.keys()):
        spec = registry.features[name]
        print(f"   - {spec.name} ({spec.category.value}): {spec.description[:60]}...")

    print("\n" + "="*80)
    print("TEST: Generate context for sample task")
    print("="*80)

    task = "Add a new metric to the dashboard showing total theta decay per day"
    context = registry.generate_legion_context(task)

    print("\nContext generated:")
    print(context[:1000] + "..." if len(context) > 1000 else context)

    print("\n✅ Feature Spec Agents System Ready!")
    print("Legion can now understand all Magnus features for intelligent task creation.")
