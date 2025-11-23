"""
Sports Betting Agent - Unified LangGraph-based agent
Migrated from src/advanced_betting_ai_agent.py
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import math

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

# Import betting components
try:
    from src.advanced_betting_ai_agent import AdvancedBettingAIAgent
    BETTING_AVAILABLE = True
except ImportError:
    BETTING_AVAILABLE = False

logger = logging.getLogger(__name__)


@tool
def analyze_betting_opportunity_tool(game_data: str, market_data: str) -> str:
    """Analyze a sports betting opportunity"""
    try:
        if not BETTING_AVAILABLE:
            return "Betting components not available"
        
        import json
        game = json.loads(game_data) if isinstance(game_data, str) else game_data
        market = json.loads(market_data) if isinstance(market_data, str) else market_data
        
        agent = AdvancedBettingAIAgent()
        result = agent.analyze_betting_opportunity(game, market)
        return json.dumps(result, default=str)
    except Exception as e:
        return f"Error analyzing opportunity: {str(e)}"


class SportsBettingAgent(BaseAgent):
    """
    Sports Betting Agent - AI-powered sports betting analysis
    
    Capabilities:
    - Analyze betting opportunities
    - Calculate win probabilities
    - Expected value calculations
    - Kelly Criterion bet sizing
    - Confidence scoring
    - High-confidence signal detection
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize Sports Betting Agent"""
        tools = [analyze_betting_opportunity_tool]
        
        super().__init__(
            name="sports_betting_agent",
            description="AI-powered sports betting analysis with Kelly Criterion, expected value, and confidence scoring",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.betting_agent = AdvancedBettingAIAgent() if BETTING_AVAILABLE else None
        
        self.metadata['capabilities'] = [
            'analyze_betting_opportunity',
            'calculate_win_probability',
            'calculate_expected_value',
            'kelly_criterion_sizing',
            'confidence_scoring',
            'high_confidence_signals',
            'game_state_analysis',
            'odds_analysis'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute sports betting agent
        
        Processes requests for:
        - Betting opportunity analysis
        - Win probability calculations
        - Expected value analysis
        - Bet sizing recommendations
        """
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            if not self.betting_agent:
                state['result'] = {
                    'error': 'Betting components not available',
                    'message': 'AdvancedBettingAIAgent not initialized'
                }
                return state
            
            # Extract game and market data from context
            game_data = context.get('game_data', {})
            market_data = context.get('market_data', {})
            
            if not game_data or not market_data:
                state['result'] = {
                    'error': 'Missing data',
                    'message': 'game_data and market_data required'
                }
                return state
            
            # Analyze betting opportunity
            analysis = self.betting_agent.analyze_betting_opportunity(
                game_data=game_data,
                market_data=market_data,
                historical_data=context.get('historical_data')
            )
            
            result = {
                'analysis': analysis,
                'timestamp': datetime.now().isoformat()
            }
            
            state['result'] = result
            state['metadata']['agent'] = self.name
            state['metadata']['execution_time'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"SportsBettingAgent error: {e}")
            state['error'] = str(e)
            state['result'] = {'error': str(e)}
            return state

