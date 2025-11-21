"""
Talk to AVA - Voice Conversation Interface
==========================================

AVA (Automated Vector Agent) - Your AI trading assistant with voice capabilities.

This script allows you to have voice conversations with AVA via Telegram.

Features:
- Send voice messages to AVA via Telegram
- AVA transcribes your voice (Whisper - FREE)
- AVA processes your request
- AVA responds with voice message (Piper TTS - FREE)
- Get stock alerts, portfolio updates, task status, and more

Usage:
1. Send voice message to Telegram bot
2. AVA transcribes and processes
3. AVA responds with voice message

Commands you can say:
- "Hey AVA, how's my portfolio?"
- "AVA, should I sell a put on NVDA?"
- "What are you working on?"
- "Any important stock alerts?"
- "What's the status of AAPL?"
"""

import os
import sys
from pathlib import Path

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add src to path
sys.path.insert(0, str(Path(__file__).parent / "src"))

print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║     🎤 AVA - Automated Vector Agent (Voice Interface) 🎤         ║
║                                                                  ║
║  Your AI trading assistant with voice capabilities              ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

AVA Voice Features:
- 🎤 Send voice messages via Telegram
- 🧠 AI-powered responses
- 📊 Portfolio updates
- 📈 Stock analysis
- ⚡ Real-time alerts
- 🔄 Task status updates

Setup Status:
""")

# Check if voice dependencies are installed
try:
    import whisper
    print("✅ Whisper (speech-to-text) - INSTALLED")
except ImportError:
    print("❌ Whisper (speech-to-text) - NOT INSTALLED")
    print("   Install: pip install openai-whisper")

try:
    import piper
    print("✅ Piper TTS (text-to-speech) - INSTALLED")
except ImportError:
    print("⚠️  Piper TTS (text-to-speech) - NOT INSTALLED")
    print("   Install: pip install piper-tts")

try:
    import telegram
    print("✅ Telegram Bot - CONFIGURED")
except ImportError:
    print("❌ Telegram Bot - NOT CONFIGURED")

print("""
How to Talk to AVA:
1. Open Telegram
2. Send voice message to your bot
3. AVA will transcribe and respond
4. Get voice reply from AVA

Example Conversations:
- "Hey AVA, how's my portfolio today?"
- "AVA, analyze NVDA for a cash-secured put"
- "What tasks did you complete today?"
- "Any earnings announcements this week?"

🚀 AVA is ready to assist you 24/7!
""")

if __name__ == "__main__":
    print("\nTo start talking to AVA:")
    print("1. Send a voice message to your Telegram bot")
    print("2. Or run: python src/ava/telegram_voice_bot.py")
