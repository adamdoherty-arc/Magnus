# AVA Custom LLM & Personality Integration Guide

**Last Updated:** 2025-11-21
**Version:** 2.0
**Author:** Magnus Trading Platform Team

---

## Table of Contents

1. [Overview](#overview)
2. [Current Architecture](#current-architecture)
3. [Personality System](#personality-system)
4. [Adding New LLM Models](#adding-new-llm-models)
5. [Custom Fine-Tuned Models](#custom-fine-tuned-models)
6. [Personality-Specific LLM Routing](#personality-specific-llm-routing)
7. [Integration Examples](#integration-examples)
8. [Best Practices](#best-practices)

---

## Overview

AVA's personality system is designed to provide diverse interaction styles while maintaining consistent, high-quality financial advice. This guide explains how to:

- Integrate new LLM providers (OpenAI, Anthropic, Cohere, etc.)
- Create custom fine-tuned models for specific personality modes
- Route different personalities to different LLMs for optimal performance
- Implement advanced prompt engineering for personality consistency

---

## Current Architecture

### LLM Stack

```
AVA Core (ava_core.py)
    ↓
LangGraph Workflow
    ↓
LLM Selection Logic
    ├── Groq (llama-3.3-70b-versatile) [FREE - Default]
    ├── OpenAI (gpt-4o-mini) [Paid]
    ├── DeepSeek [FREE Fallback]
    ├── Gemini [FREE Fallback]
    └── Local LLM (Ollama/Qwen) [FREE - Fast inference]
```

### Personality System

```
AVA Personality (ava_personality.py)
    ↓
10 Personality Modes
    ├── PROFESSIONAL - Formal, data-focused (CFA-style)
    ├── FRIENDLY - Warm, approachable (default)
    ├── WITTY - Humorous, clever banter
    ├── MENTOR - Teaching, patient guidance
    ├── CONCISE - Brief, essential data only
    ├── CHARMING - Flirty, playful
    ├── ANALYST - Bloomberg terminal style, quantitative (NEW)
    ├── COACH - Motivational, performance-focused (NEW)
    ├── REBEL - Contrarian, challenges conventional wisdom (NEW)
    └── GURU - Zen master, philosophical (NEW)
```

---

## Personality System

### File Structure

```
src/ava/
├── ava_personality.py          # Core personality system (427 lines)
│   ├── PersonalityMode (Enum)
│   ├── EmotionalState (Enum)
│   ├── GREETINGS
│   ├── RESPONSE_STYLES
│   ├── EMOTIONAL_EXPRESSIONS
│   └── MARKET_PHRASES
├── core/ava_core.py             # LLM integration (614 lines)
└── prompts/
    └── master_financial_advisor_prompt.py  # 696-line master prompt
```

### Personality Configuration

Each personality mode has:

1. **Greetings** - Time-aware, personality-specific welcome messages
2. **Response Styles** - Emoji usage, formality, data emphasis
3. **Emotional Expressions** - How each personality expresses emotions
4. **Market Phrases** - Personality-specific trading terminology

Example:

```python
# In ava_personality.py

PersonalityMode.ANALYST: {
    'emoji_usage': 'data_icons_only',  # 📊 📈 📉 only
    'exclamation': False,
    'casual_phrases': False,
    'formality': 'very_high',
    'data_emphasis': 'maximum_quantitative'
}
```

---

## Adding New LLM Models

### Method 1: Add to Existing LLMService (Recommended)

**File:** `src/services/llm_service.py`

```python
from langchain_anthropic import ChatAnthropic

class LLMService:
    def __init__(self):
        # Existing providers
        self.groq_llm = ChatGroq(...)
        self.openai_llm = ChatOpenAI(...)

        # ADD NEW PROVIDER
        self.anthropic_llm = ChatAnthropic(
            model="claude-sonnet-4-5",
            anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
            temperature=0.7,
            max_tokens=2000
        )

    def generate_response(self, prompt, provider="auto"):
        if provider == "anthropic":
            return self.anthropic_llm.invoke(prompt)
        elif provider == "groq":
            return self.groq_llm.invoke(prompt)
        # ... etc
```

### Method 2: Direct Integration in AVA Core

**File:** `src/ava/core/ava_core.py`

```python
from langchain_anthropic import ChatAnthropic
from langchain_community.llms import HuggingFaceHub

class AVACore:
    def __init__(self):
        # Existing LLM setup
        try:
            self.llm = ChatGroq(
                model="llama-3.3-70b-versatile",
                api_key=os.getenv('GROQ_API_KEY'),
                temperature=0.7
            )
        except:
            # ADD NEW FALLBACK MODEL
            self.llm = ChatAnthropic(
                model="claude-sonnet-4-5",
                anthropic_api_key=os.getenv('ANTHROPIC_API_KEY'),
                temperature=0.7
            )
```

### Method 3: Custom LLM Class (Advanced)

Create a custom LLM wrapper for full control:

```python
# src/ava/custom_llm_adapter.py

from langchain.llms.base import LLM
from typing import Optional, List

class CustomLLMAdapter(LLM):
    """Adapter for custom LLM APIs"""

    api_url: str
    api_key: str
    model_name: str

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        """Call your custom LLM API"""
        import requests

        response = requests.post(
            self.api_url,
            headers={"Authorization": f"Bearer {self.api_key}"},
            json={
                "model": self.model_name,
                "prompt": prompt,
                "temperature": 0.7,
                "max_tokens": 2000,
                "stop": stop
            }
        )

        return response.json()['choices'][0]['text']

    @property
    def _llm_type(self) -> str:
        return "custom_llm"


# Usage in ava_core.py
from src.ava.custom_llm_adapter import CustomLLMAdapter

self.llm = CustomLLMAdapter(
    api_url="https://api.your-llm-provider.com/v1/completions",
    api_key=os.getenv('CUSTOM_LLM_API_KEY'),
    model_name="your-model-name"
)
```

---

## Custom Fine-Tuned Models

### Creating Personality-Specific Fine-Tuned Models

**Scenario:** You want to fine-tune GPT-4o for the ANALYST personality mode.

#### Step 1: Prepare Training Data

Create a JSONL file with examples of ANALYST personality responses:

```jsonl
{"messages": [{"role": "system", "content": "You are AVA in ANALYST mode: Bloomberg-style, data-obsessed, quantitative financial advisor."}, {"role": "user", "content": "What do you think of AAPL?"}, {"role": "assistant", "content": "📊 AAPL Analysis:\n\nPrice: $180.25 (+1.2% today)\nP/E Ratio: 29.4x (vs sector avg 25.1x)\nRSI(14): 62.3 (neutral territory)\nEMA(50): $175.80 (bullish crossover)\n\n📈 Technical: Uptrend intact above 50-day EMA. Resistance at $185.\n\n💼 Fundamental: iPhone sales beat consensus by 3.2%. Services revenue growth: +12% YoY.\n\n⚡ Rating: BUY. Target: $195 (+8.2% upside). Stop: $172 (-4.6%)."}}, ...]}
{"messages": [{"role": "system", "content": "You are AVA in ANALYST mode: Bloomberg-style, data-obsessed, quantitative financial advisor."}, {"role": "user", "content": "Should I sell my SPY position?"}, {"role": "assistant", "content": "📉 Position Analysis Required:\n\nCurrent SPY: $500.15\nYour entry: [NEED DATA]\nP&L: [CALCULATING]\n\nMarket Context:\n- VIX: 14.2 (low volatility)\n- SPY RSI(14): 58.7 (neutral)\n- Above 50-day MA: YES (+2.1%)\n- Above 200-day MA: YES (+8.3%)\n\n📊 Recommendation: HOLD. Trend remains bullish. No sell signal detected. Consider trailing stop at $485 (-3%)."}}]
```

#### Step 2: Fine-Tune the Model

**OpenAI Fine-Tuning:**

```python
import openai

# Upload training file
file = openai.File.create(
    file=open("analyst_personality_training.jsonl", "rb"),
    purpose='fine-tune'
)

# Create fine-tuning job
fine_tune = openai.FineTuningJob.create(
    training_file=file.id,
    model="gpt-4o-mini-2024-07-18",
    suffix="ava-analyst"
)

# Wait for completion (check status)
print(f"Fine-tune job ID: {fine_tune.id}")
print(f"Status: {fine_tune.status}")

# Once complete, you'll get a model ID like:
# ft:gpt-4o-mini-2024-07-18:your-org:ava-analyst:abc123
```

#### Step 3: Integrate Fine-Tuned Model

```python
# In ava_core.py or llm_service.py

from langchain_openai import ChatOpenAI

# Map personality modes to specific models
PERSONALITY_MODELS = {
    PersonalityMode.ANALYST: ChatOpenAI(
        model="ft:gpt-4o-mini-2024-07-18:magnus:ava-analyst:abc123",
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.5  # Lower temp for analytical consistency
    ),
    PersonalityMode.COACH: ChatOpenAI(
        model="ft:gpt-4o-mini-2024-07-18:magnus:ava-coach:def456",
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.8  # Higher temp for motivational variety
    ),
    PersonalityMode.GURU: ChatOpenAI(
        model="ft:gpt-4o-mini-2024-07-18:magnus:ava-guru:ghi789",
        openai_api_key=os.getenv('OPENAI_API_KEY'),
        temperature=0.9  # High temp for philosophical creativity
    ),
    # Default for others
    'default': ChatGroq(model="llama-3.3-70b-versatile", ...)
}

def get_llm_for_personality(mode: PersonalityMode):
    """Get the appropriate LLM for the personality mode"""
    return PERSONALITY_MODELS.get(mode, PERSONALITY_MODELS['default'])
```

---

## Personality-Specific LLM Routing

### Advanced Routing Strategy

Create intelligent routing based on personality requirements:

```python
# src/ava/llm_router.py

from typing import Dict
from src.ava.ava_personality import PersonalityMode

class LLMRouter:
    """Route queries to optimal LLM based on personality and query type"""

    # Define LLM tiers
    TIER_PREMIUM = "premium"  # GPT-4, Claude Sonnet
    TIER_STANDARD = "standard"  # GPT-4o-mini, Groq
    TIER_FAST = "fast"  # Local LLM, Gemini Flash

    # Personality → Tier mapping
    PERSONALITY_TIERS = {
        PersonalityMode.ANALYST: TIER_PREMIUM,  # Need highest accuracy
        PersonalityMode.PROFESSIONAL: TIER_STANDARD,
        PersonalityMode.GURU: TIER_PREMIUM,  # Need creativity
        PersonalityMode.COACH: TIER_STANDARD,
        PersonalityMode.REBEL: TIER_STANDARD,
        PersonalityMode.WITTY: TIER_STANDARD,
        PersonalityMode.FRIENDLY: TIER_FAST,  # Can use local
        PersonalityMode.MENTOR: TIER_STANDARD,
        PersonalityMode.CONCISE: TIER_FAST,  # Fast responses
        PersonalityMode.CHARMING: TIER_FAST
    }

    # Query complexity detection
    COMPLEX_KEYWORDS = [
        'analyze', 'calculate', 'compare', 'evaluate',
        'backtest', 'optimize', 'forecast', 'predict'
    ]

    @classmethod
    def route(cls, personality: PersonalityMode, query: str) -> str:
        """Determine which LLM to use"""

        # Check if query is complex
        is_complex = any(kw in query.lower() for kw in cls.COMPLEX_KEYWORDS)

        # Get base tier from personality
        base_tier = cls.PERSONALITY_TIERS.get(personality, cls.TIER_STANDARD)

        # Upgrade to premium for complex queries
        if is_complex and base_tier == cls.TIER_STANDARD:
            return cls.TIER_PREMIUM

        return base_tier


# Usage in AVA Core

class AVACore:
    def process_message(self, user_message: str):
        # Get current personality
        personality = self.personality.mode

        # Route to appropriate LLM
        tier = LLMRouter.route(personality, user_message)

        if tier == LLMRouter.TIER_PREMIUM:
            llm = self.premium_llm  # Claude Sonnet or GPT-4
        elif tier == LLMRouter.TIER_STANDARD:
            llm = self.standard_llm  # Groq or GPT-4o-mini
        else:
            llm = self.fast_llm  # Local LLM or Gemini Flash

        # Generate response
        response = llm.invoke(self.build_prompt(user_message))
        return response
```

---

## Integration Examples

### Example 1: Add Cohere for ANALYST Mode

```python
# 1. Install library
# pip install cohere langchain-cohere

# 2. Add to ava_core.py
from langchain_cohere import ChatCohere

class AVACore:
    def __init__(self):
        # Add Cohere as ANALYST-specific LLM
        self.cohere_analyst = ChatCohere(
            model="command-r-plus",
            cohere_api_key=os.getenv('COHERE_API_KEY'),
            temperature=0.3,  # Low temp for analytical precision
            max_tokens=2000
        )

    def get_llm_for_personality(self):
        if self.personality.mode == PersonalityMode.ANALYST:
            return self.cohere_analyst
        else:
            return self.llm  # Default LLM
```

### Example 2: Local Fine-Tuned Qwen Model for COACH

```python
# 1. Fine-tune Qwen locally using LoRA
# (Requires: transformers, peft, datasets)

# 2. Load fine-tuned model in magnus_local_llm.py

from transformers import AutoModelForCausalLM, AutoTokenizer
import torch

class MagnusLocalLLM:
    def load_coach_model(self):
        """Load fine-tuned COACH personality model"""
        model_path = "./models/qwen-2.5-7b-coach-lora"

        self.coach_tokenizer = AutoTokenizer.from_pretrained(model_path)
        self.coach_model = AutoModelForCausalLM.from_pretrained(
            model_path,
            torch_dtype=torch.float16,
            device_map="auto"
        )

    def generate_coach_response(self, prompt):
        """Generate response using COACH model"""
        inputs = self.coach_tokenizer(prompt, return_tensors="pt")
        outputs = self.coach_model.generate(
            **inputs,
            max_new_tokens=500,
            temperature=0.8,  # Higher for motivational variety
            top_p=0.9
        )
        return self.coach_tokenizer.decode(outputs[0], skip_special_tokens=True)
```

### Example 3: Multi-Model Ensemble for GURU

```python
# Combine multiple models for philosophical depth

class GuruEnsemble:
    """Ensemble of LLMs for GURU personality"""

    def __init__(self):
        self.models = [
            ChatAnthropic(model="claude-sonnet-4-5"),  # Deep reasoning
            ChatOpenAI(model="gpt-4o"),  # Philosophical nuance
            ChatGroq(model="llama-3.3-70b-versatile")  # Creativity
        ]

    async def generate_ensemble_response(self, prompt):
        """Get responses from all models and synthesize"""

        # Generate from all models in parallel
        responses = await asyncio.gather(*[
            model.ainvoke(prompt) for model in self.models
        ])

        # Synthesize best aspects from each
        synthesis_prompt = f"""
        Synthesize these three philosophical responses into one zen-like answer:

        Response 1: {responses[0]}
        Response 2: {responses[1]}
        Response 3: {responses[2]}

        Create a single, unified philosophical response that captures
        the best wisdom from all three. Format as AVA's GURU personality.
        """

        final_response = await self.models[0].ainvoke(synthesis_prompt)
        return final_response
```

---

## Best Practices

### 1. Prompt Engineering Per Personality

Always prepend personality-specific system prompts:

```python
SYSTEM_PROMPTS = {
    PersonalityMode.ANALYST: """You are AVA in ANALYST mode.
        - Think like a Bloomberg terminal analyst
        - Always provide quantitative data
        - Use financial metrics (P/E, RSI, Sharpe ratio)
        - Be precise and data-driven
        - Format: numbers, percentages, ratios first, then interpretation""",

    PersonalityMode.COACH: """You are AVA in COACH mode.
        - Be energetic and motivational
        - Focus on performance and growth
        - Use sports/victory analogies
        - Emphasize discipline and execution
        - End with actionable next steps""",

    PersonalityMode.GURU: """You are AVA in GURU mode.
        - Be philosophical and contemplative
        - Use market wisdom as life lessons
        - Reference timeless trading principles
        - Emphasize patience and discipline
        - Use metaphors from nature/universe"""
}
```

### 2. Temperature Settings

Optimize temperature per personality:

```python
TEMPERATURE_SETTINGS = {
    PersonalityMode.ANALYST: 0.3,      # Low - need precision
    PersonalityMode.PROFESSIONAL: 0.5,
    PersonalityMode.CONCISE: 0.4,
    PersonalityMode.FRIENDLY: 0.7,     # Medium - natural conversation
    PersonalityMode.MENTOR: 0.6,
    PersonalityMode.COACH: 0.8,        # High - varied motivation
    PersonalityMode.WITTY: 0.9,        # High - creative humor
    PersonalityMode.REBEL: 0.8,
    PersonalityMode.CHARMING: 0.9,
    PersonalityMode.GURU: 0.9          # High - philosophical creativity
}
```

### 3. Cost Optimization

Route expensive models only when necessary:

```python
# Use free models for simple queries
if len(user_message.split()) < 10 and not requires_analysis(user_message):
    llm = local_llm  # Free, fast
else:
    llm = premium_llm  # Paid, accurate
```

### 4. Fallback Chain

Always have fallbacks:

```python
LLM_FALLBACK_CHAIN = [
    ChatGroq(model="llama-3.3-70b-versatile"),  # Free, fast (try first)
    ChatOpenAI(model="gpt-4o-mini"),            # Paid, reliable
    LocalLLM(model="qwen-2.5-7b"),              # Free, local
    ChatGoogleGenerativeAI(model="gemini-flash")  # Free, fast
]

def get_llm_with_fallback():
    for llm in LLM_FALLBACK_CHAIN:
        try:
            llm.invoke("test")
            return llm
        except:
            continue
    raise Exception("All LLMs failed!")
```

### 5. Response Post-Processing

Add personality finishing touches:

```python
def apply_personality_styling(response, personality, emotional_state):
    """Add personality-specific formatting"""

    if personality == PersonalityMode.ANALYST:
        # Add data formatting
        response = add_data_boxes(response)
        response = highlight_metrics(response)

    elif personality == PersonalityMode.COACH:
        # Add motivational elements
        response += "\n\n💪 You've got this! Now go execute!"

    elif personality == PersonalityMode.GURU:
        # Add philosophical quote
        response += "\n\n🙏 _Remember: The market rewards the patient._"

    return response
```

---

## Testing Custom Integrations

```python
# test_custom_llm_personality.py

def test_analyst_personality():
    """Test ANALYST personality with custom LLM"""

    ava = AVACore()
    ava.personality.set_mode(PersonalityMode.ANALYST)

    response = ava.process_message("Analyze TSLA")

    # Verify analytical characteristics
    assert "📊" in response  # Data icon
    assert any(metric in response for metric in ['P/E', 'RSI', 'EMA'])
    assert response.count('%') >= 2  # Multiple percentages
    assert len(response.split('\n')) >= 5  # Multi-line analysis


def test_coach_personality():
    """Test COACH personality with custom LLM"""

    ava = AVACore()
    ava.personality.set_mode(PersonalityMode.COACH)

    response = ava.process_message("Should I take profits?")

    # Verify motivational characteristics
    assert any(word in response.upper() for word in ['WIN', 'CHAMPION', 'GO'])
    assert '!' in response  # Exclamation points
    assert '💪' in response or '🏆' in response  # Motivational emojis
```

---

## Conclusion

AVA's architecture supports unlimited LLM customization:

- **Easy:** Add new LLM providers in minutes
- **Advanced:** Fine-tune models for specific personalities
- **Scalable:** Route different queries to optimal models
- **Cost-Effective:** Mix free and paid models intelligently

**Next Steps:**
1. Choose which personalities need custom models
2. Gather training data for fine-tuning
3. Set up LLM routing logic
4. Test and iterate on personality consistency

For questions or advanced integration support, consult the AVA development team.
