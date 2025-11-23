"""
Economic Indicators Module
Fetches and analyzes economic indicators for sector analysis
"""

import os
import requests
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import logging
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class EconomicIndicatorsManager:
    """
    Manages economic indicators: PMI, GDP, unemployment, interest rates
    Uses FRED API (Federal Reserve Economic Data)
    """

    def __init__(self, fred_api_key: Optional[str] = None):
        """
        Initialize Economic Indicators Manager

        Args:
            fred_api_key: FRED API key (optional - will auto-load from .env if not provided)
        """
        # Auto-load from environment if not provided
        self.fred_api_key = fred_api_key or os.getenv('FRED_API_KEY')
        self.base_url = "https://api.stlouisfed.org/fred/series/observations"

        if self.fred_api_key:
            logger.info("FRED API key loaded successfully - will use live economic data")
        else:
            logger.warning("No FRED API key found - will use mock data")

        # FRED Series IDs for key indicators
        self.series_ids = {
            'pmi': 'MANEMP',  # ISM Manufacturing PMI
            'gdp': 'GDP',  # Gross Domestic Product
            'unemployment': 'UNRATE',  # Unemployment Rate
            'fed_funds': 'FEDFUNDS',  # Federal Funds Rate
            'cpi': 'CPIAUCSL',  # Consumer Price Index
            'retail_sales': 'RSXFS',  # Retail Sales
            'industrial_production': 'INDPRO',  # Industrial Production Index
            'housing_starts': 'HOUST',  # Housing Starts
            'consumer_confidence': 'UMCSENT',  # University of Michigan Consumer Sentiment
        }

        # Economic cycle thresholds
        self.pmi_expansion_threshold = 50.0
        self.pmi_strong_expansion = 55.0
        self.pmi_recession = 42.3
        self.gdp_recession = 0.0
        self.unemployment_full_employment = 4.0

    def fetch_fred_data(
        self,
        series_id: str,
        limit: int = 12
    ) -> Optional[pd.DataFrame]:
        """
        Fetch data from FRED API

        Args:
            series_id: FRED series ID
            limit: Number of observations to fetch

        Returns:
            DataFrame with date and value columns
        """
        if not self.fred_api_key:
            logger.warning("No FRED API key provided. Using mock data.")
            return self._get_mock_data(series_id)

        try:
            params = {
                'series_id': series_id,
                'api_key': self.fred_api_key,
                'file_type': 'json',
                'sort_order': 'desc',
                'limit': limit
            }

            response = requests.get(self.base_url, params=params, timeout=10)
            response.raise_for_status()

            data = response.json()
            if 'observations' not in data:
                return None

            observations = data['observations']
            df = pd.DataFrame(observations)

            # Convert date and value
            df['date'] = pd.to_datetime(df['date'])
            df['value'] = pd.to_numeric(df['value'], errors='coerce')

            # Filter out missing values
            df = df.dropna(subset=['value'])

            # Sort by date ascending
            df = df.sort_values('date')

            return df[['date', 'value']]

        except Exception as e:
            logger.error(f"Error fetching FRED data for {series_id}: {e}")
            return self._get_mock_data(series_id)

    def _get_mock_data(self, series_id: str) -> pd.DataFrame:
        """
        Generate mock economic data for testing

        Args:
            series_id: Series identifier

        Returns:
            Mock DataFrame
        """
        # Generate dates for last 12 months
        dates = pd.date_range(end=datetime.now(), periods=12, freq='MS')

        # Mock values based on series type
        if 'pmi' in series_id.lower() or series_id == 'MANEMP':
            # PMI oscillates around 50
            values = np.random.normal(52, 3, 12)
        elif 'gdp' in series_id.lower():
            # GDP grows at ~2-3% annually
            values = np.linspace(20000, 21000, 12)  # Billions
        elif 'unemployment' in series_id.lower() or series_id == 'UNRATE':
            # Unemployment around 4%
            values = np.random.normal(4.0, 0.5, 12)
        elif 'fed' in series_id.lower() or series_id == 'FEDFUNDS':
            # Fed funds rate around 4.5%
            values = np.random.normal(4.5, 0.3, 12)
        elif 'cpi' in series_id.lower():
            # CPI increasing
            values = np.linspace(300, 310, 12)
        else:
            # Generic increasing trend
            values = np.linspace(100, 105, 12)

        return pd.DataFrame({
            'date': dates,
            'value': values
        })

    def get_latest_pmi(self) -> Dict[str, any]:
        """
        Get latest Manufacturing PMI

        Returns:
            Dictionary with PMI value, date, and interpretation
        """
        data = self.fetch_fred_data(self.series_ids['pmi'], limit=2)

        if data is None or data.empty:
            return {
                'value': 52.0,
                'date': datetime.now(),
                'interpretation': 'Expansion (Mock Data)',
                'trend': 'Neutral'
            }

        latest = data.iloc[-1]
        pmi_value = float(latest['value'])

        # Interpretation
        if pmi_value > self.pmi_strong_expansion:
            interpretation = "Strong Expansion"
        elif pmi_value > self.pmi_expansion_threshold:
            interpretation = "Expansion"
        elif pmi_value > self.pmi_recession:
            interpretation = "Contraction"
        else:
            interpretation = "Recession Signal"

        # Trend (compare to previous month)
        if len(data) >= 2:
            prev_pmi = float(data.iloc[-2]['value'])
            trend = "Improving" if pmi_value > prev_pmi else "Declining"
        else:
            trend = "Neutral"

        return {
            'value': round(pmi_value, 1),
            'date': latest['date'],
            'interpretation': interpretation,
            'trend': trend
        }

    def get_latest_gdp_growth(self) -> Dict[str, any]:
        """
        Get latest GDP growth rate

        Returns:
            Dictionary with GDP growth, date, and interpretation
        """
        data = self.fetch_fred_data(self.series_ids['gdp'], limit=5)

        if data is None or data.empty:
            return {
                'value': 2.5,
                'date': datetime.now(),
                'interpretation': 'Moderate Growth (Mock Data)',
                'annual_rate': 2.5
            }

        # Calculate year-over-year growth
        if len(data) >= 5:
            latest_gdp = float(data.iloc[-1]['value'])
            year_ago_gdp = float(data.iloc[-5]['value'])
            yoy_growth = ((latest_gdp - year_ago_gdp) / year_ago_gdp) * 100
        else:
            yoy_growth = 2.5  # Default

        # Interpretation
        if yoy_growth > 3.0:
            interpretation = "Strong Growth"
        elif yoy_growth > 2.0:
            interpretation = "Moderate Growth"
        elif yoy_growth > 0:
            interpretation = "Slow Growth"
        else:
            interpretation = "Recession"

        return {
            'value': round(yoy_growth, 1),
            'date': data.iloc[-1]['date'],
            'interpretation': interpretation,
            'annual_rate': round(yoy_growth, 1)
        }

    def get_latest_unemployment(self) -> Dict[str, any]:
        """
        Get latest unemployment rate

        Returns:
            Dictionary with unemployment rate and interpretation
        """
        data = self.fetch_fred_data(self.series_ids['unemployment'], limit=2)

        if data is None or data.empty:
            return {
                'value': 4.0,
                'date': datetime.now(),
                'interpretation': 'Full Employment (Mock Data)',
                'trend': 'Neutral'
            }

        latest = data.iloc[-1]
        unemployment = float(latest['value'])

        # Interpretation
        if unemployment < self.unemployment_full_employment:
            interpretation = "Full Employment"
        elif unemployment < 5.0:
            interpretation = "Healthy"
        elif unemployment < 6.0:
            interpretation = "Elevated"
        else:
            interpretation = "High Unemployment"

        # Trend
        if len(data) >= 2:
            prev_unemployment = float(data.iloc[-2]['value'])
            if unemployment < prev_unemployment:
                trend = "Improving"
            elif unemployment > prev_unemployment:
                trend = "Worsening"
            else:
                trend = "Stable"
        else:
            trend = "Stable"

        return {
            'value': round(unemployment, 1),
            'date': latest['date'],
            'interpretation': interpretation,
            'trend': trend
        }

    def get_latest_fed_funds_rate(self) -> Dict[str, any]:
        """
        Get latest Federal Funds Rate

        Returns:
            Dictionary with rate and interpretation
        """
        data = self.fetch_fred_data(self.series_ids['fed_funds'], limit=2)

        if data is None or data.empty:
            return {
                'value': 4.5,
                'date': datetime.now(),
                'interpretation': 'Restrictive (Mock Data)',
                'trend': 'Neutral'
            }

        latest = data.iloc[-1]
        rate = float(latest['value'])

        # Interpretation
        if rate > 5.0:
            interpretation = "Restrictive (Tightening)"
        elif rate > 3.0:
            interpretation = "Neutral to Restrictive"
        elif rate > 1.0:
            interpretation = "Accommodative"
        else:
            interpretation = "Very Accommodative (Easing)"

        # Trend
        if len(data) >= 2:
            prev_rate = float(data.iloc[-2]['value'])
            if rate > prev_rate:
                trend = "Rising (Hawkish)"
            elif rate < prev_rate:
                trend = "Falling (Dovish)"
            else:
                trend = "Unchanged"
        else:
            trend = "Unchanged"

        return {
            'value': round(rate, 2),
            'date': latest['date'],
            'interpretation': interpretation,
            'trend': trend
        }

    def get_economic_snapshot(self) -> Dict[str, any]:
        """
        Get comprehensive economic snapshot

        Returns:
            Dictionary with all key indicators
        """
        pmi = self.get_latest_pmi()
        gdp = self.get_latest_gdp_growth()
        unemployment = self.get_latest_unemployment()
        fed_funds = self.get_latest_fed_funds_rate()

        # Determine overall economic cycle
        pmi_value = pmi['value']
        gdp_value = gdp['value']

        if pmi_value > self.pmi_strong_expansion and gdp_value > 3.0:
            cycle = "Early Expansion"
            cycle_color = "🟢"
        elif pmi_value > self.pmi_expansion_threshold and gdp_value > 2.0:
            cycle = "Mid Expansion"
            cycle_color = "🟢"
        elif pmi_value < self.pmi_expansion_threshold and gdp_value < 2.0:
            cycle = "Late Cycle / Slowdown"
            cycle_color = "🟡"
        else:
            cycle = "Recession Risk"
            cycle_color = "🔴"

        return {
            'cycle': cycle,
            'cycle_color': cycle_color,
            'pmi': pmi,
            'gdp': gdp,
            'unemployment': unemployment,
            'fed_funds': fed_funds,
            'updated': datetime.now()
        }

    def get_sector_recommendations_from_economy(
        self,
        snapshot: Optional[Dict] = None
    ) -> Dict[str, List[str]]:
        """
        Generate sector recommendations based on economic conditions

        Args:
            snapshot: Economic snapshot (if None, will fetch fresh)

        Returns:
            Dictionary with overweight/underweight sectors
        """
        if snapshot is None:
            snapshot = self.get_economic_snapshot()

        cycle = snapshot['cycle']
        pmi_value = snapshot['pmi']['value']
        fed_funds_value = snapshot['fed_funds']['value']

        # Base recommendations on cycle
        if cycle == "Early Expansion":
            overweight = ['Industrials', 'Materials', 'Information Technology']
            underweight = ['Utilities', 'Consumer Staples']

        elif cycle == "Mid Expansion":
            overweight = ['Information Technology', 'Consumer Discretionary', 'Industrials']
            underweight = ['Utilities', 'Real Estate']

        elif "Late Cycle" in cycle or "Slowdown" in cycle:
            overweight = ['Energy', 'Financials', 'Consumer Staples']
            underweight = ['Industrials', 'Materials']

        else:  # Recession Risk
            overweight = ['Utilities', 'Consumer Staples', 'Health Care']
            underweight = ['Consumer Discretionary', 'Industrials', 'Materials']

        # Adjust for interest rates
        if fed_funds_value > 4.5:  # High rates
            if 'Financials' not in overweight:
                overweight.append('Financials')
            if 'Real Estate' not in underweight:
                underweight.append('Real Estate')
        elif fed_funds_value < 2.0:  # Low rates
            if 'Real Estate' not in overweight:
                overweight.append('Real Estate')
            if 'Utilities' not in overweight:
                overweight.append('Utilities')

        return {
            'cycle': cycle,
            'overweight': list(set(overweight)),  # Remove duplicates
            'underweight': list(set(underweight)),
            'pmi': pmi_value,
            'fed_funds': fed_funds_value
        }

    def plot_economic_timeline(self) -> pd.DataFrame:
        """
        Get economic indicators time series for plotting

        Returns:
            DataFrame with all indicators over time
        """
        # Fetch data for each indicator
        pmi_data = self.fetch_fred_data(self.series_ids['pmi'], limit=24)
        gdp_data = self.fetch_fred_data(self.series_ids['gdp'], limit=24)
        unemployment_data = self.fetch_fred_data(self.series_ids['unemployment'], limit=24)
        fed_funds_data = self.fetch_fred_data(self.series_ids['fed_funds'], limit=24)

        # Merge on date
        timeline = pmi_data.rename(columns={'value': 'PMI'})

        if gdp_data is not None:
            timeline = timeline.merge(
                gdp_data.rename(columns={'value': 'GDP'}),
                on='date',
                how='outer'
            )

        if unemployment_data is not None:
            timeline = timeline.merge(
                unemployment_data.rename(columns={'value': 'Unemployment'}),
                on='date',
                how='outer'
            )

        if fed_funds_data is not None:
            timeline = timeline.merge(
                fed_funds_data.rename(columns={'value': 'Fed_Funds_Rate'}),
                on='date',
                how='outer'
            )

        # Sort by date
        timeline = timeline.sort_values('date')

        return timeline
