# Enhanced Game Cards - Design Specification

## Overview
Modular, data-rich game cards with DeepSeek AI integration and comprehensive team statistics.

## Card Structure (Clean & Modular)

```
┌─────────────────────────────────────────────────────────┐
│ ⚡ LIVE • 4th Quarter 5:23        [Subscribe] Button   │
├─────────────────────────────────────────────────────────┤
│                                                           │
│  🏈 Away Team Logo    SCORE       @      Home Team Logo   │
│     Team Name          21                    Team Name     │
│     Record: 8-2        Win %                 Record: 6-4   │
│     ↑ Streak: W3       70%                   ↓ Streak: L2  │
│                                                           │
├─────────────────────────────────────────────────────────┤
│  📊 TEAM STATISTICS                                       │
│  ┌──────────────────────────────────────────────┐        │
│  │ Away Team    │  Category     │  Home Team   │        │
│  │   350        │  Total Yards  │     280      │        │
│  │   24.5       │  PPG Average  │     21.3     │        │
│  │   18.2       │  PA Average   │     23.5     │        │
│  │   +6.3       │  Point Diff   │     -2.2     │        │
│  └──────────────────────────────────────────────┘        │
├─────────────────────────────────────────────────────────┤
│  🤖 AI PREDICTIONS                                        │
│  ┌─────────────────┬─────────────────┐                   │
│  │ Local Model     │  DeepSeek R1     │                   │
│  │ Predicted: Away │  Predicted: Away │                   │
│  │ Win Prob: 65%   │  Win Prob: 68%   │                   │
│  │ Spread: -3.5    │  Spread: -4.0    │                   │
│  │ 🟢 HIGH CONF     │  🟢 HIGH CONF     │                   │
│  └─────────────────┴─────────────────┘                   │
│                                                           │
│  💡 DeepSeek Insight: "Away team has dominated          │
│     recent meetings with superior rushing attack..."      │
├─────────────────────────────────────────────────────────┤
│  💰 BETTING ODDS & VALUE                                  │
│  │ Kalshi: Away 56¢ | Home 44¢                          │
│  │ Expected Value: +12.5% 🟢                             │
│  │ Recommendation: BET AWAY                              │
├─────────────────────────────────────────────────────────┤
│  📈 [View Detailed Stats] [Historical Matchups]          │
└─────────────────────────────────────────────────────────┘
```

## Data Fields

### 1. Header Section
- Live status indicator
- Game clock / scheduled time
- Subscribe/Unsubscribe button

### 2. Matchup Section
- Team logos with glow for predicted winner
- Current score
- **NEW**: Team records (W-L)
- **NEW**: Current streak (W3, L2, etc.)
- **NEW**: Win probability %

### 3. Team Statistics (NEW - Expandable)
- Total yards (current game or season average)
- Points per game average
- Points against average
- Point differential
- Offensive efficiency rating
- Defensive efficiency rating

### 4. AI Predictions Section (ENHANCED)
- **Side-by-side comparison**:
  - Local Model (NFL/NCAA Predictor)
  - DeepSeek R1 Analysis
- Predicted winner
- Win probability %
- Predicted spread
- Confidence level with emoji
- **NEW**: DeepSeek detailed insight (1-2 sentences)

### 5. Betting Section
- Kalshi odds (if available)
- Expected value calculation
- Recommendation (BET/HOLD/PASS)
- Position tracking (if user has bet)

### 6. Expandable Details
- Historical head-to-head record
- Last 5 meetings
- Key player stats (if available)
- Weather/venue information

## Color Scheme

### Confidence Levels
- 🟢 **High** (>70%): Green glow `#00ff00`
- 🟡 **Medium** (55-69%): Gold glow `#ffd700`
- ⚪ **Low** (<55%): No glow

### Card States
- **Live**: Red pulsing indicator
- **Upcoming**: Blue accent
- **Final**: Gray overlay

## Modular Components

### Component 1: Header Bar
```python
def render_header(status, is_live, is_watched):
    # Returns: Status indicator + Subscribe button
```

### Component 2: Team Display
```python
def render_team(team_name, logo, score, record, streak, win_prob):
    # Returns: Logo + Name + Stats in clean layout
```

### Component 3: Stats Table
```python
def render_stats_comparison(away_stats, home_stats):
    # Returns: Side-by-side stats comparison
```

### Component 4: AI Predictions
```python
def render_ai_predictions(local_prediction, deepseek_prediction):
    # Returns: Dual prediction display with insights
```

### Component 5: Betting Info
```python
def render_betting_info(kalshi_odds, expected_value, recommendation):
    # Returns: Odds + EV + Recommendation
```

## CSS Improvements

### Cleaner Borders
```css
.game-card {
    border: 2px solid rgba(128, 128, 128, 0.3);
    border-radius: 12px;
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
}

.game-card:hover {
    box-shadow: 0 8px 20px rgba(0, 0, 0, 0.15);
    transform: translateY(-2px);
}
```

### Section Dividers
```css
.card-section {
    border-top: 1px solid rgba(128, 128, 128, 0.2);
    padding: 12px 0;
}
```

### Stats Table
```css
.stats-table {
    display: grid;
    grid-template-columns: 1fr 2fr 1fr;
    gap: 8px;
    text-align: center;
}
```

## DeepSeek Integration

### API Call
```python
def get_deepseek_game_analysis(away_team, home_team, game_context):
    prompt = f"""
    Analyze this NFL/NCAA game matchup:
    Away: {away_team} ({away_record})
    Home: {home_team} ({home_record})
    
    Provide:
    1. Predicted winner
    2. Win probability (%)
    3. Predicted spread
    4. Key insight (1-2 sentences)
    
    Return as JSON.
    """
    
    llm_service = LLMService()
    result = llm_service.generate(
        prompt=prompt,
        provider="deepseek",
        model="deepseek-chat",
        temperature=0.3
    )
    
    return parse_json(result['text'])
```

## Performance Optimizations

1. **Lazy Loading**: Load DeepSeek predictions only when card is visible
2. **Caching**: Cache predictions for 5 minutes
3. **Batch Requests**: Request DeepSeek for multiple games at once
4. **Fallback**: Show local prediction immediately, DeepSeek when ready

## Implementation Priority

1. ✅ Basic layout restructure
2. ✅ Add team records and streaks
3. ✅ Add DeepSeek API integration
4. ✅ Side-by-side AI comparison
5. ✅ Expandable stats section
6. ✅ Clean CSS styling
7. ✅ Performance optimizations

