"""
Streamlit Voice Commands UI Integration
========================================

Provides UI components for voice command interaction in Streamlit.

Features:
- Voice command button with visual feedback
- Real-time transcription display
- Command confirmation dialogs
- Voice feedback settings
- Command history viewer

Author: Magnus Trading Platform
Created: 2025-11-21
"""

import streamlit as st
import logging
from typing import Optional, Dict, Any, Callable
from pathlib import Path
import json

logger = logging.getLogger(__name__)


# ============================================================================
# Voice Command UI Components
# ============================================================================

def create_voice_command_interface(
    key_prefix: str = "voice_cmd_",
    on_command: Optional[Callable[[Dict[str, Any]], None]] = None,
    show_history: bool = True,
    show_help: bool = True
) -> Optional[Dict[str, Any]]:
    """
    Create complete voice command interface

    Args:
        key_prefix: Prefix for Streamlit component keys
        on_command: Callback function when command is executed
        show_history: Show command history
        show_help: Show help button

    Returns:
        Command result dict if command was executed
    """
    from src.voice.voice_command_handler import VoiceCommandHandler

    # Initialize handler in session state
    if f"{key_prefix}handler" not in st.session_state:
        st.session_state[f"{key_prefix}handler"] = VoiceCommandHandler()

    handler = st.session_state[f"{key_prefix}handler"]

    # Voice command button with custom styling
    st.markdown("""
    <style>
        .voice-command-button {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 1rem 2rem;
            border-radius: 50px;
            border: none;
            font-size: 1.1rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
            transition: all 0.3s ease;
            display: flex;
            align-items: center;
            gap: 0.5rem;
        }

        .voice-command-button:hover {
            transform: translateY(-2px);
            box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
        }

        .voice-command-button.listening {
            background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
            animation: pulse 1.5s ease-in-out infinite;
        }

        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.05); }
        }

        .voice-transcript {
            background: #f8f9fa;
            border-left: 4px solid #667eea;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
            font-family: 'Courier New', monospace;
        }

        .command-result {
            background: #e8f5e9;
            border-left: 4px solid #4caf50;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }

        .command-error {
            background: #ffebee;
            border-left: 4px solid #f44336;
            padding: 1rem;
            margin: 1rem 0;
            border-radius: 8px;
        }

        .wake-word-indicator {
            display: inline-block;
            padding: 0.25rem 0.75rem;
            background: #667eea;
            color: white;
            border-radius: 12px;
            font-size: 0.85rem;
            font-weight: 600;
        }

        .command-history-item {
            background: white;
            padding: 0.75rem;
            margin: 0.5rem 0;
            border-radius: 6px;
            border: 1px solid #e0e0e0;
        }
    </style>
    """, unsafe_allow_html=True)

    # Main voice command interface
    col1, col2, col3 = st.columns([2, 1, 1])

    with col1:
        st.markdown("### 🎤 Voice Commands")

    with col2:
        if show_help:
            if st.button("❓ Voice Help", key=f"{key_prefix}help_btn"):
                st.session_state[f"{key_prefix}show_help"] = True

    with col3:
        if st.button("📊 History", key=f"{key_prefix}history_btn"):
            st.session_state[f"{key_prefix}show_history"] = not st.session_state.get(f"{key_prefix}show_history", False)

    # Wake word indicator
    wake_word = handler.config.wake_word.value.replace("_", " ").title()
    st.markdown(f'<span class="wake-word-indicator">Wake Word: {wake_word}</span>', unsafe_allow_html=True)

    st.divider()

    # Voice input section
    col1, col2 = st.columns([3, 1])

    with col1:
        # Text input for voice transcript (also allows typing)
        voice_input = st.text_input(
            "Voice Input (or type command)",
            key=f"{key_prefix}input",
            placeholder=f'Say "{wake_word}" followed by your command...',
            help="Use the microphone button to speak, or type your command here"
        )

    with col2:
        # Voice button using Web Speech API
        listening_state = st.session_state.get(f"{key_prefix}listening", False)

        # Create voice button with JavaScript
        voice_button_html = f"""
        <div id="voice-button-container">
            <button id="voice-button" class="voice-command-button {'listening' if listening_state else ''}">
                <span id="mic-icon">🎤</span>
                <span id="button-text">{'Listening...' if listening_state else 'Speak'}</span>
            </button>
        </div>

        <script>
        const voiceButton = document.getElementById('voice-button');
        const micIcon = document.getElementById('mic-icon');
        const buttonText = document.getElementById('button-text');
        const voiceInput = document.querySelector('input[aria-label="Voice Input (or type command)"]');

        let recognition = null;
        let isListening = false;

        // Check for Web Speech API support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {{
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            recognition = new SpeechRecognition();

            recognition.continuous = false;
            recognition.interimResults = true;
            recognition.lang = 'en-US';

            recognition.onstart = () => {{
                isListening = true;
                voiceButton.classList.add('listening');
                micIcon.textContent = '🔴';
                buttonText.textContent = 'Listening...';
            }};

            recognition.onresult = (event) => {{
                const transcript = Array.from(event.results)
                    .map(result => result[0].transcript)
                    .join('');

                if (voiceInput) {{
                    voiceInput.value = transcript;
                    voiceInput.dispatchEvent(new Event('input', {{ bubbles: true }}));
                }}
            }};

            recognition.onend = () => {{
                isListening = false;
                voiceButton.classList.remove('listening');
                micIcon.textContent = '🎤';
                buttonText.textContent = 'Speak';

                // Trigger command processing
                if (voiceInput && voiceInput.value) {{
                    const enterEvent = new KeyboardEvent('keydown', {{
                        key: 'Enter',
                        code: 'Enter',
                        keyCode: 13,
                        bubbles: true
                    }});
                    voiceInput.dispatchEvent(enterEvent);
                }}
            }};

            recognition.onerror = (event) => {{
                console.error('Speech recognition error:', event.error);
                isListening = false;
                voiceButton.classList.remove('listening');
                micIcon.textContent = '🎤';
                buttonText.textContent = 'Speak';
            }};
        }}

        voiceButton.addEventListener('click', () => {{
            if (!recognition) {{
                alert('Voice recognition not supported in this browser. Please use Chrome or Edge.');
                return;
            }}

            if (isListening) {{
                recognition.stop();
            }} else {{
                recognition.start();
            }}
        }});
        </script>
        """

        st.markdown(voice_button_html, unsafe_allow_html=True)

    # Process command if entered
    command_result = None
    if voice_input:
        with st.spinner("Processing command..."):
            command_result = handler.process_voice_input(voice_input)

            # Display result
            if command_result["status"] == "wake_word_detected":
                st.info(f"🎤 {command_result['message']}")
                st.session_state[f"{key_prefix}listening"] = True

            elif command_result["status"] == "success":
                st.markdown(f'<div class="command-result">✅ {command_result["message"]}</div>', unsafe_allow_html=True)

                # Execute callback if provided
                if on_command:
                    on_command(command_result)

                # Clear input
                st.session_state[f"{key_prefix}listening"] = False

            elif command_result["status"] == "confirmation_required":
                st.warning(f"⚠️ {command_result['message']}")

                col1, col2 = st.columns(2)
                with col1:
                    if st.button("✅ Confirm", key=f"{key_prefix}confirm"):
                        if on_command:
                            on_command(command_result)
                        st.success("Command confirmed!")

                with col2:
                    if st.button("❌ Cancel", key=f"{key_prefix}cancel"):
                        st.info("Command cancelled")

            elif command_result["status"] == "no_match":
                st.markdown(f'<div class="command-error">❌ {command_result["message"]}</div>', unsafe_allow_html=True)

            elif command_result["status"] == "error":
                st.markdown(f'<div class="command-error">⚠️ {command_result["message"]}</div>', unsafe_allow_html=True)

    # Show help if requested
    if st.session_state.get(f"{key_prefix}show_help"):
        st.divider()
        st.markdown("### 📚 Available Voice Commands")

        from src.voice.voice_command_handler import format_help_text
        help_text = format_help_text()
        st.markdown(help_text)

        if st.button("✖️ Close Help", key=f"{key_prefix}close_help"):
            st.session_state[f"{key_prefix}show_help"] = False

    # Show command history if requested
    if show_history and st.session_state.get(f"{key_prefix}show_history"):
        st.divider()
        st.markdown("### 📜 Command History")

        history = handler.get_command_history(limit=10)

        if not history:
            st.info("No commands executed yet")
        else:
            for i, cmd in enumerate(reversed(history)):
                success_icon = "✅" if cmd["success"] else "❌"
                st.markdown(f"""
                <div class="command-history-item">
                    {success_icon} <strong>{cmd['command'].replace('_', ' ').title()}</strong><br>
                    <small>{cmd['transcript']}</small><br>
                    <small style="color: #666;">{cmd['timestamp'].strftime('%I:%M:%S %p')}</small>
                </div>
                """, unsafe_allow_html=True)

            col1, col2 = st.columns(2)
            with col1:
                if st.button("🗑️ Clear History", key=f"{key_prefix}clear_history"):
                    handler.clear_history()
                    st.success("History cleared!")
                    st.rerun()

            with col2:
                stats = handler.get_statistics()
                st.metric("Success Rate", f"{stats['success_rate']}%")

    return command_result


def create_voice_settings(key_prefix: str = "voice_settings_"):
    """
    Create voice command settings panel

    Args:
        key_prefix: Prefix for Streamlit component keys
    """
    st.markdown("### ⚙️ Voice Command Settings")

    # Wake word selection
    from src.voice.voice_command_handler import WakeWord

    wake_word_options = {
        "Hey AVA": WakeWord.HEY_AVA,
        "Magnus": WakeWord.MAGNUS,
        "Computer": WakeWord.COMPUTER,
        "Assistant": WakeWord.ASSISTANT
    }

    selected_wake_word = st.selectbox(
        "Wake Word",
        options=list(wake_word_options.keys()),
        key=f"{key_prefix}wake_word",
        help="The phrase to activate voice commands"
    )

    # Sensitivity
    sensitivity = st.slider(
        "Wake Word Sensitivity",
        min_value=0.0,
        max_value=1.0,
        value=0.5,
        step=0.1,
        key=f"{key_prefix}sensitivity",
        help="Higher sensitivity = more likely to trigger (may have false positives)"
    )

    # Timeout
    timeout = st.number_input(
        "Command Timeout (seconds)",
        min_value=3,
        max_value=30,
        value=5,
        key=f"{key_prefix}timeout",
        help="How long to wait for a command after wake word"
    )

    # Feedback options
    col1, col2 = st.columns(2)

    with col1:
        confirmation_sound = st.checkbox(
            "Confirmation Sound",
            value=True,
            key=f"{key_prefix}confirmation_sound",
            help="Play sound when wake word detected"
        )

    with col2:
        visual_feedback = st.checkbox(
            "Visual Feedback",
            value=True,
            key=f"{key_prefix}visual_feedback",
            help="Show visual indicators during listening"
        )

    # Voice feedback (text-to-speech)
    st.divider()
    st.markdown("#### 🔊 Voice Feedback (Text-to-Speech)")

    enable_tts = st.checkbox(
        "Enable Voice Responses",
        value=False,
        key=f"{key_prefix}enable_tts",
        help="AVA will speak responses aloud"
    )

    if enable_tts:
        voice_speed = st.slider(
            "Voice Speed",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key=f"{key_prefix}voice_speed"
        )

        voice_pitch = st.slider(
            "Voice Pitch",
            min_value=0.5,
            max_value=2.0,
            value=1.0,
            step=0.1,
            key=f"{key_prefix}voice_pitch"
        )

        # Test voice
        if st.button("🔊 Test Voice", key=f"{key_prefix}test_voice"):
            test_text = "Hello! I'm AVA, your trading assistant. How can I help you today?"

            # Use Web Speech API for text-to-speech
            st.markdown(f"""
            <script>
            const utterance = new SpeechSynthesisUtterance("{test_text}");
            utterance.rate = {voice_speed};
            utterance.pitch = {voice_pitch};
            window.speechSynthesis.speak(utterance);
            </script>
            """, unsafe_allow_html=True)

            st.success("Playing voice sample...")

    # Save settings
    st.divider()
    if st.button("💾 Save Voice Settings", type="primary", key=f"{key_prefix}save"):
        # Save to session state and config
        settings = {
            "wake_word": wake_word_options[selected_wake_word].value,
            "sensitivity": sensitivity,
            "timeout": timeout,
            "confirmation_sound": confirmation_sound,
            "visual_feedback": visual_feedback,
            "enable_tts": enable_tts,
            "voice_speed": voice_speed if enable_tts else 1.0,
            "voice_pitch": voice_pitch if enable_tts else 1.0
        }

        # Save to config file
        config_path = Path("config/voice_commands.yaml")
        config_path.parent.mkdir(parents=True, exist_ok=True)

        import yaml
        with open(config_path, 'w') as f:
            yaml.dump(settings, f)

        st.success("✅ Voice settings saved!")
        st.balloons()


def create_compact_voice_button(key_prefix: str = "compact_voice_") -> Optional[str]:
    """
    Create compact voice button for sidebar or toolbar

    Args:
        key_prefix: Prefix for Streamlit component keys

    Returns:
        Voice transcript if available
    """
    # Compact voice button
    st.markdown("""
    <style>
        .compact-voice-btn {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 0.5rem 1rem;
            border-radius: 25px;
            border: none;
            font-size: 0.9rem;
            font-weight: 600;
            cursor: pointer;
            box-shadow: 0 2px 8px rgba(102, 126, 234, 0.3);
            transition: all 0.2s ease;
        }

        .compact-voice-btn:hover {
            transform: translateY(-1px);
            box-shadow: 0 4px 12px rgba(102, 126, 234, 0.5);
        }
    </style>
    """, unsafe_allow_html=True)

    col1, col2 = st.columns([1, 3])

    with col1:
        st.markdown('<button class="compact-voice-btn">🎤</button>', unsafe_allow_html=True)

    with col2:
        voice_input = st.text_input(
            "Voice",
            key=f"{key_prefix}input",
            placeholder="Say 'Hey AVA'...",
            label_visibility="collapsed"
        )

    return voice_input if voice_input else None


# ============================================================================
# Command Action Handlers
# ============================================================================

def handle_voice_command_action(command_result: Dict[str, Any]):
    """
    Handle voice command actions (navigation, data display, etc.)

    Args:
        command_result: Result from voice command processing
    """
    action = command_result.get("action")

    if action == "show_portfolio":
        st.switch_page("dashboard.py")

    elif action == "get_quote":
        ticker = command_result.get("ticker")
        if ticker:
            st.session_state["selected_ticker"] = ticker
            st.switch_page("dashboard.py")

    elif action == "show_market":
        st.switch_page("dashboard.py")

    elif action == "analyze_stock":
        ticker = command_result.get("ticker")
        if ticker:
            st.session_state["analysis_ticker"] = ticker
            st.switch_page("options_analysis_page.py")

    elif action == "scan_options":
        st.switch_page("options_trading_hub_page.py")

    elif action == "navigate":
        page = command_result.get("page")
        if page:
            try:
                st.switch_page(f"{page}.py")
            except:
                st.error(f"Page not found: {page}")

    elif action == "change_personality":
        personality = command_result.get("personality")
        if personality:
            st.session_state["ava_personality"] = personality
            st.rerun()

    elif action == "toggle_setting":
        setting = command_result.get("setting")
        enable = command_result.get("enable")
        if setting:
            st.session_state[f"setting_{setting}"] = enable
            st.rerun()

    elif action == "show_help":
        st.session_state["show_voice_help"] = True
        st.rerun()


# ============================================================================
# Helper Functions
# ============================================================================

def load_voice_settings() -> Dict[str, Any]:
    """Load voice settings from config file"""
    config_path = Path("config/voice_commands.yaml")

    if not config_path.exists():
        return {
            "wake_word": "hey_ava",
            "sensitivity": 0.5,
            "timeout": 5,
            "confirmation_sound": True,
            "visual_feedback": True,
            "enable_tts": False,
            "voice_speed": 1.0,
            "voice_pitch": 1.0
        }

    import yaml
    with open(config_path) as f:
        return yaml.safe_load(f)


def save_voice_settings(settings: Dict[str, Any]):
    """Save voice settings to config file"""
    config_path = Path("config/voice_commands.yaml")
    config_path.parent.mkdir(parents=True, exist_ok=True)

    import yaml
    with open(config_path, 'w') as f:
        yaml.dump(settings, f)
