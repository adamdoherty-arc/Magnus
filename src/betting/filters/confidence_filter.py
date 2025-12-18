"""
Confidence Filter
Threshold filter for prediction confidence scores
"""

import streamlit as st
import pandas as pd
from src.betting.filters.base_filter import BaseBettingFilter


class ConfidenceFilter(BaseBettingFilter):
    """
    Filter for confidence/probability thresholds.

    Used to filter predictions by minimum confidence percentage.
    Consolidates confidence filtering from all sports betting pages.
    """

    def __init__(self,
                 label: str = "Min Confidence %",
                 min_val: int = 50,
                 max_val: int = 100,
                 default: int = 60,
                 step: int = 5,
                 help_text: str = None):
        """
        Initialize confidence filter.

        Args:
            label: Display label
            min_val: Minimum confidence value (default 50)
            max_val: Maximum confidence value (default 100)
            default: Default confidence value (default 60)
            step: Slider step size (default 5)
            help_text: Optional help text
        """
        super().__init__(label)
        self.min_val = min_val
        self.max_val = max_val
        self.default = default
        self.step = step
        self.help_text = help_text or "Filter by minimum prediction confidence"

    def render(self, key_prefix: str) -> int:
        """
        Render confidence slider.

        Args:
            key_prefix: Unique key prefix

        Returns:
            Selected minimum confidence threshold
        """
        return st.slider(
            self.label,
            min_value=self.min_val,
            max_value=self.max_val,
            value=self.default,
            step=self.step,
            key=f"{key_prefix}_confidence",
            help=self.help_text
        )

    def apply(self, df: pd.DataFrame, threshold: int) -> pd.DataFrame:
        """
        Apply confidence threshold filter.

        Args:
            df: Input DataFrame
            threshold: Minimum confidence threshold

        Returns:
            Filtered DataFrame with confidence >= threshold
        """
        # Try multiple common column names for confidence
        confidence_cols = ['confidence', 'probability', 'win_probability',
                          'confidence_score', 'score']

        for col in confidence_cols:
            if col in df.columns:
                # Handle percentage (0-100) or decimal (0-1) formats
                if df[col].max() <= 1.0:
                    # Decimal format (0-1), convert threshold
                    return df[df[col] >= (threshold / 100.0)]
                else:
                    # Percentage format (0-100)
                    return df[df[col] >= threshold]

        # If no confidence column found, return unfiltered
        return df
