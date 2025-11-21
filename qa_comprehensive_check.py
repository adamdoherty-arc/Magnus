"""Comprehensive QA Check - All Features"""
import sys
sys.path.insert(0, 'c:\Code\WheelStrategy')

from src.tradingview_db_manager import TradingViewDBManager
from src.csp_opportunities_finder import CSPOpportunitiesFinder
import os

def print_section(title):
    print("\n" + "=" * 80)
    print(f"{title}")
    print("=" * 80)

def check_database_tables():
    """Check if all required database tables exist and have data"""
    print_section("1. DATABASE TABLES CHECK")

    tv_manager = TradingViewDBManager()
    conn = tv_manager.get_connection()
    cur = conn.cursor()

    tables_to_check = [
        'stock_data',
        'stock_premiums',
        'tradingview_watchlists',
        'tradingview_stocks',
        'stock_sectors',
        'sector_analysis',
        'sector_etfs',
        'options_flow',
        'options_flow_analysis'
    ]

    results = []
    for table in tables_to_check:
        cur.execute(f"SELECT COUNT(*) FROM {table}")
        count = cur.fetchone()[0]
        status = "OK" if count > 0 else "EMPTY"
        results.append((table, count, status))
        print(f"  {table:30} {count:>8,} rows  [{status}]")

    cur.close()
    conn.close()
    return results

def check_csp_opportunities():
    """Check CSP Opportunities Finder"""
    print_section("2. CSP OPPORTUNITIES FINDER")

    finder = CSPOpportunitiesFinder()
    test_symbols = ['BMNR', 'UPST', 'CIFR', 'HIMS']

    try:
        opps = finder.find_opportunities_for_symbols(test_symbols)
        if not opps.empty:
            print(f"  Status: OK - Found {len(opps)} opportunities")
            print(f"  Avg Monthly Return: {opps['Monthly %'].mean():.2f}%")
            return True
        else:
            print(f"  Status: FAIL - No opportunities found")
            return False
    except Exception as e:
        print(f"  Status: ERROR - {e}")
        return False

def main():
    print("=" * 80)
    print("MAGNUS DASHBOARD - COMPREHENSIVE QA CHECK")
    print("=" * 80)

    table_results = check_database_tables()
    csp_ok = check_csp_opportunities()

    print("\n" + "=" * 80)
    print("SUMMARY")
    print("=" * 80)
    
    empty_tables = [t[0] for t in table_results if t[2] == "EMPTY"]
    print(f"Empty tables: {len(empty_tables)}")
    for t in empty_tables:
        print(f"  - {t}")
    
    print(f"\nCSP Opportunities: {'WORKING' if csp_ok else 'BROKEN'}")

if __name__ == "__main__":
    main()
