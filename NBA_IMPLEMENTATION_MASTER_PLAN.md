# NBA Integration - Master Implementation Plan

## 📋 Project Overview
Build complete NBA sports betting integration with real-time scores, advanced AI predictions, and Kalshi market integration to match/exceed NFL and NCAA functionality.

## 🎯 Goals
1. Real-time NBA game data from multiple sources
2. Advanced ML prediction models
3. Kalshi NBA betting markets with real-time updates
4. Clean, modern game cards with rich statistics
5. Better UX than existing NFL/NCAA cards
6. AI-powered betting recommendations

## 📊 Research Summary

### Data Sources Available
1. **ESPN NBA API** (Primary)
   - URL: `https://site.api.espn.com/apis/site/v2/sports/basketball/nba/scoreboard`
   - Features: Live scores, schedules, team stats, player stats
   - Update Frequency: ~15-30 seconds during games
   - Cost: Free (unofficial API)

2. **NBA Stats API** (nba_api package)
   - Package: `pip install nba_api`
   - Features: Official NBA stats, advanced metrics, player tracking
   - Data: Team stats, player stats, historical data
   - Cost: Free (official API)

3. **Kalshi NBA Markets**
   - Markets: Team winner, player props, season props
   - Real-time pricing: Yes (needs polling every 10-30 seconds)
   - Coverage: Most NBA games

### Modern Prediction Algorithms to Use
1. **Elo Rating System** (proven for sports)
2. **Bradley-Terry Model** (pairwise comparisons)
3. **Neural Networks** (TensorFlow/PyTorch for complex patterns)
4. **XGBoost** (gradient boosting for tabular data)
5. **Ensemble Methods** (combining multiple models)
6. **Player Impact Metrics** (BPM, VORP, Win Shares)

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────┐
│              NBA Game Cards UI                   │
├─────────────────────────────────────────────────┤
│                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐      │
│  │ ESPN     │  │ NBA API  │  │ Kalshi   │      │
│  │ Scores   │  │ Stats    │  │ Markets  │      │
│  └────┬─────┘  └────┬─────┘  └────┬─────┘      │
│       │             │              │             │
│       └─────────────┼──────────────┘             │
│                     │                            │
│           ┌─────────▼─────────┐                 │
│           │ Data Integration  │                 │
│           │     Layer         │                 │
│           └─────────┬─────────┘                 │
│                     │                            │
│           ┌─────────▼─────────┐                 │
│           │ NBA Predictor     │                 │
│           │  (Elo + XGBoost)  │                 │
│           └─────────┬─────────┘                 │
│                     │                            │
│           ┌─────────▼─────────┐                 │
│           │ DeepSeek AI       │                 │
│           │  (Reasoning)      │                 │
│           └─────────┬─────────┘                 │
│                     │                            │
│           ┌─────────▼─────────┐                 │
│           │ Betting           │                 │
│           │ Recommendations   │                 │
│           └───────────────────┘                 │
└─────────────────────────────────────────────────┘
```

## 📝 Detailed Task Breakdown

### Phase 1: Data Integration (Tasks 1-3)
**Priority: Critical**

#### Task 1.1: Create ESPN NBA Live Data Module
- [ ] Create `src/espn_nba_live_data.py`
- [ ] Implement `ESPNNBALiveData` class
- [ ] Parse game data (scores, time, status)
- [ ] Parse team data (records, stats)
- [ ] Parse player data (points, rebounds, assists)
- [ ] Handle live game updates
- [ ] Add error handling and retries
- [ ] Add caching layer (5-minute TTL)

#### Task 1.2: Create NBA Team Database
- [ ] Create `src/nba_team_database.py`
- [ ] Add all 30 NBA teams with logos
- [ ] Team abbreviations and full names
- [ ] Team colors (primary/secondary)
- [ ] Conference and division info
- [ ] Historical performance data
- [ ] Logo fetching from ESPN CDN

#### Task 1.3: Integrate NBA Stats API
- [ ] Install `nba_api` package
- [ ] Create wrapper class for stats
- [ ] Fetch team advanced metrics
- [ ] Fetch player statistics
- [ ] Calculate efficiency ratings
- [ ] Cache data (daily refresh)

### Phase 2: Prediction Engine (Task 4)
**Priority: Critical**

#### Task 2.1: Build NBA Elo System
- [ ] Initialize team Elo ratings (base: 1500)
- [ ] Implement Elo update algorithm
- [ ] Factor in home court advantage (~60 points)
- [ ] Factor in rest days
- [ ] Factor in back-to-back games
- [ ] Factor in travel distance
- [ ] Historical calibration

#### Task 2.2: Build XGBoost Model
- [ ] Collect historical NBA data
- [ ] Feature engineering:
  - Team stats (PPG, FG%, 3P%, rebounds, assists, turnovers)
  - Recent form (last 5-10 games)
  - Head-to-head history
  - Home/away splits
  - Rest days
  - Injuries (if available)
- [ ] Train XGBoost classifier
- [ ] Cross-validation and tuning
- [ ] Save model for inference

#### Task 2.3: Create NBA Predictor Agent
- [ ] Create `src/prediction_agents/nba_predictor.py`
- [ ] Combine Elo + XGBoost predictions
- [ ] Implement ensemble weighting
- [ ] Add confidence scoring
- [ ] Generate explanation text
- [ ] Calculate predicted spreads
- [ ] Add over/under predictions

### Phase 3: Kalshi Integration (Task 5)
**Priority: High**

#### Task 3.1: Map Kalshi NBA Markets
- [ ] Identify NBA market patterns
- [ ] Create team name matching
- [ ] Handle different market types:
  - Team to win game
  - Player props (points, rebounds, assists)
  - Season props
  - Playoff odds
- [ ] Robust error handling

#### Task 3.2: Implement Real-Time Price Updates
- [ ] Create background polling system
- [ ] Poll every 15-30 seconds for live games
- [ ] Poll every 5 minutes for upcoming games
- [ ] WebSocket integration (if available)
- [ ] Event-driven updates to UI
- [ ] Price change notifications
- [ ] Historical price tracking

#### Task 3.3: Create Kalshi Price Monitor
- [ ] Create `src/kalshi_price_monitor.py`
- [ ] Background thread for polling
- [ ] Cache current prices
- [ ] Detect price changes (>2%)
- [ ] Trigger UI updates
- [ ] Log price history

### Phase 4: Game Cards UI (Tasks 6-7)
**Priority: High**

#### Task 4.1: Design NBA Game Card Layout
- [ ] Modern, clean design (better than NFL/NCAA)
- [ ] Card sections:
  - Header: Status, time, subscribe button
  - Matchup: Team logos, scores, records
  - Stats: PPG, FG%, 3P%, rebounds, assists
  - Predictions: Local Model + DeepSeek side-by-side
  - Key Players: Top scorers, assists leaders
  - Betting: Kalshi odds, EV, recommendation
  - Expandable: Detailed stats, injuries, trends
- [ ] Responsive design
- [ ] Smooth animations

#### Task 4.2: Implement NBA-Specific Stats
- [ ] Points per game (PPG)
- [ ] Field goal percentage (FG%)
- [ ] 3-point percentage (3P%)
- [ ] Rebounds per game (RPG)
- [ ] Assists per game (APG)
- [ ] Turnovers per game (TPG)
- [ ] Plus/minus differential
- [ ] Offensive/defensive rating
- [ ] Pace (possessions per game)

#### Task 4.3: Add Player Stats Cards
- [ ] Top 3 players per team
- [ ] Player headshots
- [ ] PPG, RPG, APG
- [ ] Recent performance
- [ ] Injury status

### Phase 5: Betting Intelligence (Task 8)
**Priority: High**

#### Task 5.1: Calculate Expected Value
- [ ] Compare model probability vs Kalshi price
- [ ] Calculate EV percentage
- [ ] Adjust for fees/commissions
- [ ] Risk-adjusted EV

#### Task 5.2: Generate Recommendations
- [ ] BET: EV > 10%, confidence > 70%
- [ ] WATCH: EV > 5%, confidence > 60%
- [ ] PASS: All others
- [ ] Kelly Criterion sizing
- [ ] Bankroll management

#### Task 5.3: Create Betting Dashboard
- [ ] Best bets of the day
- [ ] Live arbitrage opportunities
- [ ] Value tracker
- [ ] Historical performance

### Phase 6: Testing & Optimization (Task 10)
**Priority: Medium**

#### Task 6.1: Model Testing
- [ ] Backtest predictions on historical data
- [ ] Calculate accuracy, ROI, Sharpe ratio
- [ ] Compare to betting lines
- [ ] Tune hyperparameters

#### Task 6.2: Performance Testing
- [ ] Load testing with 30+ games
- [ ] API rate limit testing
- [ ] Cache effectiveness
- [ ] UI responsiveness

#### Task 6.3: User Testing
- [ ] Test on different devices
- [ ] Test with slow connections
- [ ] Test edge cases (no games, API down)
- [ ] Gather feedback

## 🔧 Technical Specifications

### File Structure
```
src/
├── espn_nba_live_data.py           # ESPN NBA API wrapper
├── nba_team_database.py            # Team info and logos
├── nba_stats_integration.py        # NBA Stats API wrapper
├── kalshi_nba_matcher.py           # Match ESPN to Kalshi
├── kalshi_price_monitor.py         # Real-time price tracking
├── prediction_agents/
│   └── nba_predictor.py            # NBA prediction model
├── game_card_components_nba.py     # NBA-specific UI components
└── nba_betting_analyzer.py         # Betting recommendations

game_cards_visual_page.py          # Add NBA tab integration
```

### Dependencies to Add
```bash
pip install nba_api                 # Official NBA stats
pip install xgboost                 # ML predictions
pip install scikit-learn            # ML utilities
pip install pandas                  # Data manipulation
pip install numpy                   # Numerical operations
```

### Database Schema (if needed)
```sql
-- NBA Games
CREATE TABLE nba_games (
    game_id VARCHAR PRIMARY KEY,
    game_date TIMESTAMP,
    home_team VARCHAR,
    away_team VARCHAR,
    home_score INT,
    away_score INT,
    status VARCHAR,
    ...
);

-- NBA Predictions
CREATE TABLE nba_predictions (
    prediction_id SERIAL PRIMARY KEY,
    game_id VARCHAR REFERENCES nba_games,
    predicted_winner VARCHAR,
    win_probability FLOAT,
    confidence VARCHAR,
    ...
);

-- Kalshi NBA Prices
CREATE TABLE kalshi_nba_prices (
    price_id SERIAL PRIMARY KEY,
    market_ticker VARCHAR,
    game_id VARCHAR,
    timestamp TIMESTAMP,
    yes_price FLOAT,
    no_price FLOAT,
    ...
);
```

## 📈 Success Metrics

### Prediction Accuracy
- **Target**: >55% accuracy on game winners
- **Target**: >60% accuracy on high-confidence picks
- **Target**: Positive ROI on recommended bets

### User Experience
- **Load Time**: <2 seconds for game cards
- **Update Frequency**: <30 seconds for live games
- **UI Response**: <100ms for interactions

### Betting Performance
- **EV Accuracy**: Actual EV within ±3% of predicted
- **ROI**: Positive returns over 50+ bet sample
- **Sharp Ratio**: >1.5 for betting recommendations

## 🚀 Implementation Timeline

### Week 1: Foundation
- Day 1-2: Tasks 1.1, 1.2 (ESPN + Team Database)
- Day 3-4: Task 1.3 (NBA Stats API)
- Day 5: Testing and integration

### Week 2: Predictions
- Day 6-7: Task 2.1 (Elo System)
- Day 8-9: Task 2.2 (XGBoost Model)
- Day 10: Task 2.3 (NBA Predictor Agent)

### Week 3: Markets & UI
- Day 11-12: Task 3.1-3.2 (Kalshi Integration)
- Day 13-14: Task 4.1-4.2 (Game Cards)
- Day 15: Task 4.3 (Player Stats)

### Week 4: Polish & Test
- Day 16-17: Task 5.1-5.2 (Betting Intelligence)
- Day 18-19: Task 6.1-6.2 (Testing)
- Day 20: Final polish and launch

## 💰 Expected Costs
- **APIs**: $0 (all free)
- **Computation**: Minimal (local ML models)
- **DeepSeek**: ~$0.01 per day (for insights)
- **Total**: <$5/month

## 🎯 Next Steps
1. Start with ESPN NBA integration
2. Build team database
3. Create basic game cards
4. Add prediction engine
5. Integrate Kalshi markets
6. Polish and optimize

---

**Status**: Ready to implement
**Priority**: High
**Estimated Effort**: 3-4 weeks
**Team**: 1 developer (AI-assisted)

