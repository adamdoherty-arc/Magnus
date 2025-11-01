"""
Example Usage of AI Research Agents

Demonstrates how to use all four specialist agents for comprehensive stock analysis.
"""

import asyncio
import os
from loguru import logger

# Configure logging
logger.add("ai_research.log", rotation="10 MB", level="INFO")

from fundamental_agent import FundamentalAgent
from technical_agent import TechnicalAgent
from sentiment_agent import SentimentAgent
from options_agent import OptionsAgent


async def analyze_stock_comprehensive(symbol: str):
    """
    Run all four agents on a stock and display results.

    Args:
        symbol: Stock ticker to analyze
    """
    logger.info(f"Starting comprehensive analysis for {symbol}")
    print(f"\n{'='*80}")
    print(f"Comprehensive AI Research Analysis: {symbol}")
    print(f"{'='*80}\n")

    # Initialize all agents
    fundamental_agent = FundamentalAgent()
    technical_agent = TechnicalAgent()
    sentiment_agent = SentimentAgent()
    options_agent = OptionsAgent()

    # Run all analyses in parallel for maximum speed
    logger.info("Running all agents in parallel...")
    results = await asyncio.gather(
        fundamental_agent.analyze(symbol),
        technical_agent.analyze(symbol),
        sentiment_agent.analyze(symbol),
        options_agent.analyze(symbol),
        return_exceptions=True
    )

    fundamental, technical, sentiment, options = results

    # Display Fundamental Analysis
    print("\n" + "="*80)
    print("1. FUNDAMENTAL ANALYSIS")
    print("="*80)

    if isinstance(fundamental, Exception):
        print(f"Error: {fundamental}")
    else:
        print(f"\nOverall Score: {fundamental.score}/100")
        print(f"Valuation: {fundamental.valuation_assessment}")
        print(f"\nKey Metrics:")
        print(f"  P/E Ratio: {fundamental.pe_ratio:.2f} (Sector Avg: {fundamental.sector_avg_pe:.2f})")
        print(f"  P/B Ratio: {fundamental.pb_ratio:.2f}")
        print(f"  ROE: {fundamental.roe*100:.2f}%")
        print(f"  Debt/Equity: {fundamental.debt_to_equity:.2f}")
        print(f"  Revenue Growth YoY: {fundamental.revenue_growth_yoy*100:.2f}%")
        print(f"  Dividend Yield: {fundamental.dividend_yield*100:.2f}%")
        print(f"  Free Cash Flow: ${fundamental.free_cash_flow:,.0f}")

        print(f"\nStrengths:")
        for strength in fundamental.key_strengths:
            print(f"  - {strength}")

        print(f"\nRisks:")
        for risk in fundamental.key_risks:
            print(f"  - {risk}")

        if fundamental.next_earnings_date:
            print(f"\nNext Earnings: {fundamental.next_earnings_date}")

    # Display Technical Analysis
    print("\n" + "="*80)
    print("2. TECHNICAL ANALYSIS")
    print("="*80)

    if isinstance(technical, Exception):
        print(f"Error: {technical}")
    else:
        print(f"\nOverall Score: {technical.score}/100")
        print(f"Trend: {technical.trend.value.upper()}")
        print(f"\nIndicators:")
        print(f"  RSI: {technical.rsi:.2f}")
        print(f"  MACD Signal: {technical.macd_signal.value.upper()}")

        ma = technical.moving_averages
        print(f"\nMoving Averages:")
        print(f"  Current Price: ${ma['current_price']:.2f}")
        print(f"  MA20: ${ma['MA20']:.2f}")
        print(f"  MA50: ${ma['MA50']:.2f}")
        print(f"  MA200: ${ma['MA200']:.2f}")

        bb = technical.bollinger_bands
        print(f"\nBollinger Bands:")
        print(f"  Upper: ${bb['upper']:.2f}")
        print(f"  Middle: ${bb['middle']:.2f}")
        print(f"  Lower: ${bb['lower']:.2f}")

        print(f"\nSupport Levels: {', '.join([f'${s:.2f}' for s in technical.support_levels])}")
        print(f"Resistance Levels: {', '.join([f'${r:.2f}' for r in technical.resistance_levels])}")

        print(f"\nVolume Analysis: {technical.volume_analysis}")

        print(f"\nChart Patterns:")
        for pattern in technical.chart_patterns:
            print(f"  - {pattern}")

        print(f"\nRecommendation: {technical.recommendation}")

    # Display Sentiment Analysis
    print("\n" + "="*80)
    print("3. SENTIMENT ANALYSIS")
    print("="*80)

    if isinstance(sentiment, Exception):
        print(f"Error: {sentiment}")
    else:
        print(f"\nOverall Score: {sentiment.score}/100")

        print(f"\nSocial Sentiment:")
        print(f"  Reddit: {sentiment.social_sentiment.value.upper()}")
        print(f"  Reddit Mentions (24h): {sentiment.reddit_mentions_24h}")

        print(f"\nAnalyst Ratings:")
        print(f"  Overall Rating: {sentiment.analyst_rating.value.upper()}")

        consensus = sentiment.analyst_consensus
        print(f"  Consensus Breakdown:")
        print(f"    Strong Buy: {consensus.strong_buy}")
        print(f"    Buy: {consensus.buy}")
        print(f"    Hold: {consensus.hold}")
        print(f"    Sell: {consensus.sell}")
        print(f"    Strong Sell: {consensus.strong_sell}")
        print(f"    Average Rating: {consensus.average_rating:.2f}/5.0")

        print(f"\nInstitutional Flow: {sentiment.institutional_flow.value.upper()}")

        if sentiment.insider_trades:
            print(f"\nRecent Insider Trades:")
            for trade in sentiment.insider_trades[:5]:
                print(f"  - {trade.date}: {trade.insider_name} {trade.transaction_type.upper()} "
                      f"{trade.shares:,} shares @ ${trade.price:.2f} (${trade.value:,.0f})")
        else:
            print("\nNo recent insider trades")

    # Display Options Analysis
    print("\n" + "="*80)
    print("4. OPTIONS ANALYSIS")
    print("="*80)

    if isinstance(options, Exception):
        print(f"Error: {options}")
    else:
        print(f"\nImplied Volatility:")
        print(f"  Current IV: {options.current_iv*100:.2f}%")
        print(f"  IV Rank: {options.iv_rank}/100")
        print(f"  IV Percentile: {options.iv_percentile}/100")
        print(f"  30-Day Mean: {options.iv_mean_30d*100:.2f}%")
        print(f"  30-Day Std Dev: {options.iv_std_30d*100:.2f}%")

        print(f"\nEarnings:")
        print(f"  Next Earnings Date: {options.next_earnings_date}")
        print(f"  Days to Earnings: {options.days_to_earnings}")
        print(f"  Avg Earnings Move: {options.avg_earnings_move*100:.2f}%")

        print(f"\nOptions Metrics:")
        print(f"  Put/Call Ratio: {options.put_call_ratio:.2f}")
        print(f"  Max Pain: ${options.max_pain:.2f}")

        if options.unusual_options_activity:
            print(f"\nUnusual Options Activity:")
            for activity in options.unusual_options_activity[:5]:
                print(f"  - {activity.option_type.upper()} ${activity.strike} exp {activity.expiration}")
                print(f"    Volume: {activity.volume:,} | OI: {activity.open_interest:,} | "
                      f"Vol/OI: {activity.volume_oi_ratio:.2f}")
                print(f"    Premium: ${activity.premium:,.0f}")
                print(f"    {activity.description}")
        else:
            print("\nNo unusual options activity detected")

        print(f"\nRecommended Strategies:")
        for i, strategy in enumerate(options.recommended_strategies, 1):
            print(f"\n  Strategy {i}: {strategy.strategy.upper()}")
            print(f"    Strike: ${strategy.strike:.2f}")
            print(f"    Expiration: {strategy.expiration}")
            print(f"    Premium: ${strategy.premium:.2f} per share")
            print(f"    Probability of Profit: {strategy.probability_of_profit*100:.1f}%")
            print(f"    Max Profit: ${strategy.max_profit:.2f}")
            if strategy.max_loss != float('inf'):
                print(f"    Max Loss: ${strategy.max_loss:.2f}")
            else:
                print(f"    Max Loss: Unlimited")
            print(f"    Rationale: {strategy.rationale}")

    # Summary
    print("\n" + "="*80)
    print("ANALYSIS SUMMARY")
    print("="*80)

    scores = []
    if not isinstance(fundamental, Exception):
        scores.append(("Fundamental", fundamental.score))
    if not isinstance(technical, Exception):
        scores.append(("Technical", technical.score))
    if not isinstance(sentiment, Exception):
        scores.append(("Sentiment", sentiment.score))

    if scores:
        print("\nAgent Scores:")
        for name, score in scores:
            print(f"  {name}: {score}/100")

        avg_score = sum(s for _, s in scores) / len(scores)
        print(f"\nOverall Average Score: {avg_score:.1f}/100")

        if avg_score >= 70:
            print("\nConclusion: BULLISH - Strong signals across multiple analysis dimensions")
        elif avg_score >= 50:
            print("\nConclusion: NEUTRAL - Mixed signals, exercise caution")
        else:
            print("\nConclusion: BEARISH - Weak fundamentals or technical setup")

    print("\n" + "="*80 + "\n")
    logger.info(f"Completed comprehensive analysis for {symbol}")


async def analyze_multiple_stocks(symbols: list):
    """
    Analyze multiple stocks in parallel.

    Args:
        symbols: List of stock tickers
    """
    print(f"\nAnalyzing {len(symbols)} stocks in parallel...")

    tasks = [analyze_stock_comprehensive(symbol) for symbol in symbols]
    await asyncio.gather(*tasks, return_exceptions=True)


async def main():
    """Main entry point for example script."""
    # Example 1: Single stock analysis
    symbol = "AAPL"  # Change to any stock ticker

    # Check for required environment variables
    if not os.getenv("ALPHA_VANTAGE_API_KEY"):
        print("WARNING: ALPHA_VANTAGE_API_KEY not set - fundamental analysis will use fallback data")
        print("Get a free key at: https://www.alphavantage.co/support/#api-key\n")

    if not os.getenv("REDDIT_CLIENT_ID"):
        print("INFO: Reddit API credentials not set - sentiment analysis will skip Reddit data")
        print("Get credentials at: https://www.reddit.com/prefs/apps\n")

    await analyze_stock_comprehensive(symbol)

    # Example 2: Multiple stocks (uncomment to use)
    # symbols = ["AAPL", "MSFT", "GOOGL", "TSLA"]
    # await analyze_multiple_stocks(symbols)


if __name__ == "__main__":
    # Run the async main function
    asyncio.run(main())
