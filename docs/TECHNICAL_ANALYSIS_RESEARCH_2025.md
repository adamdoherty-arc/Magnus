# Comprehensive Technical Analysis Research 2025

**Research Date:** November 22, 2025
**Project:** Magnus Options & Trading Platform
**Focus:** TradingView API, Python Technical Analysis Libraries, Advanced Indicators

---

## Table of Contents
1. [TradingView API Capabilities](#tradingview-api-capabilities)
2. [Python Technical Analysis Libraries](#python-technical-analysis-libraries)
3. [GitHub Repositories for Advanced Indicators](#github-repositories)
4. [Best Practices for Technical Analysis 2025](#best-practices)
5. [Indicators Breakdown](#indicators-breakdown)
6. [Current Implementation Status](#current-implementation)
7. [Recommendations](#recommendations)

---

## 1. TradingView API Capabilities

### Overview
**Important Note:** TradingView does NOT provide a public REST API for direct market data or indicator value access as of 2025. They are planning to add this in the future.

### What TradingView Offers

#### A. Charting Library & Widgets
- Advanced charting tools
- Extensive library of technical indicators
- Multi-chart layouts for analyzing multiple assets
- Integration via JavaScript APIs

#### B. Datafeed API
- JavaScript-based API for connecting custom data sources
- Allows platforms to feed their own data into TradingView charts
- Not for downloading TradingView's data

#### C. Broker REST API
- Designed for broker integration
- Supports order execution on TradingView platform
- Not for retail data access

#### D. Pine Script
- TradingView's native scripting language
- Create custom technical indicators and strategies
- Runs on TradingView's platform (not exportable directly)

### Third-Party Solutions
- Unofficial libraries exist (e.g., `tradingview-ta` on PyPI)
- Community-developed tools like `Mathieu2301/TradingView-API` on GitHub
- Limited and unofficial - use with caution

### Key Limitation
- Free version has very limited features
- Paid subscriptions required for full API access
- Cannot directly download historical data or indicator values via official API

### Current Magnus Implementation
```python
# requirements.txt shows:
tradingview-ta>=3.3.0
```

This library provides:
- Technical analysis data scraping
- Real-time market sentiment
- Basic indicator values (unofficial)

---

## 2. Python Technical Analysis Libraries

### A. TA-Lib (Industry Standard)
**GitHub:** https://github.com/TA-Lib/ta-lib-python
**PyPI:** `pip install TA-Lib`

#### Features
- **150+ indicators** including:
  - Overlap Studies (SMA, EMA, Bollinger Bands)
  - Momentum Indicators (RSI, MACD, Stochastic, CCI)
  - Volume Indicators (OBV, AD, ADOSC)
  - Volatility Indicators (ATR, NATR)
  - Price Transform
  - Cycle Indicators
  - Pattern Recognition (candlestick patterns)

#### Performance
- C-library with Python wrapper (using Cython)
- **2-4x faster** than SWIG interface
- Supports both Pandas and Polars libraries
- Industry-standard accuracy

#### Installation Note
Requires both:
1. TA-Lib C library (system-level)
2. Python wrapper (pip install)

#### Example Usage
```python
import talib
import numpy as np

# RSI
rsi = talib.RSI(close_prices, timeperiod=14)

# MACD
macd, signal, hist = talib.MACD(close_prices,
                                 fastperiod=12,
                                 slowperiod=26,
                                 signalperiod=9)

# Bollinger Bands
upper, middle, lower = talib.BBANDS(close_prices,
                                     timeperiod=20,
                                     nbdevup=2,
                                     nbdevdn=2)

# Stochastic
slowk, slowd = talib.STOCH(high, low, close,
                           fastk_period=14,
                           slowk_period=3,
                           slowd_period=3)

# Volume Indicators
obv = talib.OBV(close_prices, volume)
adx = talib.ADX(high, low, close, timeperiod=14)
```

---

### B. pandas-ta (Modern & Easy to Use)
**GitHub:** https://github.com/0xAVX/pandas-ta (most active fork)
**PyPI:** `pip install pandas-ta`

#### Features
- **150+ indicators** when TA-Lib is installed
- **60+ candlestick patterns** (with TA-Lib)
- Built on Pandas for easy integration
- NumPy for performance

#### Three Processing Styles
1. **Standard:** `ta.rsi(df['close'], length=14)`
2. **DataFrame Extension:** `df.ta.rsi(length=14)`
3. **Strategy Mode:** `df.ta.strategy('all')`

#### Magnus Current Implementation
```python
# requirements.txt shows:
pandas-ta==0.4.71b0
```

#### Example Usage
```python
import pandas as pd
import pandas_ta as ta

# Add RSI to DataFrame
df['rsi'] = ta.rsi(df['close'], length=14)

# Using DataFrame extension
df.ta.macd(fast=12, slow=26, signal=9, append=True)

# Apply all indicators at once
df.ta.strategy('all')

# Custom strategy
my_strategy = ta.Strategy(
    name="My Strategy",
    ta=[
        {"kind": "rsi"},
        {"kind": "macd", "fast": 12, "slow": 26},
        {"kind": "bbands", "length": 20},
        {"kind": "stoch"},
        {"kind": "adx"}
    ]
)
df.ta.strategy(my_strategy)
```

---

### C. pandas-ta-classic
**GitHub:** https://github.com/jaslGH/pandas-ta
**PyPI:** `pip install pandas-ta-classic`

#### Features
- **141 indicators** and utility functions
- **62 TA-Lib candlestick patterns**
- **203 total indicators**
- Community-maintained version
- More stable than bleeding-edge pandas-ta

---

### D. ta (Technical Analysis Library)
**GitHub:** https://github.com/bukosabino/ta
**PyPI:** `pip install ta`

#### Features
- Pure Python implementation (no C dependencies)
- Easy installation via pip
- 30+ common indicators
- Clean, documented API

#### Magnus Current Implementation
```python
# requirements.txt shows:
ta==0.11.0
```

#### Example Usage
```python
from ta import add_all_ta_features
from ta.utils import dropna
from ta.momentum import RSIIndicator
from ta.trend import MACD

# Clean NaN values
df = dropna(df)

# Add all technical indicators
df = add_all_ta_features(
    df, open="open", high="high", low="low",
    close="close", volume="volume"
)

# Or individual indicators
rsi_indicator = RSIIndicator(close=df['close'], window=14)
df['rsi'] = rsi_indicator.rsi()

macd = MACD(close=df['close'])
df['macd'] = macd.macd()
df['macd_signal'] = macd.macd_signal()
df['macd_diff'] = macd.macd_diff()
```

---

### E. finta (Financial Technical Analysis)
**GitHub:** https://github.com/peerchemist/finta
**PyPI:** `pip install finta`

#### Features
- Expects properly formatted OHLC DataFrame
- Column names in lowercase: ["open", "high", "low", "close", "volume"]
- Well-documented TA class
- Clean API

#### Example Usage
```python
from finta import TA

# DataFrame must have lowercase columns
df.columns = [col.lower() for col in df.columns]

# RSI
rsi = TA.RSI(df)

# MACD
macd = TA.MACD(df)

# Bollinger Bands
bbands = TA.BBANDS(df)

# Ichimoku
ichimoku = TA.ICHIMOKU(df)
```

---

### F. Tulipy (Fast C Implementation)
**PyPI:** `pip install tulipy`

#### Features
- Python bindings for Tulip Indicators
- Fast C implementation
- Lightweight and efficient
- Over 100 indicators

---

### G. VectorBT (Backtesting-Focused)
**PyPI:** `pip install vectorbt`

#### Features
- Fast backtesting using NumPy vectorization
- Built-in technical indicators
- Portfolio analysis and metrics
- Visualization capabilities
- Parameter optimization

#### Example Usage
```python
import vectorbt as vbt

# Fetch data
data = vbt.YFData.download("AAPL", start='2023-01-01', end='2025-01-01')

# Generate signals using RSI
rsi = vbt.RSI.run(data.get('Close'))
entries = rsi.rsi_below(30)  # Oversold
exits = rsi.rsi_above(70)    # Overbought

# Run backtest
portfolio = vbt.Portfolio.from_signals(
    data.get('Close'),
    entries,
    exits
)

# Analyze results
print(portfolio.stats())
portfolio.plot().show()
```

---

## 3. GitHub Repositories for Advanced Indicators

### Top Repositories (2025)

#### 1. pandas-ta (0xAVX fork)
- **URL:** https://github.com/0xAVX/pandas-ta
- **Stars:** Most active fork
- **Features:** 150+ indicators
- **Status:** Actively maintained

#### 2. TA-Lib Official Python Wrapper
- **URL:** https://github.com/TA-Lib/ta-lib-python
- **Stars:** Industry standard
- **Features:** 150+ indicators, C-based performance
- **Status:** Actively maintained

#### 3. Technical Analysis Library (bukosabino)
- **URL:** https://github.com/bukosabino/ta
- **Features:** Pure Python, 30+ indicators
- **Status:** Actively maintained

#### 4. finta
- **URL:** https://github.com/peerchemist/finta
- **Features:** Common financial technical indicators
- **Status:** Actively maintained

#### 5. Unofficial TradingView API
- **URL:** https://github.com/Mathieu2301/TradingView-API
- **Features:** Get real-time stocks from TradingView
- **Status:** Community-maintained (unofficial)

### Options Trading Specific Libraries

#### 1. QuantLib
- **URL:** https://github.com/lballabio/QuantLib
- Comprehensive quantitative finance library
- Options pricing, Greeks, implied volatility
- Industry-standard for derivatives

#### 2. Mibian
- **URL:** https://github.com/yassinemaaroufi/mibian
- Options pricing (Black-Scholes, Binomial)
- Greeks calculation (Delta, Gamma, Theta, Vega, Rho)

**Magnus Current Implementation:**
```python
# requirements.txt shows:
mibian==0.1.3
```

#### 3. py_vollib
- Implied volatility calculations
- Based on Peter Jäckel's "Let's be rational"
- Very fast IV computation

#### 4. Vollib
- Options pricing library
- Multiple pricing models
- Fast and efficient

#### 5. Optopsy
- Options trading backtesting
- Strategy analysis

---

## 4. Best Practices for Technical Analysis 2025

### A. Multi-Timeframe Analysis
```python
# Analyze multiple timeframes
timeframes = ['1d', '4h', '1h', '15m']
for tf in timeframes:
    df = get_data(symbol, interval=tf)
    analyze_trend(df)
```

### B. Indicator Combination & Confirmation
**Don't rely on single indicators**
- Use 2-3 indicators from different categories
- Momentum + Trend + Volume

**Example Setup:**
```python
def multi_indicator_signal(df):
    # Momentum
    rsi = ta.rsi(df['close'], length=14)

    # Trend
    macd = ta.macd(df['close'])
    ema_20 = ta.ema(df['close'], length=20)
    ema_50 = ta.ema(df['close'], length=50)

    # Volume
    obv = ta.obv(df['close'], df['volume'])

    # Volatility
    atr = ta.atr(df['high'], df['low'], df['close'])

    # Combine signals
    bullish = (
        (rsi < 40) &  # Not overbought
        (macd['MACD_12_26_9'] > macd['MACDs_12_26_9']) &  # MACD bullish
        (df['close'] > ema_20) &  # Above short-term trend
        (ema_20 > ema_50) &  # Trend aligned
        (obv > obv.shift(5))  # Volume increasing
    )

    return bullish
```

### C. Backtesting Before Live Trading
```python
import vectorbt as vbt

# Generate signals
entries, exits = generate_signals(df)

# Backtest
portfolio = vbt.Portfolio.from_signals(
    df['close'],
    entries,
    exits,
    init_cash=10000,
    fees=0.001  # 0.1% fees
)

# Analyze performance
stats = portfolio.stats()
sharpe = stats['Sharpe Ratio']
max_dd = stats['Max Drawdown [%]']

# Only deploy if metrics are good
if sharpe > 1.5 and max_dd < 20:
    deploy_strategy()
```

### D. Risk Management with ATR
```python
def calculate_position_size(capital, risk_pct, atr, entry_price):
    """
    Use ATR for volatility-adjusted position sizing
    """
    risk_amount = capital * risk_pct
    stop_distance = atr * 1.5  # 1.5 ATR stop

    shares = risk_amount / stop_distance
    max_shares = (capital * 0.1) / entry_price  # Max 10% position

    return min(shares, max_shares)
```

### E. Divergence Detection
```python
from scipy.signal import find_peaks

def detect_rsi_divergence(df, lookback=20):
    """
    Detect bullish/bearish RSI divergence
    """
    # Find price peaks and troughs
    price_highs, _ = find_peaks(df['high'].values, distance=lookback)
    price_lows, _ = find_peaks(-df['low'].values, distance=lookback)

    # Find RSI peaks and troughs
    rsi_highs, _ = find_peaks(df['rsi'].values, distance=lookback)
    rsi_lows, _ = find_peaks(-df['rsi'].values, distance=lookback)

    # Bullish divergence: price lower low, RSI higher low
    # Bearish divergence: price higher high, RSI lower high

    return divergences
```

### F. Machine Learning Integration
```python
from sklearn.ensemble import RandomForestClassifier
import pandas as pd

def ml_enhanced_signals(df):
    """
    Combine technical indicators with ML
    """
    # Create features from technical indicators
    features = pd.DataFrame({
        'rsi': ta.rsi(df['close']),
        'macd_hist': ta.macd(df['close'])['MACDh_12_26_9'],
        'atr': ta.atr(df['high'], df['low'], df['close']),
        'obv': ta.obv(df['close'], df['volume']),
        'adx': ta.adx(df['high'], df['low'], df['close'])
    })

    # Train model on historical data
    X = features.dropna()
    y = (df['close'].shift(-1) > df['close']).astype(int)

    model = RandomForestClassifier(n_estimators=100)
    model.fit(X[:-1], y[:-1])

    # Predict
    predictions = model.predict_proba(X)

    return predictions
```

### G. Real-Time Data Processing
```python
import redis
import asyncio

class RealtimeIndicators:
    def __init__(self):
        self.redis_client = redis.Redis()
        self.buffer = []

    async def process_tick(self, tick):
        """Process incoming market data"""
        self.buffer.append(tick)

        if len(self.buffer) >= 14:  # Enough for RSI
            df = pd.DataFrame(self.buffer)
            rsi = ta.rsi(df['close'], length=14).iloc[-1]

            # Cache result
            self.redis_client.setex(
                f'rsi:{tick["symbol"]}',
                60,  # 60 second TTL
                rsi
            )
```

### H. Advanced Pattern Recognition
```python
def detect_chart_patterns(df):
    """
    Detect common chart patterns
    """
    patterns = []

    # Head and Shoulders
    if detect_head_and_shoulders(df):
        patterns.append('HEAD_AND_SHOULDERS')

    # Double Top/Bottom
    if detect_double_top(df):
        patterns.append('DOUBLE_TOP')

    # Triangle patterns
    if detect_triangle(df):
        patterns.append('TRIANGLE')

    return patterns
```

---

## 5. Indicators Breakdown

### A. Momentum Indicators

#### RSI (Relative Strength Index)
**Purpose:** Identify overbought/oversold conditions
**Best Practices 2025:**
```python
# Traditional RSI
rsi_14 = ta.rsi(df['close'], length=14)

# Multi-period RSI for confirmation
rsi_9 = ta.rsi(df['close'], length=9)
rsi_21 = ta.rsi(df['close'], length=21)

# Signals
oversold = (rsi_14 < 30)  # Classic
strong_oversold = (rsi_14 < 30) & (rsi_9 < 30)  # Confirmed
divergence = detect_rsi_divergence(df, rsi_14)  # Advanced
```

**For Options Trading:**
- RSI < 30: Consider bullish options (calls, call spreads)
- RSI > 70: Consider bearish options (puts, put spreads)
- Divergence: Strong reversal signal

---

#### MACD (Moving Average Convergence Divergence)
**Purpose:** Trend following and momentum
**Best Practices 2025:**
```python
# Standard MACD
macd_result = ta.macd(df['close'], fast=12, slow=26, signal=9)
macd_line = macd_result['MACD_12_26_9']
signal_line = macd_result['MACDs_12_26_9']
histogram = macd_result['MACDh_12_26_9']

# Signals
bullish_cross = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
bearish_cross = (macd_line < signal_line) & (macd_line.shift(1) >= signal_line.shift(1))

# Histogram divergence (advanced)
histogram_increasing = histogram > histogram.shift(1)
price_decreasing = df['close'] < df['close'].shift(1)
bullish_divergence = histogram_increasing & price_decreasing
```

**For Options Trading:**
- Bullish cross + rising histogram: Buy calls
- Bearish cross + falling histogram: Buy puts
- Zero-line cross: Strong trend change

---

#### Stochastic Oscillator
**Purpose:** Momentum and reversal signals
**Best Practices 2025:**
```python
# Stochastic
stoch = ta.stoch(df['high'], df['low'], df['close'],
                 k=14, d=3, smooth_k=3)
k_line = stoch['STOCHk_14_3_3']
d_line = stoch['STOCHd_14_3_3']

# Signals
oversold = (k_line < 20) & (d_line < 20)
overbought = (k_line > 80) & (d_line > 80)
bullish_cross = (k_line > d_line) & (k_line.shift(1) <= d_line.shift(1))
```

**For Options Trading:**
- Stochastic < 20 + bullish cross: High probability call setup
- Stochastic > 80 + bearish cross: High probability put setup

---

### B. Bollinger Bands
**Purpose:** Volatility and mean reversion
**Best Practices 2025:**
```python
# Bollinger Bands
bbands = ta.bbands(df['close'], length=20, std=2)
upper = bbands['BBU_20_2.0']
middle = bbands['BBM_20_2.0']  # SMA
lower = bbands['BBL_20_2.0']

# Bandwidth (volatility measure)
bandwidth = (upper - lower) / middle

# Signals
squeeze = bandwidth < bandwidth.quantile(0.2)  # Low volatility
expansion = bandwidth > bandwidth.quantile(0.8)  # High volatility

# Mean reversion
oversold_bb = df['close'] < lower
overbought_bb = df['close'] > upper

# Breakout
breakout_up = (df['close'] > upper) & (df['close'].shift(1) <= upper.shift(1))
breakout_down = (df['close'] < lower) & (df['close'].shift(1) >= lower.shift(1))
```

**For Options Trading:**
- Squeeze (low bandwidth): Straddle/strangle (expect volatility)
- Price at lower band + RSI oversold: Bull call spread
- Price at upper band + RSI overbought: Bear put spread
- Bandwidth expansion: Implied volatility likely to spike (good for long options)

---

### C. Volume-Based Indicators

#### OBV (On-Balance Volume)
**Purpose:** Confirm price trends with volume
**Best Practices 2025:**
```python
# OBV
obv = ta.obv(df['close'], df['volume'])

# Trend confirmation
obv_rising = obv > obv.shift(5)
price_rising = df['close'] > df['close'].shift(5)
trend_confirmed = obv_rising & price_rising

# Divergence
obv_falling = obv < obv.shift(5)
price_rising = df['close'] > df['close'].shift(5)
bearish_divergence = obv_falling & price_rising
```

---

#### VWAP (Volume Weighted Average Price)
**Purpose:** Intraday fair value
**Best Practices 2025:**
```python
def calculate_vwap(df):
    """
    Calculate VWAP - resets daily for intraday
    """
    df['typical_price'] = (df['high'] + df['low'] + df['close']) / 3
    df['tp_volume'] = df['typical_price'] * df['volume']

    # Cumulative for the day
    df['cumulative_tp_volume'] = df.groupby(df.index.date)['tp_volume'].cumsum()
    df['cumulative_volume'] = df.groupby(df.index.date)['volume'].cumsum()

    df['vwap'] = df['cumulative_tp_volume'] / df['cumulative_volume']

    return df['vwap']

# Signals
above_vwap = df['close'] > df['vwap']  # Bullish
below_vwap = df['close'] < df['vwap']  # Bearish
```

**For Options Trading:**
- Price consistently above VWAP: Bullish bias (calls)
- Price consistently below VWAP: Bearish bias (puts)
- VWAP as dynamic support/resistance

---

#### MFI (Money Flow Index)
**Purpose:** Volume-weighted RSI
**Best Practices 2025:**
```python
# Money Flow Index
mfi = ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=14)

# Signals
oversold_mfi = mfi < 20
overbought_mfi = mfi > 80

# Divergence (more reliable than RSI alone)
mfi_rising = mfi > mfi.shift(5)
price_falling = df['close'] < df['close'].shift(5)
bullish_divergence = mfi_rising & price_falling
```

---

### D. Advanced Indicators

#### Ichimoku Cloud
**Purpose:** All-in-one trend, momentum, and support/resistance
**Best Practices 2025:**
```python
# Ichimoku
ichimoku = ta.ichimoku(df['high'], df['low'], df['close'])[0]

tenkan = ichimoku['ITS_9']  # Conversion line
kijun = ichimoku['IKS_26']  # Base line
senkou_a = ichimoku['ISA_9']  # Leading span A
senkou_b = ichimoku['ISB_26']  # Leading span B
chikou = ichimoku['ICS_26']  # Lagging span

# Signals
bullish_tk_cross = (tenkan > kijun) & (tenkan.shift(1) <= kijun.shift(1))
above_cloud = df['close'] > senkou_a
strong_bullish = bullish_tk_cross & above_cloud

# Cloud thickness (support strength)
cloud_thickness = abs(senkou_a - senkou_b)
strong_support = cloud_thickness > cloud_thickness.quantile(0.7)
```

**For Options Trading:**
- Price above cloud: Bullish bias, buy calls
- Price below cloud: Bearish bias, buy puts
- Thin cloud: Lower confidence, consider spreads
- Thick cloud: Higher confidence, directional plays

---

#### ATR (Average True Range)
**Purpose:** Volatility measurement and position sizing
**Best Practices 2025:**
```python
# ATR
atr = ta.atr(df['high'], df['low'], df['close'], length=14)

# Volatility-adjusted stops
long_stop = df['close'] - (1.5 * atr)
short_stop = df['close'] + (1.5 * atr)

# Targets (Risk:Reward of 1:2)
long_target = df['close'] + (3.0 * atr)
short_target = df['close'] - (3.0 * atr)

# Volatility regime
atr_percentile = atr.rolling(100).apply(
    lambda x: pd.Series(x).rank(pct=True).iloc[-1]
)
low_vol = atr_percentile < 0.3
high_vol = atr_percentile > 0.7
```

**For Options Trading:**
- High ATR: Buy options (volatility expansion)
- Low ATR: Sell options (volatility contraction)
- ATR-based strike selection: ±1 ATR from current price

---

#### ADX (Average Directional Index)
**Purpose:** Trend strength measurement
**Best Practices 2025:**
```python
# ADX
adx_result = ta.adx(df['high'], df['low'], df['close'], length=14)
adx = adx_result['ADX_14']
di_plus = adx_result['DMP_14']
di_minus = adx_result['DMN_14']

# Trend strength
weak_trend = adx < 20
moderate_trend = (adx >= 20) & (adx < 40)
strong_trend = adx >= 40

# Direction
bullish = (di_plus > di_minus) & (adx > 20)
bearish = (di_minus > di_plus) & (adx > 20)

# Signals
strong_bullish = (di_plus > di_minus) & (adx > 40)
strong_bearish = (di_minus > di_plus) & (adx > 40)
```

**For Options Trading:**
- ADX > 40 + bullish: Strong trend, buy calls or call spreads
- ADX > 40 + bearish: Strong trend, buy puts or put spreads
- ADX < 20: Avoid directional plays, consider iron condors

---

#### CCI (Commodity Channel Index)
**Purpose:** Cyclical trends and overbought/oversold
**Best Practices 2025:**
```python
# CCI
cci = ta.cci(df['high'], df['low'], df['close'], length=20)

# Signals
oversold = cci < -100
overbought = cci > 100
extreme_oversold = cci < -200  # Stronger signal
extreme_overbought = cci > 200

# Zero line cross (trend change)
bullish_cross = (cci > 0) & (cci.shift(1) <= 0)
bearish_cross = (cci < 0) & (cci.shift(1) >= 0)
```

---

### E. Custom Indicators for Options Trading

#### Implied Volatility Rank (IVR)
```python
def calculate_ivr(iv_current, iv_history_252):
    """
    Calculate Implied Volatility Rank
    IV Rank = (Current IV - Min IV) / (Max IV - Min IV)
    """
    iv_min = iv_history_252.min()
    iv_max = iv_history_252.max()

    ivr = ((iv_current - iv_min) / (iv_max - iv_min)) * 100

    return ivr

# Usage for options strategies
if ivr > 50:
    strategy = "SELL_PREMIUM"  # Iron condor, credit spreads
elif ivr < 50:
    strategy = "BUY_PREMIUM"  # Debit spreads, long options
```

---

#### Put/Call Ratio
```python
def calculate_pcr(put_volume, call_volume):
    """
    Put/Call Ratio - Sentiment indicator
    """
    pcr = put_volume / call_volume

    if pcr > 1.0:
        sentiment = "BEARISH"  # More puts than calls
    elif pcr < 0.7:
        sentiment = "BULLISH"  # More calls than puts
    else:
        sentiment = "NEUTRAL"

    return pcr, sentiment
```

---

#### Expected Move
```python
def calculate_expected_move(price, iv, dte):
    """
    Expected Move = Price × IV × sqrt(DTE / 365)
    """
    expected_move = price * iv * np.sqrt(dte / 365)

    upper_bound = price + expected_move
    lower_bound = price - expected_move

    return {
        'expected_move': expected_move,
        'upper': upper_bound,
        'lower': lower_bound
    }
```

---

#### Greeks-Based Indicators
```python
import mibian

def calculate_options_greeks(spot, strike, rate, days, volatility, call_put='c'):
    """
    Calculate Greeks using mibian
    """
    if call_put == 'c':
        option = mibian.BS([spot, strike, rate, days], volatility=volatility)
        return {
            'delta': option.callDelta,
            'gamma': option.gamma,
            'theta': option.callTheta,
            'vega': option.vega,
            'rho': option.callRho
        }
    else:
        option = mibian.BS([spot, strike, rate, days], volatility=volatility)
        return {
            'delta': option.putDelta,
            'gamma': option.gamma,
            'theta': option.putTheta,
            'vega': option.vega,
            'rho': option.putRho
        }
```

---

#### Delta-Hedged Position Indicator
```python
def calculate_delta_hedge(position_delta, shares_per_contract=100):
    """
    Calculate shares needed to delta-hedge options position
    """
    shares_to_hedge = -position_delta * shares_per_contract

    return {
        'shares_to_hedge': shares_to_hedge,
        'action': 'BUY' if shares_to_hedge > 0 else 'SELL',
        'quantity': abs(shares_to_hedge)
    }
```

---

## 6. Current Implementation Status (Magnus Platform)

### Installed Libraries
```python
# From requirements.txt
pandas>=2.2.0
numpy>=2.0.0
scipy==1.11.4
ta==0.11.0
pandas-ta==0.4.71b0
mibian==0.1.3
yfinance>=0.2.48
tradingview-ta>=3.3.0
```

### Existing Indicator Files

#### c:\code\Magnus\src\advanced_technical_indicators.py
**Implements:**
- Volume Profile (POC, VAH, VAL, HVN, LVN)
- Market Profile (TPO Charts)
- Order Flow Analysis (CVD - Cumulative Volume Delta)
- Harmonic Patterns detection (Gartley, Butterfly - placeholders)

**Code Quality:** Production-ready
**Test Coverage:** Has `__main__` test block

---

#### c:\code\Magnus\src\momentum_indicators.py
**Implements:**
- RSI (Relative Strength Index)
- MACD (Moving Average Convergence Divergence)
- EMAs (20, 50, 200)
- ATR (Average True Range) with stop-loss/target calculations
- CVD (Cumulative Volume Delta)
- Fibonacci retracement levels

**Code Quality:** Production-ready
**Test Coverage:** Has `__main__` test block

---

#### c:\code\Magnus\src\smart_money_indicators.py
**Implements:**
- Order Blocks (institutional entry points)
- Fair Value Gaps (FVG - price imbalances)
- Break of Structure (BOS) / Change of Character (CHoCH)
- Liquidity Pools (stop loss clusters)
- Swing highs/lows detection

**Code Quality:** Production-ready
**Test Coverage:** Has `__main__` test block

---

### What's Missing

#### Standard Indicators Not Yet Implemented
- [ ] Bollinger Bands (can add via pandas-ta)
- [ ] Stochastic Oscillator
- [ ] OBV (On-Balance Volume)
- [ ] VWAP (Volume Weighted Average Price)
- [ ] MFI (Money Flow Index)
- [ ] Ichimoku Cloud
- [ ] ADX (Average Directional Index)
- [ ] CCI (Commodity Channel Index)

#### Options-Specific Indicators
- [ ] Implied Volatility Rank (IVR)
- [ ] Put/Call Ratio analysis
- [ ] Expected Move calculations
- [ ] Greeks aggregation and tracking
- [ ] Delta-hedge calculations
- [ ] Volatility smile analysis

#### Advanced Features
- [ ] Multi-timeframe analysis
- [ ] Divergence detection (RSI, MACD, etc.)
- [ ] Pattern recognition (Head & Shoulders, Double Top/Bottom, etc.)
- [ ] ML-enhanced signals
- [ ] Real-time indicator updates
- [ ] Backtesting framework integration

---

## 7. Recommendations

### Short-Term Wins (1-2 weeks)

#### 1. Add Missing Standard Indicators
```python
# Create: src/standard_indicators.py

from typing import Dict
import pandas as pd
import pandas_ta as ta

class StandardIndicators:
    """Common technical indicators using pandas-ta"""

    def bollinger_bands(self, df: pd.DataFrame, length=20, std=2) -> Dict:
        bbands = ta.bbands(df['close'], length=length, std=std)
        return {
            'upper': bbands[f'BBU_{length}_{std}'],
            'middle': bbands[f'BBM_{length}_{std}'],
            'lower': bbands[f'BBL_{length}_{std}'],
            'bandwidth': (bbands[f'BBU_{length}_{std}'] - bbands[f'BBL_{length}_{std}']) / bbands[f'BBM_{length}_{std}']
        }

    def stochastic(self, df: pd.DataFrame, k=14, d=3) -> Dict:
        stoch = ta.stoch(df['high'], df['low'], df['close'], k=k, d=d)
        return {
            'k': stoch[f'STOCHk_{k}_{d}_3'],
            'd': stoch[f'STOCHd_{k}_{d}_3']
        }

    def obv(self, df: pd.DataFrame) -> pd.Series:
        return ta.obv(df['close'], df['volume'])

    def vwap(self, df: pd.DataFrame) -> pd.Series:
        return ta.vwap(df['high'], df['low'], df['close'], df['volume'])

    def mfi(self, df: pd.DataFrame, length=14) -> pd.Series:
        return ta.mfi(df['high'], df['low'], df['close'], df['volume'], length=length)

    def ichimoku(self, df: pd.DataFrame) -> Dict:
        ich = ta.ichimoku(df['high'], df['low'], df['close'])[0]
        return {
            'tenkan': ich['ITS_9'],
            'kijun': ich['IKS_26'],
            'senkou_a': ich['ISA_9'],
            'senkou_b': ich['ISB_26'],
            'chikou': ich['ICS_26']
        }

    def adx(self, df: pd.DataFrame, length=14) -> Dict:
        adx_result = ta.adx(df['high'], df['low'], df['close'], length=length)
        return {
            'adx': adx_result[f'ADX_{length}'],
            'di_plus': adx_result[f'DMP_{length}'],
            'di_minus': adx_result[f'DMN_{length}']
        }

    def cci(self, df: pd.DataFrame, length=20) -> pd.Series:
        return ta.cci(df['high'], df['low'], df['close'], length=length)
```

---

#### 2. Create Options-Specific Indicator Module
```python
# Create: src/options_indicators.py

import numpy as np
import pandas as pd
import mibian

class OptionsIndicators:
    """Options-specific technical indicators"""

    def implied_volatility_rank(self, current_iv: float, iv_history: pd.Series) -> float:
        """Calculate IV Rank (0-100)"""
        iv_min = iv_history.min()
        iv_max = iv_history.max()

        if iv_max == iv_min:
            return 50.0

        ivr = ((current_iv - iv_min) / (iv_max - iv_min)) * 100
        return ivr

    def expected_move(self, price: float, iv: float, dte: int) -> Dict:
        """Calculate expected move based on IV"""
        move = price * iv * np.sqrt(dte / 365)

        return {
            'expected_move': move,
            'upper_bound': price + move,
            'lower_bound': price - move,
            'move_pct': (move / price) * 100
        }

    def calculate_greeks(self, spot: float, strike: float,
                        rate: float, dte: int, iv: float,
                        option_type: str = 'call') -> Dict:
        """Calculate option Greeks using mibian"""
        option = mibian.BS([spot, strike, rate, dte], volatility=iv*100)

        if option_type == 'call':
            return {
                'delta': option.callDelta,
                'gamma': option.gamma,
                'theta': option.callTheta,
                'vega': option.vega,
                'rho': option.callRho,
                'price': option.callPrice
            }
        else:
            return {
                'delta': option.putDelta,
                'gamma': option.gamma,
                'theta': option.putTheta,
                'vega': option.vega,
                'rho': option.putRho,
                'price': option.putPrice
            }

    def put_call_ratio(self, put_volume: float, call_volume: float) -> Dict:
        """Calculate Put/Call ratio and sentiment"""
        if call_volume == 0:
            return {'pcr': None, 'sentiment': 'UNKNOWN'}

        pcr = put_volume / call_volume

        if pcr > 1.0:
            sentiment = 'BEARISH'
        elif pcr < 0.7:
            sentiment = 'BULLISH'
        else:
            sentiment = 'NEUTRAL'

        return {
            'pcr': pcr,
            'sentiment': sentiment,
            'put_volume': put_volume,
            'call_volume': call_volume
        }
```

---

#### 3. Multi-Timeframe Analysis Framework
```python
# Create: src/multi_timeframe_analysis.py

import pandas as pd
import yfinance as yf
from typing import List, Dict

class MultiTimeframeAnalysis:
    """Analyze indicators across multiple timeframes"""

    def __init__(self, symbol: str):
        self.symbol = symbol
        self.timeframes = {
            'daily': '1d',
            '4hour': '4h',
            '1hour': '1h',
            '15min': '15m'
        }

    def analyze_all_timeframes(self) -> Dict:
        """Get indicator signals across all timeframes"""
        results = {}

        for tf_name, tf_interval in self.timeframes.items():
            df = self.get_data(tf_interval)
            results[tf_name] = self.analyze_timeframe(df)

        # Combine signals
        alignment = self.check_alignment(results)

        return {
            'timeframes': results,
            'alignment': alignment,
            'overall_signal': self.get_overall_signal(alignment)
        }

    def get_data(self, interval: str, period: str = '30d') -> pd.DataFrame:
        """Fetch data for timeframe"""
        ticker = yf.Ticker(self.symbol)
        df = ticker.history(period=period, interval=interval)
        return df

    def analyze_timeframe(self, df: pd.DataFrame) -> Dict:
        """Analyze single timeframe"""
        from src.momentum_indicators import MomentumIndicators

        mi = MomentumIndicators()
        current_price = df['Close'].iloc[-1]

        indicators = mi.get_all_momentum_indicators(df, current_price)

        return {
            'rsi': indicators['rsi']['signal'],
            'macd': indicators['macd']['signal'],
            'ema_alignment': indicators['emas']['alignment'],
            'trend': self.determine_trend(indicators)
        }

    def check_alignment(self, results: Dict) -> Dict:
        """Check if all timeframes agree"""
        trends = [tf['trend'] for tf in results.values()]

        bullish_count = trends.count('BULLISH')
        bearish_count = trends.count('BEARISH')
        neutral_count = trends.count('NEUTRAL')

        if bullish_count >= 3:
            alignment = 'STRONG_BULLISH'
        elif bearish_count >= 3:
            alignment = 'STRONG_BEARISH'
        elif bullish_count > bearish_count:
            alignment = 'WEAK_BULLISH'
        elif bearish_count > bullish_count:
            alignment = 'WEAK_BEARISH'
        else:
            alignment = 'NEUTRAL'

        return {
            'alignment': alignment,
            'bullish_count': bullish_count,
            'bearish_count': bearish_count,
            'neutral_count': neutral_count
        }
```

---

### Medium-Term Improvements (1-2 months)

#### 1. Backtesting Integration
- Integrate with VectorBT for strategy testing
- Store backtest results in PostgreSQL
- Create backtesting dashboard in Streamlit

#### 2. Real-Time Indicator Pipeline
- Use Redis for caching indicator values
- WebSocket integration for live updates
- Celery tasks for background calculation

#### 3. ML-Enhanced Signals
- Train models on historical indicator combinations
- Feature importance analysis
- Ensemble methods for robust signals

#### 4. Advanced Pattern Recognition
- Implement chart pattern detection
- Harmonic pattern completion
- Elliott Wave analysis

---

### Long-Term Vision (3-6 months)

#### 1. Custom Indicator Builder
- Allow users to create custom indicators via UI
- Save and share indicator strategies
- Backtest custom indicators

#### 2. Automated Strategy Generation
- ML discovers profitable indicator combinations
- Genetic algorithms for parameter optimization
- Walk-forward analysis

#### 3. Integration with Trading
- Auto-generate options strategies based on indicators
- Risk management rules from ATR/volatility
- Position sizing from indicator confidence

---

## Code Examples: Combining Everything

### Complete Technical Analysis Pipeline
```python
# Example: complete_analysis.py

import pandas as pd
import yfinance as yf
from src.momentum_indicators import MomentumIndicators
from src.smart_money_indicators import SmartMoneyIndicators
from src.advanced_technical_indicators import VolumeProfileCalculator, OrderFlowAnalyzer
from src.standard_indicators import StandardIndicators  # To be created
from src.options_indicators import OptionsIndicators  # To be created

class CompleteTechnicalAnalysis:
    """Complete technical analysis combining all indicators"""

    def __init__(self, symbol: str, period: str = '3mo', interval: str = '1d'):
        self.symbol = symbol
        self.period = period
        self.interval = interval

        # Initialize all indicator classes
        self.momentum = MomentumIndicators()
        self.smc = SmartMoneyIndicators()
        self.vp_calc = VolumeProfileCalculator()
        self.of_analyzer = OrderFlowAnalyzer()
        self.standard = StandardIndicators()
        self.options = OptionsIndicators()

        # Fetch data
        self.df = self.get_data()
        self.current_price = self.df['close'].iloc[-1]

    def get_data(self) -> pd.DataFrame:
        """Fetch and prepare data"""
        ticker = yf.Ticker(self.symbol)
        df = ticker.history(period=self.period, interval=self.interval)
        df.columns = [col.lower() for col in df.columns]
        return df

    def analyze(self) -> Dict:
        """Run complete analysis"""

        # 1. Momentum Indicators
        momentum = self.momentum.get_all_momentum_indicators(self.df, self.current_price)

        # 2. Standard Indicators
        standard = {
            'bbands': self.standard.bollinger_bands(self.df),
            'stoch': self.standard.stochastic(self.df),
            'obv': self.standard.obv(self.df),
            'vwap': self.standard.vwap(self.df),
            'mfi': self.standard.mfi(self.df),
            'ichimoku': self.standard.ichimoku(self.df),
            'adx': self.standard.adx(self.df),
            'cci': self.standard.cci(self.df)
        }

        # 3. Smart Money Concepts
        smc = self.smc.get_all_smc_indicators(self.df)

        # 4. Volume Profile
        volume_profile = self.vp_calc.calculate_volume_profile(self.df)
        vp_signals = self.vp_calc.get_trading_signals(self.current_price, volume_profile)

        # 5. Order Flow
        self.df['cvd'] = self.of_analyzer.calculate_cvd(self.df)
        cvd_divergences = self.of_analyzer.find_cvd_divergences(self.df)

        # 6. Options Indicators (if applicable)
        options_analysis = None
        if self.has_options_data():
            options_analysis = self.analyze_options()

        # 7. Generate overall signal
        overall_signal = self.generate_overall_signal({
            'momentum': momentum,
            'standard': standard,
            'smc': smc,
            'volume_profile': vp_signals,
            'cvd_divergences': cvd_divergences
        })

        return {
            'symbol': self.symbol,
            'current_price': self.current_price,
            'momentum': momentum,
            'standard': standard,
            'smc': smc,
            'volume_profile': volume_profile,
            'vp_signals': vp_signals,
            'cvd_divergences': cvd_divergences,
            'options': options_analysis,
            'overall_signal': overall_signal,
            'timestamp': pd.Timestamp.now()
        }

    def generate_overall_signal(self, indicators: Dict) -> Dict:
        """Combine all indicators into overall signal"""

        score = 0
        max_score = 0
        signals = []

        # RSI
        max_score += 10
        if indicators['momentum']['rsi']['signal']['signal'] == 'OVERSOLD':
            score += 10
            signals.append('RSI Oversold (Bullish)')
        elif indicators['momentum']['rsi']['signal']['signal'] == 'OVERBOUGHT':
            score -= 10
            signals.append('RSI Overbought (Bearish)')

        # MACD
        max_score += 10
        macd_signal = indicators['momentum']['macd']['signal']['signal']
        if 'BULLISH' in macd_signal:
            score += 10
            signals.append(f'MACD {macd_signal}')
        elif 'BEARISH' in macd_signal:
            score -= 10
            signals.append(f'MACD {macd_signal}')

        # EMA Alignment
        max_score += 15
        ema_align = indicators['momentum']['emas']['alignment']
        if ema_align['alignment'] == 'BULLISH':
            if ema_align['strength'] == 'STRONG':
                score += 15
                signals.append('Strong Bullish EMA Alignment')
            else:
                score += 7
                signals.append('Moderate Bullish EMA Alignment')
        elif ema_align['alignment'] == 'BEARISH':
            if ema_align['strength'] == 'STRONG':
                score -= 15
                signals.append('Strong Bearish EMA Alignment')
            else:
                score -= 7
                signals.append('Moderate Bearish EMA Alignment')

        # Volume Profile
        max_score += 10
        vp_position = indicators['volume_profile']['position']
        if vp_position == 'AT_POC':
            score += 5  # Neutral but important
            signals.append('Price at POC (Key Level)')
        elif vp_position == 'BELOW_VALUE_AREA':
            score += 10
            signals.append('Price Below Value Area (Bullish)')
        elif vp_position == 'ABOVE_VALUE_AREA':
            score -= 10
            signals.append('Price Above Value Area (Bearish)')

        # Smart Money Concepts
        max_score += 10
        smc_trend = indicators['smc']['market_structure']['current_trend']
        if smc_trend == 'BULLISH':
            score += 10
            signals.append('Market Structure Bullish')
        elif smc_trend == 'BEARISH':
            score -= 10
            signals.append('Market Structure Bearish')

        # CVD Divergences
        if indicators['cvd_divergences']:
            max_score += 15
            latest_div = indicators['cvd_divergences'][-1]
            if latest_div['type'] == 'BULLISH_DIVERGENCE':
                score += 15
                signals.append('Bullish CVD Divergence (Strong Reversal Signal)')
            else:
                score -= 15
                signals.append('Bearish CVD Divergence (Strong Reversal Signal)')

        # Normalize score
        if max_score > 0:
            normalized_score = (score / max_score) * 100
        else:
            normalized_score = 0

        # Determine overall signal
        if normalized_score > 60:
            overall = 'STRONG_BULLISH'
            confidence = 'HIGH'
        elif normalized_score > 30:
            overall = 'BULLISH'
            confidence = 'MEDIUM'
        elif normalized_score < -60:
            overall = 'STRONG_BEARISH'
            confidence = 'HIGH'
        elif normalized_score < -30:
            overall = 'BEARISH'
            confidence = 'MEDIUM'
        else:
            overall = 'NEUTRAL'
            confidence = 'LOW'

        return {
            'signal': overall,
            'confidence': confidence,
            'score': normalized_score,
            'supporting_signals': signals,
            'recommendation': self.get_recommendation(overall, confidence)
        }

    def get_recommendation(self, signal: str, confidence: str) -> str:
        """Generate actionable recommendation"""

        if signal == 'STRONG_BULLISH' and confidence == 'HIGH':
            return "🚀 Strong bullish setup. Consider: Long calls, bull call spreads, or cash-secured puts"
        elif signal == 'BULLISH':
            return "✅ Bullish bias. Consider: Bull call spreads or protective calls"
        elif signal == 'STRONG_BEARISH' and confidence == 'HIGH':
            return "⚠️ Strong bearish setup. Consider: Long puts, bear put spreads, or covered calls"
        elif signal == 'BEARISH':
            return "📉 Bearish bias. Consider: Bear put spreads or protective puts"
        else:
            return "ℹ️ No clear directional bias. Consider: Iron condors, strangles, or wait for better setup"


# Usage
if __name__ == "__main__":
    analyzer = CompleteTechnicalAnalysis('AAPL', period='3mo', interval='1d')
    results = analyzer.analyze()

    print(f"\n{'='*80}")
    print(f"Complete Technical Analysis: {results['symbol']}")
    print(f"{'='*80}")
    print(f"Current Price: ${results['current_price']:.2f}")
    print(f"\nOverall Signal: {results['overall_signal']['signal']}")
    print(f"Confidence: {results['overall_signal']['confidence']}")
    print(f"Score: {results['overall_signal']['score']:.1f}/100")
    print(f"\nRecommendation:")
    print(f"{results['overall_signal']['recommendation']}")
    print(f"\nSupporting Signals:")
    for signal in results['overall_signal']['supporting_signals']:
        print(f"  • {signal}")
    print(f"{'='*80}\n")
```

---

## Summary

### Current Strengths
- Already have advanced indicators (Volume Profile, Order Flow, Smart Money)
- Good foundation with pandas-ta and ta libraries
- Options pricing with mibian
- Production-ready code structure

### Quick Wins
1. Add standard indicators (Bollinger, Stochastic, ADX, etc.) using pandas-ta
2. Create options-specific indicator module
3. Build multi-timeframe analysis

### Medium-Term
1. Backtesting integration
2. Real-time updates with Redis/WebSocket
3. ML-enhanced signals

### Long-Term
1. Custom indicator builder UI
2. Automated strategy discovery
3. Full integration with options trading

### Best Libraries for Magnus
1. **pandas-ta**: Primary indicator library (already installed)
2. **ta**: Backup/alternative (already installed)
3. **TA-Lib**: For performance-critical calculations (consider adding)
4. **VectorBT**: For backtesting (recommend adding)
5. **mibian**: Options pricing (already installed)

---

## Next Steps

1. **Review this document** and prioritize features
2. **Create missing indicator modules** (standard_indicators.py, options_indicators.py)
3. **Integrate with existing pages** (supply_demand_zones_page.py, options_analysis_page.py)
4. **Add tests** for new indicators
5. **Update documentation** with usage examples
6. **Deploy to production** incrementally

---

**End of Research Document**
