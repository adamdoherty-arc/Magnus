"""
Base Filter Class
Abstract base class for all betting filters
"""

from abc import ABC, abstractmethod
from typing import Any
import pandas as pd


class BaseBettingFilter(ABC):
    """
    Base class for all betting filters.

    All filter implementations should inherit from this class and implement:
    - render(): Display the filter UI and return selected value(s)
    - apply(): Apply filter logic to a DataFrame
    """

    def __init__(self, label: str = None):
        """
        Initialize filter.

        Args:
            label: Display label for the filter
        """
        self.label = label

    @abstractmethod
    def render(self, key_prefix: str) -> Any:
        """
        Render the filter UI component.

        Args:
            key_prefix: Unique prefix for Streamlit widget keys

        Returns:
            Selected filter value(s)
        """
        pass

    @abstractmethod
    def apply(self, df: pd.DataFrame, value: Any) -> pd.DataFrame:
        """
        Apply filter to DataFrame.

        Args:
            df: Input DataFrame
            value: Filter value from render()

        Returns:
            Filtered DataFrame
        """
        pass

    def get_filter_name(self) -> str:
        """Get filter name (class name without 'Filter' suffix)"""
        return type(self).__name__.replace('Filter', '').lower()
