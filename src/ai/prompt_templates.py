"""
Prompt Templates for Kalshi Market Analysis
Structured prompts for different AI models
"""

from typing import Dict, Optional, List
from datetime import datetime


def build_market_analysis_prompt(market: Dict, context: Optional[Dict] = None) -> str:
    """
    Build comprehensive market analysis prompt

    Args:
        market: Market data dictionary
        context: Optional context (weather, injuries, stats, etc.)

    Returns:
        Formatted prompt string
    """

    # Extract market data
    ticker = market.get('ticker', 'N/A')
    title = market.get('title', 'N/A')
    yes_price = market.get('yes_price', 0.5)
    no_price = market.get('no_price', 0.5)
    volume = market.get('volume', 0)
    open_interest = market.get('open_interest', 0)
    close_time = market.get('close_time', 'N/A')

    # Build context section
    context_text = build_context_summary(context) if context else "No additional context provided."

    # Implied probability
    implied_prob_yes = yes_price * 100
    implied_prob_no = no_price * 100

    prompt = f"""You are an expert NFL prediction analyst evaluating a Kalshi betting market.

=== MARKET INFORMATION ===
Ticker: {ticker}
Question: {title}

Current Pricing:
- YES: ${yes_price:.2f} (Implied Probability: {implied_prob_yes:.1f}%)
- NO: ${no_price:.2f} (Implied Probability: {implied_prob_no:.1f}%)

Market Activity:
- Trading Volume: ${volume:,.0f}
- Open Interest: {open_interest:,} contracts
- Closing Time: {close_time}

=== CONTEXTUAL DATA ===
{context_text}

=== ANALYSIS FRAMEWORK ===

Please analyze this market using the following framework:

1. VALUE ASSESSMENT
   - What is the market asking? Clarify the specific outcome.
   - What is the implied probability from the YES price?
   - Based on available data, what should the TRUE probability be?
   - Calculate Expected Value (EV): (True Prob - Market Prob) / Market Prob
   - Is there a pricing inefficiency we can exploit?

2. TEAM/PLAYER ANALYSIS
   - Recent performance trends (last 3-5 games)
   - Head-to-head history (if applicable)
   - Home/away performance splits
   - Key player status and impact
   - Offensive/defensive matchup dynamics

3. SITUATIONAL FACTORS
   - Weather impact (for outdoor games)
   - Days of rest / travel distance
   - Playoff implications / motivation
   - Public betting bias (is this a trap line?)
   - Coaching matchup and game planning

4. MARKET DYNAMICS
   - Is the volume high enough for liquidity?
   - Has the line moved significantly? Why?
   - Are sharp bettors or public driving the price?
   - Time until close (optimal entry window?)

5. RISK ASSESSMENT
   - What could go wrong with this prediction?
   - Key uncertainties (weather, injuries, volatility)
   - Downside scenarios to consider
   - Overall risk level (low/medium/high)

=== OUTPUT FORMAT ===

Respond with ONLY valid JSON in this exact format:

{{
  "predicted_outcome": "yes" or "no",
  "confidence": 0-100,
  "edge_percentage": -50 to 50,
  "reasoning": "2-3 sentence explanation of your prediction",
  "key_factors": [
    "Most important factor 1",
    "Most important factor 2",
    "Most important factor 3"
  ],
  "risk_level": "low" or "medium" or "high",
  "recommended_action": "strong_buy" or "buy" or "hold" or "pass"
}}

IMPORTANT:
- Be specific and data-driven in your analysis
- Consider both sides of the market
- Explain WHY you predict this outcome
- Identify the key factors driving your decision
- Be honest about uncertainty and risk
- Respond ONLY with the JSON object (no additional text)
"""

    return prompt


def build_context_summary(context: Dict) -> str:
    """
    Build formatted context summary from context dictionary

    Args:
        context: Context data dictionary

    Returns:
        Formatted context string
    """
    sections = []

    # Weather data
    if 'weather' in context and context['weather']:
        weather = context['weather']
        sections.append(f"""Weather Conditions:
- Temperature: {weather.get('temp', 'N/A')}°F
- Wind Speed: {weather.get('wind_speed', 'N/A')} mph
- Conditions: {weather.get('conditions', 'N/A')}
- Precipitation Probability: {weather.get('precip_prob', 'N/A')}%""")

    # Injury data
    if 'injuries' in context and context['injuries']:
        injuries = context['injuries']
        injury_lines = ["Injury Report:"]

        for team, team_injuries in injuries.items():
            if team_injuries:
                injury_lines.append(f"  {team.title()}:")
                for injury in team_injuries:
                    injury_lines.append(f"    - {injury}")
            else:
                injury_lines.append(f"  {team.title()}: No significant injuries")

        sections.append('\n'.join(injury_lines))

    # Team stats
    if 'team_stats' in context and context['team_stats']:
        stats = context['team_stats']
        sections.append(f"""Team Statistics:
Home Team:
- Win Rate: {stats.get('home_win_pct', 'N/A')}%
- Points Per Game: {stats.get('home_ppg', 'N/A')}
- Points Allowed: {stats.get('home_papg', 'N/A')}

Away Team:
- Win Rate: {stats.get('away_win_pct', 'N/A')}%
- Points Per Game: {stats.get('away_ppg', 'N/A')}
- Points Allowed: {stats.get('away_papg', 'N/A')}""")

    # Recent performance
    if 'recent_form' in context and context['recent_form']:
        form = context['recent_form']
        sections.append(f"""Recent Form (Last 5 Games):
- Home Team: {form.get('home_last5', 'N/A')}
- Away Team: {form.get('away_last5', 'N/A')}""")

    # Head-to-head
    if 'head_to_head' in context and context['head_to_head']:
        h2h = context['head_to_head']
        sections.append(f"""Head-to-Head History:
- Games Played: {h2h.get('total_games', 'N/A')}
- Home Team Wins: {h2h.get('home_wins', 'N/A')}
- Average Point Differential: {h2h.get('avg_point_diff', 'N/A')}""")

    # Social sentiment
    if 'sentiment' in context and context['sentiment']:
        sentiment = context['sentiment']
        sections.append(f"""Social Media Sentiment:
- Twitter: {sentiment.get('twitter_score', 'N/A')}/100
- Reddit: {sentiment.get('reddit_score', 'N/A')}/100
- Public Betting: {sentiment.get('public_pct', 'N/A')}% on YES""")

    # Line movement
    if 'line_movement' in context and context['line_movement']:
        movement = context['line_movement']
        sections.append(f"""Line Movement Analysis:
- Movement Type: {movement.get('type', 'N/A')}
- Price Velocity: {movement.get('velocity', 'N/A')}
- Steam Moves Detected: {movement.get('steam_count', 0)}""")

    # Additional notes
    if 'notes' in context and context['notes']:
        sections.append(f"Additional Context:\n{context['notes']}")

    return '\n\n'.join(sections) if sections else "No additional context available."


def build_live_game_update_prompt(
    market: Dict,
    game_state: Dict,
    original_prediction: Optional[Dict] = None
) -> str:
    """
    Build prompt for live game analysis

    Args:
        market: Market data
        game_state: Current game state
        original_prediction: Original pre-game prediction (optional)

    Returns:
        Formatted prompt
    """

    title = market.get('title', 'N/A')
    current_price = market.get('yes_price', 0.5)

    quarter = game_state.get('quarter', 'N/A')
    time_remaining = game_state.get('time_remaining', 'N/A')
    score = game_state.get('score', 'N/A')
    possession = game_state.get('possession', 'N/A')
    recent_plays = game_state.get('recent_plays', [])

    plays_text = '\n'.join(f"  - {play}" for play in recent_plays[-5:])

    original_text = ""
    if original_prediction:
        original_text = f"""
Original Pre-Game Prediction:
- Outcome: {original_prediction.get('predicted_outcome', 'N/A')}
- Confidence: {original_prediction.get('confidence', 'N/A')}%
- Reasoning: {original_prediction.get('reasoning', 'N/A')}
"""

    prompt = f"""You are providing LIVE game analysis for a Kalshi betting market.

=== MARKET ===
Question: {title}
Current YES Price: ${current_price:.2f}

=== LIVE GAME SITUATION ===
Quarter: {quarter}
Time Remaining: {time_remaining}
Score: {score}
Possession: {possession}

Recent Plays:
{plays_text}

{original_text}

=== TASK ===
Provide a brief 2-3 sentence update on how the current game situation affects this market.

Consider:
1. Has the probability changed based on game events?
2. Should bettors adjust their positions?
3. Is there now value on YES or NO given the live situation?

Respond in JSON:
{{
  "updated_probability": 0-100,
  "recommendation": "buy_yes", "buy_no", "hold", or "exit",
  "commentary": "2-3 sentence analysis"
}}
"""

    return prompt


def build_sentiment_analysis_prompt(texts: List[str], market_title: str) -> str:
    """
    Build prompt for sentiment analysis

    Args:
        texts: List of social media texts
        market_title: Market title for context

    Returns:
        Formatted prompt
    """

    # Sample up to 20 texts
    sample_texts = texts[:20]
    texts_formatted = '\n'.join(f"{i+1}. {text}" for i, text in enumerate(sample_texts))

    prompt = f"""Analyze sentiment for this Kalshi market from social media posts.

MARKET: {market_title}

SOCIAL MEDIA POSTS ({len(texts)} total, showing {len(sample_texts)}):
{texts_formatted}

Analyze the overall sentiment toward this market outcome.

Respond in JSON:
{{
  "sentiment_score": -100 to 100,
  "bullish_percentage": 0-100,
  "bearish_percentage": 0-100,
  "confidence": 0-100,
  "key_themes": ["theme1", "theme2", "theme3"],
  "summary": "One sentence summary of sentiment"
}}

Where:
- sentiment_score: -100 (very bearish) to +100 (very bullish)
- confidence: How confident in the sentiment reading
"""

    return prompt


def build_chain_of_thought_prompt(market: Dict, context: Optional[Dict] = None) -> str:
    """
    Build Chain-of-Thought reasoning prompt for more detailed analysis

    Args:
        market: Market data
        context: Optional context data

    Returns:
        Formatted CoT prompt
    """

    base_prompt = build_market_analysis_prompt(market, context)

    cot_suffix = """

=== CHAIN-OF-THOUGHT REASONING ===

Before providing your JSON response, think through this step-by-step:

Step 1: UNDERSTAND THE MARKET
- What exactly is being asked?
- What needs to happen for YES to win?
- What are the key variables?

Step 2: ASSESS MARKET PRICING
- What is the current implied probability?
- Does this seem efficient or mispriced?
- Why might the market be wrong?

Step 3: ANALYZE THE FUNDAMENTALS
- What does the data say about true probability?
- What are the strongest factors for YES?
- What are the strongest factors for NO?

Step 4: CALCULATE EXPECTED VALUE
- True Probability vs Market Probability
- Edge = (True Prob - Market Prob) / Market Prob
- Is there positive expected value?

Step 5: ASSESS RISK
- What could invalidate this prediction?
- How confident should we be?
- What's the downside scenario?

Step 6: FINAL DECISION
- Should we bet YES, NO, or PASS?
- How much should we stake?
- What price would be too expensive?

Show your reasoning for each step, then provide your final JSON response.
"""

    return base_prompt + cot_suffix


# ============================================================================
# Testing
# ============================================================================

def test_prompts():
    """Test prompt generation"""

    market = {
        'ticker': 'NFL-KC-BUF-001',
        'title': 'Will the Chiefs beat the Bills by more than 3 points?',
        'yes_price': 0.48,
        'no_price': 0.52,
        'volume': 125000,
        'open_interest': 8500,
        'close_time': '2025-11-10T13:00:00Z'
    }

    context = {
        'weather': {
            'temp': 38,
            'wind_speed': 12,
            'conditions': 'Partly Cloudy',
            'precip_prob': 20
        },
        'injuries': {
            'chiefs': ['Travis Kelce (Questionable - Ankle)'],
            'bills': []
        },
        'team_stats': {
            'home_win_pct': 75.0,
            'home_ppg': 28.5,
            'home_papg': 18.2,
            'away_win_pct': 70.0,
            'away_ppg': 26.8,
            'away_papg': 20.5
        }
    }

    print("="*80)
    print("STANDARD ANALYSIS PROMPT")
    print("="*80)
    prompt = build_market_analysis_prompt(market, context)
    print(prompt)

    print("\n" + "="*80)
    print("CHAIN-OF-THOUGHT PROMPT")
    print("="*80)
    cot_prompt = build_chain_of_thought_prompt(market, context)
    print(cot_prompt[:500] + "...")


if __name__ == "__main__":
    test_prompts()
