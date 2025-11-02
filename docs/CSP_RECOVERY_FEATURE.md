# CSP Recovery & Roll Strategy Feature Documentation

## Overview

The CSP Recovery & Roll Strategy Feature provides intelligent recommendations for managing losing Cash Secured Put (CSP) positions. It analyzes your losing positions and suggests optimal recovery strategies including new CSP opportunities, roll strategies, and risk management actions.

## Features

### 1. CSP Recovery Analyzer
- Identifies all losing CSP positions (stock price below strike)
- Calculates support levels and IV rank
- Finds optimal recovery CSP opportunities at lower strikes
- Ranks opportunities by AI score based on:
  - Probability of profit (40% weight)
  - Premium yield (25% weight)
  - Recovery percentage (20% weight)
  - Strike distance from current price (15% weight)

### 2. Option Roll Evaluator
- Evaluates 4 strategies for each losing position:
  - **Roll Down**: Same expiration, lower strike
  - **Roll Out**: Same strike, later expiration
  - **Roll Down & Out**: Lower strike, later expiration
  - **Accept Assignment**: Take delivery and sell covered calls
- Calculates net credits/debits for each strategy
- Provides pros and cons for each option
- Generates AI recommendations with confidence levels

### 3. AI Options Advisor
- Fundamental analysis (P/E, growth, margins, earnings)
- Technical analysis (trend, RSI, MACD, support/resistance)
- Option Greeks analysis (delta, gamma, theta, vega, rho)
- Monte Carlo simulations for probability modeling
- Market conditions assessment (VIX, sector rotation)
- Generates comprehensive strategy recommendations

### 4. Recovery Strategies Tab UI
- Interactive Streamlit interface
- Sortable tables with color-coded metrics
- Expandable strategy comparison cards
- Risk dashboard with portfolio-level metrics
- Direct links to execute trades in Robinhood

## Installation

### Prerequisites
```bash
pip install pandas numpy yfinance scipy talib langchain streamlit plotly
```

### File Structure
```
src/
├── csp_recovery_analyzer.py    # Recovery opportunity finder
├── option_roll_evaluator.py    # Roll strategy evaluator
├── ai_options_advisor.py       # AI-powered recommendations
└── recovery_strategies_tab.py  # Streamlit UI component

positions_page_improved.py      # Modified to include recovery tab
test_recovery_strategies.py     # Test suite with sample data
```

## Usage

### In the Dashboard

1. Navigate to the **Positions** page
2. When you have losing CSP positions, a **"🎯 Recovery Strategies"** section will appear
3. Click to expand the recovery strategies interface
4. Use the tabs to explore:
   - **Recovery Opportunities**: New CSPs to buy at better strikes
   - **Roll Evaluations**: Compare roll strategies for each position
   - **AI Analysis**: Deep fundamental and technical analysis
   - **Risk Dashboard**: Portfolio-level risk metrics

### Programmatic Usage

```python
from src.csp_recovery_analyzer import CSPRecoveryAnalyzer
from src.option_roll_evaluator import OptionRollEvaluator
from src.ai_options_advisor import AIOptionsAdvisor

# Initialize analyzers
analyzer = CSPRecoveryAnalyzer()
evaluator = OptionRollEvaluator()
advisor = AIOptionsAdvisor()

# Example position
position = {
    'symbol': 'AAPL',
    'option_type': 'put',
    'position_type': 'short',
    'strike_price': 180,
    'current_price': 175,  # Stock below strike
    'average_price': 2.50,
    'quantity': -1,
    'expiration_date': '2024-01-19'
}

# Find recovery opportunities
losing_positions = analyzer.analyze_losing_positions([position])
opportunities = analyzer.find_recovery_opportunities(losing_positions[0])

# Evaluate roll strategies
comparison = evaluator.compare_strategies(losing_positions[0])
print(comparison['recommendation'])

# Get AI recommendation
recommendation = advisor.recommend_strategy(losing_positions[0], opportunities)
print(recommendation)
```

## Key Metrics Explained

### AI Score (0-100)
Composite score for ranking recovery opportunities:
- **80-100**: STRONG BUY - Excellent recovery potential
- **60-79**: BUY - Good balance of premium and safety
- **40-59**: CONSIDER - Moderate opportunity
- **Below 40**: WEAK - Limited recovery potential

### Probability of Profit
Calculated using Black-Scholes model, represents the probability that the option will expire worthless (favorable for sellers).

### Recovery Percentage
How much of your current loss could be recovered by the premium from the new position.

### Roll Strategy Scoring
Each roll strategy is scored based on:
- Probability of profit (30%)
- Net credit received (25%)
- Capital efficiency (20%)
- Time value (15%)
- Special bonuses (e.g., wheel opportunity)

## Configuration

### API Keys (Optional)
For enhanced AI recommendations, add your OpenAI API key:

```python
advisor = AIOptionsAdvisor(openai_api_key="your-api-key")
```

### Risk Parameters
Modify risk thresholds in the analyzer:

```python
analyzer = CSPRecoveryAnalyzer()
analyzer.risk_free_rate = 0.045  # Current risk-free rate
analyzer.trading_days = 252      # Trading days per year
```

## Testing

Run the comprehensive test suite:

```bash
python test_recovery_strategies.py
```

This will test:
- CSP Recovery Analyzer with sample positions
- Option Roll Evaluator with all 4 strategies
- AI Options Advisor analysis capabilities
- Full integration of all components

## Performance Considerations

### Caching
- Option chain data is cached for 15 minutes
- Technical indicators are cached for 1 hour
- Fundamental data is cached for 24 hours

### API Rate Limits
- yfinance: No hard limit, but be respectful
- OpenAI: Depends on your tier (if using LLM features)
- Market data: Consider using batch requests

### Optimization Tips
1. Limit the number of strikes analyzed (default: 5)
2. Use broader expiration date ranges for fewer API calls
3. Cache frequently accessed symbols
4. Run analysis during market hours for accurate pricing

## Troubleshooting

### Common Issues

1. **No recovery opportunities found**
   - Check if options data is available for the symbol
   - Verify market hours (options pricing may be stale)
   - Ensure sufficient strikes exist below current price

2. **Roll strategies show as not feasible**
   - Verify option chain has future expirations
   - Check if the symbol has liquid options
   - Ensure position data is complete

3. **AI recommendations are generic**
   - Add OpenAI API key for enhanced analysis
   - Ensure internet connection for market data
   - Check if fundamental data is available

### Debug Mode

Enable detailed logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Future Enhancements

### Planned Features
1. **Multi-leg strategy builder**: Create complex recovery spreads
2. **Backtesting engine**: Test strategies on historical data
3. **Alert system**: Notifications for optimal roll timing
4. **Portfolio optimization**: Suggest portfolio-wide adjustments
5. **Machine learning**: Train on your historical trades

### Integration Opportunities
1. **Broker APIs**: Direct order execution
2. **Discord/Telegram bots**: Real-time alerts
3. **Database persistence**: Track strategy performance
4. **Web API**: Expose as REST service

## Support

For issues or questions:
1. Check the test suite output for diagnostic information
2. Review logs for detailed error messages
3. Ensure all dependencies are installed
4. Verify Robinhood connection is active

## License

This feature is part of the Magnus Wheel Strategy Trading Dashboard.
All rights reserved.

---

*Last Updated: November 2024*
*Version: 1.0.0*