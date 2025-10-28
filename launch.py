#!/usr/bin/env python
"""Launch the Wheel Strategy Trading System"""

import os
import sys
import webbrowser
import time
import subprocess
from pathlib import Path

print("="*60)
print("WHEEL STRATEGY TRADING SYSTEM")
print("Options Income Generation")
print("="*60)

# Create logs directory
Path('logs').mkdir(exist_ok=True)

print("\nStarting Streamlit Dashboard...")
print("-"*40)

# Launch Streamlit
try:
    # Start the dashboard
    process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "dashboard.py", "--server.headless", "true"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    # Wait a moment for server to start
    time.sleep(3)

    # Open browser
    url = "http://localhost:8501"
    print(f"\nOpening dashboard at: {url}")
    webbrowser.open(url)

    print("\n" + "="*60)
    print("SYSTEM IS RUNNING")
    print("="*60)
    print("\nDashboard: http://localhost:8501")
    print("Press Ctrl+C to stop")
    print("="*60 + "\n")

    # Keep running
    while True:
        line = process.stdout.readline()
        if line:
            print(f"[Dashboard] {line.strip()}")
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\nShutting down...")
    process.terminate()
    print("System stopped.")
except Exception as e:
    print(f"Error: {e}")
    print("\nTroubleshooting:")
    print("1. Make sure streamlit is installed: pip install streamlit")
    print("2. Check that dashboard.py exists in current directory")
    print("3. Ensure port 8501 is not in use")