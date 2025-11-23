"""
Momentum and Trend Indicators
RSI, MACD, EMAs, ATR, CVD, Fibonacci
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class MomentumIndicators:
    """
    Momentum and trend indicators for confirmation

    Includes: RSI, MACD, EMAs, ATR, CVD, Fibonacci
    """

    def __init__(
        self,
        rsi_period: int = 14,
        macd_fast: int = 12,
        macd_slow: int = 26,
        macd_signal: int = 9,
        atr_period: int = 14
    ):
        """
        Initialize Momentum Indicators

        Args:
            rsi_period: RSI calculation period
            macd_fast: MACD fast EMA period
            macd_slow: MACD slow EMA period
            macd_signal: MACD signal line period
            atr_period: ATR calculation period
        """
        self.rsi_period = rsi_period
        self.macd_fast = macd_fast
        self.macd_slow = macd_slow
        self.macd_signal = macd_signal
        self.atr_period = atr_period

    def calculate_rsi(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate RSI (Relative Strength Index)

        RSI < 30 = Oversold (buy signal)
        RSI > 70 = Overbought (sell signal)
        """
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=self.rsi_period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=self.rsi_period).mean()

        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))

        logger.info(f"RSI calculated (current: {rsi.iloc[-1]:.1f})")
        return rsi

    def get_rsi_signal(self, rsi: pd.Series) -> Dict:
        """Get RSI signal and strength"""
        current_rsi = rsi.iloc[-1]

        if current_rsi < 30:
            return {'signal': 'OVERSOLD', 'strength': 'STRONG_BUY', 'value': float(current_rsi)}
        elif current_rsi < 40:
            return {'signal': 'OVERSOLD', 'strength': 'BUY', 'value': float(current_rsi)}
        elif current_rsi > 70:
            return {'signal': 'OVERBOUGHT', 'strength': 'STRONG_SELL', 'value': float(current_rsi)}
        elif current_rsi > 60:
            return {'signal': 'OVERBOUGHT', 'strength': 'SELL', 'value': float(current_rsi)}
        else:
            return {'signal': 'NEUTRAL', 'strength': 'NEUTRAL', 'value': float(current_rsi)}

    def calculate_macd(self, df: pd.DataFrame) -> Dict:
        """
        Calculate MACD (Moving Average Convergence Divergence)

        MACD line crosses above signal = Bullish
        MACD line crosses below signal = Bearish
        """
        ema_fast = df['close'].ewm(span=self.macd_fast, adjust=False).mean()
        ema_slow = df['close'].ewm(span=self.macd_slow, adjust=False).mean()

        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=self.macd_signal, adjust=False).mean()
        histogram = macd_line - signal_line

        logger.info(f"MACD calculated (histogram: {histogram.iloc[-1]:.2f})")

        return {
            'macd': macd_line,
            'signal': signal_line,
            'histogram': histogram
        }

    def get_macd_signal(self, macd: Dict) -> Dict:
        """Get MACD signal"""
        current_hist = macd['histogram'].iloc[-1]
        prev_hist = macd['histogram'].iloc[-2]

        # Bullish crossover
        if current_hist > 0 and prev_hist <= 0:
            return {'signal': 'BULLISH_CROSS', 'strength': 'BUY', 'histogram': float(current_hist)}
        # Bearish crossover
        elif current_hist < 0 and prev_hist >= 0:
            return {'signal': 'BEARISH_CROSS', 'strength': 'SELL', 'histogram': float(current_hist)}
        # Bullish continuation
        elif current_hist > 0:
            return {'signal': 'BULLISH', 'strength': 'HOLD', 'histogram': float(current_hist)}
        # Bearish continuation
        elif current_hist < 0:
            return {'signal': 'BEARISH', 'strength': 'AVOID', 'histogram': float(current_hist)}
        else:
            return {'signal': 'NEUTRAL', 'strength': 'NEUTRAL', 'histogram': float(current_hist)}

    def calculate_emas(self, df: pd.DataFrame) -> Dict:
        """
        Calculate key EMAs (20, 50, 200)

        Price above all EMAs = Strong bullish
        Price below all EMAs = Strong bearish
        """
        ema_20 = df['close'].ewm(span=20, adjust=False).mean()
        ema_50 = df['close'].ewm(span=50, adjust=False).mean()
        ema_200 = df['close'].ewm(span=200, adjust=False).mean()

        logger.info("EMAs calculated (20, 50, 200)")

        return {
            'ema_20': ema_20,
            'ema_50': ema_50,
            'ema_200': ema_200
        }

    def get_ema_alignment(self, emas: Dict, current_price: float) -> Dict:
        """
        Check EMA alignment

        Bullish alignment: Price > EMA20 > EMA50 > EMA200
        Bearish alignment: Price < EMA20 < EMA50 < EMA200
        """
        ema_20 = emas['ema_20'].iloc[-1]
        ema_50 = emas['ema_50'].iloc[-1]
        ema_200 = emas['ema_200'].iloc[-1]

        # Perfect bullish alignment
        if current_price > ema_20 > ema_50 > ema_200:
            return {
                'alignment': 'BULLISH',
                'strength': 'STRONG',
                'above_ema_200': True,
                'all_aligned': True
            }
        # Perfect bearish alignment
        elif current_price < ema_20 < ema_50 < ema_200:
            return {
                'alignment': 'BEARISH',
                'strength': 'STRONG',
                'above_ema_200': False,
                'all_aligned': True
            }
        # Above EMA 200 (bullish bias)
        elif current_price > ema_200:
            return {
                'alignment': 'BULLISH',
                'strength': 'MODERATE',
                'above_ema_200': True,
                'all_aligned': False
            }
        # Below EMA 200 (bearish bias)
        elif current_price < ema_200:
            return {
                'alignment': 'BEARISH',
                'strength': 'MODERATE',
                'above_ema_200': False,
                'all_aligned': False
            }
        else:
            return {
                'alignment': 'NEUTRAL',
                'strength': 'NEUTRAL',
                'above_ema_200': False,
                'all_aligned': False
            }

    def calculate_atr(self, df: pd.DataFrame) -> pd.Series:
        """
        Calculate ATR (Average True Range)

        Used for volatility-adjusted stops and targets
        """
        high_low = df['high'] - df['low']
        high_close = abs(df['high'] - df['close'].shift())
        low_close = abs(df['low'] - df['close'].shift())

        true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = true_range.rolling(window=self.atr_period).mean()

        logger.info(f"ATR calculated (current: ${atr.iloc[-1]:.2f})")
        return atr

    def calculate_atr_stops(
        self,
        current_price: float,
        atr: pd.Series,
        multiplier: float = 1.5
    ) -> Dict:
        """
        Calculate ATR-based stop losses and targets

        Stop = Entry ± (multiplier × ATR)
        Target = Entry + (risk/reward × risk)
        """
        current_atr = atr.iloc[-1]

        return {
            'atr': float(current_atr),
            'long_stop': float(current_price - (multiplier * current_atr)),
            'short_stop': float(current_price + (multiplier * current_atr)),
            'long_target_1': float(current_price + (2 * multiplier * current_atr)),  # 1:2 R/R
            'long_target_2': float(current_price + (3 * multiplier * current_atr)),  # 1:3 R/R
            'short_target_1': float(current_price - (2 * multiplier * current_atr)),
            'short_target_2': float(current_price - (3 * multiplier * current_atr))
        }

    def calculate_volume_delta(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate Volume Delta and CVD (Cumulative Volume Delta)

        Positive CVD = Accumulation (buying pressure)
        Negative CVD = Distribution (selling pressure)
        """
        df_copy = df.copy()
        df_copy['delta'] = 0

        for i in range(len(df_copy)):
            if df_copy['close'].iloc[i] > df_copy['open'].iloc[i]:
                # Up candle = buy volume
                df_copy.loc[df_copy.index[i], 'delta'] = df_copy['volume'].iloc[i]
            elif df_copy['close'].iloc[i] < df_copy['open'].iloc[i]:
                # Down candle = sell volume
                df_copy.loc[df_copy.index[i], 'delta'] = -df_copy['volume'].iloc[i]
            else:
                # Doji = neutral
                df_copy.loc[df_copy.index[i], 'delta'] = 0

        # Cumulative Volume Delta
        df_copy['cvd'] = df_copy['delta'].cumsum()

        logger.info(f"CVD calculated (current: {df_copy['cvd'].iloc[-1]:.0f})")

        return df_copy[['delta', 'cvd']]

    def get_cvd_signal(self, cvd_data: pd.DataFrame, zone_type: str) -> Dict:
        """
        Get CVD signal based on zone type

        For demand zones: Want CVD rising (accumulation)
        For supply zones: Want CVD falling (distribution)
        """
        current_cvd = cvd_data['cvd'].iloc[-1]
        previous_cvd = cvd_data['cvd'].iloc[-20]  # 20 periods ago

        cvd_trend = 'RISING' if current_cvd > previous_cvd else 'FALLING'

        if zone_type == 'DEMAND':
            if cvd_trend == 'RISING':
                return {
                    'signal': 'ACCUMULATION',
                    'strength': 'CONFIRMING',
                    'cvd': float(current_cvd),
                    'trend': cvd_trend
                }
            else:
                return {
                    'signal': 'DISTRIBUTION',
                    'strength': 'CONFLICTING',
                    'cvd': float(current_cvd),
                    'trend': cvd_trend
                }
        else:  # SUPPLY
            if cvd_trend == 'FALLING':
                return {
                    'signal': 'DISTRIBUTION',
                    'strength': 'CONFIRMING',
                    'cvd': float(current_cvd),
                    'trend': cvd_trend
                }
            else:
                return {
                    'signal': 'ACCUMULATION',
                    'strength': 'CONFLICTING',
                    'cvd': float(current_cvd),
                    'trend': cvd_trend
                }

    def calculate_fibonacci_levels(
        self,
        swing_high: float,
        swing_low: float,
        trend: str = 'BULLISH'
    ) -> Dict:
        """
        Calculate Fibonacci retracement levels

        For bullish trend: Retrace from high to low
        For bearish trend: Retrace from low to high
        """
        if trend == 'BULLISH':
            diff = swing_high - swing_low
            base = swing_low
        else:
            diff = swing_low - swing_high
            base = swing_high

        levels = {
            'level_0': float(swing_high if trend == 'BULLISH' else swing_low),
            'level_236': float(base + (diff * 0.236)),
            'level_382': float(base + (diff * 0.382)),
            'level_50': float(base + (diff * 0.50)),
            'level_618': float(base + (diff * 0.618)),  # Golden ratio
            'level_786': float(base + (diff * 0.786)),
            'level_100': float(swing_low if trend == 'BULLISH' else swing_high),
            'swing_high': float(swing_high),
            'swing_low': float(swing_low),
            'trend': trend
        }

        logger.info(f"Fibonacci levels calculated ({trend})")
        return levels

    def is_at_fibonacci_level(
        self,
        price: float,
        fib_levels: Dict,
        tolerance_pct: float = 1.0
    ) -> Optional[Dict]:
        """Check if price is at a Fibonacci level"""
        for level_name, level_price in fib_levels.items():
            if level_name.startswith('level_'):
                distance_pct = abs(price - level_price) / price * 100
                if distance_pct <= tolerance_pct:
                    return {
                        'at_fib_level': True,
                        'level': level_name,
                        'price': float(level_price),
                        'distance_pct': float(distance_pct)
                    }

        return {'at_fib_level': False}

    def get_all_momentum_indicators(self, df: pd.DataFrame, current_price: float) -> Dict:
        """Get all momentum indicators at once"""
        rsi = self.calculate_rsi(df)
        macd = self.calculate_macd(df)
        emas = self.calculate_emas(df)
        atr = self.calculate_atr(df)
        cvd_data = self.calculate_volume_delta(df)

        return {
            'rsi': {
                'series': rsi,
                'signal': self.get_rsi_signal(rsi)
            },
            'macd': {
                'data': macd,
                'signal': self.get_macd_signal(macd)
            },
            'emas': {
                'data': emas,
                'alignment': self.get_ema_alignment(emas, current_price)
            },
            'atr': {
                'series': atr,
                'stops': self.calculate_atr_stops(current_price, atr)
            },
            'cvd': cvd_data
        }


if __name__ == "__main__":
    # Test
    import yfinance as yf
    logging.basicConfig(level=logging.INFO)

    print("Testing Momentum Indicators with AAPL...")

    ticker = yf.Ticker("AAPL")
    df = ticker.history(period="3mo", interval="1d")
    current_price = df['Close'].iloc[-1]

    mi = MomentumIndicators()
    indicators = mi.get_all_momentum_indicators(df, current_price)

    print(f"\nCurrent Price: ${current_price:.2f}")
    print(f"\nRSI: {indicators['rsi']['signal']['value']:.1f} ({indicators['rsi']['signal']['signal']})")
    print(f"MACD Signal: {indicators['macd']['signal']['signal']}")
    print(f"EMA Alignment: {indicators['emas']['alignment']['alignment']} ({indicators['emas']['alignment']['strength']})")
    print(f"ATR: ${indicators['atr']['stops']['atr']:.2f}")
    print(f"ATR Stop (Long): ${indicators['atr']['stops']['long_stop']:.2f}")
    print(f"ATR Target (Long): ${indicators['atr']['stops']['long_target_1']:.2f}")
    print(f"CVD: {indicators['cvd']['cvd'].iloc[-1]:.0f}")

    # Test Fibonacci
    swing_high = df['High'].iloc[-60:].max()
    swing_low = df['Low'].iloc[-60:].min()
    fib = mi.calculate_fibonacci_levels(swing_high, swing_low, 'BULLISH')
    print(f"\nFibonacci 0.618 (Golden Ratio): ${fib['level_618']:.2f}")
