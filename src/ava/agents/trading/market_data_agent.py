"""
Market Data Agent - Unified LangGraph-based agent
Migrated from src/agents/runtime/market_data_agent.py
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import yfinance as yf
import pandas as pd

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_stock_price_tool(symbol: str) -> str:
    """Get current stock price for a symbol"""
    try:
        ticker = yf.Ticker(symbol)
        hist = ticker.history(period="1d")
        if hist.empty:
            return f"No data for {symbol}"
        price = float(hist['Close'].iloc[-1])
        return f"{symbol}: ${price:.2f}"
    except Exception as e:
        return f"Error getting price for {symbol}: {str(e)}"


@tool
def get_stock_info_tool(symbol: str) -> str:
    """Get comprehensive stock information"""
    try:
        ticker = yf.Ticker(symbol)
        info = ticker.info
        hist = ticker.history(period="1mo")
        
        if hist.empty:
            return f"No data for {symbol}"
        
        current_price = float(hist['Close'].iloc[-1])
        avg_volume = int(hist['Volume'].mean())
        volatility = float(hist['Close'].pct_change().std() * (252 ** 0.5))
        
        result = {
            'symbol': symbol,
            'name': info.get('longName', symbol),
            'price': current_price,
            'volume': avg_volume,
            'volatility': volatility,
            'market_cap': info.get('marketCap', 0),
            'sector': info.get('sector', 'Unknown')
        }
        
        return str(result)
    except Exception as e:
        return f"Error getting info for {symbol}: {str(e)}"


class MarketDataAgent(BaseAgent):
    """
    Market Data Agent - Provides real-time market data and analysis
    
    Capabilities:
    - Stock price lookup
    - Market data analysis
    - Volume and volatility analysis
    - Sector information
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize Market Data Agent"""
        tools = [
            get_stock_price_tool,
            get_stock_info_tool
        ]
        
        super().__init__(
            name="market_data_agent",
            description="Provides real-time market data, stock prices, and market analysis",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.metadata['capabilities'] = [
            'get_stock_price',
            'get_market_data',
            'analyze_volume',
            'analyze_volatility',
            'sector_analysis'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """
        Execute market data agent
        
        Processes requests for:
        - Stock prices
        - Market data
        - Volume analysis
        - Volatility analysis
        """
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            # Extract symbol from input
            symbol = context.get('symbol') or self._extract_symbol(input_text)
            
            if not symbol:
                state['result'] = {
                    'error': 'No symbol provided',
                    'message': 'Please provide a stock symbol'
                }
                return state
            
            # Get market data
            ticker = yf.Ticker(symbol)
            hist = ticker.history(period="1mo")
            info = ticker.info
            
            if hist.empty:
                state['result'] = {
                    'error': 'No data available',
                    'symbol': symbol
                }
                return state
            
            # Calculate metrics
            current_price = float(hist['Close'].iloc[-1])
            avg_volume = int(hist['Volume'].mean())
            volatility = float(hist['Close'].pct_change().std() * (252 ** 0.5))
            
            result = {
                'symbol': symbol,
                'company_name': info.get('longName', symbol),
                'current_price': current_price,
                'avg_volume': avg_volume,
                'volatility': volatility,
                'market_cap': info.get('marketCap', 0),
                'sector': info.get('sector', 'Unknown'),
                'pe_ratio': info.get('trailingPE'),
                'timestamp': datetime.now().isoformat()
            }
            
            state['result'] = result
            state['metadata']['agent'] = self.name
            state['metadata']['execution_time'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"MarketDataAgent error: {e}")
            state['error'] = str(e)
            state['result'] = {'error': str(e)}
            return state
    
    def _extract_symbol(self, text: str) -> Optional[str]:
        """Extract stock symbol from text"""
        # Simple extraction - can be enhanced with NLP
        words = text.upper().split()
        for word in words:
            if len(word) <= 5 and word.isalpha():
                return word
        return None

