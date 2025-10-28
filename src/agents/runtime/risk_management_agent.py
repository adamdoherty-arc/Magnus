"""Risk Management Agent for portfolio risk assessment and position sizing"""

import asyncio
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
import redis
import json
from decimal import Decimal


class RiskManagementAgent:
    """Agent responsible for risk assessment and position management"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.max_position_size_pct = 0.05  # 5% max per position
        self.max_sector_exposure = 0.30  # 30% max per sector
        self.max_total_risk = 0.20  # 20% max portfolio risk
        self.max_correlation = 0.70  # Max correlation between positions
        
    async def validate_trade(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any],
        market_data: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Validate a proposed trade against risk parameters"""
        validation = {
            'trade_id': trade.get('id'),
            'symbol': trade['symbol'],
            'valid': True,
            'warnings': [],
            'errors': [],
            'risk_metrics': {},
            'timestamp': datetime.now().isoformat()
        }
        
        # Check position sizing
        position_size_check = await self._check_position_sizing(
            trade, portfolio
        )
        if not position_size_check['passed']:
            validation['errors'].append(position_size_check['message'])
            validation['valid'] = False
        
        # Check sector allocation
        sector_check = await self._check_sector_allocation(
            trade, portfolio
        )
        if not sector_check['passed']:
            validation['warnings'].append(sector_check['message'])
        
        # Check correlation with existing positions
        correlation_check = await self._check_correlation(
            trade, portfolio
        )
        if correlation_check['correlation'] > self.max_correlation:
            validation['warnings'].append(
                f"High correlation ({correlation_check['correlation']:.2f}) with existing positions"
            )
        
        # Calculate portfolio impact
        impact = await self._calculate_portfolio_impact(
            trade, portfolio
        )
        validation['risk_metrics'] = impact
        
        # Check if total risk exceeds limits
        if impact['new_total_risk'] > self.max_total_risk:
            validation['errors'].append(
                f"Trade would exceed max portfolio risk ({impact['new_total_risk']:.2%} > {self.max_total_risk:.2%})"
            )
            validation['valid'] = False
        
        # Market conditions check
        if market_data:
            market_check = await self._check_market_conditions(
                trade, market_data
            )
            if market_check['risk_level'] == 'high':
                validation['warnings'].append(
                    f"High market risk: {market_check['reason']}"
                )
        
        return validation
    
    async def calculate_position_size(
        self,
        symbol: str,
        strategy: str,
        portfolio_value: float,
        stock_price: float,
        volatility: float = 0.25
    ) -> Dict[str, Any]:
        """Calculate optimal position size based on Kelly Criterion and risk limits"""
        
        # Base position size (% of portfolio)
        base_size = self.max_position_size_pct
        
        # Adjust for volatility
        if volatility > 0.40:
            size_multiplier = 0.5  # Half size for high volatility
        elif volatility > 0.30:
            size_multiplier = 0.75
        elif volatility < 0.15:
            size_multiplier = 0.5  # Half size for very low volatility (less premium)
        else:
            size_multiplier = 1.0
        
        adjusted_size = base_size * size_multiplier
        
        # Calculate position details
        position_value = portfolio_value * adjusted_size
        
        if strategy in ['CSP', 'wheel']:
            # For cash-secured puts, we need cash equal to 100 shares at strike
            contracts = int(position_value / (stock_price * 100))
            contracts = max(1, min(contracts, 5))  # Between 1-5 contracts
            
            capital_required = contracts * stock_price * 100
            
        elif strategy == 'CC':
            # For covered calls, based on shares owned
            shares = int(position_value / stock_price)
            contracts = shares // 100
            contracts = max(1, contracts)
            
            capital_required = contracts * 100 * stock_price
        
        else:
            contracts = 1
            capital_required = stock_price * 100
        
        return {
            'symbol': symbol,
            'strategy': strategy,
            'recommended_contracts': contracts,
            'position_value': position_value,
            'capital_required': capital_required,
            'position_size_pct': adjusted_size,
            'volatility_adjustment': size_multiplier,
            'max_loss': capital_required * 0.50,  # Assume 50% max loss
            'timestamp': datetime.now().isoformat()
        }
    
    async def analyze_portfolio_risk(
        self,
        portfolio: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Comprehensive portfolio risk analysis"""
        
        positions = portfolio.get('positions', [])
        total_value = portfolio.get('total_value', 0)
        
        if not positions or total_value == 0:
            return {
                'status': 'no_positions',
                'total_value': 0,
                'risk_metrics': {},
                'timestamp': datetime.now().isoformat()
            }
        
        # Calculate position concentration
        position_values = [p['market_value'] for p in positions]
        position_weights = [v / total_value for v in position_values]
        
        # Herfindahl Index for concentration
        hhi = sum([w ** 2 for w in position_weights])
        
        # Sector allocation
        sector_allocation = {}
        for pos in positions:
            sector = pos.get('sector', 'Unknown')
            sector_allocation[sector] = sector_allocation.get(sector, 0) + (
                pos['market_value'] / total_value
            )
        
        # Calculate portfolio Greeks (if options)
        total_delta = sum([p.get('delta', 0) * p.get('quantity', 0) for p in positions])
        total_theta = sum([p.get('theta', 0) * p.get('quantity', 0) for p in positions])
        total_gamma = sum([p.get('gamma', 0) * p.get('quantity', 0) for p in positions])
        
        # Value at Risk (simplified - using normal distribution)
        portfolio_volatility = await self._calculate_portfolio_volatility(positions)
        var_95 = total_value * portfolio_volatility * 1.65  # 95% VaR
        var_99 = total_value * portfolio_volatility * 2.33  # 99% VaR
        
        # Maximum drawdown potential
        max_drawdown = min(total_value, sum([
            p.get('max_loss', p['market_value'] * 0.5) for p in positions
        ]))
        
        # Risk scoring
        risk_score = self._calculate_risk_score({
            'concentration': hhi,
            'max_sector': max(sector_allocation.values()) if sector_allocation else 0,
            'total_delta': abs(total_delta),
            'portfolio_vol': portfolio_volatility
        })
        
        return {
            'total_value': total_value,
            'position_count': len(positions),
            'concentration_index': hhi,
            'sector_allocation': sector_allocation,
            'largest_position_pct': max(position_weights) if position_weights else 0,
            'greeks': {
                'delta': total_delta,
                'theta': total_theta,
                'gamma': total_gamma
            },
            'value_at_risk': {
                '95_pct_1_day': var_95,
                '99_pct_1_day': var_99
            },
            'max_drawdown': max_drawdown,
            'portfolio_volatility': portfolio_volatility,
            'risk_score': risk_score,
            'risk_level': self._get_risk_level(risk_score),
            'recommendations': await self._generate_risk_recommendations(
                risk_score, sector_allocation, hhi
            ),
            'timestamp': datetime.now().isoformat()
        }
    
    async def _check_position_sizing(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check if position size is within limits"""
        portfolio_value = portfolio.get('total_value', 0)
        
        if portfolio_value == 0:
            return {
                'passed': False,
                'message': 'Portfolio value is zero'
            }
        
        position_value = trade.get('capital_required', 0)
        position_pct = position_value / portfolio_value
        
        if position_pct > self.max_position_size_pct:
            return {
                'passed': False,
                'message': f'Position size ({position_pct:.2%}) exceeds limit ({self.max_position_size_pct:.2%})'
            }
        
        return {'passed': True, 'message': 'Position size OK'}
    
    async def _check_sector_allocation(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> Dict[str, bool]:
        """Check sector concentration"""
        positions = portfolio.get('positions', [])
        total_value = portfolio.get('total_value', 0)
        
        if total_value == 0:
            return {'passed': True, 'message': 'No existing positions'}
        
        trade_sector = trade.get('sector', 'Unknown')
        trade_value = trade.get('capital_required', 0)
        
        # Calculate current sector exposure
        sector_exposure = {}
        for pos in positions:
            sector = pos.get('sector', 'Unknown')
            sector_exposure[sector] = sector_exposure.get(sector, 0) + pos['market_value']
        
        # Add new trade
        current_sector_value = sector_exposure.get(trade_sector, 0)
        new_sector_value = current_sector_value + trade_value
        new_sector_pct = new_sector_value / (total_value + trade_value)
        
        if new_sector_pct > self.max_sector_exposure:
            return {
                'passed': False,
                'message': f'Sector exposure ({new_sector_pct:.2%}) would exceed limit ({self.max_sector_exposure:.2%})'
            }
        
        return {'passed': True, 'message': 'Sector allocation OK'}
    
    async def _check_correlation(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> Dict[str, float]:
        """Check correlation with existing positions"""
        # Simplified - in production would calculate actual correlations
        positions = portfolio.get('positions', [])
        
        if not positions:
            return {'correlation': 0.0}
        
        # Check if same symbol already in portfolio
        symbol = trade['symbol']
        for pos in positions:
            if pos.get('symbol') == symbol:
                return {'correlation': 1.0}  # Perfect correlation
        
        # Check sector correlation
        trade_sector = trade.get('sector')
        sector_count = sum(1 for p in positions if p.get('sector') == trade_sector)
        
        if sector_count > 2:
            return {'correlation': 0.8}  # High correlation
        elif sector_count > 0:
            return {'correlation': 0.5}  # Moderate correlation
        
        return {'correlation': 0.2}  # Low correlation
    
    async def _calculate_portfolio_impact(
        self,
        trade: Dict[str, Any],
        portfolio: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Calculate how trade impacts portfolio risk"""
        current_risk = portfolio.get('risk_metrics', {}).get('portfolio_risk', 0.10)
        trade_risk = trade.get('risk', 0.05)
        
        # Simple weighted average for new risk
        total_value = portfolio.get('total_value', 0)
        trade_value = trade.get('capital_required', 0)
        
        if total_value + trade_value == 0:
            new_risk = trade_risk
        else:
            new_risk = (
                (current_risk * total_value + trade_risk * trade_value) /
                (total_value + trade_value)
            )
        
        return {
            'current_total_risk': current_risk,
            'trade_risk': trade_risk,
            'new_total_risk': new_risk,
            'risk_increase': new_risk - current_risk
        }
    
    async def _check_market_conditions(
        self,
        trade: Dict[str, Any],
        market_data: Dict[str, Any]
    ) -> Dict[str, str]:
        """Check current market conditions for risk"""
        vix = market_data.get('vix', 20)
        
        if vix > 30:
            return {
                'risk_level': 'high',
                'reason': f'VIX at {vix} indicates high volatility'
            }
        elif vix < 12:
            return {
                'risk_level': 'low',
                'reason': f'VIX at {vix} may mean low premiums'
            }
        
        return {
            'risk_level': 'moderate',
            'reason': f'VIX at {vix} is in normal range'
        }
    
    async def _calculate_portfolio_volatility(
        self,
        positions: List[Dict[str, Any]]
    ) -> float:
        """Calculate portfolio volatility"""
        if not positions:
            return 0.0
        
        # Simplified - use average of position volatilities
        vols = [p.get('volatility', 0.25) for p in positions]
        return np.mean(vols) if vols else 0.25
    
    def _calculate_risk_score(self, metrics: Dict[str, float]) -> float:
        """Calculate overall risk score (0-100)"""
        score = 0.0
        
        # Concentration risk (0-30 points)
        hhi = metrics.get('concentration', 0)
        if hhi > 0.25:
            score += 30
        elif hhi > 0.15:
            score += 20
        elif hhi > 0.10:
            score += 10
        
        # Sector concentration (0-20 points)
        max_sector = metrics.get('max_sector', 0)
        if max_sector > 0.40:
            score += 20
        elif max_sector > 0.30:
            score += 15
        elif max_sector > 0.20:
            score += 10
        
        # Delta exposure (0-25 points)
        delta = abs(metrics.get('total_delta', 0))
        if delta > 100:
            score += 25
        elif delta > 50:
            score += 15
        elif delta > 25:
            score += 10
        
        # Volatility (0-25 points)
        vol = metrics.get('portfolio_vol', 0.25)
        if vol > 0.50:
            score += 25
        elif vol > 0.35:
            score += 15
        elif vol > 0.25:
            score += 10
        
        return min(100, score)
    
    def _get_risk_level(self, risk_score: float) -> str:
        """Convert risk score to risk level"""
        if risk_score >= 70:
            return 'HIGH'
        elif risk_score >= 40:
            return 'MODERATE'
        else:
            return 'LOW'
    
    async def _generate_risk_recommendations(
        self,
        risk_score: float,
        sector_allocation: Dict[str, float],
        hhi: float
    ) -> List[str]:
        """Generate risk management recommendations"""
        recommendations = []
        
        if risk_score >= 70:
            recommendations.append("Consider reducing position sizes")
            recommendations.append("Avoid new positions until risk decreases")
        
        if hhi > 0.20:
            recommendations.append("Portfolio is concentrated - consider diversification")
        
        for sector, weight in sector_allocation.items():
            if weight > 0.30:
                recommendations.append(
                    f"High exposure to {sector} ({weight:.1%}) - consider rebalancing"
                )
        
        if not recommendations:
            recommendations.append("Portfolio risk is well-managed")
        
        return recommendations