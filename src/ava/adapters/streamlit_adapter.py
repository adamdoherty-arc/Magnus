"""
Streamlit Adapter for AVA
Provides Streamlit UI components
"""

import streamlit as st
from typing import Optional, List, Dict
import asyncio
from src.ava.core import AVACore, MessageResponse
import logging

logger = logging.getLogger(__name__)


class StreamlitAVAAdapter:
    """Streamlit adapter for AVA Core"""

    def __init__(self, ava_core: Optional[AVACore] = None):
        """
        Initialize Streamlit adapter

        Args:
            ava_core: AVA Core instance (creates new if None)
        """
        self.ava = ava_core or AVACore()

        # Initialize session state
        if 'ava_messages' not in st.session_state:
            st.session_state.ava_messages = []

        if 'ava_user_id' not in st.session_state:
            st.session_state.ava_user_id = 'web_user_default'

    def show_chat_interface(self, expanded: bool = False):
        """
        Show AVA chat interface

        Args:
            expanded: Whether to show expanded by default
        """
        with st.expander("🤖 **AVA - Your Expert Trading Assistant**", expanded=expanded):
            st.caption("I have full access to Magnus. Ask me anything or request improvements!")

            # Display chat history
            for msg in st.session_state.ava_messages:
                with st.chat_message(msg['role']):
                    st.markdown(msg['content'])

            # Chat input
            user_input = st.chat_input("Ask AVA anything...", key="ava_streamlit_input")

            if user_input:
                # Add user message
                st.session_state.ava_messages.append({
                    'role': 'user',
                    'content': user_input
                })

                # Display user message
                with st.chat_message('user'):
                    st.markdown(user_input)

                # Get AVA response with streaming
                with st.chat_message('assistant'):
                    response_placeholder = st.empty()
                    full_response = ""

                    # Stream response
                    async def stream_response():
                        nonlocal full_response
                        async for chunk in self.ava.process_message(
                            message=user_input,
                            user_id=st.session_state.ava_user_id,
                            platform='web'
                        ):
                            full_response += chunk
                            response_placeholder.markdown(full_response + "▌")

                        # Final update without cursor
                        response_placeholder.markdown(full_response)

                    # Run async
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    try:
                        loop.run_until_complete(stream_response())
                    finally:
                        loop.close()

                # Add AVA response to history
                st.session_state.ava_messages.append({
                    'role': 'assistant',
                    'content': full_response
                })

                # Rerun to update chat
                st.rerun()

            # Quick actions
            st.markdown("---")
            st.caption("**Quick Actions:**")
            col1, col2, col3 = st.columns(3)

            with col1:
                if st.button("📊 Analyze Watchlist", key="ava_quick_analyze"):
                    st.session_state.ava_messages.append({
                        'role': 'user',
                        'content': 'Analyze my default watchlist'
                    })
                    st.rerun()

            with col2:
                if st.button("💼 Check Portfolio", key="ava_quick_portfolio"):
                    st.session_state.ava_messages.append({
                        'role': 'user',
                        'content': 'Show my portfolio status'
                    })
                    st.rerun()

            with col3:
                if st.button("📝 View Tasks", key="ava_quick_tasks"):
                    st.session_state.ava_messages.append({
                        'role': 'user',
                        'content': 'Show me recent tasks'
                    })
                    st.rerun()

    def process_message_sync(self, message: str) -> MessageResponse:
        """
        Process message synchronously (for non-streaming use cases)

        Args:
            message: User message

        Returns:
            MessageResponse
        """
        return self.ava.process_message_sync(
            message=message,
            user_id=st.session_state.ava_user_id,
            platform='web'
        )

