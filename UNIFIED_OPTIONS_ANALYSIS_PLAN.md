# Unified Options Analysis - Implementation Plan

## Executive Summary

Combining AI Options Agent (screening) and Comprehensive Strategy (deep analysis) into ONE streamlined "Options Analysis" page with current positions integration and AVA chatbot support.

---

## Complete Feature List

### From AI Options Agent
1. Batch screening (200+ stocks)
2. Multi-source selection (watchlist, database, all stocks)
3. Multi-criteria scoring (5 dimensions: Fundamental, Technical, Greeks, Risk, Sentiment)
4. Configurable filters (DTE, delta, premium, score threshold)
5. Optional LLM reasoning
6. Results ranking and display
7. Score breakdowns
8. Top picks historical tracking
9. Performance metrics

### From Comprehensive Strategy
1. Single stock deep dive
2. All 10 strategies evaluation
3. Market environment analysis (volatility, trend, regime)
4. Multi-model AI consensus (3 models)
5. Auto-fill from database
6. Manual override capability
7. Strategy suitability scoring
8. Detailed AI reasoning
9. Win rate estimates

### New Features (Research-Based)
1. Real-time Greeks calculator
2. P&L visualization (payoff diagrams)
3. Probability of Profit (POP)
4. Unusual options flow detection
5. Earnings calendar context
6. IV rank/percentile/skew analysis
7. Comprehensive risk metrics
8. **Current positions dropdown integration**
9. Position risk analysis
10. AVA natural language queries

---

## Implementation Tasks

### Phase 1: Core Foundation (Day 1-2)

#### Task 1.1: Create Positions Manager
- [ ] Build `src/data/positions_manager.py`
- [ ] Fetch current positions from Robinhood API
- [ ] Cache positions in session state
- [ ] Format for dropdown display
- [ ] Handle API errors gracefully

#### Task 1.2: Enhanced Stock Selector
- [ ] Extend `src/ai_options_agent/shared/stock_selector.py`
- [ ] Add "Current Positions" mode
- [ ] Integrate positions_manager
- [ ] Display format: "AAPL - $150 PUT 30 DTE (Current Position)"
- [ ] Auto-load position details when selected

#### Task 1.3: Unified Analyzer Core
- [ ] Create `src/options_analysis/unified_analyzer.py`
- [ ] Combine OptionsAnalysisAgent + ComprehensiveStrategyAnalyzer
- [ ] Single entry point for both screening and deep analysis
- [ ] Shared caching layer
- [ ] Optimized database queries

### Phase 2: UI Layout (Day 2-3)

#### Task 2.1: Three-Panel Layout
- [ ] Create `options_analysis_page.py`
- [ ] Left panel (30%): Stock selection + Filters + Results
- [ ] Center panel (45%): Strategy analysis + Greeks + P&L
- [ ] Right panel (25%): Context (flow, earnings, IV, news)
- [ ] Responsive design for smaller screens

#### Task 2.2: Left Panel Components
- [ ] Stock selector with 4 modes (manual, watchlist, database, **positions**)
- [ ] Screening filters (DTE, delta, premium, IV)
- [ ] "Run Scan" button
- [ ] Results table (scrollable, paginated)
- [ ] Click handler → load in center panel
- [ ] Strategy rankings widget

#### Task 2.3: Center Panel Components
- [ ] Selected stock header
- [ ] P&L visualization (payoff diagram)
- [ ] Greeks display (Delta, Gamma, Theta, Vega)
- [ ] Risk metrics (max loss, max profit, breakeven, POP)
- [ ] Strategy selector tabs (10 strategies)
- [ ] Execute/analyze buttons
- [ ] Time decay forecast

#### Task 2.4: Right Panel Components
- [ ] Unusual flow indicator
- [ ] Earnings date + expected move
- [ ] IV rank/percentile chart
- [ ] Quick stats (volume, OI, bid/ask)
- [ ] News feed (recent headlines)
- [ ] Related alerts

### Phase 3: Analysis Features (Day 3-4)

#### Task 3.1: Screening Engine Integration
- [ ] Connect to existing scoring engine
- [ ] Add positions as data source
- [ ] Optimize query performance
- [ ] Cache scan results
- [ ] Progressive loading for large result sets

#### Task 3.2: Strategy Evaluation Integration
- [ ] Integrate all 10 strategy evaluators
- [ ] Market environment analyzer
- [ ] Multi-model AI consensus
- [ ] Strategy ranking algorithm
- [ ] Results caching

#### Task 3.3: Greeks Calculator
- [ ] Create `src/options_analysis/greeks_calculator.py`
- [ ] Delta, Gamma, Theta, Vega calculations
- [ ] Real-time updates on parameter changes
- [ ] Vectorized computation for speed
- [ ] Display with visual indicators

#### Task 3.4: P&L Visualizer
- [ ] Create `src/options_analysis/pl_visualizer.py`
- [ ] Plotly/Matplotlib payoff diagrams
- [ ] Interactive strike adjustment
- [ ] Time decay animation
- [ ] Multiple scenarios overlay

### Phase 4: Advanced Features (Day 4-5)

#### Task 4.1: Unusual Flow Detection
- [ ] Create `src/options_analysis/flow_detector.py`
- [ ] Query for large orders (volume > 10x avg)
- [ ] Institutional activity patterns
- [ ] Smart money indicators
- [ ] Real-time alerts

#### Task 4.2: Earnings Integration
- [ ] Query earnings calendar API
- [ ] Calculate days to earnings
- [ ] Historical IV crush data
- [ ] Expected move calculation
- [ ] Warning for positions near earnings

#### Task 4.3: IV Analysis
- [ ] IV rank calculation (252-day percentile)
- [ ] IV percentile chart visualization
- [ ] Term structure display
- [ ] Skew analysis
- [ ] Historical IV overlay

#### Task 4.4: Probability of Profit
- [ ] Statistical POP calculation
- [ ] Monte Carlo simulation
- [ ] IV impact analysis
- [ ] Time decay impact
- [ ] Visual probability cone

### Phase 5: AVA Integration (Day 5-6)

#### Task 5.1: Query Parser
- [ ] Create `src/options_analysis/ava_integration.py`
- [ ] NLP intent classification
- [ ] Extract: ticker, strategy, filters, action
- [ ] Handle ambiguous queries
- [ ] Validation layer

#### Task 5.2: Command Handlers
- [ ] "Find opportunities" → Run scan
- [ ] "Analyze [ticker]" → Load strategy analysis
- [ ] "Best strategy for [ticker]" → Run all 10 strategies
- [ ] "My [ticker] position" → Load current position
- [ ] "Show me [strategy type]" → Filter to strategy

#### Task 5.3: Results Formatter
- [ ] Concise summary for chat display
- [ ] Top 3-5 results
- [ ] Key metrics highlighting
- [ ] Clickable links to full page
- [ ] Follow-up suggestions

#### Task 5.4: Session Integration
- [ ] Share session state with main page
- [ ] Sync selected stock
- [ ] Cache query results
- [ ] Update page when AVA runs analysis

### Phase 6: Polish & Optimization (Day 6-7)

#### Task 6.1: Performance Optimization
- [ ] Query optimization (< 1s for scans)
- [ ] Caching layer (Redis/memory)
- [ ] Progressive loading
- [ ] Debounce filter changes (300ms)
- [ ] Virtual scrolling for large tables

#### Task 6.2: Error Handling
- [ ] API timeout handling
- [ ] Database connection errors
- [ ] Invalid input validation
- [ ] Graceful degradation
- [ ] User-friendly error messages

#### Task 6.3: Testing
- [ ] Unit tests for core analyzers
- [ ] Integration tests for data flow
- [ ] UI responsiveness testing
- [ ] Performance benchmarks
- [ ] User acceptance testing

#### Task 6.4: Documentation
- [ ] User guide
- [ ] Feature explanations
- [ ] Workflow examples
- [ ] Keyboard shortcuts
- [ ] Troubleshooting guide

---

## File Structure

```
c:/Code/Legion/repos/ava/
├── options_analysis_page.py (NEW - main unified page)
│
├── src/
│   ├── options_analysis/ (NEW - unified module)
│   │   ├── __init__.py
│   │   ├── unified_analyzer.py (combines both engines)
│   │   ├── greeks_calculator.py
│   │   ├── pl_visualizer.py
│   │   ├── flow_detector.py
│   │   ├── earnings_analyzer.py
│   │   ├── iv_analyzer.py
│   │   ├── pop_calculator.py
│   │   └── ava_integration.py
│   │
│   ├── data/
│   │   └── positions_manager.py (NEW - Robinhood positions)
│   │
│   └── ai_options_agent/ (EXISTING - reuse components)
│       ├── scoring_engine.py (reuse)
│       ├── options_analysis_agent.py (reuse)
│       ├── comprehensive_strategy_analyzer.py (reuse)
│       ├── llm_manager.py (reuse)
│       └── shared/
│           ├── stock_selector.py (ENHANCE with positions)
│           ├── data_fetchers.py (reuse)
│           └── display_helpers.py (reuse)
│
└── (archive for reference)
    ├── ai_options_agent_page.py (OLD)
    └── comprehensive_strategy_page.py (OLD)
```

---

## Technical Details

### Positions Integration

```python
# src/data/positions_manager.py

class PositionsManager:
    """Fetch and manage current options positions from Robinhood"""

    def get_current_positions(self) -> List[Dict]:
        """
        Returns list of current options positions

        Format:
        [
            {
                'symbol': 'AAPL',
                'strike': 150.0,
                'expiry': '2025-12-15',
                'option_type': 'put',
                'quantity': 5,
                'entry_price': 2.50,
                'current_price': 3.10,
                'pnl': 300.0,
                'days_to_expiry': 30
            },
            ...
        ]
        """

    def format_for_dropdown(self, positions: List[Dict]) -> List[str]:
        """
        Format for stock selector dropdown

        Returns:
        [
            "AAPL - $150 PUT 30 DTE (+$300 P&L)",
            "TSLA - $700 CALL 45 DTE (-$150 P&L)",
            ...
        ]
        """
```

### Enhanced Stock Selector

```python
# Extend src/ai_options_agent/shared/stock_selector.py

class StockSelector:
    def render_single_stock_selector(self, modes=None):
        """
        modes: ["manual", "tradingview", "database", "positions"]
        """

        # Add new mode
        if "positions" in modes:
            positions_mgr = PositionsManager()
            positions = positions_mgr.get_current_positions()

            if positions:
                st.selectbox(
                    "Or select from current positions:",
                    positions_mgr.format_for_dropdown(positions)
                )

                # When selected, auto-fill:
                # - Symbol
                # - Strike
                # - Expiry
                # - Current Greeks
                # - P&L
```

### AVA Integration Example

```python
# src/options_analysis/ava_integration.py

class OptionsAnalysisAVA:
    """AVA integration for Options Analysis"""

    def parse_query(self, user_input: str) -> Dict:
        """
        Parse natural language query

        Examples:
        "Find CSP opportunities in NVDA watchlist"
        → {'action': 'scan', 'source': 'watchlist', 'watchlist': 'NVDA', 'strategy': 'csp'}

        "What's the best strategy for my AAPL position?"
        → {'action': 'analyze', 'source': 'position', 'symbol': 'AAPL'}

        "Show me calendar spreads on SPY"
        → {'action': 'analyze', 'symbol': 'SPY', 'strategy': 'calendar_spread'}
        """

    def execute_query(self, parsed: Dict) -> Dict:
        """Execute parsed query and return results"""

    def format_response(self, results: Dict) -> str:
        """Format results for chat display"""
```

---

## Success Metrics

1. **Page Load**: < 2 seconds
2. **Scan Execution**: < 1 second (100 results)
3. **Greeks Update**: < 200ms
4. **Strategy Ranking**: < 500ms
5. **AI Consensus**: < 5 seconds
6. **Zero crashes** under normal load

---

## Timeline

- **Day 1-2**: Core foundation (positions manager, unified analyzer)
- **Day 2-3**: UI layout (three-panel design)
- **Day 3-4**: Analysis features (screening, strategies, Greeks, P&L)
- **Day 4-5**: Advanced features (flow, earnings, IV, POP)
- **Day 5-6**: AVA integration
- **Day 6-7**: Polish, optimization, testing

**Total**: 7 days for full implementation

---

## Immediate Next Steps

1. ✅ Research complete
2. ✅ Specification documented
3. → Build positions manager
4. → Create unified analyzer core
5. → Build three-panel UI
6. → Integrate all features
7. → Test and deploy

---

## Questions to Resolve

1. Should we archive old pages or delete them?
2. Default scan filters (DTE, delta)?
3. Which LLM provider as default for AI consensus?
4. How many top results to show in AVA chat (3, 5, 10)?
5. Should positions auto-refresh on page load?
6. Mobile-first or desktop-first design?
7. Export format (CSV, JSON, PDF)?

Let's proceed with implementation!
