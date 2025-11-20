"""
Supply/Demand Zones Dashboard Page
===================================

Interactive dashboard for viewing and managing supply/demand zones.

Features:
- View active zones by ticker
- Monitor current opportunities (price near zones)
- View zone statistics and performance
- Recent alerts history
- Manual scan triggers
- Zone visualization with charts
"""

import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import sys
from datetime import datetime, timedelta
import yfinance as yf
from dotenv import load_dotenv

# Load environment variables FIRST before any imports that use them
load_dotenv()

# Add src to path
sys.path.insert(0, 'src')

from src.zone_database_manager import ZoneDatabaseManager
from src.zone_detector import ZoneDetector
from src.zone_analyzer import ZoneAnalyzer
from src.price_monitor import PriceMonitor

# Page config
st.set_page_config(
    page_title="Supply/Demand Zones",
    page_icon="📊",
    layout="wide"
)

# Initialize components
@st.cache_resource
def get_db_manager():
    return ZoneDatabaseManager()

@st.cache_resource
def get_zone_detector():
    return ZoneDetector()

@st.cache_resource
def get_zone_analyzer():
    return ZoneAnalyzer()

@st.cache_resource
def get_price_monitor():
    return PriceMonitor(db_manager=get_db_manager(), zone_analyzer=get_zone_analyzer())


def show_supply_demand_zones():
    st.title("📊 Technical Analysis Hub")
    st.caption("Supply/Demand Zones • Fibonacci • Volume Profile • Order Flow")

    # Sync status widget
    from src.components.sync_status_widget import SyncStatusWidget
    sync_widget = SyncStatusWidget()
    sync_widget.display(
        table_name="stock_data",
        title="Data Sync Status",
        compact=True
    )

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Controls")

        page = st.radio(
            "Analysis Tool",
            [
                "🎯 Active Zones",
                "💰 Buy Zone Scanner",
                "💰 Opportunities",
                "📐 Fibonacci",
                "📈 Volume Profile",
                "💹 Order Flow",
                "📈 Statistics",
                "🔔 Alerts",
                "🔍 Scanner"
            ]
        )

        st.markdown("---")

        # Conditional filters based on page
        if page in ["🎯 Active Zones", "💰 Opportunities"]:
            st.subheader("Zone Filters")

            zone_type_filter = st.selectbox(
                "Zone Type",
                ["All", "DEMAND", "SUPPLY"]
            )

            min_strength_filter = st.slider(
                "Min Strength",
                0, 100, 50,
                help="Minimum zone strength score"
            )

            status_filter = st.multiselect(
                "Status",
                ["FRESH", "TESTED", "WEAK", "BROKEN"],
                default=["FRESH", "TESTED"]
            )
        elif page in ["📐 Fibonacci", "📈 Volume Profile", "💹 Order Flow"]:
            st.subheader("Stock Selection")

            # PERFORMANCE: Use cached TradingView manager
            tv_manager = get_tradingview_manager_for_scanner()

            selection_mode = st.radio(
                "Select from",
                ["Manual Entry", "Watchlist", "Popular"],
                key="stock_selection"
            )

            if selection_mode == "Manual Entry":
                symbol = st.text_input("Ticker Symbol", value="AAPL", key="manual_symbol").upper()
            elif selection_mode == "Watchlist":
                # PERFORMANCE: Use cached watchlists
                watchlists = get_all_watchlists_cached(tv_manager)
                if watchlists:
                    selected_wl = st.selectbox("Watchlist", list(watchlists.keys()))
                    symbol = st.selectbox("Symbol", watchlists[selected_wl])
                else:
                    st.warning("No watchlists found")
                    symbol = st.text_input("Ticker Symbol", value="AAPL", key="fallback_symbol").upper()
            else:
                popular = ['AAPL', 'MSFT', 'GOOGL', 'AMZN', 'TSLA', 'NVDA', 'META', 'SPY', 'QQQ']
                symbol = st.selectbox("Symbol", popular)

            st.markdown("---")
            st.subheader("Timeframe")

            period = st.selectbox("Period", ['1mo', '3mo', '6mo', '1y'], index=2, key="period_select")
            interval = st.selectbox("Interval", ['1d', '1wk', '1h'], index=0, key="interval_select")

            if page == "📐 Fibonacci":
                st.markdown("---")
                st.subheader("Fibonacci Settings")
                fib_lookback = st.slider("Swing Lookback", 5, 50, 20, key="fib_lookback")

    # Main content
    if page == "🎯 Active Zones":
        show_active_zones_page(zone_type_filter, min_strength_filter, status_filter)

    elif page == "💰 Buy Zone Scanner":
        show_buy_zone_scanner_page()

    elif page == "💰 Opportunities":
        show_opportunities_page(min_strength_filter)

    elif page == "📐 Fibonacci":
        show_fibonacci_page(symbol, period, interval, fib_lookback)

    elif page == "📈 Volume Profile":
        show_volume_profile_page(symbol, period, interval)

    elif page == "💹 Order Flow":
        show_order_flow_page(symbol, period, interval)

    elif page == "📈 Statistics":
        show_statistics_page()

    elif page == "🔔 Alerts":
        show_alerts_page()

    elif page == "🔍 Scanner":
        show_scanner_page()


# PERFORMANCE: Cached active zones query
@st.cache_data(ttl=300)
def get_active_zones_cached(_db, zone_type, min_strength):
    """Get active zones with 5-minute cache"""
    return _db.get_active_zones(zone_type=zone_type, min_strength=min_strength)

def show_active_zones_page(zone_type_filter, min_strength_filter, status_filter):
    """Show active zones with filtering"""

    st.header("🎯 Active Supply/Demand Zones")

    db = get_db_manager()

    # PERFORMANCE: Get cached zones
    zones = get_active_zones_cached(
        db,
        None if zone_type_filter == "All" else zone_type_filter,
        min_strength_filter
    )

    # Filter by status
    if status_filter:
        zones = [z for z in zones if z['status'] in status_filter]

    if not zones:
        st.info("No active zones found matching filters")
        return

    st.success(f"Found {len(zones)} active zones")

    # Group by ticker
    zones_by_ticker = {}
    for zone in zones:
        ticker = zone['ticker']
        if ticker not in zones_by_ticker:
            zones_by_ticker[ticker] = []
        zones_by_ticker[ticker].append(zone)

    # Ticker selector
    selected_ticker = st.selectbox(
        "Select Ticker",
        sorted(zones_by_ticker.keys())
    )

    if selected_ticker:
        show_ticker_zones(selected_ticker, zones_by_ticker[selected_ticker])


def show_ticker_zones(ticker: str, zones: list):
    """Display zones for a specific ticker"""

    st.subheader(f"{ticker} Zones")

    # Get current price
    try:
        ticker_obj = yf.Ticker(ticker)
        data = ticker_obj.history(period='1d', interval='1m')
        if not data.empty:
            current_price = float(data['Close'].iloc[-1])
            st.metric("Current Price", f"${current_price:.2f}")
        else:
            current_price = None
    except:
        current_price = None

    # Create zones dataframe
    zones_df = pd.DataFrame([{
        'ID': z['id'],
        'Type': z['zone_type'],
        'Bottom': f"${z['zone_bottom']:.2f}",
        'Top': f"${z['zone_top']:.2f}",
        'Midpoint': f"${z['zone_midpoint']:.2f}",
        'Strength': z['strength_score'],
        'Status': z['status'],
        'Tests': z['test_count'],
        'Formed': z['formed_date'].strftime('%Y-%m-%d') if z['formed_date'] else 'N/A'
    } for z in zones])

    st.dataframe(zones_df, use_container_width=True)

    # Visualize zones if we have current price
    if current_price:
        st.subheader("Zone Visualization")
        show_zone_chart(ticker, zones, current_price)


def show_zone_chart(ticker: str, zones: list, current_price: float):
    """Show price chart with zones overlayed"""

    try:
        # Fetch historical data
        ticker_obj = yf.Ticker(ticker)
        df = ticker_obj.history(period='3mo', interval='1d')

        if df.empty:
            st.warning("No price data available")
            return

        # Create candlestick chart
        fig = go.Figure()

        # Candlesticks
        fig.add_trace(go.Candlestick(
            x=df.index,
            open=df['Open'],
            high=df['High'],
            low=df['Low'],
            close=df['Close'],
            name=ticker
        ))

        # Add zones as rectangles
        for zone in zones:
            color = 'rgba(0, 255, 0, 0.2)' if zone['zone_type'] == 'DEMAND' else 'rgba(255, 0, 0, 0.2)'
            border_color = 'green' if zone['zone_type'] == 'DEMAND' else 'red'

            fig.add_shape(
                type="rect",
                x0=df.index[0],
                x1=df.index[-1],
                y0=zone['zone_bottom'],
                y1=zone['zone_top'],
                fillcolor=color,
                line=dict(color=border_color, width=2),
                layer="below"
            )

            # Add zone label
            fig.add_annotation(
                x=df.index[-1],
                y=zone['zone_midpoint'],
                text=f"{zone['zone_type']} ({zone['strength_score']}/100)",
                showarrow=False,
                bgcolor=border_color,
                font=dict(color='white', size=10)
            )

        # Add current price line
        fig.add_hline(
            y=current_price,
            line_dash="dash",
            line_color="blue",
            annotation_text=f"Current: ${current_price:.2f}"
        )

        fig.update_layout(
            title=f"{ticker} - Supply/Demand Zones",
            xaxis_title="Date",
            yaxis_title="Price ($)",
            height=600,
            showlegend=False
        )

        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"Error creating chart: {e}")


# PERFORMANCE: Cached price summary
@st.cache_data(ttl=60)
def get_price_summary_cached(_monitor, tickers):
    """Get price summary with 1-minute cache"""
    return _monitor.get_price_summary(tickers)

def show_opportunities_page(min_strength_filter):
    """Show current trading opportunities"""

    st.header("💰 Current Trading Opportunities")

    st.info("Shows stocks where price is near high-quality zones")

    db = get_db_manager()
    monitor = get_price_monitor()

    # PERFORMANCE: Get cached active zones
    zones = get_active_zones_cached(db, None, min_strength_filter)

    if not zones:
        st.warning("No active zones found")
        return

    # Get unique tickers
    tickers = list(set(z['ticker'] for z in zones))

    st.write(f"Monitoring {len(tickers)} tickers...")

    # PERFORMANCE: Get cached price summary
    with st.spinner("Fetching current prices and analyzing zones..."):
        summary_df = get_price_summary_cached(monitor, tickers)

    if summary_df.empty:
        st.warning("No price data available")
        return

    # Show opportunities (where price is near zones)
    opportunities = summary_df[summary_df['Nearest Zone Distance'].notna() &
                               (summary_df['Nearest Zone Distance'] <= 5.0)]

    if opportunities.empty:
        st.info("No immediate opportunities found. No stocks are within 5% of a zone.")
        st.dataframe(summary_df, use_container_width=True)
        return

    st.success(f"Found {len(opportunities)} opportunities!")

    # Sort by distance (closest first)
    opportunities = opportunities.sort_values('Nearest Zone Distance')

    # Format dataframe
    opportunities_display = opportunities.copy()
    opportunities_display['Current Price'] = opportunities_display['Current Price'].apply(lambda x: f"${x:.2f}")
    opportunities_display['Nearest Zone Distance'] = opportunities_display['Nearest Zone Distance'].apply(lambda x: f"${x:.2f}")

    st.dataframe(opportunities_display, use_container_width=True)

    # Highlight top opportunity
    if len(opportunities) > 0:
        st.subheader("🔥 Top Opportunity")

        top_opp = opportunities.iloc[0]

        col1, col2, col3, col4 = st.columns(4)

        with col1:
            st.metric("Symbol", top_opp['Symbol'])

        with col2:
            st.metric("Current Price", f"${top_opp['Current Price']}")

        with col3:
            st.metric("Zone Type", top_opp['Nearest Zone Type'])

        with col4:
            st.metric("Distance", f"${top_opp['Nearest Zone Distance']:.2f}")


# PERFORMANCE: Cached zone statistics
@st.cache_data(ttl=300)
def get_zone_statistics_cached(_db):
    """Get zone statistics with 5-minute cache"""
    return _db.get_zone_statistics()

# PERFORMANCE: Cached scan logs
@st.cache_data(ttl=300)
def get_scan_logs_cached(_db, limit=10):
    """Get scan logs with 5-minute cache"""
    return _db.get_scan_logs(limit=limit)

def show_statistics_page():
    """Show zone statistics and performance metrics"""

    st.header("📈 Zone Statistics")

    db = get_db_manager()

    # Overall statistics
    st.subheader("Overall Statistics")

    col1, col2, col3, col4 = st.columns(4)

    # PERFORMANCE: Get cached statistics
    stats = get_zone_statistics_cached(db)

    with col1:
        st.metric("Total Zones", stats.get('total_zones', 0))

    with col2:
        st.metric("Active Zones", stats.get('active_zones', 0))

    with col3:
        st.metric("Fresh Zones", stats.get('fresh_zones', 0))

    with col4:
        avg_strength = stats.get('avg_strength', 0)
        st.metric("Avg Strength", f"{avg_strength:.1f}/100" if avg_strength else "N/A")

    # Zone breakdown
    st.subheader("Zone Breakdown")

    col1, col2 = st.columns(2)

    with col1:
        st.metric("Demand Zones", stats.get('demand_zones', 0))

    with col2:
        st.metric("Supply Zones", stats.get('supply_zones', 0))

    # Recent scan logs
    st.subheader("Recent Scanner Activity")

    # PERFORMANCE: Get cached scan logs
    logs = get_scan_logs_cached(db, limit=10)

    if logs:
        logs_df = pd.DataFrame([{
            'Timestamp': log['scan_timestamp'].strftime('%Y-%m-%d %H:%M:%S'),
            'Type': log['scan_type'],
            'Tickers': log['tickers_scanned'],
            'Zones Found': log['zones_found'],
            'Zones Updated': log['zones_updated'],
            'Alerts': log['alerts_sent'],
            'Duration': f"{log['duration_seconds']:.1f}s",
            'Status': log['status']
        } for log in logs])

        st.dataframe(logs_df, use_container_width=True)
    else:
        st.info("No scan logs yet")


# PERFORMANCE: Cached recent alerts
@st.cache_data(ttl=60)
def get_recent_alerts_cached(_db, hours):
    """Get recent alerts with 1-minute cache"""
    return _db.get_recent_alerts(hours=hours)

def show_alerts_page():
    """Show recent alerts"""

    st.header("🔔 Recent Alerts")

    db = get_db_manager()

    # Time filter
    hours_back = st.selectbox(
        "Time Period",
        [1, 4, 12, 24, 48, 168],
        format_func=lambda x: f"Last {x} hours" if x < 24 else f"Last {x//24} days",
        index=3  # Default to 24 hours
    )

    # PERFORMANCE: Get cached alerts
    alerts = get_recent_alerts_cached(db, hours_back)

    if not alerts:
        st.info(f"No alerts in the last {hours_back} hours")
        return

    st.success(f"Found {len(alerts)} alerts")

    # Create alerts dataframe
    alerts_df = pd.DataFrame([{
        'Time': alert['sent_at'].strftime('%Y-%m-%d %H:%M:%S'),
        'Ticker': alert['ticker'],
        'Type': alert['alert_type'],
        'Price': f"${alert['alert_price']:.2f}",
        'Zone Type': alert['zone_type'],
        'Quality': alert['setup_quality'],
        'Status': alert['status']
    } for alert in alerts])

    st.dataframe(alerts_df, use_container_width=True)

    # Alert statistics
    st.subheader("Alert Statistics")

    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Total Alerts", len(alerts))

    with col2:
        high_quality = sum(1 for a in alerts if a['setup_quality'] == 'HIGH')
        st.metric("High Quality", high_quality)

    with col3:
        unique_tickers = len(set(a['ticker'] for a in alerts))
        st.metric("Unique Tickers", unique_tickers)


# PERFORMANCE: Cached TradingView manager for scanner
@st.cache_resource
def get_tradingview_manager_for_scanner():
    """Cached TradingView manager"""
    from src.tradingview_db_manager import TradingViewDBManager
    return TradingViewDBManager()

# PERFORMANCE: Cached buy zone scanner
@st.cache_resource
def get_buy_zone_scanner():
    """Cached buy zone scanner"""
    from src.zone_buy_scanner import BuyZoneScanner
    return BuyZoneScanner()

# PERFORMANCE: Cached watchlists for scanner
@st.cache_data(ttl=300)
def get_all_watchlists_cached(_tv_manager):
    """Get all watchlists with 5-minute cache"""
    return _tv_manager.get_all_symbols_dict()

# PERFORMANCE: Cached database stocks
@st.cache_data(ttl=300)
def get_database_stocks_cached(_buy_scanner):
    """Get database stocks with 5-minute cache"""
    return _buy_scanner._get_database_stocks()

def show_scanner_page():
    """Manual scanner controls with enhanced stock selection"""

    st.header("🔍 Zone Scanner")

    st.info("Manually trigger zone detection and price monitoring scans")

    # PERFORMANCE: Initialize with cached managers
    tv_manager = get_tradingview_manager_for_scanner()
    buy_scanner = get_buy_zone_scanner()

    # Scan mode selection
    st.subheader("📋 Select Stocks to Scan")

    scan_mode = st.radio(
        "Scan Mode",
        ["Single Symbol", "Multiple Symbols", "Watchlists", "Database Stocks", "All Sources"],
        horizontal=True
    )

    symbols_to_scan = []

    if scan_mode == "Single Symbol":
        # Single symbol scan
        col1, col2 = st.columns([3, 1])
        with col1:
            symbol_input = st.text_input("Ticker Symbol", value="AAPL").upper()
        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            if st.button("Add", type="secondary", use_container_width=True):
                if symbol_input:
                    symbols_to_scan = [symbol_input]

        if symbol_input:
            symbols_to_scan = [symbol_input]

    elif scan_mode == "Multiple Symbols":
        # Multiple symbols input
        symbols_input = st.text_area(
            "Enter symbols (one per line or comma-separated)",
            value="AAPL, MSFT, TSLA, NVDA, SPY",
            height=100
        )

        if symbols_input:
            # Parse symbols (handle both comma and newline separated)
            symbols_raw = symbols_input.replace('\n', ',').split(',')
            symbols_to_scan = [s.strip().upper() for s in symbols_raw if s.strip()]

    elif scan_mode == "Watchlists":
        # PERFORMANCE: Cached watchlist selection with multiselect
        all_watchlists = get_all_watchlists_cached(tv_manager)
        watchlist_names = list(all_watchlists.keys())

        if not watchlist_names:
            st.warning("No TradingView watchlists found in database. Sync watchlists first.")
        else:
            selected_watchlists = st.multiselect(
                "Select Watchlists to Scan",
                watchlist_names,
                default=[watchlist_names[0]] if watchlist_names else [],
                help="Select one or more TradingView watchlists"
            )

            if selected_watchlists:
                # Get symbols from selected watchlists
                for wl_name in selected_watchlists:
                    symbols_to_scan.extend(all_watchlists[wl_name])

                symbols_to_scan = list(set(symbols_to_scan))  # Remove duplicates
                st.info(f"Selected {len(symbols_to_scan)} unique symbols from {len(selected_watchlists)} watchlist(s)")

    elif scan_mode == "Database Stocks":
        # PERFORMANCE: Get cached database stocks
        db_stocks = get_database_stocks_cached(buy_scanner)

        if not db_stocks:
            st.warning("No stocks found in database. Sync stock data first.")
        else:
            st.info(f"Found {len(db_stocks)} stocks in database")

            # Option to limit number of stocks
            use_limit = st.checkbox("Limit number of stocks to scan", value=True)

            if use_limit:
                limit = st.slider("Max stocks to scan", min_value=10, max_value=500, value=100, step=10)
                symbols_to_scan = db_stocks[:limit]
            else:
                symbols_to_scan = db_stocks

    elif scan_mode == "All Sources":
        # Combine watchlists and database stocks
        col1, col2 = st.columns(2)

        with col1:
            use_watchlists = st.checkbox("Include Watchlists", value=True)
            if use_watchlists:
                # PERFORMANCE: Use cached watchlists
                all_watchlists = get_all_watchlists_cached(tv_manager)
                for symbols_list in all_watchlists.values():
                    symbols_to_scan.extend(symbols_list)

        with col2:
            use_database = st.checkbox("Include Database Stocks", value=True)
            if use_database:
                # PERFORMANCE: Use cached database stocks
                db_stocks = get_database_stocks_cached(buy_scanner)
                symbols_to_scan.extend(db_stocks)

        # Remove duplicates
        symbols_to_scan = list(set(symbols_to_scan))

        if symbols_to_scan:
            st.info(f"Combined total: {len(symbols_to_scan)} unique symbols")

            # Limit option
            use_limit = st.checkbox("Limit number of stocks to scan", value=True, key="all_sources_limit")
            if use_limit:
                limit = st.slider("Max stocks to scan", min_value=10, max_value=500, value=200, step=10, key="all_sources_slider")
                symbols_to_scan = symbols_to_scan[:limit]
                st.info(f"Scanning {len(symbols_to_scan)} symbols (limited)")

    # Display selected symbols
    if symbols_to_scan:
        with st.expander(f"📋 Selected Symbols ({len(symbols_to_scan)})", expanded=False):
            # Show symbols in columns for better display
            num_cols = 5
            cols = st.columns(num_cols)
            for i, symbol in enumerate(sorted(symbols_to_scan)):
                cols[i % num_cols].write(f"• {symbol}")

    # Scan button
    st.markdown("---")

    if not symbols_to_scan:
        st.warning("⚠️ No symbols selected. Please select stocks to scan.")
    else:
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            scan_button = st.button(
                f"🔍 Scan {len(symbols_to_scan)} Symbol(s) for Zones",
                type="primary",
                use_container_width=True
            )

        if scan_button:
            # Perform batch scan
            with st.spinner(f"Scanning {len(symbols_to_scan)} symbols for zones... This may take a while."):
                scanner = SupplyDemandScanner(enable_telegram=False)

                total_zones_found = 0
                total_zones_saved = 0
                total_high_quality = 0
                scanned_count = 0
                errors = []

                # Progress bar
                progress_bar = st.progress(0)
                status_text = st.empty()

                for i, symbol in enumerate(symbols_to_scan):
                    try:
                        status_text.text(f"Scanning {symbol} ({i+1}/{len(symbols_to_scan)})...")
                        result = scanner.scan_symbol_for_zones(symbol)

                        if 'error' not in result:
                            scanned_count += 1
                            total_zones_found += result.get('zones_found', 0)
                            total_zones_saved += result.get('zones_saved', 0)
                            total_high_quality += result.get('high_quality_zones', 0)
                        else:
                            errors.append(f"{symbol}: {result['error']}")

                    except Exception as e:
                        errors.append(f"{symbol}: {str(e)}")

                    # Update progress
                    progress_bar.progress((i + 1) / len(symbols_to_scan))

                progress_bar.empty()
                status_text.empty()

            # Show results
            st.success(f"✅ Scan complete! Scanned {scanned_count}/{len(symbols_to_scan)} symbols")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Symbols Scanned", scanned_count)

            with col2:
                st.metric("Zones Found", total_zones_found)

            with col3:
                st.metric("Zones Saved", total_zones_saved)

            with col4:
                st.metric("High Quality Zones", total_high_quality)

            # Show errors if any
            if errors:
                with st.expander(f"⚠️ Errors ({len(errors)})", expanded=False):
                    for error in errors[:20]:  # Show first 20 errors
                        st.text(error)
                    if len(errors) > 20:
                        st.text(f"... and {len(errors) - 20} more errors")


# PERFORMANCE: Cached zone summary stats
@st.cache_data(ttl=60)
def get_zone_summary_stats_cached(_scanner, df):
    """Get zone summary stats with 1-minute cache"""
    return _scanner.get_zone_summary_stats(df)

# PERFORMANCE: Cached buy zone scan
@st.cache_data(ttl=60)
def scan_for_buy_zones_cached(_scanner, watchlist_names, use_database_stocks, max_distance_pct, min_strength, min_rating):
    """Scan for buy zones with 1-minute cache"""
    return _scanner.scan_for_buy_zones(
        watchlist_names=watchlist_names,
        use_database_stocks=use_database_stocks,
        max_distance_pct=max_distance_pct,
        min_strength=min_strength,
        min_rating=min_rating
    )

def show_buy_zone_scanner_page():
    """Enhanced buy zone scanner with watchlists and database stocks"""

    st.header("💰 Buy Zone Scanner - Find Best Stocks in Demand Zones")
    st.caption("Scans watchlists and database stocks to find the best buy opportunities in demand zones")

    # PERFORMANCE: Use cached scanner
    scanner = get_buy_zone_scanner()
    
    # Configuration section
    with st.expander("⚙️ Scanner Configuration", expanded=False):
        col1, col2 = st.columns(2)
        
        with col1:
            # PERFORMANCE: Cached watchlist selection
            all_watchlists = get_all_watchlists_cached(scanner.tv_manager)
            watchlist_names = list(all_watchlists.keys())
            
            selected_watchlists = st.multiselect(
                "Select Watchlists",
                watchlist_names,
                default=[],
                help="Select TradingView watchlists to scan. Leave empty to scan all watchlists."
            )
            
            use_database_stocks = st.checkbox(
                "Include Database Stocks",
                value=True,
                help="Also scan stocks from the database stocks table"
            )
        
        with col2:
            max_distance = st.slider(
                "Max Distance from Zone (%)",
                min_value=0.5,
                max_value=10.0,
                value=5.0,
                step=0.5,
                help="Maximum distance from zone midpoint to consider"
            )
            
            min_strength = st.slider(
                "Min Zone Strength",
                min_value=0,
                max_value=100,
                value=50,
                help="Minimum zone strength score (0-100)"
            )
            
            min_rating = st.slider(
                "Min Overall Rating",
                min_value=0.0,
                max_value=100.0,
                value=60.0,
                step=5.0,
                help="Minimum overall rating to display (0-100)"
            )
    
    # Scan button
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        scan_button = st.button("🔍 Scan for Buy Zones", type="primary", use_container_width=True)
    
    if scan_button:
        with st.spinner("Scanning for buy zones... This may take a minute."):
            # PERFORMANCE: Perform cached scan
            df = scan_for_buy_zones_cached(
                scanner,
                selected_watchlists if selected_watchlists else None,
                use_database_stocks,
                max_distance,
                min_strength,
                min_rating
            )

            if df.empty:
                st.warning("No buy zones found matching your criteria. Try adjusting filters.")
                return

            # Store in session state
            st.session_state['buy_zone_results'] = df
            # PERFORMANCE: Use cached stats
            st.session_state['buy_zone_stats'] = get_zone_summary_stats_cached(scanner, df)
    
    # Display results if available
    if 'buy_zone_results' in st.session_state:
        df = st.session_state['buy_zone_results']
        stats = st.session_state['buy_zone_stats']
        
        # Summary statistics
        st.subheader("📊 Summary Statistics")
        col1, col2, col3, col4, col5 = st.columns(5)
        
        with col1:
            st.metric("Total Opportunities", stats['total_opportunities'])
        with col2:
            st.metric("Avg Rating", f"{stats['avg_rating']:.1f}")
        with col3:
            st.metric("Avg Distance", f"{stats['avg_distance']:.2f}%")
        with col4:
            st.metric("Avg Strength", f"{stats['avg_strength']:.1f}")
        with col5:
            st.metric("Excellent (85+)", stats['excellent_count'])
        
        st.markdown("---")
        
        # Rating distribution chart
        st.subheader("📈 Rating Distribution")
        rating_counts = {
            'Excellent (85+)': stats['excellent_count'],
            'Very Good (75-84)': stats['very_good_count'],
            'Good (65-74)': stats['good_count'],
            'Fair (55-64)': len(df[(df['Overall Rating'] >= 55) & (df['Overall Rating'] < 65)]),
            'Weak (<55)': len(df[df['Overall Rating'] < 55])
        }
        
        import plotly.express as px
        fig = px.bar(
            x=list(rating_counts.keys()),
            y=list(rating_counts.values()),
            title="Buy Zone Opportunities by Rating",
            labels={'x': 'Rating Category', 'y': 'Count'}
        )
        st.plotly_chart(fig, use_container_width=True)
        
        st.markdown("---")
        
        # Filters
        st.subheader("🔍 Filter Results")
        filter_col1, filter_col2, filter_col3 = st.columns(3)
        
        with filter_col1:
            rating_filter = st.slider(
                "Min Rating",
                min_value=0.0,
                max_value=100.0,
                value=float(df['Overall Rating'].min()),
                step=5.0
            )
        
        with filter_col2:
            distance_filter = st.slider(
                "Max Distance (%)",
                min_value=0.0,
                max_value=10.0,
                value=float(df['Distance from Zone (%)'].max()),
                step=0.5
            )
        
        with filter_col3:
            strength_filter = st.slider(
                "Min Strength",
                min_value=0.0,
                max_value=100.0,
                value=float(df['Zone Strength'].min()),
                step=5.0
            )
        
        # Apply filters
        filtered_df = df[
            (df['Overall Rating'] >= rating_filter) &
            (df['Distance from Zone (%)'] <= distance_filter) &
            (df['Zone Strength'] >= strength_filter)
        ]
        
        st.info(f"Showing {len(filtered_df)} of {len(df)} opportunities")
        
        # Display table
        st.subheader("📋 Buy Zone Opportunities")
        
        # Format display columns
        display_df = filtered_df.copy()
        display_df['Current Price'] = display_df['Current Price'].apply(lambda x: f"${x:.2f}")
        display_df['Zone Bottom'] = display_df['Zone Bottom'].apply(lambda x: f"${x:.2f}")
        display_df['Zone Top'] = display_df['Zone Top'].apply(lambda x: f"${x:.2f}")
        display_df['Zone Midpoint'] = display_df['Zone Midpoint'].apply(lambda x: f"${x:.2f}")
        display_df['Distance from Zone (%)'] = display_df['Distance from Zone (%)'].apply(lambda x: f"{x:.2f}%")
        display_df['Zone Strength'] = display_df['Zone Strength'].apply(lambda x: f"{x:.1f}")
        display_df['Overall Rating'] = display_df['Overall Rating'].apply(lambda x: f"{x:.1f}")
        
        # Select columns to display
        display_columns = [
            'Symbol', 'Current Price', 'Zone Midpoint', 'Distance from Zone (%)',
            'Zone Strength', 'Zone Status', 'Test Count', 'Overall Rating', 'Recommendation'
        ]
        
        st.dataframe(
            display_df[display_columns],
            use_container_width=True,
            height=600
        )
        
        # Top opportunities visualization
        st.subheader("🎯 Top 10 Buy Zone Opportunities")
        top_10 = filtered_df.head(10)
        
        fig = go.Figure()
        
        # Bar chart of ratings
        fig.add_trace(go.Bar(
            x=top_10['Symbol'],
            y=top_10['Overall Rating'],
            text=top_10['Overall Rating'].apply(lambda x: f"{x:.1f}"),
            textposition='auto',
            marker=dict(
                color=top_10['Overall Rating'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Rating")
            )
        ))
        
        fig.update_layout(
            title="Top 10 Buy Zone Opportunities by Rating",
            xaxis_title="Symbol",
            yaxis_title="Overall Rating",
            height=400
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
        # Distance vs Strength scatter plot
        st.subheader("📊 Distance vs Strength Analysis")
        fig2 = go.Figure()
        
        fig2.add_trace(go.Scatter(
            x=filtered_df['Distance from Zone (%)'],
            y=filtered_df['Zone Strength'],
            mode='markers',
            marker=dict(
                size=filtered_df['Overall Rating'] / 2,
                color=filtered_df['Overall Rating'],
                colorscale='RdYlGn',
                showscale=True,
                colorbar=dict(title="Rating"),
                line=dict(width=1, color='black')
            ),
            text=filtered_df['Symbol'],
            hovertemplate='<b>%{text}</b><br>' +
                          'Distance: %{x:.2f}%<br>' +
                          'Strength: %{y:.1f}<br>' +
                          'Rating: %{marker.color:.1f}<extra></extra>'
        ))
        
        fig2.update_layout(
            title="Zone Distance vs Strength (Size = Rating)",
            xaxis_title="Distance from Zone (%)",
            yaxis_title="Zone Strength",
            height=500
        )
        
        st.plotly_chart(fig2, use_container_width=True)


def show_fibonacci_page(symbol, period, interval, fib_lookback):
    """Fibonacci analysis tab"""
    from src.fibonacci_calculator import FibonacciCalculator

    st.header(f"📐 Fibonacci Analysis - {symbol}")

    # Fetch data
    with st.spinner(f"Fetching {symbol} data..."):
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            st.error(f"No data available for {symbol}")
            return

        df.columns = [col.lower() for col in df.columns]

    current_price = df['close'].iloc[-1]

    # Display current price
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Current Price", f"${current_price:.2f}")
    with col2:
        st.metric("Period High", f"${df['high'].max():.2f}")
    with col3:
        st.metric("Period Low", f"${df['low'].min():.2f}")

    st.markdown("---")

    # Fibonacci analysis
    fib_calc = FibonacciCalculator()

    with st.spinner("Detecting swing patterns..."):
        swings = fib_calc.auto_detect_swings(df, lookback=fib_lookback)

    if not swings:
        st.warning("No significant swing patterns found. Try adjusting lookback period.")
        return

    st.success(f"✅ Found {len(swings)} swing patterns")

    # Swing selector
    swing_options = [
        f"Swing {i+1}: {s['type']} (${s['swing_low']:.2f} → ${s['swing_high']:.2f})"
        for i, s in enumerate(swings)
    ]

    selected_idx = st.selectbox(
        "Select Swing Pattern",
        range(len(swing_options)),
        format_func=lambda x: swing_options[x],
        index=len(swing_options) - 1
    )

    swing = swings[selected_idx]

    # Display details in tabs
    tab1, tab2, tab3 = st.tabs(["📊 Levels", "🎯 Golden Zone", "🔗 Confluence"])

    with tab1:
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Swing Details")
            st.write(f"**Type**: {swing['type']}")
            st.write(f"**High**: ${swing['swing_high']:.2f}")
            st.write(f"**Low**: ${swing['swing_low']:.2f}")
            st.write(f"**Range**: ${swing['price_range']:.2f} ({swing['range_pct']:.2f}%)")

        with col2:
            st.markdown("### Fibonacci Levels")
            for level, price in swing['retracement_levels'].items():
                st.write(f"**{level}**: ${price:.2f}")

    with tab2:
        in_golden_zone = (swing['golden_zone']['bottom'] <= current_price <= swing['golden_zone']['top'])

        if in_golden_zone:
            st.success("🔥 **CURRENT PRICE IN GOLDEN ZONE**")
            st.write("**This is a high probability reversal area!**")
        else:
            distance = min(
                abs(current_price - swing['golden_zone']['top']),
                abs(current_price - swing['golden_zone']['bottom'])
            )
            st.info(f"Distance to Golden Zone: ${distance:.2f}")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("Golden Zone Top", f"${swing['golden_zone']['top']:.2f}")
        with col2:
            st.metric("Golden Zone Bottom", f"${swing['golden_zone']['bottom']:.2f}")

    with tab3:
        confluences = fib_calc.find_fibonacci_confluence(swings, tolerance_pct=1.0)

        if confluences:
            st.success(f"Found {len(confluences)} confluence zones")

            conf_df = pd.DataFrame([{
                'Price': f"${c['price']:.2f}",
                'Strength': c['strength'],
                'Zone': f"${c['price_min']:.2f} - ${c['price_max']:.2f}"
            } for c in confluences[:10]])

            st.dataframe(conf_df, use_container_width=True, hide_index=True)
        else:
            st.info("No significant confluence zones found")

    # Chart with Fibonacci levels
    st.markdown("---")
    st.subheader("📈 Price Chart with Fibonacci Levels")

    fig = go.Figure()

    # Candlestick
    fig.add_trace(go.Candlestick(
        x=df.index,
        open=df['open'],
        high=df['high'],
        low=df['low'],
        close=df['close'],
        name=symbol
    ))

    # Fibonacci levels
    for level_name, level_price in swing['retracement_levels'].items():
        fig.add_hline(
            y=level_price,
            line_dash="dot",
            line_color="gray",
            annotation_text=f"Fib {level_name}",
            annotation_position="right"
        )

    # Golden Zone
    fig.add_hrect(
        y0=swing['golden_zone']['bottom'],
        y1=swing['golden_zone']['top'],
        fillcolor="rgba(255, 215, 0, 0.2)",
        line_width=0,
        annotation_text="Golden Zone",
        annotation_position="top right"
    )

    fig.update_layout(
        title=f"{symbol} - Fibonacci Retracement",
        xaxis_title="Date",
        yaxis_title="Price ($)",
        height=600,
        showlegend=False
    )

    st.plotly_chart(fig, use_container_width=True)


def show_volume_profile_page(symbol, period, interval):
    """Volume Profile analysis tab"""
    from src.advanced_technical_indicators import VolumeProfileCalculator

    st.header(f"📈 Volume Profile - {symbol}")

    # Fetch data
    with st.spinner(f"Fetching {symbol} data..."):
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            st.error(f"No data available for {symbol}")
            return

        df.columns = [col.lower() for col in df.columns]

    current_price = df['close'].iloc[-1]

    # Calculate Volume Profile
    vp_calc = VolumeProfileCalculator()

    with st.spinner("Calculating Volume Profile..."):
        vp = vp_calc.calculate_volume_profile(df, price_bins=40)

    # Display key metrics
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("POC (Point of Control)", f"${vp['poc']['price']:.2f}")
        st.caption(f"{vp['poc']['pct_of_total']:.1f}% of total volume")

    with col2:
        st.metric("VAH (Value Area High)", f"${vp['vah']:.2f}")
        st.caption(f"Top of 70% volume range")

    with col3:
        st.metric("VAL (Value Area Low)", f"${vp['val']:.2f}")
        st.caption(f"Bottom of 70% volume range")

    st.markdown("---")

    # Trading signals
    signals = vp_calc.get_trading_signals(current_price, vp)

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current Price", f"${current_price:.2f}")
    with col2:
        st.metric("Position", signals['position'].replace('_', ' '))
    with col3:
        st.metric("Bias", signals['bias'])
    with col4:
        if signals['setup_quality'] == 'EXCELLENT':
            st.success(signals['setup_quality'])
        elif signals['setup_quality'] == 'GOOD':
            st.info(signals['setup_quality'])
        else:
            st.warning(signals['setup_quality'])

    st.markdown("---")

    # Recommendation
    if signals['setup_quality'] == 'EXCELLENT':
        st.success(f"**{signals['recommendation']}**")
    elif signals['setup_quality'] == 'GOOD':
        st.info(f"**{signals['recommendation']}**")
    else:
        st.warning(f"**{signals['recommendation']}**")

    st.markdown("---")

    # Volume Profile Chart
    st.subheader("📊 Volume Profile Distribution")

    fig = go.Figure()

    # Horizontal volume bars
    fig.add_trace(go.Bar(
        y=vp['price_levels'],
        x=vp['volume_at_price'],
        orientation='h',
        marker=dict(
            color=vp['volume_at_price'],
            colorscale='Blues',
            showscale=True
        ),
        name='Volume'
    ))

    # POC line
    fig.add_hline(
        y=vp['poc']['price'],
        line_color="red",
        line_width=3,
        annotation_text=f"POC: ${vp['poc']['price']:.2f}"
    )

    # Value Area
    fig.add_hrect(
        y0=vp['val'],
        y1=vp['vah'],
        fillcolor="rgba(255, 0, 0, 0.1)",
        line_width=0
    )

    # Current price
    fig.add_hline(
        y=current_price,
        line_dash="dash",
        line_color="green",
        annotation_text=f"Current: ${current_price:.2f}"
    )

    fig.update_layout(
        title=f"{symbol} Volume Profile",
        xaxis_title="Volume",
        yaxis_title="Price ($)",
        height=600
    )

    st.plotly_chart(fig, use_container_width=True)


def show_order_flow_page(symbol, period, interval):
    """Order Flow (CVD) analysis tab"""
    from src.advanced_technical_indicators import OrderFlowAnalyzer

    st.header(f"💹 Order Flow (CVD) - {symbol}")

    # Fetch data
    with st.spinner(f"Fetching {symbol} data..."):
        ticker = yf.Ticker(symbol)
        df = ticker.history(period=period, interval=interval)

        if df.empty:
            st.error(f"No data available for {symbol}")
            return

        df.columns = [col.lower() for col in df.columns]

    # Calculate CVD
    of_analyzer = OrderFlowAnalyzer()
    df['cvd'] = of_analyzer.calculate_cvd(df)

    # Metrics
    current_cvd = df['cvd'].iloc[-1]
    cvd_change_1d = df['cvd'].iloc[-1] - df['cvd'].iloc[-2]
    cvd_change_5d = df['cvd'].iloc[-1] - df['cvd'].iloc[-6] if len(df) >= 6 else 0
    cvd_trend = "BULLISH" if cvd_change_5d > 0 else "BEARISH" if cvd_change_5d < 0 else "NEUTRAL"

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Current CVD", f"{current_cvd:,.0f}")
    with col2:
        st.metric("1-Day Change", f"{cvd_change_1d:+,.0f}")
    with col3:
        st.metric("5-Day Change", f"{cvd_change_5d:+,.0f}")
    with col4:
        if cvd_trend == "BULLISH":
            st.success(f"Trend: {cvd_trend}")
        elif cvd_trend == "BEARISH":
            st.error(f"Trend: {cvd_trend}")
        else:
            st.info(f"Trend: {cvd_trend}")

    st.markdown("---")

    # Divergences
    st.subheader("🔍 CVD Divergences")

    divergences = of_analyzer.find_cvd_divergences(df, lookback=10)

    if divergences:
        st.success(f"✅ Found {len(divergences)} divergence signal(s)")

        for div in divergences:
            if div['type'] == 'BULLISH_DIVERGENCE':
                st.success(f"**{div['type']}** on {div['date'].date()}")
            else:
                st.warning(f"**{div['type']}** on {div['date'].date()}")

            st.write(f"Price: ${div['price']:.2f}")
            st.write(div['signal'])
            st.write("---")
    else:
        st.info("No divergences detected in recent data")

    st.markdown("---")

    # CVD Chart
    st.subheader("📈 Price & CVD Chart")

    fig = make_subplots(
        rows=2, cols=1,
        shared_xaxes=True,
        vertical_spacing=0.1,
        row_heights=[0.6, 0.4],
        subplot_titles=(f'{symbol} Price', 'Cumulative Volume Delta (CVD)')
    )

    # Price chart
    fig.add_trace(
        go.Candlestick(
            x=df.index,
            open=df['open'],
            high=df['high'],
            low=df['low'],
            close=df['close'],
            name='Price'
        ),
        row=1, col=1
    )

    # CVD chart
    fig.add_trace(
        go.Scatter(
            x=df.index,
            y=df['cvd'],
            mode='lines',
            line=dict(color='purple', width=2),
            fill='tozeroy',
            fillcolor='rgba(128, 0, 128, 0.1)',
            name='CVD'
        ),
        row=2, col=1
    )

    fig.update_layout(
        height=700,
        showlegend=False,
        xaxis_rangeslider_visible=False
    )

    st.plotly_chart(fig, use_container_width=True)


if __name__ == "__main__":
    show_supply_demand_zones()
