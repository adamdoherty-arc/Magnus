"""
Start AVA Telegram Bot
======================

Launches AVA Telegram bot from project root to ensure .env loads correctly.
"""

import sys
from pathlib import Path

# Ensure we're in the right directory
import os
os.chdir(Path(__file__).parent)

# Load environment with override to ensure .env file values take precedence
from dotenv import load_dotenv
load_dotenv(override=True)

# Now run the bot
from src.ava.telegram_bot import main

if __name__ == "__main__":
    main()
