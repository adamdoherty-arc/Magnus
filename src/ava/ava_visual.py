"""
AVA Visual Avatar System
=========================

Manages AVA's visual appearance with:
- Static images for different expressions
- Fallback to emojis if images not available
- Dynamic expression based on conversation state
- Support for animated GIFs

Author: AVA Trading Platform
Created: 2025-11-11
Updated: 2025-11-12 - Enhanced with new AVA avatar
"""

from pathlib import Path
from enum import Enum
import streamlit as st
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class AvaExpression(Enum):
    """AVA's facial expressions"""
    NEUTRAL = "neutral"
    THINKING = "thinking"
    HAPPY = "happy"
    SURPRISED = "surprised"
    SPEAKING = "speaking"
    ERROR = "error"
    SUCCESS = "success"


class AvaVisual:
    """Visual avatar system for AVA"""

    # Asset paths
    ASSET_PATH = Path("assets/ava")

    # Expression to file mapping - Updated to use new AVA image
    EXPRESSIONS = {
        AvaExpression.NEUTRAL: "nancy-a-legs-up.jpg",  # Updated: New AVA image
        AvaExpression.THINKING: "nancy-a-legs-up.jpg",
        AvaExpression.HAPPY: "nancy-a-legs-up.jpg",
        AvaExpression.SURPRISED: "nancy-a-legs-up.jpg",
        AvaExpression.SPEAKING: "nancy-a-legs-up.jpg",
        AvaExpression.ERROR: "nancy-a-legs-up.jpg",
        AvaExpression.SUCCESS: "nancy-a-legs-up.jpg"
    }

    # Emoji fallbacks
    EMOJI_FALLBACKS = {
        AvaExpression.NEUTRAL: "🤖",
        AvaExpression.THINKING: "🤔",
        AvaExpression.HAPPY: "😊",
        AvaExpression.SURPRISED: "😲",
        AvaExpression.SPEAKING: "🗣️",
        AvaExpression.ERROR: "😕",
        AvaExpression.SUCCESS: "✅"
    }

    @classmethod
    def show_avatar(
        cls,
        expression: AvaExpression = AvaExpression.NEUTRAL,
        size: int = 100,
        caption: Optional[str] = None,
        use_container_width: bool = False
    ):
        """
        Display AVA's avatar with specific expression

        Args:
            expression: The expression to show
            size: Width of the image in pixels
            caption: Optional caption below image
            use_container_width: If True, image fills container width
        """
        avatar_file = cls.EXPRESSIONS.get(expression)
        avatar_path = cls.ASSET_PATH / avatar_file

        if avatar_path.exists():
            # Show image
            try:
                st.image(
                    str(avatar_path),
                    width=None if use_container_width else size,
                    caption=caption,
                    use_container_width=use_container_width
                )
                logger.debug(f"Displayed avatar: {expression.value}")
            except Exception as e:
                logger.error(f"Error displaying image {avatar_path}: {e}")
                cls._show_emoji_fallback(expression, size)
        else:
            # Fallback to emoji
            cls._show_emoji_fallback(expression, size, caption)

    @classmethod
    def _show_emoji_fallback(
        cls,
        expression: AvaExpression,
        size: int = 100,
        caption: Optional[str] = None
    ):
        """Show emoji fallback when image not available"""
        emoji = cls.EMOJI_FALLBACKS.get(expression, "🤖")

        # Calculate emoji size (approximation)
        emoji_size = int(size * 0.8)

        html = f"""
        <div style="text-align: center;">
            <div style="font-size: {emoji_size}px; line-height: 1;">{emoji}</div>
            {f'<p style="font-size: 12px; color: #666;">{caption}</p>' if caption else ''}
        </div>
        """
        st.markdown(html, unsafe_allow_html=True)
        logger.debug(f"Displayed emoji fallback: {expression.value}")

    @classmethod
    def get_expression_for_state(
        cls,
        ava_state: str,
        success: bool = True,
        is_speaking: bool = False
    ) -> AvaExpression:
        """
        Determine expression based on AVA's current state

        Args:
            ava_state: Current conversation state
            success: Whether last action was successful
            is_speaking: Whether AVA is currently responding

        Returns:
            Appropriate expression
        """
        # Speaking takes priority
        if is_speaking:
            return AvaExpression.SPEAKING

        # Error state
        if not success:
            return AvaExpression.ERROR

        # State-specific expressions
        state_map = {
            "idle": AvaExpression.NEUTRAL,
            "processing": AvaExpression.THINKING,
            "awaiting_watchlist_name": AvaExpression.NEUTRAL,
            "awaiting_ticker_symbol": AvaExpression.NEUTRAL,
            "awaiting_task_details": AvaExpression.THINKING,
            "awaiting_task_priority": AvaExpression.NEUTRAL,
            "awaiting_confirmation": AvaExpression.SURPRISED,
            "awaiting_sql_query": AvaExpression.THINKING,
            "responding": AvaExpression.SPEAKING,
            "success": AvaExpression.HAPPY
        }

        # Handle ConversationState enum
        if hasattr(ava_state, 'value'):
            ava_state = ava_state.value

        return state_map.get(ava_state, AvaExpression.NEUTRAL)

    @classmethod
    def assets_available(cls) -> bool:
        """Check if avatar assets are available"""
        return cls.ASSET_PATH.exists() and any(cls.ASSET_PATH.iterdir())

    @classmethod
    def get_assets_status(cls) -> dict:
        """Get status of all avatar assets"""
        status = {
            'path': str(cls.ASSET_PATH),
            'exists': cls.ASSET_PATH.exists(),
            'expressions': {}
        }

        for expression, filename in cls.EXPRESSIONS.items():
            file_path = cls.ASSET_PATH / filename
            status['expressions'][expression.value] = {
                'filename': filename,
                'exists': file_path.exists(),
                'path': str(file_path)
            }

        return status


class AvaAvatarWidget:
    """Reusable widget for showing AVA's avatar"""

    @staticmethod
    def show(
        expression: AvaExpression = AvaExpression.NEUTRAL,
        size: int = 100,
        show_status: bool = False,
        status_text: Optional[str] = None
    ):
        """
        Show AVA avatar widget with optional status

        Args:
            expression: Expression to display
            size: Size of avatar
            show_status: Whether to show status text
            status_text: Custom status text
        """
        # Avatar
        AvaVisual.show_avatar(expression, size)

        # Status indicator
        if show_status:
            if status_text:
                st.caption(status_text)
            else:
                # Auto-generate status text
                status_messages = {
                    AvaExpression.NEUTRAL: "Ready to help",
                    AvaExpression.THINKING: "Analyzing...",
                    AvaExpression.HAPPY: "Success!",
                    AvaExpression.SURPRISED: "Interesting!",
                    AvaExpression.SPEAKING: "Responding...",
                    AvaExpression.ERROR: "Oops, something went wrong",
                    AvaExpression.SUCCESS: "Task completed!"
                }
                st.caption(status_messages.get(expression, ""))


def show_avatar_diagnostics():
    """Show diagnostic info about avatar assets (for debugging)"""
    st.subheader("AVA Avatar Diagnostics")

    status = AvaVisual.get_assets_status()

    # Overall status
    if status['exists']:
        st.success(f"✅ Assets folder exists: {status['path']}")
    else:
        st.error(f"❌ Assets folder not found: {status['path']}")
        st.info("Run `python prepare_ava_photos.py` to set up avatar assets")
        return

    # Individual expressions
    st.write("**Expression Assets:**")

    for expression_name, expr_status in status['expressions'].items():
        col1, col2, col3 = st.columns([2, 3, 1])

        with col1:
            st.write(f"**{expression_name.title()}**")

        with col2:
            st.write(f"`{expr_status['filename']}`")

        with col3:
            if expr_status['exists']:
                st.success("✅")
            else:
                st.warning("⚠️")

    # Preview
    st.write("**Preview:**")
    cols = st.columns(len(AvaExpression))

    for idx, expression in enumerate(AvaExpression):
        with cols[idx]:
            st.caption(expression.value.title())
            AvaVisual.show_avatar(expression, size=80)


# Example usage function
def example_usage():
    """Example of how to use AVA visual system"""
    st.title("AVA Visual System Example")

    # Show all expressions
    st.subheader("All Expressions")
    cols = st.columns(len(AvaExpression))

    for idx, expression in enumerate(AvaExpression):
        with cols[idx]:
            AvaAvatarWidget.show(expression, size=100, show_status=True)

    # Interactive selector
    st.subheader("Interactive Preview")

    col1, col2 = st.columns([1, 3])

    with col1:
        selected_expression = st.selectbox(
            "Select Expression:",
            options=list(AvaExpression),
            format_func=lambda x: x.value.title()
        )

        selected_size = st.slider("Size:", 50, 200, 100)

    with col2:
        AvaVisual.show_avatar(selected_expression, size=selected_size)

    # Diagnostics
    with st.expander("🔍 Avatar Diagnostics"):
        show_avatar_diagnostics()


if __name__ == "__main__":
    # Run example when script is executed directly
    example_usage()
