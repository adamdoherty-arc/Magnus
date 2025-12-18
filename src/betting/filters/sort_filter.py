"""
Sort Filter
Filter for sorting options
"""

import streamlit as st
import pandas as pd
from src.betting.filters.base_filter import BaseBettingFilter


class SortFilter(BaseBettingFilter):
    """
    Filter for sorting options.

    Used to sort games/bets by various criteria.
    Consolidates sort functionality from sports betting pages.
    """

    def __init__(self,
                 label: str = "Sort By",
                 options: dict = None,
                 help_text: str = None):
        """
        Initialize sort filter.

        Args:
            label: Display label
            options: Dictionary mapping display names to (column, ascending) tuples
                    Default: {"Highest EV": ("ev", False), "Highest Confidence": ("confidence", False), ...}
            help_text: Optional help text
        """
        super().__init__(label)
        self.options = options or {
            "Highest EV": ("ev", False),
            "Highest Confidence": ("confidence", False),
            "Game Time": ("game_date", True),
            "Team Name": ("home_team", True),
        }
        self.help_text = help_text or "Sort betting opportunities"

    def render(self, key_prefix: str) -> str:
        """
        Render sort filter.

        Args:
            key_prefix: Unique key prefix

        Returns:
            Selected sort option display name
        """
        return st.selectbox(
            self.label,
            options=list(self.options.keys()),
            key=f"{key_prefix}_sort",
            help=self.help_text
        )

    def apply(self, df: pd.DataFrame, value: str) -> pd.DataFrame:
        """
        Apply sort to DataFrame.

        Args:
            df: Input DataFrame
            value: Selected sort option display name

        Returns:
            Sorted DataFrame
        """
        if value not in self.options:
            return df

        sort_col, ascending = self.options[value]

        # Try to find the column with various naming patterns
        column_mappings = {
            "ev": ["ev", "expected_value", "edge", "edge_percent", "value_score", "ev_percent"],
            "confidence": ["confidence", "probability", "win_probability", "confidence_score", "score"],
            "game_date": ["game_date", "date", "event_date", "game_time", "start_time", "datetime", "timestamp"],
            "home_team": ["home_team", "home", "team1", "team_name"],
            "away_team": ["away_team", "away", "team2", "opponent"],
        }

        actual_col = None
        possible_cols = column_mappings.get(sort_col, [sort_col])

        for col in possible_cols:
            if col in df.columns:
                actual_col = col
                break

        if actual_col is None:
            # Column not found, return unsorted
            return df

        try:
            # Sort the DataFrame
            return df.sort_values(by=actual_col, ascending=ascending)
        except Exception:
            # If sorting fails, return unsorted
            return df
