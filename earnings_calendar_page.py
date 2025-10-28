"""
Earnings Calendar Page - User-Friendly UI with buttons
"""
import streamlit as st
import pandas as pd
import os
from src.tradingview_db_manager import TradingViewDBManager
import robin_stocks.robinhood as rh


def show_earnings_calendar():
    """Display earnings calendar with user-friendly UI"""
    st.title("📅 Earnings Calendar")

    tv = TradingViewDBManager()
    conn = tv.get_connection()
    cur = conn.cursor()

    # Check if earnings_events table exists
    cur.execute("""
        SELECT COUNT(*) FROM information_schema.tables
        WHERE table_name = 'earnings_events'
    """)
    table_exists = cur.fetchone()[0] > 0

    # Setup section - if tables don't exist
    if not table_exists:
        st.warning("📋 Earnings tables not initialized yet")

        col1, col2 = st.columns([3, 1])
        with col1:
            st.info("Click the button to automatically create the earnings database tables")
        with col2:
            if st.button("🔧 Initialize Database", type="primary", use_container_width=True):
                with st.spinner("Creating earnings tables..."):
                    try:
                        # Create earnings_events table
                        cur.execute("""
                            CREATE TABLE IF NOT EXISTS earnings_events (
                                id SERIAL PRIMARY KEY,
                                symbol VARCHAR(10) NOT NULL,
                                earnings_date TIMESTAMP WITH TIME ZONE,
                                earnings_time VARCHAR(10),
                                eps_estimate DECIMAL(10, 2),
                                eps_actual DECIMAL(10, 2),
                                revenue_estimate DECIMAL(15, 2),
                                revenue_actual DECIMAL(15, 2),
                                surprise_percent DECIMAL(10, 2),
                                pre_earnings_iv DECIMAL(10, 4),
                                post_earnings_iv DECIMAL(10, 4),
                                pre_earnings_price DECIMAL(10, 2),
                                post_earnings_price DECIMAL(10, 2),
                                price_move_percent DECIMAL(10, 2),
                                volume_ratio DECIMAL(10, 2),
                                options_volume INTEGER,
                                whisper_number DECIMAL(10, 2),
                                created_at TIMESTAMP DEFAULT NOW(),
                                updated_at TIMESTAMP DEFAULT NOW(),
                                UNIQUE(symbol, earnings_date)
                            )
                        """)

                        # Create index
                        cur.execute("""
                            CREATE INDEX IF NOT EXISTS idx_earnings_date
                            ON earnings_events(earnings_date DESC)
                        """)

                        conn.commit()
                        cur.close()
                        conn.close()
                        st.success("✅ Earnings tables created successfully!")
                        time.sleep(1)
                        st.rerun()
                    except Exception as e:
                        st.error(f"Error creating tables: {e}")
                        conn.rollback()
                        cur.close()
                        conn.close()
                return

    # Main interface - tables exist
    col_s1, col_s2, col_s3 = st.columns([2, 1, 1])

    with col_s1:
        cur.execute("SELECT COUNT(*) FROM earnings_events")
        count = cur.fetchone()[0]
        st.metric("📊 Earnings Events", f"{count:,}")

    with col_s2:
        if st.button("🔄 Sync Earnings", type="primary", use_container_width=True):
            sync_earnings_from_robinhood(conn, cur)

    with col_s3:
        st.caption("💡 Auto-syncs daily at 6 AM")

    st.markdown("---")

    # Display earnings data
    cur.execute("SELECT COUNT(*) FROM earnings_events")
    count = cur.fetchone()[0]

    if count > 0:
        display_earnings_table(conn, cur)
    else:
        st.warning("📭 No earnings data yet")
        st.info("👆 Click 'Sync Earnings' to fetch data from Robinhood (takes 2-3 minutes for 100 stocks)")

    cur.close()
    conn.close()


def sync_earnings_from_robinhood(conn, cur):
    """Sync earnings from Robinhood API"""
    with st.spinner("🔄 Syncing earnings from Robinhood..."):
        try:
            # Login to Robinhood
            username = os.getenv('ROBINHOOD_USERNAME')
            password = os.getenv('ROBINHOOD_PASSWORD')

            if not username or not password:
                st.error("Robinhood credentials not found in .env file")
                return

            rh.login(username, password)

            # Get stocks to sync
            cur.execute("SELECT ticker FROM stocks WHERE asset_type = 'STOCK' LIMIT 100")
            symbols = [row[0] for row in cur.fetchall()]

            synced = 0
            errors = 0
            progress_bar = st.progress(0)
            status_text = st.empty()

            for i, symbol in enumerate(symbols):
                try:
                    status_text.text(f"Syncing {symbol}... ({i+1}/{len(symbols)})")

                    # Get earnings from Robinhood
                    earnings = rh.get_earnings(symbol)

                    if earnings and len(earnings) > 0:
                        # Process latest earnings
                        latest = earnings[0]
                        report_data = latest.get('report', {})
                        eps_data = latest.get('eps', {})

                        report_date = report_data.get('date')
                        eps_actual = eps_data.get('actual')
                        eps_estimate = eps_data.get('estimate')

                        if report_date:
                            # Insert or update
                            cur.execute("""
                                INSERT INTO earnings_events (
                                    symbol, earnings_date, eps_actual, eps_estimate, updated_at
                                )
                                VALUES (%s, %s, %s, %s, NOW())
                                ON CONFLICT (symbol, earnings_date)
                                DO UPDATE SET
                                    eps_actual = EXCLUDED.eps_actual,
                                    eps_estimate = EXCLUDED.eps_estimate,
                                    updated_at = NOW()
                            """, (symbol, report_date, eps_actual, eps_estimate))

                            synced += 1

                    progress_bar.progress((i + 1) / len(symbols))

                except Exception as e:
                    errors += 1
                    continue

            conn.commit()
            rh.logout()

            status_text.empty()
            progress_bar.empty()

            st.success(f"✅ Sync Complete! {synced} earnings synced, {errors} errors")
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Sync error: {str(e)}")
            conn.rollback()


def display_earnings_table(conn, cur):
    """Display earnings data in a table"""
    # Filters
    col_f1, col_f2, col_f3 = st.columns(3)

    with col_f1:
        date_filter = st.selectbox(
            "📅 Date Range",
            ["All Time", "This Week", "Next Week", "This Month", "Next Month"],
            key="earn_date_filter"
        )

    with col_f2:
        time_filter = st.selectbox(
            "⏰ Time",
            ["All", "BMO", "AMC"],
            key="earn_time_filter"
        )

    with col_f3:
        result_filter = st.selectbox(
            "📊 Result",
            ["All", "Beat", "Miss", "Meet", "Pending"],
            key="earn_result_filter"
        )

    # Build query
    query = """
        SELECT
            e.symbol,
            e.earnings_date,
            e.earnings_time,
            e.eps_estimate,
            e.eps_actual,
            e.revenue_estimate,
            e.revenue_actual,
            CASE
                WHEN e.eps_actual > e.eps_estimate THEN 'Beat'
                WHEN e.eps_actual < e.eps_estimate THEN 'Miss'
                WHEN e.eps_actual = e.eps_estimate THEN 'Meet'
                ELSE 'Pending'
            END as result,
            s.name as company_name,
            s.sector
        FROM earnings_events e
        LEFT JOIN stocks s ON e.symbol = s.ticker
        WHERE 1=1
    """

    params = []

    # Date filter
    if date_filter == "This Week":
        query += " AND e.earnings_date >= NOW() AND e.earnings_date <= NOW() + INTERVAL '7 days'"
    elif date_filter == "Next Week":
        query += " AND e.earnings_date >= NOW() + INTERVAL '7 days' AND e.earnings_date <= NOW() + INTERVAL '14 days'"
    elif date_filter == "This Month":
        query += " AND e.earnings_date >= NOW() AND e.earnings_date <= NOW() + INTERVAL '30 days'"
    elif date_filter == "Next Month":
        query += " AND e.earnings_date >= NOW() + INTERVAL '30 days' AND e.earnings_date <= NOW() + INTERVAL '60 days'"

    # Time filter
    if time_filter != "All":
        query += " AND e.earnings_time = %s"
        params.append(time_filter)

    query += " ORDER BY e.earnings_date DESC LIMIT 200"

    cur.execute(query, params)
    rows = cur.fetchall()

    if rows:
        df = pd.DataFrame(rows, columns=[
            'Symbol', 'Date', 'Time', 'EPS Est', 'EPS Act',
            'Rev Est', 'Rev Act', 'Result', 'Company', 'Sector'
        ])

        # Format date
        df['Date'] = pd.to_datetime(df['Date']).dt.strftime('%Y-%m-%d %H:%M')

        # Filter by result if needed
        if result_filter != "All":
            df = df[df['Result'] == result_filter]

        # Summary metrics
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("📊 Total Events", len(df))
        with col2:
            beats = len(df[df['Result'] == 'Beat'])
            st.metric("✅ Beats", beats, delta=f"{beats/len(df)*100:.0f}%" if len(df) > 0 else "0%")
        with col3:
            misses = len(df[df['Result'] == 'Miss'])
            st.metric("❌ Misses", misses, delta=f"-{misses/len(df)*100:.0f}%" if len(df) > 0 else "0%")
        with col4:
            pending = len(df[df['Result'] == 'Pending'])
            st.metric("⏳ Pending", pending)

        st.markdown("### 📊 Earnings Calendar")

        # Display table
        st.dataframe(
            df,
            hide_index=True,
            use_container_width=True,
            column_config={
                "Symbol": st.column_config.TextColumn("Symbol", width="small"),
                "Date": st.column_config.TextColumn("Date", width="medium"),
                "Time": st.column_config.TextColumn("Time", width="small"),
                "EPS Est": st.column_config.NumberColumn("EPS Est", format="%.2f"),
                "EPS Act": st.column_config.NumberColumn("EPS Act", format="%.2f"),
                "Rev Est": st.column_config.NumberColumn("Rev Est ($M)", format="%.0f"),
                "Rev Act": st.column_config.NumberColumn("Rev Act ($M)", format="%.0f"),
                "Result": st.column_config.TextColumn("Result", width="small"),
                "Company": st.column_config.TextColumn("Company", width="large"),
                "Sector": st.column_config.TextColumn("Sector", width="medium")
            }
        )

        # Export button
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Download CSV",
            data=csv,
            file_name="earnings_calendar.csv",
            mime="text/csv"
        )

    else:
        st.info("📭 No earnings found for selected filters")


# Add time import
import time
