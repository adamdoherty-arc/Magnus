"""
Expected Value (EV) Filter
Filter for expected value / edge percentage
"""

import streamlit as st
import pandas as pd
from src.betting.filters.base_filter import BaseBettingFilter


class ExpectedValueFilter(BaseBettingFilter):
    """
    Filter for Expected Value (EV) / Edge percentage.

    Used to filter betting opportunities by minimum expected value.
    Consolidates EV filtering from sports betting pages.
    """

    def __init__(self,
                 label: str = "Min Expected Value %",
                 min_val: float = 0.0,
                 max_val: float = 20.0,
                 default: float = 3.0,
                 step: float = 0.5,
                 help_text: str = None):
        """
        Initialize EV filter.

        Args:
            label: Display label
            min_val: Minimum EV value (default 0.0)
            max_val: Maximum EV value (default 20.0)
            default: Default EV value (default 3.0)
            step: Slider step size (default 0.5)
            help_text: Optional help text
        """
        super().__init__(label)
        self.min_val = min_val
        self.max_val = max_val
        self.default = default
        self.step = step
        self.help_text = help_text or "Filter by minimum expected value (edge)"

    def render(self, key_prefix: str) -> float:
        """
        Render EV slider.

        Args:
            key_prefix: Unique key prefix

        Returns:
            Selected minimum EV threshold
        """
        return st.slider(
            self.label,
            min_value=self.min_val,
            max_value=self.max_val,
            value=self.default,
            step=self.step,
            key=f"{key_prefix}_ev",
            help=self.help_text
        )

    def apply(self, df: pd.DataFrame, threshold: float) -> pd.DataFrame:
        """
        Apply EV threshold filter.

        Args:
            df: Input DataFrame
            threshold: Minimum EV threshold

        Returns:
            Filtered DataFrame with EV >= threshold
        """
        # Try multiple common column names for EV
        ev_cols = ['ev', 'expected_value', 'edge', 'edge_percent',
                   'value_score', 'ev_percent']

        for col in ev_cols:
            if col in df.columns:
                return df[df[col] >= threshold]

        # If no EV column found, return unfiltered
        return df
