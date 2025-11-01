"""
Sentiment Analyst Agent
Uses Reddit (praw), news sources, and yfinance for sentiment analysis
"""

import os
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
from collections import Counter
import re
from loguru import logger

try:
    import praw
    from praw.models import Submission
    PRAW_AVAILABLE = True
except ImportError:
    logger.warning("praw not installed, Reddit sentiment will be unavailable")
    PRAW_AVAILABLE = False

import yfinance as yf

from .models import (
    SentimentAnalysis,
    SentimentType,
    InstitutionalFlow,
    AnalystRating,
    InsiderTrade,
    AnalystConsensus
)


class SentimentAgent:
    """
    Specialist agent for sentiment analysis.

    Features:
    - Reddit sentiment from r/wallstreetbets, r/stocks, r/investing
    - Analyst ratings and consensus from yfinance
    - Insider trading activity detection
    - News sentiment scoring
    - Institutional flow indicators
    """

    def __init__(
        self,
        reddit_client_id: Optional[str] = None,
        reddit_client_secret: Optional[str] = None,
        reddit_user_agent: Optional[str] = None
    ):
        """
        Initialize the Sentiment Agent.

        Args:
            reddit_client_id: Reddit API client ID
            reddit_client_secret: Reddit API client secret
            reddit_user_agent: Reddit API user agent
        """
        self.reddit = None

        if PRAW_AVAILABLE:
            try:
                self.reddit = praw.Reddit(
                    client_id=reddit_client_id or os.getenv("REDDIT_CLIENT_ID"),
                    client_secret=reddit_client_secret or os.getenv("REDDIT_CLIENT_SECRET"),
                    user_agent=reddit_user_agent or os.getenv("REDDIT_USER_AGENT", "stock_analyzer/1.0")
                )
                logger.info("Reddit API initialized successfully")
            except Exception as e:
                logger.warning(f"Failed to initialize Reddit API: {e}")
                self.reddit = None

        # Sentiment keywords for basic text analysis
        self.positive_keywords = {
            "bullish", "buy", "calls", "moon", "rocket", "gain", "gains", "up",
            "green", "profit", "strong", "great", "good", "positive", "uptrend"
        }

        self.negative_keywords = {
            "bearish", "sell", "puts", "crash", "dump", "loss", "losses", "down",
            "red", "weak", "bad", "negative", "downtrend", "short", "tank"
        }

        logger.info("SentimentAgent initialized")

    async def analyze(self, symbol: str) -> SentimentAnalysis:
        """
        Perform comprehensive sentiment analysis on a stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            SentimentAnalysis object

        Raises:
            ValueError: If symbol is invalid
        """
        symbol = symbol.upper().strip()
        logger.info(f"Starting sentiment analysis for {symbol}")

        try:
            # Fetch all data in parallel
            reddit_data, analyst_data, insider_data = await asyncio.gather(
                self._get_reddit_sentiment(symbol),
                self._get_analyst_ratings(symbol),
                self._get_insider_trades(symbol),
                return_exceptions=True
            )

            # Handle errors with fallbacks
            if isinstance(reddit_data, Exception):
                logger.warning(f"Reddit sentiment failed: {reddit_data}")
                reddit_data = {"sentiment": SentimentType.NEUTRAL, "mentions": 0}

            if isinstance(analyst_data, Exception):
                logger.warning(f"Analyst ratings failed: {analyst_data}")
                analyst_data = {
                    "rating": AnalystRating.HOLD,
                    "consensus": AnalystConsensus(0, 0, 1, 0, 0)
                }

            if isinstance(insider_data, Exception):
                logger.warning(f"Insider trades failed: {insider_data}")
                insider_data = []

            # Analyze institutional flow (would need more data sources in production)
            institutional_flow = self._analyze_institutional_flow(analyst_data, insider_data)

            # Calculate overall sentiment score
            score = self._calculate_sentiment_score(
                reddit_data,
                analyst_data,
                institutional_flow,
                insider_data
            )

            analysis = SentimentAnalysis(
                score=score,
                news_sentiment=SentimentType.NEUTRAL,  # Would need news API
                news_count_7d=0,  # Would need news API
                social_sentiment=reddit_data["sentiment"],
                reddit_mentions_24h=reddit_data["mentions"],
                stocktwits_sentiment=0.0,  # Would need StockTwits API
                institutional_flow=institutional_flow,
                insider_trades=insider_data,
                analyst_rating=analyst_data["rating"],
                analyst_consensus=analyst_data["consensus"]
            )

            logger.info(f"Sentiment analysis completed for {symbol} with score {score}")
            return analysis

        except Exception as e:
            logger.error(f"Sentiment analysis failed for {symbol}: {e}")
            return self._create_fallback_analysis(symbol)

    async def _get_reddit_sentiment(self, symbol: str) -> dict:
        """
        Fetch and analyze Reddit sentiment.

        Args:
            symbol: Stock ticker

        Returns:
            Dictionary with sentiment and mention count
        """
        if not self.reddit:
            logger.debug("Reddit API not available")
            return {"sentiment": SentimentType.NEUTRAL, "mentions": 0}

        try:
            # Search relevant subreddits
            subreddits = ["wallstreetbets", "stocks", "investing", "stockmarket"]
            mentions = []

            loop = asyncio.get_event_loop()

            for sub_name in subreddits:
                try:
                    # Run Reddit API call in executor
                    subreddit = await loop.run_in_executor(
                        None,
                        lambda: self.reddit.subreddit(sub_name)
                    )

                    # Search for posts mentioning the symbol
                    query = f"${symbol} OR {symbol}"
                    search_results = await loop.run_in_executor(
                        None,
                        lambda: list(subreddit.search(query, time_filter="day", limit=50))
                    )

                    for post in search_results:
                        # Analyze post sentiment
                        text = f"{post.title} {post.selftext}".lower()
                        sentiment = self._analyze_text_sentiment(text)

                        mentions.append({
                            "subreddit": sub_name,
                            "title": post.title,
                            "score": post.score,
                            "sentiment": sentiment,
                            "created": datetime.fromtimestamp(post.created_utc)
                        })

                except Exception as e:
                    logger.warning(f"Error fetching from r/{sub_name}: {e}")
                    continue

            # Calculate overall sentiment
            if not mentions:
                return {"sentiment": SentimentType.NEUTRAL, "mentions": 0}

            # Weight sentiment by post score
            positive_score = sum(m["score"] for m in mentions if m["sentiment"] == "positive")
            negative_score = sum(m["score"] for m in mentions if m["sentiment"] == "negative")
            neutral_score = sum(m["score"] for m in mentions if m["sentiment"] == "neutral")

            total_score = positive_score + negative_score + neutral_score

            if total_score == 0:
                overall_sentiment = SentimentType.NEUTRAL
            elif positive_score > negative_score * 1.5:
                overall_sentiment = SentimentType.POSITIVE
            elif negative_score > positive_score * 1.5:
                overall_sentiment = SentimentType.NEGATIVE
            else:
                overall_sentiment = SentimentType.NEUTRAL

            logger.info(f"Found {len(mentions)} Reddit mentions for {symbol}")

            return {
                "sentiment": overall_sentiment,
                "mentions": len(mentions)
            }

        except Exception as e:
            logger.error(f"Reddit sentiment analysis failed: {e}")
            return {"sentiment": SentimentType.NEUTRAL, "mentions": 0}

    def _analyze_text_sentiment(self, text: str) -> str:
        """
        Analyze sentiment of text using keyword matching.

        Args:
            text: Text to analyze

        Returns:
            "positive", "negative", or "neutral"
        """
        words = set(re.findall(r'\w+', text.lower()))

        positive_count = len(words & self.positive_keywords)
        negative_count = len(words & self.negative_keywords)

        if positive_count > negative_count:
            return "positive"
        elif negative_count > positive_count:
            return "negative"
        else:
            return "neutral"

    async def _get_analyst_ratings(self, symbol: str) -> dict:
        """
        Fetch analyst ratings from yfinance.

        Args:
            symbol: Stock ticker

        Returns:
            Dictionary with rating and consensus
        """
        try:
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol)

            # Fetch analyst recommendations
            recommendations = await loop.run_in_executor(
                None,
                lambda: ticker.recommendations
            )

            if recommendations is None or recommendations.empty:
                logger.debug(f"No analyst recommendations for {symbol}")
                return {
                    "rating": AnalystRating.HOLD,
                    "consensus": AnalystConsensus(0, 0, 1, 0, 0)
                }

            # Get most recent recommendations (last 3 months)
            recent = recommendations.tail(30)

            # Count ratings
            rating_counts = Counter()
            for _, row in recent.iterrows():
                rating = row.get("To Grade", "hold").lower()

                # Map to our rating system
                if "strong buy" in rating or "outperform" in rating:
                    rating_counts["strong_buy"] += 1
                elif "buy" in rating or "overweight" in rating:
                    rating_counts["buy"] += 1
                elif "sell" in rating or "underweight" in rating:
                    rating_counts["sell"] += 1
                elif "strong sell" in rating or "reduce" in rating:
                    rating_counts["strong_sell"] += 1
                else:
                    rating_counts["hold"] += 1

            consensus = AnalystConsensus(
                strong_buy=rating_counts.get("strong_buy", 0),
                buy=rating_counts.get("buy", 0),
                hold=rating_counts.get("hold", 0),
                sell=rating_counts.get("sell", 0),
                strong_sell=rating_counts.get("strong_sell", 0)
            )

            # Determine overall rating from consensus
            avg_rating = consensus.average_rating

            if avg_rating <= 1.5:
                overall_rating = AnalystRating.STRONG_BUY
            elif avg_rating <= 2.5:
                overall_rating = AnalystRating.BUY
            elif avg_rating <= 3.5:
                overall_rating = AnalystRating.HOLD
            elif avg_rating <= 4.5:
                overall_rating = AnalystRating.SELL
            else:
                overall_rating = AnalystRating.STRONG_SELL

            logger.info(f"Analyst consensus for {symbol}: {overall_rating.value}")

            return {
                "rating": overall_rating,
                "consensus": consensus
            }

        except Exception as e:
            logger.error(f"Error fetching analyst ratings: {e}")
            return {
                "rating": AnalystRating.HOLD,
                "consensus": AnalystConsensus(0, 0, 1, 0, 0)
            }

    async def _get_insider_trades(self, symbol: str) -> List[InsiderTrade]:
        """
        Fetch insider trading activity from yfinance.

        Args:
            symbol: Stock ticker

        Returns:
            List of InsiderTrade objects
        """
        try:
            loop = asyncio.get_event_loop()
            ticker = yf.Ticker(symbol)

            # Fetch insider transactions
            insider_transactions = await loop.run_in_executor(
                None,
                lambda: ticker.insider_transactions
            )

            if insider_transactions is None or insider_transactions.empty:
                logger.debug(f"No insider transactions for {symbol}")
                return []

            # Convert to InsiderTrade objects (last 10 trades)
            trades = []
            for _, row in insider_transactions.head(10).iterrows():
                try:
                    # Determine transaction type
                    transaction = str(row.get("Transaction", "")).lower()
                    if "sale" in transaction or "sell" in transaction:
                        tx_type = "sell"
                    elif "purchase" in transaction or "buy" in transaction:
                        tx_type = "buy"
                    else:
                        continue  # Skip other types

                    shares = int(row.get("Shares", 0))
                    if shares == 0:
                        continue

                    # Get price
                    price = float(row.get("Value", 0)) / shares if shares > 0 else 0.0

                    trade = InsiderTrade(
                        date=str(row.get("Start Date", "")),
                        insider_name=str(row.get("Insider", "Unknown")),
                        transaction_type=tx_type,
                        shares=shares,
                        price=price,
                        value=float(row.get("Value", 0))
                    )
                    trades.append(trade)

                except Exception as e:
                    logger.debug(f"Error parsing insider trade: {e}")
                    continue

            logger.info(f"Found {len(trades)} insider trades for {symbol}")
            return trades

        except Exception as e:
            logger.error(f"Error fetching insider trades: {e}")
            return []

    def _analyze_institutional_flow(
        self,
        analyst_data: dict,
        insider_trades: List[InsiderTrade]
    ) -> InstitutionalFlow:
        """
        Analyze institutional flow based on analyst ratings and insider activity.

        Args:
            analyst_data: Analyst ratings data
            insider_trades: List of insider trades

        Returns:
            InstitutionalFlow enum
        """
        # Score based on analyst consensus
        consensus = analyst_data["consensus"]
        avg_rating = consensus.average_rating

        # Score based on insider activity (last 10 trades)
        insider_buy_value = sum(t.value for t in insider_trades if t.transaction_type == "buy")
        insider_sell_value = sum(t.value for t in insider_trades if t.transaction_type == "sell")

        # Calculate net insider flow
        net_insider = insider_buy_value - insider_sell_value

        # Combine signals
        analyst_bullish = avg_rating < 2.5  # Buy or Strong Buy
        analyst_bearish = avg_rating > 3.5  # Sell or Strong Sell

        insider_bullish = net_insider > 1_000_000  # Net buying > $1M
        insider_bearish = net_insider < -1_000_000  # Net selling > $1M

        # Determine flow
        if analyst_bullish and insider_bullish:
            return InstitutionalFlow.HEAVY_BUYING
        elif analyst_bullish or insider_bullish:
            return InstitutionalFlow.MODERATE_BUYING
        elif analyst_bearish and insider_bearish:
            return InstitutionalFlow.HEAVY_SELLING
        elif analyst_bearish or insider_bearish:
            return InstitutionalFlow.MODERATE_SELLING
        else:
            return InstitutionalFlow.NEUTRAL

    def _calculate_sentiment_score(
        self,
        reddit_data: dict,
        analyst_data: dict,
        institutional_flow: InstitutionalFlow,
        insider_trades: List[InsiderTrade]
    ) -> int:
        """
        Calculate overall sentiment score (0-100).

        Scoring methodology:
        - Analyst consensus (40 points)
        - Social sentiment (30 points)
        - Institutional flow (20 points)
        - Insider activity (10 points)
        """
        score = 0

        # Analyst consensus score (40 points)
        avg_rating = analyst_data["consensus"].average_rating
        if avg_rating <= 1.5:
            score += 40
        elif avg_rating <= 2.5:
            score += 32
        elif avg_rating <= 3.5:
            score += 20
        elif avg_rating <= 4.5:
            score += 8
        else:
            score += 0

        # Social sentiment score (30 points)
        social_sentiment = reddit_data["sentiment"]
        if social_sentiment == SentimentType.POSITIVE:
            score += 30
        elif social_sentiment == SentimentType.NEUTRAL:
            score += 15
        else:
            score += 5

        # Institutional flow score (20 points)
        if institutional_flow == InstitutionalFlow.HEAVY_BUYING:
            score += 20
        elif institutional_flow == InstitutionalFlow.MODERATE_BUYING:
            score += 15
        elif institutional_flow == InstitutionalFlow.NEUTRAL:
            score += 10
        elif institutional_flow == InstitutionalFlow.MODERATE_SELLING:
            score += 5
        else:
            score += 0

        # Insider activity score (10 points)
        insider_buys = sum(1 for t in insider_trades if t.transaction_type == "buy")
        insider_sells = sum(1 for t in insider_trades if t.transaction_type == "sell")

        if insider_buys > insider_sells:
            score += 10
        elif insider_buys == insider_sells:
            score += 5
        else:
            score += 2

        return min(score, 100)

    def _create_fallback_analysis(self, symbol: str) -> SentimentAnalysis:
        """Create fallback analysis when data fetching fails."""
        logger.warning(f"Creating fallback sentiment analysis for {symbol}")

        return SentimentAnalysis(
            score=50,
            news_sentiment=SentimentType.NEUTRAL,
            news_count_7d=0,
            social_sentiment=SentimentType.NEUTRAL,
            reddit_mentions_24h=0,
            stocktwits_sentiment=0.0,
            institutional_flow=InstitutionalFlow.NEUTRAL,
            insider_trades=[],
            analyst_rating=AnalystRating.HOLD,
            analyst_consensus=AnalystConsensus(0, 0, 1, 0, 0)
        )
