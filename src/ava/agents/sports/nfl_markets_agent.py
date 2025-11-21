"""
NFL Markets Agent - NFL-specific betting analysis
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_nfl_markets_tool(status: str = "active", limit: int = 50) -> str:
    """Get NFL-specific Kalshi markets"""
    try:
        from src.kalshi_db_manager import KalshiDBManager
        db_manager = KalshiDBManager()
        markets = db_manager.get_markets_by_category("sports", status, limit)
        nfl_markets = [m for m in markets if 'nfl' in str(m).lower() or 'football' in str(m).lower()]
        return f"Found {len(nfl_markets)} NFL markets"
    except Exception as e:
        return f"Error: {str(e)}"


class NFLMarketsAgent(BaseAgent):
    """
    NFL Markets Agent - NFL-specific betting markets
    
    Capabilities:
    - Get NFL markets
    - Analyze NFL games
    - Player props
    - Game outcomes
    - Team performance
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize NFL Markets Agent"""
        tools = [get_nfl_markets_tool]
        
        super().__init__(
            name="nfl_markets_agent",
            description="Handles NFL-specific betting markets and game analysis",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.metadata['capabilities'] = [
            'get_nfl_markets',
            'analyze_nfl_games',
            'player_props',
            'game_outcomes',
            'team_performance',
            'nfl_betting_analysis'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute NFL markets agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            status = context.get('status', 'active')
            limit = context.get('limit', 50)
            
            try:
                from src.kalshi_db_manager import KalshiDBManager
                db_manager = KalshiDBManager()
                markets = db_manager.get_markets_by_category("sports", status, limit)
                nfl_markets = [m for m in markets if 'nfl' in str(m).lower() or 'football' in str(m).lower()]
                
                result = {
                    'action': 'get_nfl_markets',
                    'markets': nfl_markets,
                    'count': len(nfl_markets),
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                result = {
                    'error': str(e),
                    'message': 'Kalshi database not available'
                }
            
            state['result'] = result
            return state
            
        except Exception as e:
            logger.error(f"NFLMarketsAgent error: {e}")
            state['error'] = str(e)
            return state

