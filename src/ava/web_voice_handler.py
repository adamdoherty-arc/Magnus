"""
AVA Web Voice Handler
=====================

Integrates voice capabilities into the Streamlit web interface.

Features:
- Browser-based Text-to-Speech (Web Speech API)
- Browser-based Speech-to-Text (Web Speech API)
- Voice customization (pitch, rate, voice selection)
- Auto-speak toggle for AVA responses
- Voice activity detection

Author: AVA Trading Platform
Created: 2025-11-20
"""

import streamlit as st
import streamlit.components.v1 as components
from typing import Optional, Dict, Callable
import json


class WebVoiceHandler:
    """Handles voice interactions in the web interface using browser APIs"""

    # Voice configuration presets
    VOICE_PRESETS = {
        'default': {'rate': 1.0, 'pitch': 1.0, 'voice_name': None},
        'fast': {'rate': 1.5, 'pitch': 1.0, 'voice_name': None},
        'slow': {'rate': 0.8, 'pitch': 1.0, 'voice_name': None},
        'high': {'rate': 1.0, 'pitch': 1.3, 'voice_name': None},
        'low': {'rate': 1.0, 'pitch': 0.8, 'voice_name': None},
    }

    @staticmethod
    def inject_voice_controls():
        """Inject voice control JavaScript into the page"""

        voice_js = """
        <script>
        // AVA Voice System - Using Web Speech API
        class AVAVoice {
            constructor() {
                this.synth = window.speechSynthesis;
                this.recognition = null;
                this.isListening = false;
                this.autoSpeak = false;
                this.voiceSettings = {
                    rate: 1.0,
                    pitch: 1.0,
                    volume: 1.0,
                    voice: null
                };

                // Initialize speech recognition if available
                if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
                    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
                    this.recognition = new SpeechRecognition();
                    this.recognition.continuous = false;
                    this.recognition.interimResults = false;
                    this.recognition.lang = 'en-US';

                    this.recognition.onresult = (event) => {
                        const transcript = event.results[0][0].transcript;
                        console.log('Speech recognized:', transcript);
                        this.onSpeechRecognized(transcript);
                    };

                    this.recognition.onerror = (event) => {
                        console.error('Speech recognition error:', event.error);
                        this.isListening = false;
                        this.updateMicButton(false);
                    };

                    this.recognition.onend = () => {
                        this.isListening = false;
                        this.updateMicButton(false);
                    };
                }

                console.log('✅ AVA Voice System initialized');
            }

            // Text-to-Speech
            speak(text) {
                if (!this.synth) return false;

                // Cancel any ongoing speech
                this.synth.cancel();

                const utterance = new SpeechSynthesisUtterance(text);
                utterance.rate = this.voiceSettings.rate;
                utterance.pitch = this.voiceSettings.pitch;
                utterance.volume = this.voiceSettings.volume;

                if (this.voiceSettings.voice) {
                    utterance.voice = this.voiceSettings.voice;
                }

                utterance.onstart = () => {
                    console.log('🗣️ AVA speaking...');
                    this.updateSpeakButton(true);
                };

                utterance.onend = () => {
                    console.log('✅ AVA finished speaking');
                    this.updateSpeakButton(false);
                };

                utterance.onerror = (event) => {
                    console.error('Speech error:', event.error);
                    this.updateSpeakButton(false);
                };

                this.synth.speak(utterance);
                return true;
            }

            // Stop speaking
            stopSpeaking() {
                if (this.synth) {
                    this.synth.cancel();
                    this.updateSpeakButton(false);
                }
            }

            // Start listening
            startListening() {
                if (!this.recognition) {
                    alert('Speech recognition not supported in this browser');
                    return false;
                }

                if (this.isListening) {
                    this.stopListening();
                    return false;
                }

                try {
                    this.recognition.start();
                    this.isListening = true;
                    this.updateMicButton(true);
                    console.log('🎤 Listening...');
                    return true;
                } catch (error) {
                    console.error('Error starting recognition:', error);
                    return false;
                }
            }

            // Stop listening
            stopListening() {
                if (this.recognition && this.isListening) {
                    this.recognition.stop();
                    this.isListening = false;
                    this.updateMicButton(false);
                }
            }

            // Handle recognized speech
            onSpeechRecognized(transcript) {
                console.log('Recognized:', transcript);

                // Find the chat input textarea
                const chatInput = document.querySelector('.stChatInput textarea, .stTextArea textarea');
                if (chatInput) {
                    chatInput.value = transcript;
                    chatInput.dispatchEvent(new Event('input', { bubbles: true }));

                    // Optionally auto-submit
                    const submitBtn = document.querySelector('button[kind="primaryFormSubmit"]');
                    if (submitBtn && this.autoSubmit) {
                        setTimeout(() => submitBtn.click(), 100);
                    }
                }

                // Update Streamlit session state
                window.parent.postMessage({
                    type: 'streamlit:setComponentValue',
                    value: transcript
                }, '*');
            }

            // Update voice settings
            updateSettings(settings) {
                this.voiceSettings = { ...this.voiceSettings, ...settings };
                console.log('Voice settings updated:', this.voiceSettings);
            }

            // Get available voices
            getVoices() {
                if (!this.synth) return [];
                return this.synth.getVoices();
            }

            // UI update helpers
            updateMicButton(isActive) {
                const micBtn = document.getElementById('ava-mic-btn');
                if (micBtn) {
                    micBtn.style.background = isActive ? '#ef4444' : '#3b82f6';
                    micBtn.innerHTML = isActive ? '🔴 Listening...' : '🎤 Voice Input';
                }
            }

            updateSpeakButton(isSpeaking) {
                const speakBtn = document.getElementById('ava-speak-btn');
                if (speakBtn) {
                    speakBtn.innerHTML = isSpeaking ? '🔇 Stop' : '🔊 Speak';
                }
            }

            // Toggle auto-speak
            toggleAutoSpeak() {
                this.autoSpeak = !this.autoSpeak;
                console.log('Auto-speak:', this.autoSpeak);
                return this.autoSpeak;
            }
        }

        // Initialize global AVA voice instance
        window.avaVoice = new AVAVoice();

        // Helper functions for Streamlit
        window.avaSpeak = (text) => window.avaVoice.speak(text);
        window.avaStopSpeaking = () => window.avaVoice.stopSpeaking();
        window.avaStartListening = () => window.avaVoice.startListening();
        window.avaStopListening = () => window.avaVoice.stopListening();
        window.avaUpdateSettings = (settings) => window.avaVoice.updateSettings(settings);
        window.avaToggleAutoSpeak = () => window.avaVoice.toggleAutoSpeak();

        console.log('✅ AVA Voice functions loaded globally');
        </script>

        <style>
        /* Voice control button styles */
        #ava-mic-btn, #ava-speak-btn {
            padding: 8px 16px;
            border: none;
            border-radius: 8px;
            font-weight: 600;
            cursor: pointer;
            transition: all 0.2s;
            color: white;
        }

        #ava-mic-btn {
            background: #3b82f6;
        }

        #ava-mic-btn:hover {
            background: #2563eb;
            transform: translateY(-1px);
        }

        #ava-speak-btn {
            background: #10b981;
        }

        #ava-speak-btn:hover {
            background: #059669;
            transform: translateY(-1px);
        }

        .voice-controls-container {
            display: flex;
            gap: 8px;
            margin: 10px 0;
            flex-wrap: wrap;
        }

        .voice-indicator {
            display: inline-block;
            width: 8px;
            height: 8px;
            border-radius: 50%;
            background: #10b981;
            animation: pulse 2s infinite;
        }

        @keyframes pulse {
            0%, 100% { opacity: 1; }
            50% { opacity: 0.5; }
        }
        </style>
        """

        components.html(voice_js, height=0)

    @staticmethod
    def create_voice_controls(key_prefix: str = ""):
        """Create voice control buttons"""

        st.markdown("""
        <div class="voice-controls-container">
            <button id="ava-mic-btn" onclick="window.avaStartListening()">
                🎤 Voice Input
            </button>
            <button id="ava-speak-btn" onclick="window.avaStopSpeaking()">
                🔊 Speak
            </button>
        </div>
        """, unsafe_allow_html=True)

    @staticmethod
    def speak_text(text: str):
        """Make AVA speak the given text"""
        # Remove markdown formatting for better speech
        clean_text = text.replace('**', '').replace('*', '').replace('#', '').replace('`', '')

        components.html(f"""
        <script>
        if (window.avaVoice) {{
            window.avaVoice.speak(`{clean_text}`);
        }}
        </script>
        """, height=0)

    @staticmethod
    def create_voice_settings(key_prefix: str = ""):
        """Create voice settings panel"""

        with st.expander("🎙️ Voice Settings", expanded=False):
            st.markdown("### Speech Settings")

            # Auto-speak toggle
            auto_speak = st.checkbox(
                "Auto-speak AVA responses",
                value=st.session_state.get('ava_auto_speak', False),
                key=f"{key_prefix}auto_speak",
                help="Automatically speak AVA's responses"
            )
            st.session_state.ava_auto_speak = auto_speak

            # Voice rate
            rate = st.slider(
                "Speech Rate",
                min_value=0.5,
                max_value=2.0,
                value=st.session_state.get('ava_voice_rate', 1.0),
                step=0.1,
                key=f"{key_prefix}voice_rate",
                help="How fast AVA speaks"
            )
            st.session_state.ava_voice_rate = rate

            # Voice pitch
            pitch = st.slider(
                "Speech Pitch",
                min_value=0.5,
                max_value=2.0,
                value=st.session_state.get('ava_voice_pitch', 1.0),
                step=0.1,
                key=f"{key_prefix}voice_pitch",
                help="How high or low AVA's voice is"
            )
            st.session_state.ava_voice_pitch = pitch

            # Update settings in JavaScript
            settings_json = json.dumps({
                'rate': rate,
                'pitch': pitch,
                'volume': 1.0
            })

            components.html(f"""
            <script>
            if (window.avaUpdateSettings) {{
                window.avaUpdateSettings({settings_json});
            }}
            </script>
            """, height=0)

            st.markdown("### Voice Presets")
            preset_cols = st.columns(3)
            with preset_cols[0]:
                if st.button("🐢 Slow", use_container_width=True, key=f"{key_prefix}preset_slow"):
                    st.session_state.ava_voice_rate = 0.8
                    st.rerun()
            with preset_cols[1]:
                if st.button("🎯 Normal", use_container_width=True, key=f"{key_prefix}preset_normal"):
                    st.session_state.ava_voice_rate = 1.0
                    st.session_state.ava_voice_pitch = 1.0
                    st.rerun()
            with preset_cols[2]:
                if st.button("🚀 Fast", use_container_width=True, key=f"{key_prefix}preset_fast"):
                    st.session_state.ava_voice_rate = 1.5
                    st.rerun()

            st.markdown("---")
            st.caption("💡 Voice features use your browser's built-in speech synthesis. " +
                      "Availability and voice quality may vary by browser.")

    @staticmethod
    def should_auto_speak() -> bool:
        """Check if auto-speak is enabled"""
        return st.session_state.get('ava_auto_speak', False)


# Example usage
if __name__ == "__main__":
    st.title("AVA Voice Handler Test")

    # Initialize voice system
    WebVoiceHandler.inject_voice_controls()

    # Create controls
    WebVoiceHandler.create_voice_controls()

    # Settings
    WebVoiceHandler.create_voice_settings()

    # Test speaking
    if st.button("Test Speech"):
        WebVoiceHandler.speak_text("Hello! I'm AVA, your trading assistant. How can I help you today?")
