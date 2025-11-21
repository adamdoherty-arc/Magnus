"""
Autonomous Agent Launcher
=========================

Starts the autonomous AI agent that continuously works through
enhancement tasks from the database.

THIS WILL RUN INDEFINITELY until stopped with Ctrl+C or budget limit reached.
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from src.ai_continuous_improvement.autonomous_agent import main

if __name__ == "__main__":
    print("""
╔══════════════════════════════════════════════════════════════════════╗
║                                                                      ║
║           🤖 AUTONOMOUS AI AGENT - CONTINUOUS MODE 🤖                ║
║                                                                      ║
║  This agent will continuously work through tasks from the database,  ║
║  implementing enhancements 24/7 without stopping.                    ║
║                                                                      ║
║  Features:                                                           ║
║  • Database-driven task queue                                        ║
║  • Automatic priority selection                                      ║
║  • Specialized agent routing                                         ║
║  • Progress tracking                                                 ║
║  • Cost control and rate limiting                                    ║
║                                                                      ║
║  Press Ctrl+C to stop gracefully                                     ║
║                                                                      ║
╚══════════════════════════════════════════════════════════════════════╝

Usage Examples:

1. Run with defaults (10 tasks/hour, $10 budget):
   python start_autonomous_agent.py

2. Higher throughput (20 tasks/hour):
   python start_autonomous_agent.py --max-tasks-per-hour 20

3. With approval gates (review each task):
   python start_autonomous_agent.py --require-approval

4. Higher budget ($50):
   python start_autonomous_agent.py --budget-limit 50.0

5. Test single task:
   python start_autonomous_agent.py --single-task

Current configuration loading...
    """)

    main()
