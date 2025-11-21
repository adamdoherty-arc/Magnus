"""
AVA Financial Assistant Chatbot - Interactive Chat Interface
============================================================

Full-featured chatbot interface for AVA Trading Platform.
AVA can answer questions about the platform, analyze watchlists, and provide trading insights.

Features:
- Natural language conversation with AVA
- Watchlist analysis and strategy recommendations
- AVA platform knowledge (features, code, usage)
- Trading insights and market analysis
- Session history and context retention
- Free local LLM support (Ollama integration)

Author: AVA Trading Platform
Created: 2025-11-11
"""

import streamlit as st
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json

# Magnus imports
from src.ava.nlp_handler import NaturalLanguageHandler
from src.ava.enhanced_project_handler import integrate_with_ava, EnhancedProjectHandler
from src.watchlist_strategy_analyzer import WatchlistStrategyAnalyzer
from src.services.llm_service import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# PERFORMANCE: Cached AVA chatbot instance - singleton pattern
@st.cache_resource
def get_ava_chatbot():
    """Cached AVA chatbot instance"""
    return AVAChatbot()

# PERFORMANCE: Cached watchlist analyzer - singleton pattern
@st.cache_resource
def get_watchlist_analyzer():
    """Cached watchlist strategy analyzer"""
    from src.watchlist_strategy_analyzer import WatchlistStrategyAnalyzer
    return WatchlistStrategyAnalyzer()

class AVAChatbot:
    """AVA chatbot with enhanced capabilities"""

    def __init__(self):
        """Initialize AVA with all capabilities"""
        # Initialize AVA NLP handler
        self.ava = NaturalLanguageHandler()

        # Enhance with project knowledge
        self.ava = integrate_with_ava(self.ava)

        # Initialize watchlist analyzer
        self.watchlist_analyzer = WatchlistStrategyAnalyzer()

        # Initialize LLM service for conversational responses
        self.llm_service = LLMService()

        logger.info("AVA chatbot initialized successfully")

    def process_message(self, user_message: str, context: Optional[Dict] = None) -> Dict:
        """
        Process user message and generate response

        Args:
            user_message: User's input message
            context: Optional conversation context

        Returns:
            Dictionary with response and metadata
        """
        logger.info(f"Processing message: {user_message}")

        try:
            # Check for watchlist analysis requests
            if self._is_watchlist_analysis_request(user_message):
                return self._handle_watchlist_analysis(user_message)

            # Check for strategy ranking requests
            if self._is_strategy_ranking_request(user_message):
                return self._handle_strategy_ranking(user_message)

            # Use AVA's NLP handler for intent detection
            intent_result = self.ava.parse_intent(user_message, context)

            # Handle different intents
            if intent_result['intent'] == 'PROJECT_QUESTION':
                # AVA already generated answer for project questions
                return {
                    'response': intent_result['response_hint'],
                    'intent': 'PROJECT_QUESTION',
                    'sources': intent_result.get('sources', []),
                    'confidence': intent_result.get('confidence', 0.8)
                }

            elif intent_result['intent'] == 'PORTFOLIO':
                return self._handle_portfolio_query(intent_result)

            elif intent_result['intent'] == 'POSITIONS':
                return self._handle_positions_query(intent_result)

            elif intent_result['intent'] == 'OPPORTUNITIES':
                return self._handle_opportunities_query(intent_result)

            else:
                # General conversation - use LLM
                return self._handle_general_conversation(user_message, context)

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                'response': f"I encountered an error processing your request: {str(e)}",
                'intent': 'ERROR',
                'confidence': 0.0
            }

    def _is_watchlist_analysis_request(self, message: str) -> bool:
        """Detect watchlist analysis requests"""
        keywords = ['analyze watchlist', 'watchlist analysis', 'analyze stocks', 'scan watchlist']
        return any(keyword in message.lower() for keyword in keywords)

    def _is_strategy_ranking_request(self, message: str) -> bool:
        """Detect strategy ranking requests"""
        keywords = ['rank strategies', 'best strategies', 'top strategies', 'rank trades']
        return any(keyword in message.lower() for keyword in keywords)

    def _handle_watchlist_analysis(self, message: str) -> Dict:
        """Handle watchlist analysis requests"""
        # Extract watchlist name from message
        watchlist_name = self._extract_watchlist_name(message)

        if not watchlist_name:
            return {
                'response': "Which watchlist would you like me to analyze? Please specify the watchlist name.",
                'intent': 'CLARIFICATION_NEEDED',
                'confidence': 0.9
            }

        logger.info(f"Analyzing watchlist: {watchlist_name}")

        # Perform analysis
        try:
            analyses = self.watchlist_analyzer.analyze_watchlist(
                watchlist_name=watchlist_name,
                min_score=60.0,
                strategies=['CSP', 'CC']
            )

            if not analyses:
                return {
                    'response': f"I couldn't find any strategies above score 60 for the '{watchlist_name}' watchlist. This could mean:\n\n"
                                f"1. The watchlist doesn't exist\n"
                                f"2. No stocks meet the minimum quality criteria\n"
                                f"3. Market conditions aren't favorable right now\n\n"
                                f"Try checking the TradingView watchlists page or lowering the score threshold.",
                    'intent': 'WATCHLIST_ANALYSIS',
                    'confidence': 0.8
                }

            # Format results
            formatted_results = self.watchlist_analyzer.format_results(analyses, limit=10)

            return {
                'response': f"# Watchlist Analysis: {watchlist_name}\n\n{formatted_results}",
                'intent': 'WATCHLIST_ANALYSIS',
                'data': [a.__dict__ for a in analyses],
                'confidence': 0.95
            }

        except Exception as e:
            logger.error(f"Error analyzing watchlist: {e}")
            return {
                'response': f"I encountered an error analyzing the watchlist: {str(e)}",
                'intent': 'ERROR',
                'confidence': 0.5
            }

    def _handle_strategy_ranking(self, message: str) -> Dict:
        """Handle strategy ranking requests"""
        # Similar to watchlist analysis but focuses on ranking
        watchlist_name = self._extract_watchlist_name(message)

        if not watchlist_name:
            watchlist_name = 'default'  # Use default watchlist

        try:
            analyses = self.watchlist_analyzer.analyze_watchlist(
                watchlist_name=watchlist_name,
                min_score=50.0,  # Lower threshold for ranking
                strategies=['CSP', 'CC', 'Calendar', 'Iron Condor']
            )

            if not analyses:
                return {
                    'response': "No strategies found to rank. Try analyzing a specific watchlist.",
                    'intent': 'STRATEGY_RANKING',
                    'confidence': 0.7
                }

            # Sort by profit score and format
            top_10 = analyses[:10]

            response = f"# Top 10 Strategies Ranked by Profit Potential\n\n"

            for i, analysis in enumerate(top_10, 1):
                response += f"**{i}. {analysis.ticker} - {analysis.strategy_type}** (Score: {analysis.profit_score:.1f})\n"
                response += f"   {analysis.trade_details}\n"
                response += f"   Expected Premium: ${analysis.expected_premium:.0f} | "
                response += f"Probability: {analysis.probability_profit:.0f}% | "
                response += f"Recommendation: {analysis.recommendation}\n\n"

            return {
                'response': response,
                'intent': 'STRATEGY_RANKING',
                'data': [a.__dict__ for a in top_10],
                'confidence': 0.95
            }

        except Exception as e:
            logger.error(f"Error ranking strategies: {e}")
            return {
                'response': f"Error ranking strategies: {str(e)}",
                'intent': 'ERROR',
                'confidence': 0.5
            }

    def _extract_watchlist_name(self, message: str) -> Optional[str]:
        """Extract watchlist name from message"""
        # Common patterns
        patterns = [
            'analyze ',
            'watchlist ',
            'scan ',
            'check ',
            'the ',
            'my '
        ]

        message_lower = message.lower()

        for pattern in patterns:
            if pattern in message_lower:
                # Extract word after pattern
                parts = message_lower.split(pattern)
                if len(parts) > 1:
                    # Get first word after pattern
                    name = parts[1].split()[0] if parts[1].split() else None
                    if name:
                        # Clean up
                        name = name.strip('.,!?').upper()
                        return name

        # Check for specific tickers mentioned (like NVDA, TSLA, etc.)
        words = message.upper().split()
        for word in words:
            # Check if it looks like a ticker (2-5 uppercase letters)
            if word.isalpha() and 2 <= len(word) <= 5:
                return word

        return None

    def _handle_portfolio_query(self, intent_result: Dict) -> Dict:
        """Handle portfolio-related queries"""
        # This would integrate with Robinhood portfolio data
        return {
            'response': "To check your portfolio, navigate to the Dashboard or Positions page. "
                       "I can analyze specific positions if you tell me which ones you're interested in.",
            'intent': 'PORTFOLIO',
            'confidence': 0.8
        }

    def _handle_positions_query(self, intent_result: Dict) -> Dict:
        """Handle positions-related queries"""
        return {
            'response': "You can view all your live positions on the Positions page. "
                       "Would you like me to analyze any specific position or strategy?",
            'intent': 'POSITIONS',
            'confidence': 0.8
        }

    def _handle_opportunities_query(self, intent_result: Dict) -> Dict:
        """Handle opportunities-related queries"""
        return {
            'response': "To find new opportunities, I can analyze watchlists for you! "
                       "Try: 'Analyze the NVDA watchlist' or 'Show me the best CSP opportunities'",
            'intent': 'OPPORTUNITIES',
            'confidence': 0.8
        }

    def _handle_general_conversation(self, message: str, context: Optional[Dict]) -> Dict:
        """Handle general conversation using LLM"""
        try:
            # Build context-aware prompt
            prompt = f"""You are AVA, the financial assistant for Magnus Trading Dashboard.

User message: {message}

Respond conversationally and helpfully. If the user asks about trading strategies, provide insights.
If they ask about Magnus features, explain them. Keep responses concise and actionable.

Response:"""

            # Generate response using free LLM
            llm_response = self.llm_service.generate(
                prompt=prompt,
                max_tokens=400,
                temperature=0.7,
                use_cache=True
            )

            return {
                'response': llm_response['text'],
                'intent': 'GENERAL_CONVERSATION',
                'model': f"{llm_response['provider']}/{llm_response['model']}",
                'confidence': 0.75
            }

        except Exception as e:
            logger.error(f"Error in general conversation: {e}")
            return {
                'response': "I'm here to help! You can ask me about:\n"
                           "- Analyzing watchlists for trading opportunities\n"
                           "- Magnus features and how to use them\n"
                           "- Trading strategies and recommendations\n"
                           "- Your portfolio and positions\n\n"
                           "What would you like to know?",
                'intent': 'FALLBACK',
                'confidence': 0.6
            }


def show_ava_chatbot_page():
    """Main Streamlit page for AVA chatbot"""

    # FORCE CSS RELOAD WITH TIMESTAMP
    import time
    cache_buster = int(time.time())

    # Custom CSS for improved chatbot interface - VERSION 3.0 GLASSMORPHISM OVERLAY
    css_styles = f"""<style>
    /* MODERN GLASSMORPHISM LAYOUT - v3.0 */
    /* Cache-buster: {cache_buster} */

    /* Tighter chat interface */
    .stChatMessage {{
        padding: 0.3rem !important;
        margin: 0.2rem 0 !important;
    }}

    /* Bordered chat container */
    [data-testid="stChatMessageContainer"] {{
        border: 2px solid #e0e0e0;
        border-radius: 8px;
        padding: 0.5rem;
        background-color: #fafafa;
        margin-bottom: 0.5rem;
    }}

    /* Hide default separators */
    hr {{
        display: none !important;
    }}

    /* Tighter sidebar */
    section[data-testid="stSidebar"] > div {{
        padding-top: 1rem;
    }}

    /* Compact image styling */
    [data-testid="stImage"] img {{
        border-radius: 12px !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15) !important;
    }}

    /* Text input - glassmorphism style */
    .stTextInput input {{
        background: rgba(255, 255, 255, 0.95) !important;
        backdrop-filter: blur(10px) !important;
        -webkit-backdrop-filter: blur(10px) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        font-size: 0.9rem !important;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }}

    .stTextInput input:focus {{
        background: rgba(255, 255, 255, 1) !important;
        border-color: #667eea !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.25) !important;
        outline: none !important;
    }}

    /* Send button styling */
    .stButton > button[kind="primary"] {{
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.7rem 1rem !important;
        font-size: 1.2rem !important;
        font-weight: bold !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(102, 126, 234, 0.4) !important;
        transition: all 0.3s ease !important;
        min-width: 50px !important;
    }}

    .stButton > button[kind="primary"]:hover {{
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 16px rgba(102, 126, 234, 0.5) !important;
    }}

    /* Quick actions container */
    .quick-actions-box {{
        background: #f8f9fa;
        border-radius: 8px;
        padding: 0.6rem;
        margin-bottom: 0.3rem;
        border: 1px solid #e0e0e0;
    }}

    /* Reduce overall spacing - 70% reduction */
    .element-container {{
        margin-bottom: 0.15rem !important;
    }}

    h1, h2, h3 {{
        margin-top: 0.15rem !important;
        margin-bottom: 0.15rem !important;
    }}

    /* Make everything more compact */
    .block-container {{
        padding-top: 0.5rem !important;
        padding-bottom: 0.5rem !important;
    }}

    /* Reduce button padding */
    .stButton button:not([kind="primary"]) {{
        padding: 0.3rem 0.6rem !important;
        font-size: 0.85rem !important;
    }}

    /* Hide labels for cleaner look */
    .glass-input-overlay label {{
        display: none !important;
    }}
    </style>"""

    st.markdown(css_styles, unsafe_allow_html=True)

    # PERFORMANCE: Initialize chatbot with cached singleton
    if 'ava_chatbot' not in st.session_state:
        with st.spinner("Initializing AVA..."):
            st.session_state.ava_chatbot = get_ava_chatbot()

    # Initialize chat history
    if 'messages' not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant",
                "content": "👋 Hi! I'm AVA. Ask me to analyze watchlists, rank strategies, or answer questions about Magnus."
            }
        ]

    # Compact header with version indicator
    st.markdown("# 🤖 AVA")
    st.caption(f"v3.0-COMPACT | Cache: {cache_buster}")

    # OBVIOUS VISUAL INDICATOR - Can't be missed!
    st.markdown("""
        <div style="
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 15px;
            border-radius: 10px;
            text-align: center;
            font-size: 20px;
            font-weight: bold;
            margin: 10px 0 20px 0;
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        ">
            ✨ UPDATED COMPACT LAYOUT ✨
        </div>
    """, unsafe_allow_html=True)

    # Create two-column layout for better space management
    left_col, right_col = st.columns([1, 1])

    with left_col:
        # Show AVA avatar - COMPACT at top with AUTO-ROTATION
        from pathlib import Path
        import glob
        import random

        # Get all images from AnnaA folder
        image_folder = Path(r"C:\Code\Legion\repos\ava\docs\ava\AnnaA")
        image_files = sorted([f for f in image_folder.glob("*.jpg") if f.is_file()])

        # If no images found, fallback to default
        if not image_files:
            image_files = [Path("assets/ava/ava_main.jpg")]

        # Get current time for rotation (changes every 15 minutes)
        now = datetime.now()
        # Calculate 15-minute intervals: 0, 15, 30, 45
        interval_15min = (now.hour * 4) + (now.minute // 15)

        # Select image based on 15-minute intervals or manual selection
        if 'manual_image_index' in st.session_state:
            # Use manually selected index
            image_index = st.session_state.manual_image_index
            mode_text = f"Manual: {image_index + 1}/{len(image_files)}"
        else:
            # Use time-based automatic rotation
            image_index = interval_15min % len(image_files)
            next_change = ((now.minute // 15) + 1) * 15
            if next_change == 60:
                next_change_text = f"{(now.hour + 1) % 24}:00"
            else:
                next_change_text = f"{now.hour}:{next_change:02d}"
            mode_text = f"Auto: {image_index + 1}/{len(image_files)} • Next: {next_change_text}"

        avatar_path = image_files[image_index]

        # Create compact container with image
        st.markdown('<div style="max-width: 150px; margin: 0 auto;">', unsafe_allow_html=True)

        if avatar_path.exists():
            # Display image using Streamlit
            st.image(str(avatar_path), use_container_width=True)
            st.caption(f"🕐 {mode_text}")
        else:
            st.markdown("### 🤖")

        st.markdown('</div>', unsafe_allow_html=True)

        # Add manual refresh button below image
        if st.button("🔄 Next Image", key="refresh_avatar", help="Cycle to next image", use_container_width=True):
            # Rotate to next image manually
            if 'manual_image_index' not in st.session_state:
                st.session_state.manual_image_index = image_index
            st.session_state.manual_image_index = (st.session_state.manual_image_index + 1) % len(image_files)
            st.rerun()

        # Reset to auto mode button
        if 'manual_image_index' in st.session_state:
            if st.button("⏱️ Auto Mode", key="auto_mode", help="Return to automatic rotation", use_container_width=True):
                del st.session_state.manual_image_index
                st.rerun()

        # Chat input RIGHT BELOW image with glassmorphism style
        st.markdown('<div style="max-width: 200px; margin: -20px auto 5px auto; position: relative; z-index: 10;">', unsafe_allow_html=True)

        # Input and send button in one row
        input_col, btn_col = st.columns([4, 1])
        with input_col:
            chat_input_text = st.text_input(
                "Message",
                placeholder="Type...",
                label_visibility="collapsed",
                key="user_message_input"
            )
        with btn_col:
            send_clicked = st.button("➤", key="send_button", help="Send", type="primary")

        st.markdown('</div>', unsafe_allow_html=True)

        # Process message if sent
        if (send_clicked or chat_input_text) and chat_input_text:
            if 'last_msg' not in st.session_state or st.session_state.last_msg != chat_input_text:
                st.session_state.messages.append({"role": "user", "content": chat_input_text})
                st.session_state.last_msg = chat_input_text

                # Generate response
                response_data = st.session_state.ava_chatbot.process_message(
                    user_message=chat_input_text,
                    context={'history': st.session_state.messages[-5:], 'timestamp': datetime.now().isoformat()}
                )
                st.session_state.messages.append({"role": "assistant", "content": response_data['response']})
                st.rerun()

    with right_col:
        # Quick actions in right column
        st.markdown('<div class="quick-actions-box">', unsafe_allow_html=True)
        st.markdown("**⚡ Quick Actions:**")

        col1, col2 = st.columns(2)
        with col1:
            if st.button("📊 Portfolio", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Show my portfolio status"})
                st.rerun()

            if st.button("💡 Opportunities", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Show me the best trading opportunities"})
                st.rerun()

        with col2:
            if st.button("📝 Watchlist", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "Analyze the default watchlist"})
                st.rerun()

            if st.button("❓ Help", use_container_width=True):
                st.session_state.messages.append({"role": "user", "content": "What can you help me with?"})
                st.rerun()

        st.markdown('</div>', unsafe_allow_html=True)

        # Conversation history below quick actions
        st.markdown("**💬 Conversation:**")

        # Display in scrollable container
        if st.session_state.messages:
            for message in st.session_state.messages:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        else:
            st.info("👋 Start a conversation using the input on the left or quick actions above!")

    # Settings sidebar
    with st.sidebar:
        st.subheader("⚙️ Settings")
        model_option = st.selectbox(
            "Model",
            ["Auto (Free)", "Ollama", "GPT-4", "Claude"],
            label_visibility="collapsed"
        )

        st.markdown("---")

        if st.button("🗑️ Clear Chat", use_container_width=True):
            st.session_state.messages = [
                {
                    "role": "assistant",
                    "content": "Chat cleared. How can I help?"
                }
            ]
            st.rerun()


# Run page
if __name__ == "__main__":
    show_ava_chatbot_page()
