"""
Alpha Vantage API Client (FREE Tier)
=====================================

Comprehensive client for Alpha Vantage's FREE financial data API.

Features (All FREE):
- Real-time stock quotes
- Historical price data
- News & sentiment analysis (AI-powered)
- Technical indicators (50+)
- Economic indicators
- Company fundamentals

Free Tier Limits:
- 25 API calls per day (generous for most use cases)
- No cost whatsoever
- Great for educational and small-scale use

API Key: Get free at https://www.alphavantage.co/support/#api-key

Author: Magnus Trading Platform
Created: 2025-11-21
"""

import os
import requests
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import lru_cache
import json
import time

logger = logging.getLogger(__name__)


class AlphaVantageClient:
    """Client for Alpha Vantage FREE API"""

    BASE_URL = "https://www.alphavantage.co/query"

    # Default free API key (demo - replace with user's key)
    DEFAULT_API_KEY = "demo"

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize Alpha Vantage client.

        Args:
            api_key: Alpha Vantage API key (get free at alphavantage.co)
                    Falls back to env var ALPHA_VANTAGE_API_KEY
        """
        self.api_key = api_key or os.getenv('ALPHA_VANTAGE_API_KEY', self.DEFAULT_API_KEY)
        self.session = requests.Session()
        self.call_count = 0
        self.last_call_time = None

        logger.info(f"✅ Alpha Vantage client initialized (API key: {self.api_key[:8]}...)")

    def _make_request(self, params: Dict[str, str]) -> Dict[str, Any]:
        """
        Make API request with rate limiting and error handling.

        Args:
            params: API parameters

        Returns:
            JSON response as dictionary
        """
        # Add API key to params
        params['apikey'] = self.api_key

        # Rate limiting (be nice to free tier - 1 call per 12 seconds = ~25 calls/day)
        if self.last_call_time:
            elapsed = time.time() - self.last_call_time
            if elapsed < 12:  # Wait at least 12 seconds between calls
                wait_time = 12 - elapsed
                logger.info(f"⏳ Rate limiting: waiting {wait_time:.1f}s...")
                time.sleep(wait_time)

        try:
            response = self.session.get(self.BASE_URL, params=params, timeout=30)
            response.raise_for_status()

            self.last_call_time = time.time()
            self.call_count += 1

            data = response.json()

            # Check for API errors
            if "Error Message" in data:
                logger.error(f"Alpha Vantage API error: {data['Error Message']}")
                return {}

            if "Note" in data:  # Rate limit message
                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                return {}

            logger.info(f"✅ Alpha Vantage API call #{self.call_count} successful")
            return data

        except requests.exceptions.RequestException as e:
            logger.error(f"Alpha Vantage request failed: {e}")
            return {}

    # ========================================================================
    # STOCK QUOTES & PRICES (FREE)
    # ========================================================================

    @lru_cache(maxsize=100)
    def get_quote(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get real-time quote for a symbol (FREE).

        Args:
            symbol: Stock ticker (e.g., 'AAPL')

        Returns:
            Quote data with price, volume, change, etc.
        """
        params = {
            'function': 'GLOBAL_QUOTE',
            'symbol': symbol
        }

        data = self._make_request(params)

        if not data or 'Global Quote' not in data:
            return None

        quote = data['Global Quote']

        return {
            'symbol': quote.get('01. symbol', symbol),
            'price': float(quote.get('05. price', 0)),
            'change': float(quote.get('09. change', 0)),
            'change_percent': quote.get('10. change percent', '0%').rstrip('%'),
            'volume': int(quote.get('06. volume', 0)),
            'latest_trading_day': quote.get('07. latest trading day', ''),
            'previous_close': float(quote.get('08. previous close', 0)),
            'open': float(quote.get('02. open', 0)),
            'high': float(quote.get('03. high', 0)),
            'low': float(quote.get('04. low', 0)),
            'timestamp': datetime.now().isoformat()
        }

    def get_intraday(self, symbol: str, interval: str = '5min') -> Optional[List[Dict]]:
        """
        Get intraday price data (FREE).

        Args:
            symbol: Stock ticker
            interval: '1min', '5min', '15min', '30min', '60min'

        Returns:
            List of OHLCV candles
        """
        params = {
            'function': 'TIME_SERIES_INTRADAY',
            'symbol': symbol,
            'interval': interval,
            'outputsize': 'compact'  # Last 100 data points
        }

        data = self._make_request(params)

        if not data:
            return None

        # Parse time series
        time_series_key = f'Time Series ({interval})'
        if time_series_key not in data:
            return None

        candles = []
        for timestamp, values in data[time_series_key].items():
            candles.append({
                'timestamp': timestamp,
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'volume': int(values['5. volume'])
            })

        return candles

    def get_daily(self, symbol: str, outputsize: str = 'compact') -> Optional[List[Dict]]:
        """
        Get daily price history (FREE).

        Args:
            symbol: Stock ticker
            outputsize: 'compact' (100 days) or 'full' (20+ years)

        Returns:
            List of daily OHLCV candles
        """
        params = {
            'function': 'TIME_SERIES_DAILY',
            'symbol': symbol,
            'outputsize': outputsize
        }

        data = self._make_request(params)

        if not data or 'Time Series (Daily)' not in data:
            return None

        candles = []
        for date, values in data['Time Series (Daily)'].items():
            candles.append({
                'date': date,
                'open': float(values['1. open']),
                'high': float(values['2. high']),
                'low': float(values['3. low']),
                'close': float(values['4. close']),
                'volume': int(values['5. volume'])
            })

        return candles

    # ========================================================================
    # NEWS & SENTIMENT (FREE - AI-POWERED!)
    # ========================================================================

    def get_news_sentiment(
        self,
        tickers: Optional[List[str]] = None,
        topics: Optional[List[str]] = None,
        time_from: Optional[str] = None,
        time_to: Optional[str] = None,
        limit: int = 50
    ) -> Optional[Dict[str, Any]]:
        """
        Get AI-powered news sentiment analysis (FREE).

        This is GOLD - AI sentiment scores for any ticker or topic!

        Args:
            tickers: List of stock tickers (e.g., ['AAPL', 'TSLA'])
            topics: Topics like 'technology', 'earnings', 'ipo', etc.
            time_from: Start date (YYYYMMDDTHHMM format)
            time_to: End date (YYYYMMDDTHHMM format)
            limit: Max number of articles (default 50, max 1000)

        Returns:
            News articles with AI sentiment scores:
            - overall_sentiment_score (-1 to 1)
            - overall_sentiment_label (Bearish/Neutral/Bullish)
            - ticker_sentiment per symbol
        """
        params = {
            'function': 'NEWS_SENTIMENT',
            'limit': str(limit)
        }

        if tickers:
            params['tickers'] = ','.join(tickers)

        if topics:
            params['topics'] = ','.join(topics)

        if time_from:
            params['time_from'] = time_from

        if time_to:
            params['time_to'] = time_to

        data = self._make_request(params)

        if not data or 'feed' not in data:
            return None

        # Process articles
        articles = []
        for article in data['feed']:
            articles.append({
                'title': article.get('title', ''),
                'url': article.get('url', ''),
                'time_published': article.get('time_published', ''),
                'authors': article.get('authors', []),
                'summary': article.get('summary', ''),
                'source': article.get('source', ''),
                'overall_sentiment_score': float(article.get('overall_sentiment_score', 0)),
                'overall_sentiment_label': article.get('overall_sentiment_label', 'Neutral'),
                'ticker_sentiment': [
                    {
                        'ticker': ts['ticker'],
                        'relevance_score': float(ts['relevance_score']),
                        'sentiment_score': float(ts['ticker_sentiment_score']),
                        'sentiment_label': ts['ticker_sentiment_label']
                    }
                    for ts in article.get('ticker_sentiment', [])
                ]
            })

        # Calculate aggregate sentiment
        if articles:
            avg_sentiment = sum(a['overall_sentiment_score'] for a in articles) / len(articles)
            sentiment_label = 'Bullish' if avg_sentiment > 0.15 else 'Bearish' if avg_sentiment < -0.15 else 'Neutral'
        else:
            avg_sentiment = 0
            sentiment_label = 'Neutral'

        return {
            'articles': articles,
            'items_returned': len(articles),
            'aggregate_sentiment_score': avg_sentiment,
            'aggregate_sentiment_label': sentiment_label,
            'timestamp': datetime.now().isoformat()
        }

    # ========================================================================
    # TECHNICAL INDICATORS (FREE - 50+ indicators!)
    # ========================================================================

    def get_sma(self, symbol: str, interval: str = 'daily', time_period: int = 20) -> Optional[List[Dict]]:
        """Get Simple Moving Average (FREE)"""
        params = {
            'function': 'SMA',
            'symbol': symbol,
            'interval': interval,
            'time_period': str(time_period),
            'series_type': 'close'
        }

        data = self._make_request(params)

        if not data or 'Technical Analysis: SMA' not in data:
            return None

        sma_data = []
        for date, values in data['Technical Analysis: SMA'].items():
            sma_data.append({
                'date': date,
                'sma': float(values['SMA'])
            })

        return sma_data

    def get_rsi(self, symbol: str, interval: str = 'daily', time_period: int = 14) -> Optional[List[Dict]]:
        """Get Relative Strength Index (FREE)"""
        params = {
            'function': 'RSI',
            'symbol': symbol,
            'interval': interval,
            'time_period': str(time_period),
            'series_type': 'close'
        }

        data = self._make_request(params)

        if not data or 'Technical Analysis: RSI' not in data:
            return None

        rsi_data = []
        for date, values in data['Technical Analysis: RSI'].items():
            rsi_data.append({
                'date': date,
                'rsi': float(values['RSI'])
            })

        return rsi_data

    def get_macd(self, symbol: str, interval: str = 'daily') -> Optional[List[Dict]]:
        """Get MACD (Moving Average Convergence Divergence) (FREE)"""
        params = {
            'function': 'MACD',
            'symbol': symbol,
            'interval': interval,
            'series_type': 'close'
        }

        data = self._make_request(params)

        if not data or 'Technical Analysis: MACD' not in data:
            return None

        macd_data = []
        for date, values in data['Technical Analysis: MACD'].items():
            macd_data.append({
                'date': date,
                'macd': float(values['MACD']),
                'macd_signal': float(values['MACD_Signal']),
                'macd_hist': float(values['MACD_Hist'])
            })

        return macd_data

    # ========================================================================
    # COMPANY FUNDAMENTALS (FREE)
    # ========================================================================

    def get_company_overview(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Get company fundamental data (FREE).

        Returns P/E, market cap, revenue, EPS, dividend yield, etc.
        """
        params = {
            'function': 'OVERVIEW',
            'symbol': symbol
        }

        data = self._make_request(params)

        if not data or 'Symbol' not in data:
            return None

        return {
            'symbol': data.get('Symbol', symbol),
            'name': data.get('Name', ''),
            'description': data.get('Description', ''),
            'sector': data.get('Sector', ''),
            'industry': data.get('Industry', ''),
            'market_cap': data.get('MarketCapitalization', ''),
            'pe_ratio': data.get('PERatio', ''),
            'peg_ratio': data.get('PEGRatio', ''),
            'book_value': data.get('BookValue', ''),
            'dividend_yield': data.get('DividendYield', ''),
            'eps': data.get('EPS', ''),
            'revenue_per_share': data.get('RevenuePerShareTTM', ''),
            'profit_margin': data.get('ProfitMargin', ''),
            'operating_margin': data.get('OperatingMarginTTM', ''),
            '52_week_high': data.get('52WeekHigh', ''),
            '52_week_low': data.get('52WeekLow', ''),
            '50_day_ma': data.get('50DayMovingAverage', ''),
            '200_day_ma': data.get('200DayMovingAverage', ''),
            'beta': data.get('Beta', ''),
            'analyst_target_price': data.get('AnalystTargetPrice', ''),
            'timestamp': datetime.now().isoformat()
        }

    # ========================================================================
    # MARKET MOVERS & TOP PERFORMERS (FREE)
    # ========================================================================

    def get_top_gainers_losers(self) -> Optional[Dict[str, List]]:
        """
        Get today's top gainers, losers, and most actively traded (FREE).

        Perfect for finding hot stocks and opportunities!
        """
        params = {
            'function': 'TOP_GAINERS_LOSERS'
        }

        data = self._make_request(params)

        if not data:
            return None

        return {
            'top_gainers': data.get('top_gainers', []),
            'top_losers': data.get('top_losers', []),
            'most_actively_traded': data.get('most_actively_traded', []),
            'last_updated': data.get('last_updated', ''),
            'timestamp': datetime.now().isoformat()
        }

    # ========================================================================
    # HELPER METHODS
    # ========================================================================

    def get_sentiment_for_ticker(self, ticker: str, days_back: int = 7) -> Optional[Dict]:
        """
        Get aggregated sentiment for a single ticker over recent days.

        Args:
            ticker: Stock ticker
            days_back: How many days to look back (default 7)

        Returns:
            Aggregated sentiment analysis
        """
        time_from = (datetime.now() - timedelta(days=days_back)).strftime('%Y%m%dT0000')

        sentiment_data = self.get_news_sentiment(
            tickers=[ticker],
            time_from=time_from,
            limit=50
        )

        if not sentiment_data:
            return None

        # Extract ticker-specific sentiment from articles
        ticker_sentiments = []
        for article in sentiment_data['articles']:
            for ts in article['ticker_sentiment']:
                if ts['ticker'].upper() == ticker.upper():
                    ticker_sentiments.append({
                        'score': ts['sentiment_score'],
                        'label': ts['sentiment_label'],
                        'relevance': ts['relevance_score'],
                        'title': article['title'],
                        'date': article['time_published']
                    })

        if not ticker_sentiments:
            return {
                'ticker': ticker,
                'sentiment_score': 0,
                'sentiment_label': 'Neutral',
                'article_count': 0,
                'confidence': 'low'
            }

        # Calculate weighted average (by relevance)
        total_weighted_score = sum(s['score'] * s['relevance'] for s in ticker_sentiments)
        total_relevance = sum(s['relevance'] for s in ticker_sentiments)

        avg_score = total_weighted_score / total_relevance if total_relevance > 0 else 0

        # Determine label
        if avg_score > 0.15:
            label = 'Bullish'
        elif avg_score < -0.15:
            label = 'Bearish'
        else:
            label = 'Neutral'

        # Confidence based on number of articles
        if len(ticker_sentiments) >= 10:
            confidence = 'high'
        elif len(ticker_sentiments) >= 5:
            confidence = 'medium'
        else:
            confidence = 'low'

        return {
            'ticker': ticker,
            'sentiment_score': round(avg_score, 4),
            'sentiment_label': label,
            'article_count': len(ticker_sentiments),
            'confidence': confidence,
            'recent_headlines': [s['title'] for s in ticker_sentiments[:5]],
            'days_analyzed': days_back,
            'timestamp': datetime.now().isoformat()
        }

    def get_usage_stats(self) -> Dict:
        """Get API usage statistics"""
        return {
            'total_calls': self.call_count,
            'calls_remaining_today': max(0, 25 - self.call_count),
            'last_call': self.last_call_time,
            'api_key': f"{self.api_key[:8]}...",
            'free_tier': True
        }


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def get_client() -> AlphaVantageClient:
    """Get singleton Alpha Vantage client instance"""
    global _alpha_vantage_client
    if '_alpha_vantage_client' not in globals():
        _alpha_vantage_client = AlphaVantageClient()
    return _alpha_vantage_client


# Quick access functions
def get_quote(symbol: str) -> Optional[Dict]:
    """Quick function to get a quote"""
    return get_client().get_quote(symbol)


def get_news_sentiment(ticker: str, days_back: int = 7) -> Optional[Dict]:
    """Quick function to get sentiment"""
    return get_client().get_sentiment_for_ticker(ticker, days_back)


def get_company_overview(symbol: str) -> Optional[Dict]:
    """Quick function to get company fundamentals"""
    return get_client().get_company_overview(symbol)


def get_top_movers() -> Optional[Dict]:
    """Quick function to get top gainers/losers"""
    return get_client().get_top_gainers_losers()


if __name__ == "__main__":
    # Test the client
    logging.basicConfig(level=logging.INFO)

    client = AlphaVantageClient()

    print("\n=== Testing Alpha Vantage FREE API ===\n")

    # Test 1: Get quote
    print("1. Getting AAPL quote...")
    quote = client.get_quote('AAPL')
    if quote:
        print(f"   ✅ AAPL: ${quote['price']} ({quote['change_percent']}%)")

    # Test 2: Get sentiment
    print("\n2. Getting AAPL news sentiment...")
    sentiment = client.get_sentiment_for_ticker('AAPL', days_back=3)
    if sentiment:
        print(f"   ✅ Sentiment: {sentiment['sentiment_label']} (score: {sentiment['sentiment_score']})")
        print(f"   Articles analyzed: {sentiment['article_count']}")

    # Test 3: Get company overview
    print("\n3. Getting AAPL company overview...")
    overview = client.get_company_overview('AAPL')
    if overview:
        print(f"   ✅ {overview['name']}")
        print(f"   Market Cap: {overview['market_cap']}")
        print(f"   P/E Ratio: {overview['pe_ratio']}")

    # Test 4: Get top movers
    print("\n4. Getting top market movers...")
    movers = client.get_top_gainers_losers()
    if movers and 'top_gainers' in movers:
        print(f"   ✅ Top gainer: {movers['top_gainers'][0]['ticker']} (+{movers['top_gainers'][0]['change_percentage']})")

    print(f"\n=== Usage Stats ===")
    stats = client.get_usage_stats()
    print(f"API calls made: {stats['total_calls']}/25")
    print(f"Calls remaining: {stats['calls_remaining_today']}")
