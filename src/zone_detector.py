"""
Supply/Demand Zone Detection
Identifies high-probability supply and demand zones using swing point analysis
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging
from scipy.signal import find_peaks

logger = logging.getLogger(__name__)


class ZoneDetector:
    """
    Detects supply and demand zones from price action

    Supply zones (sell/resistance) form at swing highs with strong selling pressure
    Demand zones (buy/support) form at swing lows with strong buying pressure
    """

    def __init__(
        self,
        lookback_periods: int = 100,
        swing_strength: int = 5,
        min_zone_size_pct: float = 0.3,  # Relaxed from 0.5 to detect more zones
        max_zone_size_pct: float = 10.0,  # Increased from 5.0 for wider zones
        min_volume_ratio: float = 1.2  # Lowered from 1.5 for more sensitivity
    ):
        """
        Initialize zone detector

        Args:
            lookback_periods: Number of candles to analyze (default: 100)
            swing_strength: Number of candles each side for swing detection (default: 5)
            min_zone_size_pct: Minimum zone size as % of price (default: 0.5%)
            max_zone_size_pct: Maximum zone size as % of price (default: 5.0%)
            min_volume_ratio: Minimum departure/approach volume ratio (default: 1.5)
        """
        self.lookback_periods = lookback_periods
        self.swing_strength = swing_strength
        self.min_zone_size_pct = min_zone_size_pct
        self.max_zone_size_pct = max_zone_size_pct
        self.min_volume_ratio = min_volume_ratio

    def detect_zones(
        self,
        df: pd.DataFrame,
        symbol: str
    ) -> List[Dict]:
        """
        Detect supply and demand zones from OHLCV data

        Args:
            df: DataFrame with columns: open, high, low, close, volume, timestamp
            symbol: Stock ticker symbol

        Returns:
            List of zone dictionaries with boundaries, type, and metadata
        """
        if len(df) < self.lookback_periods:
            logger.warning(f"{symbol}: Not enough data ({len(df)} < {self.lookback_periods})")
            return []

        # Use last N periods
        df = df.tail(self.lookback_periods).copy()
        df = df.reset_index(drop=True)

        zones = []

        # Detect demand zones (at swing lows)
        demand_zones = self._detect_demand_zones(df, symbol)
        zones.extend(demand_zones)

        # Detect supply zones (at swing highs)
        supply_zones = self._detect_supply_zones(df, symbol)
        zones.extend(supply_zones)

        # Filter overlapping zones (keep strongest)
        zones = self._filter_overlapping_zones(zones)

        logger.info(f"{symbol}: Detected {len(zones)} zones ({len(demand_zones)} demand, {len(supply_zones)} supply)")

        return zones

    def _detect_demand_zones(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """Detect demand zones at swing lows"""

        # Find swing lows using scipy
        lows = df['low'].values
        peaks, properties = find_peaks(-lows, distance=self.swing_strength)

        if len(peaks) == 0:
            return []

        zones = []

        for peak_idx in peaks:
            # Skip if too close to edges
            if peak_idx < self.swing_strength or peak_idx >= len(df) - self.swing_strength:
                continue

            zone = self._analyze_demand_zone(df, peak_idx, symbol)
            if zone:
                zones.append(zone)

        return zones

    def _detect_supply_zones(self, df: pd.DataFrame, symbol: str) -> List[Dict]:
        """Detect supply zones at swing highs"""

        # Find swing highs using scipy
        highs = df['high'].values
        peaks, properties = find_peaks(highs, distance=self.swing_strength)

        if len(peaks) == 0:
            return []

        zones = []

        for peak_idx in peaks:
            # Skip if too close to edges
            if peak_idx < self.swing_strength or peak_idx >= len(df) - self.swing_strength:
                continue

            zone = self._analyze_supply_zone(df, peak_idx, symbol)
            if zone:
                zones.append(zone)

        return zones

    def _analyze_demand_zone(
        self,
        df: pd.DataFrame,
        swing_idx: int,
        symbol: str
    ) -> Optional[Dict]:
        """
        Analyze potential demand zone at swing low

        Demand zones form when:
        1. Price consolidates (tight range)
        2. Then explodes upward (strong buying)
        3. Volume on departure > volume on approach
        """

        # Find consolidation area before swing (approach)
        consolidation = self._find_consolidation(df, swing_idx, direction='before')
        if not consolidation:
            return None

        start_idx, end_idx = consolidation

        # Zone boundaries (base of consolidation)
        zone_bottom = df.loc[start_idx:end_idx, 'low'].min()
        zone_top = df.loc[start_idx:end_idx, 'high'].max()
        zone_midpoint = (zone_top + zone_bottom) / 2

        # Validate zone size
        zone_size_pct = ((zone_top - zone_bottom) / zone_bottom) * 100
        if zone_size_pct < self.min_zone_size_pct or zone_size_pct > self.max_zone_size_pct:
            return None

        # Calculate volume metrics
        approach_volume = df.loc[start_idx:end_idx, 'volume'].sum()

        # Find departure (impulse move up)
        departure_end = min(end_idx + 10, len(df) - 1)
        departure_volume = df.loc[end_idx:departure_end, 'volume'].sum()

        volume_ratio = departure_volume / approach_volume if approach_volume > 0 else 0

        # Require strong volume on departure
        if volume_ratio < self.min_volume_ratio:
            return None

        # Calculate impulse move strength
        departure_price = df.loc[departure_end, 'close']
        impulse_pct = ((departure_price - zone_top) / zone_top) * 100

        # Require meaningful impulse (at least 1x zone height, relaxed from 2x)
        if impulse_pct < zone_size_pct * 1.0:
            return None

        # Calculate initial strength score (will be refined by ZoneAnalyzer)
        strength_score = min(100, int(
            (volume_ratio * 20) +  # Volume contribution
            (impulse_pct * 5) +     # Impulse contribution
            30                      # Base score for fresh zone
        ))

        # Build zone dictionary
        zone = {
            'symbol': symbol,
            'zone_type': 'DEMAND',
            'zone_top': float(zone_top),
            'zone_bottom': float(zone_bottom),
            'zone_midpoint': float(zone_midpoint),
            'formed_date': df.loc[end_idx, 'timestamp'] if 'timestamp' in df.columns else datetime.now(),
            'formation_candle_index': int(end_idx),
            'approach_volume': int(approach_volume),
            'departure_volume': int(departure_volume),
            'volume_ratio': float(volume_ratio),
            'strength_score': strength_score,
            'time_at_zone': int(end_idx - start_idx + 1),
            'status': 'FRESH',
            'test_count': 0,
            'is_active': True,
            'notes': f'Swing low at index {swing_idx}, impulse: {impulse_pct:.1f}%'
        }

        return zone

    def _analyze_supply_zone(
        self,
        df: pd.DataFrame,
        swing_idx: int,
        symbol: str
    ) -> Optional[Dict]:
        """
        Analyze potential supply zone at swing high

        Supply zones form when:
        1. Price consolidates (tight range)
        2. Then drops sharply (strong selling)
        3. Volume on departure > volume on approach
        """

        # Find consolidation area before swing (approach)
        consolidation = self._find_consolidation(df, swing_idx, direction='before')
        if not consolidation:
            return None

        start_idx, end_idx = consolidation

        # Zone boundaries (top of consolidation)
        zone_bottom = df.loc[start_idx:end_idx, 'low'].min()
        zone_top = df.loc[start_idx:end_idx, 'high'].max()
        zone_midpoint = (zone_top + zone_bottom) / 2

        # Validate zone size
        zone_size_pct = ((zone_top - zone_bottom) / zone_bottom) * 100
        if zone_size_pct < self.min_zone_size_pct or zone_size_pct > self.max_zone_size_pct:
            return None

        # Calculate volume metrics
        approach_volume = df.loc[start_idx:end_idx, 'volume'].sum()

        # Find departure (impulse move down)
        departure_end = min(end_idx + 10, len(df) - 1)
        departure_volume = df.loc[end_idx:departure_end, 'volume'].sum()

        volume_ratio = departure_volume / approach_volume if approach_volume > 0 else 0

        # Require strong volume on departure
        if volume_ratio < self.min_volume_ratio:
            return None

        # Calculate impulse move strength
        departure_price = df.loc[departure_end, 'close']
        impulse_pct = ((zone_bottom - departure_price) / zone_bottom) * 100

        # Require meaningful impulse (at least 1x zone height, relaxed from 2x)
        if impulse_pct < zone_size_pct * 1.0:
            return None

        # Calculate initial strength score
        strength_score = min(100, int(
            (volume_ratio * 20) +  # Volume contribution
            (impulse_pct * 5) +     # Impulse contribution
            30                      # Base score for fresh zone
        ))

        # Build zone dictionary
        zone = {
            'symbol': symbol,
            'zone_type': 'SUPPLY',
            'zone_top': float(zone_top),
            'zone_bottom': float(zone_bottom),
            'zone_midpoint': float(zone_midpoint),
            'formed_date': df.loc[end_idx, 'timestamp'] if 'timestamp' in df.columns else datetime.now(),
            'formation_candle_index': int(end_idx),
            'approach_volume': int(approach_volume),
            'departure_volume': int(departure_volume),
            'volume_ratio': float(volume_ratio),
            'strength_score': strength_score,
            'time_at_zone': int(end_idx - start_idx + 1),
            'status': 'FRESH',
            'test_count': 0,
            'is_active': True,
            'notes': f'Swing high at index {swing_idx}, impulse: {impulse_pct:.1f}%'
        }

        return zone

    def _find_consolidation(
        self,
        df: pd.DataFrame,
        swing_idx: int,
        direction: str = 'before',
        max_candles: int = 10
    ) -> Optional[Tuple[int, int]]:
        """
        Find consolidation area (tight price range) near swing point

        Args:
            df: Price data
            swing_idx: Index of swing point
            direction: 'before' or 'after' swing point
            max_candles: Maximum consolidation length

        Returns:
            (start_idx, end_idx) or None
        """

        if direction == 'before':
            # Look backward from swing
            start_search = max(0, swing_idx - max_candles)
            end_search = swing_idx

            # Find tight consolidation
            for window_size in range(3, max_candles + 1):
                start = swing_idx - window_size
                if start < 0:
                    continue

                window = df.loc[start:swing_idx]
                high_range = window['high'].max() - window['low'].min()
                avg_price = window['close'].mean()

                # Tight consolidation: range < 5% of price (relaxed from 2%)
                if (high_range / avg_price) < 0.05:
                    return (start, swing_idx)

            # If no tight consolidation, use last 3-5 candles
            return (max(0, swing_idx - 5), swing_idx)

        else:
            # Look forward from swing
            start_search = swing_idx
            end_search = min(len(df) - 1, swing_idx + max_candles)

            for window_size in range(3, max_candles + 1):
                end = swing_idx + window_size
                if end >= len(df):
                    continue

                window = df.loc[swing_idx:end]
                high_range = window['high'].max() - window['low'].min()
                avg_price = window['close'].mean()

                # Relaxed from 0.02 (2%) to 0.05 (5%)
                if (high_range / avg_price) < 0.05:
                    return (swing_idx, end)

            return (swing_idx, min(len(df) - 1, swing_idx + 5))

    def _filter_overlapping_zones(self, zones: List[Dict]) -> List[Dict]:
        """
        Remove overlapping zones, keeping only the strongest

        Args:
            zones: List of zone dictionaries

        Returns:
            Filtered list with no overlaps
        """

        if len(zones) <= 1:
            return zones

        # Sort by strength score (highest first)
        zones_sorted = sorted(zones, key=lambda z: z['strength_score'], reverse=True)

        filtered = []

        for zone in zones_sorted:
            # Check if overlaps with any already-kept zone
            overlaps = False

            for kept_zone in filtered:
                # Zones overlap if they're the same type and ranges intersect
                if zone['zone_type'] == kept_zone['zone_type']:
                    if self._zones_overlap(zone, kept_zone):
                        overlaps = True
                        break

            if not overlaps:
                filtered.append(zone)

        return filtered

    def _zones_overlap(self, zone1: Dict, zone2: Dict) -> bool:
        """Check if two zones overlap"""

        # Zone 1 range
        z1_top = zone1['zone_top']
        z1_bottom = zone1['zone_bottom']

        # Zone 2 range
        z2_top = zone2['zone_top']
        z2_bottom = zone2['zone_bottom']

        # Check for overlap
        return not (z1_top < z2_bottom or z1_bottom > z2_top)


def detect_zones_for_symbol(
    symbol: str,
    df: pd.DataFrame,
    lookback_periods: int = 100
) -> List[Dict]:
    """
    Convenience function to detect zones for a single symbol

    Args:
        symbol: Stock ticker
        df: OHLCV DataFrame with columns: open, high, low, close, volume, timestamp
        lookback_periods: Number of candles to analyze

    Returns:
        List of detected zones
    """

    detector = ZoneDetector(lookback_periods=lookback_periods)
    return detector.detect_zones(df, symbol)


if __name__ == "__main__":
    # Test with sample data
    import yfinance as yf

    logging.basicConfig(level=logging.INFO)

    print("Testing ZoneDetector with AAPL...")

    # Fetch AAPL data
    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="6mo", interval="1d")
    df = df.reset_index()
    df.columns = [c.lower() for c in df.columns]
    df = df.rename(columns={'date': 'timestamp'})

    # Detect zones
    detector = ZoneDetector()
    zones = detector.detect_zones(df, "AAPL")

    print(f"\nDetected {len(zones)} zones:\n")

    for i, zone in enumerate(zones, 1):
        print(f"Zone {i}:")
        print(f"  Type: {zone['zone_type']}")
        print(f"  Range: ${zone['zone_bottom']:.2f} - ${zone['zone_top']:.2f}")
        print(f"  Strength: {zone['strength_score']}/100")
        print(f"  Volume Ratio: {zone['volume_ratio']:.2f}x")
        print(f"  Formed: {zone['formed_date']}")
        print()
