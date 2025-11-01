"""
Quick import test to verify all agents are properly configured
"""

import sys
from pathlib import Path

# Add src directory to Python path
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

try:
    print("Testing imports...")
    print(f"Python path includes: {project_root}")

    # Test package import
    from agents.ai_research import (
        FundamentalAgent,
        TechnicalAgent,
        SentimentAgent,
        OptionsAgent,
        FundamentalAnalysis,
        TechnicalAnalysis,
        SentimentAnalysis,
        OptionsAnalysis,
        TrendDirection,
        SignalType,
        SentimentType
    )
    print("[OK] All agents and models imported from package successfully")

    # Test agent initialization
    fundamental = FundamentalAgent()
    print(f"[OK] FundamentalAgent initialized: {fundamental.__class__.__name__}")

    technical = TechnicalAgent()
    print(f"[OK] TechnicalAgent initialized: {technical.__class__.__name__}")

    sentiment = SentimentAgent()
    print(f"[OK] SentimentAgent initialized: {sentiment.__class__.__name__}")

    options = OptionsAgent()
    print(f"[OK] OptionsAgent initialized: {options.__class__.__name__}")

    print("\n" + "="*60)
    print("SUCCESS: All agents are properly configured!")
    print("="*60)
    print("\nNext steps:")
    print("1. Set environment variables:")
    print("   set ALPHA_VANTAGE_API_KEY=your_key")
    print("   set REDDIT_CLIENT_ID=your_id (optional)")
    print("   set REDDIT_CLIENT_SECRET=your_secret (optional)")
    print("\n2. Install optional dependencies:")
    print("   pip install pandas-ta mibian praw")
    print("\n3. Run example:")
    print("   python example_usage.py")

except ImportError as e:
    print(f"\n[ERROR] Import Error: {e}")
    print("\nMake sure all dependencies are installed:")
    print("  pip install yfinance pandas numpy scipy loguru aiohttp")
    sys.exit(1)

except Exception as e:
    print(f"\n[ERROR] Unexpected Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
