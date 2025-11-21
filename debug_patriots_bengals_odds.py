"""
Debug Patriots vs Bengals Kalshi Odds Assignment
================================================

This script traces through the exact logic to see if odds are being assigned correctly.
"""

# Actual market data from database
market_cin = {
    'ticker': 'KXNFLGAME-25NOV23NECIN-CIN',
    'title': 'New England at Cincinnati Winner?',
    'yes_price': 0.23,  # YES = Bengals win
    'no_price': 0.77    # NO = Patriots win
}

market_ne = {
    'ticker': 'KXNFLGAME-25NOV23NECIN-NE',
    'title': 'New England at Cincinnati Winner?',
    'yes_price': 0.79,  # YES = Patriots win
    'no_price': 0.21    # NO = Bengals win
}

# Game info
away_team = "New England Patriots"  # 9-2 record
home_team = "Cincinnati Bengals"    # 3-7 record

print("="*80)
print("PATRIOTS vs BENGALS - KALSHI ODDS ASSIGNMENT DEBUG")
print("="*80)

print(f"\nGame: {away_team} (AWAY) @ {home_team} (HOME)")
print(f"Records: Patriots 9-2 vs Bengals 3-7")
print(f"\nExpected: Patriots should be heavily favored (~75-80%)")

print("\n" + "="*80)
print("MARKET 1: KXNFLGAME-25NOV23NECIN-CIN")
print("="*80)

ticker_suffix = 'cin'
print(f"Ticker suffix: {ticker_suffix}")
print(f"YES price: {market_cin['yes_price']} (23 cents) = Bengals WIN")
print(f"NO price: {market_cin['no_price']} (77 cents) = Patriots WIN")

# Match logic from espn_kalshi_matcher.py line 224-245
# Check if ticker suffix matches away team
away_is_yes = False
if ticker_suffix.lower() in ['ne', 'new england', 'patriots']:
    away_is_yes = True
elif ticker_suffix.lower() in ['cin', 'cincinnati', 'bengals']:
    away_is_yes = False

print(f"\nDoes suffix match AWAY team (Patriots)? {away_is_yes}")

if away_is_yes:
    away_price = market_cin['yes_price']
    home_price = market_cin['no_price']
else:
    away_price = market_cin['no_price']
    home_price = market_cin['yes_price']

print(f"\nAssigned odds:")
print(f"  away_price (Patriots) = {away_price} ({away_price*100:.0f} cents)")
print(f"  home_price (Bengals) = {home_price} ({home_price*100:.0f} cents)")

print(f"\nRESULT: Patriots {away_price*100:.0f}%, Bengals {home_price*100:.0f}%")
if away_price > home_price:
    print("CORRECT: Patriots favored (matches their 9-2 record)")
else:
    print("ERROR: Bengals favored (doesn't match their 3-7 record!)")

print("\n" + "="*80)
print("MARKET 2: KXNFLGAME-25NOV23NECIN-NE")
print("="*80)

ticker_suffix_2 = 'ne'
print(f"Ticker suffix: {ticker_suffix_2}")
print(f"YES price: {market_ne['yes_price']} (79 cents) = Patriots WIN")
print(f"NO price: {market_ne['no_price']} (21 cents) = Bengals WIN")

# Check if ticker suffix matches away team
away_is_yes_2 = False
if ticker_suffix_2.lower() in ['ne', 'new england', 'patriots']:
    away_is_yes_2 = True

print(f"\nDoes suffix match AWAY team (Patriots)? {away_is_yes_2}")

if away_is_yes_2:
    away_price_2 = market_ne['yes_price']
    home_price_2 = market_ne['no_price']
else:
    away_price_2 = market_ne['no_price']
    home_price_2 = market_ne['yes_price']

print(f"\nAssigned odds:")
print(f"  away_price (Patriots) = {away_price_2} ({away_price_2*100:.0f} cents)")
print(f"  home_price (Bengals) = {home_price_2} ({home_price_2*100:.0f} cents)")

print(f"\nRESULT: Patriots {away_price_2*100:.0f}%, Bengals {home_price_2*100:.0f}%")
if away_price_2 > home_price_2:
    print("CORRECT: Patriots favored (matches their 9-2 record)")
else:
    print("ERROR: Bengals favored (doesn't match their 3-7 record!)")

print("\n" + "="*80)
print("COMPARISON")
print("="*80)
print(f"Market 1 (-CIN): Patriots {away_price*100:.0f}%, Bengals {home_price*100:.0f}%")
print(f"Market 2 (-NE):  Patriots {away_price_2*100:.0f}%, Bengals {home_price_2*100:.0f}%")
print(f"\nDifference: {abs(away_price - away_price_2)*100:.0f} cents")

print("\n" + "="*80)
print("SCREENSHOT SHOWS:")
print("="*80)
print("Patriots: 77 cents")
print("Bengals: 23 cents")
print("\nThis matches MARKET 1 (-CIN) assignment")
print("So Kalshi odds are being assigned CORRECTLY!")

print("\n" + "="*80)
print("THE REAL PROBLEM:")
print("="*80)
print("The AI is predicting Bengals win with 78% probability")
print("This contradicts BOTH:")
print("  1. Kalshi market odds (Patriots 77%)")
print("  2. Team records (Patriots 9-2 vs Bengals 3-7)")
print("\nROOT CAUSE: Outdated Elo ratings")
print("  Bengals Elo: 1545 (ranked #15)")
print("  Patriots Elo: 1455 (ranked #28)")
print("  ^ These are BACKWARDS based on current records!")
