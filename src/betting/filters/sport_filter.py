"""
Sport Filter
Filter for sport/league selection
"""

import streamlit as st
import pandas as pd
from src.betting.filters.base_filter import BaseBettingFilter


class SportFilter(BaseBettingFilter):
    """
    Filter for sport/league selection.

    Used to filter games by sport or league.
    Consolidates sport filtering from sports betting pages.
    """

    def __init__(self,
                 label: str = "Sport",
                 options: list = None,
                 help_text: str = None):
        """
        Initialize sport filter.

        Args:
            label: Display label
            options: List of sport options (default: ["All", "NFL", "NCAA Football", "NBA", "NCAA Basketball"])
            help_text: Optional help text
        """
        super().__init__(label)
        self.options = options or ["All", "NFL", "NCAA Football", "NBA", "NCAA Basketball"]
        self.help_text = help_text or "Filter by sport or league"

    def render(self, key_prefix: str) -> str:
        """
        Render sport filter.

        Args:
            key_prefix: Unique key prefix

        Returns:
            Selected sport option
        """
        return st.selectbox(
            self.label,
            options=self.options,
            key=f"{key_prefix}_sport",
            help=self.help_text
        )

    def apply(self, df: pd.DataFrame, value: str) -> pd.DataFrame:
        """
        Apply sport filter.

        Args:
            df: Input DataFrame
            value: Selected sport option

        Returns:
            Filtered DataFrame
        """
        if value == "All":
            return df

        # Try multiple common column names for sport/league
        sport_cols = ['sport', 'league', 'sport_type', 'league_name', 'category']

        sport_col = None
        for col in sport_cols:
            if col in df.columns:
                sport_col = col
                break

        if sport_col is None:
            return df  # No sport column found

        # Normalize sport values for comparison
        df_copy = df.copy()
        df_copy['_normalized_sport'] = df_copy[sport_col].astype(str).str.lower().str.strip()

        # Map filter value to possible sport representations
        sport_mappings = {
            "NFL": ["nfl", "national football league", "football", "american football"],
            "NCAA Football": ["ncaa", "ncaaf", "college football", "ncaa football", "cfb"],
            "NBA": ["nba", "national basketball association", "basketball", "pro basketball"],
            "NCAA Basketball": ["ncaab", "college basketball", "ncaa basketball", "cbb"],
            "MLB": ["mlb", "major league baseball", "baseball"],
            "NHL": ["nhl", "national hockey league", "hockey"],
            "Soccer": ["soccer", "football", "mls", "epl", "premier league"],
            "Tennis": ["tennis"],
            "Golf": ["golf", "pga"],
            "MMA": ["mma", "ufc", "mixed martial arts"],
        }

        # Get possible values for the selected sport
        possible_values = sport_mappings.get(value, [value.lower()])

        # Filter by sport
        mask = df_copy['_normalized_sport'].isin(possible_values)
        result = df_copy[mask].drop('_normalized_sport', axis=1)

        return result
