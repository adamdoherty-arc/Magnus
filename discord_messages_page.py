"""
XTrade Messages Page
View and analyze XTrade alerts and signals from Discord channels
"""

import streamlit as st
import pandas as pd
import psycopg2
import psycopg2.extras
from datetime import datetime, timedelta
import os
import re
import json

st.set_page_config(page_title="XTrade Messages", page_icon="📱", layout="wide")


class DiscordDB:
    """Discord database manager"""

    def __init__(self):
        self.db_host = os.getenv('DB_HOST', 'localhost')
        self.db_port = os.getenv('DB_PORT', '5432')
        self.db_name = os.getenv('DB_NAME', 'trading')
        self.db_user = os.getenv('DB_USER', 'postgres')
        self.db_password = os.getenv('DB_PASSWORD', '')

    def get_connection(self):
        return psycopg2.connect(
            host=self.db_host,
            port=self.db_port,
            database=self.db_name,
            user=self.db_user,
            password=self.db_password
        )

    def get_channels(self):
        """Get all Discord channels"""
        conn = None
        cur = None
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
            cur.execute("""
                SELECT
                    channel_id,
                    channel_name,
                    server_name,
                    last_sync,
                    (SELECT COUNT(*) FROM discord_messages WHERE channel_id = c.channel_id) as message_count
                FROM discord_channels c
                ORDER BY last_sync DESC NULLS LAST
            """)
            return cur.fetchall()
        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def get_messages(self, channel_id=None, search_term=None, hours_back=24, limit=100):
        """Get Discord messages with filters"""
        conn = None
        cur = None
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            query = """
                SELECT
                    m.message_id,
                    m.content,
                    m.author_name,
                    m.timestamp,
                    c.channel_name,
                    c.server_name,
                    m.reactions,
                    m.attachments,
                    m.embeds
                FROM discord_messages m
                JOIN discord_channels c ON m.channel_id = c.channel_id
                WHERE m.timestamp >= NOW() - INTERVAL '%s hours'
            """
            params = [hours_back]

            if channel_id:
                query += " AND m.channel_id = %s"
                params.append(channel_id)

            if search_term:
                query += " AND m.content ILIKE %s"
                params.append(f'%{search_term}%')

            query += " ORDER BY m.timestamp DESC LIMIT %s"
            params.append(limit)

            cur.execute(query, params)
            return cur.fetchall()

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()

    def search_betting_signals(self, hours_back=24):
        """Search for betting-related messages"""
        conn = None
        cur = None
        try:
            conn = self.get_connection()
            cur = conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

            # Keywords for betting signals
            betting_keywords = [
                'bet', 'odds', 'spread', 'moneyline', 'under', 'over',
                'parlay', 'pick', 'lock', 'play', 'wager'
            ]

            # Build search condition
            search_conditions = ' OR '.join([f"content ILIKE '%{kw}%'" for kw in betting_keywords])

            query = f"""
                SELECT
                    m.message_id,
                    m.content,
                    m.author_name,
                    m.timestamp,
                    c.channel_name,
                    c.server_name,
                    m.reactions
                FROM discord_messages m
                JOIN discord_channels c ON m.channel_id = c.channel_id
                WHERE m.timestamp >= NOW() - INTERVAL '{hours_back} hours'
                AND ({search_conditions})
                ORDER BY m.timestamp DESC
                LIMIT 200
            """

            cur.execute(query)
            return cur.fetchall()

        finally:
            if cur:
                cur.close()
            if conn:
                conn.close()


def parse_betting_signal(content: str):
    """Parse betting signal from message content"""
    # Look for patterns like:
    # "Lakers -5.5"
    # "Over 220.5"
    # "Moneyline: Chiefs"

    signal = {
        'team': None,
        'spread': None,
        'total': None,
        'moneyline': None,
        'confidence': 'LOW'
    }

    # Spread pattern
    spread_match = re.search(r'([A-Za-z\s]+)\s*([-+]?\d+\.?\d*)', content)
    if spread_match:
        signal['team'] = spread_match.group(1).strip()
        signal['spread'] = spread_match.group(2)

    # Total pattern
    total_match = re.search(r'(over|under)\s*(\d+\.?\d*)', content, re.IGNORECASE)
    if total_match:
        signal['total'] = f"{total_match.group(1)} {total_match.group(2)}"

    # Confidence indicators
    if any(word in content.lower() for word in ['lock', 'max bet', 'confident']):
        signal['confidence'] = 'HIGH'
    elif any(word in content.lower() for word in ['lean', 'like']):
        signal['confidence'] = 'MEDIUM'

    return signal


def analyze_trading_signal(content: str, author: str, timestamp: datetime):
    """Analyze Discord message for trading signals using pattern matching"""

    signal = {
        'message': content[:100],  # First 100 chars
        'author': author,
        'timestamp': timestamp,
        'ticker': None,
        'action': None,
        'entry_price': None,
        'target': None,
        'stop_loss': None,
        'confidence': 0,
        'signal_type': None
    }

    # Extract ticker symbols ($XXX or plain symbols)
    ticker_patterns = [
        r'\$([A-Z]{1,5})',  # $AAPL
        r'\b([A-Z]{2,5})\b',  # AAPL
    ]

    tickers = []
    for pattern in ticker_patterns:
        matches = re.findall(pattern, content.upper())
        tickers.extend(matches)

    if tickers:
        signal['ticker'] = tickers[0]

    # Detect action (buy/sell/long/short)
    content_lower = content.lower()
    if any(word in content_lower for word in ['buy', 'long', 'call', 'bullish']):
        signal['action'] = 'BUY'
    elif any(word in content_lower for word in ['sell', 'short', 'put', 'bearish']):
        signal['action'] = 'SELL'

    # Extract price levels
    price_pattern = r'\$?(\d+(?:\.\d{1,2})?)'
    prices = re.findall(price_pattern, content)

    if len(prices) >= 1:
        signal['entry_price'] = float(prices[0])
    if len(prices) >= 2:
        signal['target'] = float(prices[1])
    if len(prices) >= 3:
        signal['stop_loss'] = float(prices[2])

    # Detect signal type
    if any(word in content_lower for word in ['option', 'call', 'put']):
        signal['signal_type'] = 'OPTIONS'
    elif any(word in content_lower for word in ['swing', 'day trade']):
        signal['signal_type'] = 'SWING'
    else:
        signal['signal_type'] = 'STOCK'

    # Calculate confidence score (0-100)
    confidence_score = 0

    # Has ticker
    if signal['ticker']:
        confidence_score += 30

    # Has action
    if signal['action']:
        confidence_score += 20

    # Has price targets
    if signal['entry_price']:
        confidence_score += 20
    if signal['target']:
        confidence_score += 15
    if signal['stop_loss']:
        confidence_score += 15

    # Confidence keywords
    if any(word in content_lower for word in ['lock', 'confident', 'strong']):
        confidence_score = min(100, confidence_score + 20)
    elif any(word in content_lower for word in ['maybe', 'risky', 'uncertain']):
        confidence_score = max(0, confidence_score - 20)

    signal['confidence'] = confidence_score

    # Only return if it looks like a trade signal (has ticker + action OR ticker + prices)
    if signal['ticker'] and (signal['action'] or signal['entry_price']):
        return signal

    return None


def main():
    st.title("📱 XTrade Messages")
    st.markdown("Monitor betting signals from Discord channels")

    db = DiscordDB()

    # Sidebar filters
    with st.sidebar:
        st.header("⚙️ Filters")

        # Get channels
        channels = db.get_channels()

        if channels:
            channel_options = {
                f"{c['server_name']} / {c['channel_name']}": c['channel_id']
                for c in channels
            }
            channel_options = {"All Channels": None, **channel_options}

            selected_channel_name = st.selectbox("Channel", list(channel_options.keys()))
            selected_channel = channel_options[selected_channel_name]
        else:
            selected_channel = None
            st.warning("No channels configured")

        hours_back = st.slider("Hours Back", 1, 168, 24)

        search_term = st.text_input("Search Messages", placeholder="Enter keywords...")

        betting_only = st.checkbox("Betting Signals Only", value=False)

        if st.button("🔄 Refresh"):
            st.rerun()

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric("Channels", len(channels) if channels else 0)

    with col2:
        total_messages = sum(c.get('message_count', 0) for c in channels) if channels else 0
        st.metric("Total Messages", f"{total_messages:,}")

    with col3:
        if channels and channels[0].get('last_sync'):
            last_sync = channels[0]['last_sync']
            st.metric("Last Sync", last_sync.strftime('%H:%M'))
        else:
            st.metric("Last Sync", "Never")

    with col4:
        st.metric("Time Range", f"{hours_back}h")

    st.markdown("---")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📨 Messages", "🎯 Betting Signals", "💰 AI Trading Signals", "📊 Analytics"])

    with tab1:
        st.markdown("### Recent Messages")

        # Fetch messages
        if betting_only:
            messages = db.search_betting_signals(hours_back=hours_back)
        else:
            messages = db.get_messages(
                channel_id=selected_channel,
                search_term=search_term,
                hours_back=hours_back,
                limit=200
            )

        if messages:
            st.info(f"Found {len(messages)} messages")

            for msg in messages:
                # Calculate time ago
                time_ago = datetime.now() - msg['timestamp']
                if time_ago.days > 0:
                    time_str = f"{time_ago.days}d ago"
                elif time_ago.seconds > 3600:
                    time_str = f"{time_ago.seconds // 3600}h ago"
                else:
                    time_str = f"{time_ago.seconds // 60}m ago"

                # Display message
                with st.container():
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.markdown(f"""
                            **{msg['author_name']}** • {msg['server_name']} / {msg['channel_name']}
                        """)
                        st.write(msg['content'])

                    with col2:
                        st.caption(time_str)
                        st.caption(msg['timestamp'].strftime('%m/%d %H:%M'))

                    # Reactions
                    if msg.get('reactions'):
                        import json
                        try:
                            reactions = json.loads(msg['reactions']) if isinstance(msg['reactions'], str) else msg['reactions']
                            if reactions:
                                reaction_str = " ".join([f"{r.get('emoji', {}).get('name', '?')} {r.get('count', 0)}" for r in reactions])
                                st.caption(f"Reactions: {reaction_str}")
                        except:
                            pass

                    st.markdown("---")

        else:
            st.warning("No messages found")

    with tab2:
        st.markdown("### 🎯 Betting Signals")
        st.markdown("Messages containing betting keywords")

        signals = db.search_betting_signals(hours_back=hours_back)

        if signals:
            st.success(f"Found {len(signals)} betting-related messages")

            for msg in signals:
                # Parse signal
                parsed = parse_betting_signal(msg['content'])

                # Color based on confidence
                if parsed['confidence'] == 'HIGH':
                    border_color = '#00ff00'
                    bg_color = 'rgba(0, 255, 0, 0.1)'
                elif parsed['confidence'] == 'MEDIUM':
                    border_color = '#ffd700'
                    bg_color = 'rgba(255, 215, 0, 0.1)'
                else:
                    border_color = '#888888'
                    bg_color = 'rgba(136, 136, 136, 0.1)'

                st.markdown(f"""
                    <div style="border-left: 4px solid {border_color}; background: {bg_color};
                                padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                        <p style="margin: 0;"><strong>{msg['author_name']}</strong> • {msg['channel_name']}</p>
                        <p style="margin: 5px 0; color: #aaa;">{msg['timestamp'].strftime('%m/%d %H:%M')}</p>
                    </div>
                """, unsafe_allow_html=True)

                st.write(msg['content'])

                # Show parsed info
                col1, col2, col3 = st.columns(3)
                with col1:
                    if parsed['team']:
                        st.metric("Team", parsed['team'])
                with col2:
                    if parsed['spread']:
                        st.metric("Spread", parsed['spread'])
                with col3:
                    st.metric("Confidence", parsed['confidence'])

                st.markdown("---")

        else:
            st.warning("No betting signals found")

    with tab3:
        st.markdown("### 💰 AI Trading Signals")
        st.markdown("AI-detected trading alerts from Discord messages")

        # Fetch messages for analysis
        if betting_only:
            analysis_messages = db.search_betting_signals(hours_back=hours_back)
        else:
            analysis_messages = db.get_messages(
                channel_id=selected_channel,
                search_term=search_term,
                hours_back=hours_back,
                limit=500
            )

        if analysis_messages:
            # Analyze all messages for trading signals
            trading_signals = []
            for msg in analysis_messages:
                signal = analyze_trading_signal(
                    msg['content'],
                    msg['author_name'],
                    msg['timestamp']
                )
                if signal:
                    trading_signals.append(signal)

            if trading_signals:
                st.success(f"Found {len(trading_signals)} trading signals")

                # Convert to DataFrame
                signals_df = pd.DataFrame(trading_signals)

                # Sort by confidence (highest first)
                signals_df = signals_df.sort_values('confidence', ascending=False)

                # Display summary stats
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    buy_signals = len(signals_df[signals_df['action'] == 'BUY'])
                    st.metric("Buy Signals", buy_signals)

                with col2:
                    sell_signals = len(signals_df[signals_df['action'] == 'SELL'])
                    st.metric("Sell Signals", sell_signals)

                with col3:
                    avg_confidence = signals_df['confidence'].mean()
                    st.metric("Avg Confidence", f"{avg_confidence:.0f}%")

                with col4:
                    high_conf = len(signals_df[signals_df['confidence'] >= 70])
                    st.metric("High Confidence", high_conf)

                st.markdown("---")

                # Display signals table
                st.markdown("#### Trading Signals Table")

                # Format for display
                display_df = signals_df[[
                    'timestamp', 'author', 'ticker', 'action', 'signal_type',
                    'entry_price', 'target', 'stop_loss', 'confidence', 'message'
                ]].copy()

                # Format timestamp
                display_df['timestamp'] = pd.to_datetime(display_df['timestamp']).dt.strftime('%m/%d %H:%M')

                # Format prices
                for col in ['entry_price', 'target', 'stop_loss']:
                    display_df[col] = display_df[col].apply(lambda x: f"${x:.2f}" if pd.notna(x) and x > 0 else "-")

                # Format confidence as percentage
                display_df['confidence'] = display_df['confidence'].apply(lambda x: f"{x:.0f}%")

                # Rename columns
                display_df.columns = [
                    'Time', 'Author', 'Ticker', 'Action', 'Type',
                    'Entry', 'Target', 'Stop', 'Confidence', 'Message'
                ]

                # Color code by confidence
                def highlight_confidence(row):
                    conf = int(row['Confidence'].rstrip('%'))
                    if conf >= 70:
                        return ['background-color: rgba(0, 255, 0, 0.2)'] * len(row)
                    elif conf >= 50:
                        return ['background-color: rgba(255, 215, 0, 0.2)'] * len(row)
                    else:
                        return ['background-color: rgba(255, 0, 0, 0.1)'] * len(row)

                st.dataframe(
                    display_df.style.apply(highlight_confidence, axis=1),
                    use_container_width=True,
                    height=600
                )

                # Download button
                csv = signals_df.to_csv(index=False)
                st.download_button(
                    label="Download Signals CSV",
                    data=csv,
                    file_name=f"trading_signals_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )

            else:
                st.warning("No trading signals detected in messages")

        else:
            st.warning("No messages to analyze")

    with tab4:
        st.markdown("### 📊 Analytics")

        if messages:
            # Author activity
            st.markdown("#### 👥 Most Active Users")
            author_counts = {}
            for msg in messages:
                author = msg['author_name']
                author_counts[author] = author_counts.get(author, 0) + 1

            author_df = pd.DataFrame([
                {'Author': k, 'Messages': v}
                for k, v in sorted(author_counts.items(), key=lambda x: x[1], reverse=True)[:10]
            ])

            st.dataframe(author_df, use_container_width=True)

            # Message timeline
            st.markdown("#### 📈 Message Activity")
            msg_times = [msg['timestamp'] for msg in messages]
            timeline_df = pd.DataFrame({'timestamp': msg_times})
            timeline_df['hour'] = timeline_df['timestamp'].dt.hour
            hourly_counts = timeline_df['hour'].value_counts().sort_index()

            st.line_chart(hourly_counts)

            # Word cloud
            st.markdown("#### 💬 Common Keywords")
            all_content = ' '.join([msg['content'] for msg in messages])
            words = re.findall(r'\b[a-z]{4,}\b', all_content.lower())
            word_counts = {}
            for word in words:
                if word not in ['that', 'this', 'with', 'from', 'have', 'been']:
                    word_counts[word] = word_counts.get(word, 0) + 1

            top_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:20]
            words_df = pd.DataFrame(top_words, columns=['Word', 'Count'])

            st.dataframe(words_df, use_container_width=True)

        else:
            st.info("No data for analytics")

    # Setup instructions
    with st.expander("⚙️ Setup Instructions"):
        st.markdown("""
        ### Discord Message Sync Setup

        1. **Get Discord User Token**:
           - Open Discord in browser
           - Press F12 (DevTools)
           - Go to Network tab
           - Refresh Discord
           - Find any request, look for "authorization" header
           - Copy the token

        2. **Install DiscordChatExporter**:
           ```bash
           # Download from https://github.com/Tyrrrz/DiscordChatExporter
           # Or use dotnet tool:
           dotnet tool install -g DiscordChatExporter.Cli
           ```

        3. **Add to .env**:
           ```
           DISCORD_USER_TOKEN=your_token_here
           DISCORD_EXPORTER_PATH=path/to/DiscordChatExporter.Cli.exe
           ```

        4. **Sync Channel**:
           ```bash
           python src/discord_message_sync.py CHANNEL_ID 7
           ```

        5. **Automate** (Windows Task Scheduler):
           - Schedule to run every hour
           - Pulls latest messages automatically

        **Note**: Using user tokens violates Discord ToS. Use at your own risk.
        """)


if __name__ == "__main__":
    main()
