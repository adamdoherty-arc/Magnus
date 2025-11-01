"""
Fundamental Analyst Agent
Fetches financial data from Alpha Vantage and calculates valuation metrics
"""

import os
import asyncio
import aiohttp
from typing import Dict, List, Optional
from datetime import datetime, timedelta
from loguru import logger

from .models import FundamentalAnalysis


class FundamentalAgent:
    """
    Specialist agent for fundamental analysis using Alpha Vantage API.

    Features:
    - Fetches company overview, income statements, balance sheets
    - Calculates P/E, P/B, ROE, debt ratios
    - Compares to sector averages
    - Identifies key strengths and risks
    """

    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Fundamental Agent.

        Args:
            api_key: Alpha Vantage API key (defaults to ALPHA_VANTAGE_API_KEY env var)
        """
        self.api_key = api_key or os.getenv("ALPHA_VANTAGE_API_KEY")
        self.base_url = "https://www.alphavantage.co/query"
        self.timeout = aiohttp.ClientTimeout(total=30)

        # Cache for API responses (simple in-memory cache)
        self._cache: Dict[str, tuple] = {}  # key -> (data, timestamp)
        self.cache_ttl = timedelta(hours=6)  # Cache fundamental data for 6 hours

        logger.info("FundamentalAgent initialized")

    async def analyze(self, symbol: str) -> FundamentalAnalysis:
        """
        Perform comprehensive fundamental analysis on a stock.

        Args:
            symbol: Stock ticker symbol

        Returns:
            FundamentalAnalysis object with all metrics

        Raises:
            ValueError: If API key is missing or symbol is invalid
            RuntimeError: If API calls fail after retries
        """
        if not self.api_key:
            logger.error("Alpha Vantage API key not configured")
            raise ValueError("ALPHA_VANTAGE_API_KEY environment variable must be set")

        symbol = symbol.upper().strip()
        logger.info(f"Starting fundamental analysis for {symbol}")

        try:
            # Fetch all required data in parallel
            overview, income_stmt, balance_sheet = await asyncio.gather(
                self._get_company_overview(symbol),
                self._get_income_statement(symbol),
                self._get_balance_sheet(symbol),
                return_exceptions=True
            )

            # Handle errors with fallbacks
            if isinstance(overview, Exception):
                logger.warning(f"Company overview failed: {overview}")
                overview = {}

            if isinstance(income_stmt, Exception):
                logger.warning(f"Income statement failed: {income_stmt}")
                income_stmt = {}

            if isinstance(balance_sheet, Exception):
                logger.warning(f"Balance sheet failed: {balance_sheet}")
                balance_sheet = {}

            # Calculate metrics
            analysis = self._calculate_metrics(symbol, overview, income_stmt, balance_sheet)

            logger.info(f"Fundamental analysis completed for {symbol} with score {analysis.score}")
            return analysis

        except Exception as e:
            logger.error(f"Fundamental analysis failed for {symbol}: {e}")
            # Return fallback analysis
            return self._create_fallback_analysis(symbol)

    async def _get_company_overview(self, symbol: str) -> dict:
        """Fetch company overview data from Alpha Vantage."""
        cache_key = f"overview_{symbol}"

        # Check cache
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.debug(f"Using cached overview for {symbol}")
                return data

        params = {
            "function": "OVERVIEW",
            "symbol": symbol,
            "apikey": self.api_key
        }

        data = await self._make_request(params)

        # Validate response
        if not data or "Symbol" not in data:
            raise ValueError(f"Invalid response for {symbol}: missing Symbol field")

        # Cache the result
        self._cache[cache_key] = (data, datetime.now())

        return data

    async def _get_income_statement(self, symbol: str) -> dict:
        """Fetch income statement data from Alpha Vantage."""
        cache_key = f"income_{symbol}"

        # Check cache
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.debug(f"Using cached income statement for {symbol}")
                return data

        params = {
            "function": "INCOME_STATEMENT",
            "symbol": symbol,
            "apikey": self.api_key
        }

        data = await self._make_request(params)

        # Cache the result
        self._cache[cache_key] = (data, datetime.now())

        return data

    async def _get_balance_sheet(self, symbol: str) -> dict:
        """Fetch balance sheet data from Alpha Vantage."""
        cache_key = f"balance_{symbol}"

        # Check cache
        if cache_key in self._cache:
            data, timestamp = self._cache[cache_key]
            if datetime.now() - timestamp < self.cache_ttl:
                logger.debug(f"Using cached balance sheet for {symbol}")
                return data

        params = {
            "function": "BALANCE_SHEET",
            "symbol": symbol,
            "apikey": self.api_key
        }

        data = await self._make_request(params)

        # Cache the result
        self._cache[cache_key] = (data, datetime.now())

        return data

    async def _make_request(self, params: dict, retries: int = 3) -> dict:
        """
        Make HTTP request to Alpha Vantage API with retry logic.

        Args:
            params: Query parameters
            retries: Number of retry attempts

        Returns:
            JSON response as dictionary
        """
        for attempt in range(retries):
            try:
                async with aiohttp.ClientSession(timeout=self.timeout) as session:
                    async with session.get(self.base_url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()

                            # Check for API error messages
                            if "Error Message" in data:
                                raise ValueError(f"API error: {data['Error Message']}")

                            if "Note" in data:
                                # Rate limit hit
                                logger.warning(f"Alpha Vantage rate limit: {data['Note']}")
                                if attempt < retries - 1:
                                    await asyncio.sleep(12)  # Wait before retry
                                    continue
                                else:
                                    raise RuntimeError("Rate limit exceeded")

                            return data
                        else:
                            logger.warning(f"HTTP {response.status} on attempt {attempt + 1}/{retries}")
                            if attempt < retries - 1:
                                await asyncio.sleep(2 ** attempt)  # Exponential backoff

            except asyncio.TimeoutError:
                logger.warning(f"Timeout on attempt {attempt + 1}/{retries}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)

            except Exception as e:
                logger.error(f"Request failed on attempt {attempt + 1}/{retries}: {e}")
                if attempt < retries - 1:
                    await asyncio.sleep(2 ** attempt)
                else:
                    raise

        raise RuntimeError("All retry attempts failed")

    def _calculate_metrics(
        self,
        symbol: str,
        overview: dict,
        income_stmt: dict,
        balance_sheet: dict
    ) -> FundamentalAnalysis:
        """
        Calculate all fundamental metrics and generate analysis.

        Args:
            symbol: Stock ticker
            overview: Company overview data
            income_stmt: Income statement data
            balance_sheet: Balance sheet data

        Returns:
            FundamentalAnalysis object
        """
        try:
            # Extract key metrics with fallbacks
            pe_ratio = self._safe_float(overview.get("PERatio"), 0.0)
            pb_ratio = self._safe_float(overview.get("PriceToBookRatio"), 0.0)
            debt_to_equity = self._safe_float(overview.get("DebtToEquity"), 0.0)
            roe = self._safe_float(overview.get("ReturnOnEquityTTM"), 0.0)
            dividend_yield = self._safe_float(overview.get("DividendYield"), 0.0)

            # Earnings data
            earnings_beat_streak = 0  # Would need historical earnings data
            eps_growth = self._safe_float(overview.get("QuarterlyEarningsGrowthYOY"), 0.0)

            # Revenue growth
            revenue_growth = self._safe_float(overview.get("QuarterlyRevenueGrowthYOY"), 0.0)

            # Sector average (Alpha Vantage doesn't provide this directly, use industry heuristics)
            sector = overview.get("Sector", "Unknown")
            sector_avg_pe = self._get_sector_avg_pe(sector)

            # Free cash flow calculation
            free_cash_flow = 0.0
            if income_stmt and "annualReports" in income_stmt and income_stmt["annualReports"]:
                latest_report = income_stmt["annualReports"][0]
                operating_cash_flow = self._safe_float(
                    latest_report.get("operatingCashflow"), 0.0
                )
                capital_expenditures = self._safe_float(
                    latest_report.get("capitalExpenditures"), 0.0
                )
                free_cash_flow = operating_cash_flow - capital_expenditures

            # Valuation assessment
            valuation = self._assess_valuation(pe_ratio, pb_ratio, sector_avg_pe)

            # Key strengths and risks
            strengths = self._identify_strengths(
                revenue_growth, roe, dividend_yield, debt_to_equity
            )
            risks = self._identify_risks(
                pe_ratio, sector_avg_pe, debt_to_equity, revenue_growth
            )

            # Calculate overall score (0-100)
            score = self._calculate_score(
                pe_ratio, sector_avg_pe, pb_ratio, roe,
                revenue_growth, debt_to_equity, free_cash_flow
            )

            # Next earnings date
            next_earnings = None
            if "LatestQuarter" in overview:
                next_earnings = self._estimate_next_earnings(overview["LatestQuarter"])

            # Analyst estimates (if available)
            analyst_estimates = {
                "eps": self._safe_float(overview.get("AnalystTargetPrice"), 0.0),
                "revenue": 0.0  # Not available in overview
            }

            return FundamentalAnalysis(
                score=score,
                revenue_growth_yoy=revenue_growth,
                earnings_beat_streak=earnings_beat_streak,
                pe_ratio=pe_ratio,
                sector_avg_pe=sector_avg_pe,
                pb_ratio=pb_ratio,
                debt_to_equity=debt_to_equity,
                roe=roe,
                free_cash_flow=free_cash_flow,
                dividend_yield=dividend_yield,
                valuation_assessment=valuation,
                key_strengths=strengths,
                key_risks=risks,
                next_earnings_date=next_earnings,
                analyst_estimates=analyst_estimates
            )

        except Exception as e:
            logger.error(f"Error calculating metrics for {symbol}: {e}")
            return self._create_fallback_analysis(symbol)

    def _safe_float(self, value, default: float = 0.0) -> float:
        """Safely convert value to float with fallback."""
        if value is None or value == "None":
            return default
        try:
            return float(value)
        except (ValueError, TypeError):
            return default

    def _get_sector_avg_pe(self, sector: str) -> float:
        """Get average P/E ratio for sector (industry benchmarks)."""
        sector_pe_map = {
            "Technology": 30.0,
            "Healthcare": 25.0,
            "Financial Services": 15.0,
            "Consumer Cyclical": 20.0,
            "Consumer Defensive": 22.0,
            "Industrials": 20.0,
            "Energy": 15.0,
            "Utilities": 18.0,
            "Real Estate": 35.0,
            "Basic Materials": 18.0,
            "Communication Services": 20.0,
        }
        return sector_pe_map.get(sector, 20.0)

    def _assess_valuation(self, pe: float, pb: float, sector_avg_pe: float) -> str:
        """Assess whether stock is overvalued, undervalued, or fairly valued."""
        if pe <= 0 or sector_avg_pe <= 0:
            return "Unable to assess valuation (negative or zero P/E)"

        pe_discount = (sector_avg_pe - pe) / sector_avg_pe

        if pe_discount > 0.20:
            return "Undervalued - Trading below sector average"
        elif pe_discount < -0.20:
            return "Overvalued - Trading above sector average"
        else:
            return "Fairly valued - In line with sector"

    def _identify_strengths(
        self,
        revenue_growth: float,
        roe: float,
        dividend_yield: float,
        debt_to_equity: float
    ) -> List[str]:
        """Identify key fundamental strengths."""
        strengths = []

        if revenue_growth > 0.15:
            strengths.append(f"Strong revenue growth: {revenue_growth*100:.1f}% YoY")

        if roe > 0.15:
            strengths.append(f"High return on equity: {roe*100:.1f}%")

        if dividend_yield > 0.02:
            strengths.append(f"Attractive dividend yield: {dividend_yield*100:.2f}%")

        if debt_to_equity < 0.5:
            strengths.append("Low debt levels - strong balance sheet")

        if not strengths:
            strengths.append("Maintaining stable operations")

        return strengths

    def _identify_risks(
        self,
        pe: float,
        sector_avg_pe: float,
        debt_to_equity: float,
        revenue_growth: float
    ) -> List[str]:
        """Identify key fundamental risks."""
        risks = []

        if pe > sector_avg_pe * 1.5:
            risks.append(f"High valuation risk: P/E 50% above sector average")

        if debt_to_equity > 1.5:
            risks.append(f"High debt burden: D/E ratio of {debt_to_equity:.2f}")

        if revenue_growth < 0:
            risks.append(f"Declining revenue: {revenue_growth*100:.1f}% YoY")

        if not risks:
            risks.append("No major fundamental red flags identified")

        return risks

    def _calculate_score(
        self,
        pe: float,
        sector_avg_pe: float,
        pb: float,
        roe: float,
        revenue_growth: float,
        debt_to_equity: float,
        fcf: float
    ) -> int:
        """
        Calculate overall fundamental score (0-100).

        Scoring methodology:
        - Valuation (30 points): P/E vs sector, P/B ratio
        - Profitability (25 points): ROE
        - Growth (25 points): Revenue growth
        - Financial health (20 points): Debt levels, FCF
        """
        score = 0

        # Valuation score (30 points)
        if pe > 0 and sector_avg_pe > 0:
            pe_ratio = pe / sector_avg_pe
            if pe_ratio < 0.8:
                score += 30  # Significantly undervalued
            elif pe_ratio < 1.0:
                score += 25  # Moderately undervalued
            elif pe_ratio < 1.2:
                score += 20  # Fairly valued
            elif pe_ratio < 1.5:
                score += 10  # Moderately overvalued
            else:
                score += 0   # Significantly overvalued
        else:
            score += 15  # Neutral if can't calculate

        # Profitability score (25 points)
        if roe > 0.20:
            score += 25
        elif roe > 0.15:
            score += 20
        elif roe > 0.10:
            score += 15
        elif roe > 0.05:
            score += 10
        else:
            score += 5

        # Growth score (25 points)
        if revenue_growth > 0.20:
            score += 25
        elif revenue_growth > 0.10:
            score += 20
        elif revenue_growth > 0.05:
            score += 15
        elif revenue_growth > 0:
            score += 10
        else:
            score += 0

        # Financial health (20 points)
        health_score = 0
        if debt_to_equity < 0.5:
            health_score += 10
        elif debt_to_equity < 1.0:
            health_score += 7
        elif debt_to_equity < 1.5:
            health_score += 4

        if fcf > 0:
            health_score += 10
        elif fcf > -1000000000:  # -$1B
            health_score += 5

        score += health_score

        return min(score, 100)

    def _estimate_next_earnings(self, latest_quarter: str) -> str:
        """Estimate next earnings date based on quarterly pattern."""
        try:
            latest = datetime.strptime(latest_quarter, "%Y-%m-%d")
            # Add approximately 90 days for next quarter
            next_earnings = latest + timedelta(days=90)
            return next_earnings.strftime("%Y-%m-%d")
        except Exception:
            return "Unknown"

    def _create_fallback_analysis(self, symbol: str) -> FundamentalAnalysis:
        """Create fallback analysis when API fails."""
        logger.warning(f"Creating fallback fundamental analysis for {symbol}")

        return FundamentalAnalysis(
            score=50,  # Neutral score
            revenue_growth_yoy=0.0,
            earnings_beat_streak=0,
            pe_ratio=0.0,
            sector_avg_pe=20.0,
            pb_ratio=0.0,
            debt_to_equity=0.0,
            roe=0.0,
            free_cash_flow=0.0,
            dividend_yield=0.0,
            valuation_assessment="Data unavailable",
            key_strengths=["Unable to fetch fundamental data"],
            key_risks=["API data unavailable - use caution"],
            next_earnings_date=None,
            analyst_estimates=None
        )
