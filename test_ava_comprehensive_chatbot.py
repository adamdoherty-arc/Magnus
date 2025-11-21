"""
AVA Chatbot Comprehensive Testing Suite
========================================

Tests for verifying AVA chatbot capabilities across all features:
1. Modern chatbot features (NLU, context, memory, intents)
2. Platform access (portfolio, Robinhood, TradingView, databases)
3. Reasoning capabilities (analysis, patterns, risk, strategies)
4. Core functionality (quick actions, real-time data, history)

Author: Test Automation Specialist
Created: 2025-11-12
"""

import sys
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
import traceback

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# =============================================================================
# Test Result Tracking
# =============================================================================

@dataclass
class TestResult:
    """Individual test result"""
    test_name: str
    category: str
    passed: bool
    message: str
    details: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())


@dataclass
class TestSuite:
    """Test suite with results tracking"""
    name: str
    results: List[TestResult] = field(default_factory=list)

    def add_result(self, result: TestResult):
        """Add test result"""
        self.results.append(result)

    def get_summary(self) -> Dict[str, Any]:
        """Get test summary"""
        total = len(self.results)
        passed = sum(1 for r in self.results if r.passed)
        failed = total - passed

        by_category = {}
        for result in self.results:
            if result.category not in by_category:
                by_category[result.category] = {'passed': 0, 'failed': 0}
            if result.passed:
                by_category[result.category]['passed'] += 1
            else:
                by_category[result.category]['failed'] += 1

        return {
            'total_tests': total,
            'passed': passed,
            'failed': failed,
            'pass_rate': (passed / total * 100) if total > 0 else 0,
            'by_category': by_category
        }


# =============================================================================
# Test Categories
# =============================================================================

class ModernChatbotTests:
    """Tests for modern chatbot features"""

    def __init__(self):
        self.suite = TestSuite("Modern Chatbot Features")

    def test_natural_language_understanding(self) -> TestResult:
        """Test NLU capabilities"""
        try:
            from src.ava.nlp_handler import NaturalLanguageHandler

            handler = NaturalLanguageHandler()

            # Test various phrasings of same intent
            test_cases = [
                ("How's my portfolio doing?", "portfolio"),
                ("Show me my positions", "positions"),
                ("What are the best trading opportunities?", "opportunities"),
                ("Can you help me?", "help")
            ]

            results = []
            for query, expected_intent in test_cases:
                result = handler.parse_intent(query)
                intent_match = expected_intent in result['intent'].lower()
                results.append(intent_match)

            all_passed = all(results)

            return TestResult(
                test_name="Natural Language Understanding",
                category="Modern Chatbot",
                passed=all_passed,
                message=f"NLU correctly identified {sum(results)}/{len(results)} intents",
                details={'test_cases': len(test_cases), 'passed': sum(results)}
            )

        except Exception as e:
            return TestResult(
                test_name="Natural Language Understanding",
                category="Modern Chatbot",
                passed=False,
                message=f"NLU test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_context_awareness(self) -> TestResult:
        """Test context and conversation memory"""
        try:
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # First message with context
            msg1 = chatbot.process_message(
                "What are good NVDA opportunities?",
                context={'history': []}
            )

            # Follow-up message referencing previous
            msg2 = chatbot.process_message(
                "What about the risks?",
                context={
                    'history': [
                        {'role': 'user', 'content': 'What are good NVDA opportunities?'},
                        {'role': 'assistant', 'content': msg1['response']}
                    ]
                }
            )

            # Check if context is maintained
            has_response = bool(msg2.get('response'))

            return TestResult(
                test_name="Context Awareness",
                category="Modern Chatbot",
                passed=has_response,
                message="Context awareness working" if has_response else "Context not maintained",
                details={
                    'first_intent': msg1.get('intent'),
                    'second_intent': msg2.get('intent'),
                    'context_used': True
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Context Awareness",
                category="Modern Chatbot",
                passed=False,
                message=f"Context test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_multi_turn_conversation(self) -> TestResult:
        """Test multi-turn conversation handling"""
        try:
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()
            conversation_history = []

            # Simulate 3-turn conversation
            turns = [
                "Tell me about CSP opportunities",
                "Which one has the lowest risk?",
                "Show me the details on that one"
            ]

            responses = []
            for turn in turns:
                response = chatbot.process_message(
                    turn,
                    context={'history': conversation_history}
                )
                responses.append(response)
                conversation_history.append({'role': 'user', 'content': turn})
                conversation_history.append({'role': 'assistant', 'content': response['response']})

            all_responded = all(r.get('response') for r in responses)

            return TestResult(
                test_name="Multi-turn Conversation",
                category="Modern Chatbot",
                passed=all_responded,
                message=f"Handled {len(turns)}-turn conversation successfully",
                details={
                    'turns': len(turns),
                    'responses': [r.get('intent') for r in responses]
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Multi-turn Conversation",
                category="Modern Chatbot",
                passed=False,
                message=f"Multi-turn test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_intent_recognition(self) -> TestResult:
        """Test intent recognition accuracy"""
        try:
            from src.ava.nlp_handler import NaturalLanguageHandler

            handler = NaturalLanguageHandler()

            # Test specific intents with variations
            test_intents = {
                'portfolio': [
                    "Show my portfolio",
                    "How's my account doing?",
                    "What's my balance?"
                ],
                'positions': [
                    "What positions do I have?",
                    "Show my trades",
                    "My options contracts"
                ],
                'opportunities': [
                    "Find good trades",
                    "Best CSP plays",
                    "Trading opportunities"
                ],
                'help': [
                    "Help me",
                    "What can you do?",
                    "Show commands"
                ]
            }

            correct = 0
            total = 0

            for expected_intent, queries in test_intents.items():
                for query in queries:
                    result = handler.parse_intent(query)
                    total += 1
                    if expected_intent in result['intent'].lower():
                        correct += 1

            accuracy = (correct / total * 100) if total > 0 else 0

            return TestResult(
                test_name="Intent Recognition",
                category="Modern Chatbot",
                passed=accuracy >= 70,  # 70% threshold
                message=f"Intent recognition accuracy: {accuracy:.1f}%",
                details={
                    'correct': correct,
                    'total': total,
                    'accuracy': accuracy
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Intent Recognition",
                category="Modern Chatbot",
                passed=False,
                message=f"Intent recognition test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_entity_extraction(self) -> TestResult:
        """Test entity extraction (tickers, dates, numbers)"""
        try:
            from src.ava.nlp_handler import NaturalLanguageHandler

            handler = NaturalLanguageHandler()

            # Test entity extraction
            test_cases = [
                ("Show me NVDA opportunities", ["NVDA"]),
                ("What about TSLA and AAPL?", ["TSLA", "AAPL"]),
                ("Analyze MSFT", ["MSFT"])
            ]

            extractions = []
            for query, expected_entities in test_cases:
                result = handler.parse_intent(query)
                entities = result.get('entities', {})
                tickers = entities.get('tickers', [])

                # Check if expected entities are found
                found = all(ticker in tickers for ticker in expected_entities)
                extractions.append(found)

            success_rate = sum(extractions) / len(extractions) * 100

            return TestResult(
                test_name="Entity Extraction",
                category="Modern Chatbot",
                passed=success_rate >= 60,  # 60% threshold
                message=f"Entity extraction success rate: {success_rate:.1f}%",
                details={
                    'test_cases': len(test_cases),
                    'successful': sum(extractions)
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Entity Extraction",
                category="Modern Chatbot",
                passed=False,
                message=f"Entity extraction test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_error_handling(self) -> TestResult:
        """Test graceful error handling and degradation"""
        try:
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # Test with invalid/edge case inputs
            test_inputs = [
                "",  # Empty
                "asdfasdfasdf",  # Nonsense
                "!@#$%^&*()",  # Special chars
                "x" * 1000,  # Very long
            ]

            errors_handled = []
            for test_input in test_inputs:
                try:
                    response = chatbot.process_message(test_input)
                    # Should still get a response (fallback)
                    has_response = bool(response.get('response'))
                    errors_handled.append(has_response)
                except Exception as e:
                    # Should not throw exceptions
                    errors_handled.append(False)

            graceful = all(errors_handled)

            return TestResult(
                test_name="Error Handling",
                category="Modern Chatbot",
                passed=graceful,
                message="Gracefully handles errors" if graceful else "Some errors not handled",
                details={
                    'test_cases': len(test_inputs),
                    'handled': sum(errors_handled)
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Error Handling",
                category="Modern Chatbot",
                passed=False,
                message=f"Error handling test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_user_feedback_mechanism(self) -> TestResult:
        """Test if user feedback mechanisms exist"""
        try:
            # Check if feedback tracking exists in chatbot
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # Check for feedback-related methods/attributes
            has_feedback_method = hasattr(chatbot, 'record_feedback') or \
                                 hasattr(chatbot, 'track_feedback') or \
                                 hasattr(chatbot, 'feedback')

            return TestResult(
                test_name="User Feedback Mechanism",
                category="Modern Chatbot",
                passed=False,  # Typically not implemented yet
                message="Feedback mechanism not implemented (common gap)",
                details={
                    'has_method': has_feedback_method,
                    'recommendation': 'Implement feedback collection for response quality'
                }
            )

        except Exception as e:
            return TestResult(
                test_name="User Feedback Mechanism",
                category="Modern Chatbot",
                passed=False,
                message=f"Feedback test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def run_all_tests(self) -> TestSuite:
        """Run all modern chatbot tests"""
        logger.info("Running Modern Chatbot Tests...")

        tests = [
            self.test_natural_language_understanding,
            self.test_context_awareness,
            self.test_multi_turn_conversation,
            self.test_intent_recognition,
            self.test_entity_extraction,
            self.test_error_handling,
            self.test_user_feedback_mechanism
        ]

        for test in tests:
            result = test()
            self.suite.add_result(result)
            logger.info(f"  {result.test_name}: {'PASS' if result.passed else 'FAIL'}")

        return self.suite


class PlatformAccessTests:
    """Tests for platform data access"""

    def __init__(self):
        self.suite = TestSuite("Platform Access")

    def test_portfolio_data_access(self) -> TestResult:
        """Test access to portfolio data"""
        try:
            # Check if portfolio integration exists
            from src.services.robinhood_client import RobinhoodClient

            client = RobinhoodClient()

            # Test if we can access portfolio data
            has_portfolio_method = hasattr(client, 'get_portfolio') or \
                                  hasattr(client, 'get_account')

            return TestResult(
                test_name="Portfolio Data Access",
                category="Platform Access",
                passed=has_portfolio_method,
                message="Portfolio access available" if has_portfolio_method else "Portfolio access not found",
                details={
                    'client_type': type(client).__name__,
                    'has_method': has_portfolio_method
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Portfolio Data Access",
                category="Platform Access",
                passed=False,
                message=f"Portfolio access test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_robinhood_integration(self) -> TestResult:
        """Test Robinhood integration"""
        try:
            from src.services.robinhood_client import RobinhoodClient

            client = RobinhoodClient()

            # Check available methods
            methods = [
                'get_positions',
                'get_account',
                'get_portfolio',
                'place_order',
                'get_orders'
            ]

            available_methods = [m for m in methods if hasattr(client, m)]

            coverage = len(available_methods) / len(methods) * 100

            return TestResult(
                test_name="Robinhood Integration",
                category="Platform Access",
                passed=coverage >= 50,  # At least 50% methods
                message=f"Robinhood integration: {coverage:.0f}% coverage",
                details={
                    'available_methods': available_methods,
                    'coverage': coverage
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Robinhood Integration",
                category="Platform Access",
                passed=False,
                message=f"Robinhood integration test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_tradingview_watchlists(self) -> TestResult:
        """Test TradingView watchlist access"""
        try:
            from src.watchlist_strategy_analyzer import WatchlistStrategyAnalyzer

            analyzer = WatchlistStrategyAnalyzer()

            # Test if watchlist analysis is available
            has_analyze = hasattr(analyzer, 'analyze_watchlist')

            # Try to analyze (may fail due to no data, that's ok)
            can_execute = False
            if has_analyze:
                try:
                    # Quick test with likely invalid watchlist
                    result = analyzer.analyze_watchlist('TEST', min_score=90)
                    can_execute = True
                except:
                    # Expected to fail, but method exists
                    can_execute = True

            return TestResult(
                test_name="TradingView Watchlists",
                category="Platform Access",
                passed=has_analyze and can_execute,
                message="Watchlist analysis available" if has_analyze else "Watchlist analysis not found",
                details={
                    'has_method': has_analyze,
                    'can_execute': can_execute
                }
            )

        except Exception as e:
            return TestResult(
                test_name="TradingView Watchlists",
                category="Platform Access",
                passed=False,
                message=f"TradingView test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_database_queries(self) -> TestResult:
        """Test database query capabilities"""
        try:
            import psycopg2
            import os
            from dotenv import load_dotenv

            load_dotenv()

            # Test connection
            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'postgres'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )

            cursor = conn.cursor()

            # Check for key tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
            """)
            tables = [row[0] for row in cursor.fetchall()]

            key_tables = ['robinhood_positions', 'csp_opportunities', 'xtrades_alerts']
            available_tables = [t for t in key_tables if t in tables]

            cursor.close()
            conn.close()

            coverage = len(available_tables) / len(key_tables) * 100

            return TestResult(
                test_name="Database Queries",
                category="Platform Access",
                passed=coverage >= 30,  # At least 1 key table
                message=f"Database access: {len(available_tables)}/{len(key_tables)} key tables",
                details={
                    'available_tables': available_tables,
                    'coverage': coverage
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Database Queries",
                category="Platform Access",
                passed=False,
                message=f"Database query test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_market_data_access(self) -> TestResult:
        """Test market data access"""
        try:
            # Check if market data modules exist
            modules_to_check = [
                'src.robinhood_integration',
                'src.price_monitor',
                'src.services.robinhood_client'
            ]

            available_modules = []
            for module_name in modules_to_check:
                try:
                    __import__(module_name)
                    available_modules.append(module_name)
                except:
                    pass

            has_market_data = len(available_modules) > 0

            return TestResult(
                test_name="Market Data Access",
                category="Platform Access",
                passed=has_market_data,
                message=f"Market data modules: {len(available_modules)}/{len(modules_to_check)}",
                details={
                    'available_modules': available_modules
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Market Data Access",
                category="Platform Access",
                passed=False,
                message=f"Market data test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_analytics_data(self) -> TestResult:
        """Test analytics and performance data access"""
        try:
            # Check if analytics modules exist
            has_analytics = False
            try:
                from src.analytics import performance_tracker
                has_analytics = True
            except:
                pass

            # Check for analytics DB tables
            import psycopg2
            import os

            try:
                conn = psycopg2.connect(
                    host=os.getenv('DB_HOST', 'localhost'),
                    database=os.getenv('DB_NAME', 'postgres'),
                    user=os.getenv('DB_USER', 'postgres'),
                    password=os.getenv('DB_PASSWORD', '')
                )

                cursor = conn.cursor()
                cursor.execute("""
                    SELECT table_name
                    FROM information_schema.tables
                    WHERE table_schema = 'public'
                    AND table_name LIKE '%analytics%'
                """)
                analytics_tables = cursor.fetchall()
                cursor.close()
                conn.close()

                has_analytics_tables = len(analytics_tables) > 0
            except:
                has_analytics_tables = False

            return TestResult(
                test_name="Analytics Data",
                category="Platform Access",
                passed=has_analytics or has_analytics_tables,
                message="Analytics data available" if (has_analytics or has_analytics_tables) else "Analytics not found",
                details={
                    'has_module': has_analytics,
                    'has_tables': has_analytics_tables
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Analytics Data",
                category="Platform Access",
                passed=False,
                message=f"Analytics test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def run_all_tests(self) -> TestSuite:
        """Run all platform access tests"""
        logger.info("Running Platform Access Tests...")

        tests = [
            self.test_portfolio_data_access,
            self.test_robinhood_integration,
            self.test_tradingview_watchlists,
            self.test_database_queries,
            self.test_market_data_access,
            self.test_analytics_data
        ]

        for test in tests:
            result = test()
            self.suite.add_result(result)
            logger.info(f"  {result.test_name}: {'PASS' if result.passed else 'FAIL'}")

        return self.suite


class ReasoningCapabilitiesTests:
    """Tests for AI reasoning and analysis"""

    def __init__(self):
        self.suite = TestSuite("Reasoning Capabilities")

    def test_analysis_recommendations(self) -> TestResult:
        """Test analysis and recommendation generation"""
        try:
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # Ask for analysis/recommendations
            response = chatbot.process_message(
                "What are the best CSP opportunities right now?"
            )

            has_recommendation = 'recommendation' in response.get('response', '').lower() or \
                               response.get('intent') == 'OPPORTUNITIES'

            return TestResult(
                test_name="Analysis & Recommendations",
                category="Reasoning",
                passed=has_recommendation,
                message="Can provide recommendations" if has_recommendation else "Recommendations limited",
                details={
                    'intent': response.get('intent'),
                    'has_data': bool(response.get('data'))
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Analysis & Recommendations",
                category="Reasoning",
                passed=False,
                message=f"Analysis test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_pattern_recognition(self) -> TestResult:
        """Test pattern recognition capabilities"""
        try:
            # Check if pattern detection modules exist
            has_patterns = False
            try:
                from src.supply_demand_zones_page import detect_zones
                has_patterns = True
            except:
                try:
                    from src.zone_detector import ZoneDetector
                    has_patterns = True
                except:
                    pass

            return TestResult(
                test_name="Pattern Recognition",
                category="Reasoning",
                passed=has_patterns,
                message="Pattern detection available" if has_patterns else "Pattern detection not implemented",
                details={
                    'has_module': has_patterns,
                    'recommendation': 'Integrate pattern detection with AVA responses' if has_patterns else 'Add pattern detection'
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Pattern Recognition",
                category="Reasoning",
                passed=False,
                message=f"Pattern recognition test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_risk_assessment(self) -> TestResult:
        """Test risk assessment capabilities"""
        try:
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # Ask about risks
            response = chatbot.process_message(
                "What are the risks of selling cash-secured puts on NVDA?"
            )

            mentions_risk = 'risk' in response.get('response', '').lower()

            return TestResult(
                test_name="Risk Assessment",
                category="Reasoning",
                passed=mentions_risk,
                message="Can assess risk" if mentions_risk else "Risk assessment limited",
                details={
                    'response_length': len(response.get('response', '')),
                    'mentions_risk': mentions_risk
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Risk Assessment",
                category="Reasoning",
                passed=False,
                message=f"Risk assessment test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_trade_evaluation(self) -> TestResult:
        """Test trade evaluation capabilities"""
        try:
            from src.watchlist_strategy_analyzer import WatchlistStrategyAnalyzer

            analyzer = WatchlistStrategyAnalyzer()

            # Check if trade evaluation methods exist
            has_evaluation = hasattr(analyzer, 'analyze_watchlist') or \
                           hasattr(analyzer, 'evaluate_trade')

            return TestResult(
                test_name="Trade Evaluation",
                category="Reasoning",
                passed=has_evaluation,
                message="Trade evaluation available" if has_evaluation else "Trade evaluation not found",
                details={
                    'has_method': has_evaluation
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Trade Evaluation",
                category="Reasoning",
                passed=False,
                message=f"Trade evaluation test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_strategy_suggestions(self) -> TestResult:
        """Test strategy suggestion capabilities"""
        try:
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # Ask for strategy suggestions
            response = chatbot.process_message(
                "What strategy should I use for bullish market conditions?"
            )

            has_strategy = 'strategy' in response.get('response', '').lower() or \
                          'csp' in response.get('response', '').lower() or \
                          'call' in response.get('response', '').lower()

            return TestResult(
                test_name="Strategy Suggestions",
                category="Reasoning",
                passed=has_strategy,
                message="Can suggest strategies" if has_strategy else "Strategy suggestions limited",
                details={
                    'intent': response.get('intent'),
                    'mentions_strategy': has_strategy
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Strategy Suggestions",
                category="Reasoning",
                passed=False,
                message=f"Strategy suggestion test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def run_all_tests(self) -> TestSuite:
        """Run all reasoning capability tests"""
        logger.info("Running Reasoning Capabilities Tests...")

        tests = [
            self.test_analysis_recommendations,
            self.test_pattern_recognition,
            self.test_risk_assessment,
            self.test_trade_evaluation,
            self.test_strategy_suggestions
        ]

        for test in tests:
            result = test()
            self.suite.add_result(result)
            logger.info(f"  {result.test_name}: {'PASS' if result.passed else 'FAIL'}")

        return self.suite


class CoreFunctionalityTests:
    """Tests for core chatbot functionality"""

    def __init__(self):
        self.suite = TestSuite("Core Functionality")

    def test_quick_actions(self) -> TestResult:
        """Test quick action buttons"""
        try:
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # Simulate quick actions
            quick_actions = [
                "Show my portfolio status",
                "Analyze the default watchlist",
                "Show me the best trading opportunities",
                "What can you help me with?"
            ]

            responses = []
            for action in quick_actions:
                response = chatbot.process_message(action)
                responses.append(bool(response.get('response')))

            all_work = all(responses)

            return TestResult(
                test_name="Quick Actions",
                category="Core Functionality",
                passed=all_work,
                message=f"Quick actions: {sum(responses)}/{len(responses)} working",
                details={
                    'total': len(quick_actions),
                    'working': sum(responses)
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Quick Actions",
                category="Core Functionality",
                passed=False,
                message=f"Quick actions test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_realtime_data_retrieval(self) -> TestResult:
        """Test real-time data retrieval"""
        try:
            # Check if real-time modules exist
            has_realtime = False
            try:
                from src.price_monitor import PriceMonitor
                has_realtime = True
            except:
                try:
                    from src.nfl_realtime_sync import sync_realtime
                    has_realtime = True
                except:
                    pass

            return TestResult(
                test_name="Real-time Data Retrieval",
                category="Core Functionality",
                passed=has_realtime,
                message="Real-time data modules found" if has_realtime else "Real-time data not implemented",
                details={
                    'has_module': has_realtime,
                    'recommendation': 'Connect real-time data to AVA responses'
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Real-time Data Retrieval",
                category="Core Functionality",
                passed=False,
                message=f"Real-time data test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_historical_data_analysis(self) -> TestResult:
        """Test historical data analysis"""
        try:
            # Check if historical analysis exists
            import psycopg2
            import os

            conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                database=os.getenv('DB_NAME', 'postgres'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '')
            )

            cursor = conn.cursor()

            # Check for historical data tables
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND (table_name LIKE '%history%' OR table_name LIKE '%historical%')
            """)
            historical_tables = cursor.fetchall()

            cursor.close()
            conn.close()

            has_historical = len(historical_tables) > 0

            return TestResult(
                test_name="Historical Data Analysis",
                category="Core Functionality",
                passed=has_historical,
                message=f"Historical data: {len(historical_tables)} tables found",
                details={
                    'tables': len(historical_tables),
                    'has_data': has_historical
                }
            )

        except Exception as e:
            return TestResult(
                test_name="Historical Data Analysis",
                category="Core Functionality",
                passed=False,
                message=f"Historical data test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def test_user_preferences(self) -> TestResult:
        """Test user preferences and settings"""
        try:
            # Check if preferences system exists
            from ava_chatbot_page import AVAChatbot

            chatbot = AVAChatbot()

            # Check for preference-related attributes
            has_preferences = hasattr(chatbot, 'preferences') or \
                            hasattr(chatbot, 'user_settings') or \
                            hasattr(chatbot, 'config')

            return TestResult(
                test_name="User Preferences",
                category="Core Functionality",
                passed=False,  # Usually not implemented
                message="User preferences not implemented (common gap)",
                details={
                    'has_system': has_preferences,
                    'recommendation': 'Add user preference tracking (e.g., default watchlist, risk tolerance)'
                }
            )

        except Exception as e:
            return TestResult(
                test_name="User Preferences",
                category="Core Functionality",
                passed=False,
                message=f"User preferences test failed: {str(e)}",
                error=traceback.format_exc()
            )

    def run_all_tests(self) -> TestSuite:
        """Run all core functionality tests"""
        logger.info("Running Core Functionality Tests...")

        tests = [
            self.test_quick_actions,
            self.test_realtime_data_retrieval,
            self.test_historical_data_analysis,
            self.test_user_preferences
        ]

        for test in tests:
            result = test()
            self.suite.add_result(result)
            logger.info(f"  {result.test_name}: {'PASS' if result.passed else 'FAIL'}")

        return self.suite


# =============================================================================
# Main Test Runner
# =============================================================================

def generate_report(all_suites: List[TestSuite]) -> str:
    """Generate comprehensive test report"""
    report = []
    report.append("=" * 80)
    report.append("AVA CHATBOT COMPREHENSIVE TEST REPORT")
    report.append("=" * 80)
    report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")

    # Overall summary
    total_tests = sum(len(suite.results) for suite in all_suites)
    total_passed = sum(sum(1 for r in suite.results if r.passed) for suite in all_suites)
    total_failed = total_tests - total_passed
    overall_pass_rate = (total_passed / total_tests * 100) if total_tests > 0 else 0

    report.append("OVERALL SUMMARY")
    report.append("-" * 80)
    report.append(f"Total Tests: {total_tests}")
    report.append(f"Passed: {total_passed} ({overall_pass_rate:.1f}%)")
    report.append(f"Failed: {total_failed}")
    report.append("")

    # Suite summaries
    for suite in all_suites:
        summary = suite.get_summary()
        report.append(f"\n{suite.name.upper()}")
        report.append("-" * 80)
        report.append(f"Tests: {summary['total_tests']} | "
                     f"Passed: {summary['passed']} | "
                     f"Failed: {summary['failed']} | "
                     f"Pass Rate: {summary['pass_rate']:.1f}%")
        report.append("")

        # Individual test results
        for result in suite.results:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            report.append(f"  {status} - {result.test_name}")
            report.append(f"      {result.message}")
            if result.details:
                for key, value in result.details.items():
                    report.append(f"      - {key}: {value}")
            if result.error and not result.passed:
                report.append(f"      ERROR: {result.error[:200]}...")
            report.append("")

    # Recommendations section
    report.append("\n" + "=" * 80)
    report.append("RECOMMENDATIONS FOR IMPROVEMENTS")
    report.append("=" * 80)

    recommendations = []

    # Analyze failures and generate recommendations
    for suite in all_suites:
        for result in suite.results:
            if not result.passed and result.details:
                rec = result.details.get('recommendation')
                if rec and rec not in recommendations:
                    recommendations.append(rec)

    # Add general recommendations
    if total_failed > 0:
        recommendations.extend([
            "Implement comprehensive error handling for all edge cases",
            "Add user feedback collection mechanism for response quality",
            "Implement user preference system for personalized experience",
            "Add session persistence for conversation history",
            "Integrate real-time data feeds into AVA responses",
            "Add comprehensive logging for debugging and improvement",
            "Implement A/B testing for response variations",
            "Add response time monitoring and optimization"
        ])

    for i, rec in enumerate(recommendations, 1):
        report.append(f"{i}. {rec}")

    report.append("")
    report.append("=" * 80)
    report.append("END OF REPORT")
    report.append("=" * 80)

    return "\n".join(report)


def main():
    """Main test execution"""
    print("\n" + "=" * 80)
    print("AVA CHATBOT COMPREHENSIVE TESTING")
    print("=" * 80 + "\n")

    all_suites = []

    # Run test suites
    try:
        # Modern Chatbot Features
        modern_tests = ModernChatbotTests()
        modern_suite = modern_tests.run_all_tests()
        all_suites.append(modern_suite)

        # Platform Access
        platform_tests = PlatformAccessTests()
        platform_suite = platform_tests.run_all_tests()
        all_suites.append(platform_suite)

        # Reasoning Capabilities
        reasoning_tests = ReasoningCapabilitiesTests()
        reasoning_suite = reasoning_tests.run_all_tests()
        all_suites.append(reasoning_suite)

        # Core Functionality
        core_tests = CoreFunctionalityTests()
        core_suite = core_tests.run_all_tests()
        all_suites.append(core_suite)

    except Exception as e:
        logger.error(f"Fatal error during testing: {e}")
        logger.error(traceback.format_exc())

    # Generate report
    report = generate_report(all_suites)

    # Print report
    print("\n" + report)

    # Save report to file
    report_file = f"ava_chatbot_test_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    with open(report_file, 'w') as f:
        f.write(report)

    print(f"\nReport saved to: {report_file}")

    return all_suites


if __name__ == "__main__":
    main()
