"""
Kalshi Markets Agent - Unified LangGraph-based agent
Handles all Kalshi prediction markets (Politics, Sports, Economics, Crypto, etc.)
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import os

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

# Import Kalshi components
try:
    from src.kalshi_db_manager import KalshiDBManager
    from src.kalshi_public_client import KalshiPublicClient
    KALSHI_AVAILABLE = True
except ImportError:
    KALSHI_AVAILABLE = False
    logger.warning("Kalshi components not available")

logger = logging.getLogger(__name__)


@tool
def get_kalshi_markets_tool(category: str = "all", status: str = "active", limit: int = 50) -> str:
    """Get Kalshi prediction markets by category"""
    try:
        if not KALSHI_AVAILABLE:
            return "Kalshi components not available"
        
        db_manager = KalshiDBManager()
        markets = db_manager.get_markets_by_category(category, status, limit)
        return f"Found {len(markets)} markets in category {category}"
    except Exception as e:
        return f"Error getting Kalshi markets: {str(e)}"


@tool
def get_best_kalshi_opportunities_tool(min_score: float = 70.0, category: str = "all") -> str:
    """Get best Kalshi betting opportunities by AI score"""
    try:
        if not KALSHI_AVAILABLE:
            return "Kalshi components not available"
        
        db_manager = KalshiDBManager()
        opportunities = db_manager.get_top_opportunities(min_score=min_score, category=category, limit=20)
        return f"Found {len(opportunities)} opportunities with score >= {min_score}"
    except Exception as e:
        return f"Error getting opportunities: {str(e)}"


class KalshiMarketsAgent(BaseAgent):
    """
    Kalshi Markets Agent - Handles all Kalshi prediction markets
    
    Capabilities:
    - Get markets by category (Politics, Sports, Economics, Crypto, etc.)
    - Find best opportunities by AI score
    - Analyze market odds and liquidity
    - Compare markets across categories
    - Track market performance
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize Kalshi Markets Agent"""
        tools = [
            get_kalshi_markets_tool,
            get_best_kalshi_opportunities_tool
        ]
        
        super().__init__(
            name="kalshi_markets_agent",
            description="Handles all Kalshi prediction markets including Politics, Sports, Economics, Crypto, Companies, Tech, Climate, and World events",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.db_manager = KalshiDBManager() if KALSHI_AVAILABLE else None
        self.client = KalshiPublicClient() if KALSHI_AVAILABLE else None
        
        self.metadata['capabilities'] = [
            'get_kalshi_markets',
            'find_best_opportunities',
            'analyze_market_odds',
            'compare_categories',
            'track_market_performance',
            'politics_markets',
            'sports_markets',
            'economics_markets',
            'crypto_markets',
            'companies_markets',
            'tech_markets',
            'climate_markets',
            'world_markets'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute Kalshi markets agent
        
        Processes requests for:
        - Market discovery by category
        - Best opportunity identification
        - Market analysis
        - Odds comparison
        """
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            if not self.db_manager:
                state['result'] = {
                    'error': 'Kalshi components not available',
                    'message': 'Kalshi database manager not initialized'
                }
                return state
            
            # Extract parameters from input/context
            category = context.get('category', 'all')
            min_score = context.get('min_score', 70.0)
            status = context.get('status', 'active')
            limit = context.get('limit', 50)
            
            # Determine action based on input
            if 'best' in input_text.lower() or 'opportunity' in input_text.lower():
                # Get best opportunities
                opportunities = self.db_manager.get_top_opportunities(
                    min_score=min_score,
                    category=category,
                    limit=limit
                )
                
                result = {
                    'action': 'get_best_opportunities',
                    'opportunities': opportunities,
                    'count': len(opportunities),
                    'category': category,
                    'min_score': min_score,
                    'timestamp': datetime.now().isoformat()
                }
            else:
                # Get markets by category
                markets = self.db_manager.get_markets_by_category(
                    category=category,
                    status=status,
                    limit=limit
                )
                
                result = {
                    'action': 'get_markets',
                    'markets': markets,
                    'count': len(markets),
                    'category': category,
                    'status': status,
                    'timestamp': datetime.now().isoformat()
                }
            
            state['result'] = result
            state['metadata']['agent'] = self.name
            state['metadata']['execution_time'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"KalshiMarketsAgent error: {e}")
            state['error'] = str(e)
            state['result'] = {'error': str(e)}
            return state

