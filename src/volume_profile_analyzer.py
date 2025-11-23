"""
Volume Profile Analysis
POC, Value Area, High/Low Volume Nodes
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)


class VolumeProfileAnalyzer:
    """
    Volume Profile Analysis - price-based volume distribution

    Key metrics:
    - POC (Point of Control): Price with highest volume
    - Value Area: Range containing 70% of volume
    - HVN/LVN: High and Low Volume Nodes
    """

    def __init__(
        self,
        price_bins: int = 50,
        value_area_pct: float = 0.70,
        hvn_threshold: float = 1.5,
        lvn_threshold: float = 0.5
    ):
        """
        Initialize Volume Profile Analyzer

        Args:
            price_bins: Number of price levels to analyze
            value_area_pct: Percentage for value area (default: 70%)
            hvn_threshold: Threshold multiplier for HVN (std devs)
            lvn_threshold: Threshold multiplier for LVN (std devs)
        """
        self.price_bins = price_bins
        self.value_area_pct = value_area_pct
        self.hvn_threshold = hvn_threshold
        self.lvn_threshold = lvn_threshold

    def calculate_volume_profile(self, df: pd.DataFrame) -> Dict:
        """
        Calculate complete volume profile

        Returns:
            Dictionary with POC, VAH, VAL, and volume distribution
        """
        if len(df) == 0:
            return self._empty_profile()

        # Create price bins
        price_min = df['low'].min()
        price_max = df['high'].max()
        price_range = price_max - price_min

        if price_range == 0:
            return self._empty_profile()

        bin_size = price_range / self.price_bins

        # Allocate volume to price bins
        volume_by_price = {}

        for i in range(len(df)):
            candle_low = df['low'].iloc[i]
            candle_high = df['high'].iloc[i]
            candle_volume = df['volume'].iloc[i]

            # Find which bins this candle touches
            bins_touched = []
            for bin_num in range(self.price_bins):
                bin_bottom = price_min + (bin_num * bin_size)
                bin_top = bin_bottom + bin_size

                # Check if candle overlaps this bin
                if candle_high >= bin_bottom and candle_low <= bin_top:
                    bins_touched.append(bin_num)

            # Distribute volume evenly across touched bins
            if bins_touched:
                volume_per_bin = candle_volume / len(bins_touched)
                for bin_num in bins_touched:
                    bin_price = price_min + (bin_num * bin_size) + (bin_size / 2)
                    volume_by_price[bin_price] = volume_by_price.get(bin_price, 0) + volume_per_bin

        if not volume_by_price:
            return self._empty_profile()

        # Find POC (highest volume)
        poc_price = max(volume_by_price, key=volume_by_price.get)
        poc_volume = volume_by_price[poc_price]

        # Calculate Value Area (70% of volume)
        total_volume = sum(volume_by_price.values())
        value_area_volume = total_volume * self.value_area_pct

        # Start from POC and expand until we have 70% of volume
        sorted_prices = sorted(volume_by_price.keys(),
                              key=lambda p: volume_by_price[p],
                              reverse=True)

        va_volume = 0
        va_prices = []

        for price in sorted_prices:
            va_prices.append(price)
            va_volume += volume_by_price[price]
            if va_volume >= value_area_volume:
                break

        vah = max(va_prices)  # Value Area High
        val = min(va_prices)  # Value Area Low

        logger.info(f"Volume Profile calculated: POC=${poc_price:.2f}, VA=[${val:.2f}, ${vah:.2f}]")

        return {
            'poc': float(poc_price),
            'poc_volume': float(poc_volume),
            'vah': float(vah),
            'val': float(val),
            'value_area_volume': float(va_volume),
            'total_volume': float(total_volume),
            'volume_by_price': {float(k): float(v) for k, v in volume_by_price.items()},
            'price_bins': self.price_bins,
            'bin_size': float(bin_size)
        }

    def identify_volume_nodes(self, volume_profile: Dict) -> Dict:
        """
        Identify High Volume Nodes (HVN) and Low Volume Nodes (LVN)

        HVN = Strong support/resistance (lots of trading)
        LVN = Weak areas (price moves through quickly)
        """
        if not volume_profile or 'volume_by_price' not in volume_profile:
            return {'hvn': [], 'lvn': []}

        volume_data = volume_profile['volume_by_price']
        volumes = list(volume_data.values())

        if not volumes:
            return {'hvn': [], 'lvn': []}

        # Calculate statistics
        avg_volume = sum(volumes) / len(volumes)
        variance = sum((v - avg_volume)**2 for v in volumes) / len(volumes)
        std_volume = variance ** 0.5

        hvn_threshold = avg_volume + (std_volume * self.hvn_threshold)
        lvn_threshold = avg_volume - (std_volume * self.lvn_threshold)

        hvn = []  # High Volume Nodes
        lvn = []  # Low Volume Nodes

        for price, volume in volume_data.items():
            if volume >= hvn_threshold:
                hvn.append({
                    'price': float(price),
                    'volume': float(volume),
                    'type': 'HVN',
                    'strength': int((volume / avg_volume) * 50)
                })
            elif volume <= lvn_threshold:
                lvn.append({
                    'price': float(price),
                    'volume': float(volume),
                    'type': 'LVN',
                    'strength': int((volume / avg_volume) * 50)
                })

        # Sort by price
        hvn.sort(key=lambda x: x['price'])
        lvn.sort(key=lambda x: x['price'])

        logger.info(f"Identified {len(hvn)} HVN and {len(lvn)} LVN")

        return {'hvn': hvn, 'lvn': lvn}

    def get_volume_at_price(self, volume_profile: Dict, price: float, tolerance: float = 0.01) -> float:
        """
        Get volume at specific price (within tolerance %)

        Args:
            volume_profile: Volume profile dict
            price: Target price
            tolerance: Price tolerance as percentage

        Returns:
            Volume at that price level
        """
        if not volume_profile or 'volume_by_price' not in volume_profile:
            return 0.0

        volume_data = volume_profile['volume_by_price']

        # Find closest price within tolerance
        for vp_price, volume in volume_data.items():
            if abs(vp_price - price) / price <= tolerance:
                return float(volume)

        return 0.0

    def is_near_poc(self, price: float, volume_profile: Dict, tolerance_pct: float = 2.0) -> bool:
        """Check if price is near POC (within tolerance %)"""
        if not volume_profile or 'poc' not in volume_profile:
            return False

        poc = volume_profile['poc']
        distance_pct = abs(price - poc) / poc * 100

        return distance_pct <= tolerance_pct

    def is_in_value_area(self, price: float, volume_profile: Dict) -> bool:
        """Check if price is within value area"""
        if not volume_profile or 'val' not in volume_profile or 'vah' not in volume_profile:
            return False

        return volume_profile['val'] <= price <= volume_profile['vah']

    def is_at_hvn(self, price: float, volume_nodes: Dict, tolerance_pct: float = 1.0) -> bool:
        """Check if price is at a High Volume Node"""
        if not volume_nodes or 'hvn' not in volume_nodes:
            return False

        for hvn in volume_nodes['hvn']:
            distance_pct = abs(price - hvn['price']) / price * 100
            if distance_pct <= tolerance_pct:
                return True

        return False

    def is_at_lvn(self, price: float, volume_nodes: Dict, tolerance_pct: float = 1.0) -> bool:
        """Check if price is at a Low Volume Node"""
        if not volume_nodes or 'lvn' not in volume_nodes:
            return False

        for lvn in volume_nodes['lvn']:
            distance_pct = abs(price - lvn['price']) / price * 100
            if distance_pct <= tolerance_pct:
                return True

        return False

    def calculate_rolling_volume_profile(
        self,
        df: pd.DataFrame,
        window: int = 50
    ) -> List[Dict]:
        """
        Calculate rolling volume profile (moving window)

        Useful for dynamic POC tracking

        Args:
            df: Price data
            window: Rolling window size

        Returns:
            List of volume profiles over time
        """
        profiles = []

        for i in range(window, len(df)):
            window_df = df.iloc[i-window:i]
            profile = self.calculate_volume_profile(window_df)
            profile['index'] = i
            profile['timestamp'] = df.index[i] if hasattr(df.index[i], 'strftime') else None
            profiles.append(profile)

        logger.info(f"Calculated {len(profiles)} rolling volume profiles")
        return profiles

    def _empty_profile(self) -> Dict:
        """Return empty volume profile"""
        return {
            'poc': 0.0,
            'poc_volume': 0.0,
            'vah': 0.0,
            'val': 0.0,
            'value_area_volume': 0.0,
            'total_volume': 0.0,
            'volume_by_price': {},
            'price_bins': 0,
            'bin_size': 0.0
        }

    def get_complete_analysis(self, df: pd.DataFrame) -> Dict:
        """Get complete volume profile analysis"""
        volume_profile = self.calculate_volume_profile(df)
        volume_nodes = self.identify_volume_nodes(volume_profile)

        return {
            'volume_profile': volume_profile,
            'volume_nodes': volume_nodes,
            'poc': volume_profile['poc'],
            'vah': volume_profile['vah'],
            'val': volume_profile['val'],
            'hvn': volume_nodes['hvn'],
            'lvn': volume_nodes['lvn']
        }


if __name__ == "__main__":
    # Test
    import yfinance as yf
    logging.basicConfig(level=logging.INFO)

    print("Testing Volume Profile Analyzer with AAPL...")

    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo", interval="1d")

    vpa = VolumeProfileAnalyzer()
    analysis = vpa.get_complete_analysis(df)

    print(f"\nPOC: ${analysis['poc']:.2f}")
    print(f"Value Area: ${analysis['val']:.2f} - ${analysis['vah']:.2f}")
    print(f"High Volume Nodes: {len(analysis['hvn'])}")
    print(f"Low Volume Nodes: {len(analysis['lvn'])}")

    print("\nTop 5 High Volume Nodes:")
    for i, hvn in enumerate(analysis['hvn'][:5], 1):
        print(f"  {i}. ${hvn['price']:.2f} (Strength: {hvn['strength']})")
