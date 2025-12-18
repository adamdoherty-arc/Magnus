"""
Game Status Filter
Filter for game/event status (live, upcoming, final, etc.)
"""

import streamlit as st
import pandas as pd
from src.betting.filters.base_filter import BaseBettingFilter


class GameStatusFilter(BaseBettingFilter):
    """
    Filter for game/event status.

    Used to filter games by their current status.
    Consolidates status filtering from sports betting pages.
    """

    def __init__(self,
                 label: str = "Game Status",
                 options: list = None,
                 help_text: str = None):
        """
        Initialize game status filter.

        Args:
            label: Display label
            options: List of status options (default: ["All Games", "Live Only", "Upcoming", "Final"])
            help_text: Optional help text
        """
        super().__init__(label)
        self.options = options or ["All Games", "Live Only", "Upcoming", "Final"]
        self.help_text = help_text or "Filter by game status"

    def render(self, key_prefix: str) -> str:
        """
        Render game status filter.

        Args:
            key_prefix: Unique key prefix

        Returns:
            Selected status option
        """
        return st.selectbox(
            self.label,
            options=self.options,
            key=f"{key_prefix}_status",
            help=self.help_text
        )

    def apply(self, df: pd.DataFrame, value: str) -> pd.DataFrame:
        """
        Apply game status filter.

        Args:
            df: Input DataFrame
            value: Selected status option

        Returns:
            Filtered DataFrame
        """
        if value == "All Games" or value == "All":
            return df

        # Try multiple common column names for status
        status_cols = ['status', 'game_status', 'event_status', 'state']

        status_col = None
        for col in status_cols:
            if col in df.columns:
                status_col = col
                break

        if status_col is None:
            return df  # No status column found

        # Normalize status values for comparison
        df_copy = df.copy()
        df_copy['_normalized_status'] = df_copy[status_col].astype(str).str.lower().str.strip()

        if value == "Live Only":
            # Match various live status representations
            live_patterns = ['live', 'in progress', 'active', 'playing', 'in_progress']
            mask = df_copy['_normalized_status'].isin(live_patterns)
            result = df_copy[mask].drop('_normalized_status', axis=1)
        elif value == "Upcoming":
            # Match various upcoming status representations
            upcoming_patterns = ['upcoming', 'scheduled', 'pending', 'not started',
                               'not_started', 'pre-game', 'pregame']
            mask = df_copy['_normalized_status'].isin(upcoming_patterns)
            result = df_copy[mask].drop('_normalized_status', axis=1)
        elif value == "Final":
            # Match various final status representations
            final_patterns = ['final', 'completed', 'finished', 'ended', 'complete']
            mask = df_copy['_normalized_status'].isin(final_patterns)
            result = df_copy[mask].drop('_normalized_status', axis=1)
        else:
            result = df_copy.drop('_normalized_status', axis=1)

        return result
