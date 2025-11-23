

# AI Position Recommendation System - Quick Start Guide

## Overview

This guide will help you integrate the AI-powered position recommendation system into your options trading dashboard in under 30 minutes.

## System Capabilities

- **Real-time Analysis**: Get actionable recommendations for every option position
- **Hybrid Intelligence**: Combines rule-based quantitative analysis with LLM reasoning
- **Cost-Optimized**: Tiered model selection keeps costs under $5/month
- **Multi-Model Support**: Claude, GPT-4, Gemini, local Llama3
- **Rich UI**: Beautiful Streamlit cards with confidence badges and action buttons

## Prerequisites

1. **Existing Installation**: You should already have the base system installed
2. **API Keys** (at least one):
   - `ANTHROPIC_API_KEY` (recommended - most cost-effective)
   - `OPENAI_API_KEY` (optional)
   - `GOOGLE_API_KEY` (optional for Gemini)
3. **Database**: PostgreSQL running (already configured)
4. **Robinhood**: Active account with positions

## Installation Steps

### Step 1: Install Additional Dependencies

```bash
# Update requirements.txt with new packages
pip install py_vollib==1.0.1
pip install polygon-api-client==1.12.4  # Optional for real-time Greeks
pip install finnhub-python==2.4.18      # Optional for news sentiment
```

### Step 2: Set Up API Keys

Add to your `.env` file:

```bash
# AI Models (choose at least one)
ANTHROPIC_API_KEY=sk-ant-xxxxx  # Recommended
OPENAI_API_KEY=sk-xxxxx         # Optional
GOOGLE_API_KEY=xxxxx            # Optional

# Market Data (optional - yfinance is free and already works)
POLYGON_API_KEY=xxxxx    # Optional for real-time Greeks
FINNHUB_API_KEY=xxxxx    # Optional for news sentiment
```

### Step 3: Test Core Components

**Test 1: Position Data Aggregator**

```bash
python src/ai/position_data_aggregator.py
```

Expected output:
```
===============================================================================
POSITION DATA AGGREGATOR TEST
===============================================================================

Fetched 5 positions

AAPL $150 CSP
  P/L: $125.00 (+50.0%)
  Stock: $165.50 (+2.30%)
  DTE: 40 | Moneyness: OTM
  Greeks: Δ=-0.15 Θ=2.50
```

**Test 2: Quantitative Analyzer**

```bash
python src/ai/position_quantitative_analyzer.py
```

Expected output:
```
===============================================================================
QUANTITATIVE ANALYZER TEST
===============================================================================

Position: AAPL $150 CSP
P/L: $125.00 (+50.0%)
DTE: 40 | Moneyness: OTM

===============================================================================
QUANTITATIVE ANALYSIS
===============================================================================
Recommendation: CLOSE_NOW
Confidence: 85%
Risk Level: LOW

Reasoning: Position is up 50.0%, exceeding profit target. Lock in gains.
```

**Test 3: LLM Analyzer (requires API key)**

```bash
python src/ai/position_llm_analyzer.py
```

Expected output:
```
===============================================================================
LLM POSITION ANALYZER TEST
===============================================================================

Analyzing: AAPL $150 CSP
P/L: $125.00 (+50.0%)
DTE: 40 | Moneyness: OTM

===============================================================================
RECOMMENDATION
===============================================================================
Action: CLOSE_NOW
Confidence: 87%
Risk Level: LOW
Urgency: MEDIUM

Rationale: Position has reached 50% profit target with strong bullish
momentum. Recommend closing to lock in gains before potential reversal.

Key Factors:
  - Achieved profit target at 50%+
  - Stock trading 10% above strike
  - Low volatility environment (IV Rank: 25)

Model Used: claude-3-5-sonnet
Cost: $0.0135
```

**Test 4: Recommendation Aggregator**

```bash
python src/ai/position_recommendation_aggregator.py
```

This will test the full pipeline combining quant + LLM analysis.

### Step 4: Update Positions Page

Edit `positions_page_improved.py` to integrate recommendations:

```python
# Add to imports
from src.ai.position_recommendation_aggregator import (
    PositionRecommendationAggregator,
    analyze_portfolio
)
from src.ai.position_data_aggregator import PositionDataAggregator
from src.components.ai_recommendation_card import render_ai_recommendation_card
import asyncio

# Add to show_positions_page() function after displaying positions table

# AI Recommendations Section
st.markdown("---")
st.subheader("🤖 AI Position Recommendations")

# Toggle for enabling AI analysis
enable_ai = st.checkbox(
    "Enable AI Analysis (uses LLM API)",
    value=st.session_state.get('enable_ai_recs', True),
    help="Disable to use only rule-based quantitative analysis (no API costs)"
)
st.session_state.enable_ai_recs = enable_ai

if st.button("🔄 Generate Recommendations", type="primary"):
    with st.spinner("Analyzing positions..."):
        try:
            # Fetch and enrich positions
            aggregator_obj = PositionDataAggregator()
            enriched_positions = aggregator_obj.fetch_all_positions()

            if not enriched_positions:
                st.warning("No positions found")
            else:
                # Analyze portfolio
                recommendations = asyncio.run(
                    analyze_portfolio(enriched_positions, use_llm=enable_ai)
                )

                # Store in session state
                st.session_state.recommendations = recommendations
                st.session_state.enriched_positions = enriched_positions

                st.success(f"Analyzed {len(recommendations)} positions")

        except Exception as e:
            st.error(f"Error generating recommendations: {e}")

# Display recommendations if available
if 'recommendations' in st.session_state and 'enriched_positions' in st.session_state:
    recommendations = st.session_state.recommendations
    positions = st.session_state.enriched_positions

    # Display each recommendation
    for i, (pos, rec) in enumerate(zip(positions, recommendations)):
        with st.expander(
            f"{pos.symbol} ${pos.strike} {pos.position_type} - "
            f"{'🟢' if pos.pnl_dollar > 0 else '🔴'} ${pos.pnl_dollar:.2f}",
            expanded=(i == 0)  # Expand first position
        ):
            # Show position details
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Stock Price", f"${pos.stock_price:.2f}")
            with col2:
                st.metric("Strike", f"${pos.strike:.2f}")
            with col3:
                st.metric("DTE", pos.dte)
            with col4:
                st.metric("P/L", f"{pos.pnl_percent:+.1f}%")

            # Render AI recommendation card
            render_ai_recommendation_card(
                position=pos.to_dict(),
                recommendation=rec.to_dict(),
                expanded=True
            )
```

### Step 5: Test in Dashboard

```bash
streamlit run dashboard.py
```

Navigate to the Positions page and click "Generate Recommendations"

## Configuration

### Adjust Model Selection

Edit `config/services.yaml`:

```yaml
ai_recommendations:
  model_strategy: 'tiered'  # 'tiered', 'single', 'ensemble'

  models:
    critical: 'claude'   # For losing positions
    standard: 'gemini'   # For routine analysis (cheaper)
    bulk: 'llama3'       # For stable positions (free, if Ollama installed)

  # Cost controls
  budget:
    daily_limit: 2.00    # USD
    monthly_limit: 50.00
```

### Customize Thresholds

Edit `src/ai/position_quantitative_analyzer.py`:

```python
THRESHOLDS = {
    'profit_target_pct': 50,      # Take profit at 50% of max
    'loss_threshold_pct': -100,   # Cut loss at -100%
    'roll_dte': 7,                # Roll when DTE < 7
    'critical_dte': 3,            # Critical action needed
}
```

## Cost Management

### Expected Costs

| Scenario | Daily Cost | Monthly Cost |
|----------|-----------|--------------|
| 5 positions, 3 refreshes/day, all Claude | $0.20 | $6.00 |
| 10 positions, 3 refreshes/day, mixed strategy | $0.25 | $7.50 |
| 25 positions, 3 refreshes/day, with caching | $0.50 | $15.00 |
| Quant-only (no LLM) | $0.00 | $0.00 |

### View Cost Dashboard

```python
from src.ai.cost_tracker import CostTracker

tracker = CostTracker()
print(tracker.generate_report(days=7))
```

Output:
```
================================================================================
KALSHI AI COST REPORT
================================================================================
Period: Last 7 days
Generated: 2025-11-10 14:30:00

SUMMARY
-------
Total Cost: $1.25
Total Requests: 45
Avg Cost/Request: $0.0278

BUDGET STATUS
-------------
Daily    $   0.18 / $   2.00 ( 9.0%) [OK]
Weekly   $   1.25 / $   7.00 (17.9%) [OK]
Monthly  $   5.00 / $  50.00 (10.0%) [OK]

USAGE BY MODEL
--------------------------------------------------------------------------------
claude-3.5-sonnet     $   0.75     15 requests
gemini-pro            $   0.30     20 requests
llama3:70b            $   0.00     10 requests

OPTIMIZATION RECOMMENDATIONS
--------------------------------------------------------------------------------
1. Usage is within optimal parameters. No changes needed.
```

## Advanced Features

### 1. Portfolio-Level Analysis

```python
from src.ai.position_recommendation_aggregator import analyze_portfolio

# Get recommendations for all positions
recommendations = await analyze_portfolio(positions, use_llm=True)

# Filter high-urgency recommendations
urgent = [rec for rec in recommendations if rec.urgency == 'high']

# Show summary
for rec in urgent:
    print(f"{rec.symbol}: {rec.action} - {rec.rationale}")
```

### 2. Historical Tracking

Track recommendation performance in database:

```sql
CREATE TABLE position_recommendation_history (
    id SERIAL PRIMARY KEY,
    position_id VARCHAR(100),
    recommendation_action VARCHAR(50),
    confidence INTEGER,
    quant_signal VARCHAR(50),
    llm_signal VARCHAR(50),
    position_pnl_at_time DECIMAL(10,2),
    followed BOOLEAN DEFAULT FALSE,
    outcome_pnl DECIMAL(10,2),
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);
```

### 3. Custom Prompts

Modify `src/ai/position_llm_analyzer.py` to customize prompts:

```python
def _build_position_analysis_prompt(self, position, quant_analysis, market_context):
    # Add your custom context
    custom_context = f"""
    TRADING STRATEGY: Conservative wheel strategy
    MAX LOSS TOLERANCE: -$500 per position
    PROFIT TARGET: 50% of max profit
    """

    prompt = f"""
    {custom_context}

    === POSITION DETAILS ===
    {position.symbol} {position.position_type}
    ...
    """

    return prompt
```

### 4. Telegram Alerts

Integrate with existing Telegram bot:

```python
from src.ava.telegram_bot import send_message

async def send_urgent_recommendations(recommendations):
    urgent = [r for r in recommendations if r.urgency == 'high']

    if urgent:
        message = "🚨 URGENT POSITION ALERTS 🚨\n\n"

        for rec in urgent:
            message += f"**{rec.symbol}** {rec.position_type}\n"
            message += f"Action: {rec.action.upper()}\n"
            message += f"Reason: {rec.rationale}\n\n"

        await send_message(message)
```

## Troubleshooting

### Issue: "No positions found"

**Solution**: Ensure you're logged into Robinhood and have active option positions.

```python
# Test login
import robin_stocks.robinhood as rh
rh.login(username='your_email', password='your_password')
print(rh.get_open_option_positions())
```

### Issue: "LLM API error"

**Solution**: Check API key is set correctly:

```python
import os
print(os.getenv('ANTHROPIC_API_KEY'))  # Should not be None
```

If None, add to `.env` file.

### Issue: "mibian import error"

**Solution**: Greeks calculation requires mibian:

```bash
pip install mibian==0.1.3
```

### Issue: "Slow analysis (>10 seconds)"

**Solution**: Enable caching in `config/services.yaml`:

```yaml
ai_recommendations:
  cache_ttl:
    position_data: 300      # 5 minutes
    llm_response: 1800      # 30 minutes
```

### Issue: "Costs too high"

**Solution**:

1. Switch to cheaper models (Gemini instead of Claude):
   ```yaml
   models:
     standard: 'gemini'  # $0.0018 per analysis
   ```

2. Disable LLM for stable positions:
   ```python
   # Only use LLM for losing or risky positions
   use_llm = position.pnl_percent < -20 or position.dte < 7
   ```

3. Increase cache TTL:
   ```yaml
   cache_ttl:
     llm_response: 3600  # 1 hour instead of 30 min
   ```

## Performance Benchmarks

| Operation | Time | Cost |
|-----------|------|------|
| Fetch position data | 2-3s | $0 |
| Quantitative analysis | <100ms | $0 |
| LLM analysis (Claude) | 2-4s | $0.0135 |
| LLM analysis (Gemini) | 1-2s | $0.0018 |
| Full portfolio (10 positions) | 8-12s | $0.05-$0.15 |

## Best Practices

1. **Start with Quant-Only**: Test the system without LLM costs first
2. **Use Tiered Strategy**: Reserve expensive models for critical positions
3. **Cache Aggressively**: 30-minute cache is usually sufficient
4. **Review Daily**: Generate recommendations once per day, not every page load
5. **Track Performance**: Monitor which recommendations lead to good outcomes
6. **Set Budgets**: Use cost tracker alerts to avoid overspending

## Next Steps

1. **Integrate with Auto-Trading**: Connect recommendations to execution engine
2. **Backtest Strategies**: Test recommendation strategies on historical data
3. **Personalize Prompts**: Adjust for your risk tolerance and trading style
4. **Add Notifications**: Alert on high-urgency recommendations
5. **Build Dashboard**: Create portfolio-level recommendation analytics

## Support

- **Documentation**: `docs/ai/position_recommendation_system_architecture.md`
- **Cost Tracking**: `python src/ai/cost_tracker.py`
- **Test Suite**: `pytest tests/test_position_recommendations.py`

## Example Output

```
═══════════════════════════════════════════════════════════════════
PORTFOLIO RECOMMENDATIONS SUMMARY
═══════════════════════════════════════════════════════════════════

💰 Close Now: 3 positions
✋ Hold: 5 positions
🔄 Roll: 2 positions
🚨 Urgent Actions: 1 position

⚠️ 1 position requires immediate attention:

AAPL $150 CSP
🔄 ROLL OUT | 90% Confidence | HIGH Urgency
Rationale: 5 DTE remaining with position ATM. Roll to avoid assignment
and collect additional premium. Target next monthly expiration.

Key Factors:
- Near expiration (5 DTE)
- Stock within 2% of strike
- High gamma risk detected

Expected Outcome: Extend duration and collect $1.50 additional credit
═══════════════════════════════════════════════════════════════════
```

---

**Ready to trade smarter with AI! 🚀**
