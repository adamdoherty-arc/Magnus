"""
Shared Display Helper Functions
Provides common UI components and formatting
"""

import streamlit as st


def display_score_gauge(score: int, label: str):
    """Display a score as a colored gauge"""
    if score >= 80:
        color = "🟢"
    elif score >= 60:
        color = "🟡"
    else:
        color = "🔴"

    st.metric(label, f"{score}/100 {color}")


def display_recommendation_badge(recommendation: str) -> str:
    """Display recommendation with color coding"""
    colors = {
        'STRONG_BUY': '🟢',
        'BUY': '🟢',
        'HOLD': '🟡',
        'CAUTION': '🟠',
        'AVOID': '🔴'
    }

    color = colors.get(recommendation, '⚪')
    return f"{color} {recommendation}"


def format_currency(value: float) -> str:
    """Format value as currency"""
    return f"${value:,.2f}"


def format_percentage(value: float) -> str:
    """Format value as percentage"""
    return f"{value:.2f}%"


def format_market_cap(value: int) -> str:
    """Format market cap in billions"""
    return f"${value/1e9:.1f}B"
