## Example RAG Prompts and Responses

This document shows example prompts sent to Claude and expected responses.

## Example 1: High-Win-Rate CSP on AAPL

### Input Alert
```json
{
  "ticker": "AAPL",
  "strategy": "CSP",
  "action": "BTO",
  "strike_price": 170.0,
  "expiration_date": "2024-12-20",
  "dte": 30,
  "premium": 2.50,
  "current_price": 178.50,
  "current_vix": 15.2,
  "iv_rank": 45,
  "alert_text": "BTO 2x $AAPL 12/20 $170 CSP @ $2.50 - High IV rank, bullish on tech"
}
```

### RAG Context (Retrieved Trades)
```
### Trade #1 (Similarity: 92%)
Date: 2024-10-15
Ticker: AAPL
Strategy: CSP
Strike: $170 | DTE: 28
Premium: $2.30
VIX: 14.8
Market Trend: Bullish
Outcome: WIN - +$180.00 (+78.3%) in 15 days

### Trade #2 (Similarity: 89%)
Date: 2024-09-20
Ticker: AAPL
Strategy: CSP
Strike: $175 | DTE: 32
Premium: $2.80
VIX: 16.1
Market Trend: Bullish
Outcome: WIN - +$220.00 (+78.6%) in 18 days

### Trade #3 (Similarity: 85%)
Date: 2024-08-10
Ticker: AAPL
Strategy: CSP
Strike: $165 | DTE: 27
Premium: $2.10
VIX: 15.5
Market Trend: Neutral
Outcome: WIN - +$150.00 (+71.4%) in 12 days

AGGREGATE STATISTICS
Total Similar Trades: 8
Win Rate: 87.5%
Average P&L: $165.50
Average P&L %: +75.2%
Average Hold Time: 14 days
```

### Claude Response
```json
{
  "recommendation": "TAKE",
  "confidence": 87,
  "reasoning": "This AAPL CSP shows excellent historical performance with 87.5% win rate across 8 similar trades. The current market conditions closely align with previous successful trades: VIX in the 15-16 range, stock trading 5% above strike, and similar DTE. The premium of $2.50 per contract is in line with historical premiums that yielded average returns of +75%. The combination of high IV rank (45) and bullish market trend further supports entering this trade.",
  "historical_evidence": [
    "8 similar AAPL CSPs with 87.5% win rate",
    "Average P&L of +$165.50 per trade (+75.2%)",
    "Similar VIX range (14.8-16.1) yielded positive outcomes",
    "Comparable DTE (27-32 days) closed profitably in 2 weeks",
    "Bullish market trend correlated with 90% win rate"
  ],
  "risk_factors": [
    "Slight elevation in IV rank could indicate upcoming volatility",
    "Tech sector concentration risk if market turns bearish",
    "$170 strike is only 4.7% below current price - limited buffer"
  ],
  "suggested_adjustments": "Consider taking partial profits at 50% of max profit (approximately $125 per contract) to lock in gains early, based on historical data showing average hold time of only 14 days. Alternatively, set a stop-loss at $5.00 per contract (-100% loss) to limit downside risk."
}
```

---

## Example 2: Low-Win-Rate IC on Volatile Stock

### Input Alert
```json
{
  "ticker": "TSLA",
  "strategy": "Iron Condor",
  "action": "BTO",
  "strike_price": "320/330/370/380",
  "expiration_date": "2024-12-15",
  "dte": 25,
  "premium": 1.80,
  "current_price": 345.00,
  "current_vix": 22.5,
  "iv_rank": 78,
  "alert_text": "BTO TSLA 12/15 IC 320/330/370/380 @ $1.80 credit - High IV environment"
}
```

### RAG Context (Retrieved Trades)
```
### Trade #1 (Similarity: 81%)
Date: 2024-09-15
Ticker: TSLA
Strategy: Iron Condor
Strike: $310/320/360/370 | DTE: 23
Premium: $1.60
VIX: 24.2
Market Trend: Bearish
Outcome: LOSS - -$320.00 (-200.0%) in 8 days
Trade Thesis: Price moved outside short strikes, forced early exit

### Trade #2 (Similarity: 78%)
Date: 2024-08-20
Ticker: TSLA
Strategy: Iron Condor
Strike: $315/325/365/375 | DTE: 27
Premium: $1.70
VIX: 21.8
Market Trend: Neutral
Outcome: LOSS - -$180.00 (-105.9%) in 12 days

### Trade #3 (Similarity: 75%)
Date: 2024-07-10
Ticker: TSLA
Strategy: Iron Condor
Strike: $325/335/375/385 | DTE: 26
Premium: $1.90
VIX: 23.1
Market Trend: Volatile
Outcome: WIN - +$120.00 (+63.2%) in 20 days
Trade Thesis: Stayed range-bound, closed at 65% profit

AGGREGATE STATISTICS
Total Similar Trades: 5
Win Rate: 40.0%
Average P&L: -$76.00
Average P&L %: -28.5%
Average Hold Time: 13 days
```

### Claude Response
```json
{
  "recommendation": "PASS",
  "confidence": 78,
  "reasoning": "Historical data shows TSLA Iron Condors in high-IV environments have only a 40% win rate, with average losses of -$76 per trade. The elevated VIX (22.5) and high IV rank (78) indicate significant volatility risk, which has resulted in losses in 3 out of 5 similar trades. TSLA's tendency to make large price movements quickly (as evidenced by the -200% loss in Trade #1) makes Iron Condors particularly risky. The narrow $10 wings provide limited protection if price moves beyond short strikes.",
  "historical_evidence": [
    "Only 40% win rate for similar TSLA Iron Condors",
    "Average loss of -$76 per trade (-28.5%)",
    "2 out of 5 trades resulted in >100% losses due to price breakout",
    "High VIX environment (21-24) correlated with 70% loss rate",
    "TSLA volatility caused breaches of short strikes in 8-12 days"
  ],
  "risk_factors": [
    "TSLA's high beta and volatility make defined-risk spreads dangerous",
    "IV rank of 78 suggests elevated risk of large price movements",
    "Narrow $10 wings provide minimal protection",
    "Historical losses exceeded max profit by 2-3x",
    "VIX above 20 has historically resulted in 70% loss rate for TSLA ICs"
  ],
  "suggested_adjustments": "If you must enter this trade, consider: (1) Wider strikes (e.g., $315/330/360/375) to provide more breathing room, (2) Reduce position size by 50% due to high risk, (3) Set tight stop-loss at $3.50 per contract to limit downside, or (4) Wait for IV rank to drop below 60 before entering TSLA Iron Condors."
}
```

---

## Example 3: New Symbol with No Historical Data

### Input Alert
```json
{
  "ticker": "SMCI",
  "strategy": "CSP",
  "action": "BTO",
  "strike_price": 800.0,
  "expiration_date": "2024-12-20",
  "dte": 30,
  "premium": 45.00,
  "current_price": 925.00,
  "current_vix": 15.8,
  "iv_rank": 92,
  "alert_text": "BTO 1x $SMCI 12/20 $800 CSP @ $45 - AI hype play, high premium"
}
```

### RAG Context (Retrieved Trades)
```
No similar historical trades found.
```

### Claude Response
```json
{
  "recommendation": "MONITOR",
  "confidence": 35,
  "reasoning": "No historical data available for SMCI options trades in our database. The extremely high IV rank (92) and large premium ($45 per share) suggest elevated volatility and risk. While the 13.5% cushion below current price provides some safety, the lack of historical context makes it difficult to assess probability of success. This appears to be a speculative trade on AI-related momentum, which can be unpredictable.",
  "historical_evidence": [
    "No similar SMCI trades in database",
    "No comparable high-IV (>90) CSP trades to reference"
  ],
  "risk_factors": [
    "No historical data to validate strategy on this symbol",
    "Extremely high IV rank (92) indicates significant volatility risk",
    "AI-related stocks can have rapid price swings",
    "$45 premium suggests high perceived risk by market",
    "Requires $80,000+ in buying power for 1 contract",
    "Momentum trades often reverse quickly"
  ],
  "suggested_adjustments": "Before entering: (1) Paper trade this first to collect data, (2) Verify SMCI's historical price action and volatility patterns, (3) Consider starting with 1/4 position size to test waters, (4) Set strict stop-loss at $100 per share to cap maximum loss, or (5) Wait for IV rank to normalize below 70 before entering. Alternatively, consider more liquid, established tech stocks like NVDA or AMD for CSP strategies with proven track records."
}
```

---

## Example 4: Marginal Trade with Mixed Signals

### Input Alert
```json
{
  "ticker": "MSFT",
  "strategy": "Put Credit Spread",
  "action": "BTO",
  "strike_price": "360/365",
  "expiration_date": "2024-12-15",
  "dte": 25,
  "premium": 1.20,
  "current_price": 375.00,
  "current_vix": 16.5,
  "iv_rank": 35,
  "alert_text": "BTO MSFT 12/15 360/365 PCS @ $1.20 - Low IV, earnings coming"
}
```

### RAG Context (Retrieved Trades)
```
### Trade #1 (Similarity: 88%)
Date: 2024-10-05
Ticker: MSFT
Strategy: Put Credit Spread
Strike: $355/360 | DTE: 28
Premium: $1.10
VIX: 15.9
Market Trend: Bullish
Outcome: WIN - +$90.00 (+81.8%) in 21 days

### Trade #2 (Similarity: 85%)
Date: 2024-08-20
Ticker: MSFT
Strategy: Put Credit Spread
Strike: $350/355 | DTE: 22
Premium: $1.05
VIX: 17.2
Market Trend: Neutral
Outcome: WIN - +$80.00 (+76.2%) in 18 days

### Trade #3 (Similarity: 82%)
Date: 2024-07-15
Ticker: MSFT
Strategy: Put Credit Spread
Strike: $365/370 | DTE: 27
Premium: $1.25
VIX: 16.8
Market Trend: Bullish
Outcome: LOSS - -$280.00 (-224.0%) in 5 days
Trade Thesis: Earnings miss caused rapid decline below short strike

AGGREGATE STATISTICS
Total Similar Trades: 6
Win Rate: 66.7%
Average P&L: $28.33
Average P&L %: +23.6%
Average Hold Time: 15 days
```

### Claude Response
```json
{
  "recommendation": "MONITOR",
  "confidence": 52,
  "reasoning": "This MSFT Put Credit Spread shows mixed historical performance with 66.7% win rate but notable earnings-related risk. While 4 out of 6 similar trades were profitable with good returns (+80%), one trade resulted in a significant loss (-224%) during an earnings period. The alert mentions 'earnings coming', which introduces event risk that has historically caused breaches of the short strike. The moderate IV rank (35) and reasonable premium ($1.20) are positive, but the earnings catalyst warrants caution.",
  "historical_evidence": [
    "66.7% win rate for similar MSFT Put Credit Spreads",
    "Average profit of +23.6% on winning trades",
    "Successful trades held for 18-21 days",
    "CRITICAL: One earnings-related trade lost -224% in 5 days",
    "Non-earnings trades had 80% win rate"
  ],
  "risk_factors": [
    "Upcoming earnings introduces significant event risk",
    "Historical earnings-related trade lost >200% of premium",
    "Only $5 width provides limited protection on gap moves",
    "Earnings volatility can breach strikes quickly (5 days in past)",
    "Max risk ($380) is 3.2x max profit ($120)"
  ],
  "suggested_adjustments": "RECOMMENDATION DEPENDS ON EARNINGS DATE: (1) If earnings is >30 days away: TAKE this trade with standard position sizing, (2) If earnings is within DTE: PASS and wait until after earnings to enter, (3) Alternative: Close position 3 days before earnings if still open to avoid event risk, or (4) Consider wider spread ($355/365) to provide more downside protection during earnings volatility. The alert author should specify earnings date for a more definitive recommendation."
}
```

---

## Example 5: Contradictory Signals (Good Historical Data but Poor Current Conditions)

### Input Alert
```json
{
  "ticker": "AAPL",
  "strategy": "CSP",
  "action": "BTO",
  "strike_price": 170.0,
  "expiration_date": "2024-12-20",
  "dte": 30,
  "premium": 4.50,
  "current_price": 172.00,
  "current_vix": 28.5,
  "iv_rank": 88,
  "alert_text": "BTO 2x $AAPL 12/20 $170 CSP @ $4.50 - High premium opportunity"
}
```

### RAG Context (Retrieved Trades)
```
### Similar trades with VIX 10-18 had 85% win rate
### Similar trades with VIX >25 had 45% win rate

AGGREGATE STATISTICS (VIX <20)
Total Similar Trades: 12
Win Rate: 83.3%
Average P&L: $168.00

AGGREGATE STATISTICS (VIX >25)
Total Similar Trades: 4
Win Rate: 25.0%
Average P&L: -$145.00
```

### Claude Response
```json
{
  "recommendation": "PASS",
  "confidence": 72,
  "reasoning": "While AAPL CSPs have historically performed well (85% win rate in normal conditions), the current market environment is significantly different. VIX at 28.5 represents elevated market fear, and historical data shows AAPL CSPs have only a 25% win rate when entered during high-volatility regimes (VIX >25). The $4.50 premium is indeed attractive (unusually high), but this premium exists precisely because of elevated risk. The stock trading only $2 above the strike provides minimal safety cushion during volatile markets.",
  "historical_evidence": [
    "AAPL CSPs: 85% win rate in normal VIX (10-18)",
    "AAPL CSPs: 25% win rate in high VIX (>25)",
    "High-VIX environment has caused average loss of -$145",
    "Only 1 of 4 similar trades profitable during market stress",
    "Volatility spikes often coincide with rapid AAPL selloffs"
  ],
  "risk_factors": [
    "VIX at 28.5 indicates significant market stress",
    "Extremely high IV rank (88) suggests elevated crash risk",
    "Only 1.2% cushion below current price - very tight",
    "Historical data shows 75% loss rate in similar conditions",
    "Premium inflation due to fear, not opportunity"
  ],
  "suggested_adjustments": "Wait for VIX to decline below 22 before entering AAPL CSPs. If you must enter now: (1) Reduce position size by 75%, (2) Use lower strike ($160) for more protection, (3) Consider shorter DTE (14 days) to reduce exposure time, or (4) Switch to a defined-risk Put Spread instead of naked CSP to cap maximum loss. The 'high premium opportunity' is actually a red flag indicating elevated risk."
}
```

---

## Prompt Engineering Best Practices

### 1. Structured Context
Always provide:
- Clear alert details
- Historical similar trades with outcomes
- Aggregate statistics
- Current market conditions

### 2. Explicit Output Format
Request JSON format with specific fields:
- recommendation (TAKE/PASS/MONITOR)
- confidence (0-100)
- reasoning
- historical_evidence
- risk_factors
- suggested_adjustments

### 3. Few-Shot Examples
Include 2-3 example recommendations in system prompt to guide Claude's responses.

### 4. Confidence Calibration
Ask Claude to differentiate between:
- High confidence (80-100%): Clear historical pattern
- Medium confidence (50-79%): Mixed signals
- Low confidence (0-49%): Insufficient data or conflicting signals

### 5. Risk-First Thinking
Always ask Claude to identify risks before benefits to ensure balanced analysis.

---

## Testing Your Prompts

Use this checklist to validate prompt quality:

- [ ] Does the recommendation match historical data?
- [ ] Is confidence score justified by evidence?
- [ ] Are all major risks identified?
- [ ] Does reasoning reference specific historical trades?
- [ ] Are suggested adjustments actionable?
- [ ] Would a human trader agree with this analysis?

---

## Advanced Prompt Techniques

### Chain-of-Thought Reasoning

Add to system prompt:
```
Before providing your recommendation, think through:
1. What do the historical trades tell us?
2. How do current conditions compare to past successful trades?
3. What are the key risk factors?
4. What is the probability-weighted expected outcome?
Then provide your final recommendation.
```

### Self-Critique

Add to prompt:
```
After your initial recommendation, critique your own analysis:
- What assumptions did you make?
- What could go wrong?
- What would make you change your recommendation?
```

### Confidence Intervals

Request probability ranges:
```
Provide probability ranges for outcomes:
- P(profit > 50%): X%
- P(profit 0-50%): Y%
- P(loss): Z%
```

---

## Conclusion

Effective RAG prompts combine:
1. Rich historical context
2. Clear output structure
3. Risk-aware reasoning
4. Actionable insights

Test and iterate on your prompts to improve recommendation quality over time.
