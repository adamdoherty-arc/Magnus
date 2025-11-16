"""
Data Freshness Widget - Lightweight component for showing when data was last updated

Usage:
    from src.components.data_freshness_widget import show_data_freshness, DataFreshnessWidget

    # Simple inline display
    show_data_freshness(
        last_update=datetime.now(),
        cache_ttl=300,
        data_source="Yahoo Finance"
    )

    # Widget with more options
    widget = DataFreshnessWidget()
    widget.display(
        last_update=datetime.now(),
        cache_ttl=300,
        data_source="Yahoo Finance",
        show_warning=True
    )
"""

import streamlit as st
from datetime import datetime, timedelta
from typing import Optional


def show_data_freshness(
    last_update: Optional[datetime] = None,
    cache_ttl: Optional[int] = None,
    data_source: str = "Database",
    compact: bool = True
):
    """
    Simple inline display of data freshness

    Args:
        last_update: When data was last refreshed (defaults to now)
        cache_ttl: Cache TTL in seconds (e.g., 300 for 5 minutes)
        data_source: Where the data came from
        compact: Use compact single-line display
    """
    if last_update is None:
        last_update = datetime.now()

    # Format time
    time_str = last_update.strftime('%H:%M:%S')
    date_str = last_update.strftime('%Y-%m-%d')

    # Show date only if not today
    today = datetime.now().date()
    if last_update.date() != today:
        display_time = f"{date_str} {time_str}"
    else:
        display_time = time_str

    # Build freshness text
    if cache_ttl:
        cache_min = cache_ttl // 60
        cache_sec = cache_ttl % 60
        if cache_min > 0:
            cache_str = f"{cache_min}m"
        else:
            cache_str = f"{cache_sec}s"
        freshness = f"📊 Updated: {display_time} | 🔄 Cache: {cache_str} | 📡 {data_source}"
    else:
        freshness = f"📊 Updated: {display_time} | 📡 {data_source}"

    if compact:
        st.caption(freshness)
    else:
        st.info(freshness)


class DataFreshnessWidget:
    """
    Widget for displaying data freshness with warnings for stale data
    """

    def display(
        self,
        last_update: Optional[datetime] = None,
        cache_ttl: Optional[int] = None,
        data_source: str = "Database",
        show_warning: bool = True,
        warning_threshold: Optional[int] = None
    ):
        """
        Display data freshness with optional staleness warnings

        Args:
            last_update: When data was last refreshed
            cache_ttl: Cache TTL in seconds
            data_source: Data source name
            show_warning: Show warning if data is stale
            warning_threshold: Custom staleness threshold in seconds (defaults to 2x cache_ttl)
        """
        if last_update is None:
            last_update = datetime.now()

        # Calculate age
        age_seconds = (datetime.now() - last_update).total_seconds()

        # Determine staleness
        if warning_threshold is None and cache_ttl:
            warning_threshold = cache_ttl * 2

        is_stale = False
        if warning_threshold and age_seconds > warning_threshold:
            is_stale = True

        # Format display
        if age_seconds < 60:
            age_str = f"{int(age_seconds)}s ago"
        elif age_seconds < 3600:
            age_str = f"{int(age_seconds // 60)}m ago"
        elif age_seconds < 86400:
            age_str = f"{int(age_seconds // 3600)}h ago"
        else:
            age_str = f"{int(age_seconds // 86400)}d ago"

        # Create columns for layout
        col1, col2, col3 = st.columns([2, 2, 1])

        with col1:
            time_str = last_update.strftime('%H:%M:%S')
            date_str = last_update.strftime('%Y-%m-%d')
            today = datetime.now().date()

            if last_update.date() != today:
                st.caption(f"🕐 Last Update: {date_str} {time_str}")
            else:
                st.caption(f"🕐 Last Update: {time_str}")

        with col2:
            if cache_ttl:
                cache_min = cache_ttl // 60
                st.caption(f"🔄 Cache: {cache_min}min")
            else:
                st.caption(f"📊 Age: {age_str}")

        with col3:
            st.caption(f"📡 {data_source}")

        # Show warning if stale
        if show_warning and is_stale:
            threshold_min = warning_threshold // 60
            st.warning(f"⚠️ Data is stale ({age_str}). Expected refresh every {threshold_min}min. Consider refreshing manually.")

    def display_compact(
        self,
        last_update: Optional[datetime] = None,
        cache_ttl: Optional[int] = None,
        data_source: str = "DB"
    ):
        """
        Ultra-compact single-line display for tight layouts

        Args:
            last_update: When data was last refreshed
            cache_ttl: Cache TTL in seconds
            data_source: Data source abbreviation
        """
        show_data_freshness(
            last_update=last_update,
            cache_ttl=cache_ttl,
            data_source=data_source,
            compact=True
        )

    def get_freshness_status(
        self,
        last_update: datetime,
        cache_ttl: int
    ) -> dict:
        """
        Get freshness status as structured data

        Returns:
            dict with status, age_seconds, is_stale, color
        """
        age_seconds = (datetime.now() - last_update).total_seconds()

        # Determine status
        if age_seconds < cache_ttl:
            status = "fresh"
            color = "🟢"
        elif age_seconds < cache_ttl * 2:
            status = "aging"
            color = "🟡"
        else:
            status = "stale"
            color = "🔴"

        return {
            'status': status,
            'age_seconds': age_seconds,
            'is_stale': status == 'stale',
            'color': color,
            'last_update': last_update
        }


# Convenience function for quick inline use
def quick_timestamp(data_source: str = "Data", cache_minutes: int = 5):
    """
    Quick timestamp display - just shows current time with cache info

    Args:
        data_source: Name of data source
        cache_minutes: Cache duration in minutes
    """
    now = datetime.now()
    time_str = now.strftime('%H:%M:%S')
    st.caption(f"🕐 {time_str} | 🔄 {cache_minutes}m cache | 📡 {data_source}")
