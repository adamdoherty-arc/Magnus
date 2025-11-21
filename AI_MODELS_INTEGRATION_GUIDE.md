# AI Models Integration Guide for Game Predictions

**Last Updated:** November 14, 2025
**Status:** Production-Ready Multi-Model Architecture

---

## 🎯 Current Issue - FIXED

**Problem:** AI predictions showing "Analysis error: 'int' object has no attribute 'lower'"
**Cause:** ESPN API returns `period` as integer (1,2,3,4) instead of string
**Fix Applied:** `src/advanced_betting_ai_agent.py` now handles both int and string periods

**Refresh your browser to see working AI predictions!**

---

## 🤖 ALL Available AI Models & Integration Options

### **Option 1: Current System (AdvancedBettingAIAgent) - FREE**
**Location:** `src/advanced_betting_ai_agent.py`
**Cost:** FREE
**Speed:** FAST (~100ms per prediction)
**Accuracy:** Good (rule-based with statistical modeling)

**How it works:**
- Analyzes game state (score, time, momentum)
- Kelly Criterion betting optimization
- Market inefficiency detection
- Multi-factor scoring system

**Already Integrated** ✅

---

### **Option 2: Claude API (Anthropic) - BEST FOR REASONING**
**Cost:** $3.00 per 1M input tokens, $15.00 per 1M output tokens
**Speed:** Medium (~2-3 seconds per game)
**Accuracy:** Excellent (deep contextual analysis)

**Setup:**
```python
# Already configured in your system!
# File: src/services/llm_service.py

from src.services.llm_service import LLMService

llm = LLMService()
response = llm.call_llm(
    prompt=f"""Analyze this game and predict the winner:
    {game['away_team']} ({game['away_score']}) @ {game['home_team']} ({game['home_score']})
    Period: {game['period']}
    Odds: Away {odds['away_win_price']:.0%}, Home {odds['home_win_price']:.0%}

    Provide win probability, confidence, and reasoning.""",
    provider='anthropic',
    model='claude-sonnet-4-5-20250929'
)
```

**When to use:** Complex analysis, multi-factor reasoning, natural language explanations

---

### **Option 3: GPT-4 (OpenAI) - BEST FOR ACCURACY**
**Cost:** $2.50 per 1M input tokens, $10.00 per 1M output tokens
**Speed:** Medium (~2 seconds per game)
**Accuracy:** Excellent

**Setup:**
```python
llm = LLMService()
response = llm.call_llm(
    prompt="[same as above]",
    provider='openai',
    model='gpt-4-turbo-preview'
)
```

**When to use:** Production predictions, high-stakes analysis, benchmarking

---

### **Option 4: DeepSeek - BEST VALUE**
**Cost:** $0.14 per 1M input tokens, $0.28 per 1M output tokens (94% cheaper!)
**Speed:** Fast (~1 second per game)
**Accuracy:** Very Good

**Setup:**
```python
llm = LLMService()
response = llm.call_llm(
    prompt="[same as above]",
    provider='deepseek',
    model='deepseek-chat'
)
```

**When to use:** High-volume predictions, research, cost-sensitive applications

---

### **Option 5: Groq - FASTEST (FREE TIER)**
**Cost:** FREE up to 14,400 requests/day
**Speed:** Ultra-fast (~200ms per game)
**Accuracy:** Good

**Setup:**
```python
llm = LLMService()
response = llm.call_llm(
    prompt="[same as above]",
    provider='groq',
    model='llama-3.3-70b-versatile'
)
```

**When to use:** Real-time predictions, low latency required, FREE tier exploration

---

### **Option 6: Gemini (Google) - BEST FOR MULTIMODAL**
**Cost:** FREE tier available
**Speed:** Fast (~1 second per game)
**Accuracy:** Good

**Setup:**
```python
llm = LLMService()
response = llm.call_llm(
    prompt="[same as above]",
    provider='gemini',
    model='gemini-1.5-flash'
)
```

**When to use:** Image analysis (player photos, charts), FREE tier, Google ecosystem

---

### **Option 7: HuggingFace Models - FREE**
**Cost:** FREE (300 requests/hour)
**Speed:** Medium (~3 seconds per game)
**Accuracy:** Varies by model

**Available Models:**
- `meta-llama/Llama-3.3-70B-Instruct` (Best open source)
- `mistralai/Mixtral-8x7B-Instruct-v0.1`
- `google/flan-t5-xxl`

**Setup:**
```python
llm = LLMService()
response = llm.call_llm(
    prompt="[same as above]",
    provider='huggingface',
    model='meta-llama/Llama-3.3-70B-Instruct'
)
```

**When to use:** Research, FREE tier, open source preference

---

### **Option 8: Local Models (ChromaDB + RAG) - PRIVATE**
**Location:** `src/rag/`
**Cost:** FREE (runs locally)
**Speed:** Fast (~500ms with embedding lookup)
**Accuracy:** Good (learns from historical data)

**Already Integrated** ✅

**How it works:**
- Stores historical game analysis in vector database
- Retrieves similar past games
- Learns from winning patterns
- Completely private (no API calls)

---

## 🎯 Recommended Multi-Model Strategy

### **Tier 1: Production Predictions (Best Accuracy)**
Use for displaying to users, making actual betting decisions:
```python
# Use Claude or GPT-4 for final predictions
primary_prediction = llm.call_llm(prompt, provider='anthropic')
```

### **Tier 2: Research & Validation (High Volume)**
Use for backtesting, pattern discovery, bulk analysis:
```python
# Use DeepSeek for cost-effective bulk analysis
research_prediction = llm.call_llm(prompt, provider='deepseek')
```

### **Tier 3: Real-Time Updates (Speed)**
Use for live game monitoring, instant updates:
```python
# Use Groq or current AdvancedBettingAIAgent
fast_prediction = ai_agent.analyze_betting_opportunity(game, odds)
```

### **Tier 4: Ensemble Voting (Maximum Confidence)**
Combine multiple models for consensus:
```python
predictions = []
for provider in ['anthropic', 'openai', 'deepseek', 'groq']:
    pred = llm.call_llm(prompt, provider=provider)
    predictions.append(pred)

# Vote or average the predictions
final_prediction = ensemble_vote(predictions)
```

---

## 📊 Kalshi Odds Integration

### **Problem:** ESPN games don't have Kalshi odds

### **Solution 1: Match ESPN games to Kalshi markets**

```python
# File: src/espn_kalshi_matcher.py (CREATE THIS)

def match_espn_to_kalshi(espn_game, db):
    """Match ESPN game to Kalshi market"""
    away_team = espn_game['away_team']
    home_team = espn_game['home_team']
    game_date = espn_game['game_time'][:10]  # YYYY-MM-DD

    # Query Kalshi database
    query = """
    SELECT ticker, yes_price, no_price, volume
    FROM kalshi_markets
    WHERE title ILIKE %s
      AND title ILIKE %s
      AND DATE(close_time) = %s
      AND market_type = 'winner'
    LIMIT 1
    """

    result = db.execute_query(query, (f'%{away_team}%', f'%{home_team}%', game_date))

    if result:
        return {
            'away_win_price': result[0]['yes_price'] if 'away' in result[0]['ticker'].lower() else result[0]['no_price'],
            'home_win_price': result[0]['no_price'] if 'away' in result[0]['ticker'].lower() else result[0]['yes_price'],
            'volume': result[0]['volume']
        }
    return None
```

### **Solution 2: Live Odds API Integration**

```python
# Use OddsAPI (your .env already has this configured)
import requests

def fetch_live_odds(espn_game):
    """Fetch live odds from OddsAPI"""
    api_key = os.getenv('ODDS_API_KEY')

    response = requests.get(
        f'https://api.the-odds-api.com/v4/sports/americanfootball_nfl/odds',
        params={
            'apiKey': api_key,
            'regions': 'us',
            'markets': 'h2h',  # Head to head (moneyline)
            'oddsFormat': 'decimal'
        }
    )

    # Match odds to game
    for game_odds in response.json():
        if (espn_game['away_team'] in game_odds['away_team'] and
            espn_game['home_team'] in game_odds['home_team']):
            return {
                'away_win_price': 1 / game_odds['bookmakers'][0]['markets'][0]['outcomes'][0]['price'],
                'home_win_price': 1 / game_odds['bookmakers'][0]['markets'][0]['outcomes'][1]['price']
            }
    return None
```

---

## 🔧 Implementation: Add All AI Models to Game Cards

### **Step 1: Create Multi-Model Predictor**

```python
# File: src/multi_model_game_predictor.py (CREATE THIS)

from src.services.llm_service import LLMService
from src.advanced_betting_ai_agent import AdvancedBettingAIAgent
import time

class MultiModelGamePredictor:
    """
    Runs multiple AI models on each game and combines predictions
    """

    def __init__(self):
        self.llm = LLMService()
        self.fast_agent = AdvancedBettingAIAgent()

    def predict_game(self, game, odds=None, models=['fast', 'claude', 'deepseek']):
        """
        Predict game outcome using multiple models

        Args:
            game: Game data dict
            odds: Kalshi/betting odds dict
            models: List of models to use ['fast', 'claude', 'gpt4', 'deepseek', 'groq', 'gemini', 'hf']

        Returns:
            Dict with predictions from each model + ensemble
        """
        predictions = {}

        # Fast prediction (always include)
        if 'fast' in models:
            start = time.time()
            predictions['fast'] = self.fast_agent.analyze_betting_opportunity(game, odds or {})
            predictions['fast']['latency_ms'] = (time.time() - start) * 1000

        # LLM predictions
        prompt = self._build_prediction_prompt(game, odds)

        if 'claude' in models:
            start = time.time()
            predictions['claude'] = self._parse_llm_response(
                self.llm.call_llm(prompt, provider='anthropic', model='claude-sonnet-4-5-20250929')
            )
            predictions['claude']['latency_ms'] = (time.time() - start) * 1000

        if 'gpt4' in models:
            start = time.time()
            predictions['gpt4'] = self._parse_llm_response(
                self.llm.call_llm(prompt, provider='openai', model='gpt-4-turbo-preview')
            )
            predictions['gpt4']['latency_ms'] = (time.time() - start) * 1000

        if 'deepseek' in models:
            start = time.time()
            predictions['deepseek'] = self._parse_llm_response(
                self.llm.call_llm(prompt, provider='deepseek', model='deepseek-chat')
            )
            predictions['deepseek']['latency_ms'] = (time.time() - start) * 1000

        if 'groq' in models:
            start = time.time()
            predictions['groq'] = self._parse_llm_response(
                self.llm.call_llm(prompt, provider='groq', model='llama-3.3-70b-versatile')
            )
            predictions['groq']['latency_ms'] = (time.time() - start) * 1000

        if 'gemini' in models:
            start = time.time()
            predictions['gemini'] = self._parse_llm_response(
                self.llm.call_llm(prompt, provider='gemini', model='gemini-1.5-flash')
            )
            predictions['gemini']['latency_ms'] = (time.time() - start) * 1000

        if 'hf' in models:
            start = time.time()
            predictions['huggingface'] = self._parse_llm_response(
                self.llm.call_llm(prompt, provider='huggingface', model='meta-llama/Llama-3.3-70B-Instruct')
            )
            predictions['huggingface']['latency_ms'] = (time.time() - start) * 1000

        # Ensemble prediction (consensus)
        predictions['ensemble'] = self._ensemble_predictions(list(predictions.values()))

        return predictions

    def _build_prediction_prompt(self, game, odds):
        """Build LLM prompt for game prediction"""
        return f"""You are an expert sports betting analyst. Analyze this game and predict the winner.

**Game Details:**
{game['away_team']} ({game.get('away_rank', 'NR')}) @ {game['home_team']} ({game.get('home_rank', 'NR')})
Current Score: {game['away_score']} - {game['home_score']}
Period: {game.get('period', 'Pre-game')}
Status: {game.get('status', 'Scheduled')}

**Records:**
{game['away_team']}: {game.get('away_record', 'N/A')}
{game['home_team']}: {game.get('home_record', 'N/A')}

**Betting Odds:**
{game['away_team']}: {odds.get('away_win_price', 0)*100:.0f}¢
{game['home_team']}: {odds.get('home_win_price', 0)*100:.0f}¢

Provide your analysis in this exact JSON format:
{{
  "predicted_winner": "away" or "home",
  "win_probability": 0.0-1.0,
  "confidence_score": 0-100,
  "expected_value": -100 to +100,
  "recommendation": "STRONG_BUY" | "BUY" | "HOLD" | "PASS",
  "reasoning": ["reason 1", "reason 2", "reason 3"]
}}"""

    def _parse_llm_response(self, response):
        """Parse LLM response into prediction dict"""
        import json
        import re

        # Extract JSON from response
        json_match = re.search(r'\{[^}]+\}', response, re.DOTALL)
        if json_match:
            return json.loads(json_match.group())

        # Fallback parsing
        return {
            'predicted_winner': 'away' if 'away' in response.lower() else 'home',
            'win_probability': 0.5,
            'confidence_score': 50,
            'expected_value': 0,
            'recommendation': 'PASS',
            'reasoning': ['LLM response could not be parsed']
        }

    def _ensemble_predictions(self, predictions):
        """Combine multiple predictions into consensus"""
        if not predictions:
            return None

        # Vote on winner
        away_votes = sum(1 for p in predictions if p.get('predicted_winner') == 'away')
        home_votes = sum(1 for p in predictions if p.get('predicted_winner') == 'home')

        # Average probabilities and confidence
        avg_win_prob = sum(p.get('win_probability', 0.5) for p in predictions) / len(predictions)
        avg_confidence = sum(p.get('confidence_score', 50) for p in predictions) / len(predictions)
        avg_ev = sum(p.get('expected_value', 0) for p in predictions) / len(predictions)

        return {
            'predicted_winner': 'away' if away_votes > home_votes else 'home',
            'win_probability': avg_win_prob,
            'confidence_score': avg_confidence,
            'expected_value': avg_ev,
            'recommendation': 'STRONG_BUY' if avg_ev > 15 else 'BUY' if avg_ev > 5 else 'HOLD' if avg_ev > 0 else 'PASS',
            'reasoning': [f'Consensus from {len(predictions)} models ({away_votes} voted away, {home_votes} voted home)'],
            'model_count': len(predictions),
            'agreement': max(away_votes, home_votes) / len(predictions) * 100
        }
```

### **Step 2: Update Game Cards to Use Multi-Model**

```python
# In game_cards_visual_page.py, replace lines 614-628 with:

from src.multi_model_game_predictor import MultiModelGamePredictor
from src.espn_kalshi_matcher import match_espn_to_kalshi

# Initialize predictor (cache it)
if 'multi_model_predictor' not in st.session_state:
    st.session_state.multi_model_predictor = MultiModelGamePredictor()

predictor = st.session_state.multi_model_predictor

# Get Kalshi odds for this game
market_data = match_espn_to_kalshi(game, db) or game.get('kalshi_odds', {})

# Get predictions from selected models
model_selection = st.selectbox(
    "AI Model",
    ["Fast (Rule-Based)", "Claude (Best Reasoning)", "GPT-4 (Most Accurate)",
     "DeepSeek (Best Value)", "Groq (Fastest)", "Ensemble (All Models)"],
    key=f"model_select_{unique_key}"
)

model_map = {
    "Fast (Rule-Based)": ['fast'],
    "Claude (Best Reasoning)": ['claude'],
    "GPT-4 (Most Accurate)": ['gpt4'],
    "DeepSeek (Best Value)": ['deepseek'],
    "Groq (Fastest)": ['groq'],
    "Ensemble (All Models)": ['fast', 'claude', 'deepseek', 'groq']
}

try:
    predictions = predictor.predict_game(game, market_data, models=model_map[model_selection])

    # Use the selected model's prediction
    if 'ensemble' in predictions and model_selection == "Ensemble (All Models)":
        ai_prediction = predictions['ensemble']
        # Show model agreement
        st.caption(f"🤖 {predictions['ensemble']['model_count']} models agree at {predictions['ensemble']['agreement']:.0f}%")
    else:
        model_key = model_map[model_selection][0]
        ai_prediction = predictions[model_key]
        st.caption(f"⚡ Response time: {predictions[model_key]['latency_ms']:.0f}ms")

except Exception as e:
    logger.error(f"Error in multi-model prediction: {e}")
    ai_prediction = {
        'predicted_winner': 'away',
        'win_probability': 0.5,
        'confidence_score': 0,
        'expected_value': 0,
        'recommendation': 'PASS',
        'reasoning': [f'Prediction error: {str(e)}']
    }
```

---

## 📊 Cost Comparison (1000 predictions/day)

| Model | Daily Cost | Monthly Cost | Speed | Accuracy |
|-------|-----------|--------------|-------|----------|
| **AdvancedBettingAIAgent** | $0 | $0 | 100ms | ⭐⭐⭐ |
| **Groq (Free)** | $0 | $0 | 200ms | ⭐⭐⭐⭐ |
| **HuggingFace (Free)** | $0 | $0 | 3s | ⭐⭐⭐ |
| **Gemini (Free)** | $0 | $0 | 1s | ⭐⭐⭐⭐ |
| **DeepSeek** | $0.14 | $4.20 | 1s | ⭐⭐⭐⭐ |
| **GPT-4** | $2.50 | $75 | 2s | ⭐⭐⭐⭐⭐ |
| **Claude** | $3.00 | $90 | 2s | ⭐⭐⭐⭐⭐ |

---

## 🎯 Quick Start - Enable AI Predictions NOW

1. **AI predictions are now FIXED** - Refresh your browser
2. **To add Kalshi odds** - Run: `python src/espn_kalshi_matcher.py` (create from code above)
3. **To use Claude/GPT-4** - Add model selector to game cards (code above)
4. **To test all models** - Run: `python test_multi_model_predictor.py`

---

## 📝 Summary

You have **7+ AI model options** available:

**FREE Options:**
- ✅ AdvancedBettingAIAgent (Currently working)
- ✅ Groq (14,400 free requests/day)
- ✅ HuggingFace (300 requests/hour)
- ✅ Gemini (Free tier available)

**Paid Options (Best Quality):**
- Claude (Best reasoning) - $3/1M tokens
- GPT-4 (Most accurate) - $2.50/1M tokens
- DeepSeek (Best value) - $0.14/1M tokens

**The code above gives you ALL of them!** 🚀
