"""
AVA Unified Agents Package
All specialized agents for the Magnus/AVA system
"""

# Trading Agents
from .trading.market_data_agent import MarketDataAgent
from .trading.options_analysis_agent import OptionsAnalysisAgent
from .trading.strategy_agent import StrategyAgent
from .trading.risk_management_agent import RiskManagementAgent
from .trading.portfolio_agent import PortfolioAgent
from .trading.earnings_agent import EarningsAgent
from .trading.premium_scanner_agent import PremiumScannerAgent

# Analysis Agents
from .analysis.fundamental_agent import FundamentalAnalysisAgent
from .analysis.technical_agent import TechnicalAnalysisAgent
from .analysis.sentiment_agent import SentimentAnalysisAgent
from .analysis.supply_demand_agent import SupplyDemandAgent
from .analysis.sector_agent import SectorAnalysisAgent
from .analysis.options_flow_agent import OptionsFlowAgent

# Sports Betting Agents
from .sports.kalshi_markets_agent import KalshiMarketsAgent
from .sports.sports_betting_agent import SportsBettingAgent
from .sports.nfl_markets_agent import NFLMarketsAgent
from .sports.game_analysis_agent import GameAnalysisAgent
from .sports.odds_comparison_agent import OddsComparisonAgent
from .sports.betting_strategy_agent import BettingStrategyAgent

# Monitoring Agents
from .monitoring.watchlist_monitor_agent import WatchlistMonitorAgent
from .monitoring.xtrades_monitor_agent import XtradesMonitorAgent
from .monitoring.alert_agent import AlertAgent
from .monitoring.price_action_agent import PriceActionMonitorAgent

# Research Agents
from .research.knowledge_agent import KnowledgeAgent
from .research.research_agent import ResearchAgent
from .research.documentation_agent import DocumentationAgent

# Management Agents
from .management.task_management_agent import TaskManagementAgent
from .management.position_agent import PositionManagementAgent
from .management.settings_agent import SettingsAgent

# Code Development Agents
from .code.code_recommendation_agent import CodeRecommendationAgent
from .code.claude_code_controller_agent import ClaudeCodeControllerAgent
from .code.qa_agent import QAAgent

__all__ = [
    # Trading Agents
    "MarketDataAgent",
    "OptionsAnalysisAgent",
    "StrategyAgent",
    "RiskManagementAgent",
    "PortfolioAgent",
    "EarningsAgent",
    "PremiumScannerAgent",
    
    # Analysis Agents
    "FundamentalAnalysisAgent",
    "TechnicalAnalysisAgent",
    "SentimentAnalysisAgent",
    "SupplyDemandAgent",
    "SectorAnalysisAgent",
    "OptionsFlowAgent",
    
    # Sports Betting Agents
    "KalshiMarketsAgent",
    "SportsBettingAgent",
    "NFLMarketsAgent",
    "GameAnalysisAgent",
    "OddsComparisonAgent",
    "BettingStrategyAgent",
    
    # Monitoring Agents
    "WatchlistMonitorAgent",
    "XtradesMonitorAgent",
    "AlertAgent",
    "PriceActionMonitorAgent",
    
    # Research Agents
    "KnowledgeAgent",
    "ResearchAgent",
    "DocumentationAgent",
    
    # Management Agents
    "TaskManagementAgent",
    "PositionManagementAgent",
    "SettingsAgent",
    
    # Code Development Agents
    "CodeRecommendationAgent",
    "ClaudeCodeControllerAgent",
    "QAAgent",
]
