"""
AI Options Agent - Scoring Engine
Multi-Criteria Decision Making (MCDM) system for evaluating options opportunities

Implements 5 specialized scorers:
- FundamentalScorer: Company fundamentals (P/E, EPS, sector strength)
- TechnicalScorer: Price trends and technical indicators
- GreeksScorer: Options Greeks analysis (Delta, IV, Theta)
- RiskScorer: Risk assessment (max loss, probability, breakeven)
- SentimentScorer: Market sentiment analysis (stub for now)

Each scorer returns 0-100 score. Final score is weighted average.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime, date

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FundamentalScorer:
    """
    Scores opportunities based on company fundamentals

    Scoring Factors:
    - P/E Ratio (20%): Lower P/E for value, higher for growth
    - EPS Growth (25%): Positive EPS trend
    - Market Cap (15%): Stability preference
    - Sector Strength (20%): Quality sectors weighted higher
    - Dividend Yield (10%): Income generation
    - Financial Health (10%): Debt ratios, profitability
    """

    # Tier 1 sectors (score 100): Technology, Healthcare, Consumer Staples
    # Tier 2 sectors (score 80): Financials, Industrials, Consumer Discretionary
    # Tier 3 sectors (score 60): Energy, Materials, Real Estate
    # Tier 4 sectors (score 40): Utilities, Communication Services
    SECTOR_SCORES = {
        'Technology': 100,
        'Healthcare': 100,
        'Consumer Staples': 100,
        'Financials': 80,
        'Industrials': 80,
        'Consumer Discretionary': 80,
        'Energy': 60,
        'Materials': 60,
        'Real Estate': 60,
        'Utilities': 40,
        'Communication Services': 40,
    }

    def score(self, opportunity: Dict[str, Any]) -> int:
        """
        Score based on fundamental analysis

        Args:
            opportunity: Dict with keys: pe_ratio, eps, market_cap, sector, dividend_yield

        Returns:
            Score 0-100
        """
        try:
            scores = []
            weights = []

            # P/E Ratio scoring (20%)
            pe_ratio = opportunity.get('pe_ratio')
            if pe_ratio and pe_ratio > 0:
                if 10 <= pe_ratio <= 25:
                    pe_score = 100  # Ideal range
                elif 5 <= pe_ratio < 10:
                    pe_score = 80  # Value stock
                elif 25 < pe_ratio <= 35:
                    pe_score = 70  # Growth stock
                elif pe_ratio < 5:
                    pe_score = 50  # Too cheap, potential issues
                else:
                    pe_score = 40  # Too expensive
                scores.append(pe_score)
                weights.append(0.20)

            # EPS scoring (25%) - currently not available in database
            # TODO: Add EPS data to stocks table for better fundamental analysis
            eps = opportunity.get('eps')
            if eps is not None:  # Only score if EPS data exists
                if eps > 5:
                    eps_score = 100
                elif eps > 2:
                    eps_score = 85
                elif eps > 1:
                    eps_score = 70
                elif eps > 0:
                    eps_score = 55
                else:
                    eps_score = 20  # Negative EPS
                scores.append(eps_score)
                weights.append(0.25)

            # Market Cap scoring (15%) - prefer large/mega cap for wheel strategy
            market_cap = opportunity.get('market_cap')
            if market_cap:
                if market_cap >= 200_000_000_000:  # $200B+ mega cap
                    mc_score = 100
                elif market_cap >= 10_000_000_000:  # $10B+ large cap
                    mc_score = 90
                elif market_cap >= 2_000_000_000:  # $2B+ mid cap
                    mc_score = 70
                else:  # Small cap
                    mc_score = 50
                scores.append(mc_score)
                weights.append(0.15)

            # Sector scoring (20%)
            sector = opportunity.get('sector')
            if sector:
                sector_score = self.SECTOR_SCORES.get(sector, 50)  # Default 50 if unknown
                scores.append(sector_score)
                weights.append(0.20)

            # Dividend Yield scoring (10%)
            dividend_yield = opportunity.get('dividend_yield')
            if dividend_yield is not None:
                if dividend_yield >= 3.0:
                    div_score = 100
                elif dividend_yield >= 2.0:
                    div_score = 85
                elif dividend_yield >= 1.0:
                    div_score = 70
                else:
                    div_score = 50  # No/low dividend is okay
                scores.append(div_score)
                weights.append(0.10)

            # Calculate weighted average
            if not scores:
                logger.warning(f"No fundamental data for {opportunity.get('symbol')}")
                return 50  # Neutral if no data

            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

            return int(weighted_score)

        except Exception as e:
            logger.error(f"Error in FundamentalScorer: {e}")
            return 50  # Neutral on error


class TechnicalScorer:
    """
    Scores opportunities based on technical analysis

    Scoring Factors:
    - Price vs Strike (30%): How far OTM the put is
    - Volume (20%): Liquidity indicator
    - Open Interest (20%): Market depth
    - Price Trend (30%): Recent price stability
    """

    def score(self, opportunity: Dict[str, Any]) -> int:
        """
        Score based on technical indicators

        Args:
            opportunity: Dict with keys: stock_price, strike_price, volume, oi

        Returns:
            Score 0-100
        """
        try:
            scores = []
            weights = []

            # Price vs Strike scoring (30%)
            stock_price = opportunity.get('stock_price')
            strike_price = opportunity.get('strike_price')

            if stock_price and strike_price and stock_price > 0:
                otm_percent = ((stock_price - strike_price) / stock_price) * 100

                # Ideal: 10-20% OTM for CSP
                if 10 <= otm_percent <= 20:
                    price_score = 100
                elif 5 <= otm_percent < 10:
                    price_score = 85
                elif 20 < otm_percent <= 30:
                    price_score = 75
                elif 0 <= otm_percent < 5:
                    price_score = 60  # Too close to ATM
                else:
                    price_score = 40  # Too far OTM or ITM

                scores.append(price_score)
                weights.append(0.30)

            # Volume scoring (20%)
            volume = opportunity.get('volume')
            if volume is not None:
                if volume >= 1000:
                    vol_score = 100
                elif volume >= 500:
                    vol_score = 85
                elif volume >= 100:
                    vol_score = 70
                elif volume >= 50:
                    vol_score = 55
                else:
                    vol_score = 30  # Low liquidity
                scores.append(vol_score)
                weights.append(0.20)

            # Open Interest scoring (20%)
            oi = opportunity.get('oi')
            if oi is not None:
                if oi >= 1000:
                    oi_score = 100
                elif oi >= 500:
                    oi_score = 85
                elif oi >= 250:
                    oi_score = 70
                elif oi >= 100:
                    oi_score = 55
                else:
                    oi_score = 30  # Low liquidity
                scores.append(oi_score)
                weights.append(0.20)

            # Bid-Ask Spread scoring (30%)
            bid = opportunity.get('bid')
            ask = opportunity.get('ask')
            if bid and ask and bid > 0:
                spread_pct = ((ask - bid) / bid) * 100

                if spread_pct <= 3:
                    spread_score = 100  # Tight spread
                elif spread_pct <= 5:
                    spread_score = 85
                elif spread_pct <= 10:
                    spread_score = 70
                elif spread_pct <= 15:
                    spread_score = 50
                else:
                    spread_score = 30  # Wide spread

                scores.append(spread_score)
                weights.append(0.30)

            # Calculate weighted average
            if not scores:
                logger.warning(f"No technical data for {opportunity.get('symbol')}")
                return 50

            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

            return int(weighted_score)

        except Exception as e:
            logger.error(f"Error in TechnicalScorer: {e}")
            return 50


class GreeksScorer:
    """
    Scores opportunities based on Options Greeks

    Scoring Factors:
    - Delta (30%): Target -0.20 to -0.35 for CSP
    - Implied Volatility (30%): Higher IV = higher premium
    - Premium/Strike Ratio (25%): Return potential
    - DTE Range (15%): Target 25-35 DTE
    """

    def score(self, opportunity: Dict[str, Any]) -> int:
        """
        Score based on Options Greeks

        Args:
            opportunity: Dict with keys: delta, iv, premium, strike_price, dte

        Returns:
            Score 0-100
        """
        try:
            scores = []
            weights = []

            # Delta scoring (30%)
            delta = opportunity.get('delta')
            if delta is not None:
                abs_delta = abs(delta)

                # Target: 0.20-0.35 delta for CSP
                if 0.20 <= abs_delta <= 0.35:
                    delta_score = 100
                elif 0.15 <= abs_delta < 0.20 or 0.35 < abs_delta <= 0.40:
                    delta_score = 85
                elif 0.10 <= abs_delta < 0.15 or 0.40 < abs_delta <= 0.45:
                    delta_score = 70
                else:
                    delta_score = 50  # Too high or too low

                scores.append(delta_score)
                weights.append(0.30)

            # Implied Volatility scoring (30%)
            iv = opportunity.get('iv')
            if iv is not None:
                iv_pct = iv * 100  # Convert to percentage

                # Higher IV = higher premium (good for sellers)
                if iv_pct >= 50:
                    iv_score = 100
                elif iv_pct >= 40:
                    iv_score = 90
                elif iv_pct >= 30:
                    iv_score = 80
                elif iv_pct >= 25:
                    iv_score = 70
                elif iv_pct >= 20:
                    iv_score = 60
                else:
                    iv_score = 40  # Too low IV

                scores.append(iv_score)
                weights.append(0.30)

            # Premium/Strike Ratio scoring (25%)
            premium = opportunity.get('premium')
            strike_price = opportunity.get('strike_price')

            if premium and strike_price and strike_price > 0:
                premium_ratio = (premium / strike_price) * 100

                # Target: 1-3% premium per contract
                if 2.0 <= premium_ratio <= 4.0:
                    prem_score = 100
                elif 1.5 <= premium_ratio < 2.0 or 4.0 < premium_ratio <= 5.0:
                    prem_score = 85
                elif 1.0 <= premium_ratio < 1.5 or 5.0 < premium_ratio <= 6.0:
                    prem_score = 70
                else:
                    prem_score = 50

                scores.append(prem_score)
                weights.append(0.25)

            # DTE scoring (15%)
            dte = opportunity.get('dte')
            if dte is not None:
                # Target: 25-35 DTE
                if 25 <= dte <= 35:
                    dte_score = 100
                elif 20 <= dte < 25 or 35 < dte <= 40:
                    dte_score = 85
                elif 15 <= dte < 20 or 40 < dte <= 45:
                    dte_score = 70
                else:
                    dte_score = 50

                scores.append(dte_score)
                weights.append(0.15)

            # Calculate weighted average
            if not scores:
                logger.warning(f"No Greeks data for {opportunity.get('symbol')}")
                return 50

            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

            return int(weighted_score)

        except Exception as e:
            logger.error(f"Error in GreeksScorer: {e}")
            return 50


class RiskScorer:
    """
    Scores opportunities based on risk assessment

    Scoring Factors:
    - Max Loss (35%): Capital at risk
    - Probability of Profit (30%): Based on delta
    - Breakeven Distance (20%): Safety margin
    - Annualized Return (15%): Risk-adjusted return
    """

    def score(self, opportunity: Dict[str, Any]) -> int:
        """
        Score based on risk metrics

        Args:
            opportunity: Dict with keys: strike_price, premium, delta, stock_price, annual_return

        Returns:
            Score 0-100 (higher = lower risk)
        """
        try:
            scores = []
            weights = []

            # Max Loss scoring (35%) - lower is better
            strike_price = opportunity.get('strike_price')
            premium = opportunity.get('premium')

            if strike_price and premium:
                max_loss = strike_price - (premium / 100)  # Premium is in cents

                # Prefer lower max loss
                if max_loss <= 20:
                    loss_score = 100
                elif max_loss <= 50:
                    loss_score = 90
                elif max_loss <= 100:
                    loss_score = 75
                elif max_loss <= 200:
                    loss_score = 60
                else:
                    loss_score = 40

                scores.append(loss_score)
                weights.append(0.35)

            # Probability of Profit scoring (30%) - based on delta
            delta = opportunity.get('delta')
            if delta is not None:
                # For puts, probability of profit ≈ 100 - |delta * 100|
                prob_profit = 100 - (abs(delta) * 100)

                if prob_profit >= 75:
                    prob_score = 100
                elif prob_profit >= 65:
                    prob_score = 85
                elif prob_profit >= 55:
                    prob_score = 70
                else:
                    prob_score = 50

                scores.append(prob_score)
                weights.append(0.30)

            # Breakeven Distance scoring (20%)
            stock_price = opportunity.get('stock_price')
            breakeven = opportunity.get('breakeven')

            if stock_price and breakeven and stock_price > 0:
                breakeven_distance = ((stock_price - breakeven) / stock_price) * 100

                # Higher distance = safer
                if breakeven_distance >= 15:
                    be_score = 100
                elif breakeven_distance >= 10:
                    be_score = 85
                elif breakeven_distance >= 5:
                    be_score = 70
                else:
                    be_score = 50

                scores.append(be_score)
                weights.append(0.20)

            # Annualized Return scoring (15%)
            annual_return = opportunity.get('annual_return')
            if annual_return is not None:
                # Target: 20-40% annual return for wheel strategy
                if 25 <= annual_return <= 45:
                    ret_score = 100
                elif 15 <= annual_return < 25 or 45 < annual_return <= 60:
                    ret_score = 85
                elif 10 <= annual_return < 15 or 60 < annual_return <= 80:
                    ret_score = 70
                else:
                    ret_score = 50

                scores.append(ret_score)
                weights.append(0.15)

            # Calculate weighted average
            if not scores:
                logger.warning(f"No risk data for {opportunity.get('symbol')}")
                return 50

            total_weight = sum(weights)
            weighted_score = sum(s * w for s, w in zip(scores, weights)) / total_weight

            return int(weighted_score)

        except Exception as e:
            logger.error(f"Error in RiskScorer: {e}")
            return 50


class SentimentScorer:
    """
    Scores opportunities based on market sentiment

    NOTE: This is a stub implementation. Full implementation requires:
    - News sentiment API (Finnhub, Alpha Vantage)
    - Social media sentiment (Reddit WSB, Twitter/X)
    - Analyst ratings aggregation
    - Insider trading data

    For now, returns neutral score (70) for all symbols.
    TODO: Implement full sentiment analysis in Phase 3-4
    """

    def score(self, opportunity: Dict[str, Any]) -> int:
        """
        Score based on market sentiment (stub)

        Args:
            opportunity: Dict with symbol

        Returns:
            Score 0-100 (currently always 70 = neutral)
        """
        # Stub: Return neutral score
        # TODO: Implement sentiment analysis:
        # - Check news sentiment from Finnhub API
        # - Analyze Reddit WSB mentions
        # - Aggregate analyst ratings
        # - Check insider trading

        return 70  # Neutral sentiment


class MultiCriteriaScorer:
    """
    Combines all scorers using weighted Multi-Criteria Decision Making (MCDM)

    Default Weights:
    - Fundamental: 20%
    - Technical: 20%
    - Greeks: 20%
    - Risk: 25%
    - Sentiment: 15%

    Total: 100%
    """

    DEFAULT_WEIGHTS = {
        'fundamental': 0.20,
        'technical': 0.20,
        'greeks': 0.20,
        'risk': 0.25,
        'sentiment': 0.15
    }

    def __init__(self, weights: Optional[Dict[str, float]] = None):
        """
        Initialize multi-criteria scorer

        Args:
            weights: Optional custom weights dict (must sum to 1.0)
        """
        self.weights = weights or self.DEFAULT_WEIGHTS

        # Validate weights sum to 1.0
        total = sum(self.weights.values())
        if not 0.99 <= total <= 1.01:  # Allow small floating point error
            raise ValueError(f"Weights must sum to 1.0, got {total}")

        # Initialize individual scorers
        self.fundamental_scorer = FundamentalScorer()
        self.technical_scorer = TechnicalScorer()
        self.greeks_scorer = GreeksScorer()
        self.risk_scorer = RiskScorer()
        self.sentiment_scorer = SentimentScorer()

        logger.info(f"Initialized MultiCriteriaScorer with weights: {self.weights}")

    def score_opportunity(self, opportunity: Dict[str, Any]) -> Dict[str, Any]:
        """
        Score an opportunity using all criteria

        Args:
            opportunity: Dict with all opportunity data

        Returns:
            Dict with individual scores, final score, and recommendation:
            {
                'symbol': str,
                'fundamental_score': int,
                'technical_score': int,
                'greeks_score': int,
                'risk_score': int,
                'sentiment_score': int,
                'final_score': int,
                'recommendation': str,  # STRONG_BUY, BUY, HOLD, CAUTION, AVOID
                'confidence': int  # 0-100
            }
        """
        try:
            symbol = opportunity.get('symbol', 'UNKNOWN')

            # Calculate individual scores
            fundamental_score = self.fundamental_scorer.score(opportunity)
            technical_score = self.technical_scorer.score(opportunity)
            greeks_score = self.greeks_scorer.score(opportunity)
            risk_score = self.risk_scorer.score(opportunity)
            sentiment_score = self.sentiment_scorer.score(opportunity)

            # Calculate weighted final score
            final_score = int(
                fundamental_score * self.weights['fundamental'] +
                technical_score * self.weights['technical'] +
                greeks_score * self.weights['greeks'] +
                risk_score * self.weights['risk'] +
                sentiment_score * self.weights['sentiment']
            )

            # Determine recommendation based on final score
            if final_score >= 85:
                recommendation = 'STRONG_BUY'
                confidence = 90
            elif final_score >= 75:
                recommendation = 'BUY'
                confidence = 80
            elif final_score >= 60:
                recommendation = 'HOLD'
                confidence = 70
            elif final_score >= 45:
                recommendation = 'CAUTION'
                confidence = 60
            else:
                recommendation = 'AVOID'
                confidence = 50

            result = {
                'symbol': symbol,
                'fundamental_score': fundamental_score,
                'technical_score': technical_score,
                'greeks_score': greeks_score,
                'risk_score': risk_score,
                'sentiment_score': sentiment_score,
                'final_score': final_score,
                'recommendation': recommendation,
                'confidence': confidence,

                # Include key metrics for display
                'strike_price': opportunity.get('strike_price'),
                'expiration_date': opportunity.get('expiration_date'),
                'dte': opportunity.get('dte'),
                'premium': opportunity.get('premium'),
                'delta': opportunity.get('delta'),
                'monthly_return': opportunity.get('monthly_return'),
                'annual_return': opportunity.get('annual_return')
            }

            logger.info(f"Scored {symbol}: {final_score}/100 ({recommendation})")
            return result

        except Exception as e:
            logger.error(f"Error scoring opportunity: {e}")
            return {
                'symbol': opportunity.get('symbol', 'ERROR'),
                'fundamental_score': 0,
                'technical_score': 0,
                'greeks_score': 0,
                'risk_score': 0,
                'sentiment_score': 0,
                'final_score': 0,
                'recommendation': 'ERROR',
                'confidence': 0
            }

    def score_batch(self, opportunities: list[Dict[str, Any]]) -> list[Dict[str, Any]]:
        """
        Score multiple opportunities and return sorted by final score

        Args:
            opportunities: List of opportunity dicts

        Returns:
            List of scored opportunities, sorted by final_score DESC
        """
        scored = [self.score_opportunity(opp) for opp in opportunities]
        return sorted(scored, key=lambda x: x['final_score'], reverse=True)


# Example usage
if __name__ == "__main__":
    # Test data
    test_opportunity = {
        'symbol': 'AAPL',
        'stock_price': 175.50,
        'strike_price': 165.00,
        'expiration_date': date(2025, 12, 19),
        'dte': 30,
        'premium': 285.0,
        'delta': -0.28,
        'monthly_return': 1.73,
        'annual_return': 20.76,
        'iv': 0.32,
        'bid': 2.80,
        'ask': 2.90,
        'volume': 1250,
        'oi': 3500,
        'breakeven': 162.15,
        'pe_ratio': 28.5,
        'eps': 6.15,
        'market_cap': 2_700_000_000_000,
        'sector': 'Technology',
        'dividend_yield': 0.52
    }

    scorer = MultiCriteriaScorer()
    result = scorer.score_opportunity(test_opportunity)

    print("\n=== AI Options Scoring Results ===")
    print(f"Symbol: {result['symbol']}")
    print(f"Fundamental Score: {result['fundamental_score']}/100")
    print(f"Technical Score: {result['technical_score']}/100")
    print(f"Greeks Score: {result['greeks_score']}/100")
    print(f"Risk Score: {result['risk_score']}/100")
    print(f"Sentiment Score: {result['sentiment_score']}/100")
    print(f"\nFinal Score: {result['final_score']}/100")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Confidence: {result['confidence']}%")
