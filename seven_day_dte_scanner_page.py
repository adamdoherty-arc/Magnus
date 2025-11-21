"""
7-Day DTE Cash-Secured Puts Scanner
Optimized for weekly theta decay and capital efficiency
"""
import streamlit as st
import psycopg2
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv()

st.set_page_config(page_title="7-Day DTE Scanner", page_icon="⚡", layout="wide")

# PERFORMANCE: Connection pooling with caching
@st.cache_resource
def get_connection():
    """Cached database connection (singleton pattern for connection pooling)"""
    return psycopg2.connect(
        host='localhost',
        port='5432',
        database='magnus',
        user='postgres',
        password=os.getenv('DB_PASSWORD')
    )

@st.cache_data(ttl=60)  # 1-minute cache for opportunities
def fetch_opportunities(dte_min, dte_max, delta_min=-0.4, delta_max=-0.2, min_premium=0):
    """Fetch CSP opportunities for given DTE range"""
    conn = get_connection()
    cur = conn.cursor()

    query = '''
        SELECT
            symbol,
            strike_price,
            premium,
            dte,
            premium_pct,
            annual_return,
            delta,
            prob_profit,
            implied_volatility,
            volume,
            open_interest,
            strike_type,
            expiration_date
        FROM stock_premiums
        WHERE dte BETWEEN %s AND %s
          AND premium > %s
          AND delta BETWEEN %s AND %s
          AND strike_price > 0
        ORDER BY (premium / dte) DESC
    '''

    cur.execute(query, (dte_min, dte_max, min_premium, delta_min, delta_max))
    columns = [desc[0] for desc in cur.description]
    results = cur.fetchall()
    cur.close()

    df = pd.DataFrame(results, columns=columns)

    # Calculate additional metrics
    if not df.empty:
        df['weekly_return'] = df['premium_pct']
        df['annualized_52wk'] = df['premium_pct'] * (365 / df['dte'])
        df['premium_per_day'] = df['premium'] / df['dte']
        df['risk_reward_ratio'] = df['premium'] / df['strike_price']

    return df

def calculate_compounding(initial_capital, weekly_return_pct, weeks):
    """Calculate weekly compounding returns"""
    value = initial_capital
    history = [value]

    for _ in range(weeks):
        value = value * (1 + weekly_return_pct / 100)
        history.append(value)

    return history

# Page Header
st.title("⚡ 7-Day DTE Cash-Secured Puts Scanner")
st.markdown("""
**Optimized for Weekly Theta Decay & Capital Efficiency**

Research shows 7-day DTE generates **32.04% annualized returns** vs 28.80% for 30-day DTE.
This page helps you find and compare the best weekly opportunities.
""")

# Strategy Overview
with st.expander("📊 Why 7-Day DTE?"):
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Theta Decay", "3-4x Faster", help="Theta accelerates dramatically in final 7 days")

    with col2:
        st.metric("Capital Efficiency", "52x Per Year", help="Deploy capital weekly vs monthly")

    with col3:
        st.metric("Annualized Return", "+3.24%", help="32.04% vs 28.80% for 30-day DTE")

    st.markdown("""
    **Advantages:**
    - Accelerated theta decay in final week
    - Weekly compounding opportunities
    - More responsive to market changes
    - Lower gamma risk duration

    **Considerations:**
    - Requires active weekly management
    - Higher transaction costs (more frequent trades)
    - Less time to recover if ITM
    - Need to monitor daily
    """)

# Filters
st.subheader("🎯 Opportunity Filters")
col1, col2, col3, col4 = st.columns(4)

with col1:
    dte_range = st.select_slider(
        "DTE Range",
        options=['5-7 Days (Weekly)', '7-Day DTE (5-9)', '30-Day DTE (25-35)', 'Both'],
        value='7-Day DTE (5-9)'
    )

with col2:
    delta_range = st.slider(
        "Delta Range",
        min_value=-0.5,
        max_value=-0.1,
        value=(-0.4, -0.2),
        step=0.05,
        help="Probability of profit: -0.30 delta ≈ 70% PoP"
    )

with col3:
    min_premium = st.number_input(
        "Min Premium ($)",
        min_value=0.0,
        value=0.0,
        step=10.0
    )

with col4:
    min_annual_return = st.number_input(
        "Min Annualized Return (%)",
        min_value=0.0,
        value=30.0,
        step=5.0
    )

# Fetch data based on selection
if dte_range == '5-7 Days (Weekly)':
    df_7day = fetch_opportunities(5, 7, delta_range[0], delta_range[1], min_premium)
    df_30day = pd.DataFrame()
elif dte_range == '7-Day DTE (5-9)':
    df_7day = fetch_opportunities(5, 9, delta_range[0], delta_range[1], min_premium)
    df_30day = pd.DataFrame()
elif dte_range == '30-Day DTE (25-35)':
    df_7day = pd.DataFrame()
    df_30day = fetch_opportunities(25, 35, delta_range[0], delta_range[1], min_premium)
else:  # Both
    df_7day = fetch_opportunities(5, 9, delta_range[0], delta_range[1], min_premium)
    df_30day = fetch_opportunities(25, 35, delta_range[0], delta_range[1], min_premium)

# Filter by min annual return
if not df_7day.empty:
    df_7day = df_7day[df_7day['annualized_52wk'] >= min_annual_return]
if not df_30day.empty:
    df_30day = df_30day[df_30day['annual_return'] >= min_annual_return]

# Summary Stats
st.subheader("📈 Performance Comparison")

col1, col2 = st.columns(2)

with col1:
    st.markdown("### 7-Day DTE (Weekly)")
    if not df_7day.empty:
        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric("Opportunities", len(df_7day))

        with metric_col2:
            avg_weekly = df_7day['premium_pct'].mean()
            st.metric("Avg Weekly Return", f"{avg_weekly:.2f}%")

        with metric_col3:
            avg_annual = df_7day['annualized_52wk'].mean()
            st.metric("Avg Annualized", f"{avg_annual:.1f}%")
    else:
        st.info("No 7-day opportunities match current filters")

with col2:
    st.markdown("### 30-Day DTE (Monthly)")
    if not df_30day.empty:
        metric_col1, metric_col2, metric_col3 = st.columns(3)

        with metric_col1:
            st.metric("Opportunities", len(df_30day))

        with metric_col2:
            avg_monthly = df_30day['premium_pct'].mean()
            st.metric("Avg Monthly Return", f"{avg_monthly:.2f}%")

        with metric_col3:
            avg_annual = df_30day['annual_return'].mean()
            st.metric("Avg Annualized", f"{avg_annual:.1f}%")
    else:
        st.info("No 30-day opportunities match current filters")

# Top Opportunities
st.subheader("🏆 Top Opportunities")

if not df_7day.empty:
    st.markdown("#### 7-Day DTE")

    # Format display dataframe
    display_df = df_7day.head(20).copy()
    display_df['Strike'] = display_df['strike_price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
    display_df['Premium'] = display_df['premium'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
    display_df['Weekly%'] = display_df['premium_pct'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
    display_df['Annual%'] = display_df['annualized_52wk'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
    display_df['Delta'] = display_df['delta'].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "")
    display_df['PoP%'] = display_df['prob_profit'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
    display_df['$/Day'] = display_df['premium_per_day'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")

    st.dataframe(
        display_df[['symbol', 'Strike', 'Premium', 'dte', 'Weekly%', 'Annual%', 'Delta', 'PoP%', '$/Day', 'strike_type']],
        use_container_width=True,
        height=400
    )

    # Download button
    csv = df_7day.to_csv(index=False)
    st.download_button(
        label="📥 Download 7-Day Opportunities (CSV)",
        data=csv,
        file_name=f"7day_csp_opportunities_{datetime.now().strftime('%Y%m%d')}.csv",
        mime="text/csv"
    )

if not df_30day.empty:
    st.markdown("#### 30-Day DTE (For Comparison)")

    display_df = df_30day.head(20).copy()
    display_df['Strike'] = display_df['strike_price'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
    display_df['Premium'] = display_df['premium'].apply(lambda x: f"${x:.2f}" if pd.notna(x) else "")
    display_df['Monthly%'] = display_df['premium_pct'].apply(lambda x: f"{x:.2f}%" if pd.notna(x) else "")
    display_df['Annual%'] = display_df['annual_return'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")
    display_df['Delta'] = display_df['delta'].apply(lambda x: f"{x:.3f}" if pd.notna(x) else "")
    display_df['PoP%'] = display_df['prob_profit'].apply(lambda x: f"{x:.1f}%" if pd.notna(x) else "")

    st.dataframe(
        display_df[['symbol', 'Strike', 'Premium', 'dte', 'Monthly%', 'Annual%', 'Delta', 'PoP%', 'strike_type']],
        use_container_width=True,
        height=400
    )

# Weekly Compounding Calculator
st.subheader("💰 Weekly Compounding Calculator")

calc_col1, calc_col2, calc_col3, calc_col4 = st.columns(4)

with calc_col1:
    initial_capital = st.number_input("Initial Capital ($)", min_value=1000, value=10000, step=1000)

with calc_col2:
    if not df_7day.empty:
        default_weekly_return = df_7day['premium_pct'].median()
    else:
        default_weekly_return = 2.0
    weekly_return = st.number_input("Weekly Return (%)", min_value=0.1, value=float(default_weekly_return), step=0.1)

with calc_col3:
    num_weeks = st.number_input("Number of Weeks", min_value=1, max_value=52, value=12)

with calc_col4:
    trades_per_week = st.number_input("Trades Per Week", min_value=1, max_value=5, value=1)

# Calculate compounding
compound_history = calculate_compounding(initial_capital, weekly_return * trades_per_week, num_weeks)
final_value = compound_history[-1]
total_gain = final_value - initial_capital
total_return_pct = (total_gain / initial_capital) * 100
annualized_return = total_return_pct * (52 / num_weeks)

# Display results
result_col1, result_col2, result_col3 = st.columns(3)

with result_col1:
    st.metric("Final Value", f"${final_value:,.2f}", f"+${total_gain:,.2f}")

with result_col2:
    st.metric("Total Return", f"{total_return_pct:.1f}%", f"{num_weeks} weeks")

with result_col3:
    st.metric("Annualized Return", f"{annualized_return:.1f}%", "52-week projection")

# Compounding chart
fig_compound = go.Figure()
fig_compound.add_trace(go.Scatter(
    x=list(range(len(compound_history))),
    y=compound_history,
    mode='lines+markers',
    name='Portfolio Value',
    line=dict(color='#00D9FF', width=3),
    marker=dict(size=6)
))

fig_compound.update_layout(
    title="Weekly Compounding Growth",
    xaxis_title="Week",
    yaxis_title="Portfolio Value ($)",
    height=400,
    template="plotly_dark",
    hovermode='x unified'
)

st.plotly_chart(fig_compound, use_container_width=True)

# Comparison visualization
if not df_7day.empty and not df_30day.empty:
    st.subheader("📊 7-Day vs 30-Day Comparison")

    # Create comparison dataframe
    comparison_data = {
        'Strategy': ['7-Day DTE', '30-Day DTE'],
        'Avg Weekly/Monthly Return': [
            df_7day['premium_pct'].mean(),
            df_30day['premium_pct'].mean()
        ],
        'Avg Annualized Return': [
            df_7day['annualized_52wk'].mean(),
            df_30day['annual_return'].mean()
        ],
        'Opportunities': [len(df_7day), len(df_30day)],
        'Avg DTE': [df_7day['dte'].mean(), df_30day['dte'].mean()]
    }

    comparison_df = pd.DataFrame(comparison_data)

    # Bar chart
    fig_comparison = go.Figure()

    fig_comparison.add_trace(go.Bar(
        name='7-Day DTE',
        x=['Weekly Return', 'Annualized', 'Opportunities'],
        y=[comparison_df.loc[0, 'Avg Weekly/Monthly Return'],
           comparison_df.loc[0, 'Avg Annualized Return'],
           comparison_df.loc[0, 'Opportunities']],
        marker_color='#00D9FF'
    ))

    fig_comparison.add_trace(go.Bar(
        name='30-Day DTE',
        x=['Monthly Return', 'Annualized', 'Opportunities'],
        y=[comparison_df.loc[1, 'Avg Weekly/Monthly Return'],
           comparison_df.loc[1, 'Avg Annualized Return'],
           comparison_df.loc[1, 'Opportunities']],
        marker_color='#FF6B9D'
    ))

    fig_comparison.update_layout(
        title="Strategy Comparison",
        barmode='group',
        height=400,
        template="plotly_dark",
        yaxis_title="Value"
    )

    st.plotly_chart(fig_comparison, use_container_width=True)

# Footer
st.markdown("---")
st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
st.caption("Research: 7-Day DTE = 32.04% annualized | 30-Day DTE = 28.80% annualized | Based on historical theta decay analysis")
