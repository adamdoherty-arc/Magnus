"""
Xtrades Monitoring Service Launcher
====================================

Quick start script for the Xtrades real-time monitoring service.

Usage:
    python start_xtrades_monitor.py                    # Start continuous monitoring
    python start_xtrades_monitor.py --test             # Run single test cycle
    python start_xtrades_monitor.py --interval 300     # Custom interval (5 minutes)
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.xtrades_monitor.monitoring_service import main

if __name__ == "__main__":
    print("""
╔═══════════════════════════════════════════════════════════════╗
║                                                               ║
║   🚀 Xtrades Real-Time Monitoring Service                    ║
║                                                               ║
║   Features:                                                   ║
║   • Auto-scrape Xtrades every 2.5 minutes                    ║
║   • Multi-strategy AI evaluation (10 strategies)             ║
║   • Multi-model consensus (Claude + DeepSeek + Gemini)       ║
║   • Telegram alerts for high-quality trades (score >= 80)    ║
║   • Smart rate limiting (max 5 alerts/hour)                  ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
    """)

    main()
