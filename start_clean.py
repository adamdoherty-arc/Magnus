#!/usr/bin/env python
"""Startup script for Wheel Strategy Trading System"""

import os
import sys
import subprocess
import time
import json
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def check_dependencies():
    """Check if required services are running"""
    print("Checking dependencies...")

    # Check Redis
    try:
        import redis
        r = redis.Redis(host='localhost', port=6379)
        r.ping()
        print("OK: Redis is running")
    except:
        print("WARNING: Redis is not running. Starting Redis...")
        try:
            subprocess.Popen(['redis-server'], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            time.sleep(2)
            print("OK: Redis started")
        except:
            print("WARNING: Please install and start Redis manually")
            print("   Windows: Download from https://github.com/microsoftarchive/redis/releases")
            print("   Mac: brew install redis && brew services start redis")
            print("   Linux: sudo apt-get install redis-server && sudo service redis-server start")
            return False

    # Check PostgreSQL (optional for now)
    try:
        import psycopg2
        # Try to get credentials from environment or use defaults
        db_config = {
            "host": os.getenv('PGHOST', 'localhost'),
            "database": os.getenv('PGDATABASE', 'wheel_strategy'),
            "user": os.getenv('PGUSER', 'postgres'),
            "password": os.getenv('PGPASSWORD', 'postgres123!')
        }
        conn = psycopg2.connect(**db_config)
        conn.close()
        print("OK: PostgreSQL is connected")
    except ImportError:
        print("WARNING: PostgreSQL driver not installed (pip install psycopg2-binary)")
        print("   System will use Redis for data storage (limited historical data)")
    except Exception as e:
        print("WARNING: PostgreSQL not configured (optional)")
        print("   System will use Redis only (limited to recent data)")
        print("\n   To enable PostgreSQL for full features:")
        print("   1. Install PostgreSQL: https://www.postgresql.org/download/")
        print("   2. Run setup script:")
        print("      Windows: setup_postgres.bat")
        print("      Mac/Linux: ./setup_postgres.sh")
        print("   3. Or manually create database:")
        print("      createdb wheel_strategy")
        print("      psql -d wheel_strategy -f database_schema.sql")

    return True

def create_default_config():
    """Create default config if not exists"""
    config_path = Path('config.json')

    if not config_path.exists():
        print("Creating default configuration...")

        default_config = {
            "starting_capital": 50000,
            "max_stock_price": 50.0,
            "watchlist": [
                "F", "INTC", "T", "KO", "PFE", "BAC",
                "PLTR", "SOFI", "NIO", "BB"
            ],
            "strategy_params": {
                "min_premium_yield": 0.01,
                "target_delta": 0.30,
                "min_dte": 21,
                "max_dte": 45
            },
            "alert_channels": ["console"],
            "redis": {
                "host": "localhost",
                "port": 6379,
                "db": 0
            }
        }

        with open(config_path, 'w') as f:
            json.dump(default_config, f, indent=2)

        print("OK: Default config created")
    else:
        print("OK: Config file exists")

def install_requirements():
    """Install Python requirements if needed"""
    missing_packages = []

    # Check core packages
    required_packages = {
        'fastapi': 'fastapi',
        'streamlit': 'streamlit',
        'yfinance': 'yfinance',
        'redis': 'redis',
        'pandas': 'pandas',
        'loguru': 'loguru'
    }

    for module_name, package_name in required_packages.items():
        try:
            __import__(module_name)
        except ImportError:
            missing_packages.append(package_name)

    if not missing_packages:
        print("OK: Python dependencies installed")
        return True

    print(f"Installing missing packages: {', '.join(missing_packages)}")

    # Try to install missing packages
    for package in missing_packages:
        try:
            subprocess.check_call(
                [sys.executable, "-m", "pip", "install", package],
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL
            )
            print(f"   OK: {package} installed")
        except:
            print(f"   WARNING: Failed to install {package}")

    # Verify installation
    critical_missing = []
    for module_name in ['streamlit', 'yfinance', 'pandas']:
        try:
            __import__(module_name)
        except ImportError:
            critical_missing.append(module_name)

    if critical_missing:
        print(f"\nWARNING: Critical packages missing: {', '.join(critical_missing)}")
        print("Please install manually:")
        print(f"   pip install {' '.join(critical_missing)}")
        return False

    return True

def start_system():
    """Start the main system and dashboard"""
    print("\nStarting Wheel Strategy Trading System...\n")

    # Start main application
    print("Starting trading system...")
    main_process = subprocess.Popen(
        [sys.executable, "src/main.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        universal_newlines=True
    )

    time.sleep(3)

    # Start Streamlit dashboard
    print("Starting web dashboard...")
    dashboard_process = subprocess.Popen(
        [sys.executable, "-m", "streamlit", "run", "dashboard.py"],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print("\n" + "="*60)
    print("WHEEL STRATEGY TRADING SYSTEM IS RUNNING")
    print("="*60)
    print("\nDashboard: http://localhost:8501")
    print("Logs: logs/wheel_strategy.log")
    print("Press Ctrl+C to stop\n")
    print("="*60 + "\n")

    try:
        # Keep running until interrupted
        while True:
            # Print main process output
            line = main_process.stdout.readline()
            if line:
                print(f"[System] {line.strip()}")
            time.sleep(0.1)

    except KeyboardInterrupt:
        print("\nShutting down...")
        main_process.terminate()
        dashboard_process.terminate()
        print("OK: System stopped")

def main():
    """Main entry point"""
    print("")
    print("WHEEL STRATEGY TRADING SYSTEM")
    print("="*40)
    print("Premium Income Generation Through")
    print("Cash-Secured Puts & Covered Calls")
    print("="*40 + "\n")

    # Create logs directory
    Path('logs').mkdir(exist_ok=True)

    # Check and setup
    if not check_dependencies():
        print("\nWARNING: Please fix dependency issues and try again")
        sys.exit(1)

    create_default_config()

    if not install_requirements():
        print("\nWARNING: Please install missing dependencies and try again")
        print("\nRecommended approach:")
        print("  1. Run: setup.bat (to create virtual environment)")
        print("  2. Run: run.bat (to start with venv)")
        sys.exit(1)

    # Start system
    start_system()

if __name__ == "__main__":
    main()