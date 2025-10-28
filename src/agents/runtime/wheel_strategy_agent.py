"""Wheel Strategy Agent for finding optimal put and call opportunities"""

import asyncio
import pandas as pd
import numpy as np
from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime, timedelta, date
from loguru import logger
import yfinance as yf
from scipy.stats import norm
import redis
import json


class WheelStrategyAgent:
    """Agent for implementing wheel strategy logic and finding opportunities"""
    
    def __init__(self, redis_client: redis.Redis):
        self.redis_client = redis_client
        self.min_premium_yield = 0.01  # 1% minimum monthly
        self.target_delta = 0.30  # 30 delta for optimal premium/risk
        self.dte_range = (21, 45)  # Days to expiration range
        self.max_position_value = 5000  # Max $ per position
        
    async def find_put_opportunities(
        self, 
        symbols: List[str], 
        capital_available: float = 50000
    ) -> List[Dict[str, Any]]:
        """Find optimal cash-secured put opportunities"""
        opportunities = []
        
        for symbol in symbols:
            try:
                # Get current price
                ticker = yf.Ticker(symbol)
                current_price = ticker.history(period="1d")['Close'].iloc[-1]
                
                # Skip if stock price too high for position sizing
                if current_price * 100 > self.max_position_value:
                    continue
                
                # Get options chain
                options = await self._get_options_chain(symbol, 'puts')
                
                if options.empty:
                    continue
                
                # Find best put opportunity
                best_put = await self._find_optimal_put(
                    symbol, 
                    current_price, 
                    options
                )
                
                if best_put and best_put['expected_return'] >= self.min_premium_yield:
                    opportunities.append(best_put)
                    
            except Exception as e:
                logger.error(f"Error finding put opportunities for {symbol}: {e}")
                continue
        
        # Sort by expected return
        return sorted(opportunities, key=lambda x: x['expected_return'], reverse=True)
    
    async def find_call_opportunities(
        self, 
        holdings: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Find optimal covered call opportunities for holdings"""
        opportunities = []
        
        for holding in holdings:
            try:
                symbol = holding['symbol']
                cost_basis = holding['cost_basis']
                shares = holding['shares']
                
                if shares < 100:
                    continue  # Need at least 100 shares for covered call
                
                # Get current price
                ticker = yf.Ticker(symbol)
                current_price = ticker.history(period="1d")['Close'].iloc[-1]
                
                # Get options chain
                options = await self._get_options_chain(symbol, 'calls')
                
                if options.empty:
                    continue
                
                # Find best call opportunity
                best_call = await self._find_optimal_call(
                    symbol,
                    current_price,
                    cost_basis,
                    options
                )
                
                if best_call:
                    opportunities.append(best_call)
                    
            except Exception as e:
                logger.error(f"Error finding call opportunities for {holding}: {e}")
                continue
        
        return sorted(opportunities, key=lambda x: x['expected_return'], reverse=True)
    
    async def analyze_wheel_cycle(
        self, 
        symbol: str, 
        current_position: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Analyze complete wheel cycle for a symbol"""
        ticker = yf.Ticker(symbol)
        current_price = ticker.history(period="1d")['Close'].iloc[-1]
        
        analysis = {
            'symbol': symbol,
            'current_price': float(current_price),
            'timestamp': datetime.now().isoformat(),
            'recommendations': []
        }
        
        if not current_position:
            # No position - look for CSP opportunity
            puts = await self._get_options_chain(symbol, 'puts')
            if not puts.empty:
                best_put = await self._find_optimal_put(symbol, current_price, puts)
                if best_put:
                    analysis['recommendations'].append({
                        'action': 'SELL_CSP',
                        'details': best_put
                    })
        
        elif current_position['type'] == 'csp':
            # Have CSP - check if should close or let expire
            days_to_expiry = (current_position['expiration'] - datetime.now()).days
            
            if days_to_expiry <= 7:
                if current_price > current_position['strike'] * 1.05:
                    analysis['recommendations'].append({
                        'action': 'CLOSE_CSP',
                        'reason': 'Near expiration, likely to expire worthless'
                    })
            
        elif current_position['type'] == 'stock':
            # Own stock - look for CC opportunity
            calls = await self._get_options_chain(symbol, 'calls')
            if not calls.empty:
                best_call = await self._find_optimal_call(
                    symbol,
                    current_price, 
                    current_position['cost_basis'],
                    calls
                )
                if best_call:
                    analysis['recommendations'].append({
                        'action': 'SELL_CC',
                        'details': best_call
                    })
        
        elif current_position['type'] == 'cc':
            # Have CC - check if should roll or let expire
            days_to_expiry = (current_position['expiration'] - datetime.now()).days
            
            if current_price > current_position['strike'] and days_to_expiry <= 14:
                # Consider rolling up and out
                analysis['recommendations'].append({
                    'action': 'ROLL_CC',
                    'reason': 'ITM with near expiration'
                })
        
        return analysis
    
    async def _get_options_chain(
        self, 
        symbol: str, 
        option_type: str = 'puts'
    ) -> pd.DataFrame:
        """Get options chain data"""
        try:
            ticker = yf.Ticker(symbol)
            
            # Get expiration dates
            expirations = ticker.options
            
            if not expirations:
                return pd.DataFrame()
            
            # Filter expirations within our DTE range
            valid_expirations = []
            for exp in expirations:
                exp_date = datetime.strptime(exp, '%Y-%m-%d')
                dte = (exp_date - datetime.now()).days
                
                if self.dte_range[0] <= dte <= self.dte_range[1]:
                    valid_expirations.append(exp)
            
            if not valid_expirations:
                return pd.DataFrame()
            
            # Get options data for valid expirations
            all_options = []
            
            for exp in valid_expirations[:3]:  # Limit to 3 nearest expirations
                opt = ticker.option_chain(exp)
                
                if option_type == 'puts':
                    chain = opt.puts
                else:
                    chain = opt.calls
                
                chain['expiration'] = exp
                chain['dte'] = (datetime.strptime(exp, '%Y-%m-%d') - datetime.now()).days
                
                all_options.append(chain)
            
            if all_options:
                return pd.concat(all_options, ignore_index=True)
            
            return pd.DataFrame()
            
        except Exception as e:
            logger.error(f"Error getting options chain for {symbol}: {e}")
            return pd.DataFrame()
    
    async def _find_optimal_put(
        self, 
        symbol: str, 
        current_price: float,
        options: pd.DataFrame
    ) -> Optional[Dict[str, Any]]:
        """Find optimal put to sell"""
        if options.empty:
            return None
        
        # Filter for OTM puts with good liquidity
        otm_puts = options[
            (options['strike'] < current_price * 0.95) &  # At least 5% OTM
            (options['strike'] > current_price * 0.80) &  # Not more than 20% OTM
            (options['volume'] > 10) &  # Some volume
            (options['openInterest'] > 50)  # Some open interest
        ].copy()
        
        if otm_puts.empty:
            return None
        
        # Calculate metrics
        otm_puts['premium_yield'] = (otm_puts['bid'] / otm_puts['strike']) * (365 / otm_puts['dte'])
        otm_puts['annualized_return'] = otm_puts['premium_yield'] * 100
        
        # Calculate probability of profit (simplified)
        otm_puts['moneyness'] = otm_puts['strike'] / current_price
        otm_puts['prob_profit'] = 1 - otm_puts['moneyness']
        
        # Score opportunities
        otm_puts['score'] = (
            otm_puts['premium_yield'] * 100 +  # Weight premium
            otm_puts['prob_profit'] * 50 +  # Weight probability
            (otm_puts['volume'] / 100) * 10  # Weight liquidity
        )
        
        # Get best opportunity
        best = otm_puts.nlargest(1, 'score').iloc[0]
        
        return {
            'symbol': symbol,
            'strategy': 'CSP',
            'strike': float(best['strike']),
            'expiration': best['expiration'],
            'dte': int(best['dte']),
            'bid': float(best['bid']),
            'ask': float(best['ask']),
            'premium': float(best['bid']),
            'current_price': float(current_price),
            'premium_yield': float(best['premium_yield']),
            'expected_return': float(best['annualized_return']),
            'prob_profit': float(best['prob_profit']),
            'capital_required': float(best['strike'] * 100),
            'score': float(best['score']),
            'recommendation': 'SELL_PUT',
            'timestamp': datetime.now().isoformat()
        }
    
    async def _find_optimal_call(
        self,
        symbol: str,
        current_price: float,
        cost_basis: float,
        options: pd.DataFrame
    ) -> Optional[Dict[str, Any]]:
        """Find optimal call to sell against holdings"""
        if options.empty:
            return None
        
        # Filter for OTM calls above cost basis
        otm_calls = options[
            (options['strike'] > max(current_price * 1.02, cost_basis)) &  # Above current and cost
            (options['strike'] < current_price * 1.15) &  # Not too far OTM
            (options['volume'] > 10) &
            (options['openInterest'] > 50)
        ].copy()
        
        if otm_calls.empty:
            return None
        
        # Calculate metrics
        otm_calls['premium_yield'] = (otm_calls['bid'] / current_price) * (365 / otm_calls['dte'])
        otm_calls['if_called_return'] = (
            (otm_calls['strike'] - cost_basis + otm_calls['bid']) / cost_basis
        ) * (365 / otm_calls['dte'])
        
        # Probability of being called (simplified)
        otm_calls['moneyness'] = current_price / otm_calls['strike']
        otm_calls['prob_called'] = otm_calls['moneyness']
        
        # Score opportunities
        otm_calls['score'] = (
            otm_calls['premium_yield'] * 100 +
            otm_calls['if_called_return'] * 50 +
            (1 - otm_calls['prob_called']) * 30  # Prefer lower probability of assignment
        )
        
        # Get best opportunity
        best = otm_calls.nlargest(1, 'score').iloc[0]
        
        return {
            'symbol': symbol,
            'strategy': 'CC',
            'strike': float(best['strike']),
            'expiration': best['expiration'],
            'dte': int(best['dte']),
            'bid': float(best['bid']),
            'ask': float(best['ask']),
            'premium': float(best['bid']),
            'current_price': float(current_price),
            'cost_basis': float(cost_basis),
            'premium_yield': float(best['premium_yield']),
            'if_called_return': float(best['if_called_return']),
            'expected_return': float(best['premium_yield']) * 100,
            'prob_called': float(best['prob_called']),
            'score': float(best['score']),
            'recommendation': 'SELL_CALL',
            'timestamp': datetime.now().isoformat()
        }
    
    async def calculate_greeks(
        self,
        symbol: str,
        strike: float,
        expiration: str,
        option_type: str = 'put'
    ) -> Dict[str, float]:
        """Calculate option Greeks"""
        try:
            ticker = yf.Ticker(symbol)
            current_price = ticker.history(period="1d")['Close'].iloc[-1]
            
            # Get risk-free rate (simplified - using 5%)
            r = 0.05
            
            # Calculate time to expiration
            exp_date = datetime.strptime(expiration, '%Y-%m-%d')
            T = (exp_date - datetime.now()).days / 365
            
            # Get historical volatility
            hist = ticker.history(period="3mo")
            returns = hist['Close'].pct_change().dropna()
            sigma = returns.std() * np.sqrt(252)
            
            # Black-Scholes calculations
            d1 = (np.log(current_price / strike) + (r + 0.5 * sigma ** 2) * T) / (sigma * np.sqrt(T))
            d2 = d1 - sigma * np.sqrt(T)
            
            if option_type == 'call':
                delta = norm.cdf(d1)
                theta = -(current_price * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) - r * strike * np.exp(-r * T) * norm.cdf(d2)
            else:
                delta = -norm.cdf(-d1)
                theta = -(current_price * norm.pdf(d1) * sigma) / (2 * np.sqrt(T)) + r * strike * np.exp(-r * T) * norm.cdf(-d2)
            
            gamma = norm.pdf(d1) / (current_price * sigma * np.sqrt(T))
            vega = current_price * norm.pdf(d1) * np.sqrt(T) / 100
            
            return {
                'delta': float(delta),
                'gamma': float(gamma),
                'theta': float(theta / 365),  # Daily theta
                'vega': float(vega),
                'iv': float(sigma)
            }
            
        except Exception as e:
            logger.error(f"Error calculating Greeks: {e}")
            return {'delta': 0, 'gamma': 0, 'theta': 0, 'vega': 0, 'iv': 0}