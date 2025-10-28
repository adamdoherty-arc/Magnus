"""Market Data Agent for continuous stock monitoring and filtering"""

import asyncio
import yfinance as yf
import pandas as pd
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from tradingview_ta import TA_Handler, Interval
import redis
import json
from decimal import Decimal


class MarketDataAgent:
    """Agent responsible for market data collection and filtering"""
    
    def __init__(self, redis_client: redis.Redis, max_price: float = 50.0):
        self.redis_client = redis_client
        self.max_price = max_price
        self.watchlist = []
        self.price_threshold = max_price
        self.min_volume = 1000000  # Minimum daily volume
        self.min_options_volume = 100  # Minimum options volume
        
    async def scan_opportunities(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """Scan for stocks meeting criteria for wheel strategy"""
        opportunities = []
        
        if not symbols:
            # Get popular stocks under $50 from various sources
            symbols = await self._get_candidate_symbols()
        
        logger.info(f"Scanning {len(symbols)} symbols for opportunities")
        
        for symbol in symbols:
            try:
                stock_data = await self._analyze_stock(symbol)
                
                if stock_data and self._meets_criteria(stock_data):
                    opportunities.append(stock_data)
                    
                    # Cache the opportunity
                    await self._cache_opportunity(symbol, stock_data)
                    
            except Exception as e:
                logger.error(f"Error analyzing {symbol}: {e}")
                continue
                
        return sorted(opportunities, key=lambda x: x.get('score', 0), reverse=True)
    
    async def monitor_prices(self, symbols: List[str], callback=None) -> None:
        """Real-time price monitoring with alert triggers"""
        logger.info(f"Starting price monitoring for {len(symbols)} symbols")
        
        while True:
            for symbol in symbols:
                try:
                    current_price = await self._get_current_price(symbol)
                    
                    # Check for significant moves
                    cached_data = await self._get_cached_data(symbol)
                    if cached_data:
                        prev_price = cached_data.get('last_price', current_price)
                        change_pct = abs((current_price - prev_price) / prev_price)
                        
                        if change_pct > 0.03:  # 3% move
                            alert = {
                                'symbol': symbol,
                                'type': 'price_move',
                                'previous': prev_price,
                                'current': current_price,
                                'change_pct': change_pct,
                                'timestamp': datetime.now().isoformat()
                            }
                            
                            if callback:
                                await callback(alert)
                            
                            # Publish to Redis for other services
                            await self._publish_alert(alert)
                    
                    # Update cache
                    await self._update_price_cache(symbol, current_price)
                    
                except Exception as e:
                    logger.error(f"Error monitoring {symbol}: {e}")
                    
            await asyncio.sleep(60)  # Check every minute
    
    async def get_tradingview_signals(self, symbol: str) -> Dict[str, Any]:
        """Get technical analysis signals from TradingView"""
        try:
            handler = TA_Handler(
                symbol=symbol,
                exchange="NASDAQ" if symbol in self._nasdaq_symbols else "NYSE",
                screener="america",
                interval=Interval.INTERVAL_1_DAY
            )
            
            analysis = handler.get_analysis()
            
            return {
                'recommendation': analysis.summary['RECOMMENDATION'],
                'buy_signals': analysis.summary['BUY'],
                'sell_signals': analysis.summary['SELL'],
                'neutral_signals': analysis.summary['NEUTRAL'],
                'rsi': analysis.indicators.get('RSI', None),
                'macd': analysis.indicators.get('MACD.macd', None)
            }
            
        except Exception as e:
            logger.error(f"Error getting TradingView signals for {symbol}: {e}")
            return {}
    
    async def _analyze_stock(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Comprehensive stock analysis"""
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            hist = ticker.history(period="1mo")
            
            if hist.empty:
                return None
            
            current_price = hist['Close'].iloc[-1]
            avg_volume = hist['Volume'].mean()
            
            # Skip if price too high or volume too low
            if current_price > self.max_price or avg_volume < self.min_volume:
                return None
            
            # Calculate volatility
            returns = hist['Close'].pct_change().dropna()
            volatility = returns.std() * (252 ** 0.5)  # Annualized
            
            # Get TradingView signals
            tv_signals = await self.get_tradingview_signals(symbol)
            
            # Calculate opportunity score
            score = self._calculate_opportunity_score({
                'price': current_price,
                'volume': avg_volume,
                'volatility': volatility,
                'tv_signals': tv_signals
            })
            
            return {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'sector': info.get('sector', 'Unknown'),
                'current_price': float(current_price),
                'avg_volume': int(avg_volume),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', None),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 1.0),
                'volatility': float(volatility),
                'tv_signals': tv_signals,
                'score': score,
                'timestamp': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _meets_criteria(self, stock_data: Dict[str, Any]) -> bool:
        """Check if stock meets wheel strategy criteria"""
        # Price under threshold
        if stock_data['current_price'] > self.max_price:
            return False
        
        # Adequate volume
        if stock_data['avg_volume'] < self.min_volume:
            return False
        
        # Reasonable volatility (not too low, not too high)
        volatility = stock_data.get('volatility', 0)
        if volatility < 0.15 or volatility > 0.60:
            return False
        
        # Not in blacklist sectors
        blacklist_sectors = ['Biotechnology', 'Pharmaceuticals']
        if stock_data.get('sector') in blacklist_sectors:
            return False
        
        return True
    
    def _calculate_opportunity_score(self, metrics: Dict[str, Any]) -> float:
        """Calculate opportunity score for ranking"""
        score = 0.0
        
        # Price component (prefer lower prices for capital efficiency)
        price_score = max(0, (50 - metrics['price']) / 50) * 20
        score += price_score
        
        # Volume component (higher is better)
        volume_score = min(20, metrics['volume'] / 1000000)
        score += volume_score
        
        # Volatility component (sweet spot around 25-35%)
        vol = metrics['volatility']
        if 0.25 <= vol <= 0.35:
            vol_score = 30
        elif 0.20 <= vol <= 0.40:
            vol_score = 20
        else:
            vol_score = 10
        score += vol_score
        
        # TradingView signals
        tv = metrics.get('tv_signals', {})
        if tv.get('recommendation') in ['BUY', 'STRONG_BUY']:
            score += 20
        elif tv.get('recommendation') == 'NEUTRAL':
            score += 10
        
        return min(100, score)
    
    async def _get_candidate_symbols(self) -> List[str]:
        """Get list of candidate symbols to scan"""
        # No default candidates - only use configured watchlist
        candidates = []

        # Add from watchlist if configured
        if self.watchlist:
            candidates.extend(self.watchlist)
        
        return list(set(candidates))  # Remove duplicates
    
    async def _get_current_price(self, symbol: str) -> float:
        """Get current stock price"""
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        return float(hist['Close'].iloc[-1]) if not hist.empty else 0.0
    
    async def _cache_opportunity(self, symbol: str, data: Dict[str, Any]) -> None:
        """Cache opportunity data in Redis"""
        key = f"opportunity:{symbol}"
        self.redis_client.setex(
            key,
            3600,  # 1 hour expiry
            json.dumps(data, default=str)
        )
    
    async def _get_cached_data(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get cached data for symbol"""
        key = f"price:{symbol}"
        data = self.redis_client.get(key)
        return json.loads(data) if data else None
    
    async def _update_price_cache(self, symbol: str, price: float) -> None:
        """Update price cache"""
        key = f"price:{symbol}"
        data = {
            'symbol': symbol,
            'last_price': price,
            'timestamp': datetime.now().isoformat()
        }
        self.redis_client.setex(key, 300, json.dumps(data))  # 5 min expiry
    
    async def _publish_alert(self, alert: Dict[str, Any]) -> None:
        """Publish alert to Redis pub/sub"""
        channel = f"alerts:{alert['type']}"
        self.redis_client.publish(channel, json.dumps(alert, default=str))
    
    @property
    def _nasdaq_symbols(self) -> set:
        """Common NASDAQ symbols"""
        return {'AAPL', 'MSFT', 'AMZN', 'GOOGL', 'META', 'TSLA', 'NVDA', 
                'INTC', 'CSCO', 'CMCSA', 'ADBE', 'NFLX', 'PYPL', 'QCOM'}