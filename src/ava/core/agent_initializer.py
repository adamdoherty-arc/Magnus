"""
Agent Initializer - Registers all agents with the registry
"""

import logging
from typing import List, Optional

from .agent_registry import AgentRegistry

# Import all agents
from ..agents.trading.market_data_agent import MarketDataAgent
from ..agents.trading.options_analysis_agent import OptionsAnalysisAgent
from ..agents.trading.strategy_agent import StrategyAgent
from ..agents.trading.risk_management_agent import RiskManagementAgent
from ..agents.trading.portfolio_agent import PortfolioAgent
from ..agents.trading.earnings_agent import EarningsAgent
from ..agents.trading.premium_scanner_agent import PremiumScannerAgent

from ..agents.analysis.fundamental_agent import FundamentalAnalysisAgent
from ..agents.analysis.technical_agent import TechnicalAnalysisAgent
from ..agents.analysis.sentiment_agent import SentimentAnalysisAgent
from ..agents.analysis.supply_demand_agent import SupplyDemandAgent
from ..agents.analysis.sector_agent import SectorAnalysisAgent
from ..agents.analysis.options_flow_agent import OptionsFlowAgent

from ..agents.sports.kalshi_markets_agent import KalshiMarketsAgent
from ..agents.sports.sports_betting_agent import SportsBettingAgent
from ..agents.sports.nfl_markets_agent import NFLMarketsAgent
from ..agents.sports.game_analysis_agent import GameAnalysisAgent
from ..agents.sports.odds_comparison_agent import OddsComparisonAgent
from ..agents.sports.betting_strategy_agent import BettingStrategyAgent

from ..agents.monitoring.watchlist_monitor_agent import WatchlistMonitorAgent
from ..agents.monitoring.xtrades_monitor_agent import XtradesMonitorAgent
from ..agents.monitoring.alert_agent import AlertAgent
from ..agents.monitoring.price_action_agent import PriceActionMonitorAgent
from ..agents.monitoring.discord_agent import DiscordAgent  # NEW: Discord integration
from ..agents.monitoring.analytics_agent import AnalyticsAgent  # NEW: Analytics performance
from ..agents.monitoring.cache_metrics_agent import CacheMetricsAgent  # NEW: Cache monitoring

from ..agents.research.knowledge_agent import KnowledgeAgent
from ..agents.research.research_agent import ResearchAgent
from ..agents.research.documentation_agent import DocumentationAgent

from ..agents.management.task_management_agent import TaskManagementAgent
from ..agents.management.position_agent import PositionManagementAgent
from ..agents.management.settings_agent import SettingsAgent

from ..agents.code.code_recommendation_agent import CodeRecommendationAgent
from ..agents.code.claude_code_controller_agent import ClaudeCodeControllerAgent
from ..agents.code.qa_agent import QAAgent

logger = logging.getLogger(__name__)


def initialize_all_agents(registry: Optional[AgentRegistry] = None) -> List:
    """
    Initialize all agents (does not register - use ensure_agents_initialized)
    
    Args:
        registry: Optional registry instance to register with
    
    Returns:
        List of initialized agent instances
    """
    agents = []
    
    try:
        # Trading Agents
        agents.append(MarketDataAgent())
        agents.append(OptionsAnalysisAgent())
        agents.append(StrategyAgent())
        agents.append(RiskManagementAgent())
        agents.append(PortfolioAgent())
        agents.append(EarningsAgent())
        agents.append(PremiumScannerAgent())
        
        # Analysis Agents
        agents.append(FundamentalAnalysisAgent())
        agents.append(TechnicalAnalysisAgent())
        agents.append(SentimentAnalysisAgent())
        agents.append(SupplyDemandAgent())
        agents.append(SectorAnalysisAgent())
        agents.append(OptionsFlowAgent())
        
        # Sports Betting Agents
        agents.append(KalshiMarketsAgent())
        agents.append(SportsBettingAgent())
        agents.append(NFLMarketsAgent())
        agents.append(GameAnalysisAgent())
        agents.append(OddsComparisonAgent())
        agents.append(BettingStrategyAgent())
        
        # Monitoring Agents
        agents.append(WatchlistMonitorAgent())
        agents.append(XtradesMonitorAgent())
        agents.append(AlertAgent())
        agents.append(PriceActionMonitorAgent())
        agents.append(DiscordAgent())  # NEW: Discord message monitoring
        agents.append(AnalyticsAgent())  # NEW: Performance analytics
        agents.append(CacheMetricsAgent())  # NEW: Cache metrics tracking
        
        # Research Agents
        agents.append(KnowledgeAgent())
        agents.append(ResearchAgent())
        agents.append(DocumentationAgent())
        
        # Management Agents
        agents.append(TaskManagementAgent())
        agents.append(PositionManagementAgent())
        agents.append(SettingsAgent())
        
        # Code Development Agents
        agents.append(CodeRecommendationAgent())
        agents.append(ClaudeCodeControllerAgent())
        agents.append(QAAgent())
        
        # Register with provided registry if given
        if registry:
            for agent in agents:
                try:
                    registry.register(agent)
                    logger.info(f"Registered agent: {agent.name}")
                except Exception as e:
                    logger.error(f"Failed to register agent {agent.name}: {e}")
        
        logger.info(f"Successfully initialized {len(agents)} agents")
        return agents
        
    except Exception as e:
        logger.error(f"Error initializing agents: {e}")
        return agents


# Global registry instance - singleton pattern
_registry_instance: Optional[AgentRegistry] = None

def get_registry() -> AgentRegistry:
    """Get or create the global registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = AgentRegistry()
    return _registry_instance

def ensure_agents_initialized():
    """Ensure agents are initialized (idempotent)"""
    global _registry_instance
    registry = get_registry()
    
    # Check if agents are already registered
    existing_count = len(registry.list_agent_names())
    if existing_count > 0:
        logger.info(f"Agents already initialized: {existing_count} agents")
        return
    
    # Initialize and register all agents
    logger.info("Initializing all agents...")
    agents = initialize_all_agents()
    
    registered_count = 0
    for agent in agents:
        try:
            registry.register(agent)
            registered_count += 1
            logger.info(f"Registered agent: {agent.name}")
        except Exception as e:
            logger.error(f"Failed to register agent {agent.name}: {e}")
    
    final_count = len(registry.list_agent_names())
    logger.info(f"Successfully initialized and registered {registered_count}/{len(agents)} agents. Registry now has {final_count} agents.")
    
    if final_count == 0:
        logger.error("WARNING: No agents registered! Check initialization errors above.")

