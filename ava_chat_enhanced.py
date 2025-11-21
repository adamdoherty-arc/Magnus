"""
AVA - Enhanced Chat Experience
================================

Modern, beautiful chatbot interface with:
- Sleek dark theme UI
- Real-time conversational AI
- Voice input/output capability
- Quick action buttons
- Context-aware responses
- Portfolio integration
- Watchlist analysis
- Trading insights

Author: AVA Trading Platform
Created: 2025-11-12
"""

import streamlit as st
import logging
from datetime import datetime
from typing import Dict, List, Optional
import json
from pathlib import Path

# AVA imports
from src.ava.nlp_handler import NaturalLanguageHandler
from src.ava.enhanced_project_handler import integrate_with_ava, EnhancedProjectHandler
from src.ava.ava_visual import AvaVisual, AvaExpression
from src.ava.conversation_memory_manager import ConversationMemoryManager
from src.watchlist_strategy_analyzer import WatchlistStrategyAnalyzer
from src.services.llm_service import LLMService

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page config
st.set_page_config(
    page_title="AVA - Your Expert Trading Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Enhanced CSS for modern chatbot experience
st.markdown("""
<style>
    /* Dark theme background */
    .stApp {
        background: linear-gradient(135deg, #1a1a2e 0%, #16213e 100%);
    }

    /* Header styling */
    .ava-header {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        padding: 2rem;
        border-radius: 15px;
        margin-bottom: 2rem;
        box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
        text-align: center;
    }

    .ava-title {
        font-size: 2.5rem;
        font-weight: 700;
        color: #ffffff;
        margin: 0;
        text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.5);
    }

    .ava-subtitle {
        font-size: 1.1rem;
        color: #a0a0a0;
        margin-top: 0.5rem;
    }

    /* Avatar styling */
    .ava-avatar {
        border-radius: 50%;
        border: 4px solid #ffffff;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.4);
        margin: 0 auto 1rem auto;
        display: block;
    }

    /* Chat container */
    .chat-container {
        background: rgba(255, 255, 255, 0.05);
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Message bubbles */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 5px 20px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: right;
        clear: both;
        box-shadow: 0 2px 10px rgba(102, 126, 234, 0.3);
    }

    .ava-message {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
        color: white;
        padding: 1rem 1.5rem;
        border-radius: 20px 20px 20px 5px;
        margin: 0.5rem 0;
        max-width: 80%;
        float: left;
        clear: both;
        border: 1px solid rgba(255, 255, 255, 0.1);
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
    }

    /* Quick action buttons */
    .quick-action-btn {
        background: rgba(102, 126, 234, 0.2);
        border: 1px solid #667eea;
        color: #667eea;
        padding: 0.5rem 1rem;
        border-radius: 20px;
        margin: 0.3rem;
        cursor: pointer;
        transition: all 0.3s ease;
        display: inline-block;
    }

    .quick-action-btn:hover {
        background: #667eea;
        color: white;
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }

    /* Input area - styled as a proper text box */
    .stTextInput input {
        background: rgba(255, 255, 255, 0.95) !important;
        border: 2px solid rgba(102, 126, 234, 0.3) !important;
        color: #1a1a2e !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        font-size: 1.05rem !important;
        box-shadow: 0 2px 10px rgba(0, 0, 0, 0.1) !important;
        transition: all 0.3s ease !important;
    }

    .stTextInput input:focus {
        border-color: #667eea !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.2) !important;
        outline: none !important;
    }

    .stTextInput input::placeholder {
        color: rgba(26, 26, 46, 0.5) !important;
    }

    /* Send button - positioned to the right */
    .stButton button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
        border-radius: 12px !important;
        padding: 1rem 1.5rem !important;
        font-weight: 600 !important;
        font-size: 1rem !important;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3) !important;
        transition: all 0.3s ease !important;
        height: 100% !important;
        min-height: 3.5rem !important;
    }

    .stButton button:hover {
        transform: translateY(-2px) !important;
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.5) !important;
        background: linear-gradient(135deg, #764ba2 0%, #667eea 100%) !important;
    }

    .stButton button:active {
        transform: translateY(0px) !important;
    }

    /* Chat input container */
    .chat-input-container {
        display: flex;
        gap: 0.75rem;
        align-items: center;
        padding: 1rem;
        background: rgba(255, 255, 255, 0.05);
        border-radius: 15px;
        backdrop-filter: blur(10px);
        border: 1px solid rgba(255, 255, 255, 0.1);
    }

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(135deg, #0f3460 0%, #16213e 100%);
    }

    /* Status indicators */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 0.5rem;
    }

    .status-online {
        background: #4ade80;
        box-shadow: 0 0 10px #4ade80;
    }

    .status-thinking {
        background: #fbbf24;
        box-shadow: 0 0 10px #fbbf24;
        animation: pulse 1.5s ease-in-out infinite;
    }

    @keyframes pulse {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
</style>
""", unsafe_allow_html=True)


class AVAChatInterface:
    """Enhanced AVA Chat Interface"""

    def __init__(self):
        """Initialize AVA chat interface"""
        # Initialize session state
        if 'messages' not in st.session_state:
            st.session_state.messages = []

        if 'ava_nlp' not in st.session_state:
            st.session_state.ava_nlp = self._initialize_ava()

        if 'conversation_memory' not in st.session_state:
            st.session_state.conversation_memory = ConversationMemoryManager()

        logger.info("AVA Chat Interface initialized")

    def _initialize_ava(self):
        """Initialize AVA NLP handler"""
        try:
            ava = NaturalLanguageHandler()
            ava = integrate_with_ava(ava)
            logger.info("AVA NLP initialized successfully")
            return ava
        except Exception as e:
            logger.error(f"Error initializing AVA: {e}")
            return None

    def show_header(self):
        """Display enhanced header with AVA avatar"""
        st.markdown("""
        <div class="ava-header">
            <h1 class="ava-title">🤖 AVA - Your Expert Trading Assistant</h1>
            <p class="ava-subtitle">Ask me anything! I'll ask clarifying questions to help you get exactly what you need.</p>
        </div>
        """, unsafe_allow_html=True)

        # Show AVA avatar
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            avatar_path = Path("assets/ava/ava_main.jpg")
            if avatar_path.exists():
                st.image(str(avatar_path), width=200, use_container_width=False)
            else:
                st.markdown("## 🤖", unsafe_allow_html=True)

    def show_quick_actions(self):
        """Display quick action buttons"""
        st.markdown("### Quick Actions:")

        col1, col2, col3, col4 = st.columns(4)

        quick_actions = [
            ("📊 Portfolio", "Show my portfolio status"),
            ("📈 Analyze", "Analyze my watchlist"),
            ("💡 Help", "What can you help me with?"),
            ("🔍 About", "Tell me about AVA")
        ]

        for idx, (label, query) in enumerate(quick_actions):
            col = [col1, col2, col3, col4][idx]
            with col:
                if st.button(label, key=f"quick_action_{idx}", use_container_width=True):
                    self.process_user_message(query)

    def show_chat_history(self):
        """Display chat message history"""
        st.markdown('<div class="chat-container">', unsafe_allow_html=True)

        for message in st.session_state.messages:
            if message["role"] == "user":
                st.markdown(f'<div class="user-message">{message["content"]}</div><br>', unsafe_allow_html=True)
            else:
                st.markdown(f'<div class="ava-message">{message["content"]}</div><br>', unsafe_allow_html=True)

        st.markdown('</div>', unsafe_allow_html=True)

    def process_user_message(self, user_message: str):
        """Process user message and generate AVA response"""
        if not user_message.strip():
            return

        # Add user message to history
        st.session_state.messages.append({"role": "user", "content": user_message})

        # Show thinking indicator
        with st.spinner("AVA is thinking..."):
            try:
                if st.session_state.ava_nlp:
                    # Get conversation context
                    context = st.session_state.conversation_memory.get_context()

                    # Parse intent
                    result = st.session_state.ava_nlp.parse_intent(user_message, context)

                    # Generate response
                    response = self._generate_response(result, user_message)

                    # Update conversation memory
                    st.session_state.conversation_memory.add_exchange(user_message, response)
                else:
                    response = "I'm sorry, I'm having trouble initializing. Please refresh the page."

                # Add AVA response to history
                st.session_state.messages.append({"role": "assistant", "content": response})

            except Exception as e:
                logger.error(f"Error processing message: {e}")
                error_response = f"I encountered an error: {str(e)}. Please try again."
                st.session_state.messages.append({"role": "assistant", "content": error_response})

    def _generate_response(self, intent_result: Dict, user_message: str) -> str:
        """Generate appropriate response based on intent"""
        intent = intent_result.get('intent', 'GENERAL')

        # Handle different intents
        if intent == 'PROJECT_QUESTION':
            return intent_result.get('response_hint', 'I can help with that!')

        elif intent == 'PORTFOLIO':
            return "📊 Let me check your portfolio status...\n\nTo provide accurate information, I need access to your live portfolio data. Please make sure you're connected to your trading account."

        elif intent == 'POSITIONS':
            return "📈 I'll analyze your current positions...\n\nWould you like me to:\n- Show all positions\n- Analyze specific positions\n- Suggest adjustments?"

        elif intent == 'OPPORTUNITIES':
            return "💡 Looking for trading opportunities...\n\nWhat type of opportunities are you interested in?\n- Cash-secured puts\n- Covered calls\n- Calendar spreads"

        elif intent == 'WATCHLIST':
            return "👀 I can help with watchlist analysis!\n\nWhich watchlist would you like me to analyze?\n- All watchlists\n- Specific watchlist\n- Top opportunities"

        else:
            # General conversation
            return self._generate_general_response(user_message)

    def _generate_general_response(self, message: str) -> str:
        """Generate general conversational response"""
        # Common queries
        if any(word in message.lower() for word in ['hello', 'hi', 'hey']):
            return "👋 Hello! I'm AVA, your expert trading assistant. How can I help you today?"

        elif any(word in message.lower() for word in ['help', 'what can you do', 'capabilities']):
            return """I can help you with:

📊 **Portfolio Management**
- View portfolio status and balance
- Track performance and P&L

📈 **Position Analysis**
- Analyze current positions
- Suggest adjustments and rolls
- Calculate Greeks and risk metrics

💡 **Trading Opportunities**
- Find cash-secured put opportunities
- Identify covered call candidates
- Analyze calendar spreads

👀 **Watchlist Management**
- Analyze watchlists for best opportunities
- Rank stocks by strategy suitability
- Monitor alerts from followed traders

🔍 **Market Research**
- Answer questions about the platform
- Provide trading insights
- Explain strategies

What would you like to explore?"""

        elif 'about' in message.lower() or 'who are you' in message.lower():
            return """I'm AVA (Advanced Virtual Assistant) - your expert trading assistant for options trading with the Wheel Strategy.

I'm powered by advanced AI and have deep knowledge of:
- Options trading strategies
- Portfolio management
- Technical analysis
- Risk management
- Market data analysis

I'm here to help you make better trading decisions by providing insights, analysis, and recommendations based on your portfolio and market conditions.

What would you like to know?"""

        else:
            # Use LLM for general conversation
            return f"I understand you're asking about '{message}'. Could you provide more details so I can give you the best answer?"

    def show_chat_input(self):
        """Display chat input area with text box and send button"""
        # Wrapper with better styling
        st.markdown('<div class="chat-input-container">', unsafe_allow_html=True)

        # Create columns for input and button
        col1, col2 = st.columns([5, 1])

        with col1:
            user_input = st.text_input(
                "Message",
                placeholder="Type your message and press Enter...",
                label_visibility="collapsed",
                key="chat_input"
            )

        with col2:
            send_button = st.button("➤ Send", use_container_width=True, type="primary")

        st.markdown('</div>', unsafe_allow_html=True)

        # Handle sending message - works with both button click and Enter key
        if user_input and (send_button or user_input):
            # Check if this is a new message (not already processed)
            if 'last_processed_message' not in st.session_state or st.session_state.last_processed_message != user_input:
                self.process_user_message(user_input)
                st.session_state.last_processed_message = user_input
                st.rerun()

    def show_sidebar(self):
        """Display sidebar with settings and info"""
        with st.sidebar:
            st.markdown("### 🤖 AVA Status")

            # Status indicator
            if st.session_state.ava_nlp:
                st.markdown('<span class="status-indicator status-online"></span> Online', unsafe_allow_html=True)
            else:
                st.markdown('<span class="status-indicator" style="background: #ef4444;"></span> Offline', unsafe_allow_html=True)

            st.markdown("---")

            # Settings
            st.markdown("### ⚙️ Settings")

            # Voice toggle
            voice_enabled = st.checkbox("🎤 Voice Input", value=False)

            # Auto-scroll
            auto_scroll = st.checkbox("📜 Auto-scroll", value=True)

            # Theme
            st.markdown("### 🎨 Theme")
            theme = st.selectbox("Select theme:", ["Dark (Default)", "Light", "Auto"])

            st.markdown("---")

            # Stats
            st.markdown("### 📊 Session Stats")
            st.metric("Messages", len(st.session_state.messages))

            if st.session_state.messages:
                first_message = st.session_state.messages[0]
                st.caption(f"Started: Just now")

            st.markdown("---")

            # Actions
            if st.button("🗑️ Clear Chat", use_container_width=True):
                st.session_state.messages = []
                st.session_state.conversation_memory = ConversationMemoryManager()
                st.rerun()

            if st.button("📥 Export Chat", use_container_width=True):
                # Export chat history
                chat_export = json.dumps(st.session_state.messages, indent=2)
                st.download_button(
                    "Download JSON",
                    chat_export,
                    file_name=f"ava_chat_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                    mime="application/json"
                )


def main():
    """Main application"""
    # Initialize chat interface
    chat = AVAChatInterface()

    # Show sidebar
    chat.show_sidebar()

    # Create two-column layout for better space management
    left_col, right_col = st.columns([1, 1])

    with left_col:
        # Show header in left column
        st.markdown("""
        <div class="ava-header">
            <h1 class="ava-title">🤖 AVA</h1>
            <p class="ava-subtitle">Your Expert Trading Assistant</p>
        </div>
        """, unsafe_allow_html=True)

        # Show AVA avatar - 70% size for better proportion
        avatar_path = Path("assets/ava/ava_main.jpg")
        if avatar_path.exists():
            st.image(str(avatar_path), use_container_width=True)
        else:
            st.markdown("## 🤖", unsafe_allow_html=True)

        # Add spacing
        st.markdown("<div style='margin-bottom: 1rem;'></div>", unsafe_allow_html=True)

        # Chat input positioned 30% up from image (right after it)
        chat.show_chat_input()

    with right_col:
        # Quick actions in right column
        st.markdown("### ⚡ Quick Actions:")
        chat.show_quick_actions()

        st.markdown("---")

        # Show chat history or welcome message
        if st.session_state.messages:
            st.markdown("### 💬 Conversation:")
            chat.show_chat_history()
        else:
            st.markdown("""
            <div class="chat-container" style="text-align: center; padding: 2rem;">
                <h3 style="color: #a0a0a0;">👋 Welcome!</h3>
                <p style="color: #808080;">Ask me anything about trading or use a quick action.</p>
            </div>
            """, unsafe_allow_html=True)

    # Footer
    st.markdown("---")
    st.markdown(
        '<p style="text-align: center; color: #666;">Powered by AVA Trading Platform | AI-Enhanced Trading Assistant</p>',
        unsafe_allow_html=True
    )


if __name__ == "__main__":
    main()
