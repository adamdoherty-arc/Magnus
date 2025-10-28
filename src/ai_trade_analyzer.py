"""AI-powered trade analyzer for wheel strategy positions"""

from datetime import datetime, timedelta
from typing import Dict, List, Any
import yfinance as yf

class AITradeAnalyzer:
    """Analyzes trades and provides AI recommendations"""

    def analyze_csp(self, symbol: str, strike: float, expiration: str, premium_collected: float,
                    current_value: float, days_to_expiry: int) -> Dict[str, Any]:
        """
        Analyze a cash-secured put position and provide recommendations
        """

        # Calculate profit metrics
        current_cost_to_close = abs(current_value)
        profit_if_closed = premium_collected - current_cost_to_close
        profit_percentage = (profit_if_closed / premium_collected * 100) if premium_collected > 0 else 0

        # Get current stock price
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.info.get('currentPrice', strike)

            # Calculate moneyness
            moneyness_pct = ((current_price - strike) / strike) * 100
            is_itm = current_price < strike
        except:
            current_price = strike
            moneyness_pct = 0
            is_itm = False

        # Generate recommendation
        recommendation = self._generate_csp_recommendation(
            profit_percentage, days_to_expiry, moneyness_pct, is_itm
        )

        # Risk assessment
        risk_level = self._assess_risk(is_itm, days_to_expiry, moneyness_pct)

        return {
            'symbol': symbol,
            'current_price': current_price,
            'strike': strike,
            'is_itm': is_itm,
            'moneyness_pct': moneyness_pct,
            'profit_if_closed': profit_if_closed,
            'profit_percentage': profit_percentage,
            'cost_to_close': current_cost_to_close,
            'days_to_expiry': days_to_expiry,
            'recommendation': recommendation,
            'risk_level': risk_level,
            'annual_return': self._calculate_annual_return(profit_percentage, days_to_expiry)
        }

    def _generate_csp_recommendation(self, profit_pct: float, days_to_expiry: int,
                                     moneyness_pct: float, is_itm: bool) -> Dict[str, str]:
        """Generate recommendation based on position metrics"""

        # Aggressive profit-taking strategy for maximum returns
        if profit_pct >= 75:
            return {
                'action': 'BUY_BACK_IMMEDIATELY',
                'reason': f'Captured {profit_pct:.1f}% of max profit - Excellent return!',
                'detail': 'Close position and redeploy capital for higher annualized returns.',
                'urgency': 'HIGH',
                'emoji': '🎯'
            }

        elif profit_pct >= 50 and days_to_expiry > 7:
            return {
                'action': 'BUY_BACK_RECOMMENDED',
                'reason': f'{profit_pct:.1f}% profit with {days_to_expiry} days remaining',
                'detail': 'Strong profit captured. Consider closing to free capital for new trades.',
                'urgency': 'MEDIUM',
                'emoji': '✅'
            }

        elif profit_pct >= 25 and days_to_expiry > 14:
            return {
                'action': 'MONITOR_CLOSELY',
                'reason': f'{profit_pct:.1f}% profit - Watch for 50% target',
                'detail': 'Set alert for 50% profit target. Good candidate for early exit.',
                'urgency': 'LOW',
                'emoji': '👀'
            }

        elif is_itm and days_to_expiry < 7:
            return {
                'action': 'PREPARE_FOR_ASSIGNMENT',
                'reason': f'ITM by {abs(moneyness_pct):.1f}% with {days_to_expiry} days left',
                'detail': 'High probability of assignment. Prepare to take shares or roll.',
                'urgency': 'HIGH',
                'emoji': '⚠️'
            }

        elif days_to_expiry <= 3:
            return {
                'action': 'HOLD_TO_EXPIRY',
                'reason': f'Only {days_to_expiry} days remaining',
                'detail': 'Maximum theta decay occurring. Hold unless ITM.',
                'urgency': 'LOW',
                'emoji': '⏰'
            }

        else:
            return {
                'action': 'HOLD_POSITION',
                'reason': f'{profit_pct:.1f}% profit captured so far',
                'detail': 'Continue collecting theta decay. Monitor daily.',
                'urgency': 'LOW',
                'emoji': '💎'
            }

    def _assess_risk(self, is_itm: bool, days_to_expiry: int, moneyness_pct: float) -> str:
        """Assess risk level of position"""

        if is_itm and abs(moneyness_pct) > 5:
            return 'HIGH'
        elif is_itm or days_to_expiry < 7:
            return 'MEDIUM'
        else:
            return 'LOW'

    def _calculate_annual_return(self, profit_pct: float, days_to_expiry: int) -> float:
        """Calculate annualized return if closed now"""

        if days_to_expiry <= 0:
            return 0

        days_held = 45 - days_to_expiry  # Assuming 45 DTE originally
        if days_held <= 0:
            days_held = 1

        return (profit_pct / days_held) * 365

    def get_portfolio_recommendations(self, positions: List[Dict]) -> Dict[str, Any]:
        """Get recommendations for entire portfolio"""

        total_value = 0
        recommendations = []
        buyback_candidates = []

        for pos in positions:
            if pos.get('Type') == 'CSP':
                analysis = self.analyze_csp(
                    pos['Symbol'],
                    pos.get('Strike', 0),
                    pos.get('Expiration', ''),
                    pos.get('Premium', 0),
                    pos.get('Current Value', 0),
                    pos.get('Days to Expiry', 0)
                )

                recommendations.append(analysis)

                # Track buyback candidates
                if analysis['profit_percentage'] >= 50:
                    buyback_candidates.append({
                        'symbol': analysis['symbol'],
                        'profit': analysis['profit_if_closed'],
                        'profit_pct': analysis['profit_percentage'],
                        'cost': analysis['cost_to_close']
                    })

                total_value += abs(pos.get('Current Value', 0))

        return {
            'recommendations': recommendations,
            'buyback_candidates': sorted(buyback_candidates, key=lambda x: x['profit_pct'], reverse=True),
            'total_positions': len(positions),
            'total_value': total_value,
            'suggested_action': self._get_portfolio_action(buyback_candidates)
        }

    def _get_portfolio_action(self, buyback_candidates: List[Dict]) -> str:
        """Get overall portfolio action"""

        if len(buyback_candidates) >= 3:
            return "🔥 Multiple profitable exits available! Close positions to maximize returns."
        elif len(buyback_candidates) >= 1:
            total_profit = sum(c['profit'] for c in buyback_candidates)
            return f"💰 Close {len(buyback_candidates)} position(s) to capture ${total_profit:.2f} profit"
        else:
            return "Hold all positions for continued theta decay"