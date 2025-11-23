# Technical Indicators Quick Reference Guide

**Quick guide for implementing and using technical indicators in Magnus platform**

---

## Installation Check

```bash
# Verify installed packages
pip list | grep -E "pandas-ta|ta|mibian|yfinance"

# Should show:
# ta==0.11.0
# pandas-ta==0.4.71b0
# mibian==0.1.3
# yfinance>=0.2.48
```

---

## Available Indicator Modules

### 1. Momentum Indicators
**File:** `c:\code\Magnus\src\momentum_indicators.py`
**Includes:** RSI, MACD, EMAs, ATR, CVD, Fibonacci

```python
from src.momentum_indicators import MomentumIndicators

mi = MomentumIndicators()
indicators = mi.get_all_momentum_indicators(df, current_price)

# Access results
rsi_signal = indicators['rsi']['signal']  # 'OVERSOLD', 'OVERBOUGHT', 'NEUTRAL'
macd_signal = indicators['macd']['signal']  # 'BULLISH_CROSS', 'BEARISH_CROSS'
ema_alignment = indicators['emas']['alignment']  # 'BULLISH', 'BEARISH'
atr_stops = indicators['atr']['stops']  # Stop loss levels
```

---

### 2. Smart Money Indicators
**File:** `c:\code\Magnus\src\smart_money_indicators.py`
**Includes:** Order Blocks, Fair Value Gaps, BOS/CHoCH, Liquidity Pools

```python
from src.smart_money_indicators import SmartMoneyIndicators

smc = SmartMoneyIndicators()
indicators = smc.get_all_smc_indicators(df)

# Access results
order_blocks = indicators['order_blocks']  # Institutional levels
fvgs = indicators['fair_value_gaps']  # Price imbalances
structure = indicators['market_structure']  # Trend analysis
liquidity = indicators['liquidity_pools']  # Stop hunt levels
```

---

### 3. Advanced Technical Indicators
**File:** `c:\code\Magnus\src\advanced_technical_indicators.py`
**Includes:** Volume Profile, Order Flow (CVD)

```python
from src.advanced_technical_indicators import VolumeProfileCalculator, OrderFlowAnalyzer

# Volume Profile
vp_calc = VolumeProfileCalculator()
volume_profile = vp_calc.calculate_volume_profile(df)
vp_signals = vp_calc.get_trading_signals(current_price, volume_profile)

# Order Flow
of_analyzer = OrderFlowAnalyzer()
cvd = of_analyzer.calculate_cvd(df)
divergences = of_analyzer.find_cvd_divergences(df)
```

---

### 4. Standard Indicators (NEW)
**File:** `c:\code\Magnus\src\standard_indicators.py`
**Includes:** Bollinger Bands, Stochastic, OBV, VWAP, MFI, Ichimoku, ADX, CCI

```python
from src.standard_indicators import StandardIndicators

si = StandardIndicators()
indicators = si.get_all_indicators(df, current_price)

# Access results
bollinger = indicators['bollinger']['signal']  # Volatility analysis
stochastic = indicators['stochastic']['signal']  # Momentum
adx = indicators['adx']['signal']  # Trend strength
ichimoku = indicators['ichimoku']['signal']  # All-in-one
```

---

### 5. Options Indicators (NEW)
**File:** `c:\code\Magnus\src\options_indicators.py`
**Includes:** IVR, Expected Move, Greeks, Put/Call Ratio

```python
from src.options_indicators import OptionsIndicators

oi = OptionsIndicators()

# Implied Volatility Rank
ivr = oi.implied_volatility_rank(current_iv, iv_history)

# Expected Move
expected = oi.expected_move(price=150, iv=0.25, dte=30)

# Greeks
greeks = oi.calculate_greeks(spot=150, strike=155, rate=0.05, dte=30, iv=0.25)

# Strategy Recommendation
recommendation = oi.option_strategy_recommendation(ivr=75, trend='BULLISH', expected_move=expected)
```

---

## Common Usage Patterns

### Pattern 1: Complete Stock Analysis

```python
import yfinance as yf
from src.momentum_indicators import MomentumIndicators
from src.standard_indicators import StandardIndicators
from src.smart_money_indicators import SmartMoneyIndicators

# Fetch data
ticker = yf.Ticker('AAPL')
df = ticker.history(period='3mo', interval='1d')
df.columns = [col.lower() for col in df.columns]
current_price = df['close'].iloc[-1]

# Analyze
mi = MomentumIndicators()
si = StandardIndicators()
smc = SmartMoneyIndicators()

momentum = mi.get_all_momentum_indicators(df, current_price)
standard = si.get_all_indicators(df, current_price)
smart_money = smc.get_all_smc_indicators(df)

# Combine signals
bullish_signals = 0
if momentum['rsi']['signal']['signal'] == 'OVERSOLD':
    bullish_signals += 1
if momentum['macd']['signal']['signal'] in ['BULLISH_CROSS', 'BULLISH']:
    bullish_signals += 1
if standard['adx']['signal']['signal'] in ['STRONG_BULLISH', 'BULLISH']:
    bullish_signals += 1

# Overall signal
if bullish_signals >= 2:
    overall = 'BULLISH'
else:
    overall = 'NEUTRAL or BEARISH'

print(f"Overall Signal: {overall}")
```

---

### Pattern 2: Options Strategy Selection

```python
from src.options_indicators import OptionsIndicators
from src.standard_indicators import StandardIndicators

# Get IV data (from your database or API)
current_iv = 0.28
iv_history = get_iv_history('AAPL')  # Your function

# Calculate IVR
oi = OptionsIndicators()
ivr_result = oi.implied_volatility_rank(current_iv, iv_history)

# Get trend from technical indicators
si = StandardIndicators()
indicators = si.get_all_indicators(df, current_price)
trend = indicators['adx']['signal']['direction']

# Calculate expected move
expected = oi.expected_move(price=current_price, iv=current_iv, dte=30)

# Get strategy recommendation
recommendation = oi.option_strategy_recommendation(
    ivr=ivr_result['ivr'],
    trend=trend,
    expected_move=expected
)

print(f"Top Strategy: {recommendation['top_recommendation']['strategy']}")
print(f"Reason: {recommendation['top_recommendation']['reason']}")
```

---

### Pattern 3: Entry Signal Generation

```python
def generate_entry_signal(symbol: str) -> dict:
    """Generate comprehensive entry signal"""

    # Fetch data
    ticker = yf.Ticker(symbol)
    df = ticker.history(period='3mo', interval='1d')
    df.columns = [col.lower() for col in df.columns]
    current_price = df['close'].iloc[-1]

    # Initialize indicators
    mi = MomentumIndicators()
    si = StandardIndicators()

    # Calculate
    momentum = mi.get_all_momentum_indicators(df, current_price)
    standard = si.get_all_indicators(df, current_price)

    # Score system
    score = 0
    signals = []

    # RSI
    if momentum['rsi']['signal']['signal'] == 'OVERSOLD':
        score += 2
        signals.append('RSI Oversold')
    elif momentum['rsi']['signal']['signal'] == 'OVERBOUGHT':
        score -= 2
        signals.append('RSI Overbought')

    # MACD
    if momentum['macd']['signal']['signal'] == 'BULLISH_CROSS':
        score += 3
        signals.append('MACD Bullish Cross')
    elif momentum['macd']['signal']['signal'] == 'BEARISH_CROSS':
        score -= 3
        signals.append('MACD Bearish Cross')

    # ADX
    adx_signal = standard['adx']['signal']
    if adx_signal['signal'] == 'STRONG_BULLISH':
        score += 3
        signals.append('Strong Bullish Trend')
    elif adx_signal['signal'] == 'STRONG_BEARISH':
        score -= 3
        signals.append('Strong Bearish Trend')

    # Bollinger Bands
    bb_signal = standard['bollinger']['signal']
    if bb_signal['signal'] == 'OVERSOLD':
        score += 1
        signals.append('Price Below BB Lower')
    elif bb_signal['signal'] == 'OVERBOUGHT':
        score -= 1
        signals.append('Price Above BB Upper')

    # Determine overall signal
    if score >= 5:
        overall = 'STRONG_BUY'
    elif score >= 3:
        overall = 'BUY'
    elif score <= -5:
        overall = 'STRONG_SELL'
    elif score <= -3:
        overall = 'SELL'
    else:
        overall = 'NEUTRAL'

    # Calculate stop loss using ATR
    atr_stops = momentum['atr']['stops']

    return {
        'symbol': symbol,
        'current_price': current_price,
        'signal': overall,
        'score': score,
        'supporting_signals': signals,
        'stop_loss': atr_stops['long_stop'],
        'target': atr_stops['long_target_1'],
        'timestamp': pd.Timestamp.now()
    }

# Usage
signal = generate_entry_signal('AAPL')
print(f"Signal: {signal['signal']} (Score: {signal['score']})")
print(f"Entry: ${signal['current_price']:.2f}")
print(f"Stop: ${signal['stop_loss']:.2f}")
print(f"Target: ${signal['target']:.2f}")
```

---

## Indicator Cheat Sheet

### Quick Reference Table

| Indicator | Best For | Bullish Signal | Bearish Signal | Options Application |
|-----------|----------|----------------|----------------|---------------------|
| **RSI** | Overbought/Oversold | < 30 | > 70 | Reversal plays |
| **MACD** | Trend | Bullish cross | Bearish cross | Trend following |
| **Bollinger Bands** | Volatility | Price < Lower | Price > Upper | IV expansion/contraction |
| **Stochastic** | Momentum | K crosses above D in oversold | K crosses below D in overbought | High-probability entries |
| **ADX** | Trend Strength | ADX > 40 + DI+ > DI- | ADX > 40 + DI- > DI+ | Directional vs neutral strategies |
| **Ichimoku** | All-in-one | TK cross above cloud | TK cross below cloud | Trend confirmation |
| **VWAP** | Intraday fair value | Price bounces off VWAP | Price rejects at VWAP | Day trading entries |
| **OBV** | Volume confirmation | Rising with price | Falling with price | Confirm breakouts |
| **MFI** | Volume RSI | < 20 | > 80 | Volume-confirmed reversals |
| **CCI** | Cyclical | < -100 | > 100 | Mean reversion |
| **ATR** | Volatility | High ATR | Low ATR | Position sizing, stop loss |

---

## Options Strategy Matrix

### Based on IVR and Trend

| IVR | Trend | Strategy | Reason |
|-----|-------|----------|--------|
| > 50 | Bullish | Bull Put Spread | Sell high premium below support |
| > 50 | Bearish | Bear Call Spread | Sell high premium above resistance |
| > 50 | Neutral | Iron Condor | Sell premium on both sides |
| < 50 | Bullish | Long Call / Bull Call Spread | Buy cheap premium |
| < 50 | Bearish | Long Put / Bear Put Spread | Buy cheap puts |
| < 50 | Neutral | Long Straddle/Strangle | Expect volatility expansion |

---

## Best Practices

### 1. Multi-Indicator Confirmation
- Never rely on a single indicator
- Use at least 2-3 from different categories
- Example: RSI (momentum) + MACD (trend) + ADX (strength)

### 2. Timeframe Analysis
```python
# Analyze multiple timeframes
timeframes = ['1d', '4h', '1h']
signals = {}

for tf in timeframes:
    df = get_data(symbol, interval=tf)
    signals[tf] = analyze(df)

# All timeframes must agree for strong signal
if all(signals[tf]['signal'] == 'BULLISH' for tf in timeframes):
    overall_signal = 'STRONG_BULLISH'
```

### 3. Backtesting
```python
# Always backtest before live trading
import vectorbt as vbt

# Generate signals
entries = (rsi < 30) & (macd_hist > 0)
exits = (rsi > 70) | (macd_hist < 0)

# Backtest
portfolio = vbt.Portfolio.from_signals(
    df['close'],
    entries,
    exits,
    init_cash=10000,
    fees=0.001
)

# Check performance
print(portfolio.stats())
```

### 4. Risk Management
```python
# Use ATR for stop loss
mi = MomentumIndicators()
atr = mi.calculate_atr(df)
stop_loss = current_price - (1.5 * atr.iloc[-1])

# Position sizing
risk_per_trade = 0.02  # 2% risk
capital = 10000
risk_amount = capital * risk_per_trade
stop_distance = current_price - stop_loss
position_size = risk_amount / stop_distance
```

---

## Common Combinations

### Combination 1: Trend Following
```python
# EMA Alignment + MACD + ADX
ema_bullish = price > ema_20 > ema_50
macd_bullish = macd_hist > 0
strong_trend = adx > 25

entry_signal = ema_bullish and macd_bullish and strong_trend
```

### Combination 2: Mean Reversion
```python
# Bollinger Bands + RSI + Stochastic
bb_oversold = price < bb_lower
rsi_oversold = rsi < 30
stoch_oversold = stoch_k < 20

reversal_signal = bb_oversold and rsi_oversold and stoch_oversold
```

### Combination 3: Breakout
```python
# Bollinger Squeeze + Volume + ATR
squeeze = bb_bandwidth < bb_bandwidth.quantile(0.2)
volume_spike = volume > volume.rolling(20).mean() * 1.5
volatility_expansion = atr > atr.rolling(20).mean()

breakout_setup = squeeze and volume_spike and volatility_expansion
```

---

## Integration with Existing Pages

### Supply/Demand Zones Page
```python
# In supply_demand_zones_page.py
from src.standard_indicators import StandardIndicators

# Add to zone analysis
si = StandardIndicators()
indicators = si.get_all_indicators(df, current_price)

# Confirm zones with indicators
if zone_type == 'DEMAND' and indicators['rsi']['signal']['signal'] == 'OVERSOLD':
    confidence = 'HIGH'
```

### Options Analysis Page
```python
# In options_analysis_page.py
from src.options_indicators import OptionsIndicators

oi = OptionsIndicators()

# Add IVR analysis
ivr = oi.implied_volatility_rank(current_iv, iv_history)
st.metric("IV Rank", f"{ivr['ivr']:.0f}%", ivr['strategy'])

# Strategy recommendations
recommendation = oi.option_strategy_recommendation(ivr['ivr'], trend, expected_move)
st.write("Recommended Strategy:", recommendation['top_recommendation']['strategy'])
```

---

## Testing

### Run Individual Tests
```bash
# Test momentum indicators
python c:\code\Magnus\src\momentum_indicators.py

# Test standard indicators
python c:\code\Magnus\src\standard_indicators.py

# Test options indicators
python c:\code\Magnus\src\options_indicators.py

# Test smart money indicators
python c:\code\Magnus\src\smart_money_indicators.py

# Test advanced indicators
python c:\code\Magnus\src\advanced_technical_indicators.py
```

### Quick Test Script
```python
# test_all_indicators.py
import yfinance as yf
from src.momentum_indicators import MomentumIndicators
from src.standard_indicators import StandardIndicators
from src.smart_money_indicators import SmartMoneyIndicators
from src.options_indicators import OptionsIndicators

def test_all():
    # Fetch test data
    ticker = yf.Ticker('AAPL')
    df = ticker.history(period='3mo', interval='1d')
    df.columns = [col.lower() for col in df.columns]
    current_price = df['close'].iloc[-1]

    print(f"Testing with {len(df)} days of AAPL data")
    print(f"Current Price: ${current_price:.2f}\n")

    # Test each module
    try:
        mi = MomentumIndicators()
        momentum = mi.get_all_momentum_indicators(df, current_price)
        print("✅ Momentum Indicators OK")
    except Exception as e:
        print(f"❌ Momentum Indicators FAILED: {e}")

    try:
        si = StandardIndicators()
        standard = si.get_all_indicators(df, current_price)
        print("✅ Standard Indicators OK")
    except Exception as e:
        print(f"❌ Standard Indicators FAILED: {e}")

    try:
        smc = SmartMoneyIndicators()
        smart_money = smc.get_all_smc_indicators(df)
        print("✅ Smart Money Indicators OK")
    except Exception as e:
        print(f"❌ Smart Money Indicators FAILED: {e}")

    try:
        oi = OptionsIndicators()
        ivr = oi.implied_volatility_rank(0.25, pd.Series([0.2, 0.3, 0.22, 0.28]))
        print("✅ Options Indicators OK")
    except Exception as e:
        print(f"❌ Options Indicators FAILED: {e}")

if __name__ == "__main__":
    test_all()
```

---

## Next Steps

1. **Review the comprehensive research document:**
   - `c:\code\Magnus\docs\TECHNICAL_ANALYSIS_RESEARCH_2025.md`

2. **Test the new indicator modules:**
   - `python c:\code\Magnus\src\standard_indicators.py`
   - `python c:\code\Magnus\src\options_indicators.py`

3. **Integrate into existing pages:**
   - Add to supply_demand_zones_page.py
   - Add to options_analysis_page.py
   - Add to positions_page_improved.py

4. **Create visualization dashboard:**
   - Multi-indicator overview page
   - Real-time signal monitoring
   - Backtesting results display

5. **Add to database:**
   - Store indicator signals
   - Track historical performance
   - Alert on signal changes

---

## Resources

- **Research Document:** `docs\TECHNICAL_ANALYSIS_RESEARCH_2025.md`
- **Momentum Indicators:** `src\momentum_indicators.py`
- **Standard Indicators:** `src\standard_indicators.py`
- **Smart Money:** `src\smart_money_indicators.py`
- **Advanced:** `src\advanced_technical_indicators.py`
- **Options:** `src\options_indicators.py`

---

**Last Updated:** November 22, 2025
