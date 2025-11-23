"""
AVA Integration for Options Analysis
Natural language query support for the unified Options Analysis page
"""

import logging
import re
from typing import Dict, Any, Optional, List
from src.options_analysis.unified_analyzer import UnifiedOptionsAnalyzer

logger = logging.getLogger(__name__)


class OptionsAnalysisAVA:
    """AVA integration for natural language options analysis queries"""

    def __init__(self, analyzer: UnifiedOptionsAnalyzer):
        """
        Initialize AVA integration

        Args:
            analyzer: UnifiedOptionsAnalyzer instance
        """
        self.analyzer = analyzer

        # Query patterns
        self.patterns = {
            'scan': r'(find|scan|search|show me).*(opportunities|options|trades)',
            'analyze': r'(analyze|what.*strategy|best strategy|recommend)',
            'position': r'(my position|current position|holding)',
            'watchlist': r'watchlist|in (NVDA|MAIN|Investment)',
            'symbol': r'\b([A-Z]{1,5})\b',  # Stock ticker pattern
            'strategy_type': r'(CSP|calendar|spread|iron condor|covered call)',
        }

    def parse_query(self, user_input: str) -> Dict[str, Any]:
        """
        Parse natural language query

        Args:
            user_input: User's natural language input

        Returns:
            Dict with parsed intent and parameters:
            {
                'action': 'scan' | 'analyze' | 'position',
                'symbol': str (if found),
                'watchlist': str (if found),
                'strategy': str (if specified),
                'filters': dict (default filters)
            }

        Examples:
            "Find CSP opportunities in NVDA watchlist"
            → {'action': 'scan', 'watchlist': 'NVDA', 'strategy': 'csp'}

            "What's the best strategy for AAPL?"
            → {'action': 'analyze', 'symbol': 'AAPL'}

            "Analyze my TSLA position"
            → {'action': 'position', 'symbol': 'TSLA'}

            "Show me calendar spreads on SPY"
            → {'action': 'analyze', 'symbol': 'SPY', 'strategy': 'calendar'}
        """
        user_input = user_input.lower()
        result = {
            'action': None,
            'symbol': None,
            'watchlist': None,
            'strategy': None,
            'filters': {
                'dte_range': (20, 40),
                'delta_range': (-0.45, -0.15),
                'min_premium': 100.0,
                'min_score': 60  # Higher default for AVA queries
            }
        }

        # Determine action
        if re.search(self.patterns['scan'], user_input):
            result['action'] = 'scan'
        elif re.search(self.patterns['position'], user_input):
            result['action'] = 'position'
        elif re.search(self.patterns['analyze'], user_input):
            result['action'] = 'analyze'
        else:
            # Default to scan if ambiguous
            result['action'] = 'scan'

        # Extract symbol
        symbol_matches = re.findall(self.patterns['symbol'], user_input.upper())
        if symbol_matches:
            # Filter out common words
            excluded = ['IN', 'ON', 'FOR', 'MY', 'THE', 'CSP', 'PUT', 'CALL']
            symbols = [s for s in symbol_matches if s not in excluded]
            if symbols:
                result['symbol'] = symbols[0]

        # Extract watchlist
        if re.search(self.patterns['watchlist'], user_input):
            watchlist_match = re.search(r'in (NVDA|MAIN|Investment|Track)', user_input, re.IGNORECASE)
            if watchlist_match:
                result['watchlist'] = watchlist_match.group(1)

        # Extract strategy type
        strategy_match = re.search(self.patterns['strategy_type'], user_input, re.IGNORECASE)
        if strategy_match:
            result['strategy'] = strategy_match.group(1).lower()

        logger.info(f"Parsed AVA query: {result}")
        return result

    def execute_query(self, parsed: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute parsed query using the analyzer

        Args:
            parsed: Parsed query from parse_query()

        Returns:
            Dict with execution results
        """
        action = parsed['action']

        try:
            if action == 'scan':
                return self._execute_scan(parsed)
            elif action == 'analyze':
                return self._execute_analyze(parsed)
            elif action == 'position':
                return self._execute_position(parsed)
            else:
                return {
                    'success': False,
                    'error': 'Unknown action',
                    'message': "I'm not sure what you want me to do. Try 'find opportunities' or 'analyze [symbol]'."
                }

        except Exception as e:
            logger.error(f"Error executing AVA query: {e}")
            return {
                'success': False,
                'error': str(e),
                'message': f"Sorry, I encountered an error: {str(e)}"
            }

    def _execute_scan(self, parsed: Dict) -> Dict:
        """Execute screening scan"""
        filters = parsed['filters']
        watchlist = parsed['watchlist']
        symbol = parsed['symbol']

        scan_params = {
            'source': 'watchlist' if watchlist else 'symbols' if symbol else 'all',
            'watchlist_name': watchlist,
            'symbols': [symbol] if symbol else None,
            'dte_range': filters['dte_range'],
            'delta_range': filters['delta_range'],
            'min_premium': filters['min_premium'],
            'limit': 20,  # Limit for AVA responses
            'min_score': filters['min_score'],
            'use_llm': False  # Fast scanning for AVA
        }

        results = self.analyzer.screen_opportunities(**scan_params)

        return {
            'success': True,
            'action': 'scan',
            'results': results,
            'opportunities': results.get('opportunities', [])[:5],  # Top 5
            'summary': results.get('summary', {})
        }

    def _execute_analyze(self, parsed: Dict) -> Dict:
        """Execute strategy analysis for a stock"""
        symbol = parsed['symbol']

        if not symbol:
            return {
                'success': False,
                'error': 'No symbol specified',
                'message': "Please specify a stock symbol to analyze (e.g., 'analyze AAPL')."
            }

        # Fetch stock data
        from src.ai_options_agent.shared.data_fetchers import (
            fetch_stock_info,
            fetch_options_suggestions,
            calculate_iv_for_stock
        )

        stock_info = fetch_stock_info(symbol)

        if not stock_info:
            return {
                'success': False,
                'error': f'Could not fetch data for {symbol}',
                'message': f"Sorry, I couldn't find data for {symbol}. Please check the symbol."
            }

        # Get suggested option
        options_suggestions = fetch_options_suggestions(symbol)
        if options_suggestions:
            selected_option = options_suggestions[0]  # Use best option
        else:
            selected_option = {
                'strike': stock_info.get('current_price', 100) * 0.95,
                'dte': 30,
                'delta': -0.30,
                'premium': 250
            }

        # Prepare analysis data
        stock_data = {
            'symbol': symbol,
            'current_price': stock_info.get('current_price', 0),
            'iv': calculate_iv_for_stock(symbol),
            'price_52w_high': stock_info.get('high_52week', 0),
            'price_52w_low': stock_info.get('low_52week', 0),
            'market_cap': stock_info.get('market_cap', 0),
            'pe_ratio': stock_info.get('pe_ratio', 28.5),
            'sector': stock_info.get('sector', 'Unknown')
        }

        options_data = {
            'strike_price': selected_option.get('strike', 0),
            'dte': selected_option.get('dte', 0),
            'delta': selected_option.get('delta', -0.30),
            'premium': selected_option.get('premium', 0)
        }

        # Run analysis
        analysis = self.analyzer.analyze_stock_strategies(
            symbol=symbol,
            stock_data=stock_data,
            options_data=options_data,
            use_multi_model=False  # Fast analysis for AVA
        )

        return {
            'success': True,
            'action': 'analyze',
            'symbol': symbol,
            'analysis': analysis,
            'top_strategies': analysis.get('strategy_rankings', [])[:3]
        }

    def _execute_position(self, parsed: Dict) -> Dict:
        """Execute position analysis"""
        symbol = parsed['symbol']

        # Get positions
        from src.data.positions_manager import PositionsManager
        positions_mgr = PositionsManager()

        if symbol:
            positions = positions_mgr.get_position_by_symbol(symbol)
        else:
            positions = positions_mgr.get_current_positions()

        if not positions:
            return {
                'success': False,
                'error': 'No positions found',
                'message': f"I couldn't find any positions{' for ' + symbol if symbol else ''}."
            }

        # Analyze first position
        position = positions[0]

        analysis = self.analyzer.analyze_position(
            position=position,
            use_multi_model=False
        )

        return {
            'success': True,
            'action': 'position',
            'position': position,
            'analysis': analysis,
            'recommendation': analysis.get('recommendation', 'KEEP')
        }

    def format_response(self, result: Dict) -> str:
        """
        Format execution results for chat display

        Args:
            result: Result from execute_query()

        Returns:
            Formatted string for AVA chat response
        """
        if not result.get('success', False):
            return f"❌ {result.get('message', 'An error occurred')}"

        action = result.get('action')

        if action == 'scan':
            return self._format_scan_response(result)
        elif action == 'analyze':
            return self._format_analyze_response(result)
        elif action == 'position':
            return self._format_position_response(result)
        else:
            return "✅ Query executed successfully"

    def _format_scan_response(self, result: Dict) -> str:
        """Format scan results for chat"""
        opportunities = result.get('opportunities', [])
        summary = result.get('summary', {})

        if not opportunities:
            return "🔍 No opportunities found with current filters. Try adjusting your criteria."

        response = f"🎯 **Found {summary.get('total', 0)} opportunities!**\n\n**Top 5:**\n\n"

        for idx, opp in enumerate(opportunities[:5]):
            symbol = opp.get('symbol', 'N/A')
            score = opp.get('final_score', 0)
            strike = opp.get('strike_price', 0)
            dte = opp.get('dte', 0)
            premium = opp.get('premium', 0) / 100

            response += f"{idx+1}. **{symbol}** - Score: {score}/100\n"
            response += f"   ${strike:.0f} strike, {dte}d DTE, ${premium:.2f} premium\n\n"

        response += f"\n💡 Average score: {summary.get('avg_score', 0):.0f}/100"
        response += f"\n✅ {summary.get('strong_buys', 0)} STRONG BUY recommendations"

        return response

    def _format_analyze_response(self, result: Dict) -> str:
        """Format strategy analysis for chat"""
        symbol = result.get('symbol', 'N/A')
        analysis = result.get('analysis', {})
        top_strategies = result.get('top_strategies', [])

        if not top_strategies:
            return f"❌ Could not analyze strategies for {symbol}"

        env = analysis.get('environment_analysis', {})

        response = f"🎯 **Analysis for {symbol}**\n\n"
        response += f"📊 **Market Environment:**\n"
        response += f"- Volatility: {env.get('volatility_regime', 'N/A').upper()}\n"
        response += f"- Trend: {env.get('trend', 'N/A').upper()}\n"
        response += f"- IV: {env.get('iv', 0)*100:.1f}%\n\n"

        response += f"🏆 **Top 3 Strategies:**\n\n"

        for idx, strategy in enumerate(top_strategies):
            name = strategy.get('name', 'Unknown')
            score = strategy.get('score', 0)
            win_rate = strategy.get('win_rate', 'N/A')

            response += f"{idx+1}. **{name}** - {score}/100 (Win rate: {win_rate})\n"

        response += f"\n💡 **Recommendation:** Use {top_strategies[0].get('name', 'the top strategy')}"

        return response

    def _format_position_response(self, result: Dict) -> str:
        """Format position analysis for chat"""
        position = result.get('position', {})
        analysis = result.get('analysis', {})
        recommendation = result.get('recommendation', 'KEEP')

        symbol = position.get('symbol', 'N/A')
        pnl = position.get('pnl', 0)
        pnl_pct = position.get('pnl_pct', 0)

        response = f"📊 **Position Analysis: {symbol}**\n\n"
        response += f"💰 Current P&L: ${pnl:.2f} ({pnl_pct:+.1f}%)\n"
        response += f"📅 DTE: {position.get('dte', 0)} days\n"
        response += f"🎯 Strike: ${position.get('strike', 0):.2f}\n\n"

        if recommendation == 'KEEP':
            response += "✅ **KEEP** - Position is still optimal"
        elif recommendation == 'ADJUST':
            response += "⚠️ **ADJUST** - Consider rolling or modifying"
        else:
            response += "❌ **CLOSE** - Exit this position"

        top_strategies = analysis.get('strategy_rankings', [])[:3]
        if top_strategies:
            response += "\n\n🎯 **Alternative Strategies:**\n"
            for idx, s in enumerate(top_strategies):
                response += f"{idx+1}. {s.get('name', 'Unknown')} ({s.get('score', 0)}/100)\n"

        return response
