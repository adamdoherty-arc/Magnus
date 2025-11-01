"""
AI Research Assistant Package
Multi-agent system for comprehensive stock analysis

Production-ready specialist agents:
- FundamentalAgent: Financial metrics and valuation analysis (Alpha Vantage)
- TechnicalAgent: Price action and technical indicators (yfinance + pandas_ta)
- SentimentAgent: Market sentiment from Reddit and analysts (praw + yfinance)
- OptionsAgent: Options strategies and Greeks (yfinance + mibian)

Each agent provides async analyze() method returning structured data.
"""

# Import agents
from .fundamental_agent import FundamentalAgent
from .technical_agent import TechnicalAgent
from .sentiment_agent import SentimentAgent
from .options_agent import OptionsAgent

# Import orchestrator
from .orchestrator import ResearchOrchestrator

# Import data models
from .models import (
    ResearchReport,
    ResearchRequest,
    FundamentalAnalysis,
    TechnicalAnalysis,
    SentimentAnalysis,
    OptionsAnalysis,
    TradeRecommendation,
    Position,
    ErrorResponse,
    TrendDirection,
    SignalType,
    SentimentType,
    InstitutionalFlow,
    AnalystRating,
    TradeAction,
    InsiderTrade,
    AnalystConsensus,
    UnusualActivity,
    StrategyRecommendation,
    AnalysisMetadata
)

__version__ = "1.0.0"
__all__ = [
    # Specialist Agents
    "FundamentalAgent",
    "TechnicalAgent",
    "SentimentAgent",
    "OptionsAgent",
    
    # Orchestrator
    "ResearchOrchestrator",

    # Main Report Types
    "ResearchReport",
    "ResearchRequest",
    "FundamentalAnalysis",
    "TechnicalAnalysis",
    "SentimentAnalysis",
    "OptionsAnalysis",
    "TradeRecommendation",
    "Position",
    "ErrorResponse",

    # Enums
    "TrendDirection",
    "SignalType",
    "SentimentType",
    "InstitutionalFlow",
    "AnalystRating",
    "TradeAction",

    # Supporting Types
    "InsiderTrade",
    "AnalystConsensus",
    "UnusualActivity",
    "StrategyRecommendation",
    "AnalysisMetadata"
]
