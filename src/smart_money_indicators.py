"""
Smart Money Concepts (ICT) Indicators
Order Blocks, Fair Value Gaps, BOS/CHoCH, Liquidity Pools
"""

import pandas as pd
import numpy as np
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SmartMoneyIndicators:
    """
    Implements Inner Circle Trader (ICT) Smart Money Concepts:
    - Order Blocks (institutional entry points)
    - Fair Value Gaps (price imbalances)
    - Break of Structure / Change of Character
    - Liquidity Pools (stop loss clusters)
    """

    def __init__(
        self,
        swing_window: int = 5,
        min_fvg_pct: float = 0.1,
        min_liquidity_touches: int = 2
    ):
        """
        Initialize Smart Money Indicators

        Args:
            swing_window: Window for swing high/low detection
            min_fvg_pct: Minimum gap size for FVG (%)
            min_liquidity_touches: Minimum touches for liquidity pool
        """
        self.swing_window = swing_window
        self.min_fvg_pct = min_fvg_pct
        self.min_liquidity_touches = min_liquidity_touches

    def detect_order_blocks(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect Order Blocks (last candle before reversal)

        Bullish OB: Last down candle before strong rally
        Bearish OB: Last up candle before strong drop
        """
        order_blocks = []

        for i in range(2, len(df) - 1):
            # Bullish Order Block
            if (df['close'].iloc[i] < df['open'].iloc[i] and  # Red candle
                df['close'].iloc[i+1] > df['open'].iloc[i+1] and  # Next is green
                df['close'].iloc[i+1] > df['high'].iloc[i]):  # Breaks previous high

                strength = self._calculate_ob_strength(df, i, 'BULLISH')

                order_blocks.append({
                    'type': 'BULLISH_OB',
                    'top': float(df['high'].iloc[i]),
                    'bottom': float(df['low'].iloc[i]),
                    'midpoint': float((df['high'].iloc[i] + df['low'].iloc[i]) / 2),
                    'index': int(i),
                    'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None,
                    'strength': strength,
                    'volume': int(df['volume'].iloc[i]),
                    'mitigated': False
                })

            # Bearish Order Block
            elif (df['close'].iloc[i] > df['open'].iloc[i] and  # Green candle
                  df['close'].iloc[i+1] < df['open'].iloc[i+1] and  # Next is red
                  df['close'].iloc[i+1] < df['low'].iloc[i]):  # Breaks previous low

                strength = self._calculate_ob_strength(df, i, 'BEARISH')

                order_blocks.append({
                    'type': 'BEARISH_OB',
                    'top': float(df['high'].iloc[i]),
                    'bottom': float(df['low'].iloc[i]),
                    'midpoint': float((df['high'].iloc[i] + df['low'].iloc[i]) / 2),
                    'index': int(i),
                    'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None,
                    'strength': strength,
                    'volume': int(df['volume'].iloc[i]),
                    'mitigated': False
                })

        logger.info(f"Detected {len(order_blocks)} order blocks")
        return order_blocks

    def _calculate_ob_strength(self, df: pd.DataFrame, index: int, ob_type: str) -> int:
        """Calculate order block strength (0-100)"""
        strength = 50  # Base score

        # Volume factor
        avg_volume = df['volume'].iloc[max(0, index-20):index].mean()
        if avg_volume > 0:
            volume_ratio = df['volume'].iloc[index] / avg_volume
            strength += min(25, volume_ratio * 10)

        # Impulse strength
        if ob_type == 'BULLISH':
            impulse = (df['close'].iloc[index+1] - df['low'].iloc[index]) / df['low'].iloc[index]
        else:
            impulse = (df['high'].iloc[index] - df['close'].iloc[index+1]) / df['high'].iloc[index]

        strength += min(25, impulse * 1000)

        return min(100, int(strength))

    def detect_fair_value_gaps(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect Fair Value Gaps (price imbalances)

        Bullish FVG: Gap between high[i] and low[i+2]
        Bearish FVG: Gap between low[i] and high[i+2]
        """
        fvgs = []

        for i in range(len(df) - 2):
            # Bullish FVG (gap up)
            if df['low'].iloc[i+2] > df['high'].iloc[i]:
                gap_size = df['low'].iloc[i+2] - df['high'].iloc[i]
                gap_pct = (gap_size / df['close'].iloc[i]) * 100

                if gap_pct >= self.min_fvg_pct:
                    fvgs.append({
                        'type': 'BULLISH_FVG',
                        'top': float(df['low'].iloc[i+2]),
                        'bottom': float(df['high'].iloc[i]),
                        'midpoint': float((df['low'].iloc[i+2] + df['high'].iloc[i]) / 2),
                        'index': int(i),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None,
                        'gap_size': float(gap_size),
                        'gap_pct': float(gap_pct),
                        'filled': False,
                        'fill_percentage': 0.0
                    })

            # Bearish FVG (gap down)
            elif df['high'].iloc[i+2] < df['low'].iloc[i]:
                gap_size = df['low'].iloc[i] - df['high'].iloc[i+2]
                gap_pct = (gap_size / df['close'].iloc[i]) * 100

                if gap_pct >= self.min_fvg_pct:
                    fvgs.append({
                        'type': 'BEARISH_FVG',
                        'top': float(df['low'].iloc[i]),
                        'bottom': float(df['high'].iloc[i+2]),
                        'midpoint': float((df['low'].iloc[i] + df['high'].iloc[i+2]) / 2),
                        'index': int(i),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None,
                        'gap_size': float(gap_size),
                        'gap_pct': float(gap_pct),
                        'filled': False,
                        'fill_percentage': 0.0
                    })

        # Check which FVGs have been filled
        for fvg in fvgs:
            fvg['filled'], fvg['fill_percentage'] = self._check_fvg_filled(df, fvg)

        logger.info(f"Detected {len(fvgs)} fair value gaps")
        return fvgs

    def _check_fvg_filled(self, df: pd.DataFrame, fvg: Dict) -> Tuple[bool, float]:
        """Check if FVG has been filled by subsequent price action"""
        start_idx = fvg['index'] + 3

        if start_idx >= len(df):
            return False, 0.0

        subsequent_prices = df.iloc[start_idx:]
        gap_size = fvg['top'] - fvg['bottom']

        if fvg['type'] == 'BULLISH_FVG':
            # Check if price came back down into gap
            lowest_reentry = subsequent_prices['low'].min()
            if lowest_reentry <= fvg['top']:
                fill_amount = fvg['top'] - max(lowest_reentry, fvg['bottom'])
                fill_pct = (fill_amount / gap_size) * 100
                return fill_pct >= 50, fill_pct
        else:  # BEARISH_FVG
            # Check if price came back up into gap
            highest_reentry = subsequent_prices['high'].max()
            if highest_reentry >= fvg['bottom']:
                fill_amount = min(highest_reentry, fvg['top']) - fvg['bottom']
                fill_pct = (fill_amount / gap_size) * 100
                return fill_pct >= 50, fill_pct

        return False, 0.0

    def detect_market_structure(self, df: pd.DataFrame) -> Dict:
        """
        Detect Break of Structure (BOS) and Change of Character (CHoCH)

        BOS: Price breaks previous high/low in trend direction
        CHoCH: Price breaks structure against trend (reversal signal)
        """
        swing_highs = self._find_swing_highs(df)
        swing_lows = self._find_swing_lows(df)

        if len(swing_highs) < 3 or len(swing_lows) < 3:
            return {'bos': [], 'choch': [], 'current_trend': 'NEUTRAL'}

        structure_breaks = []
        current_trend = self._determine_trend(df, swing_highs, swing_lows)

        for i in range(len(df)):
            if i < self.swing_window:
                continue

            current_price = df['close'].iloc[i]

            if current_trend == 'BULLISH':
                # Look for BOS (break above previous high)
                recent_highs = [h['price'] for h in swing_highs if h['index'] < i]
                if recent_highs and current_price > max(recent_highs[-3:]):
                    structure_breaks.append({
                        'type': 'BOS',
                        'direction': 'BULLISH',
                        'price': float(current_price),
                        'index': int(i),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None
                    })

                # Look for CHoCH (break below recent low = reversal)
                recent_lows = [l['price'] for l in swing_lows if l['index'] < i]
                if recent_lows and current_price < min(recent_lows[-3:]):
                    structure_breaks.append({
                        'type': 'CHOCH',
                        'direction': 'BEARISH',
                        'price': float(current_price),
                        'index': int(i),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None
                    })
                    current_trend = 'BEARISH'

            elif current_trend == 'BEARISH':
                # Look for BOS (break below previous low)
                recent_lows = [l['price'] for l in swing_lows if l['index'] < i]
                if recent_lows and current_price < min(recent_lows[-3:]):
                    structure_breaks.append({
                        'type': 'BOS',
                        'direction': 'BEARISH',
                        'price': float(current_price),
                        'index': int(i),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None
                    })

                # Look for CHoCH (break above recent high = reversal)
                recent_highs = [h['price'] for h in swing_highs if h['index'] < i]
                if recent_highs and current_price > max(recent_highs[-3:]):
                    structure_breaks.append({
                        'type': 'CHOCH',
                        'direction': 'BULLISH',
                        'price': float(current_price),
                        'index': int(i),
                        'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None
                    })
                    current_trend = 'BULLISH'

        logger.info(f"Detected {len(structure_breaks)} structure breaks")

        return {
            'bos': [s for s in structure_breaks if s['type'] == 'BOS'],
            'choch': [s for s in structure_breaks if s['type'] == 'CHOCH'],
            'current_trend': current_trend,
            'swing_highs': swing_highs,
            'swing_lows': swing_lows
        }

    def detect_liquidity_pools(self, df: pd.DataFrame) -> List[Dict]:
        """
        Detect liquidity pools (stop loss clusters)

        Buy-side liquidity: Above recent swing highs
        Sell-side liquidity: Below recent swing lows
        """
        swing_highs = self._find_swing_highs(df)
        swing_lows = self._find_swing_lows(df)

        liquidity_pools = []

        # Buy-side liquidity (above highs)
        for high in swing_highs:
            # Check if multiple highs cluster nearby (within 2%)
            nearby_highs = [h for h in swing_highs
                           if abs(h['price'] - high['price']) / high['price'] < 0.02]

            if len(nearby_highs) >= self.min_liquidity_touches:
                liquidity_pools.append({
                    'type': 'BUY_SIDE_LIQUIDITY',
                    'price': float(high['price']),
                    'touches': len(nearby_highs),
                    'strength': len(nearby_highs) * 10,
                    'swept': False,
                    'indices': [h['index'] for h in nearby_highs]
                })

        # Sell-side liquidity (below lows)
        for low in swing_lows:
            nearby_lows = [l for l in swing_lows
                          if abs(l['price'] - low['price']) / low['price'] < 0.02]

            if len(nearby_lows) >= self.min_liquidity_touches:
                liquidity_pools.append({
                    'type': 'SELL_SIDE_LIQUIDITY',
                    'price': float(low['price']),
                    'touches': len(nearby_lows),
                    'strength': len(nearby_lows) * 10,
                    'swept': False,
                    'indices': [l['index'] for l in nearby_lows]
                })

        # Check which pools have been swept
        for pool in liquidity_pools:
            pool['swept'] = self._check_liquidity_swept(df, pool)

        logger.info(f"Detected {len(liquidity_pools)} liquidity pools")
        return liquidity_pools

    def _check_liquidity_swept(self, df: pd.DataFrame, pool: Dict) -> bool:
        """Check if liquidity has been swept"""
        max_index = max(pool['indices'])
        if max_index >= len(df) - 1:
            return False

        subsequent_prices = df.iloc[max_index + 1:]

        if pool['type'] == 'BUY_SIDE_LIQUIDITY':
            # Check if price swept above
            return subsequent_prices['high'].max() > pool['price'] * 1.001
        else:
            # Check if price swept below
            return subsequent_prices['low'].min() < pool['price'] * 0.999

    def _find_swing_highs(self, df: pd.DataFrame) -> List[Dict]:
        """Find swing highs (local maxima)"""
        swing_highs = []

        for i in range(self.swing_window, len(df) - self.swing_window):
            is_swing_high = True

            # Check if highest in window
            for j in range(i - self.swing_window, i + self.swing_window + 1):
                if j != i and df['high'].iloc[j] >= df['high'].iloc[i]:
                    is_swing_high = False
                    break

            if is_swing_high:
                swing_highs.append({
                    'price': float(df['high'].iloc[i]),
                    'index': int(i),
                    'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None
                })

        return swing_highs

    def _find_swing_lows(self, df: pd.DataFrame) -> List[Dict]:
        """Find swing lows (local minima)"""
        swing_lows = []

        for i in range(self.swing_window, len(df) - self.swing_window):
            is_swing_low = True

            # Check if lowest in window
            for j in range(i - self.swing_window, i + self.swing_window + 1):
                if j != i and df['low'].iloc[j] <= df['low'].iloc[i]:
                    is_swing_low = False
                    break

            if is_swing_low:
                swing_lows.append({
                    'price': float(df['low'].iloc[i]),
                    'index': int(i),
                    'timestamp': df.index[i] if hasattr(df.index[i], 'strftime') else None
                })

        return swing_lows

    def _determine_trend(self, df: pd.DataFrame, swing_highs: List[Dict], swing_lows: List[Dict]) -> str:
        """Determine current market trend"""
        if len(swing_highs) < 2 or len(swing_lows) < 2:
            return 'NEUTRAL'

        # Check recent swing highs
        recent_highs = swing_highs[-3:]
        recent_lows = swing_lows[-3:]

        # Bullish: Higher highs and higher lows
        if all(recent_highs[i]['price'] < recent_highs[i+1]['price'] for i in range(len(recent_highs)-1)):
            if all(recent_lows[i]['price'] < recent_lows[i+1]['price'] for i in range(len(recent_lows)-1)):
                return 'BULLISH'

        # Bearish: Lower highs and lower lows
        if all(recent_highs[i]['price'] > recent_highs[i+1]['price'] for i in range(len(recent_highs)-1)):
            if all(recent_lows[i]['price'] > recent_lows[i+1]['price'] for i in range(len(recent_lows)-1)):
                return 'BEARISH'

        return 'NEUTRAL'

    def get_all_smc_indicators(self, df: pd.DataFrame) -> Dict:
        """Get all Smart Money Concepts indicators at once"""
        return {
            'order_blocks': self.detect_order_blocks(df),
            'fair_value_gaps': self.detect_fair_value_gaps(df),
            'market_structure': self.detect_market_structure(df),
            'liquidity_pools': self.detect_liquidity_pools(df)
        }


if __name__ == "__main__":
    # Test
    import yfinance as yf
    logging.basicConfig(level=logging.INFO)

    print("Testing Smart Money Indicators with AAPL...")

    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo", interval="1d")
    df = df.reset_index()

    smc = SmartMoneyIndicators()
    indicators = smc.get_all_smc_indicators(df)

    print(f"\nOrder Blocks: {len(indicators['order_blocks'])}")
    print(f"Fair Value Gaps: {len(indicators['fair_value_gaps'])}")
    print(f"BOS: {len(indicators['market_structure']['bos'])}")
    print(f"CHoCH: {len(indicators['market_structure']['choch'])}")
    print(f"Current Trend: {indicators['market_structure']['current_trend']}")
    print(f"Liquidity Pools: {len(indicators['liquidity_pools'])}")
