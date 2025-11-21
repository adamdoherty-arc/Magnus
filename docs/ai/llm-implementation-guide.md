# LLM Implementation Guide for Magnus Platform
## Practical Integration Roadmap

**Last Updated:** November 6, 2025

---

## Quick Start: Claude Integration

### Step 1: Install Dependencies

```bash
pip install anthropic==0.18.0
pip install openai==1.12.0  # For DeepSeek compatibility
pip install huggingface-hub==0.20.0  # For FinGPT
```

Add to `requirements.txt`:
```
anthropic>=0.18.0
openai>=1.12.0
huggingface-hub>=0.20.0
tiktoken>=0.5.0  # Token counting
```

### Step 2: Environment Variables

Add to `.env`:
```bash
# LLM API Keys
ANTHROPIC_API_KEY=sk-ant-api03-...
OPENAI_API_KEY=sk-...  # For GPT-4o
DEEPSEEK_API_KEY=sk-...
HUGGINGFACE_API_KEY=hf_...

# LLM Configuration
LLM_PRIMARY_MODEL=claude-3-5-sonnet-20241022
LLM_SECONDARY_MODEL=gpt-4o
LLM_SENTIMENT_MODEL=FinGPT/fingpt-sentiment_llama2-7b_lora
LLM_BULK_MODEL=deepseek-chat

# Cost Controls
LLM_MAX_MONTHLY_COST=100.00  # USD
LLM_MAX_TOKENS_PER_REQUEST=4000
LLM_ENABLE_CACHING=true
```

### Step 3: Create LLM Client Wrapper

Create `C:\Code\WheelStrategy\src\llm_client.py`:

```python
"""
LLM Client Manager for Magnus Trading Platform
Provides unified interface for Claude, GPT-4o, FinGPT, DeepSeek
"""

import os
import logging
from typing import Dict, List, Optional, Any
from enum import Enum
import anthropic
from openai import OpenAI
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ModelProvider(Enum):
    """Supported LLM providers"""
    CLAUDE = "claude"
    GPT4O = "gpt4o"
    FINGPT = "fingpt"
    DEEPSEEK = "deepseek"


class LLMClient:
    """Unified LLM client for financial analysis"""

    def __init__(self):
        # Initialize clients
        self.claude_client = anthropic.Anthropic(
            api_key=os.getenv("ANTHROPIC_API_KEY")
        )
        self.openai_client = OpenAI(
            api_key=os.getenv("OPENAI_API_KEY")
        )
        self.deepseek_client = OpenAI(
            api_key=os.getenv("DEEPSEEK_API_KEY"),
            base_url="https://api.deepseek.com"
        )

        # Cost tracking
        self.monthly_cost = 0.0
        self.max_monthly_cost = float(os.getenv("LLM_MAX_MONTHLY_COST", 100))

        # Token pricing (per 1M tokens)
        self.pricing = {
            "claude-3-5-sonnet": {"input": 3.00, "output": 15.00},
            "gpt-4o": {"input": 2.50, "output": 10.00},
            "deepseek-chat": {"input": 0.14, "output": 0.28},
        }

    def analyze_trade(
        self,
        symbol: str,
        strike: float,
        expiration: str,
        premium: float,
        current_value: float,
        days_to_expiry: int,
        stock_price: float,
        model: ModelProvider = ModelProvider.CLAUDE
    ) -> Dict[str, Any]:
        """
        Analyze options trade using specified LLM

        Args:
            symbol: Stock ticker
            strike: Strike price
            expiration: Expiration date
            premium: Premium collected
            current_value: Current option value
            days_to_expiry: Days until expiration
            stock_price: Current stock price
            model: Which LLM to use

        Returns:
            Analysis dictionary with recommendation
        """
        # Build prompt
        prompt = self._build_trade_analysis_prompt(
            symbol, strike, expiration, premium,
            current_value, days_to_expiry, stock_price
        )

        # Route to appropriate model
        if model == ModelProvider.CLAUDE:
            response = self._call_claude(prompt)
        elif model == ModelProvider.GPT4O:
            response = self._call_gpt4o(prompt)
        elif model == ModelProvider.DEEPSEEK:
            response = self._call_deepseek(prompt)
        else:
            raise ValueError(f"Unsupported model: {model}")

        # Parse response
        try:
            analysis = json.loads(response)
            return analysis
        except json.JSONDecodeError:
            logger.error(f"Failed to parse LLM response: {response}")
            return {"error": "Failed to parse response"}

    def analyze_sentiment(
        self,
        text: str,
        symbol: str
    ) -> Dict[str, Any]:
        """
        Analyze sentiment of news/earnings text

        Args:
            text: Text to analyze
            symbol: Stock ticker

        Returns:
            Sentiment analysis
        """
        prompt = f"""Analyze the sentiment of this financial text for {symbol}.

Text:
{text[:2000]}  # Limit to 2000 chars

Return JSON with:
{{
    "sentiment": "BULLISH" | "NEUTRAL" | "BEARISH",
    "confidence": 0-100,
    "key_phrases": ["phrase1", "phrase2"],
    "reasoning": "explanation"
}}"""

        # Use GPT-4o for speed
        response = self._call_gpt4o(prompt)

        try:
            return json.loads(response)
        except:
            return {
                "sentiment": "NEUTRAL",
                "confidence": 0,
                "error": "Failed to parse"
            }

    def bulk_analyze(
        self,
        symbols: List[str],
        analysis_type: str = "premium_opportunities"
    ) -> List[Dict[str, Any]]:
        """
        Bulk analysis using DeepSeek (cheap)

        Args:
            symbols: List of tickers to analyze
            analysis_type: Type of analysis

        Returns:
            List of analyses
        """
        prompt = f"""Analyze these {len(symbols)} stocks for {analysis_type}:

Symbols: {', '.join(symbols)}

For each, provide:
- Premium opportunity score (0-100)
- Risk level (LOW/MEDIUM/HIGH)
- Key factors

Return JSON array."""

        response = self._call_deepseek(prompt)

        try:
            return json.loads(response)
        except:
            logger.error("Bulk analysis failed")
            return []

    def _build_trade_analysis_prompt(
        self,
        symbol: str,
        strike: float,
        expiration: str,
        premium: float,
        current_value: float,
        days_to_expiry: int,
        stock_price: float
    ) -> str:
        """Build comprehensive trade analysis prompt"""

        # Calculate metrics
        profit = premium - abs(current_value)
        profit_pct = (profit / premium * 100) if premium > 0 else 0
        moneyness = ((stock_price - strike) / strike * 100)
        is_itm = stock_price < strike

        prompt = f"""You are an expert options trader analyzing a cash-secured put (CSP) position.

POSITION DETAILS:
- Symbol: {symbol}
- Strike Price: ${strike:.2f}
- Expiration: {expiration}
- Days to Expiry: {days_to_expiry}
- Premium Collected: ${premium:.2f}
- Current Option Value: ${abs(current_value):.2f}
- Current Stock Price: ${stock_price:.2f}

CALCULATED METRICS:
- Current P&L: ${profit:.2f} ({profit_pct:.1f}%)
- Moneyness: {moneyness:.1f}% {"ITM" if is_itm else "OTM"}
- Assignment Risk: {"HIGH" if is_itm and days_to_expiry < 7 else "MEDIUM" if is_itm else "LOW"}

ANALYSIS REQUIRED:
1. Estimate Options Greeks:
   - Delta (probability of ITM at expiration)
   - Theta (daily decay in dollars)
   - Gamma (delta sensitivity)
   - Vega (volatility sensitivity)

2. Probability Analysis:
   - Probability of profit (PoP)
   - Probability of assignment
   - Expected value of position

3. Recommended Action:
   - CLOSE_NOW (take profits)
   - HOLD (let theta decay)
   - ROLL (extend expiration)
   - PREPARE_ASSIGNMENT (likely to be assigned)

4. Risk Assessment:
   - Overall risk level (LOW/MEDIUM/HIGH)
   - Key risks to monitor
   - Stop-loss recommendation

Return response as JSON:
{{
    "greeks": {{
        "delta": 0.0 to 1.0,
        "theta": dollars per day,
        "gamma": number,
        "vega": number,
        "explanation": "brief explanation of each"
    }},
    "probabilities": {{
        "profit": 0-100,
        "assignment": 0-100,
        "expected_value": dollars
    }},
    "recommendation": {{
        "action": "CLOSE_NOW" | "HOLD" | "ROLL" | "PREPARE_ASSIGNMENT",
        "confidence": 0-100,
        "reasoning": "detailed reasoning",
        "alternative_actions": ["alternative1", "alternative2"]
    }},
    "risk_assessment": {{
        "level": "LOW" | "MEDIUM" | "HIGH",
        "key_risks": ["risk1", "risk2"],
        "stop_loss": dollar amount or null
    }},
    "summary": "2-3 sentence executive summary"
}}

Be conservative with recommendations. Account for transaction costs ($1-2 per trade).
Prioritize capital preservation over aggressive profit-taking."""

        return prompt

    def _call_claude(self, prompt: str) -> str:
        """Call Claude 3.5 Sonnet"""
        try:
            message = self.claude_client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=2000,
                temperature=0.3,  # Lower temp for consistent financial analysis
                messages=[{
                    "role": "user",
                    "content": prompt
                }]
            )

            # Track cost
            input_tokens = message.usage.input_tokens
            output_tokens = message.usage.output_tokens
            cost = (
                (input_tokens / 1_000_000) * self.pricing["claude-3-5-sonnet"]["input"] +
                (output_tokens / 1_000_000) * self.pricing["claude-3-5-sonnet"]["output"]
            )
            self.monthly_cost += cost

            logger.info(f"Claude API call: ${cost:.4f} (Total: ${self.monthly_cost:.2f})")

            return message.content[0].text

        except Exception as e:
            logger.error(f"Claude API error: {e}")
            raise

    def _call_gpt4o(self, prompt: str) -> str:
        """Call GPT-4o"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4o",
                messages=[{
                    "role": "system",
                    "content": "You are an expert options trading analyst. Provide analysis in valid JSON format."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3,
                max_tokens=2000,
                response_format={"type": "json_object"}
            )

            # Track cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = (
                (input_tokens / 1_000_000) * self.pricing["gpt-4o"]["input"] +
                (output_tokens / 1_000_000) * self.pricing["gpt-4o"]["output"]
            )
            self.monthly_cost += cost

            logger.info(f"GPT-4o API call: ${cost:.4f} (Total: ${self.monthly_cost:.2f})")

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"GPT-4o API error: {e}")
            raise

    def _call_deepseek(self, prompt: str) -> str:
        """Call DeepSeek (cheap bulk analysis)"""
        try:
            response = self.deepseek_client.chat.completions.create(
                model="deepseek-chat",
                messages=[{
                    "role": "system",
                    "content": "You are a financial analyst. Return valid JSON."
                }, {
                    "role": "user",
                    "content": prompt
                }],
                temperature=0.3,
                max_tokens=2000
            )

            # Track cost
            input_tokens = response.usage.prompt_tokens
            output_tokens = response.usage.completion_tokens
            cost = (
                (input_tokens / 1_000_000) * self.pricing["deepseek-chat"]["input"] +
                (output_tokens / 1_000_000) * self.pricing["deepseek-chat"]["output"]
            )
            self.monthly_cost += cost

            logger.info(f"DeepSeek API call: ${cost:.4f} (Total: ${self.monthly_cost:.2f})")

            return response.choices[0].message.content

        except Exception as e:
            logger.error(f"DeepSeek API error: {e}")
            raise

    def get_cost_summary(self) -> Dict[str, float]:
        """Get cost tracking summary"""
        return {
            "monthly_cost": round(self.monthly_cost, 2),
            "max_monthly_cost": self.max_monthly_cost,
            "remaining_budget": round(self.max_monthly_cost - self.monthly_cost, 2),
            "budget_used_pct": round((self.monthly_cost / self.max_monthly_cost) * 100, 1)
        }


# Example usage
if __name__ == "__main__":
    client = LLMClient()

    # Test trade analysis
    analysis = client.analyze_trade(
        symbol="NVDA",
        strike=135.0,
        expiration="2025-11-21",
        premium=250.0,
        current_value=-50.0,
        days_to_expiry=15,
        stock_price=142.50,
        model=ModelProvider.CLAUDE
    )

    print("\n" + "="*80)
    print("TRADE ANALYSIS RESULTS")
    print("="*80)
    print(json.dumps(analysis, indent=2))

    # Cost summary
    print("\n" + "="*80)
    print("COST SUMMARY")
    print("="*80)
    print(json.dumps(client.get_cost_summary(), indent=2))
```

---

## Step 4: Upgrade AI Trade Analyzer

Create `C:\Code\WheelStrategy\src\ai_trade_analyzer_v2.py`:

```python
"""
Enhanced AI Trade Analyzer using Claude 3.5 Sonnet
Replaces rule-based logic with LLM-powered analysis
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import yfinance as yf
from src.llm_client import LLMClient, ModelProvider
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class AITradeAnalyzerV2:
    """Enhanced AI analyzer using Claude 3.5 Sonnet"""

    def __init__(self):
        self.llm_client = LLMClient()

    def analyze_csp(
        self,
        symbol: str,
        strike: float,
        expiration: str,
        premium_collected: float,
        current_value: float,
        days_to_expiry: int
    ) -> Dict[str, Any]:
        """
        Analyze CSP position using Claude

        Args:
            symbol: Stock ticker
            strike: Strike price
            expiration: Expiration date
            premium_collected: Premium collected
            current_value: Current option value
            days_to_expiry: Days to expiry

        Returns:
            Enhanced analysis with Greeks, probabilities, recommendations
        """
        # Get current stock price
        try:
            ticker = yf.Ticker(symbol)
            stock_price = ticker.info.get('currentPrice', strike)
        except:
            stock_price = strike
            logger.warning(f"Could not fetch stock price for {symbol}, using strike")

        # Call LLM for analysis
        try:
            analysis = self.llm_client.analyze_trade(
                symbol=symbol,
                strike=strike,
                expiration=expiration,
                premium=premium_collected,
                current_value=current_value,
                days_to_expiry=days_to_expiry,
                stock_price=stock_price,
                model=ModelProvider.CLAUDE
            )

            # Add legacy fields for backward compatibility
            analysis['symbol'] = symbol
            analysis['current_price'] = stock_price
            analysis['strike'] = strike
            analysis['is_itm'] = stock_price < strike
            analysis['moneyness_pct'] = ((stock_price - strike) / strike) * 100
            analysis['profit_if_closed'] = premium_collected - abs(current_value)
            analysis['profit_percentage'] = (
                (analysis['profit_if_closed'] / premium_collected * 100)
                if premium_collected > 0 else 0
            )
            analysis['cost_to_close'] = abs(current_value)
            analysis['days_to_expiry'] = days_to_expiry

            # Map LLM recommendation to legacy format
            llm_action = analysis['recommendation']['action']
            action_map = {
                'CLOSE_NOW': 'BUY_BACK_IMMEDIATELY',
                'HOLD': 'HOLD_POSITION',
                'ROLL': 'CONSIDER_ROLLING',
                'PREPARE_ASSIGNMENT': 'PREPARE_FOR_ASSIGNMENT'
            }

            analysis['recommendation_legacy'] = {
                'action': action_map.get(llm_action, 'HOLD_POSITION'),
                'reason': analysis['recommendation']['reasoning'][:100],
                'detail': analysis['recommendation']['reasoning'],
                'urgency': 'HIGH' if analysis['recommendation']['confidence'] > 80 else 'MEDIUM',
                'emoji': self._get_emoji(llm_action)
            }

            # Add risk level
            analysis['risk_level'] = analysis['risk_assessment']['level']

            # Calculate annual return
            analysis['annual_return'] = self._calculate_annual_return(
                analysis['profit_percentage'],
                days_to_expiry
            )

            return analysis

        except Exception as e:
            logger.error(f"LLM analysis failed for {symbol}: {e}")
            # Fallback to simple rule-based
            return self._fallback_analysis(
                symbol, strike, expiration, premium_collected,
                current_value, days_to_expiry, stock_price
            )

    def analyze_sentiment(
        self,
        symbol: str,
        news_text: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze sentiment for a symbol

        Args:
            symbol: Stock ticker
            news_text: Optional news text to analyze

        Returns:
            Sentiment analysis
        """
        if not news_text:
            # Fetch recent news
            try:
                ticker = yf.Ticker(symbol)
                news = ticker.news[:3]  # Get 3 most recent news items
                news_text = " ".join([
                    item.get('title', '') + " " + item.get('summary', '')
                    for item in news
                ])
            except:
                return {
                    "sentiment": "NEUTRAL",
                    "confidence": 0,
                    "error": "No news available"
                }

        return self.llm_client.analyze_sentiment(news_text, symbol)

    def get_portfolio_recommendations(
        self,
        positions: List[Dict]
    ) -> Dict[str, Any]:
        """
        Get recommendations for entire portfolio

        Args:
            positions: List of position dicts

        Returns:
            Portfolio-level recommendations
        """
        recommendations = []
        buyback_candidates = []

        for pos in positions:
            if pos.get('Type') == 'CSP':
                try:
                    analysis = self.analyze_csp(
                        pos['Symbol'],
                        pos.get('Strike', 0),
                        pos.get('Expiration', ''),
                        pos.get('Premium', 0),
                        pos.get('Current Value', 0),
                        pos.get('Days to Expiry', 0)
                    )

                    recommendations.append(analysis)

                    # Track buyback candidates
                    if analysis['recommendation']['action'] in ['CLOSE_NOW', 'BUY_BACK_IMMEDIATELY']:
                        buyback_candidates.append({
                            'symbol': analysis['symbol'],
                            'profit': analysis['profit_if_closed'],
                            'profit_pct': analysis['profit_percentage'],
                            'cost': analysis['cost_to_close'],
                            'confidence': analysis['recommendation']['confidence']
                        })

                except Exception as e:
                    logger.error(f"Failed to analyze position {pos.get('Symbol')}: {e}")
                    continue

        return {
            'recommendations': recommendations,
            'buyback_candidates': sorted(
                buyback_candidates,
                key=lambda x: x['confidence'],
                reverse=True
            ),
            'total_positions': len(positions),
            'suggested_action': self._get_portfolio_action(buyback_candidates),
            'cost_summary': self.llm_client.get_cost_summary()
        }

    def _get_emoji(self, action: str) -> str:
        """Get emoji for action"""
        emoji_map = {
            'CLOSE_NOW': '🎯',
            'HOLD': '💎',
            'ROLL': '🔄',
            'PREPARE_ASSIGNMENT': '⚠️'
        }
        return emoji_map.get(action, '📊')

    def _calculate_annual_return(self, profit_pct: float, days_to_expiry: int) -> float:
        """Calculate annualized return"""
        if days_to_expiry <= 0:
            return 0
        days_held = 45 - days_to_expiry
        if days_held <= 0:
            days_held = 1
        return (profit_pct / days_held) * 365

    def _get_portfolio_action(self, buyback_candidates: List[Dict]) -> str:
        """Get overall portfolio action"""
        if len(buyback_candidates) >= 3:
            return "🔥 Multiple profitable exits available!"
        elif len(buyback_candidates) >= 1:
            total_profit = sum(c['profit'] for c in buyback_candidates)
            return f"💰 Close {len(buyback_candidates)} position(s) to capture ${total_profit:.2f}"
        else:
            return "Hold all positions for continued theta decay"

    def _fallback_analysis(
        self,
        symbol: str,
        strike: float,
        expiration: str,
        premium: float,
        current_value: float,
        days_to_expiry: int,
        stock_price: float
    ) -> Dict[str, Any]:
        """Fallback to rule-based if LLM fails"""
        profit = premium - abs(current_value)
        profit_pct = (profit / premium * 100) if premium > 0 else 0
        is_itm = stock_price < strike

        return {
            'symbol': symbol,
            'current_price': stock_price,
            'strike': strike,
            'is_itm': is_itm,
            'greeks': {
                'delta': 0.3 if not is_itm else 0.7,
                'theta': premium / days_to_expiry if days_to_expiry > 0 else 0,
                'explanation': "Estimated using fallback logic (LLM unavailable)"
            },
            'probabilities': {
                'profit': 70 if not is_itm else 30,
                'assignment': 10 if not is_itm else 60
            },
            'recommendation': {
                'action': 'HOLD',
                'confidence': 50,
                'reasoning': 'Using fallback analysis - LLM unavailable'
            },
            'risk_assessment': {
                'level': 'MEDIUM',
                'key_risks': ['LLM analysis unavailable']
            },
            'profit_if_closed': profit,
            'profit_percentage': profit_pct,
            'error': 'Using fallback logic'
        }


# Example usage
if __name__ == "__main__":
    analyzer = AITradeAnalyzerV2()

    # Test CSP analysis
    analysis = analyzer.analyze_csp(
        symbol='NVDA',
        strike=135.0,
        expiration='2025-11-21',
        premium_collected=250.0,
        current_value=-50.0,
        days_to_expiry=15
    )

    print("\n" + "="*80)
    print("CSP ANALYSIS")
    print("="*80)
    import json
    print(json.dumps(analysis, indent=2))

    # Test sentiment analysis
    sentiment = analyzer.analyze_sentiment('NVDA')
    print("\n" + "="*80)
    print("SENTIMENT ANALYSIS")
    print("="*80)
    print(json.dumps(sentiment, indent=2))
```

---

## Step 5: Integration Testing

Create `C:\Code\WheelStrategy\test_llm_integration.py`:

```python
"""Test LLM integration"""

from src.ai_trade_analyzer_v2 import AITradeAnalyzerV2
import json


def test_csp_analysis():
    """Test CSP analysis with Claude"""
    analyzer = AITradeAnalyzerV2()

    print("\n" + "="*80)
    print("TEST 1: Profitable CSP (75% profit captured)")
    print("="*80)

    analysis = analyzer.analyze_csp(
        symbol='AAPL',
        strike=180.0,
        expiration='2025-11-14',
        premium_collected=200.0,
        current_value=-50.0,  # Down from $200 to $50
        days_to_expiry=8
    )

    print(f"\nRecommendation: {analysis['recommendation']['action']}")
    print(f"Confidence: {analysis['recommendation']['confidence']}%")
    print(f"Reasoning: {analysis['recommendation']['reasoning']}")
    print(f"\nGreeks:")
    print(f"  Delta: {analysis['greeks']['delta']}")
    print(f"  Theta: ${analysis['greeks']['theta']}/day")
    print(f"\nProbabilities:")
    print(f"  Profit: {analysis['probabilities']['profit']}%")
    print(f"  Assignment: {analysis['probabilities']['assignment']}%")


def test_sentiment():
    """Test sentiment analysis"""
    analyzer = AITradeAnalyzerV2()

    print("\n" + "="*80)
    print("TEST 2: Sentiment Analysis")
    print("="*80)

    # Test with sample news
    news = """
    Apple announces record iPhone sales for Q4 2025. Revenue beats
    analyst expectations by 15%. CEO Tim Cook announces new AI features
    coming to all devices. Stock jumps 5% in after-hours trading.
    """

    sentiment = analyzer.analyze_sentiment('AAPL', news_text=news)

    print(f"\nSentiment: {sentiment.get('sentiment')}")
    print(f"Confidence: {sentiment.get('confidence')}%")
    print(f"Key Phrases: {sentiment.get('key_phrases')}")


def test_cost_tracking():
    """Test cost tracking"""
    analyzer = AITradeAnalyzerV2()

    # Run multiple analyses
    for i in range(3):
        analyzer.analyze_csp(
            symbol='NVDA',
            strike=140.0,
            expiration='2025-11-21',
            premium_collected=300.0,
            current_value=-100.0,
            days_to_expiry=15
        )

    print("\n" + "="*80)
    print("TEST 3: Cost Tracking")
    print("="*80)

    cost_summary = analyzer.llm_client.get_cost_summary()
    print(json.dumps(cost_summary, indent=2))


if __name__ == "__main__":
    test_csp_analysis()
    test_sentiment()
    test_cost_tracking()

    print("\n" + "="*80)
    print("ALL TESTS COMPLETE")
    print("="*80)
```

---

## Cost Optimization Strategies

### 1. Caching
Cache LLM responses for identical requests:

```python
import hashlib
import json
from functools import lru_cache

class CachedLLMClient(LLMClient):
    """LLM client with caching"""

    @lru_cache(maxsize=1000)
    def analyze_trade_cached(self, cache_key: str, **kwargs):
        """Cached version of analyze_trade"""
        return super().analyze_trade(**kwargs)

    def analyze_trade(self, **kwargs):
        # Create cache key from inputs
        cache_key = hashlib.md5(
            json.dumps(kwargs, sort_keys=True).encode()
        ).hexdigest()

        return self.analyze_trade_cached(cache_key, **kwargs)
```

### 2. Prompt Optimization
Reduce token usage:

```python
# Bad: 500 tokens
prompt = f"""
You are an expert options trader with 20 years of experience...
[long preamble]
Please analyze this position...
[verbose instructions]
"""

# Good: 200 tokens
prompt = f"""Analyze CSP:
Symbol: {symbol}, Strike: {strike}, DTE: {days}
Return JSON: {{"action": "", "confidence": 0-100, "reasoning": ""}}"""
```

### 3. Model Selection
Route by complexity:

```python
def analyze_trade_smart(self, **kwargs):
    """Use cheapest model that meets accuracy needs"""

    days_to_expiry = kwargs['days_to_expiry']
    premium = kwargs['premium']

    # High value or complex = Claude
    if premium > 500 or days_to_expiry > 30:
        return self.analyze_trade(model=ModelProvider.CLAUDE, **kwargs)

    # Medium = GPT-4o
    elif premium > 100:
        return self.analyze_trade(model=ModelProvider.GPT4O, **kwargs)

    # Low value = DeepSeek
    else:
        return self.analyze_trade(model=ModelProvider.DEEPSEEK, **kwargs)
```

### 4. Batch Processing
Combine multiple analyses:

```python
def analyze_portfolio_batch(self, positions: List[Dict]) -> List[Dict]:
    """Analyze multiple positions in one API call"""

    batch_prompt = "Analyze these CSP positions:\n"
    for i, pos in enumerate(positions):
        batch_prompt += f"\n{i+1}. {pos['symbol']} ${pos['strike']} {pos['days']}d"

    batch_prompt += "\n\nReturn JSON array of analyses."

    # Single API call for all positions
    response = self._call_claude(batch_prompt)
    return json.loads(response)
```

---

## Monitoring & Alerting

### Cost Alert System

```python
# In llm_client.py
def _check_budget(self):
    """Check if approaching budget limit"""
    if self.monthly_cost >= self.max_monthly_cost * 0.9:
        logger.warning(
            f"LLM budget at {self.get_cost_summary()['budget_used_pct']}%!"
        )
        # Send alert (integrate with telegram_notifier.py)
        from src.telegram_notifier import TelegramNotifier
        notifier = TelegramNotifier()
        notifier.send_alert(
            f"⚠️ LLM Budget Alert: ${self.monthly_cost:.2f} / ${self.max_monthly_cost}"
        )
```

### Performance Tracking

```python
import time

class MonitoredLLMClient(LLMClient):
    """Track latency and error rates"""

    def __init__(self):
        super().__init__()
        self.metrics = {
            'total_calls': 0,
            'errors': 0,
            'avg_latency': 0
        }

    def _call_claude(self, prompt: str) -> str:
        start = time.time()
        self.metrics['total_calls'] += 1

        try:
            result = super()._call_claude(prompt)
            latency = time.time() - start
            self.metrics['avg_latency'] = (
                (self.metrics['avg_latency'] * (self.metrics['total_calls'] - 1) + latency)
                / self.metrics['total_calls']
            )
            return result

        except Exception as e:
            self.metrics['errors'] += 1
            logger.error(f"Error rate: {self.metrics['errors']}/{self.metrics['total_calls']}")
            raise

    def get_metrics(self):
        return {
            **self.metrics,
            'error_rate': self.metrics['errors'] / max(self.metrics['total_calls'], 1)
        }
```

---

## Deployment Checklist

- [ ] Install dependencies (`pip install -r requirements.txt`)
- [ ] Add API keys to `.env` file
- [ ] Test LLM client (`python src/llm_client.py`)
- [ ] Run integration tests (`python test_llm_integration.py`)
- [ ] Update dashboard to use AITradeAnalyzerV2
- [ ] Set cost budget alerts
- [ ] Enable caching for production
- [ ] Monitor first week of usage
- [ ] A/B test vs old analyzer
- [ ] Document any issues in GitHub

---

## Troubleshooting

### Issue: "API Key Invalid"
**Solution:** Check `.env` file, ensure no extra spaces

```bash
# Wrong
ANTHROPIC_API_KEY= sk-ant-...  # Extra space

# Correct
ANTHROPIC_API_KEY=sk-ant-...
```

### Issue: "Rate Limit Exceeded"
**Solution:** Implement exponential backoff

```python
import time

def _call_claude_with_retry(self, prompt: str, max_retries=3):
    for attempt in range(max_retries):
        try:
            return self._call_claude(prompt)
        except anthropic.RateLimitError:
            if attempt < max_retries - 1:
                wait = 2 ** attempt
                logger.warning(f"Rate limited, waiting {wait}s...")
                time.sleep(wait)
            else:
                raise
```

### Issue: "JSON Parse Error"
**Solution:** Add response validation

```python
def _validate_json(self, response: str) -> Dict:
    """Validate and repair JSON"""
    try:
        return json.loads(response)
    except json.JSONDecodeError:
        # Try to extract JSON from markdown
        if "```json" in response:
            json_str = response.split("```json")[1].split("```")[0]
            return json.loads(json_str)
        raise
```

---

## Next Steps

1. **Week 1:** Implement basic Claude integration
2. **Week 2:** Add sentiment analysis with FinGPT
3. **Week 3:** Implement cost tracking and alerts
4. **Week 4:** A/B test vs old analyzer, measure accuracy

---

**Document Version:** 1.0
**Last Updated:** November 6, 2025
