"""
AVA Telegram Bot - Voice & Text Interface
==========================================

Two-way communication with AVA via Telegram:
- Send voice messages → AVA transcribes with Whisper
- Send text messages → AVA processes directly
- Receive responses (text for now, voice coming soon)

Commands:
/start - Get started with AVA
/portfolio - Portfolio status
/tasks - What AVA is working on
/help - Show available commands
"""

import os
import sys
import logging
import tempfile
from pathlib import Path
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

# Load environment (override any shell env vars with .env file values)
load_dotenv(override=True)

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

try:
    from telegram import Update
    from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
except ImportError:
    logger.error("python-telegram-bot not installed. Install: pip install python-telegram-bot")
    sys.exit(1)

try:
    from src.ava.voice_handler import AVAVoiceHandler
except ImportError:
    logger.warning("AVA voice handler not available, text-only mode")
    AVAVoiceHandler = None

try:
    from src.ava.discord_knowledge import get_discord_knowledge
    DISCORD_AVAILABLE = True
except ImportError:
    logger.warning("Discord knowledge not available")
    DISCORD_AVAILABLE = False


class AVATelegramBot:
    """AVA Telegram Bot with voice support"""

    def __init__(self):
        """Initialize bot"""
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        if not self.token or self.token == "YOUR_BOT_TOKEN_HERE":
            raise ValueError("TELEGRAM_BOT_TOKEN not configured in .env")

        self.voice_handler = AVAVoiceHandler() if AVAVoiceHandler else None
        logger.info("✅ AVA Telegram Bot initialized")

    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        chat_id = update.effective_chat.id
        user = update.effective_user

        welcome_message = f"""
👋 Hi {user.first_name}!

I'm **AVA** (Automated Vector Agent) - your AI trading assistant!

🎤 **Voice:** Send me a voice message and I'll transcribe and respond
💬 **Text:** Or just type your questions

**What I can help with:**
• Portfolio updates
• Stock analysis
• Task status
• Market alerts
• Trading opportunities

**Commands:**
/portfolio - Your portfolio status
/tasks - What I'm working on
/help - Show all commands

**Your Chat ID:** `{chat_id}`
(Save this to .env as TELEGRAM_CHAT_ID)

Try asking me: "How's my portfolio?" or "What are you working on?"
"""
        await update.message.reply_text(welcome_message, parse_mode='Markdown')
        logger.info(f"User {user.first_name} (ID: {chat_id}) started bot")

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
**AVA Commands:**

/start - Get started with AVA
/portfolio - Portfolio status
/tasks - What AVA is working on
/status - AVA system status
/signals - Recent Discord trading signals
/ticker SYMBOL - Discord signals for specific ticker
/help - This help message

**Questions you can ask:**
• "How's my portfolio?"
• "Should I sell a put on NVDA?"
• "What did you complete today?"
• "Any important alerts?"
• "What's the market doing?"
• "What are the latest Discord signals?"

Send voice messages and I'll transcribe them!
"""
        await update.message.reply_text(help_text, parse_mode='Markdown')

    async def portfolio_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /portfolio command"""
        if not self.voice_handler:
            await update.message.reply_text("Portfolio handler not available")
            return

        response = self.voice_handler.process_query("How's my portfolio?")
        await update.message.reply_text(response['response_text'])

    async def tasks_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /tasks command"""
        if not self.voice_handler:
            await update.message.reply_text("Task handler not available")
            return

        response = self.voice_handler.process_query("What are you working on?")
        await update.message.reply_text(response['response_text'])

    async def signals_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /signals command - show recent Discord trading signals"""
        if not DISCORD_AVAILABLE:
            await update.message.reply_text("Discord integration not available")
            return

        try:
            dk = get_discord_knowledge()
            signals = dk.get_recent_signals(hours_back=24, limit=5)

            if not signals:
                await update.message.reply_text("No recent Discord signals found")
                return

            response = "**Recent Discord Trading Signals:**\n\n"

            for i, signal in enumerate(signals[:5], 1):
                timestamp = signal['timestamp'].strftime('%m/%d %H:%M')
                channel = signal.get('channel_name', 'Unknown')
                author = signal.get('author_name', 'Unknown')
                content = signal['content'][:150] + "..." if len(signal['content']) > 150 else signal['content']

                response += f"**{i}. {channel}** ({timestamp})\n"
                response += f"👤 {author}\n"
                response += f"💬 {content}\n\n"

            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Sent {len(signals)} Discord signals to user")

        except Exception as e:
            logger.error(f"Error getting signals: {e}")
            await update.message.reply_text(f"Error fetching signals: {str(e)}")

    async def ticker_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /ticker command - show Discord signals for specific ticker"""
        if not DISCORD_AVAILABLE:
            await update.message.reply_text("Discord integration not available")
            return

        if not context.args:
            await update.message.reply_text("Usage: /ticker SYMBOL\nExample: /ticker AAPL")
            return

        ticker = context.args[0].upper()

        try:
            dk = get_discord_knowledge()
            signals = dk.get_signals_by_ticker(ticker, days_back=7)

            if not signals:
                await update.message.reply_text(f"No Discord signals found for ${ticker}")
                return

            response = f"**Discord Signals for ${ticker}:**\n\n"

            for i, signal in enumerate(signals[:5], 1):
                timestamp = signal['timestamp'].strftime('%m/%d %H:%M')
                channel = signal.get('channel_name', 'Unknown')
                author = signal.get('author_name', 'Unknown')
                content = signal['content'][:150] + "..." if len(signal['content']) > 150 else signal['content']

                response += f"**{i}. {channel}** ({timestamp})\n"
                response += f"👤 {author}\n"
                response += f"💬 {content}\n\n"

            await update.message.reply_text(response, parse_mode='Markdown')
            logger.info(f"Sent {len(signals)} Discord signals for {ticker} to user")

        except Exception as e:
            logger.error(f"Error getting ticker signals: {e}")
            await update.message.reply_text(f"Error fetching signals: {str(e)}")

    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        import psycopg2

        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cursor = conn.cursor()

            # Get stats
            cursor.execute("""
                SELECT
                    COUNT(*) FILTER (WHERE status = 'completed') as completed,
                    COUNT(*) FILTER (WHERE status = 'in_progress') as in_progress,
                    COUNT(*) FILTER (WHERE status = 'proposed') as pending
                FROM ci_enhancements
            """)
            completed, in_progress, pending = cursor.fetchone()

            cursor.execute("""
                SELECT COUNT(*)
                FROM ci_enhancements
                WHERE status = 'completed'
                  AND completed_at > NOW() - INTERVAL '24 hours'
            """)
            completed_today = cursor.fetchone()[0]

            cursor.close()
            conn.close()

            status_text = f"""
**AVA Status Report**

📊 **Task Queue:**
• Completed: {completed}
• In Progress: {in_progress}
• Pending: {pending}

⚡ **Today:**
• Tasks completed: {completed_today}

🤖 **Systems:**
• Voice: {'✅ Online' if self.voice_handler else '❌ Offline'}
• Database: ✅ Connected
• Telegram: ✅ Active

AVA is working 24/7 to improve your trading platform!
"""
            await update.message.reply_text(status_text, parse_mode='Markdown')

        except Exception as e:
            await update.message.reply_text(f"Error getting status: {str(e)}")

    async def handle_voice(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle voice messages"""
        if not self.voice_handler:
            await update.message.reply_text("Voice processing not available yet")
            return

        await update.message.reply_text("🎤 Transcribing your voice message...")

        try:
            # Download voice file
            voice_file = await update.message.voice.get_file()
            voice_path = f"temp_voice_{update.message.message_id}.ogg"
            await voice_file.download_to_drive(voice_path)

            # Transcribe
            transcribed_text = self.voice_handler.transcribe_voice(voice_path)

            if not transcribed_text:
                await update.message.reply_text("Sorry, couldn't transcribe your message")
                return

            # Show transcription
            await update.message.reply_text(f"📝 You said: *{transcribed_text}*", parse_mode='Markdown')

            # Process query
            response = self.voice_handler.process_query(transcribed_text)

            # Send response
            await update.message.reply_text(response['response_text'])

            # Cleanup
            if os.path.exists(voice_path):
                os.remove(voice_path)

        except Exception as e:
            logger.error(f"Error handling voice: {e}")
            await update.message.reply_text(f"Error processing voice: {str(e)}")

    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_text = update.message.text

        if not self.voice_handler:
            await update.message.reply_text("AVA is initializing... Try again in a moment")
            return

        # Process query
        response = self.voice_handler.process_query(user_text)
        response_text = response['response_text']

        # Try to generate voice response
        try:
            # Create temporary file for voice output
            with tempfile.NamedTemporaryFile(suffix='.wav', delete=False) as temp_voice:
                voice_path = temp_voice.name

            # Generate voice
            voice_success = self.voice_handler.generate_voice_response(response_text, voice_path)

            if voice_success and os.path.exists(voice_path):
                # Send voice message
                with open(voice_path, 'rb') as voice_file:
                    await update.message.reply_voice(voice=voice_file)

                # Cleanup
                os.remove(voice_path)
                logger.info(f"Sent voice response to user {update.effective_user.first_name}")
            else:
                # Fallback to text if voice generation failed
                await update.message.reply_text(response_text)
                logger.info(f"Sent text response (voice generation failed)")

        except Exception as e:
            logger.error(f"Error generating/sending voice: {e}")
            # Fallback to text
            await update.message.reply_text(response_text)

    def run(self):
        """Start the bot"""
        logger.info("🚀 Starting AVA Telegram Bot...")

        # Create application
        app = Application.builder().token(self.token).build()

        # Add handlers
        app.add_handler(CommandHandler("start", self.start_command))
        app.add_handler(CommandHandler("help", self.help_command))
        app.add_handler(CommandHandler("portfolio", self.portfolio_command))
        app.add_handler(CommandHandler("tasks", self.tasks_command))
        app.add_handler(CommandHandler("status", self.status_command))
        app.add_handler(CommandHandler("signals", self.signals_command))
        app.add_handler(CommandHandler("ticker", self.ticker_command))
        app.add_handler(MessageHandler(filters.VOICE, self.handle_voice))
        app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))

        # Start polling
        logger.info("✅ AVA Telegram Bot is running!")
        logger.info("Send a message to your bot to get your Chat ID")
        app.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point"""
    print("""
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║          🤖 AVA Telegram Bot - Starting... 🤖                    ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝

AVA is connecting to Telegram...

Once connected:
1. Open Telegram
2. Find your bot (search for the name you gave @BotFather)
3. Send /start to get your Chat ID
4. Try voice or text messages!

Examples:
• "How's my portfolio?"
• "What are you working on?"
• "Should I sell a put on AAPL?"

Press Ctrl+C to stop the bot
""")

    try:
        bot = AVATelegramBot()
        bot.run()
    except KeyboardInterrupt:
        print("\n\n👋 AVA Telegram Bot stopped")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
