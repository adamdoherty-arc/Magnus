# Calendar Spreads Feature - Technical Architecture

## Table of Contents
1. [System Overview](#system-overview)
2. [Component Architecture](#component-architecture)
3. [Data Flow](#data-flow)
4. [Core Components](#core-components)
5. [AI Scoring Engine](#ai-scoring-engine)
6. [P/L Calculation Engine](#pl-calculation-engine)
7. [Database Schema](#database-schema)
8. [API Design](#api-design)
9. [Performance Considerations](#performance-considerations)
10. [Security Architecture](#security-architecture)

## System Overview

### High-Level Architecture
```
┌─────────────────────────────────────────────────────────────┐
│                     Calendar Spreads System                  │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────┐    ┌──────────────┐    ┌──────────────┐  │
│  │  TradingView │───▶│   Watchlist  │───▶│    Market    │  │
│  │  Integration │    │   Manager    │    │   Scanner    │  │
│  └──────────────┘    └──────────────┘    └──────────────┘  │
│         │                    │                    │          │
│         ▼                    ▼                    ▼          │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              Calendar Spread Analyzer                │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • Options Chain Fetcher                             │   │
│  │  • Spread Constructor                                │   │
│  │  • Greeks Calculator                                 │   │
│  │  • Volatility Analyzer                               │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                  AI Scoring Engine                   │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • Feature Extraction                                │   │
│  │  • ML Model Pipeline                                 │   │
│  │  • Score Calculation                                 │   │
│  │  • Ranking Algorithm                                 │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │              P/L Calculation Engine                  │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • Max Profit Calculator                             │   │
│  │  • Max Loss Calculator                               │   │
│  │  • Breakeven Analyzer                                │   │
│  │  • Monte Carlo Simulator                             │   │
│  └──────────────────────────────────────────────────────┘   │
│                            │                                 │
│                            ▼                                 │
│  ┌──────────────────────────────────────────────────────┐   │
│  │                   Output Layer                       │   │
│  ├──────────────────────────────────────────────────────┤   │
│  │  • REST API          • WebSocket Stream              │   │
│  │  • Dashboard UI      • Alert System                  │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Technology Stack
- **Backend**: Python 3.11+ with FastAPI
- **AI/ML**: TensorFlow 2.14+, scikit-learn 1.3+
- **Options Data**: IBKR API, Yahoo Finance, Polygon.io
- **Database**: PostgreSQL 15 + TimescaleDB
- **Cache**: Redis 7.2
- **Message Queue**: RabbitMQ
- **Monitoring**: Prometheus + Grafana

## Component Architecture

### Service-Oriented Design
```python
# Service Registry
services/
├── watchlist_service.py       # TradingView integration
├── market_data_service.py     # Real-time market data
├── options_chain_service.py   # Options chain fetching
├── analysis_service.py        # Calendar spread analysis
├── scoring_service.py         # AI scoring engine
├── calculation_service.py     # P/L calculations
├── notification_service.py    # Alerts and notifications
└── execution_service.py       # Trade execution
```

### Microservices Communication
```yaml
services:
  - name: watchlist-service
    port: 8001
    dependencies: [tradingview-api]

  - name: analysis-service
    port: 8002
    dependencies: [market-data, options-chain]

  - name: scoring-service
    port: 8003
    dependencies: [analysis-service]

  - name: calculation-service
    port: 8004
    dependencies: [analysis-service]
```

## Data Flow

### Real-Time Processing Pipeline
```python
class CalendarSpreadPipeline:
    """
    Asynchronous pipeline for processing calendar spread opportunities
    """

    async def process(self):
        # Stage 1: Data Collection
        watchlists = await self.fetch_watchlists()
        symbols = await self.extract_symbols(watchlists)

        # Stage 2: Market Data
        market_data = await self.fetch_market_data(symbols)
        options_chains = await self.fetch_options_chains(symbols)

        # Stage 3: Spread Construction
        potential_spreads = await self.construct_spreads(
            market_data,
            options_chains
        )

        # Stage 4: Analysis & Scoring
        analyzed_spreads = await self.analyze_spreads(potential_spreads)
        scored_spreads = await self.score_spreads(analyzed_spreads)

        # Stage 5: P/L Calculation
        spreads_with_pl = await self.calculate_pl(scored_spreads)

        # Stage 6: Output
        await self.publish_results(spreads_with_pl)

    async def fetch_watchlists(self) -> List[Watchlist]:
        """Fetch watchlists from TradingView"""
        async with TradingViewClient() as client:
            return await client.get_watchlists()

    async def construct_spreads(
        self,
        market_data: MarketData,
        chains: OptionsChains
    ) -> List[CalendarSpread]:
        """Construct potential calendar spreads"""
        spreads = []

        for symbol in market_data.symbols:
            chain = chains[symbol]
            current_price = market_data[symbol].price

            # Find ATM strike
            atm_strike = self.find_atm_strike(current_price, chain.strikes)

            # Get front month (30-45 DTE)
            front_expiry = self.find_front_expiry(chain.expirations)

            # Get back month (60-90 DTE)
            back_expiry = self.find_back_expiry(chain.expirations)

            # Construct spread
            spread = CalendarSpread(
                symbol=symbol,
                strike=atm_strike,
                front_expiry=front_expiry,
                back_expiry=back_expiry,
                front_option=chain.get_option(atm_strike, front_expiry),
                back_option=chain.get_option(atm_strike, back_expiry)
            )

            spreads.append(spread)

        return spreads
```

### Event-Driven Architecture
```python
# Event definitions
@dataclass
class CalendarSpreadEvent:
    event_type: str
    timestamp: datetime
    payload: Dict[str, Any]

class EventTypes:
    WATCHLIST_UPDATED = "watchlist.updated"
    SPREAD_IDENTIFIED = "spread.identified"
    SPREAD_SCORED = "spread.scored"
    ALERT_TRIGGERED = "alert.triggered"
    TRADE_EXECUTED = "trade.executed"

# Event handler
class CalendarSpreadEventHandler:
    def __init__(self):
        self.handlers = {
            EventTypes.WATCHLIST_UPDATED: self.handle_watchlist_update,
            EventTypes.SPREAD_IDENTIFIED: self.handle_spread_identified,
            EventTypes.SPREAD_SCORED: self.handle_spread_scored,
        }

    async def handle_event(self, event: CalendarSpreadEvent):
        handler = self.handlers.get(event.event_type)
        if handler:
            await handler(event.payload)
```

## Core Components

### CalendarSpreadAnalyzer Class
```python
class CalendarSpreadAnalyzer:
    """
    Core analyzer for calendar spread opportunities
    """

    def __init__(self, config: AnalyzerConfig):
        self.config = config
        self.options_fetcher = OptionsFetcher()
        self.greeks_calculator = GreeksCalculator()
        self.volatility_analyzer = VolatilityAnalyzer()

    async def analyze(self, symbol: str) -> List[CalendarSpreadOpportunity]:
        """
        Analyze a symbol for calendar spread opportunities
        """
        # Fetch options chain
        chain = await self.options_fetcher.fetch_chain(symbol)

        # Get current market data
        market_data = await self.get_market_data(symbol)

        # Filter valid expirations
        valid_expirations = self.filter_expirations(chain.expirations)

        # Generate spread combinations
        spreads = self.generate_spreads(
            chain,
            valid_expirations,
            market_data.price
        )

        # Analyze each spread
        opportunities = []
        for spread in spreads:
            opportunity = await self.analyze_spread(spread, market_data)
            if opportunity.meets_criteria():
                opportunities.append(opportunity)

        return opportunities

    def filter_expirations(self, expirations: List[date]) -> Dict:
        """
        Filter expirations into front and back months
        """
        today = date.today()
        front_months = []
        back_months = []

        for exp in expirations:
            dte = (exp - today).days

            if self.config.min_dte_front <= dte <= self.config.max_dte_front:
                front_months.append(exp)
            elif self.config.min_dte_back <= dte <= self.config.max_dte_back:
                back_months.append(exp)

        return {
            'front': front_months,
            'back': back_months
        }

    async def analyze_spread(
        self,
        spread: CalendarSpread,
        market_data: MarketData
    ) -> CalendarSpreadOpportunity:
        """
        Detailed analysis of a single calendar spread
        """
        # Calculate Greeks
        greeks = self.greeks_calculator.calculate(spread)

        # Analyze volatility
        iv_analysis = self.volatility_analyzer.analyze(
            spread.front_option.iv,
            spread.back_option.iv,
            market_data.historical_volatility
        )

        # Calculate time decay differential
        theta_ratio = abs(spread.front_option.theta / spread.back_option.theta)

        # Price stability analysis
        price_stability = self.analyze_price_stability(
            market_data.price_history
        )

        # Liquidity check
        liquidity_score = self.calculate_liquidity_score(
            spread.front_option,
            spread.back_option
        )

        return CalendarSpreadOpportunity(
            spread=spread,
            greeks=greeks,
            iv_analysis=iv_analysis,
            theta_ratio=theta_ratio,
            price_stability=price_stability,
            liquidity_score=liquidity_score
        )
```

### Greeks Calculator
```python
class GreeksCalculator:
    """
    Calculate Greeks for calendar spreads using Black-Scholes model
    """

    def calculate(self, spread: CalendarSpread) -> SpreadGreeks:
        """
        Calculate aggregate Greeks for the calendar spread
        """
        # Calculate individual Greeks
        front_greeks = self.calculate_option_greeks(
            spread.front_option,
            spread.underlying_price
        )
        back_greeks = self.calculate_option_greeks(
            spread.back_option,
            spread.underlying_price
        )

        # Aggregate spread Greeks
        # Calendar spread = long back month - short front month
        spread_greeks = SpreadGreeks(
            delta=back_greeks.delta - front_greeks.delta,
            gamma=back_greeks.gamma - front_greeks.gamma,
            theta=back_greeks.theta - front_greeks.theta,  # Net positive
            vega=back_greeks.vega - front_greeks.vega,
            rho=back_greeks.rho - front_greeks.rho
        )

        return spread_greeks

    def calculate_option_greeks(
        self,
        option: Option,
        spot_price: float
    ) -> OptionGreeks:
        """
        Black-Scholes Greeks calculation
        """
        S = spot_price
        K = option.strike
        T = option.days_to_expiry / 365.0
        r = 0.05  # Risk-free rate
        sigma = option.implied_volatility

        # Calculate d1 and d2
        d1 = (np.log(S/K) + (r + 0.5*sigma**2)*T) / (sigma*np.sqrt(T))
        d2 = d1 - sigma*np.sqrt(T)

        # Calculate Greeks
        if option.option_type == 'CALL':
            delta = norm.cdf(d1)
            theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T))
                    - r*K*np.exp(-r*T)*norm.cdf(d2)) / 365
        else:  # PUT
            delta = norm.cdf(d1) - 1
            theta = (-S*norm.pdf(d1)*sigma/(2*np.sqrt(T))
                    + r*K*np.exp(-r*T)*norm.cdf(-d2)) / 365

        gamma = norm.pdf(d1) / (S*sigma*np.sqrt(T))
        vega = S*norm.pdf(d1)*np.sqrt(T) / 100
        rho = K*T*np.exp(-r*T)*norm.cdf(d2 if option.option_type == 'CALL' else -d2) / 100

        return OptionGreeks(
            delta=delta,
            gamma=gamma,
            theta=theta,
            vega=vega,
            rho=rho
        )
```

## AI Scoring Engine

### Machine Learning Model Architecture
```python
class CalendarSpreadScoringModel:
    """
    Neural network model for scoring calendar spreads
    """

    def __init__(self):
        self.model = self._build_model()
        self.feature_scaler = StandardScaler()
        self.feature_extractor = FeatureExtractor()

    def _build_model(self) -> tf.keras.Model:
        """
        Build the neural network architecture
        """
        inputs = tf.keras.Input(shape=(45,))  # 45 features

        # First dense block with batch normalization
        x = tf.keras.layers.Dense(128, activation='relu')(inputs)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.3)(x)

        # Second dense block
        x = tf.keras.layers.Dense(64, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)
        x = tf.keras.layers.Dropout(0.2)(x)

        # Third dense block
        x = tf.keras.layers.Dense(32, activation='relu')(x)
        x = tf.keras.layers.BatchNormalization()(x)

        # Output layer (score 0-100)
        outputs = tf.keras.layers.Dense(1, activation='sigmoid')(x)
        outputs = tf.keras.layers.Lambda(lambda x: x * 100)(outputs)

        model = tf.keras.Model(inputs=inputs, outputs=outputs)

        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=0.001),
            loss='mse',
            metrics=['mae']
        )

        return model

    def extract_features(self, opportunity: CalendarSpreadOpportunity) -> np.ndarray:
        """
        Extract features from calendar spread opportunity
        """
        features = []

        # Time decay features (7 features)
        features.extend([
            opportunity.spread.front_option.theta,
            opportunity.spread.back_option.theta,
            opportunity.theta_ratio,
            opportunity.spread.front_option.days_to_expiry,
            opportunity.spread.back_option.days_to_expiry,
            opportunity.spread.back_option.days_to_expiry -
                opportunity.spread.front_option.days_to_expiry,
            opportunity.theta_ratio / opportunity.spread.front_option.days_to_expiry
        ])

        # Volatility features (8 features)
        features.extend([
            opportunity.spread.front_option.implied_volatility,
            opportunity.spread.back_option.implied_volatility,
            opportunity.iv_analysis.iv_ratio,
            opportunity.iv_analysis.iv_percentile,
            opportunity.iv_analysis.iv_skew,
            opportunity.market_data.historical_volatility,
            opportunity.iv_analysis.iv_hv_ratio,
            opportunity.iv_analysis.term_structure_slope
        ])

        # Price features (6 features)
        features.extend([
            opportunity.price_stability.std_dev_20d,
            opportunity.price_stability.atr_14,
            opportunity.price_stability.price_range_pct,
            opportunity.moneyness,
            opportunity.distance_from_strike_pct,
            opportunity.price_stability.trend_strength
        ])

        # Greeks features (5 features)
        features.extend([
            opportunity.spread_greeks.delta,
            opportunity.spread_greeks.gamma,
            opportunity.spread_greeks.vega,
            abs(opportunity.spread_greeks.delta),
            opportunity.spread_greeks.gamma / opportunity.spread_greeks.theta
        ])

        # Liquidity features (4 features)
        features.extend([
            opportunity.spread.front_option.volume,
            opportunity.spread.back_option.volume,
            opportunity.spread.front_option.open_interest,
            opportunity.spread.back_option.open_interest
        ])

        # Market regime features (5 features)
        features.extend([
            opportunity.market_data.vix_level,
            opportunity.market_data.sector_correlation,
            opportunity.market_data.market_breadth,
            opportunity.market_data.put_call_ratio,
            opportunity.market_data.term_structure_slope
        ])

        # Risk/reward features (5 features)
        features.extend([
            opportunity.max_profit,
            opportunity.max_loss,
            opportunity.profit_loss_ratio,
            opportunity.probability_of_profit,
            opportunity.expected_value
        ])

        # Technical indicators (5 features)
        features.extend([
            opportunity.technical.rsi_14,
            opportunity.technical.bollinger_band_width,
            opportunity.technical.macd_signal,
            opportunity.technical.support_resistance_distance,
            opportunity.technical.volume_ratio_20d
        ])

        return np.array(features)

    def score(self, opportunity: CalendarSpreadOpportunity) -> float:
        """
        Generate a score for the calendar spread opportunity
        """
        # Extract features
        features = self.extract_features(opportunity)

        # Scale features
        features_scaled = self.feature_scaler.transform(
            features.reshape(1, -1)
        )

        # Predict score
        score = self.model.predict(features_scaled, verbose=0)[0][0]

        # Apply business rules adjustments
        score = self.apply_business_rules(score, opportunity)

        return min(max(score, 0), 100)  # Ensure score is between 0-100

    def apply_business_rules(
        self,
        score: float,
        opportunity: CalendarSpreadOpportunity
    ) -> float:
        """
        Apply business rules to adjust the ML score
        """
        adjusted_score = score

        # Penalize high IV environments
        if opportunity.spread.front_option.implied_volatility > 0.30:
            adjusted_score *= 0.8

        # Reward optimal theta ratio
        if 1.5 <= opportunity.theta_ratio <= 2.5:
            adjusted_score *= 1.1

        # Penalize poor liquidity
        if opportunity.liquidity_score < 50:
            adjusted_score *= 0.9

        # Reward stable price action
        if opportunity.price_stability.std_dev_20d < 0.02:
            adjusted_score *= 1.05

        return adjusted_score
```

### Feature Engineering Pipeline
```python
class FeatureEngineeringPipeline:
    """
    Feature engineering for calendar spread analysis
    """

    def __init__(self):
        self.technical_analyzer = TechnicalAnalyzer()
        self.volatility_analyzer = VolatilityAnalyzer()
        self.market_regime_detector = MarketRegimeDetector()

    def engineer_features(
        self,
        spread: CalendarSpread,
        market_data: MarketData
    ) -> Dict[str, float]:
        """
        Engineer comprehensive features for ML model
        """
        features = {}

        # Temporal features
        features.update(self.create_temporal_features(spread))

        # Volatility surface features
        features.update(self.create_volatility_surface_features(spread))

        # Market microstructure features
        features.update(self.create_microstructure_features(spread))

        # Cross-asset features
        features.update(self.create_cross_asset_features(market_data))

        # Regime features
        features.update(self.create_regime_features(market_data))

        return features

    def create_temporal_features(self, spread: CalendarSpread) -> Dict:
        """
        Time-based features
        """
        front_dte = spread.front_option.days_to_expiry
        back_dte = spread.back_option.days_to_expiry

        return {
            'dte_ratio': back_dte / front_dte,
            'dte_difference': back_dte - front_dte,
            'front_time_decay_acceleration': 1 / np.sqrt(front_dte),
            'back_time_decay_acceleration': 1 / np.sqrt(back_dte),
            'weekend_decay_advantage': self.calculate_weekend_decay(spread),
            'days_until_earnings': self.get_days_to_earnings(spread.symbol)
        }
```

## P/L Calculation Engine

### Profit/Loss Calculator
```python
class ProfitLossCalculator:
    """
    Calculate profit/loss scenarios for calendar spreads
    """

    def __init__(self):
        self.bs_pricer = BlackScholesPricer()
        self.monte_carlo = MonteCarloSimulator()

    def calculate_pl_matrix(
        self,
        spread: CalendarSpread
    ) -> PLMatrix:
        """
        Calculate P/L across price and time dimensions
        """
        # Define price range (±20% from current)
        current_price = spread.underlying_price
        price_range = np.linspace(
            current_price * 0.8,
            current_price * 1.2,
            41
        )

        # Define time points
        days_to_front_expiry = spread.front_option.days_to_expiry
        time_points = np.arange(0, days_to_front_expiry + 1)

        # Calculate P/L matrix
        pl_matrix = np.zeros((len(time_points), len(price_range)))

        for t_idx, days_passed in enumerate(time_points):
            for p_idx, price in enumerate(price_range):
                pl = self.calculate_pl_at_point(
                    spread,
                    price,
                    days_passed
                )
                pl_matrix[t_idx, p_idx] = pl

        return PLMatrix(
            prices=price_range,
            times=time_points,
            values=pl_matrix,
            max_profit=np.max(pl_matrix),
            max_loss=np.min(pl_matrix),
            breakeven_points=self.find_breakeven_points(pl_matrix, price_range)
        )

    def calculate_pl_at_point(
        self,
        spread: CalendarSpread,
        underlying_price: float,
        days_passed: int
    ) -> float:
        """
        Calculate P/L at specific price and time
        """
        # Time remaining for each option
        front_time_remaining = max(
            spread.front_option.days_to_expiry - days_passed,
            0
        ) / 365.0
        back_time_remaining = (
            spread.back_option.days_to_expiry - days_passed
        ) / 365.0

        # Calculate option values
        if front_time_remaining > 0:
            # Front month still has time value
            front_value = self.bs_pricer.price(
                underlying_price,
                spread.strike,
                front_time_remaining,
                spread.front_option.implied_volatility,
                option_type=spread.option_type
            )
        else:
            # Front month expired, calculate intrinsic value
            if spread.option_type == 'CALL':
                front_value = max(underlying_price - spread.strike, 0)
            else:
                front_value = max(spread.strike - underlying_price, 0)

        back_value = self.bs_pricer.price(
            underlying_price,
            spread.strike,
            back_time_remaining,
            spread.back_option.implied_volatility,
            option_type=spread.option_type
        )

        # Calculate P/L
        # We're short front, long back
        initial_cost = (spread.back_option.price - spread.front_option.price)
        current_value = back_value - front_value

        return current_value - initial_cost

    def calculate_max_profit(self, spread: CalendarSpread) -> float:
        """
        Calculate theoretical maximum profit
        """
        # Max profit typically occurs at strike price at front expiry
        front_expiry_value = 0  # Front option expires worthless

        # Back option value at front expiry
        time_remaining = (
            spread.back_option.days_to_expiry -
            spread.front_option.days_to_expiry
        ) / 365.0

        back_value_at_front_expiry = self.bs_pricer.price(
            spread.strike,  # At the money
            spread.strike,
            time_remaining,
            spread.back_option.implied_volatility,
            option_type=spread.option_type
        )

        initial_cost = (
            spread.back_option.price - spread.front_option.price
        )

        max_profit = back_value_at_front_expiry - initial_cost

        return max_profit

    def calculate_probability_of_profit(
        self,
        spread: CalendarSpread
    ) -> float:
        """
        Calculate probability of profit using Monte Carlo simulation
        """
        simulations = 10000
        profitable_outcomes = 0

        for _ in range(simulations):
            # Simulate price path
            final_price = self.monte_carlo.simulate_price_path(
                spread.underlying_price,
                spread.market_data.historical_volatility,
                spread.front_option.days_to_expiry
            )

            # Calculate P/L at simulated price
            pl = self.calculate_pl_at_point(
                spread,
                final_price,
                spread.front_option.days_to_expiry
            )

            if pl > 0:
                profitable_outcomes += 1

        return profitable_outcomes / simulations
```

### Monte Carlo Simulation
```python
class MonteCarloSimulator:
    """
    Monte Carlo simulation for calendar spread analysis
    """

    def __init__(self, random_seed: int = 42):
        np.random.seed(random_seed)

    def simulate_spread_outcomes(
        self,
        spread: CalendarSpread,
        num_simulations: int = 10000
    ) -> SimulationResults:
        """
        Run Monte Carlo simulation for spread outcomes
        """
        results = []

        for _ in range(num_simulations):
            # Simulate price path to front expiry
            price_path = self.simulate_price_path(
                spread.underlying_price,
                spread.market_data.historical_volatility,
                spread.front_option.days_to_expiry
            )

            # Simulate IV changes
            front_iv = self.simulate_iv_change(
                spread.front_option.implied_volatility,
                spread.front_option.days_to_expiry
            )
            back_iv = self.simulate_iv_change(
                spread.back_option.implied_volatility,
                spread.back_option.days_to_expiry
            )

            # Calculate P/L for this scenario
            pl = self.calculate_scenario_pl(
                spread,
                price_path[-1],
                front_iv,
                back_iv
            )

            results.append(pl)

        results = np.array(results)

        return SimulationResults(
            mean_pl=np.mean(results),
            median_pl=np.median(results),
            std_dev=np.std(results),
            var_95=np.percentile(results, 5),
            cvar_95=np.mean(results[results <= np.percentile(results, 5)]),
            probability_of_profit=np.sum(results > 0) / num_simulations,
            expected_value=np.mean(results),
            sharpe_ratio=np.mean(results) / np.std(results) if np.std(results) > 0 else 0,
            max_pl=np.max(results),
            min_pl=np.min(results),
            percentiles={
                5: np.percentile(results, 5),
                25: np.percentile(results, 25),
                50: np.percentile(results, 50),
                75: np.percentile(results, 75),
                95: np.percentile(results, 95)
            }
        )

    def simulate_price_path(
        self,
        initial_price: float,
        volatility: float,
        days: int
    ) -> np.ndarray:
        """
        Simulate stock price path using Geometric Brownian Motion
        """
        dt = 1/252  # Daily time step
        prices = [initial_price]

        for _ in range(days):
            drift = 0  # Assume risk-neutral
            diffusion = volatility * np.sqrt(dt) * np.random.normal()
            price = prices[-1] * np.exp(drift * dt + diffusion)
            prices.append(price)

        return np.array(prices)
```

## Database Schema

### PostgreSQL + TimescaleDB Schema
```sql
-- Main spreads table
CREATE TABLE calendar_spreads (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    underlying_price DECIMAL(10, 2) NOT NULL,
    strike DECIMAL(10, 2) NOT NULL,
    option_type VARCHAR(4) NOT NULL CHECK (option_type IN ('CALL', 'PUT')),
    front_expiry DATE NOT NULL,
    back_expiry DATE NOT NULL,
    front_option_id UUID REFERENCES options(id),
    back_option_id UUID REFERENCES options(id),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Options data table
CREATE TABLE options (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    symbol VARCHAR(10) NOT NULL,
    strike DECIMAL(10, 2) NOT NULL,
    expiry DATE NOT NULL,
    option_type VARCHAR(4) NOT NULL,
    bid DECIMAL(10, 2),
    ask DECIMAL(10, 2),
    last DECIMAL(10, 2),
    volume INTEGER,
    open_interest INTEGER,
    implied_volatility DECIMAL(5, 4),
    delta DECIMAL(5, 4),
    gamma DECIMAL(5, 4),
    theta DECIMAL(10, 4),
    vega DECIMAL(10, 4),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE(symbol, strike, expiry, option_type)
);

-- Calendar spread analysis results
CREATE TABLE spread_analysis (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    spread_id UUID REFERENCES calendar_spreads(id),
    score DECIMAL(5, 2) NOT NULL CHECK (score >= 0 AND score <= 100),
    max_profit DECIMAL(10, 2),
    max_loss DECIMAL(10, 2),
    breakeven_lower DECIMAL(10, 2),
    breakeven_upper DECIMAL(10, 2),
    probability_of_profit DECIMAL(5, 4),
    expected_value DECIMAL(10, 2),
    theta_ratio DECIMAL(5, 2),
    iv_percentile DECIMAL(5, 2),
    liquidity_score DECIMAL(5, 2),
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Time series data for spreads (using TimescaleDB)
CREATE TABLE spread_metrics (
    time TIMESTAMPTZ NOT NULL,
    spread_id UUID NOT NULL REFERENCES calendar_spreads(id),
    underlying_price DECIMAL(10, 2),
    spread_value DECIMAL(10, 2),
    front_price DECIMAL(10, 2),
    back_price DECIMAL(10, 2),
    front_iv DECIMAL(5, 4),
    back_iv DECIMAL(5, 4),
    spread_delta DECIMAL(5, 4),
    spread_theta DECIMAL(10, 4),
    spread_vega DECIMAL(10, 4)
);

-- Convert to hypertable for time-series optimization
SELECT create_hypertable('spread_metrics', 'time');

-- Indexes for performance
CREATE INDEX idx_spreads_symbol ON calendar_spreads(symbol);
CREATE INDEX idx_spreads_created ON calendar_spreads(created_at DESC);
CREATE INDEX idx_analysis_score ON spread_analysis(score DESC);
CREATE INDEX idx_analysis_spread ON spread_analysis(spread_id);
CREATE INDEX idx_options_lookup ON options(symbol, strike, expiry, option_type);

-- Materialized view for top spreads
CREATE MATERIALIZED VIEW top_calendar_spreads AS
SELECT
    cs.id,
    cs.symbol,
    cs.strike,
    cs.option_type,
    cs.front_expiry,
    cs.back_expiry,
    sa.score,
    sa.max_profit,
    sa.max_loss,
    sa.probability_of_profit,
    sa.expected_value,
    cs.created_at
FROM calendar_spreads cs
JOIN spread_analysis sa ON cs.id = sa.spread_id
WHERE sa.created_at >= NOW() - INTERVAL '1 hour'
ORDER BY sa.score DESC
LIMIT 100;

-- Refresh policy for materialized view
CREATE OR REPLACE FUNCTION refresh_top_spreads()
RETURNS TRIGGER AS $$
BEGIN
    REFRESH MATERIALIZED VIEW CONCURRENTLY top_calendar_spreads;
    RETURN NULL;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER trigger_refresh_spreads
AFTER INSERT OR UPDATE ON spread_analysis
FOR EACH STATEMENT
EXECUTE FUNCTION refresh_top_spreads();
```

## API Design

### RESTful API Endpoints
```python
from fastapi import FastAPI, Query, HTTPException
from typing import List, Optional
from datetime import date

app = FastAPI(title="Calendar Spreads API")

# Watchlist endpoints
@app.get("/api/v1/watchlists")
async def get_watchlists():
    """Get all TradingView watchlists"""
    return await watchlist_service.get_all()

@app.post("/api/v1/watchlists/sync")
async def sync_watchlists():
    """Sync watchlists from TradingView"""
    return await watchlist_service.sync_from_tradingview()

# Analysis endpoints
@app.get("/api/v1/spreads/analyze/{symbol}")
async def analyze_symbol(
    symbol: str,
    min_score: Optional[float] = Query(60, ge=0, le=100),
    max_iv: Optional[float] = Query(0.30, ge=0, le=1),
    option_type: Optional[str] = Query("BOTH", regex="^(CALL|PUT|BOTH)$")
):
    """Analyze calendar spread opportunities for a symbol"""
    opportunities = await analyzer.analyze(
        symbol=symbol,
        min_score=min_score,
        max_iv=max_iv,
        option_type=option_type
    )
    return opportunities

@app.get("/api/v1/spreads/top")
async def get_top_spreads(
    limit: int = Query(20, ge=1, le=100),
    min_score: float = Query(70, ge=0, le=100),
    symbols: Optional[List[str]] = Query(None)
):
    """Get top-scored calendar spreads"""
    spreads = await spread_service.get_top_spreads(
        limit=limit,
        min_score=min_score,
        symbols=symbols
    )
    return spreads

# P/L calculation endpoints
@app.post("/api/v1/spreads/calculate-pl")
async def calculate_pl(spread: CalendarSpreadRequest):
    """Calculate P/L matrix for a calendar spread"""
    pl_matrix = await pl_calculator.calculate(spread)
    return {
        "max_profit": pl_matrix.max_profit,
        "max_loss": pl_matrix.max_loss,
        "breakeven_points": pl_matrix.breakeven_points,
        "probability_of_profit": pl_matrix.probability_of_profit,
        "expected_value": pl_matrix.expected_value,
        "pl_chart_data": pl_matrix.to_chart_format()
    }

# Real-time updates via WebSocket
@app.websocket("/ws/spreads")
async def websocket_spreads(websocket: WebSocket):
    """WebSocket for real-time spread updates"""
    await websocket.accept()

    try:
        while True:
            # Send updates every 5 seconds
            updates = await spread_service.get_recent_updates()
            await websocket.send_json(updates)
            await asyncio.sleep(5)
    except WebSocketDisconnect:
        pass

# Alerts endpoints
@app.post("/api/v1/alerts")
async def create_alert(alert: AlertRequest):
    """Create a new calendar spread alert"""
    alert_id = await alert_service.create(alert)
    return {"alert_id": alert_id}

@app.get("/api/v1/alerts")
async def get_alerts(active_only: bool = True):
    """Get user's calendar spread alerts"""
    return await alert_service.get_user_alerts(active_only)
```

### GraphQL Schema
```graphql
type Query {
  # Get calendar spread opportunities
  calendarSpreads(
    symbols: [String!]
    minScore: Float
    maxIV: Float
    optionType: OptionType
    limit: Int
  ): [CalendarSpread!]!

  # Get specific spread details
  calendarSpread(id: ID!): CalendarSpread

  # Get P/L analysis
  plAnalysis(spreadId: ID!): PLAnalysis!
}

type Subscription {
  # Real-time spread updates
  spreadUpdates(symbols: [String!]): SpreadUpdate!

  # Alert notifications
  alertTriggered: Alert!
}

type CalendarSpread {
  id: ID!
  symbol: String!
  strike: Float!
  optionType: OptionType!
  frontExpiry: Date!
  backExpiry: Date!
  frontOption: Option!
  backOption: Option!
  analysis: SpreadAnalysis!
  plMatrix: PLMatrix!
}

type SpreadAnalysis {
  score: Float!
  maxProfit: Float!
  maxLoss: Float!
  breakevenPoints: [Float!]!
  probabilityOfProfit: Float!
  expectedValue: Float!
  thetaRatio: Float!
  ivPercentile: Float!
  liquidityScore: Float!
}

type PLMatrix {
  prices: [Float!]!
  times: [Int!]!
  values: [[Float!]!]!
  chartData: ChartData!
}

enum OptionType {
  CALL
  PUT
}
```

## Performance Considerations

### Caching Strategy
```python
class CalendarSpreadCache:
    """
    Multi-layer caching for calendar spread data
    """

    def __init__(self):
        self.redis_client = redis.Redis(
            host='localhost',
            port=6379,
            decode_responses=True
        )
        self.local_cache = TTLCache(maxsize=1000, ttl=60)

    async def get_spread_analysis(self, spread_key: str):
        """
        Get spread analysis with cache hierarchy
        """
        # Level 1: Local memory cache
        if spread_key in self.local_cache:
            return self.local_cache[spread_key]

        # Level 2: Redis cache
        redis_data = self.redis_client.get(f"spread:{spread_key}")
        if redis_data:
            data = json.loads(redis_data)
            self.local_cache[spread_key] = data
            return data

        # Level 3: Database
        data = await self.fetch_from_database(spread_key)

        # Update caches
        self.redis_client.setex(
            f"spread:{spread_key}",
            300,  # 5 minute TTL
            json.dumps(data)
        )
        self.local_cache[spread_key] = data

        return data
```

### Query Optimization
```python
class OptimizedSpreadQuery:
    """
    Optimized database queries for calendar spreads
    """

    async def get_top_spreads_batch(
        self,
        symbols: List[str],
        limit: int = 100
    ):
        """
        Batch query for multiple symbols with optimization
        """
        query = """
            WITH RankedSpreads AS (
                SELECT
                    cs.*,
                    sa.*,
                    ROW_NUMBER() OVER (
                        PARTITION BY cs.symbol
                        ORDER BY sa.score DESC
                    ) as rank
                FROM calendar_spreads cs
                JOIN spread_analysis sa ON cs.id = sa.spread_id
                WHERE
                    cs.symbol = ANY($1)
                    AND sa.created_at >= NOW() - INTERVAL '1 hour'
            )
            SELECT * FROM RankedSpreads
            WHERE rank <= $2
            ORDER BY score DESC
            LIMIT $3
        """

        return await self.db.fetch(query, symbols, 5, limit)
```

## Security Architecture

### Authentication & Authorization
```python
class CalendarSpreadSecurity:
    """
    Security layer for calendar spread operations
    """

    def __init__(self):
        self.jwt_secret = os.environ.get("JWT_SECRET")
        self.rate_limiter = RateLimiter()

    async def verify_access(
        self,
        token: str,
        required_permission: str
    ) -> bool:
        """
        Verify user has access to calendar spread features
        """
        try:
            # Decode JWT token
            payload = jwt.decode(
                token,
                self.jwt_secret,
                algorithms=["HS256"]
            )

            # Check subscription level
            if not self.has_calendar_spread_access(payload):
                return False

            # Check specific permission
            return required_permission in payload.get("permissions", [])

        except jwt.InvalidTokenError:
            return False

    def has_calendar_spread_access(self, user_payload: dict) -> bool:
        """
        Check if user subscription includes calendar spreads
        """
        subscription_tier = user_payload.get("subscription_tier")
        return subscription_tier in ["premium", "professional", "institutional"]
```

### Data Encryption
```python
class SpreadDataEncryption:
    """
    Encryption for sensitive spread data
    """

    def encrypt_trade_data(self, trade_data: dict) -> str:
        """
        Encrypt sensitive trade information
        """
        fernet = Fernet(self.encryption_key)
        json_data = json.dumps(trade_data)
        encrypted = fernet.encrypt(json_data.encode())
        return encrypted.decode()

    def decrypt_trade_data(self, encrypted_data: str) -> dict:
        """
        Decrypt trade information
        """
        fernet = Fernet(self.encryption_key)
        decrypted = fernet.decrypt(encrypted_data.encode())
        return json.loads(decrypted.decode())
```

---
*Technical Architecture Document v1.0.0*
*Last Updated: January 2025*