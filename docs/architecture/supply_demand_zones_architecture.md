# Supply/Demand Zone Detection and Alert System - Architecture Design

**Created:** 2025-11-09
**System:** Magnus Wheel Strategy Trading Dashboard
**Purpose:** Detect institutional supply/demand zones and alert on buying opportunities

---

## Table of Contents

1. [System Overview](#system-overview)
2. [Architecture Components](#architecture-components)
3. [Database Schema](#database-schema)
4. [Class Structure](#class-structure)
5. [Data Flow](#data-flow)
6. [Zone Detection Algorithm](#zone-detection-algorithm)
7. [Integration Points](#integration-points)
8. [Deployment Strategy](#deployment-strategy)

---

## System Overview

### Purpose
Automatically detect supply/demand zones (institutional support/resistance levels) on stock charts and send Telegram alerts when prices drop into demand zones (buying opportunities) or rise into supply zones (selling opportunities).

### Key Features
- Swing high/low detection based on price action
- Volume confirmation for zone strength
- Multiple timeframe analysis (daily, 4-hour, 1-hour)
- Zone test history tracking
- Real-time price monitoring against zones
- Telegram alerts with trade setup details
- Integration with existing TradingView watchlists
- Historical zone performance analytics

### Technical Principles
- **Supply Zone:** Area where selling pressure overwhelms buying (resistance)
- **Demand Zone:** Area where buying pressure overwhelms selling (support)
- **Zone Strength:** Determined by volume, time since creation, number of tests
- **Fresh Zone:** Zone that has not been tested since creation
- **Tested Zone:** Zone that price has touched but held
- **Broken Zone:** Zone that price has penetrated significantly

---

## Architecture Components

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     Supply/Demand System                        │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────┐     ┌──────────────────┐                 │
│  │  Zone Detector   │────>│  Zone Analyzer   │                 │
│  │  (swing points)  │     │  (strength calc) │                 │
│  └────────┬─────────┘     └────────┬─────────┘                 │
│           │                         │                            │
│           v                         v                            │
│  ┌──────────────────────────────────────────┐                  │
│  │         Zone Database Manager            │                  │
│  │  (zone CRUD, test tracking, history)     │                  │
│  └────────┬─────────────────────────────────┘                  │
│           │                                                      │
│           v                                                      │
│  ┌──────────────────┐     ┌──────────────────┐                 │
│  │  Price Monitor   │────>│  Alert Manager   │                 │
│  │  (zone touches)  │     │  (Telegram)      │                 │
│  └──────────────────┘     └──────────────────┘                 │
│           ^                                                      │
│           │                                                      │
│  ┌────────┴─────────┐     ┌──────────────────┐                 │
│  │ Watchlist Loader │     │  Scanner Service │                 │
│  │ (TradingView DB) │     │  (scheduler)     │                 │
│  └──────────────────┘     └──────────────────┘                 │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘

External Dependencies:
- PostgreSQL (zone storage)
- yfinance (price data)
- pandas-ta (technical indicators)
- Telegram Bot API (alerts)
```

### Component Responsibilities

1. **ZoneDetector:** Identifies swing highs/lows from OHLCV data
2. **ZoneAnalyzer:** Calculates zone strength, quality scores
3. **ZoneDatabaseManager:** CRUD operations for zones and tests
4. **PriceMonitor:** Real-time monitoring of price action vs zones
5. **AlertManager:** Formats and sends Telegram notifications
6. **WatchlistLoader:** Fetches stocks from TradingView watchlists
7. **ScannerService:** Scheduled scanning orchestrator

---

## Database Schema

### Table: `sd_zones`
Stores identified supply/demand zones.

```sql
CREATE TABLE IF NOT EXISTS sd_zones (
    id SERIAL PRIMARY KEY,
    ticker VARCHAR(20) NOT NULL,
    zone_type VARCHAR(10) NOT NULL, -- 'SUPPLY' or 'DEMAND'
    timeframe VARCHAR(10) NOT NULL, -- '1d', '4h', '1h'

    -- Zone boundaries
    zone_top DECIMAL(10,2) NOT NULL,
    zone_bottom DECIMAL(10,2) NOT NULL,
    zone_midpoint DECIMAL(10,2) NOT NULL,

    -- Formation details
    formed_date TIMESTAMP WITH TIME ZONE NOT NULL,
    formation_candle_index INTEGER,
    approach_volume BIGINT,
    departure_volume BIGINT,

    -- Strength indicators
    strength_score DECIMAL(5,2) DEFAULT 0.0, -- 0-100
    volume_ratio DECIMAL(10,2), -- departure_vol / approach_vol
    time_at_zone INTEGER, -- candles spent in zone
    rejection_candles INTEGER, -- candles showing rejection

    -- Zone status
    status VARCHAR(20) DEFAULT 'FRESH', -- FRESH, TESTED, WEAK, BROKEN
    test_count INTEGER DEFAULT 0,
    last_test_date TIMESTAMP WITH TIME ZONE,
    broken_date TIMESTAMP WITH TIME ZONE,

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    is_active BOOLEAN DEFAULT TRUE,
    notes TEXT,

    CONSTRAINT chk_zone_type CHECK (zone_type IN ('SUPPLY', 'DEMAND')),
    CONSTRAINT chk_zone_status CHECK (status IN ('FRESH', 'TESTED', 'WEAK', 'BROKEN')),
    CONSTRAINT chk_timeframe CHECK (timeframe IN ('1d', '4h', '1h', '15m'))
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_sd_zones_ticker ON sd_zones(ticker);
CREATE INDEX IF NOT EXISTS idx_sd_zones_status ON sd_zones(status);
CREATE INDEX IF NOT EXISTS idx_sd_zones_active ON sd_zones(is_active);
CREATE INDEX IF NOT EXISTS idx_sd_zones_type ON sd_zones(zone_type);
CREATE INDEX IF NOT EXISTS idx_sd_zones_ticker_active ON sd_zones(ticker, is_active);
CREATE INDEX IF NOT EXISTS idx_sd_zones_strength ON sd_zones(strength_score DESC);

COMMENT ON TABLE sd_zones IS 'Supply and demand zones detected from price action';
COMMENT ON COLUMN sd_zones.strength_score IS 'Zone strength 0-100 based on volume, rejection, tests';
COMMENT ON COLUMN sd_zones.status IS 'FRESH=untested, TESTED=held, WEAK=multiple tests, BROKEN=penetrated';
```

### Table: `sd_zone_tests`
Tracks each time price tests a zone.

```sql
CREATE TABLE IF NOT EXISTS sd_zone_tests (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES sd_zones(id) ON DELETE CASCADE,

    -- Test details
    test_date TIMESTAMP WITH TIME ZONE NOT NULL,
    test_price DECIMAL(10,2) NOT NULL,
    test_type VARCHAR(20) NOT NULL, -- 'TOUCH', 'PENETRATION', 'REJECTION', 'BREAK'

    -- Price action during test
    penetration_percent DECIMAL(5,2), -- How far into zone (%)
    reaction_candles INTEGER, -- Candles to react
    bounce_percent DECIMAL(5,2), -- % bounce from zone
    test_volume BIGINT,

    -- Test outcome
    held BOOLEAN, -- Did zone hold?
    broke_through BOOLEAN, -- Did price break through?

    -- Metadata
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),

    CONSTRAINT chk_test_type CHECK (test_type IN ('TOUCH', 'PENETRATION', 'REJECTION', 'BREAK'))
);

CREATE INDEX IF NOT EXISTS idx_sd_zone_tests_zone_id ON sd_zone_tests(zone_id);
CREATE INDEX IF NOT EXISTS idx_sd_zone_tests_date ON sd_zone_tests(test_date DESC);

COMMENT ON TABLE sd_zone_tests IS 'Historical record of zone test events';
```

### Table: `sd_alerts`
Tracks alerts sent for zone events.

```sql
CREATE TABLE IF NOT EXISTS sd_alerts (
    id SERIAL PRIMARY KEY,
    zone_id INTEGER NOT NULL REFERENCES sd_zones(id) ON DELETE CASCADE,
    ticker VARCHAR(20) NOT NULL,

    -- Alert details
    alert_type VARCHAR(30) NOT NULL, -- 'PRICE_ENTERING_DEMAND', 'PRICE_AT_SUPPLY', 'ZONE_BOUNCE', 'ZONE_BREAK'
    alert_price DECIMAL(10,2) NOT NULL,
    zone_type VARCHAR(10) NOT NULL,

    -- Trading context
    distance_to_zone DECIMAL(5,2), -- % distance
    zone_strength DECIMAL(5,2),
    setup_quality VARCHAR(20), -- 'HIGH', 'MEDIUM', 'LOW'

    -- Alert delivery
    sent_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    telegram_message_id VARCHAR(255),
    status VARCHAR(20) DEFAULT 'sent', -- 'sent', 'failed'
    error_message TEXT,

    CONSTRAINT chk_alert_type CHECK (alert_type IN (
        'PRICE_ENTERING_DEMAND', 'PRICE_AT_DEMAND', 'PRICE_ENTERING_SUPPLY',
        'PRICE_AT_SUPPLY', 'ZONE_BOUNCE', 'ZONE_BREAK'
    )),
    CONSTRAINT chk_setup_quality CHECK (setup_quality IN ('HIGH', 'MEDIUM', 'LOW'))
);

CREATE INDEX IF NOT EXISTS idx_sd_alerts_zone_id ON sd_alerts(zone_id);
CREATE INDEX IF NOT EXISTS idx_sd_alerts_ticker ON sd_alerts(ticker);
CREATE INDEX IF NOT EXISTS idx_sd_alerts_sent_at ON sd_alerts(sent_at DESC);

COMMENT ON TABLE sd_alerts IS 'Alert history for supply/demand zone events';
```

### Table: `sd_scan_log`
Audit log for scanner runs.

```sql
CREATE TABLE IF NOT EXISTS sd_scan_log (
    id SERIAL PRIMARY KEY,
    scan_timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    scan_type VARCHAR(50), -- 'ZONE_DETECTION', 'PRICE_MONITORING', 'ZONE_CLEANUP'

    -- Scan results
    tickers_scanned INTEGER DEFAULT 0,
    zones_found INTEGER DEFAULT 0,
    zones_updated INTEGER DEFAULT 0,
    alerts_sent INTEGER DEFAULT 0,

    -- Performance
    duration_seconds DECIMAL(10,2),
    status VARCHAR(50) DEFAULT 'success', -- 'success', 'partial', 'failed'
    errors TEXT,

    CONSTRAINT chk_scan_status CHECK (status IN ('success', 'partial', 'failed'))
);

CREATE INDEX IF NOT EXISTS idx_sd_scan_log_timestamp ON sd_scan_log(scan_timestamp DESC);

COMMENT ON TABLE sd_scan_log IS 'Audit log for zone scanner operations';
```

---

## Class Structure

### 1. ZoneDetector

```python
"""
Detects supply and demand zones from OHLCV data using swing point analysis.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional, Tuple
import pandas as pd
import numpy as np


@dataclass
class SwingPoint:
    """Represents a swing high or swing low point."""
    index: int
    price: float
    swing_type: str  # 'HIGH' or 'LOW'
    timestamp: datetime
    volume: int


@dataclass
class Zone:
    """Represents a detected supply or demand zone."""
    ticker: str
    zone_type: str  # 'SUPPLY' or 'DEMAND'
    timeframe: str
    zone_top: float
    zone_bottom: float
    zone_midpoint: float
    formed_date: datetime
    approach_volume: int
    departure_volume: int
    strength_score: float
    formation_candle_index: int


class ZoneDetector:
    """
    Detects supply/demand zones from price data using swing point analysis.

    A supply zone forms at a swing high where:
    - Price makes a strong move up (approach)
    - Price consolidates briefly (the zone)
    - Price moves sharply down on high volume (departure/rejection)

    A demand zone forms at a swing low where:
    - Price makes a strong move down (approach)
    - Price consolidates briefly (the zone)
    - Price moves sharply up on high volume (departure/rejection)
    """

    def __init__(
        self,
        swing_lookback: int = 5,
        min_zone_touches: int = 2,
        max_zone_width_percent: float = 3.0,
        volume_threshold: float = 1.2
    ):
        """
        Initialize zone detector with configurable parameters.

        Args:
            swing_lookback: Number of candles to left/right for swing validation
            min_zone_touches: Minimum candle touches to form valid zone
            max_zone_width_percent: Maximum zone width as % of price
            volume_threshold: Minimum departure/approach volume ratio
        """
        self.swing_lookback = swing_lookback
        self.min_zone_touches = min_zone_touches
        self.max_zone_width_percent = max_zone_width_percent
        self.volume_threshold = volume_threshold

    def detect_zones(
        self,
        ticker: str,
        df: pd.DataFrame,
        timeframe: str = '1d',
        lookback_periods: int = 100
    ) -> List[Zone]:
        """
        Detect all supply and demand zones in the given price data.

        Args:
            ticker: Stock ticker symbol
            df: DataFrame with OHLCV data (index=datetime, columns=Open,High,Low,Close,Volume)
            timeframe: Chart timeframe ('1d', '4h', '1h')
            lookback_periods: Number of recent candles to analyze

        Returns:
            List of detected Zone objects
        """
        # Validate and prepare data
        df = self._prepare_data(df, lookback_periods)

        # Find swing points
        swing_highs = self._find_swing_highs(df)
        swing_lows = self._find_swing_lows(df)

        # Detect supply zones from swing highs
        supply_zones = self._detect_supply_zones(ticker, df, swing_highs, timeframe)

        # Detect demand zones from swing lows
        demand_zones = self._detect_demand_zones(ticker, df, swing_lows, timeframe)

        # Combine and filter overlapping zones
        all_zones = supply_zones + demand_zones
        filtered_zones = self._filter_overlapping_zones(all_zones)

        return filtered_zones

    def _prepare_data(self, df: pd.DataFrame, lookback: int) -> pd.DataFrame:
        """Validate and prepare OHLCV dataframe."""
        required_cols = ['Open', 'High', 'Low', 'Close', 'Volume']
        if not all(col in df.columns for col in required_cols):
            raise ValueError(f"DataFrame must contain columns: {required_cols}")

        # Take most recent periods
        df = df.tail(lookback).copy()

        # Calculate average volume
        df['Volume_MA'] = df['Volume'].rolling(window=20).mean()

        return df

    def _find_swing_highs(self, df: pd.DataFrame) -> List[SwingPoint]:
        """
        Find swing high points where price makes a local maximum.

        A swing high is valid when the high is greater than
        N candles to the left AND N candles to the right.
        """
        swing_highs = []
        lookback = self.swing_lookback

        for i in range(lookback, len(df) - lookback):
            current_high = df.iloc[i]['High']

            # Check if current high is greater than all lookback candles
            left_candles = df.iloc[i-lookback:i]['High']
            right_candles = df.iloc[i+1:i+lookback+1]['High']

            if current_high > left_candles.max() and current_high > right_candles.max():
                swing_highs.append(SwingPoint(
                    index=i,
                    price=current_high,
                    swing_type='HIGH',
                    timestamp=df.index[i],
                    volume=int(df.iloc[i]['Volume'])
                ))

        return swing_highs

    def _find_swing_lows(self, df: pd.DataFrame) -> List[SwingPoint]:
        """
        Find swing low points where price makes a local minimum.

        A swing low is valid when the low is less than
        N candles to the left AND N candles to the right.
        """
        swing_lows = []
        lookback = self.swing_lookback

        for i in range(lookback, len(df) - lookback):
            current_low = df.iloc[i]['Low']

            # Check if current low is less than all lookback candles
            left_candles = df.iloc[i-lookback:i]['Low']
            right_candles = df.iloc[i+1:i+lookback+1]['Low']

            if current_low < left_candles.min() and current_low < right_candles.min():
                swing_lows.append(SwingPoint(
                    index=i,
                    price=current_low,
                    swing_type='LOW',
                    timestamp=df.index[i],
                    volume=int(df.iloc[i]['Volume'])
                ))

        return swing_lows

    def _detect_supply_zones(
        self,
        ticker: str,
        df: pd.DataFrame,
        swing_highs: List[SwingPoint],
        timeframe: str
    ) -> List[Zone]:
        """
        Detect supply zones from swing high points.

        Supply zone formation criteria:
        1. Strong upward move into the swing high (approach)
        2. Brief consolidation at the high (the zone)
        3. Strong downward move away from high on volume (departure/rejection)
        """
        zones = []

        for swing in swing_highs:
            # Get candles around swing point
            zone_start = max(0, swing.index - 3)
            zone_end = min(len(df), swing.index + 3)
            zone_candles = df.iloc[zone_start:zone_end]

            # Define zone boundaries (high to last green candle before reversal)
            zone_top = zone_candles['High'].max()
            zone_bottom = self._find_supply_zone_base(df, swing.index)

            if zone_bottom is None:
                continue

            # Validate zone width
            zone_width_percent = ((zone_top - zone_bottom) / zone_bottom) * 100
            if zone_width_percent > self.max_zone_width_percent:
                continue

            # Calculate approach and departure volumes
            approach_volume = self._calculate_approach_volume(df, swing.index, 'up')
            departure_volume = self._calculate_departure_volume(df, swing.index, 'down')

            # Require strong departure on volume
            volume_ratio = departure_volume / approach_volume if approach_volume > 0 else 0
            if volume_ratio < self.volume_threshold:
                continue

            # Calculate strength score
            strength_score = self._calculate_zone_strength(
                volume_ratio=volume_ratio,
                zone_width_percent=zone_width_percent,
                departure_volume=departure_volume,
                avg_volume=df['Volume_MA'].iloc[swing.index]
            )

            zone = Zone(
                ticker=ticker,
                zone_type='SUPPLY',
                timeframe=timeframe,
                zone_top=round(zone_top, 2),
                zone_bottom=round(zone_bottom, 2),
                zone_midpoint=round((zone_top + zone_bottom) / 2, 2),
                formed_date=swing.timestamp,
                approach_volume=int(approach_volume),
                departure_volume=int(departure_volume),
                strength_score=round(strength_score, 2),
                formation_candle_index=swing.index
            )

            zones.append(zone)

        return zones

    def _detect_demand_zones(
        self,
        ticker: str,
        df: pd.DataFrame,
        swing_lows: List[SwingPoint],
        timeframe: str
    ) -> List[Zone]:
        """
        Detect demand zones from swing low points.

        Demand zone formation criteria:
        1. Strong downward move into the swing low (approach)
        2. Brief consolidation at the low (the zone)
        3. Strong upward move away from low on volume (departure/rejection)
        """
        zones = []

        for swing in swing_lows:
            # Get candles around swing point
            zone_start = max(0, swing.index - 3)
            zone_end = min(len(df), swing.index + 3)
            zone_candles = df.iloc[zone_start:zone_end]

            # Define zone boundaries (low to last red candle before reversal)
            zone_bottom = zone_candles['Low'].min()
            zone_top = self._find_demand_zone_top(df, swing.index)

            if zone_top is None:
                continue

            # Validate zone width
            zone_width_percent = ((zone_top - zone_bottom) / zone_bottom) * 100
            if zone_width_percent > self.max_zone_width_percent:
                continue

            # Calculate approach and departure volumes
            approach_volume = self._calculate_approach_volume(df, swing.index, 'down')
            departure_volume = self._calculate_departure_volume(df, swing.index, 'up')

            # Require strong departure on volume
            volume_ratio = departure_volume / approach_volume if approach_volume > 0 else 0
            if volume_ratio < self.volume_threshold:
                continue

            # Calculate strength score
            strength_score = self._calculate_zone_strength(
                volume_ratio=volume_ratio,
                zone_width_percent=zone_width_percent,
                departure_volume=departure_volume,
                avg_volume=df['Volume_MA'].iloc[swing.index]
            )

            zone = Zone(
                ticker=ticker,
                zone_type='DEMAND',
                timeframe=timeframe,
                zone_top=round(zone_top, 2),
                zone_bottom=round(zone_bottom, 2),
                zone_midpoint=round((zone_top + zone_bottom) / 2, 2),
                formed_date=swing.timestamp,
                approach_volume=int(approach_volume),
                departure_volume=int(departure_volume),
                strength_score=round(strength_score, 2),
                formation_candle_index=swing.index
            )

            zones.append(zone)

        return zones

    def _find_supply_zone_base(self, df: pd.DataFrame, swing_index: int) -> Optional[float]:
        """Find the bottom of supply zone (last bullish candle before reversal)."""
        # Look at 3 candles before swing high
        for i in range(swing_index - 1, max(0, swing_index - 4), -1):
            candle = df.iloc[i]
            if candle['Close'] > candle['Open']:  # Bullish candle
                return candle['Low']
        return None

    def _find_demand_zone_top(self, df: pd.DataFrame, swing_index: int) -> Optional[float]:
        """Find the top of demand zone (last bearish candle before reversal)."""
        # Look at 3 candles before swing low
        for i in range(swing_index - 1, max(0, swing_index - 4), -1):
            candle = df.iloc[i]
            if candle['Close'] < candle['Open']:  # Bearish candle
                return candle['High']
        return None

    def _calculate_approach_volume(
        self,
        df: pd.DataFrame,
        swing_index: int,
        direction: str
    ) -> float:
        """Calculate average volume during approach to zone."""
        lookback = min(5, swing_index)
        approach_candles = df.iloc[swing_index - lookback:swing_index]
        return approach_candles['Volume'].mean()

    def _calculate_departure_volume(
        self,
        df: pd.DataFrame,
        swing_index: int,
        direction: str
    ) -> float:
        """Calculate average volume during departure from zone."""
        lookforward = min(5, len(df) - swing_index - 1)
        departure_candles = df.iloc[swing_index + 1:swing_index + 1 + lookforward]
        return departure_candles['Volume'].mean()

    def _calculate_zone_strength(
        self,
        volume_ratio: float,
        zone_width_percent: float,
        departure_volume: float,
        avg_volume: float
    ) -> float:
        """
        Calculate zone strength score (0-100).

        Factors:
        - Volume ratio (departure/approach): Higher is better
        - Zone width: Tighter zones are stronger
        - Absolute volume: Higher volume = institutional interest
        """
        # Volume score (0-40 points)
        volume_score = min(40, (volume_ratio - 1.0) * 20)

        # Tightness score (0-30 points)
        tightness_score = max(0, 30 - (zone_width_percent * 10))

        # Absolute volume score (0-30 points)
        volume_multiple = departure_volume / avg_volume if avg_volume > 0 else 1
        abs_volume_score = min(30, (volume_multiple - 1.0) * 15)

        total_score = volume_score + tightness_score + abs_volume_score
        return min(100, max(0, total_score))

    def _filter_overlapping_zones(self, zones: List[Zone]) -> List[Zone]:
        """
        Filter out overlapping zones, keeping the strongest.

        If two zones overlap by >50%, keep only the higher strength zone.
        """
        if not zones:
            return []

        # Sort by strength descending
        zones = sorted(zones, key=lambda z: z.strength_score, reverse=True)

        filtered = []
        for zone in zones:
            overlaps = False
            for existing in filtered:
                if self._zones_overlap(zone, existing):
                    overlaps = True
                    break

            if not overlaps:
                filtered.append(zone)

        return filtered

    def _zones_overlap(self, zone1: Zone, zone2: Zone, threshold: float = 0.5) -> bool:
        """Check if two zones overlap by more than threshold (50%)."""
        # Zones must be same type and ticker to overlap
        if zone1.ticker != zone2.ticker or zone1.zone_type != zone2.zone_type:
            return False

        # Calculate overlap
        overlap_top = min(zone1.zone_top, zone2.zone_top)
        overlap_bottom = max(zone1.zone_bottom, zone2.zone_bottom)

        if overlap_bottom >= overlap_top:
            return False  # No overlap

        overlap_height = overlap_top - overlap_bottom
        zone1_height = zone1.zone_top - zone1.zone_bottom
        zone2_height = zone2.zone_top - zone2.zone_bottom

        # Check if overlap is >threshold of either zone
        overlap_ratio_1 = overlap_height / zone1_height
        overlap_ratio_2 = overlap_height / zone2_height

        return overlap_ratio_1 > threshold or overlap_ratio_2 > threshold
```

### 2. ZoneAnalyzer

```python
"""
Analyzes zone quality, tracks tests, and updates zone status.
"""

from typing import Dict, List, Optional
import pandas as pd
from datetime import datetime


class ZoneAnalyzer:
    """
    Analyzes supply/demand zones for quality, test history, and status updates.
    """

    def __init__(self, penetration_threshold: float = 0.3):
        """
        Initialize zone analyzer.

        Args:
            penetration_threshold: % penetration to consider zone tested (default 30%)
        """
        self.penetration_threshold = penetration_threshold

    def analyze_zone_test(
        self,
        zone: Zone,
        current_price: float,
        current_candle: pd.Series
    ) -> Optional[Dict]:
        """
        Analyze if current price is testing a zone and the nature of the test.

        Args:
            zone: Zone object to check
            current_price: Current price
            current_candle: Current OHLC candle data

        Returns:
            Dict with test details or None if no test occurring
        """
        # Calculate zone penetration
        if zone.zone_type == 'DEMAND':
            # For demand zones, check if price has dropped into zone
            if current_price > zone.zone_top:
                return None  # Price above zone

            penetration_pct = self._calculate_penetration(
                price=current_price,
                zone_top=zone.zone_top,
                zone_bottom=zone.zone_bottom
            )

            test_type = self._determine_test_type(penetration_pct, 'DEMAND', current_candle)

        else:  # SUPPLY zone
            # For supply zones, check if price has risen into zone
            if current_price < zone.zone_bottom:
                return None  # Price below zone

            penetration_pct = self._calculate_penetration(
                price=current_price,
                zone_top=zone.zone_top,
                zone_bottom=zone.zone_bottom
            )

            test_type = self._determine_test_type(penetration_pct, 'SUPPLY', current_candle)

        if penetration_pct < self.penetration_threshold:
            return None  # Not a significant test

        return {
            'test_type': test_type,
            'penetration_pct': round(penetration_pct, 2),
            'test_price': current_price,
            'test_volume': int(current_candle.get('Volume', 0))
        }

    def _calculate_penetration(
        self,
        price: float,
        zone_top: float,
        zone_bottom: float
    ) -> float:
        """Calculate what % of the zone the price has penetrated."""
        zone_height = zone_top - zone_bottom

        if price > zone_top:
            # Above zone
            return 0.0
        elif price < zone_bottom:
            # Below zone (broke through)
            return 100.0
        else:
            # Inside zone
            penetration = zone_top - price
            return (penetration / zone_height) * 100

    def _determine_test_type(
        self,
        penetration_pct: float,
        zone_type: str,
        candle: pd.Series
    ) -> str:
        """Determine the type of zone test based on price action."""
        if penetration_pct < 30:
            return 'TOUCH'
        elif penetration_pct < 70:
            return 'PENETRATION'
        elif penetration_pct >= 100:
            return 'BREAK'
        else:
            # Check for rejection (wick)
            if zone_type == 'DEMAND':
                # Look for long lower wick (buyers stepping in)
                body_low = min(candle['Open'], candle['Close'])
                wick_size = body_low - candle['Low']
                body_size = abs(candle['Close'] - candle['Open'])

                if wick_size > body_size * 2:
                    return 'REJECTION'
            else:  # SUPPLY
                # Look for long upper wick (sellers stepping in)
                body_high = max(candle['Open'], candle['Close'])
                wick_size = candle['High'] - body_high
                body_size = abs(candle['Close'] - candle['Open'])

                if wick_size > body_size * 2:
                    return 'REJECTION'

            return 'PENETRATION'

    def calculate_zone_quality(
        self,
        zone: Zone,
        test_history: List[Dict],
        current_price: float
    ) -> str:
        """
        Calculate overall zone quality based on strength and test history.

        Returns: 'HIGH', 'MEDIUM', or 'LOW'
        """
        score = 0

        # Base strength score (0-40 points)
        score += (zone.strength_score / 100) * 40

        # Test history score (0-30 points)
        if len(test_history) == 0:
            # Fresh zone - bonus points
            score += 30
        elif len(test_history) <= 2:
            # Few tests - good
            held_tests = sum(1 for t in test_history if t.get('held', False))
            score += (held_tests / len(test_history)) * 25
        else:
            # Many tests - zone weakening
            score += 10

        # Recency score (0-30 points)
        days_old = (datetime.now() - zone.formed_date).days
        if days_old < 5:
            score += 30  # Very fresh
        elif days_old < 20:
            score += 20  # Reasonably fresh
        elif days_old < 60:
            score += 10  # Aging
        else:
            score += 5   # Old zone

        # Classify
        if score >= 70:
            return 'HIGH'
        elif score >= 40:
            return 'MEDIUM'
        else:
            return 'LOW'

    def should_send_alert(
        self,
        zone: Zone,
        current_price: float,
        test_info: Dict,
        quality: str
    ) -> bool:
        """
        Determine if an alert should be sent for this zone test.

        Criteria:
        - Zone quality must be MEDIUM or HIGH
        - For demand zones: price entering or at zone
        - For supply zones: price entering or at zone
        - Not too many recent tests
        """
        # Only alert on quality setups
        if quality == 'LOW':
            return False

        # Check test type
        test_type = test_info.get('test_type')
        if test_type in ['TOUCH', 'PENETRATION', 'REJECTION']:
            return True

        return False
```

### 3. ZoneDatabaseManager

```python
"""
Database manager for supply/demand zones using PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import os
from dotenv import load_dotenv
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


class ZoneDatabaseManager:
    """Manages supply/demand zone data in PostgreSQL database."""

    def __init__(self):
        """Initialize database connection."""
        self.db_config = {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', 'postgres123!'),
            'database': os.getenv('DB_NAME', 'magnus')
        }

    def get_connection(self):
        """Get database connection."""
        return psycopg2.connect(**self.db_config)

    # =========================================================================
    # ZONE MANAGEMENT
    # =========================================================================

    def add_zone(self, zone_data: Dict[str, Any]) -> int:
        """
        Add a new supply/demand zone to database.

        Args:
            zone_data: Dictionary containing zone fields

        Returns:
            zone_id: ID of created zone
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO sd_zones (
                            ticker, zone_type, timeframe, zone_top, zone_bottom,
                            zone_midpoint, formed_date, approach_volume, departure_volume,
                            strength_score, volume_ratio, status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        zone_data['ticker'],
                        zone_data['zone_type'],
                        zone_data['timeframe'],
                        zone_data['zone_top'],
                        zone_data['zone_bottom'],
                        zone_data['zone_midpoint'],
                        zone_data['formed_date'],
                        zone_data['approach_volume'],
                        zone_data['departure_volume'],
                        zone_data['strength_score'],
                        zone_data.get('volume_ratio', 0),
                        'FRESH'
                    ))

                    zone_id = cur.fetchone()[0]
                    logger.info(f"Added {zone_data['zone_type']} zone for {zone_data['ticker']} (ID: {zone_id})")
                    return zone_id

        except Exception as e:
            logger.error(f"Error adding zone: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_active_zones(
        self,
        ticker: Optional[str] = None,
        zone_type: Optional[str] = None,
        min_strength: float = 0.0
    ) -> List[Dict[str, Any]]:
        """
        Get all active zones with optional filters.

        Args:
            ticker: Filter by ticker (optional)
            zone_type: Filter by SUPPLY or DEMAND (optional)
            min_strength: Minimum strength score (optional)

        Returns:
            List of zone dictionaries
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT * FROM sd_zones
                    WHERE is_active = TRUE AND status != 'BROKEN'
                """
                params = []

                if ticker:
                    query += " AND ticker = %s"
                    params.append(ticker.upper())

                if zone_type:
                    query += " AND zone_type = %s"
                    params.append(zone_type.upper())

                if min_strength > 0:
                    query += " AND strength_score >= %s"
                    params.append(min_strength)

                query += " ORDER BY strength_score DESC, formed_date DESC"

                cur.execute(query, params)
                zones = cur.fetchall()
                return [dict(zone) for zone in zones]

        except Exception as e:
            logger.error(f"Error fetching zones: {e}")
            return []
        finally:
            if conn:
                conn.close()

    def update_zone_status(
        self,
        zone_id: int,
        status: str,
        test_count: Optional[int] = None
    ) -> bool:
        """
        Update zone status and test count.

        Args:
            zone_id: Zone ID
            status: New status (FRESH, TESTED, WEAK, BROKEN)
            test_count: Optional test count to set

        Returns:
            True if successful
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn:
                with conn.cursor() as cur:
                    if test_count is not None:
                        cur.execute("""
                            UPDATE sd_zones
                            SET status = %s, test_count = %s, updated_at = NOW()
                            WHERE id = %s
                        """, (status, test_count, zone_id))
                    else:
                        cur.execute("""
                            UPDATE sd_zones
                            SET status = %s, updated_at = NOW()
                            WHERE id = %s
                        """, (status, zone_id))

                    logger.info(f"Updated zone {zone_id} status to {status}")
                    return True

        except Exception as e:
            logger.error(f"Error updating zone status: {e}")
            return False
        finally:
            if conn:
                conn.close()

    # =========================================================================
    # ZONE TEST TRACKING
    # =========================================================================

    def add_zone_test(self, test_data: Dict[str, Any]) -> int:
        """
        Record a zone test event.

        Args:
            test_data: Dictionary containing test details

        Returns:
            test_id: ID of created test record
        """
        conn = None
        try:
            conn = self.get_connection()
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO sd_zone_tests (
                            zone_id, test_date, test_price, test_type,
                            penetration_percent, test_volume, held, broke_through
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        test_data['zone_id'],
                        test_data.get('test_date', datetime.now()),
                        test_data['test_price'],
                        test_data['test_type'],
                        test_data.get('penetration_percent', 0),
                        test_data.get('test_volume', 0),
                        test_data.get('held', True),
                        test_data.get('broke_through', False)
                    ))

                    test_id = cur.fetchone()[0]

                    # Update zone test count and last test date
                    cur.execute("""
                        UPDATE sd_zones
                        SET test_count = test_count + 1,
                            last_test_date = %s
                        WHERE id = %s
                    """, (test_data.get('test_date', datetime.now()), test_data['zone_id']))

                    logger.info(f"Recorded zone test (ID: {test_id})")
                    return test_id

        except Exception as e:
            logger.error(f"Error adding zone test: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_zone_tests(self, zone_id: int) -> List[Dict[str, Any]]:
        """Get all test events for a zone."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT * FROM sd_zone_tests
                    WHERE zone_id = %s
                    ORDER BY test_date DESC
                """, (zone_id,))

                tests = cur.fetchall()
                return [dict(test) for test in tests]

        except Exception as e:
            logger.error(f"Error fetching zone tests: {e}")
            return []
        finally:
            if conn:
                conn.close()

    # =========================================================================
    # ALERT MANAGEMENT
    # =========================================================================

    def add_alert(self, alert_data: Dict[str, Any]) -> int:
        """Record a sent alert."""
        conn = None
        try:
            conn = self.get_connection()
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO sd_alerts (
                            zone_id, ticker, alert_type, alert_price, zone_type,
                            zone_strength, setup_quality, telegram_message_id, status
                        )
                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s)
                        RETURNING id
                    """, (
                        alert_data['zone_id'],
                        alert_data['ticker'],
                        alert_data['alert_type'],
                        alert_data['alert_price'],
                        alert_data['zone_type'],
                        alert_data.get('zone_strength', 0),
                        alert_data.get('setup_quality', 'MEDIUM'),
                        alert_data.get('telegram_message_id'),
                        alert_data.get('status', 'sent')
                    ))

                    alert_id = cur.fetchone()[0]
                    logger.info(f"Logged alert (ID: {alert_id})")
                    return alert_id

        except Exception as e:
            logger.error(f"Error adding alert: {e}")
            raise
        finally:
            if conn:
                conn.close()

    def get_recent_alerts(
        self,
        ticker: Optional[str] = None,
        hours: int = 24
    ) -> List[Dict[str, Any]]:
        """Get recent alerts to prevent duplicates."""
        conn = None
        try:
            conn = self.get_connection()
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT * FROM sd_alerts
                    WHERE sent_at >= NOW() - INTERVAL '%s hours'
                """
                params = [hours]

                if ticker:
                    query += " AND ticker = %s"
                    params.append(ticker.upper())

                query += " ORDER BY sent_at DESC"

                cur.execute(query, params)
                alerts = cur.fetchall()
                return [dict(alert) for alert in alerts]

        except Exception as e:
            logger.error(f"Error fetching recent alerts: {e}")
            return []
        finally:
            if conn:
                conn.close()
```

### 4. PriceMonitor

```python
"""
Monitors current prices against active zones and triggers alerts.
"""

import yfinance as yf
import pandas as pd
from typing import List, Dict, Optional
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class PriceMonitor:
    """
    Monitors real-time prices and detects when stocks enter supply/demand zones.
    """

    def __init__(
        self,
        db_manager: ZoneDatabaseManager,
        zone_analyzer: ZoneAnalyzer,
        alert_cooldown_hours: int = 24
    ):
        """
        Initialize price monitor.

        Args:
            db_manager: Zone database manager instance
            zone_analyzer: Zone analyzer instance
            alert_cooldown_hours: Hours to wait before re-alerting same zone
        """
        self.db = db_manager
        self.analyzer = zone_analyzer
        self.alert_cooldown_hours = alert_cooldown_hours

    def scan_ticker(self, ticker: str) -> List[Dict]:
        """
        Scan a single ticker for zone touches.

        Args:
            ticker: Stock ticker symbol

        Returns:
            List of alert dictionaries to send
        """
        alerts_to_send = []

        try:
            # Get current price data
            stock = yf.Ticker(ticker)
            hist = stock.history(period='1d', interval='1m')

            if hist.empty:
                logger.warning(f"No price data for {ticker}")
                return []

            current_price = hist['Close'].iloc[-1]
            current_candle = hist.iloc[-1]

            # Get active zones for this ticker
            zones = self.db.get_active_zones(ticker=ticker, min_strength=40.0)

            for zone in zones:
                # Check if price is testing zone
                test_info = self.analyzer.analyze_zone_test(
                    zone=zone,
                    current_price=current_price,
                    current_candle=current_candle
                )

                if not test_info:
                    continue  # No test occurring

                # Get test history
                test_history = self.db.get_zone_tests(zone['id'])

                # Calculate zone quality
                quality = self.analyzer.calculate_zone_quality(
                    zone=zone,
                    test_history=test_history,
                    current_price=current_price
                )

                # Check if alert should be sent
                if self.analyzer.should_send_alert(zone, current_price, test_info, quality):
                    # Check for recent alerts (cooldown)
                    recent_alerts = self.db.get_recent_alerts(
                        ticker=ticker,
                        hours=self.alert_cooldown_hours
                    )

                    # Check if this zone was alerted recently
                    already_alerted = any(
                        a['zone_id'] == zone['id'] for a in recent_alerts
                    )

                    if not already_alerted:
                        alert_data = {
                            'zone_id': zone['id'],
                            'ticker': ticker,
                            'alert_type': self._get_alert_type(zone['zone_type'], test_info['test_type']),
                            'alert_price': current_price,
                            'zone_type': zone['zone_type'],
                            'zone_strength': zone['strength_score'],
                            'setup_quality': quality,
                            'zone_data': zone,
                            'test_data': test_info
                        }

                        alerts_to_send.append(alert_data)

                # Record the test
                test_data = {
                    'zone_id': zone['id'],
                    'test_date': datetime.now(),
                    'test_price': current_price,
                    'test_type': test_info['test_type'],
                    'penetration_percent': test_info['penetration_pct'],
                    'test_volume': test_info['test_volume'],
                    'held': test_info['test_type'] != 'BREAK',
                    'broke_through': test_info['test_type'] == 'BREAK'
                }

                self.db.add_zone_test(test_data)

                # Update zone status if needed
                if test_info['test_type'] == 'BREAK':
                    self.db.update_zone_status(zone['id'], 'BROKEN')
                elif test_info['test_type'] == 'REJECTION':
                    self.db.update_zone_status(zone['id'], 'TESTED')

        except Exception as e:
            logger.error(f"Error scanning {ticker}: {e}")

        return alerts_to_send

    def _get_alert_type(self, zone_type: str, test_type: str) -> str:
        """Determine alert type based on zone and test type."""
        if zone_type == 'DEMAND':
            if test_type in ['TOUCH', 'PENETRATION']:
                return 'PRICE_ENTERING_DEMAND'
            elif test_type == 'REJECTION':
                return 'ZONE_BOUNCE'
            elif test_type == 'BREAK':
                return 'ZONE_BREAK'
        else:  # SUPPLY
            if test_type in ['TOUCH', 'PENETRATION']:
                return 'PRICE_ENTERING_SUPPLY'
            elif test_type == 'REJECTION':
                return 'ZONE_BOUNCE'
            elif test_type == 'BREAK':
                return 'ZONE_BREAK'

        return 'PRICE_AT_DEMAND' if zone_type == 'DEMAND' else 'PRICE_AT_SUPPLY'

    def scan_watchlist(self, tickers: List[str]) -> List[Dict]:
        """
        Scan multiple tickers for zone touches.

        Args:
            tickers: List of ticker symbols

        Returns:
            List of all alerts to send
        """
        all_alerts = []

        for ticker in tickers:
            alerts = self.scan_ticker(ticker)
            all_alerts.extend(alerts)

        return all_alerts
```

### 5. AlertManager

```python
"""
Formats and sends Telegram alerts for supply/demand zone events.
"""

from typing import Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class SupplyDemandAlertManager:
    """
    Manages Telegram alerts for supply/demand zone events.

    Integrates with existing TelegramNotifier infrastructure.
    """

    def __init__(self, telegram_notifier, db_manager: ZoneDatabaseManager):
        """
        Initialize alert manager.

        Args:
            telegram_notifier: Existing TelegramNotifier instance
            db_manager: ZoneDatabaseManager instance
        """
        self.telegram = telegram_notifier
        self.db = db_manager

    def send_zone_alert(self, alert_data: Dict[str, Any]) -> bool:
        """
        Format and send a zone alert via Telegram.

        Args:
            alert_data: Alert information dictionary

        Returns:
            True if sent successfully
        """
        try:
            # Format message based on alert type
            message = self._format_alert_message(alert_data)

            # Send via Telegram
            message_id = self.telegram.send_custom_message(message, parse_mode="Markdown")

            if message_id:
                # Log alert to database
                alert_data['telegram_message_id'] = message_id
                alert_data['status'] = 'sent'
                self.db.add_alert(alert_data)

                logger.info(f"Sent {alert_data['alert_type']} alert for {alert_data['ticker']}")
                return True
            else:
                logger.error(f"Failed to send alert for {alert_data['ticker']}")
                return False

        except Exception as e:
            logger.error(f"Error sending zone alert: {e}")
            return False

    def _format_alert_message(self, alert_data: Dict[str, Any]) -> str:
        """Format alert message with all relevant zone information."""
        zone = alert_data['zone_data']
        test = alert_data['test_data']
        ticker = alert_data['ticker']
        alert_type = alert_data['alert_type']
        quality = alert_data['setup_quality']

        # Emoji and title based on alert type
        if 'DEMAND' in alert_type:
            emoji = "🟢"
            title = "BUYING OPPORTUNITY"
            direction = "into DEMAND zone"
        else:
            emoji = "🔴"
            title = "SELLING OPPORTUNITY"
            direction = "into SUPPLY zone"

        # Quality emoji
        quality_emoji = {
            'HIGH': '⭐⭐⭐',
            'MEDIUM': '⭐⭐',
            'LOW': '⭐'
        }.get(quality, '⭐')

        message = (
            f"{emoji} *{title}*\n\n"
            f"📈 Ticker: *{ticker}*\n"
            f"💰 Current Price: `${alert_data['alert_price']:.2f}`\n\n"
            f"📊 Zone Details:\n"
            f"  • Type: `{zone['zone_type']}`\n"
            f"  • Range: `${zone['zone_bottom']:.2f}` - `${zone['zone_top']:.2f}`\n"
            f"  • Midpoint: `${zone['zone_midpoint']:.2f}`\n"
            f"  • Strength: `{zone['strength_score']:.0f}/100`\n"
            f"  • Tests: `{zone['test_count']}`\n"
            f"  • Status: `{zone['status']}`\n\n"
            f"🎯 Setup Quality: {quality_emoji} `{quality}`\n\n"
            f"📉 Test Information:\n"
            f"  • Type: `{test['test_type']}`\n"
            f"  • Penetration: `{test['penetration_pct']:.1f}%`\n"
            f"  • Volume: `{test['test_volume']:,}`\n\n"
        )

        # Add trading suggestions
        if zone['zone_type'] == 'DEMAND':
            message += (
                f"💡 *Potential Trade Setup:*\n"
                f"  • Entry: Around `${zone['zone_midpoint']:.2f}`\n"
                f"  • Stop Loss: Below `${zone['zone_bottom']:.2f}`\n"
                f"  • Target: Previous high / 2:1 R:R\n\n"
            )
        else:  # SUPPLY
            message += (
                f"💡 *Potential Trade Setup:*\n"
                f"  • Entry: Around `${zone['zone_midpoint']:.2f}`\n"
                f"  • Stop Loss: Above `${zone['zone_top']:.2f}`\n"
                f"  • Target: Previous low / 2:1 R:R\n\n"
            )

        # Add timestamp
        message += f"🕐 Alert Time: `{datetime.now().strftime('%Y-%m-%d %I:%M %p')}`\n"

        # Add TradingView link
        message += f"\n[View on TradingView](https://www.tradingview.com/chart/?symbol={ticker})"

        return message
```

### 6. Scanner Service

```python
"""
Scheduled scanner service that orchestrates zone detection and monitoring.
"""

from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
import logging
from typing import List

logger = logging.getLogger(__name__)


class SupplyDemandScanner:
    """
    Orchestrates scheduled scanning for zone detection and price monitoring.
    """

    def __init__(
        self,
        zone_detector: ZoneDetector,
        price_monitor: PriceMonitor,
        alert_manager: SupplyDemandAlertManager,
        db_manager: ZoneDatabaseManager,
        tradingview_db_manager
    ):
        """Initialize scanner with all required components."""
        self.zone_detector = zone_detector
        self.price_monitor = price_monitor
        self.alert_manager = alert_manager
        self.db = db_manager
        self.tv_db = tradingview_db_manager

        self.scheduler = BackgroundScheduler()

    def start(self):
        """Start scheduled scanning jobs."""
        # Detect new zones: Daily at 4:30 PM (after market close)
        self.scheduler.add_job(
            self.run_zone_detection,
            'cron',
            hour=16,
            minute=30,
            id='zone_detection'
        )

        # Monitor prices: Every 15 minutes during market hours
        self.scheduler.add_job(
            self.run_price_monitoring,
            'cron',
            day_of_week='mon-fri',
            hour='9-16',
            minute='*/15',
            id='price_monitoring'
        )

        # Cleanup old/broken zones: Weekly on Sunday
        self.scheduler.add_job(
            self.cleanup_old_zones,
            'cron',
            day_of_week='sun',
            hour=0,
            minute=0,
            id='zone_cleanup'
        )

        self.scheduler.start()
        logger.info("Supply/Demand Scanner started")

    def stop(self):
        """Stop scheduler."""
        self.scheduler.shutdown()
        logger.info("Supply/Demand Scanner stopped")

    def run_zone_detection(self):
        """Detect zones for all watchlist stocks."""
        start_time = datetime.now()
        scan_id = self._log_scan_start('ZONE_DETECTION')

        try:
            # Get tickers from TradingView watchlists
            tickers = self._get_watchlist_tickers()

            zones_found = 0
            zones_updated = 0

            for ticker in tickers:
                try:
                    # Download price data
                    df = yf.Ticker(ticker).history(period='6mo', interval='1d')

                    if df.empty:
                        continue

                    # Detect zones
                    zones = self.zone_detector.detect_zones(ticker, df, timeframe='1d')

                    # Save to database
                    for zone in zones:
                        zone_dict = {
                            'ticker': zone.ticker,
                            'zone_type': zone.zone_type,
                            'timeframe': zone.timeframe,
                            'zone_top': zone.zone_top,
                            'zone_bottom': zone.zone_bottom,
                            'zone_midpoint': zone.zone_midpoint,
                            'formed_date': zone.formed_date,
                            'approach_volume': zone.approach_volume,
                            'departure_volume': zone.departure_volume,
                            'strength_score': zone.strength_score,
                            'volume_ratio': zone.departure_volume / zone.approach_volume if zone.approach_volume > 0 else 0
                        }

                        self.db.add_zone(zone_dict)
                        zones_found += 1

                except Exception as e:
                    logger.error(f"Error detecting zones for {ticker}: {e}")

            duration = (datetime.now() - start_time).total_seconds()

            self._log_scan_complete(scan_id, {
                'tickers_scanned': len(tickers),
                'zones_found': zones_found,
                'zones_updated': zones_updated,
                'duration_seconds': duration,
                'status': 'success'
            })

            logger.info(f"Zone detection complete: {zones_found} zones found in {duration:.1f}s")

        except Exception as e:
            logger.error(f"Zone detection failed: {e}")
            self._log_scan_complete(scan_id, {
                'status': 'failed',
                'errors': str(e)
            })

    def run_price_monitoring(self):
        """Monitor prices against active zones."""
        start_time = datetime.now()
        scan_id = self._log_scan_start('PRICE_MONITORING')

        try:
            # Get tickers with active zones
            tickers = self._get_tickers_with_zones()

            alerts_sent = 0

            # Scan each ticker
            alerts = self.price_monitor.scan_watchlist(tickers)

            # Send alerts
            for alert in alerts:
                if self.alert_manager.send_zone_alert(alert):
                    alerts_sent += 1

            duration = (datetime.now() - start_time).total_seconds()

            self._log_scan_complete(scan_id, {
                'tickers_scanned': len(tickers),
                'alerts_sent': alerts_sent,
                'duration_seconds': duration,
                'status': 'success'
            })

            logger.info(f"Price monitoring complete: {alerts_sent} alerts sent")

        except Exception as e:
            logger.error(f"Price monitoring failed: {e}")
            self._log_scan_complete(scan_id, {
                'status': 'failed',
                'errors': str(e)
            })

    def cleanup_old_zones(self):
        """Deactivate old or broken zones."""
        # Implementation for cleanup
        pass

    def _get_watchlist_tickers(self) -> List[str]:
        """Get all tickers from TradingView watchlists."""
        # Query TradingView DB for watchlist symbols
        watchlists = self.tv_db.get_all_watchlists(active_only=True)
        tickers = []

        for watchlist in watchlists:
            symbols = self.tv_db.get_watchlist_symbols(watchlist['id'])
            tickers.extend([s['symbol'] for s in symbols])

        return list(set(tickers))  # Remove duplicates

    def _get_tickers_with_zones(self) -> List[str]:
        """Get tickers that have active zones."""
        zones = self.db.get_active_zones()
        tickers = list(set([z['ticker'] for z in zones]))
        return tickers

    def _log_scan_start(self, scan_type: str) -> int:
        """Log scan start and return scan ID."""
        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        INSERT INTO sd_scan_log (scan_type, status)
                        VALUES (%s, 'running')
                        RETURNING id
                    """, (scan_type,))
                    return cur.fetchone()[0]
        finally:
            conn.close()

    def _log_scan_complete(self, scan_id: int, stats: Dict):
        """Update scan log with completion stats."""
        conn = self.db.get_connection()
        try:
            with conn:
                with conn.cursor() as cur:
                    cur.execute("""
                        UPDATE sd_scan_log
                        SET tickers_scanned = %s,
                            zones_found = %s,
                            zones_updated = %s,
                            alerts_sent = %s,
                            duration_seconds = %s,
                            status = %s,
                            errors = %s
                        WHERE id = %s
                    """, (
                        stats.get('tickers_scanned', 0),
                        stats.get('zones_found', 0),
                        stats.get('zones_updated', 0),
                        stats.get('alerts_sent', 0),
                        stats.get('duration_seconds', 0),
                        stats.get('status', 'success'),
                        stats.get('errors'),
                        scan_id
                    ))
        finally:
            conn.close()
```

---

## Data Flow

### Zone Detection Flow

```
1. Scheduler triggers zone detection (daily after market close)
   ↓
2. Get tickers from TradingView watchlists
   ↓
3. For each ticker:
   a. Download OHLCV data (6 months history)
   b. Run ZoneDetector.detect_zones()
   c. Save detected zones to database
   ↓
4. Log scan results to sd_scan_log table
```

### Price Monitoring Flow

```
1. Scheduler triggers price monitoring (every 15 min during market hours)
   ↓
2. Get tickers with active zones
   ↓
3. For each ticker:
   a. Fetch current price (1-minute data)
   b. Check each active zone for price intersection
   c. If zone touched:
      - Analyze test type (touch/penetration/rejection/break)
      - Calculate zone quality score
      - Check alert cooldown
      - Create alert if conditions met
   ↓
4. Send alerts via Telegram
   ↓
5. Record zone tests in database
   ↓
6. Update zone status if needed (TESTED, BROKEN, etc.)
```

### Alert Flow

```
Price touches zone
   ↓
ZoneAnalyzer determines test type
   ↓
Calculate setup quality (HIGH/MEDIUM/LOW)
   ↓
Check alert cooldown (prevent spam)
   ↓
Format alert message with:
   - Zone details
   - Current price
   - Strength score
   - Trading suggestions
   ↓
Send via Telegram
   ↓
Log alert to database
```

---

## Integration Points

### Existing Infrastructure

1. **PostgreSQL Database** (already configured)
   - Connection pool available
   - DB credentials in .env

2. **Telegram Bot** (already implemented)
   - Uses `src/telegram_notifier.py`
   - Bot token and chat ID configured

3. **TradingView Watchlists** (already in DB)
   - Table: `tv_watchlists`
   - Table: `tv_watchlist_symbols`
   - Manager: `TradingViewDBManager`

4. **Scheduler** (APScheduler already in requirements)
   - Used for other background tasks

### New Components to Create

1. `src/supply_demand/zone_detector.py`
2. `src/supply_demand/zone_analyzer.py`
3. `src/supply_demand/zone_db_manager.py`
4. `src/supply_demand/price_monitor.py`
5. `src/supply_demand/alert_manager.py`
6. `src/supply_demand/scanner_service.py`
7. `src/supply_demand/__init__.py`
8. `src/supply_demand_schema.sql` (database schema)

### Streamlit Dashboard Page

Create `supply_demand_zones_page.py`:
- View active zones by ticker
- Zone strength heatmap
- Test history charts
- Manual zone detection trigger
- Alert history table
- Performance analytics

---

## Deployment Strategy

### Phase 1: Core Implementation
1. Create database schema (run SQL script)
2. Implement ZoneDetector class
3. Implement ZoneAnalyzer class
4. Implement ZoneDatabaseManager class
5. Unit tests for zone detection algorithm

### Phase 2: Monitoring & Alerts
1. Implement PriceMonitor class
2. Implement AlertManager class
3. Integration tests with Telegram
4. Manual testing with real tickers

### Phase 3: Automation
1. Implement ScannerService class
2. Set up scheduled jobs
3. Dashboard UI page
4. Production deployment

### Phase 4: Optimization
1. Performance tuning
2. Alert quality improvements
3. Multi-timeframe analysis
4. Historical backtesting

---

## Configuration

### Environment Variables

Add to `.env`:
```bash
# Supply/Demand Scanner Settings
SD_ZONE_DETECTION_ENABLED=true
SD_PRICE_MONITORING_ENABLED=true
SD_MIN_ZONE_STRENGTH=40.0
SD_ALERT_COOLDOWN_HOURS=24
SD_SWING_LOOKBACK=5
SD_MAX_ZONE_WIDTH_PCT=3.0
SD_VOLUME_THRESHOLD=1.2
```

### Watchlist Selection

Users can select which TradingView watchlists to scan via:
- Dashboard UI checkbox selection
- Database flag `tv_watchlists.is_active`

---

## Performance Considerations

### Optimization Strategies

1. **Zone Detection:** Run once daily (not real-time)
2. **Price Monitoring:** Only tickers with active zones
3. **Database Indexes:** All critical queries indexed
4. **Alert Cooldown:** Prevent duplicate alerts
5. **Zone Cleanup:** Weekly removal of old/broken zones
6. **Caching:** Cache zone data during monitoring window

### Scalability

- **100 stocks:** ~2 minutes for detection, <10 seconds for monitoring
- **500 stocks:** ~10 minutes for detection, ~30 seconds for monitoring
- **1000 stocks:** ~20 minutes for detection, ~60 seconds for monitoring

---

## Testing Strategy

### Unit Tests

```python
# test_zone_detector.py
def test_swing_high_detection():
    # Test swing high identification
    pass

def test_supply_zone_formation():
    # Test supply zone detection logic
    pass

def test_demand_zone_formation():
    # Test demand zone detection logic
    pass

def test_zone_strength_calculation():
    # Test strength scoring
    pass
```

### Integration Tests

```python
# test_scanner_integration.py
def test_full_detection_flow():
    # Test end-to-end zone detection
    pass

def test_alert_generation():
    # Test alert creation and sending
    pass

def test_database_operations():
    # Test all CRUD operations
    pass
```

---

## Success Metrics

### KPIs to Track

1. **Zone Quality:** % of HIGH quality zones detected
2. **Alert Accuracy:** % of alerted zones that produce profitable setups
3. **Test Success Rate:** % of zones that hold on first test
4. **Average Zone Strength:** Mean strength score of detected zones
5. **Alert Response Time:** Time from zone touch to alert sent
6. **False Positive Rate:** Alerts that don't result in meaningful price action

---

## Future Enhancements

1. **Multi-timeframe confluence:** Detect when zones align across timeframes
2. **Machine learning:** Predict zone strength using historical data
3. **Options integration:** Suggest options strategies for zone plays
4. **Backtesting framework:** Test zone detection parameters on historical data
5. **Risk management:** Auto-calculate position sizing based on zone width
6. **Pattern recognition:** Identify specific price patterns within zones

---

## Conclusion

This architecture provides a robust, scalable supply/demand zone detection system that integrates seamlessly with the existing Magnus trading dashboard infrastructure. The modular design allows for incremental development and testing, with clear separation of concerns and comprehensive error handling.

The system leverages proven technical analysis principles combined with institutional volume analysis to identify high-probability trade setups, delivering actionable alerts directly to traders via Telegram.
