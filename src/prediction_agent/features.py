"""
Feature Engineering

Generates features for multi-sector prediction markets.
Implements sector-specific and common features for ML models.

Author: Python Pro
Created: 2025-11-09
"""

import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import numpy as np
import pandas as pd

from .data_sources import DataSourceManager, DataSourceResult
from .sector_configs import MarketSector

logger = logging.getLogger(__name__)


class FeatureEngineering:
    """Feature engineering for prediction markets"""

    def __init__(self, data_source_manager: Optional[DataSourceManager] = None):
        """
        Initialize feature engineering

        Args:
            data_source_manager: DataSourceManager instance (creates new if None)
        """
        self.data_source_manager = data_source_manager or DataSourceManager()

    # ========================================================================
    # COMMON FEATURES (ALL SECTORS)
    # ========================================================================

    def extract_price_history_features(self, market: Dict) -> Dict[str, float]:
        """
        Extract features from price history

        Args:
            market: Market dictionary with yes_price, no_price

        Returns:
            Dictionary of price features
        """
        features = {}

        yes_price = float(market.get('yes_price', 0.5))
        no_price = float(market.get('no_price', 0.5))

        # Basic price features
        features['yes_price'] = yes_price
        features['no_price'] = no_price
        features['price_spread'] = abs(yes_price + no_price - 1.0)  # Market efficiency
        features['price_deviation_from_50'] = abs(yes_price - 0.5)  # Distance from even odds

        # Price extremity indicators
        features['price_extreme_high'] = 1.0 if yes_price > 0.75 else 0.0
        features['price_extreme_low'] = 1.0 if yes_price < 0.25 else 0.0

        # Implied probability
        features['implied_prob_yes'] = yes_price
        features['implied_prob_no'] = no_price

        # Price efficiency score (how close sum is to 1.0)
        price_sum = yes_price + no_price
        features['price_efficiency'] = 1.0 - abs(price_sum - 1.0)

        return features

    def extract_volume_features(self, market: Dict) -> Dict[str, float]:
        """
        Extract features from volume and liquidity

        Args:
            market: Market dictionary with volume, open_interest

        Returns:
            Dictionary of volume features
        """
        features = {}

        volume = float(market.get('volume', 0))
        open_interest = int(market.get('open_interest', 0))

        # Volume features (log scale to handle wide range)
        features['volume'] = volume
        features['volume_log'] = np.log1p(volume)  # log(1 + volume)
        features['volume_high'] = 1.0 if volume >= 50000 else 0.0
        features['volume_medium'] = 1.0 if 10000 <= volume < 50000 else 0.0
        features['volume_low'] = 1.0 if volume < 10000 else 0.0

        # Open interest features
        features['open_interest'] = float(open_interest)
        features['open_interest_log'] = np.log1p(open_interest)
        features['open_interest_high'] = 1.0 if open_interest >= 5000 else 0.0

        # Liquidity score (combined metric)
        liquidity_score = (
            min(volume / 100000, 1.0) * 0.6 +
            min(open_interest / 10000, 1.0) * 0.4
        )
        features['liquidity_score'] = liquidity_score

        return features

    def extract_time_features(self, market: Dict) -> Dict[str, float]:
        """
        Extract time-based features

        Args:
            market: Market dictionary with close_time, expiration_time

        Returns:
            Dictionary of time features
        """
        features = {}

        close_time = market.get('close_time')
        now = datetime.now()

        if close_time:
            if isinstance(close_time, str):
                close_dt = datetime.fromisoformat(close_time.replace('Z', '+00:00'))
            else:
                close_dt = close_time

            # Remove timezone for comparison if needed
            if close_dt.tzinfo:
                now = datetime.now(close_dt.tzinfo)

            # Hours until close
            hours_to_close = (close_dt - now).total_seconds() / 3600
            hours_to_close = max(0, hours_to_close)

            features['hours_to_close'] = hours_to_close
            features['days_to_close'] = hours_to_close / 24

            # Time buckets
            features['closing_very_soon'] = 1.0 if hours_to_close <= 6 else 0.0
            features['closing_soon'] = 1.0 if 6 < hours_to_close <= 24 else 0.0
            features['closing_this_week'] = 1.0 if 24 < hours_to_close <= 168 else 0.0
            features['closing_later'] = 1.0 if hours_to_close > 168 else 0.0

            # Optimal timing window (12-48 hours is often best)
            features['optimal_timing'] = 1.0 if 12 <= hours_to_close <= 48 else 0.0

        else:
            # Default values if no close time
            features['hours_to_close'] = 48.0
            features['days_to_close'] = 2.0
            features['closing_very_soon'] = 0.0
            features['closing_soon'] = 0.0
            features['closing_this_week'] = 1.0
            features['closing_later'] = 0.0
            features['optimal_timing'] = 1.0

        # Day of week features (if close time available)
        if close_time and isinstance(close_dt, datetime):
            features['close_day_of_week'] = float(close_dt.weekday())
            features['close_is_weekend'] = 1.0 if close_dt.weekday() >= 5 else 0.0
        else:
            features['close_day_of_week'] = 0.0
            features['close_is_weekend'] = 0.0

        return features

    # ========================================================================
    # SPORTS FEATURES
    # ========================================================================

    def extract_sports_features(self, market: Dict, context: Dict) -> Dict[str, float]:
        """
        Extract sports-specific features

        Args:
            market: Market dictionary
            context: Context with sport type, teams, etc.

        Returns:
            Dictionary of sports features
        """
        features = {}

        # Get Reddit sentiment
        sport = context.get('sport', 'nfl')
        keywords = context.get('keywords', [])

        if keywords:
            sentiment_result = self.data_source_manager.get_reddit_sentiment(
                subreddit=sport,
                keywords=keywords,
                limit=50
            )

            if sentiment_result.success:
                features['reddit_sentiment'] = sentiment_result.data.get('sentiment_score', 50.0) / 100
                features['reddit_engagement'] = min(sentiment_result.data.get('engagement', 0) / 100, 1.0)
            else:
                features['reddit_sentiment'] = 0.5
                features['reddit_engagement'] = 0.0
        else:
            features['reddit_sentiment'] = 0.5
            features['reddit_engagement'] = 0.0

        # Team strength indicators (placeholder - would integrate real stats)
        home_team = market.get('home_team', '')
        away_team = market.get('away_team', '')

        # Popular teams (simplified)
        popular_teams = ['chiefs', 'bills', 'ravens', 'packers', '49ers', 'cowboys']
        features['home_team_popular'] = 1.0 if any(team in home_team.lower() for team in popular_teams) else 0.0
        features['away_team_popular'] = 1.0 if any(team in away_team.lower() for team in popular_teams) else 0.0

        # Market title analysis
        title = market.get('title', '').lower()
        features['is_playoff_game'] = 1.0 if 'playoff' in title or 'championship' in title else 0.0
        features['is_spread_market'] = 1.0 if 'spread' in title or 'over' in title or 'under' in title else 0.0

        return features

    # ========================================================================
    # POLITICS FEATURES
    # ========================================================================

    def extract_politics_features(self, market: Dict, context: Dict) -> Dict[str, float]:
        """
        Extract politics-specific features

        Args:
            market: Market dictionary
            context: Context with election type, candidates, etc.

        Returns:
            Dictionary of politics features
        """
        features = {}

        # Get Reddit political sentiment
        keywords = context.get('keywords', ['election'])

        sentiment_result = self.data_source_manager.get_reddit_sentiment(
            subreddit='politics',
            keywords=keywords,
            limit=100
        )

        if sentiment_result.success:
            features['political_sentiment'] = sentiment_result.data.get('sentiment_score', 50.0) / 100
            features['political_engagement'] = min(sentiment_result.data.get('engagement', 0) / 100, 1.0)
        else:
            features['political_sentiment'] = 0.5
            features['political_engagement'] = 0.0

        # Market type indicators
        title = market.get('title', '').lower()
        features['is_presidential'] = 1.0 if 'president' in title else 0.0
        features['is_congressional'] = 1.0 if 'senate' in title or 'congress' in title else 0.0
        features['is_primary'] = 1.0 if 'primary' in title else 0.0

        # Poll data (placeholder - would integrate real poll aggregators)
        features['poll_average'] = 0.5  # Would be actual poll average
        features['poll_volatility'] = 0.0  # Standard deviation of recent polls

        return features

    # ========================================================================
    # ECONOMICS FEATURES
    # ========================================================================

    def extract_economics_features(self, market: Dict, context: Dict) -> Dict[str, float]:
        """
        Extract economics-specific features

        Args:
            market: Market dictionary
            context: Context with indicators, etc.

        Returns:
            Dictionary of economics features
        """
        features = {}

        # Get FRED indicators
        indicators = context.get('indicators', ['UNRATE', 'CPIAUCSL'])

        for indicator in indicators:
            result = self.data_source_manager.get_fred_indicator(indicator)

            if result.success and result.data:
                indicator_name = indicator.lower()
                features[f'fred_{indicator_name}_value'] = result.data.get('latest_value', 0)
                features[f'fred_{indicator_name}_change'] = result.data.get('percent_change', 0) / 100
                features[f'fred_{indicator_name}_trend_up'] = 1.0 if result.data.get('trend') == 'up' else 0.0
            else:
                features[f'fred_{indicator}_value'] = 0.0
                features[f'fred_{indicator}_change'] = 0.0
                features[f'fred_{indicator}_trend_up'] = 0.0

        # Market indices (SPY, VIX)
        indices = context.get('indices', ['SPY', '^VIX'])

        for index in indices:
            result = self.data_source_manager.get_market_data(index)

            if result.success and result.data:
                index_name = index.replace('^', '').lower()
                features[f'market_{index_name}_change'] = result.data.get('percent_change', 0) / 100
                features[f'market_{index_name}_volatility'] = result.data.get('volatility', 0) / 100
            else:
                index_name = index.replace('^', '').lower()
                features[f'market_{index_name}_change'] = 0.0
                features[f'market_{index_name}_volatility'] = 0.0

        # Market type indicators
        title = market.get('title', '').lower()
        features['is_gdp_market'] = 1.0 if 'gdp' in title else 0.0
        features['is_inflation_market'] = 1.0 if 'inflation' in title or 'cpi' in title else 0.0
        features['is_employment_market'] = 1.0 if 'employment' in title or 'unemployment' in title else 0.0
        features['is_fed_market'] = 1.0 if 'fed' in title or 'interest rate' in title else 0.0

        return features

    # ========================================================================
    # CRYPTO FEATURES
    # ========================================================================

    def extract_crypto_features(self, market: Dict, context: Dict) -> Dict[str, float]:
        """
        Extract crypto-specific features

        Args:
            market: Market dictionary
            context: Context with coins, etc.

        Returns:
            Dictionary of crypto features
        """
        features = {}

        # Get crypto data
        coins = context.get('coins', ['bitcoin'])

        for coin in coins:
            result = self.data_source_manager.get_crypto_data(coin)

            if result.success and result.data:
                coin_name = coin.lower()
                features[f'crypto_{coin_name}_price'] = result.data.get('current_price', 0)
                features[f'crypto_{coin_name}_change_24h'] = result.data.get('price_change_24h', 0) / 100
                features[f'crypto_{coin_name}_change_7d'] = result.data.get('price_change_7d', 0) / 100
                features[f'crypto_{coin_name}_volume'] = np.log1p(result.data.get('total_volume', 0))
            else:
                coin_name = coin.lower()
                features[f'crypto_{coin_name}_price'] = 0.0
                features[f'crypto_{coin_name}_change_24h'] = 0.0
                features[f'crypto_{coin_name}_change_7d'] = 0.0
                features[f'crypto_{coin_name}_volume'] = 0.0

        # Get Reddit crypto sentiment
        keywords = context.get('keywords', ['bitcoin'])

        sentiment_result = self.data_source_manager.get_reddit_sentiment(
            subreddit='cryptocurrency',
            keywords=keywords,
            limit=100
        )

        if sentiment_result.success:
            features['crypto_sentiment'] = sentiment_result.data.get('sentiment_score', 50.0) / 100
            features['crypto_engagement'] = min(sentiment_result.data.get('engagement', 0) / 100, 1.0)
        else:
            features['crypto_sentiment'] = 0.5
            features['crypto_engagement'] = 0.0

        # Market type indicators
        title = market.get('title', '').lower()
        features['is_bitcoin_market'] = 1.0 if 'bitcoin' in title or 'btc' in title else 0.0
        features['is_ethereum_market'] = 1.0 if 'ethereum' in title or 'eth' in title else 0.0
        features['is_price_target_market'] = 1.0 if 'reach' in title or 'above' in title or 'below' in title else 0.0

        return features

    # ========================================================================
    # MAIN FEATURE EXTRACTION
    # ========================================================================

    def extract_features(self, market: Dict, sector: MarketSector,
                        context: Optional[Dict] = None) -> Dict[str, float]:
        """
        Extract all features for a market

        Args:
            market: Market dictionary
            sector: Market sector
            context: Optional context with additional info

        Returns:
            Dictionary of all features
        """
        if context is None:
            context = {}

        features = {}

        # Common features (all sectors)
        features.update(self.extract_price_history_features(market))
        features.update(self.extract_volume_features(market))
        features.update(self.extract_time_features(market))

        # Sector-specific features
        if sector == MarketSector.SPORTS:
            features.update(self.extract_sports_features(market, context))

        elif sector == MarketSector.POLITICS:
            features.update(self.extract_politics_features(market, context))

        elif sector == MarketSector.ECONOMICS:
            features.update(self.extract_economics_features(market, context))

        elif sector == MarketSector.CRYPTO:
            features.update(self.extract_crypto_features(market, context))

        # Fill any NaN values with 0
        for key, value in features.items():
            if pd.isna(value) or not np.isfinite(value):
                features[key] = 0.0

        return features

    def create_feature_dataframe(self, markets: List[Dict], sector: MarketSector,
                                contexts: Optional[List[Dict]] = None) -> pd.DataFrame:
        """
        Create feature dataframe for multiple markets

        Args:
            markets: List of market dictionaries
            sector: Market sector
            contexts: Optional list of context dictionaries (same length as markets)

        Returns:
            pandas DataFrame with features
        """
        if contexts is None:
            contexts = [{}] * len(markets)

        if len(markets) != len(contexts):
            raise ValueError("markets and contexts must have same length")

        feature_dicts = []

        for market, context in zip(markets, contexts):
            features = self.extract_features(market, sector, context)
            features['ticker'] = market.get('ticker', '')
            feature_dicts.append(features)

        df = pd.DataFrame(feature_dicts)

        # Move ticker to first column
        cols = ['ticker'] + [col for col in df.columns if col != 'ticker']
        df = df[cols]

        return df


# ============================================================================
# USAGE EXAMPLE
# ============================================================================

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    # Test feature engineering
    feature_eng = FeatureEngineering()

    test_market = {
        'ticker': 'TEST-NFL-001',
        'title': 'Will the Chiefs win the Super Bowl?',
        'yes_price': 0.45,
        'no_price': 0.55,
        'volume': 75000,
        'open_interest': 8000,
        'close_time': (datetime.now() + timedelta(hours=36)).isoformat(),
        'home_team': 'Chiefs',
        'away_team': 'Bills'
    }

    test_context = {
        'sport': 'nfl',
        'keywords': ['chiefs', 'super bowl']
    }

    print("\n" + "="*80)
    print("FEATURE ENGINEERING TEST")
    print("="*80)

    features = feature_eng.extract_features(test_market, MarketSector.SPORTS, test_context)

    print(f"\nExtracted {len(features)} features:")
    print("\nPrice Features:")
    for key in ['yes_price', 'no_price', 'price_spread', 'price_efficiency']:
        if key in features:
            print(f"  {key}: {features[key]:.4f}")

    print("\nVolume Features:")
    for key in ['volume_log', 'open_interest_log', 'liquidity_score']:
        if key in features:
            print(f"  {key}: {features[key]:.4f}")

    print("\nTime Features:")
    for key in ['hours_to_close', 'optimal_timing']:
        if key in features:
            print(f"  {key}: {features[key]:.4f}")

    print("\nSports Features:")
    for key in ['reddit_sentiment', 'is_playoff_game', 'home_team_popular']:
        if key in features:
            print(f"  {key}: {features[key]:.4f}")

    print("\n" + "="*80)
