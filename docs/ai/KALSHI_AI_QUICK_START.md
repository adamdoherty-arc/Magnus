# Kalshi AI Enhancement - Quick Start Guide

## Overview

This guide will get you up and running with the Kalshi AI enhancement system in under 30 minutes.

## Prerequisites

- Python 3.9+
- PostgreSQL database (already configured)
- API keys for AI models (at least one)

## Installation

### 1. Install Dependencies

```bash
# Core AI libraries
pip install openai anthropic google-generativeai

# Optional: Local model support
# Install Ollama from https://ollama.ai
# Then: ollama pull llama3:70b

# Async support
pip install aiohttp

# Already installed: psycopg2-binary, python-dotenv
```

### 2. Set Up Environment Variables

Add to your `.env` file:

```bash
# AI Model API Keys (get at least one)
OPENAI_API_KEY=sk-...          # Get from platform.openai.com
ANTHROPIC_API_KEY=sk-ant-...   # Get from console.anthropic.com
GOOGLE_API_KEY=...             # Get from makersuite.google.com

# Database (already configured)
DB_PASSWORD=your_db_password
```

### 3. Initialize Database Schema

```python
from src.ai.cost_tracker import CostTracker

# This will create the necessary tables
tracker = CostTracker()
```

Or run the SQL directly:

```bash
psql -U postgres -d magnus -f docs/ai/kalshi_ai_schema.sql
```

## Basic Usage

### Example 1: Simple Market Analysis (Single Model)

```python
import asyncio
from src.ai.model_clients import GPT4Client
from src.ai.prompt_templates import build_market_analysis_prompt

async def analyze_single_market():
    # Market data
    market = {
        'ticker': 'NFL-KC-BUF-001',
        'title': 'Will the Chiefs beat the Bills?',
        'yes_price': 0.52,
        'no_price': 0.48,
        'volume': 125000,
        'open_interest': 8500,
        'close_time': '2025-11-10T13:00:00Z'
    }

    # Build prompt
    prompt = build_market_analysis_prompt(market)

    # Get prediction
    client = GPT4Client()
    response = await client.analyze_market(prompt)

    print(response['content'])

asyncio.run(analyze_single_market())
```

### Example 2: Multi-Model Ensemble (Recommended)

```python
import asyncio
from src.ai.kalshi_ensemble import KalshiEnsemble

async def analyze_with_ensemble():
    # Initialize ensemble in 'fast' mode (GPT-4 + Gemini)
    ensemble = KalshiEnsemble(mode='fast')

    # Market data
    market = {
        'ticker': 'NFL-KC-BUF-001',
        'title': 'Will the Chiefs beat the Bills?',
        'yes_price': 0.52,
        'no_price': 0.48,
        'volume': 125000,
        'open_interest': 8500,
        'close_time': '2025-11-10T13:00:00Z'
    }

    # Optional context
    context = {
        'weather': {
            'temp': 38,
            'wind_speed': 12,
            'conditions': 'Cloudy'
        }
    }

    # Get consensus prediction
    prediction = await ensemble.predict(market, context)

    print(f"Outcome: {prediction.predicted_outcome}")
    print(f"Confidence: {prediction.confidence}%")
    print(f"Edge: {prediction.edge_percentage}%")
    print(f"Recommendation: {prediction.recommended_action}")
    print(f"Stake: {prediction.recommended_stake_pct}%")
    print(f"\nReasoning: {prediction.reasoning}")

asyncio.run(analyze_with_ensemble())
```

### Example 3: Batch Analysis with Cost Tracking

```python
import asyncio
from src.ai.kalshi_ensemble import KalshiEnsemble
from src.ai.cost_tracker import CostTracker
from src.kalshi_db_manager import KalshiDBManager

async def batch_analyze_markets():
    # Initialize
    ensemble = KalshiEnsemble(mode='balanced')
    tracker = CostTracker()
    db = KalshiDBManager()

    # Get active markets from database
    markets = db.get_active_markets(market_type='nfl')

    print(f"Analyzing {len(markets)} markets...")

    predictions = []
    for market in markets[:10]:  # Limit to 10 for demo
        try:
            # Get prediction
            pred = await ensemble.predict(market)
            predictions.append({
                'ticker': market['ticker'],
                'predicted_outcome': pred.predicted_outcome,
                'confidence_score': pred.confidence,
                'edge_percentage': pred.edge_percentage,
                'recommended_action': pred.recommended_action,
                'reasoning': pred.reasoning
            })

            # Log cost (if using real APIs)
            for model_pred in pred.individual_predictions:
                if 'usage' in model_pred.raw_response:
                    usage = model_pred.raw_response['usage']
                    tracker.log_usage(
                        model_name=model_pred.model_name,
                        input_tokens=usage.get('input_tokens', 0),
                        output_tokens=usage.get('output_tokens', 0),
                        market_ticker=market['ticker']
                    )

            print(f"✓ {market['ticker']}: {pred.predicted_outcome} "
                  f"({pred.confidence}% conf, {pred.edge_percentage}% edge)")

        except Exception as e:
            print(f"✗ {market['ticker']}: Error - {e}")

    # Store predictions in database
    db.store_predictions(predictions)

    # Print cost summary
    print(f"\n{tracker.generate_report(days=1)}")

asyncio.run(batch_analyze_markets())
```

## Ensemble Modes

Choose the mode that fits your needs:

| Mode | Models | Speed | Cost/Market | Use Case |
|------|--------|-------|-------------|----------|
| **cost** | Gemini + Llama3 | Fast | $0.002 | High volume, budget-conscious |
| **fast** | GPT-4 + Gemini | Medium | $0.037 | Balanced speed and accuracy |
| **balanced** | GPT-4 + Claude + Gemini | Slow | $0.050 | **Default - Best accuracy** |
| **premium** | All 4 models | Slowest | $0.050 | Maximum confidence needed |

```python
# Switch modes based on your needs
ensemble = KalshiEnsemble(mode='cost')     # Cheap & fast
ensemble = KalshiEnsemble(mode='fast')     # Good balance
ensemble = KalshiEnsemble(mode='balanced') # Best accuracy (default)
ensemble = KalshiEnsemble(mode='premium')  # Maximum confidence
```

## Testing Without API Keys

If you don't have API keys yet, use mock mode for testing:

```python
from src.ai.model_clients import MockModelClient
from src.ai.kalshi_ensemble import KalshiEnsemble

# Option 1: Mock individual client
client = MockModelClient('gpt4')
response = await client.analyze_market(prompt)

# Option 2: Test ensemble with mock clients (modify ensemble.py)
# Set mock=True in get_model_client() calls
```

## Cost Management

### Set Budget Limits

```python
from src.ai.cost_tracker import CostTracker

tracker = CostTracker()

# Set custom budgets
tracker.set_budget('daily', 100.00)    # $100/day
tracker.set_budget('weekly', 600.00)   # $600/week
tracker.set_budget('monthly', 2000.00) # $2000/month
```

### Monitor Spending

```python
# Get current spending
daily_spend = tracker.get_spending('daily')
weekly_spend = tracker.get_spending('weekly')

print(f"Today: ${daily_spend:.2f}")
print(f"This week: ${weekly_spend:.2f}")

# Get detailed report
print(tracker.generate_report(days=7))

# Get optimization tips
for tip in tracker.get_optimization_recommendations():
    print(f"💡 {tip}")
```

### Estimate Costs Before Running

```python
ensemble = KalshiEnsemble(mode='balanced')

# Estimate cost for 100 markets
cost_estimate = ensemble.get_cost_estimate(100)

print(f"Total cost: ${cost_estimate['total_cost']:.2f}")
print(f"Per market: ${cost_estimate['cost_per_market']:.4f}")
print(f"Breakdown: {cost_estimate['breakdown']}")
```

## Integration with Existing System

### Update Your Sync Script

Modify `sync_kalshi_markets.py`:

```python
import asyncio
from src.kalshi_client import KalshiClient
from src.kalshi_db_manager import KalshiDBManager
from src.ai.kalshi_ensemble import KalshiEnsemble

async def sync_and_analyze():
    # Existing code
    client = KalshiClient()
    db = KalshiDBManager()

    # Fetch markets
    markets = client.get_football_markets()

    # Store markets
    db.store_markets(markets['nfl'], 'nfl')

    # NEW: Analyze with AI
    ensemble = KalshiEnsemble(mode='fast')

    active_markets = db.get_active_markets('nfl')
    predictions = []

    for market in active_markets:
        pred = await ensemble.predict(market)
        predictions.append({
            'ticker': market['ticker'],
            'predicted_outcome': pred.predicted_outcome,
            'confidence_score': pred.confidence,
            'edge_percentage': pred.edge_percentage,
            # ... other fields
        })

    # Store predictions
    db.store_predictions(predictions)

if __name__ == "__main__":
    asyncio.run(sync_and_analyze())
```

### Display in Streamlit Dashboard

Create `kalshi_ai_dashboard_page.py`:

```python
import streamlit as st
from src.kalshi_db_manager import KalshiDBManager

st.title("🏈 Kalshi NFL AI Predictions")

db = KalshiDBManager()

# Get top opportunities
opportunities = db.get_top_opportunities(limit=20)

for opp in opportunities:
    with st.expander(f"#{opp['overall_rank']} - {opp['title'][:60]}..."):
        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Predicted", opp['predicted_outcome'].upper())
            st.metric("Confidence", f"{opp['confidence_score']:.0f}%")

        with col2:
            st.metric("Edge", f"{opp['edge_percentage']:.1f}%")
            st.metric("Action", opp['recommended_action'].upper())

        with col3:
            st.metric("Stake", f"{opp['recommended_stake_pct']:.1f}%")
            st.metric("Price", f"${opp['yes_price']:.2f}")

        st.write("**Reasoning:**", opp['reasoning'])

        st.write("**Key Factors:**")
        for factor in opp['key_factors']:
            st.write(f"- {factor}")
```

## Troubleshooting

### Issue: "API key not found"

**Solution:** Make sure your `.env` file has the correct API keys:

```bash
# Check if .env is loaded
from dotenv import load_dotenv
import os

load_dotenv()
print(os.getenv('OPENAI_API_KEY'))  # Should not be None
```

### Issue: "No module named 'openai'"

**Solution:** Install the required packages:

```bash
pip install openai anthropic google-generativeai
```

### Issue: "Database connection failed"

**Solution:** Verify your database credentials in `.env`:

```bash
DB_PASSWORD=your_password

# Test connection
from src.kalshi_db_manager import KalshiDBManager
db = KalshiDBManager()
stats = db.get_stats()
print(stats)
```

### Issue: "Cost too high"

**Solution:** Switch to a cheaper mode:

```python
# Instead of 'balanced' (default)
ensemble = KalshiEnsemble(mode='cost')  # 95% cheaper!

# Or limit analysis to high-value markets only
markets = [m for m in markets if m['volume'] > 50000]
```

## Next Steps

1. **Add More Context:** Integrate weather, injury, and sentiment data
2. **Implement Alerts:** Connect to Telegram bot for notifications
3. **Build ML Pipeline:** Train models on historical data
4. **Set Up Automation:** Schedule regular analysis runs

See the full implementation guide in `KALSHI_AI_ENHANCEMENT_STRATEGY.md` for details.

## API Key Setup Links

- **OpenAI (GPT-4):** https://platform.openai.com/api-keys
- **Anthropic (Claude):** https://console.anthropic.com/
- **Google (Gemini):** https://makersuite.google.com/app/apikey
- **Ollama (Local):** https://ollama.ai/ (no API key needed)

## Cost Reference

Based on 581 NFL markets analyzed 3x per day:

| Mode | Daily Cost | Weekly Cost | Season Cost (18 weeks) |
|------|-----------|-------------|------------------------|
| **Cost** | $3.49 | $24.43 | $628 |
| **Fast** | $64.49 | $451.43 | $11,608 |
| **Balanced** | $87.59 | $613.13 | $15,777 |
| **Premium** | $87.09 | $609.63 | $15,676 |

**Recommended:** Start with **fast** mode for best price/performance balance.

## Support

For questions or issues:
1. Check the main strategy document: `KALSHI_AI_ENHANCEMENT_STRATEGY.md`
2. Review code examples in `src/ai/` directory
3. Run tests with mock clients to verify setup

---

**Last Updated:** 2025-11-09
**Version:** 1.0
