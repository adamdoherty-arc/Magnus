"""
Supply/Demand Zone Scanner Service
====================================

Main orchestration service that:
1. Detects supply/demand zones on watchlist stocks
2. Monitors prices for zone events
3. Sends alerts via Telegram
4. Logs all activity to database

Can run on-demand or scheduled (cron-style with APScheduler)

Usage:
    # Run once
    python supply_demand_scanner_service.py --run-once

    # Run scheduled (every 5 minutes)
    python supply_demand_scanner_service.py --scheduled

    # Scan specific symbol
    python supply_demand_scanner_service.py --symbol AAPL

    # Scan watchlist
    python supply_demand_scanner_service.py --watchlist my_watchlist
"""

import sys
import argparse
import time
import logging
from datetime import datetime
from typing import List, Dict, Optional
import yfinance as yf
import pandas as pd

# Add src to path
sys.path.insert(0, 'src')

from src.zone_detector import ZoneDetector
from src.zone_analyzer import ZoneAnalyzer
from src.zone_database_manager import ZoneDatabaseManager
from src.price_monitor import PriceMonitor
from src.alert_manager import AlertManager

logger = logging.getLogger(__name__)


class SupplyDemandScanner:
    """
    Supply/Demand Zone Scanner Service

    Orchestrates zone detection, price monitoring, and alerting
    """

    def __init__(
        self,
        enable_telegram: bool = True,
        min_strength_alert: int = 70,
        lookback_periods: int = 100
    ):
        """
        Initialize scanner service

        Args:
            enable_telegram: Enable Telegram alerts
            min_strength_alert: Minimum strength score for alerts (0-100)
            lookback_periods: Number of candles for zone detection
        """

        logger.info("Initializing Supply/Demand Zone Scanner...")

        # Initialize components
        self.db = ZoneDatabaseManager()
        self.detector = ZoneDetector(lookback_periods=lookback_periods)
        self.analyzer = ZoneAnalyzer()
        self.price_monitor = PriceMonitor(db_manager=self.db, zone_analyzer=self.analyzer)
        self.alert_manager = AlertManager(db_manager=self.db, enable_telegram=enable_telegram)

        self.min_strength_alert = min_strength_alert

        logger.info("✅ Scanner initialized successfully")

    def scan_symbol_for_zones(self, symbol: str) -> Dict:
        """
        Scan a single symbol for supply/demand zones

        Args:
            symbol: Stock ticker

        Returns:
            Dictionary with scan results
        """

        logger.info(f"Scanning {symbol} for zones...")

        try:
            # Fetch historical data
            ticker = yf.Ticker(symbol)
            df = ticker.history(period="6mo", interval="1d")

            if df.empty:
                logger.warning(f"{symbol}: No data available")
                return {'symbol': symbol, 'zones_found': 0, 'error': 'No data'}

            # Prepare dataframe
            df = df.reset_index()
            df.columns = [c.lower() for c in df.columns]
            df = df.rename(columns={'date': 'timestamp'})

            # Detect zones
            zones = self.detector.detect_zones(df, symbol)

            if not zones:
                logger.info(f"{symbol}: No zones detected")
                return {'symbol': symbol, 'zones_found': 0}

            # Get current price for analysis
            current_price = float(df['close'].iloc[-1])

            # Analyze zones
            analyzed_zones = []
            for zone in zones:
                analyzed_zone = self.analyzer.analyze_zone(zone, current_price)
                analyzed_zones.append(analyzed_zone)

            # Filter high-quality zones
            high_quality_zones = self.analyzer.get_high_priority_zones(
                analyzed_zones,
                min_strength=self.min_strength_alert,
                actions=['BUY', 'SELL', 'PREPARE']
            )

            # Save zones to database
            saved_zones = []
            for zone in analyzed_zones:
                # Check if zone already exists (avoid duplicates)
                existing_zones = self.db.get_zones_near_price(
                    symbol=symbol,
                    current_price=zone['zone_midpoint'],
                    distance_pct=1.0
                )

                # Check for very similar zones
                is_duplicate = False
                for existing in existing_zones:
                    if (abs(existing['zone_top'] - zone['zone_top']) < 0.5 and
                        abs(existing['zone_bottom'] - zone['zone_bottom']) < 0.5):
                        is_duplicate = True
                        break

                if not is_duplicate:
                    zone_id = self.db.save_zone(zone)
                    saved_zones.append(zone_id)

            logger.info(f"{symbol}: Detected {len(zones)} zones, saved {len(saved_zones)} new zones")

            return {
                'symbol': symbol,
                'zones_found': len(zones),
                'zones_saved': len(saved_zones),
                'high_quality_zones': len(high_quality_zones),
                'zones': high_quality_zones
            }

        except Exception as e:
            logger.error(f"Error scanning {symbol}: {e}")
            return {'symbol': symbol, 'zones_found': 0, 'error': str(e)}

    def monitor_symbol_for_events(self, symbol: str) -> List[Dict]:
        """
        Monitor symbol for zone events and send alerts

        Args:
            symbol: Stock ticker

        Returns:
            List of events detected
        """

        logger.info(f"Monitoring {symbol} for zone events...")

        try:
            events = self.price_monitor.monitor_symbol(symbol)

            if events:
                logger.info(f"{symbol}: Detected {len(events)} events")

                # Send alerts for high-priority events
                for event in events:
                    if event['priority'] in ['HIGH', 'MEDIUM']:
                        self.alert_manager.send_zone_event_alert_sync(event)

            return events

        except Exception as e:
            logger.error(f"Error monitoring {symbol}: {e}")
            return []

    def scan_watchlist(self, watchlist_name: str = "default") -> Dict:
        """
        Scan all stocks in a TradingView watchlist

        Args:
            watchlist_name: Watchlist name

        Returns:
            Dictionary with scan summary
        """

        start_time = time.time()
        logger.info(f"Scanning watchlist: {watchlist_name}")

        # Get watchlist symbols from database
        query = """
            SELECT DISTINCT ticker
            FROM tradingview_watchlist_stocks
            WHERE watchlist_name = %s
            ORDER BY ticker
        """

        try:
            with self.db.get_connection() as conn:
                with conn.cursor() as cursor:
                    cursor.execute(query, (watchlist_name,))
                    symbols = [row[0] for row in cursor.fetchall()]
        except Exception as e:
            logger.error(f"Error fetching watchlist: {e}")
            # Fallback to common stocks if database not available
            symbols = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY', 'QQQ']
            logger.info(f"Using fallback symbols: {symbols}")

        if not symbols:
            logger.warning(f"No symbols in watchlist '{watchlist_name}'")
            return {'watchlist': watchlist_name, 'symbols_scanned': 0}

        logger.info(f"Found {len(symbols)} symbols in watchlist")

        # Scan each symbol
        total_zones_found = 0
        total_zones_saved = 0
        total_events = 0
        scan_results = []

        for i, symbol in enumerate(symbols, 1):
            logger.info(f"[{i}/{len(symbols)}] Processing {symbol}...")

            # Scan for zones
            scan_result = self.scan_symbol_for_zones(symbol)
            scan_results.append(scan_result)

            total_zones_found += scan_result.get('zones_found', 0)
            total_zones_saved += scan_result.get('zones_saved', 0)

            # Monitor for events
            events = self.monitor_symbol_for_events(symbol)
            total_events += len(events)

            # Small delay to avoid rate limiting
            time.sleep(0.5)

        duration = time.time() - start_time

        # Log scan to database
        log_data = {
            'scan_type': 'ZONE_DETECTION',
            'tickers_scanned': len(symbols),
            'zones_found': total_zones_found,
            'zones_updated': total_zones_saved,
            'alerts_sent': total_events,
            'duration_seconds': duration,
            'status': 'success'
        }

        self.db.log_scan(log_data)

        summary = {
            'watchlist': watchlist_name,
            'symbols_scanned': len(symbols),
            'zones_found': total_zones_found,
            'zones_saved': total_zones_saved,
            'events_detected': total_events,
            'duration_seconds': duration,
            'results': scan_results
        }

        logger.info(f"Scan complete: {len(symbols)} symbols, {total_zones_found} zones found, {total_events} events")

        return summary

    def monitor_all_zones(self) -> Dict:
        """
        Monitor all active zones for price events

        Returns:
            Dictionary with monitoring summary
        """

        start_time = time.time()
        logger.info("Monitoring all active zones...")

        events_by_symbol = self.price_monitor.monitor_all_active_zones()

        total_events = sum(len(events) for events in events_by_symbol.values())

        # Send alerts
        for symbol, events in events_by_symbol.items():
            for event in events:
                if event['priority'] in ['HIGH', 'MEDIUM']:
                    self.alert_manager.send_zone_event_alert_sync(event)

        duration = time.time() - start_time

        # Log monitoring scan
        log_data = {
            'scan_type': 'PRICE_MONITORING',
            'tickers_scanned': len(events_by_symbol),
            'zones_found': 0,
            'zones_updated': 0,
            'alerts_sent': total_events,
            'duration_seconds': duration,
            'status': 'success'
        }

        self.db.log_scan(log_data)

        logger.info(f"Monitoring complete: {len(events_by_symbol)} symbols, {total_events} events")

        return {
            'symbols_monitored': len(events_by_symbol),
            'events_detected': total_events,
            'duration_seconds': duration,
            'events_by_symbol': events_by_symbol
        }

    def cleanup_old_zones(self, days: int = 90):
        """
        Deactivate zones older than N days

        Args:
            days: Age threshold in days
        """

        logger.info(f"Cleaning up zones older than {days} days...")

        count = self.db.deactivate_old_zones(days)

        # Log cleanup scan
        log_data = {
            'scan_type': 'ZONE_CLEANUP',
            'tickers_scanned': 0,
            'zones_found': 0,
            'zones_updated': count,
            'alerts_sent': 0,
            'duration_seconds': 0,
            'status': 'success'
        }

        self.db.log_scan(log_data)

        logger.info(f"Cleanup complete: {count} zones deactivated")


def main():
    """Main entry point"""

    parser = argparse.ArgumentParser(description='Supply/Demand Zone Scanner')

    parser.add_argument('--run-once', action='store_true',
                       help='Run scan once and exit')
    parser.add_argument('--scheduled', action='store_true',
                       help='Run on schedule (every 5 minutes)')
    parser.add_argument('--symbol', type=str,
                       help='Scan specific symbol')
    parser.add_argument('--watchlist', type=str, default='default',
                       help='Scan TradingView watchlist')
    parser.add_argument('--monitor-only', action='store_true',
                       help='Only monitor existing zones (no detection)')
    parser.add_argument('--no-telegram', action='store_true',
                       help='Disable Telegram alerts')
    parser.add_argument('--cleanup', type=int, metavar='DAYS',
                       help='Cleanup zones older than N days')

    args = parser.parse_args()

    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )

    # Initialize scanner
    scanner = SupplyDemandScanner(enable_telegram=not args.no_telegram)

    try:
        # Cleanup mode
        if args.cleanup:
            scanner.cleanup_old_zones(days=args.cleanup)
            return

        # Single symbol mode
        if args.symbol:
            logger.info(f"Single symbol mode: {args.symbol}")
            scan_result = scanner.scan_symbol_for_zones(args.symbol)
            print(f"\nScan Results:")
            print(f"  Zones Found: {scan_result.get('zones_found', 0)}")
            print(f"  Zones Saved: {scan_result.get('zones_saved', 0)}")

            events = scanner.monitor_symbol_for_events(args.symbol)
            print(f"  Events: {len(events)}")
            return

        # Monitor-only mode
        if args.monitor_only:
            logger.info("Monitor-only mode")
            summary = scanner.monitor_all_zones()
            print(f"\nMonitoring Results:")
            print(f"  Symbols Monitored: {summary['symbols_monitored']}")
            print(f"  Events Detected: {summary['events_detected']}")
            return

        # Watchlist scan mode
        if args.run_once or not args.scheduled:
            logger.info(f"Running single scan on watchlist: {args.watchlist}")
            summary = scanner.scan_watchlist(args.watchlist)

            print(f"\n{'='*60}")
            print(f"Scan Summary")
            print(f"{'='*60}")
            print(f"Watchlist: {summary['watchlist']}")
            print(f"Symbols Scanned: {summary['symbols_scanned']}")
            print(f"Zones Found: {summary['zones_found']}")
            print(f"Zones Saved: {summary['zones_saved']}")
            print(f"Events Detected: {summary['events_detected']}")
            print(f"Duration: {summary['duration_seconds']:.1f}s")
            print(f"{'='*60}\n")

            return

        # Scheduled mode
        if args.scheduled:
            logger.info("Starting scheduled scanner (every 5 minutes)")
            logger.info("Press Ctrl+C to stop")

            try:
                from apscheduler.schedulers.blocking import BlockingScheduler
                from apscheduler.triggers.interval import IntervalTrigger

                scheduler = BlockingScheduler()

                # Zone detection scan (every 1 hour)
                scheduler.add_job(
                    lambda: scanner.scan_watchlist(args.watchlist),
                    IntervalTrigger(hours=1),
                    id='zone_detection',
                    name='Zone Detection Scan'
                )

                # Price monitoring (every 5 minutes)
                scheduler.add_job(
                    scanner.monitor_all_zones,
                    IntervalTrigger(minutes=5),
                    id='price_monitoring',
                    name='Price Monitoring'
                )

                # Cleanup old zones (daily at 2 AM)
                scheduler.add_job(
                    lambda: scanner.cleanup_old_zones(90),
                    'cron',
                    hour=2,
                    minute=0,
                    id='cleanup',
                    name='Zone Cleanup'
                )

                scheduler.start()

            except ImportError:
                logger.error("APScheduler not installed. Run: pip install apscheduler")
                logger.info("Falling back to simple loop...")

                # Simple loop fallback
                while True:
                    scanner.scan_watchlist(args.watchlist)
                    scanner.monitor_all_zones()

                    logger.info("Waiting 5 minutes until next scan...")
                    time.sleep(300)  # 5 minutes

    except KeyboardInterrupt:
        logger.info("\n\nShutting down scanner...")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
