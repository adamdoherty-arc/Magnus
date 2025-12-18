# Portfolio Agent - User Guide

## Overview

The PortfolioAgent is a comprehensive portfolio management and analysis tool for the Magnus AVA chatbot. It integrates with Robinhood API for real-time position data and uses local LLM (Ollama) for intelligent analysis and recommendations.

## Features

### 1. Real-Time Portfolio Metrics
- Total portfolio value
- Cash and buying power
- Position count (stocks and options)
- Total P&L and P&L percentage
- Greeks exposure (Delta, Gamma, Theta, Vega)
- Concentration and diversification metrics

### 2. Risk Assessment
- Overall risk level (low, medium, high, critical)
- Risk score (0-100)
- Concentration risk analysis
- Greeks exposure warnings
- Liquidity concerns
- Actionable recommendations

### 3. Sector Allocation
- Breakdown by symbol/sector
- Value and percentage allocation
- Position count per sector
- Diversification analysis

### 4. AI-Powered Recommendations
- Portfolio health assessment
- Rebalancing suggestions
- Hedging strategies
- Risk mitigation priorities
- Optimization opportunities

### 5. Greeks Analysis
- Aggregated portfolio Greeks
- Delta exposure (directional risk)
- Theta exposure (time decay)
- Gamma exposure (delta sensitivity)
- Vega exposure (IV sensitivity)

## Usage Examples

### Basic Usage

```python
from src.ava.agents.trading.portfolio_agent import PortfolioAgent
import asyncio

async def main():
    # Initialize agent
    agent = PortfolioAgent()

    # Get portfolio metrics
    metrics = await agent.get_portfolio_metrics()
    print(f"Total Value: ${metrics.total_value:,.2f}")
    print(f"Net Delta: {metrics.net_delta:.2f}")

    # Assess risk
    risk = await agent.assess_portfolio_risk()
    print(f"Risk Level: {risk.overall_risk_level}")

    # Get AI recommendations
    recommendations = await agent.generate_ai_recommendations()
    print(recommendations)

asyncio.run(main())
```

### Using with AVA State

```python
from src.ava.core.agent_base import AgentState

# Create state
state: AgentState = {
    'input': 'What is my portfolio risk?',
    'context': {},
    'tools': [],
    'result': None,
    'error': None,
    'metadata': {}
}

# Execute agent
result_state = await agent.execute(state)

# Access results
if result_state['error']:
    print(f"Error: {result_state['error']}")
else:
    print(result_state['result'])
```

### Specific Analysis Types

```python
# Portfolio summary
state['input'] = 'Give me a portfolio summary'
result = await agent.execute(state)

# Risk assessment
state['input'] = 'Assess my portfolio risk'
result = await agent.execute(state)

# Greeks analysis
state['input'] = 'What is my Greeks exposure?'
result = await agent.execute(state)

# Hedging strategies
state['input'] = 'Suggest hedging strategies'
result = await agent.execute(state)

# Rebalancing recommendations
state['input'] = 'Should I rebalance my portfolio?'
result = await agent.execute(state)
```

## Data Models

### PortfolioMetrics

```python
@dataclass
class PortfolioMetrics:
    total_value: float              # Total portfolio value
    cash: float                     # Cash available
    buying_power: float             # Buying power
    total_positions_value: float    # Total value of positions
    total_pnl: float               # Total profit/loss
    total_pnl_pct: float           # P&L percentage
    num_positions: int             # Number of positions
    num_stock_positions: int       # Stock positions
    num_options_positions: int     # Options positions

    # Greeks
    net_delta: float               # Aggregated delta
    net_gamma: float               # Aggregated gamma
    net_theta: float               # Aggregated theta ($/day)
    net_vega: float                # Aggregated vega

    # Risk metrics
    concentration_risk: float      # Largest position %
    sector_diversity: float        # Number of sectors
    options_exposure_pct: float    # Options as % of total
```

### RiskAssessment

```python
@dataclass
class RiskAssessment:
    overall_risk_level: str        # 'low', 'medium', 'high', 'critical'
    risk_score: int                # 0-100
    concentration_issues: List[str]
    correlation_warnings: List[str]
    greeks_warnings: List[str]
    liquidity_concerns: List[str]
    recommendations: List[str]
```

### SectorAllocation

```python
@dataclass
class SectorAllocation:
    sector: str                    # Sector name
    value: float                   # Dollar value
    percentage: float              # Percentage of portfolio
    num_positions: int             # Number of positions
    symbols: List[str]             # Stock symbols
```

## Configuration

### Environment Variables

Ensure these are set in your `.env` file:

```bash
# Robinhood credentials
ROBINHOOD_USERNAME=your_username
ROBINHOOD_PASSWORD=your_password
ROBINHOOD_MFA_CODE=your_mfa_secret  # Optional

# Ollama (for AI recommendations)
OLLAMA_HOST=http://localhost:11434  # Default
```

### Caching

The agent caches results for 5 minutes to improve performance:

```python
# Default cache TTL is 5 minutes
agent._cache_ttl = timedelta(minutes=5)

# Clear cache manually if needed
agent._cache.clear()
```

## Greeks Calculation

The agent calculates simplified Greeks estimates based on:
- Strike price vs current price (moneyness)
- Option type (call/put)
- Position type (long/short)
- Quantity

**Note:** For production use, integrate with real-time options data APIs for accurate Greeks.

### Delta Calculation
- Calls: Delta ≈ 0.1 to 0.9 based on moneyness
- Puts: Delta ≈ -0.1 to -0.9 based on moneyness
- Adjusted for long/short position

### Theta Calculation
- Simplified: -$0.02 per contract per day
- Would need actual expiration data for precision

### Gamma & Vega
- Highest for at-the-money options
- Estimated based on moneyness

## Risk Assessment Logic

Risk scores are calculated based on:

| Factor | Threshold | Risk Points |
|--------|-----------|-------------|
| Concentration > 50% | Single position | +30 |
| Concentration > 30% | Single position | +15 |
| Net Delta > 100 | Directional risk | +20 |
| Options > 50% | Portfolio exposure | +25 |
| Positions < 3 | Low diversity | +15 |

Risk Levels:
- **Low:** Score < 25
- **Medium:** Score 25-49
- **High:** Score 50-69
- **Critical:** Score ≥ 70

## AI Analysis Features

The agent uses local LLM (Qwen 2.5 32B by default) to generate:

1. **Portfolio Health Assessment**
   - Overall portfolio condition
   - Strengths and weaknesses
   - Alignment with strategy goals

2. **Rebalancing Recommendations**
   - Specific positions to adjust
   - Size recommendations
   - Timing considerations

3. **Hedging Strategies**
   - Delta hedging techniques
   - Protective puts/calls
   - Spread strategies
   - Cost-benefit analysis

4. **Risk Mitigation**
   - Priority action items
   - Concentration reduction
   - Diversification suggestions

5. **Return Optimization**
   - Income enhancement opportunities
   - Premium collection strategies
   - Wheel strategy alignment

## Integration Points

### With Other Agents

```python
# Risk Management Agent
from src.ava.agents.trading.risk_management_agent import RiskManagementAgent

risk_agent = RiskManagementAgent()
portfolio_agent = PortfolioAgent()

# Get portfolio metrics for risk validation
metrics = await portfolio_agent.get_portfolio_metrics()
# Use in trade validation
trade_validation = await risk_agent.validate_trade(trade_data, metrics)
```

### With AVA Chatbot

```python
# In AVA orchestrator
if 'portfolio' in user_query or 'positions' in user_query:
    portfolio_agent = PortfolioAgent()
    state = {
        'input': user_query,
        'context': {'user_id': user_id},
        'tools': [],
        'result': None,
        'error': None,
        'metadata': {}
    }
    result = await portfolio_agent.execute(state)
    return result['result']
```

## Testing

Run the built-in test suite:

```bash
cd c:\code\Magnus
python -m src.ava.agents.trading.portfolio_agent
```

Expected output:
```
Testing Portfolio Agent
================================================================================

1. Getting Portfolio Metrics...
   Total Value: $X,XXX.XX
   Total P&L: $XXX.XX (X.XX%)
   Positions: X
   Net Delta: XX.XX
   Net Theta: $X.XX/day
   ✓ Success

2. Assessing Portfolio Risk...
   Risk Level: MEDIUM
   Risk Score: XX/100
   Recommendations: X
   ✓ Success

3. Generating AI Recommendations...
   Generated XXXX characters of analysis
   ✓ Success

================================================================================
Portfolio Agent testing complete!
```

## Troubleshooting

### Robinhood Login Issues
```python
# Force fresh login
agent._get_robinhood_client().login(force_fresh=True)
```

### Cache Issues
```python
# Clear cache
agent._cache.clear()
agent._cache_expiry.clear()
```

### LLM Connection Issues
```python
# Verify Ollama is running
import requests
response = requests.get('http://localhost:11434/api/tags')
print(response.json())

# Initialize LLM manually
from src.magnus_local_llm import get_magnus_llm
llm = get_magnus_llm()
```

## Performance Optimization

1. **Caching**: Results cached for 5 minutes
2. **Async Operations**: All I/O is async
3. **Batch Requests**: Multiple metrics calculated in single pass
4. **Simplified Greeks**: Estimates instead of full Black-Scholes

## Future Enhancements

- [ ] Real-time Greeks from options data API
- [ ] Historical performance tracking
- [ ] Correlation analysis between positions
- [ ] Sector mapping integration
- [ ] Portfolio backtesting
- [ ] Custom risk thresholds
- [ ] Multi-account support
- [ ] Tax-loss harvesting suggestions
- [ ] Dividend tracking

## API Reference

### Core Methods

#### `get_portfolio_metrics() -> PortfolioMetrics`
Returns comprehensive portfolio metrics including value, P&L, and Greeks.

#### `assess_portfolio_risk() -> RiskAssessment`
Analyzes portfolio risk and provides risk score with recommendations.

#### `get_sector_allocation() -> List[SectorAllocation]`
Returns sector/symbol allocation breakdown.

#### `generate_ai_recommendations(context: Optional[Dict] = None) -> str`
Generates AI-powered portfolio analysis and recommendations.

#### `suggest_hedging_strategies() -> str`
Suggests specific hedging strategies based on Greeks exposure.

#### `execute(state: AgentState) -> AgentState`
Main execution method for AVA integration.

### Helper Methods

#### `_calculate_greeks_exposure(options_positions: List[Dict]) -> Dict[str, float]`
Calculates aggregated Greeks across all options positions.

#### `_calculate_concentration_risk(positions: List[Dict]) -> float`
Calculates concentration risk as percentage of largest position.

#### `_get_cached(key: str) -> Optional[Any]`
Retrieves cached value if not expired.

#### `_set_cache(key: str, value: Any)`
Sets cached value with expiry timestamp.

## License

Part of the Magnus Trading Platform. See main project LICENSE.

## Support

For issues or questions:
1. Check this documentation
2. Review test cases in the source file
3. Check AVA agent logs
4. Consult Magnus project documentation
