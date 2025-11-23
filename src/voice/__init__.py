"""
Voice Command System
====================

Hands-free interaction with AVA through voice commands.

Components:
- voice_command_handler: Core command processing and wake word detection
- streamlit_voice_commands: UI components for Streamlit integration
- Web Speech API integration for browser-based speech recognition

Quick Start:
-----------
from src.voice.streamlit_voice_commands import create_voice_command_interface

# In your Streamlit page
result = create_voice_command_interface()

if result:
    st.write(f"Command: {result['action']}")

Available Commands:
------------------
- Portfolio: "Show my portfolio", "What's my balance"
- Market Data: "What's the price of Apple", "How's the market"
- Analysis: "Analyze Tesla", "Find options opportunities"
- Navigation: "Go to dashboard", "Open options page"
- Settings: "Change personality to analyst", "Enable voice feedback"
- Help: "What can you do", "Show commands"

Wake Words:
----------
- "Hey AVA" (default)
- "Magnus"
- "Computer"
- "Assistant"

Author: Magnus Trading Platform
Created: 2025-11-21
"""

from .voice_command_handler import (
    VoiceCommandHandler,
    WakeWordDetector,
    WakeWord,
    WakeWordConfig,
    CommandPattern,
    CommandCategory,
    get_available_commands,
    format_help_text
)

from .streamlit_voice_commands import (
    create_voice_command_interface,
    create_voice_settings,
    create_compact_voice_button,
    handle_voice_command_action,
    load_voice_settings,
    save_voice_settings
)

__all__ = [
    # Core handler
    'VoiceCommandHandler',
    'WakeWordDetector',

    # Configuration
    'WakeWord',
    'WakeWordConfig',
    'CommandPattern',
    'CommandCategory',

    # Streamlit UI components
    'create_voice_command_interface',
    'create_voice_settings',
    'create_compact_voice_button',
    'handle_voice_command_action',

    # Utilities
    'get_available_commands',
    'format_help_text',
    'load_voice_settings',
    'save_voice_settings',
]

__version__ = '1.0.0'
