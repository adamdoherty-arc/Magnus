# AVA Quick Reference: Technical Analysis

**Purpose**: Fast lookup for AVA when answering technical analysis questions

---

## Fibonacci Retracement Levels

| Level | Ratio | Use Case |
|-------|-------|----------|
| 23.6% | 0.236 | Shallow pullback (strong trend) |
| 38.2% | 0.382 | Common retracement |
| 50.0% | 0.500 | Psychological level |
| 61.8% | 0.618 | **Golden Ratio** - highest probability |
| 78.6% | 0.786 | Deep retracement (weak trend) |

**Golden Zone**: 50%-61.8% = highest probability reversal area

---

## Fibonacci Extension Targets

| Level | Ratio | Use Case |
|-------|-------|----------|
| 127.2% | 1.272 | First extension target |
| 161.8% | 1.618 | **Most common** profit target |
| 200% | 2.000 | Double extension |
| 261.8% | 2.618 | Strong trend target |

---

## Volume Profile Key Levels

| Term | Full Name | Meaning | Trading Use |
|------|-----------|---------|-------------|
| **POC** | Point of Control | Price with highest volume | Fair value, support/resistance |
| **VAH** | Value Area High | Top of 70% volume range | Resistance, breakout level |
| **VAL** | Value Area Low | Bottom of 70% volume range | Support, breakdown level |
| **HVN** | High Volume Node | High volume cluster | Strong support/resistance |
| **LVN** | Low Volume Node | Low volume area | Weak level, expect fast moves |

**Trading Rules**:
- Price > POC = Bullish bias
- Price < POC = Bearish bias
- Price outside value area = expect reversion to POC
- Break above VAH = bullish breakout
- Break below VAL = bearish breakdown

---

## Order Flow (CVD) Signals

### CVD Trends
| Condition | Signal |
|-----------|--------|
| Rising CVD + Rising Price | ✅ Strong uptrend (confirmed) |
| Falling CVD + Falling Price | ✅ Strong downtrend (confirmed) |
| Rising CVD + Falling Price | ⚠️ **Bullish Divergence** (reversal signal) |
| Falling CVD + Rising Price | ⚠️ **Bearish Divergence** (reversal signal) |

### Divergence Signals (Most Powerful)

**Bullish Divergence**:
- Price: Lower low
- CVD: Higher low
- Signal: **BUY** (selling pressure weakening)

**Bearish Divergence**:
- Price: Higher high
- CVD: Lower high
- Signal: **SELL** (buying pressure weakening)

---

## High-Probability Setups (Confluence)

### Setup 1: Fibonacci Golden Zone + CVD Divergence
```
✅ Price at 50%-61.8% Fibonacci
✅ CVD bullish divergence
✅ Reversal candle
→ STRONG LONG
```

### Setup 2: POC + Fibonacci Confluence
```
✅ Fibonacci level at POC
✅ Historical support
✅ Buy pressure > 55%
→ STRONG LONG
```

### Setup 3: VAL + Support + CVD
```
✅ Price at VAL (Value Area Low)
✅ Rising CVD
✅ Demand zone overlap
→ STRONG LONG
```

---

## AVA Response Templates

### When User Asks About Fibonacci

**Template**:
```
I see you're interested in Fibonacci analysis for [SYMBOL].

Key Fibonacci levels:
- Golden Zone (50%-61.8%): $[X] - $[Y]
- 38.2% retracement: $[X]
- 78.6% support: $[X]

Current price: $[X]
Position: [Above/Below/In] Golden Zone

Recommendation: [Signal based on position]
```

### When User Asks About Volume Profile

**Template**:
```
Volume Profile analysis for [SYMBOL]:

- POC (Point of Control): $[X] (fair value)
- VAH (Value Area High): $[X]
- VAL (Value Area Low): $[X]
- Value Area: $[VAL] - $[VAH]

Current price: $[X]
Position: [Above/Below/In] value area

Bias: [Bullish/Bearish] (price is [above/below] POC)
```

### When User Asks About CVD

**Template**:
```
Order Flow (CVD) analysis for [SYMBOL]:

Current CVD: [X]
Trend: [BULLISH/BEARISH]
1-day change: [+/-X]
5-day change: [+/-X]

Buy Pressure: [X]%
Sell Pressure: [X]%

[If divergence exists]:
⚠️ [BULLISH/BEARISH] DIVERGENCE DETECTED
Signal: [BUY/SELL]
```

### When User Asks for Trade Setup

**Template**:
```
Analyzing [SYMBOL] for high-probability setups...

Confluence Analysis:
✅/❌ Fibonacci: [Status]
✅/❌ Volume Profile: [Status]
✅/❌ CVD: [Status]
✅/❌ Divergence: [Status]

Setup Quality: [EXCELLENT/GOOD/FAIR/WEAK]

[If EXCELLENT or GOOD]:
Entry: $[X]
Stop Loss: $[X]
Target: $[X]
Risk/Reward: [X]:1
```

---

## Common User Questions & Answers

**Q**: "What is the Golden Zone?"
**A**: "The Golden Zone is the 50%-61.8% Fibonacci retracement range. It's the highest probability reversal area because it combines the psychological 50% level with the mathematical 61.8% Golden Ratio. Success rate is ~80% when combined with volume confirmation."

**Q**: "What's better, Fibonacci or Volume Profile?"
**A**: "Neither is better - they're complementary. Fibonacci shows mathematical support/resistance based on price swings. Volume Profile shows where actual trading occurred. Best results come from using BOTH together (confluence trading)."

**Q**: "How do I know if a divergence is reliable?"
**A**: "A CVD divergence is most reliable when:
1. It occurs at a key support/resistance level
2. Multiple bars show the divergence (not just one)
3. Other indicators confirm (Fibonacci, Volume Profile)
4. Volume increases on reversal candle
Divergence + confluence = high probability."

**Q**: "What timeframe should I use?"
**A**: "Depends on your trading style:
- Day trading: 1-hour or 15-min charts
- Swing trading: Daily charts
- Position trading: Weekly charts
Pro tip: Use higher timeframe for trend, lower for entry."

**Q**: "Can I use this for options trading?"
**A**: "Absolutely! Technical analysis works for stocks, options, futures, crypto, forex. For options:
- Use Fibonacci to time entries (buy at Golden Zone)
- Use Volume Profile for strike selection (near POC)
- Use CVD to confirm trend strength
- Better entries = better options profits."

---

## Database Functions

### Get Cached Fibonacci
```python
from src.technical_analysis_db_manager import TechnicalAnalysisDBManager

db = TechnicalAnalysisDBManager()
swings = db.get_cached_fibonacci_levels('AAPL', '1d', '6mo')

if swings:
    # Cache HIT - use cached data
else:
    # Cache MISS - calculate fresh
```

### Get Cached Volume Profile
```python
vp = db.get_cached_volume_profile('TSLA', '1d', '3mo')

if vp:
    poc = vp['poc_price']
    vah = vp['vah_price']
    val = vp['val_price']
```

### Get Cached CVD
```python
cvd_data = db.get_cached_order_flow('NVDA', '1d', '1mo')

if cvd_data:
    current_cvd = cvd_data['current_cvd']
    trend = cvd_data['cvd_trend']
    divergences = cvd_data['divergences']
```

---

## File Locations

**Calculators**:
- `src/fibonacci_calculator.py` - Fibonacci calculations
- `src/advanced_technical_indicators.py` - Volume Profile & CVD

**Database**:
- `src/technical_analysis_schema.sql` - Database schema
- `src/technical_analysis_db_manager.py` - Database manager

**UI**:
- `supply_demand_zones_page.py` - Technical Analysis Hub page

**Knowledge Base**:
- `src/ava/knowledge_technical_analysis.md` - Full knowledge base
- `src/ava/technical_analysis_quick_reference.md` - This file

---

**AVA**: Use this reference for quick, accurate responses to technical analysis questions.
