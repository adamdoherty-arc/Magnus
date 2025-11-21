# Prediction Markets AI - Implementation Quick Reference Guide

**Purpose:** Fast-access guide for implementing prediction market systems
**Updated:** November 9, 2025

---

## Quick Model Selection Matrix

| Sector | Best Model | Secondary | Ensemble Type | Features Count |
|--------|-----------|-----------|---|---|
| **Sports** | XGBoost + LightGBM | Random Forest | Stacking | 20-40 |
| **Politics** | Logistic Regression (polling) + Market Prices | Time-series | Voting | 15-25 |
| **Economics** | LightGBM (sentiment) + ARIMA | Elastic Net | Blending | 50-100 |
| **Crypto** | LSTM + GRU | XGBoost+sentiment | Stacking | 30-50 |

---

## 1-Hour Quick Start Implementation

### Step 1: Install Dependencies (5 min)
```bash
pip install xgboost lightgbm scikit-learn pandas numpy tensorflow transformers
```

### Step 2: Data Preparation (15 min)
```python
import pandas as pd
import numpy as np
from sklearn.preprocessing import MinMaxScaler

# Load data
df = pd.read_csv('market_data.csv')

# Scale features
scaler = MinMaxScaler()
features_scaled = scaler.fit_transform(df[['price', 'volume', 'sentiment']])

# Train/test split
train_size = int(len(features_scaled) * 0.8)
X_train = features_scaled[:train_size]
y_train = df['outcome'][:train_size]
X_test = features_scaled[train_size:]
y_test = df['outcome'][train_size:]
```

### Step 3: Quick Ensemble (20 min)
```python
from sklearn.ensemble import VotingClassifier, RandomForestClassifier
from xgboost import XGBClassifier
from lightgbm import LGBMClassifier

models = [
    ('xgb', XGBClassifier(n_estimators=100)),
    ('lgb', LGBMClassifier(n_estimators=100)),
    ('rf', RandomForestClassifier(n_estimators=100))
]

ensemble = VotingClassifier(estimators=models, voting='soft')
ensemble.fit(X_train, y_train)

# Get probabilities for Kelly sizing
probs = ensemble.predict_proba(X_test)[:, 1]
```

### Step 4: Position Sizing (10 min)
```python
def kelly_sizing(prob_true, odds, bankroll, fraction=0.25):
    q = 1 - prob_true
    f = (prob_true * odds - q) / odds
    position = max(0, f * fraction * bankroll)
    return min(position, bankroll * 0.05)  # Cap at 5%

positions = [kelly_sizing(p, 1.9, 10000) for p in probs]
```

### Step 5: Evaluate & Deploy (10 min)
```python
from sklearn.metrics import brier_score_loss

predictions = ensemble.predict_proba(X_test)[:, 1]
brier = brier_score_loss(y_test, predictions)
roi = (np.sum(predictions[y_test==1] * 1.9) - np.sum(1-predictions[y_test==0])) / sum(positions)

print(f"Brier Score: {brier:.4f}")
print(f"Estimated ROI: {roi:.2%}")
```

---

## Feature Engineering Templates

### Sports Features
```python
def engineer_sports_features(team_data):
    features = pd.DataFrame()

    # Rolling averages (momentum)
    features['wins_l10'] = team_data['wins'].rolling(10).mean()
    features['ppg_l10'] = team_data['points'].rolling(10).mean()
    features['differential_l10'] = team_data['point_diff'].rolling(10).mean()

    # Efficiency metrics
    features['offensive_eff'] = team_data['points'] / team_data['possessions']
    features['defensive_eff'] = team_data['points_allowed'] / team_data['possessions']

    # Context
    features['home_indicator'] = team_data['is_home'].astype(int)
    features['rest_days'] = team_data['days_rest']

    # Trend
    features['momentum'] = features['wins_l10'] / features['wins_l20']

    return features

# Usage
sports_features = engineer_sports_features(team_stats_df)
```

### Political Features
```python
def engineer_election_features(polling_data, economic_data, market_data):
    features = pd.DataFrame()

    # Polling
    features['polling_avg'] = polling_data['aggregate_poll']
    features['polling_trend'] = polling_data['polling'].rolling(7).mean()
    features['polling_std'] = polling_data['polling'].rolling(30).std()

    # Economic
    features['gdp_growth'] = economic_data['gdp_change']
    features['unemployment'] = economic_data['unemployment_rate']
    features['consumer_confidence'] = economic_data['confidence_index']

    # Market
    features['market_probability'] = market_data['implied_prob']
    features['market_volume'] = market_data['trading_volume']
    features['spread_width'] = market_data['ask'] - market_data['bid']

    # Time decay
    days_to_election = (pd.Timestamp('2024-11-05') - features.index).days
    features['time_decay'] = 1 / (1 + np.exp(-days_to_election/30))

    return features
```

### Crypto Features
```python
def engineer_crypto_features(ohlcv_data, sentiment_data):
    features = pd.DataFrame()

    # Technical indicators
    features['rsi'] = calculate_rsi(ohlcv_data['close'])
    features['macd'] = calculate_macd(ohlcv_data['close'])
    features['bollinger_bands'] = calculate_bollinger(ohlcv_data['close'])

    # Momentum
    features['returns_5d'] = ohlcv_data['close'].pct_change(5)
    features['volatility_20d'] = ohlcv_data['close'].rolling(20).std()

    # Volume
    features['volume_ma'] = ohlcv_data['volume'].rolling(20).mean()
    features['volume_ratio'] = ohlcv_data['volume'] / features['volume_ma']

    # Sentiment
    features['sentiment_score'] = sentiment_data['aggregated_sentiment']
    features['sentiment_momentum'] = features['sentiment_score'].rolling(7).mean()

    # Macro (if available)
    features['btc_dominance'] = market_data['btc_dom']
    features['total_market_cap'] = market_data['total_cap']

    return features
```

---

## Model Training Pipeline

```python
from sklearn.model_selection import cross_val_score
from sklearn.metrics import brier_score_loss, log_loss

class PredictionModel:
    def __init__(self):
        self.models = {}
        self.meta_model = None
        self.temperature = 1.0

    def train_base_models(self, X, y):
        """Train individual base learners"""
        self.models['xgb'] = XGBClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            subsample=0.8,
            colsample_bytree=0.8
        ).fit(X, y)

        self.models['lgb'] = LGBMClassifier(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=6,
            num_leaves=31
        ).fit(X, y)

        self.models['rf'] = RandomForestClassifier(
            n_estimators=200,
            max_depth=15,
            min_samples_split=5
        ).fit(X, y)

    def generate_meta_features(self, X):
        """Generate meta-features from base models"""
        meta_X = np.column_stack([
            self.models['xgb'].predict_proba(X)[:, 1],
            self.models['lgb'].predict_proba(X)[:, 1],
            self.models['rf'].predict_proba(X)[:, 1],
        ])
        return meta_X

    def train_meta_model(self, X_meta, y):
        """Train stacking meta-learner"""
        self.meta_model = LogisticRegression(max_iter=1000)
        self.meta_model.fit(X_meta, y)

    def calibrate_temperature(self, X_val, y_val):
        """Find optimal temperature scaling"""
        meta_features = self.generate_meta_features(X_val)
        logits = self.meta_model.predict_proba(meta_features)[:, 1]

        def nll_loss(T):
            scaled = logits / T
            return -np.mean(y_val * np.log(scaled) +
                          (1-y_val) * np.log(1-scaled))

        result = minimize(nll_loss, 1.0, bounds=[(0.1, 5.0)])
        self.temperature = result.x[0]

    def predict_proba(self, X):
        """Generate calibrated probabilities"""
        meta_features = self.generate_meta_features(X)
        probs = self.meta_model.predict_proba(meta_features)[:, 1]

        # Apply temperature scaling
        scaled = probs / self.temperature
        return np.clip(scaled, 0, 1)

    def evaluate(self, X_test, y_test):
        """Comprehensive evaluation metrics"""
        probs = self.predict_proba(X_test)

        metrics = {
            'brier_score': brier_score_loss(y_test, probs),
            'log_loss': log_loss(y_test, probs),
            'accuracy': np.mean((probs > 0.5) == y_test),
            'auc': roc_auc_score(y_test, probs),
            'calibration_error': np.mean(np.abs(probs - y_test))
        }
        return metrics

# Usage
model = PredictionModel()
model.train_base_models(X_train, y_train)
meta_X_val = model.generate_meta_features(X_val)
model.train_meta_model(meta_X_val, y_val)
model.calibrate_temperature(X_val, y_val)

metrics = model.evaluate(X_test, y_test)
print(f"Brier Score: {metrics['brier_score']:.4f}")
print(f"Log Loss: {metrics['log_loss']:.4f}")
```

---

## Sentiment Analysis Quick Setup

```python
from transformers import pipeline
import pandas as pd

class SentimentAnalyzer:
    def __init__(self):
        # Use lighter models for speed
        self.roberta = pipeline("sentiment-analysis",
            model="cardiffnlp/twitter-roberta-base-sentiment")
        self.finbert = pipeline("sentiment-analysis",
            model="ProsusAI/finbert")

    def analyze_text(self, text, model='roberta'):
        """Single text sentiment"""
        if model == 'roberta':
            result = self.roberta(text[:512])
        else:
            result = self.finbert(text[:512])

        # Convert to -1 to 1 scale
        score = result[0]['score']
        label = result[0]['label']
        return (score - 0.5) * 2 if label == 'POSITIVE' else -(score - 0.5) * 2

    def aggregate_sentiments(self, texts, method='weighted'):
        """Aggregate multiple texts"""
        scores = [self.analyze_text(t) for t in texts]

        if method == 'weighted':
            # Weight recent articles higher
            weights = np.exp(np.linspace(-1, 0, len(scores)))
            weights /= weights.sum()
            return np.sum(np.array(scores) * weights)
        else:
            return np.mean(scores)

    def sentiment_to_feature(self, sentiment_score):
        """Convert sentiment to model feature"""
        # Map -1 to 1 to 0 to 1
        return (sentiment_score + 1) / 2

# Usage
analyzer = SentimentAnalyzer()
article_texts = ['crypto market explodes', 'bearish sentiment spreads']
sentiment = analyzer.aggregate_sentiments(article_texts)
sentiment_feature = analyzer.sentiment_to_feature(sentiment)
```

---

## Kelly Criterion Risk Management

```python
class RiskManager:
    def __init__(self, bankroll, kelly_fraction=0.25, max_position_pct=0.05):
        self.bankroll = bankroll
        self.kelly_fraction = kelly_fraction
        self.max_position_pct = max_position_pct
        self.positions = []

    def calculate_position_size(self, true_prob, market_odds):
        """Kelly Criterion with constraints"""
        q = 1 - true_prob
        kelly_f = (true_prob * market_odds - q) / market_odds

        # Apply fraction to reduce volatility
        position_fraction = kelly_f * self.kelly_fraction

        # Enforce constraints
        max_position = self.bankroll * self.max_position_pct
        position_size = max(0, min(position_fraction * self.bankroll, max_position))

        return position_size

    def calculate_ev(self, true_prob, market_odds, position_size):
        """Expected Value calculation"""
        win_payout = position_size * market_odds
        loss_amount = position_size

        expected_value = (true_prob * win_payout) - ((1 - true_prob) * loss_amount)
        roi = expected_value / position_size if position_size > 0 else 0

        return {'ev': expected_value, 'roi': roi, 'win_payout': win_payout}

    def should_trade(self, ev, min_ev=1.0):
        """Trading decision logic"""
        return ev > min_ev  # Only trade if EV > 1 dollar

    def track_position(self, market_id, position_size, probability, odds):
        """Record position for monitoring"""
        self.positions.append({
            'market_id': market_id,
            'position_size': position_size,
            'probability': probability,
            'odds': odds,
            'timestamp': pd.Timestamp.now(),
            'bankroll': self.bankroll
        })

    def portfolio_correlation(self, positions_df):
        """Monitor portfolio correlation risk"""
        # Prevent overconcentration
        correlation = positions_df.groupby('market_type').size()
        return correlation[correlation > 5].empty  # Flag if >5 in one type

# Usage
risk_mgr = RiskManager(bankroll=10000, kelly_fraction=0.25)

for market in markets:
    true_prob = model.predict_proba([market.features])[0]
    market_odds = market.current_odds

    position_size = risk_mgr.calculate_position_size(true_prob, market_odds)
    ev_metrics = risk_mgr.calculate_ev(true_prob, market_odds, position_size)

    if risk_mgr.should_trade(ev_metrics['ev'], min_ev=0.50):
        execute_trade(market, position_size)
        risk_mgr.track_position(market.id, position_size, true_prob, market_odds)
```

---

## Performance Monitoring Dashboard

```python
class PerformanceMonitor:
    def __init__(self):
        self.trade_log = []
        self.metrics_history = []

    def log_trade(self, market_id, prediction, odds, result, position_size):
        """Record individual trade"""
        pnl = position_size * (odds - 1) if result == 1 else -position_size

        self.trade_log.append({
            'market_id': market_id,
            'prediction': prediction,
            'odds': odds,
            'result': result,
            'position_size': position_size,
            'pnl': pnl,
            'roi': pnl / position_size if position_size > 0 else 0,
            'timestamp': pd.Timestamp.now()
        })

    def calculate_metrics(self):
        """Calculate comprehensive performance metrics"""
        trades_df = pd.DataFrame(self.trade_log)

        if len(trades_df) == 0:
            return None

        metrics = {
            'total_trades': len(trades_df),
            'win_rate': (trades_df['result'] == 1).mean(),
            'total_pnl': trades_df['pnl'].sum(),
            'avg_roi': trades_df['roi'].mean(),
            'sharpe_ratio': trades_df['roi'].mean() / trades_df['roi'].std() * np.sqrt(252),
            'max_drawdown': self.calculate_max_drawdown(trades_df),
            'profit_factor': trades_df[trades_df['pnl'] > 0]['pnl'].sum() /
                           abs(trades_df[trades_df['pnl'] < 0]['pnl'].sum()),
            'brier_score': brier_score_loss(trades_df['result'], trades_df['prediction'])
        }

        return metrics

    def calculate_max_drawdown(self, trades_df):
        """Calculate maximum peak-to-trough decline"""
        cumsum = trades_df['pnl'].cumsum()
        running_max = cumsum.expanding().max()
        drawdown = (cumsum - running_max) / running_max
        return drawdown.min()

    def print_performance_report(self):
        """Print formatted performance report"""
        metrics = self.calculate_metrics()

        print("=" * 50)
        print("PERFORMANCE REPORT")
        print("=" * 50)
        print(f"Total Trades: {metrics['total_trades']}")
        print(f"Win Rate: {metrics['win_rate']:.2%}")
        print(f"Total P&L: ${metrics['total_pnl']:.2f}")
        print(f"Average ROI: {metrics['avg_roi']:.2%}")
        print(f"Sharpe Ratio: {metrics['sharpe_ratio']:.2f}")
        print(f"Max Drawdown: {metrics['max_drawdown']:.2%}")
        print(f"Profit Factor: {metrics['profit_factor']:.2f}")
        print(f"Brier Score: {metrics['brier_score']:.4f}")
        print("=" * 50)

# Usage
monitor = PerformanceMonitor()

for market in live_markets:
    pred_prob = model.predict_proba(market.features)
    position = risk_mgr.calculate_position_size(pred_prob, market.odds)

    # ... execute trade ...

    # After market resolution
    monitor.log_trade(market.id, pred_prob, market.odds, market.result, position)

monitor.print_performance_report()
```

---

## Multi-Agent System Minimal Implementation

```python
class MultiAgentSystem:
    def __init__(self, models_dict):
        self.forecaster_model = models_dict['forecaster']
        self.critic_model = models_dict['critic']  # Optional

    def generate_forecast(self, market_data):
        """Agent 1: Generate forecast"""
        features = self.extract_features(market_data)
        base_probability = self.forecaster_model.predict_proba(features)[0]

        return {
            'probability': base_probability,
            'confidence': self.estimate_confidence(base_probability),
            'reasoning': 'Based on ensemble prediction'
        }

    def critique_forecast(self, forecast, market_data):
        """Agent 2: Validate forecast (optional)"""
        # Simple checks
        if forecast['probability'] < 0.05 or forecast['probability'] > 0.95:
            adjustment = 0.9  # Reduce extreme confidences
        else:
            adjustment = 1.0

        return {
            'confidence_adjustment': adjustment,
            'concerns': []
        }

    def make_trade_decision(self, forecast, critique, bankroll, market_odds):
        """Agent 3: Decide trading action"""
        adjusted_prob = forecast['probability'] * critique['confidence_adjustment']
        position = kelly_sizing(adjusted_prob, market_odds, bankroll)

        return {
            'position_size': position,
            'expected_value': position * (adjusted_prob * market_odds - (1 - adjusted_prob)),
            'action': 'BUY' if position > 1 else 'PASS'
        }

    def process_market(self, market_data, bankroll, market_odds):
        """Full market processing pipeline"""
        forecast = self.generate_forecast(market_data)
        critique = self.critique_forecast(forecast, market_data)
        decision = self.make_trade_decision(forecast, critique, bankroll, market_odds)

        return {
            'forecast': forecast,
            'critique': critique,
            'decision': decision,
            'final_probability': forecast['probability'] * critique['confidence_adjustment']
        }

# Usage
system = MultiAgentSystem({
    'forecaster': ensemble_model,
    'critic': None  # Optional validation layer
})

result = system.process_market(market_data, bankroll=10000, market_odds=1.9)
print(f"Position Size: ${result['decision']['position_size']:.2f}")
print(f"Expected Value: ${result['decision']['expected_value']:.2f}")
print(f"Action: {result['decision']['action']}")
```

---

## Deployment Checklist

### Pre-Deployment (Week 1)
- [ ] Data pipeline tested on 6+ months historical data
- [ ] Model backtested with 52-week out-of-sample validation
- [ ] Brier score < 0.20 (or better than 52.4% accuracy on spreads)
- [ ] Kelly Criterion sizing implemented and validated
- [ ] Risk limits configured (5% max position, 15% daily loss)
- [ ] Temperature scaling calibrated on validation set

### Go-Live (Week 2)
- [ ] Start with Manifold Markets (play money)
- [ ] Paper trade for 2 weeks minimum
- [ ] Monitor Sharpe ratio, win rate, Brier score daily
- [ ] Adjust Kelly fraction down if max drawdown > 25%
- [ ] Weekly model retraining on fresh data

### Scaling (Week 3-4)
- [ ] Move to Metaculus with small position sizes
- [ ] Gradual increase to Polymarket/Kalshi
- [ ] Monitor correlation of predictions across markets
- [ ] Implement automated retraining pipeline
- [ ] Add new features monthly based on performance

---

## Critical Success Metrics

| Metric | Target | Threshold |
|--------|--------|-----------|
| **Brier Score** | < 0.18 | Calibration is critical |
| **Win Rate** | 52-56% | 52.4% needed to break even |
| **Sharpe Ratio** | > 1.0 | Consistency matters |
| **Max Drawdown** | < 25% | Kelly Criterion helps |
| **Profit Factor** | > 1.2 | Reward/risk balance |
| **ROI Annual** | 10-30% | Realistic long-term target |

---

## Common Integration Points

**Kalshi API:**
```python
from kalshi import KalshiClient

client = KalshiClient(api_key='your_key')
markets = client.get_markets()
for market in markets:
    if should_trade(market):
        client.create_order(market.id, 'BUY', position_size, market.current_price)
```

**Manifold Markets API:**
```python
import requests

def get_manifold_markets():
    r = requests.get('https://api.manifold.markets/v0/markets')
    return r.json()

def get_market_probability(contract_id):
    r = requests.get(f'https://api.manifold.markets/v0/contract/{contract_id}')
    return r.json()['probability']
```

**Data Sources:**
```python
# Sports
import requests
scores_api = requests.get('https://api.thesportsdb.com/api/v1/...')

# Crypto
import yfinance
btc = yfinance.download('BTC-USD', start='2024-01-01')

# News Sentiment
from newsapi import NewsApiClient
newsapi = NewsApiClient(api_key='your_key')
articles = newsapi.get_everything(q='bitcoin')
```

---

**Last Updated:** November 9, 2025
**Recommended Review Frequency:** Weekly during live trading
