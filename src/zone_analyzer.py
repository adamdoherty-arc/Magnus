"""
Zone Quality Analysis
Calculates strength scores and analyzes zone quality for trading decisions
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ZoneAnalyzer:
    """
    Analyzes supply/demand zone quality and calculates strength scores

    Strength scoring factors:
    - Volume ratio (departure vs approach)
    - Zone freshness (untested zones are strongest)
    - Test history (how many times tested, outcomes)
    - Time since formation (recent zones are stronger)
    - Zone tightness (tighter = better)
    - Current price distance from zone
    """

    def __init__(
        self,
        fresh_zone_bonus: int = 30,
        volume_weight: float = 0.25,
        test_penalty: int = 15,
        age_weight: float = 0.10,
        tightness_weight: float = 0.15
    ):
        """
        Initialize analyzer

        Args:
            fresh_zone_bonus: Bonus points for untested zones (default: 30)
            volume_weight: Weight for volume ratio in scoring (default: 0.25)
            test_penalty: Penalty per failed test (default: 15)
            age_weight: Weight for age in scoring (default: 0.10)
            tightness_weight: Weight for zone tightness (default: 0.15)
        """
        self.fresh_zone_bonus = fresh_zone_bonus
        self.volume_weight = volume_weight
        self.test_penalty = test_penalty
        self.age_weight = age_weight
        self.tightness_weight = tightness_weight

    def analyze_zone(
        self,
        zone: Dict,
        current_price: float,
        test_history: Optional[List[Dict]] = None
    ) -> Dict:
        """
        Analyze zone quality and update strength score

        Args:
            zone: Zone dictionary from ZoneDetector
            current_price: Current stock price
            test_history: List of previous test results (optional)

        Returns:
            Updated zone dictionary with refined strength score and analysis
        """

        # Calculate comprehensive strength score
        strength_score = self._calculate_strength_score(zone, test_history)

        # Determine zone state
        zone_state = self._determine_zone_state(zone, test_history, current_price)

        # Calculate distance from current price
        distance_pct = self._calculate_price_distance(zone, current_price)

        # Calculate risk/reward if near zone
        risk_reward = self._calculate_risk_reward(zone, current_price)

        # Generate trading recommendation
        recommendation = self._generate_recommendation(
            zone,
            current_price,
            strength_score,
            zone_state,
            distance_pct
        )

        # Update zone with analysis
        zone['strength_score'] = strength_score
        zone['status'] = zone_state
        zone['distance_from_price_pct'] = distance_pct
        zone['risk_reward_ratio'] = risk_reward
        zone['recommendation'] = recommendation
        zone['analyzed_at'] = datetime.now()

        return zone

    def _calculate_strength_score(
        self,
        zone: Dict,
        test_history: Optional[List[Dict]] = None
    ) -> int:
        """
        Calculate comprehensive strength score (0-100)

        Components:
        1. Volume ratio (0-30 points)
        2. Freshness bonus (0-30 points)
        3. Age factor (0-15 points)
        4. Tightness factor (0-15 points)
        5. Test history penalty (0 to -45 points)
        """

        score = 0

        # 1. Volume ratio component (0-30 points)
        volume_ratio = zone.get('volume_ratio', 1.0)
        volume_score = min(30, volume_ratio * 10)  # 3.0x ratio = 30 points
        score += volume_score

        # 2. Freshness bonus (0-30 points)
        if zone.get('test_count', 0) == 0:
            score += self.fresh_zone_bonus

        # 3. Age factor (0-15 points) - newer zones are stronger
        formed_date = zone.get('formed_date')
        if formed_date:
            if isinstance(formed_date, str):
                formed_date = pd.to_datetime(formed_date)

            days_old = (datetime.now() - formed_date.replace(tzinfo=None)).days

            if days_old <= 7:
                age_score = 15  # Very recent
            elif days_old <= 30:
                age_score = 10  # Recent
            elif days_old <= 90:
                age_score = 5   # Moderate
            else:
                age_score = 2   # Old

            score += age_score

        # 4. Tightness factor (0-15 points) - tighter zones are stronger
        zone_size = zone['zone_top'] - zone['zone_bottom']
        zone_size_pct = (zone_size / zone['zone_bottom']) * 100

        if zone_size_pct < 1.0:
            tightness_score = 15  # Very tight
        elif zone_size_pct < 2.0:
            tightness_score = 10  # Tight
        elif zone_size_pct < 3.0:
            tightness_score = 5   # Moderate
        else:
            tightness_score = 2   # Loose

        score += tightness_score

        # 5. Test history penalty
        if test_history:
            failed_tests = sum(1 for t in test_history if not t.get('held', False))
            penalty = failed_tests * self.test_penalty
            score -= penalty

        # Bonus: Strong impulse move
        impulse_bonus = min(20, zone.get('volume_ratio', 1.0) * 5)
        score += impulse_bonus

        # Clamp to 0-100
        return max(0, min(100, int(score)))

    def _determine_zone_state(
        self,
        zone: Dict,
        test_history: Optional[List[Dict]],
        current_price: float
    ) -> str:
        """
        Determine zone state: FRESH, TESTED, WEAK, BROKEN

        States:
        - FRESH: Never tested (most reliable)
        - TESTED: Tested 1-2 times and held
        - WEAK: Tested 3+ times (losing strength)
        - BROKEN: Price decisively penetrated zone
        """

        test_count = zone.get('test_count', 0)

        # Check if broken
        if self._is_zone_broken(zone, current_price):
            return 'BROKEN'

        # Check test history
        if test_count == 0:
            return 'FRESH'
        elif test_count <= 2:
            return 'TESTED'
        else:
            return 'WEAK'

    def _is_zone_broken(self, zone: Dict, current_price: float) -> bool:
        """
        Check if zone has been broken

        A zone is broken when:
        - Demand zone: Price closes significantly below zone bottom
        - Supply zone: Price closes significantly above zone top
        """

        zone_type = zone['zone_type']
        zone_top = zone['zone_top']
        zone_bottom = zone['zone_bottom']
        zone_size = zone_top - zone_bottom

        # Require decisive break (close beyond zone by at least zone height)
        if zone_type == 'DEMAND':
            # Demand broken if price well below bottom
            return current_price < (zone_bottom - zone_size * 0.5)
        else:
            # Supply broken if price well above top
            return current_price > (zone_top + zone_size * 0.5)

    def _calculate_price_distance(self, zone: Dict, current_price: float) -> float:
        """
        Calculate distance from current price to zone (%)

        Returns:
        - Positive: Price above zone
        - Negative: Price below zone
        - 0: Price in zone
        """

        zone_top = zone['zone_top']
        zone_bottom = zone['zone_bottom']

        if current_price > zone_top:
            # Price above zone
            distance = ((current_price - zone_top) / zone_top) * 100
            return distance
        elif current_price < zone_bottom:
            # Price below zone
            distance = ((current_price - zone_bottom) / zone_bottom) * 100
            return distance
        else:
            # Price in zone
            return 0.0

    def _calculate_risk_reward(self, zone: Dict, current_price: float) -> Optional[float]:
        """
        Calculate risk/reward ratio for potential trade

        For demand zones: Buy at zone, sell at previous high
        For supply zones: Sell at zone, cover at previous low

        Returns:
            Risk/reward ratio or None if not applicable
        """

        zone_type = zone['zone_type']
        zone_top = zone['zone_top']
        zone_bottom = zone['zone_bottom']
        zone_mid = zone['zone_midpoint']

        # Only calculate if price is near zone (within 5%)
        distance_pct = abs(self._calculate_price_distance(zone, current_price))
        if distance_pct > 5.0:
            return None

        # Estimate risk and reward
        if zone_type == 'DEMAND':
            # Buy at zone bottom, stop below zone
            entry = zone_bottom
            stop = zone_bottom * 0.98  # 2% stop loss
            target = zone_top * 1.05   # Target 5% above zone

            risk = entry - stop
            reward = target - entry

        else:  # SUPPLY
            # Sell at zone top, stop above zone
            entry = zone_top
            stop = zone_top * 1.02     # 2% stop loss
            target = zone_bottom * 0.95 # Target 5% below zone

            risk = stop - entry
            reward = entry - target

        if risk > 0:
            return reward / risk
        else:
            return None

    def _generate_recommendation(
        self,
        zone: Dict,
        current_price: float,
        strength_score: int,
        zone_state: str,
        distance_pct: float
    ) -> Dict:
        """
        Generate trading recommendation

        Returns:
            Dictionary with action, priority, and reasoning
        """

        zone_type = zone['zone_type']

        # Default: no action
        recommendation = {
            'action': 'WATCH',
            'priority': 'LOW',
            'reasons': []
        }

        # Zone broken - no trade
        if zone_state == 'BROKEN':
            recommendation['action'] = 'AVOID'
            recommendation['reasons'].append('Zone broken')
            return recommendation

        # Weak zone - be cautious
        if zone_state == 'WEAK':
            recommendation['reasons'].append('Zone tested multiple times')
            recommendation['priority'] = 'LOW'

        # Check strength score
        if strength_score < 50:
            recommendation['reasons'].append(f'Low strength score ({strength_score}/100)')
            return recommendation

        # Check price proximity
        abs_distance = abs(distance_pct)

        if zone_type == 'DEMAND':
            # For demand zones: look for buying opportunities

            if distance_pct <= 0 and abs_distance <= 2:
                # Price at or slightly below zone
                recommendation['action'] = 'BUY'
                recommendation['priority'] = 'HIGH' if strength_score >= 75 else 'MEDIUM'
                recommendation['reasons'].append('Price at demand zone')

                if zone_state == 'FRESH':
                    recommendation['reasons'].append('Fresh zone (untested)')
                    recommendation['priority'] = 'HIGH'

            elif distance_pct > 0 and abs_distance <= 5:
                # Price slightly above zone (may return)
                recommendation['action'] = 'WATCH'
                recommendation['priority'] = 'MEDIUM'
                recommendation['reasons'].append('Price near demand zone')

            elif distance_pct < 0 and abs_distance <= 5:
                # Price falling toward zone
                recommendation['action'] = 'PREPARE'
                recommendation['priority'] = 'MEDIUM'
                recommendation['reasons'].append('Price approaching demand zone')

        else:  # SUPPLY zone
            # For supply zones: look for shorting/selling opportunities

            if distance_pct >= 0 and abs_distance <= 2:
                # Price at or slightly above zone
                recommendation['action'] = 'SELL'
                recommendation['priority'] = 'HIGH' if strength_score >= 75 else 'MEDIUM'
                recommendation['reasons'].append('Price at supply zone')

                if zone_state == 'FRESH':
                    recommendation['reasons'].append('Fresh zone (untested)')
                    recommendation['priority'] = 'HIGH'

            elif distance_pct < 0 and abs_distance <= 5:
                # Price slightly below zone (may return)
                recommendation['action'] = 'WATCH'
                recommendation['priority'] = 'MEDIUM'
                recommendation['reasons'].append('Price near supply zone')

            elif distance_pct > 0 and abs_distance <= 5:
                # Price rising toward zone
                recommendation['action'] = 'PREPARE'
                recommendation['priority'] = 'MEDIUM'
                recommendation['reasons'].append('Price approaching supply zone')

        # Add strength info
        if strength_score >= 75:
            recommendation['reasons'].append(f'Strong zone ({strength_score}/100)')

        return recommendation

    def batch_analyze_zones(
        self,
        zones: List[Dict],
        current_prices: Dict[str, float],
        test_histories: Optional[Dict[int, List[Dict]]] = None
    ) -> List[Dict]:
        """
        Analyze multiple zones in batch

        Args:
            zones: List of zone dictionaries
            current_prices: Dict mapping symbol to current price
            test_histories: Optional dict mapping zone_id to test history

        Returns:
            List of analyzed zones
        """

        analyzed_zones = []

        for zone in zones:
            symbol = zone['symbol']
            current_price = current_prices.get(symbol)

            if current_price is None:
                logger.warning(f"No current price for {symbol}, skipping analysis")
                continue

            zone_id = zone.get('id')
            test_history = None
            if test_histories and zone_id:
                test_history = test_histories.get(zone_id)

            analyzed_zone = self.analyze_zone(zone, current_price, test_history)
            analyzed_zones.append(analyzed_zone)

        return analyzed_zones

    def get_high_priority_zones(
        self,
        zones: List[Dict],
        min_strength: int = 70,
        actions: Optional[List[str]] = None
    ) -> List[Dict]:
        """
        Filter zones for high-priority trading opportunities

        Args:
            zones: List of analyzed zones
            min_strength: Minimum strength score (default: 70)
            actions: List of actions to filter (e.g., ['BUY', 'SELL'])

        Returns:
            Filtered and sorted list of zones
        """

        if actions is None:
            actions = ['BUY', 'SELL', 'PREPARE']

        # Filter by criteria
        filtered = []

        for zone in zones:
            # Check strength
            if zone.get('strength_score', 0) < min_strength:
                continue

            # Check recommendation
            recommendation = zone.get('recommendation', {})
            if recommendation.get('action') not in actions:
                continue

            # Check priority
            if recommendation.get('priority') == 'LOW':
                continue

            filtered.append(zone)

        # Sort by strength score (highest first)
        filtered.sort(key=lambda z: z.get('strength_score', 0), reverse=True)

        return filtered


if __name__ == "__main__":
    # Test analyzer
    logging.basicConfig(level=logging.INFO)

    # Sample zone
    sample_zone = {
        'symbol': 'AAPL',
        'zone_type': 'DEMAND',
        'zone_top': 180.50,
        'zone_bottom': 178.00,
        'zone_midpoint': 179.25,
        'formed_date': datetime.now() - timedelta(days=5),
        'volume_ratio': 2.5,
        'test_count': 0,
        'status': 'FRESH'
    }

    analyzer = ZoneAnalyzer()

    # Test with price at zone
    current_price = 178.50

    print("Analyzing sample zone...")
    analyzed_zone = analyzer.analyze_zone(sample_zone, current_price)

    print(f"\nZone Analysis for {analyzed_zone['symbol']}:")
    print(f"  Type: {analyzed_zone['zone_type']}")
    print(f"  Range: ${analyzed_zone['zone_bottom']:.2f} - ${analyzed_zone['zone_top']:.2f}")
    print(f"  Current Price: ${current_price:.2f}")
    print(f"  Strength Score: {analyzed_zone['strength_score']}/100")
    print(f"  Status: {analyzed_zone['status']}")
    print(f"  Distance: {analyzed_zone['distance_from_price_pct']:.2f}%")
    print(f"  R/R Ratio: {analyzed_zone.get('risk_reward_ratio', 'N/A')}")
    print(f"\nRecommendation:")
    print(f"  Action: {analyzed_zone['recommendation']['action']}")
    print(f"  Priority: {analyzed_zone['recommendation']['priority']}")
    print(f"  Reasons: {', '.join(analyzed_zone['recommendation']['reasons'])}")
