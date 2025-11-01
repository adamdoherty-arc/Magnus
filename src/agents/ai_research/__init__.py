"""
AI Research Assistant Package
Multi-agent system for comprehensive stock analysis
"""

from .models import (
    ResearchReport,
    ResearchRequest,
    FundamentalAnalysis,
    TechnicalAnalysis,
    SentimentAnalysis,
    OptionsAnalysis,
    TradeRecommendation,
    Position,
    ErrorResponse
)

__version__ = "1.0.0"
__all__ = [
    "ResearchReport",
    "ResearchRequest",
    "FundamentalAnalysis",
    "TechnicalAnalysis",
    "SentimentAnalysis",
    "OptionsAnalysis",
    "TradeRecommendation",
    "Position",
    "ErrorResponse"
]
