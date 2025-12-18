"""
Greeks Calculator
=================

Calculate option Greeks without paying for them!
Uses Black-Scholes model for accurate Greeks calculations.

Greeks:
- Delta: Sensitivity to underlying price movement
- Gamma: Rate of change of delta
- Theta: Time decay
- Vega: Sensitivity to volatility
- Rho: Sensitivity to interest rates

Author: Magnus Trading Platform
Created: 2025-11-21
"""

import logging
import numpy as np
from scipy.stats import norm
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class GreeksCalculator:
    """Calculate option Greeks using Black-Scholes model"""

    def __init__(self, risk_free_rate: float = 0.05):
        """
        Initialize Greeks calculator.

        Args:
            risk_free_rate: Risk-free interest rate (default 5%)
        """
        self.risk_free_rate = risk_free_rate

    def calculate_greeks(
        self,
        S: float,  # Current stock price
        K: float,  # Strike price
        T: float,  # Time to expiration in years
        sigma: float,  # Implied volatility
        option_type: str = 'call'  # 'call' or 'put'
    ) -> Dict[str, float]:
        """
        Calculate all Greeks for an option.

        Args:
            S: Current stock price
            K: Strike price
            T: Time to expiration (years)
            sigma: Implied volatility (e.g., 0.25 for 25%)
            option_type: 'call' or 'put'

        Returns:
            Dict with delta, gamma, theta, vega, rho
        """
        if T <= 0:
            return {
                'delta': 1.0 if S > K else 0.0,
                'gamma': 0.0,
                'theta': 0.0,
                'vega': 0.0,
                'rho': 0.0,
                'option_price': max(0, S - K) if option_type == 'call' else max(0, K - S)
            }

        # Calculate d1 and d2
        d1 = (np.log(S / K) + (self.risk_free_rate + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
        d2 = d1 - sigma * np.sqrt(T)

        # Calculate Greeks
        if option_type.lower() == 'call':
            delta = norm.cdf(d1)
            theta = ((-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))) -
                    self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * norm.cdf(d2))
            rho = K * T * np.exp(-self.risk_free_rate * T) * norm.cdf(d2) / 100
            option_price = S * norm.cdf(d1) - K * np.exp(-self.risk_free_rate * T) * norm.cdf(d2)
        else:  # put
            delta = norm.cdf(d1) - 1
            theta = ((-S * norm.pdf(d1) * sigma / (2 * np.sqrt(T))) +
                    self.risk_free_rate * K * np.exp(-self.risk_free_rate * T) * norm.cdf(-d2))
            rho = -K * T * np.exp(-self.risk_free_rate * T) * norm.cdf(-d2) / 100
            option_price = K * np.exp(-self.risk_free_rate * T) * norm.cdf(-d2) - S * norm.cdf(-d1)

        # Gamma and Vega are the same for calls and puts
        gamma = norm.pdf(d1) / (S * sigma * np.sqrt(T))
        vega = S * norm.pdf(d1) * np.sqrt(T) / 100  # Divided by 100 for 1% move

        # Theta is typically expressed as daily decay
        theta_daily = theta / 365

        return {
            'delta': round(delta, 4),
            'gamma': round(gamma, 6),
            'theta': round(theta_daily, 2),  # Daily theta
            'theta_annual': round(theta, 2),
            'vega': round(vega, 2),
            'rho': round(rho, 2),
            'option_price': round(option_price, 2)
        }

    def calculate_portfolio_greeks(self, options_positions: list[Dict]) -> Dict:
        """
        Calculate aggregate Greeks for entire options portfolio.

        Args:
            options_positions: List of options positions with:
                - symbol, strike, expiration, quantity, option_type, iv

        Returns:
            Portfolio-level Greeks
        """
        net_delta = 0
        net_gamma = 0
        net_theta = 0
        net_vega = 0
        net_rho = 0

        for pos in options_positions:
            try:
                # Extract position details
                S = float(pos.get('current_price', 0))
                K = float(pos.get('strike', 0))
                exp_str = pos.get('expiration')
                quantity = int(pos.get('quantity', 0))
                option_type = pos.get('option_type', 'call')
                iv = float(pos.get('implied_volatility', 0.25))

                # Calculate days to expiration
                if exp_str:
                    exp_date = datetime.strptime(exp_str, '%Y-%m-%d')
                    days_to_exp = (exp_date - datetime.now()).days
                    T = max(days_to_exp / 365, 0.001)  # Convert to years
                else:
                    T = 0.1  # Default to ~36 days

                # Calculate Greeks
                greeks = self.calculate_greeks(S, K, T, iv, option_type)

                # Multiply by quantity and contract multiplier (100)
                contracts = quantity * 100

                net_delta += greeks['delta'] * contracts
                net_gamma += greeks['gamma'] * contracts
                net_theta += greeks['theta'] * contracts
                net_vega += greeks['vega'] * contracts
                net_rho += greeks['rho'] * contracts

            except Exception as e:
                logger.warning(f"Error calculating Greeks for position: {e}")
                continue

        return {
            'net_delta': round(net_delta, 2),
            'net_gamma': round(net_gamma, 4),
            'net_theta': round(net_theta, 2),
            'net_vega': round(net_vega, 2),
            'net_rho': round(net_rho, 2),
            'interpretation': self._interpret_portfolio_greeks(net_delta, net_theta, net_vega)
        }

    def _interpret_portfolio_greeks(self, delta: float, theta: float, vega: float) -> Dict[str, str]:
        """Interpret portfolio Greeks"""
        interp = {}

        # Delta interpretation
        if abs(delta) < 50:
            interp['delta'] = "Neutral directional bias"
        elif delta > 50:
            interp['delta'] = f"Bullish bias ({delta:.0f} delta)"
        else:
            interp['delta'] = f"Bearish bias ({delta:.0f} delta)"

        # Theta interpretation
        if theta > 0:
            interp['theta'] = f"Collecting ${theta:.2f}/day from time decay"
        elif theta < 0:
            interp['theta'] = f"Losing ${abs(theta):.2f}/day to time decay"
        else:
            interp['theta'] = "No time decay exposure"

        # Vega interpretation
        if abs(vega) < 100:
            interp['vega'] = "Low volatility exposure"
        elif vega > 100:
            interp['vega'] = f"Long volatility (gains ${vega:.2f} per 1% IV increase)"
        else:
            interp['vega'] = f"Short volatility (loses ${abs(vega):.2f} per 1% IV increase)"

        return interp


if __name__ == "__main__":
    # Test Greeks calculator
    print("\n=== Testing Greeks Calculator ===\n")

    calc = GreeksCalculator()

    # Test individual option
    print("1. CSP Example: NVDA $480 put, 45 DTE, IV=30%")
    greeks = calc.calculate_greeks(
        S=525,  # Current price
        K=480,  # Strike
        T=45/365,  # 45 days to expiration
        sigma=0.30,  # 30% IV
        option_type='put'
    )

    print(f"   Option Price: ${greeks['option_price']:.2f}")
    print(f"   Delta: {greeks['delta']:.4f} (probability ITM ≈ {abs(greeks['delta'])*100:.1f}%)")
    print(f"   Gamma: {greeks['gamma']:.6f}")
    print(f"   Theta: ${greeks['theta']:.2f}/day")
    print(f"   Vega: ${greeks['vega']:.2f} per 1% IV change")
    print(f"   Rho: ${greeks['rho']:.2f} per 1% rate change")

    print("\n✅ Greeks Calculator is ready!")
