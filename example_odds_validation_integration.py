"""
Example: Integrating Odds Validation into Existing Code

This example shows how to add validation to your existing
Kalshi odds fetching and display logic.
"""

import os
import sys
from datetime import datetime
from typing import List, Dict

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.odds_validator import validate_kalshi_market, ValidationSeverity
from src.odds_alert_system import send_odds_alert, AlertChannel


# Database configuration
DB_CONFIG = {
    'host': 'localhost',
    'port': '5432',
    'database': 'magnus',
    'user': 'postgres',
    'password': os.getenv('DB_PASSWORD')
}

# Alert channels configuration
ALERT_CHANNELS = [
    AlertChannel(name='console', enabled=True, config={}),
    # Uncomment to enable email alerts:
    # AlertChannel(
    #     name='email',
    #     enabled=True,
    #     config={
    #         'smtp_host': 'smtp.gmail.com',
    #         'smtp_port': 587,
    #         'smtp_user': 'your@email.com',
    #         'smtp_password': 'your_app_password',
    #         'from_email': 'alerts@trading.com',
    #         'to_emails': ['admin@trading.com']
    #     }
    # )
]


def validate_and_filter_games(games: List[Dict]) -> List[Dict]:
    """
    Validate odds for all games and filter out games with critical issues

    Args:
        games: List of games with Kalshi odds

    Returns:
        List of games with validated odds only
    """
    validated_games = []

    for game in games:
        kalshi_odds = game.get('kalshi_odds')

        if not kalshi_odds:
            # No odds to validate
            validated_games.append(game)
            continue

        # Extract game data
        ticker = kalshi_odds.get('ticker')
        away_team = game.get('away_team')
        home_team = game.get('home_team')
        away_win_price = kalshi_odds.get('away_win_price')
        home_win_price = kalshi_odds.get('home_win_price')
        away_record = game.get('away_record')
        home_record = game.get('home_record')

        # Validate odds
        is_valid, results = validate_kalshi_market(
            ticker=ticker,
            away_team=away_team,
            home_team=home_team,
            away_win_price=away_win_price,
            home_win_price=home_win_price,
            db_config=DB_CONFIG,
            away_record=away_record,
            home_record=home_record,
            last_updated=datetime.now()
        )

        # Add validation status to game
        game['odds_validated'] = is_valid

        if is_valid:
            # Odds are valid - safe to display
            validated_games.append(game)
            print(f"✅ {away_team} @ {home_team}: Odds validated")
        else:
            # Critical issues detected
            print(f"❌ {away_team} @ {home_team}: CRITICAL validation failure")

            # Log critical issues
            critical_issues = [
                r for r in results
                if not r.passed and r.severity == ValidationSeverity.CRITICAL
            ]

            for issue in critical_issues:
                print(f"   - {issue.message}")

            # Send alerts
            alert_ids = send_odds_alert(
                ticker=ticker,
                away_team=away_team,
                home_team=home_team,
                away_win_price=away_win_price,
                home_win_price=home_win_price,
                validation_results=results,
                db_config=DB_CONFIG,
                alert_channels=ALERT_CHANNELS
            )

            if alert_ids:
                print(f"   📧 Alert(s) created: {alert_ids}")

            # Remove invalid odds from game
            game['kalshi_odds'] = None
            game['odds_validated'] = False

            # Still include game in list (just without odds)
            validated_games.append(game)

    return validated_games


def example_usage():
    """Example of how to use the validation system"""

    print("\n" + "="*80)
    print("ODDS VALIDATION - Example Usage")
    print("="*80 + "\n")

    # Example 1: Valid odds
    print("Example 1: Valid Odds\n")
    games_valid = [
        {
            'away_team': 'Dallas Cowboys',
            'home_team': 'Philadelphia Eagles',
            'away_record': '7-3',
            'home_record': '9-1',
            'kalshi_odds': {
                'ticker': 'KXNFL-DAL-PHI',
                'away_win_price': 0.45,
                'home_win_price': 0.55,
                'volume': 50000
            }
        }
    ]

    validated = validate_and_filter_games(games_valid)
    print(f"\nResult: {len(validated)} game(s) with validated odds\n")

    # Example 2: REVERSED odds (should be caught)
    print("\n" + "-"*80)
    print("Example 2: REVERSED Odds (Critical Issue)\n")

    games_reversed = [
        {
            'away_team': 'Buffalo Bills',
            'home_team': 'New York Jets',
            'away_record': '9-1',  # Better team
            'home_record': '3-7',  # Worse team
            'kalshi_odds': {
                'ticker': 'KXNFL-BUF-NYJ',
                'away_win_price': 0.35,  # WRONG: Better team has lower odds!
                'home_win_price': 0.65,  # WRONG: Worse team has higher odds!
                'volume': 25000
            }
        }
    ]

    validated = validate_and_filter_games(games_reversed)
    print(f"\nResult: {len(validated)} game(s), but odds were REMOVED due to critical issue\n")

    # Example 3: Invalid probability sum
    print("\n" + "-"*80)
    print("Example 3: Invalid Probability Sum\n")

    games_invalid_sum = [
        {
            'away_team': 'Kansas City Chiefs',
            'home_team': 'Las Vegas Raiders',
            'away_record': '8-2',
            'home_record': '5-5',
            'kalshi_odds': {
                'ticker': 'KXNFL-KC-LV',
                'away_win_price': 0.40,  # Sum = 0.80 (too low!)
                'home_win_price': 0.40,
                'volume': 30000
            }
        }
    ]

    validated = validate_and_filter_games(games_invalid_sum)
    print(f"\nResult: {len(validated)} game(s), odds validation status checked\n")

    print("="*80)
    print("Example Complete!")
    print("="*80)
    print("\nKey Takeaways:")
    print("1. ✅ Valid odds pass all checks and are displayed")
    print("2. ❌ CRITICAL failures (reversed odds, invalid sums) block display")
    print("3. ⚠️  Warnings are logged but don't block display")
    print("4. 📧 Automated alerts are sent for critical issues")
    print("5. 📊 All validations are logged in database for monitoring")


def example_with_real_kalshi_data():
    """
    Example showing integration with real Kalshi data fetching

    In your actual code, replace mock data with real API calls
    """
    print("\n" + "="*80)
    print("REAL-WORLD INTEGRATION EXAMPLE")
    print("="*80 + "\n")

    # Step 1: Fetch games from ESPN (your existing code)
    print("Step 1: Fetching ESPN games...")
    # espn_games = get_espn_live_scores()  # Your existing function

    # Step 2: Enrich with Kalshi odds (your existing code)
    print("Step 2: Enriching with Kalshi odds...")
    # from src.espn_kalshi_matcher import enrich_games_with_kalshi_odds
    # games_with_odds = enrich_games_with_kalshi_odds(espn_games)

    # Step 3: NEW - Validate odds before displaying
    print("Step 3: Validating odds (NEW STEP)...")
    # validated_games = validate_and_filter_games(games_with_odds)

    # Step 4: Display only validated games
    print("Step 4: Displaying validated games...")
    # for game in validated_games:
    #     if game['odds_validated']:
    #         # Safe to display Kalshi odds
    #         display_game_with_odds(game)
    #     else:
    #         # Display game without odds (use AI predictions instead)
    #         display_game_without_odds(game)

    print("\n✅ Integration complete! Your users will never see reversed odds.")


if __name__ == "__main__":
    # Run examples
    example_usage()
    print("\n")
    example_with_real_kalshi_data()

    print("\n" + "="*80)
    print("Next Steps:")
    print("="*80)
    print("1. Install database schema: psql -f src/odds_data_quality_schema.sql")
    print("2. Run unit tests: pytest tests/test_odds_validator.py -v")
    print("3. Launch dashboard: streamlit run odds_data_quality_dashboard.py")
    print("4. Integrate validation into your Kalshi odds fetching code")
    print("5. Set up email/Slack alerts for your team")
    print("\n" + "="*80)
