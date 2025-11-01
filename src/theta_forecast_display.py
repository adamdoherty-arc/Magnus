"""
Display module for theta decay forecasting in the positions page
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.graph_objects as go
import yfinance as yf
from src.theta_calculator import ThetaCalculator


def display_theta_forecasts(csp_positions: list):
    """Display theta decay forecasts for CSP positions"""

    if not csp_positions:
        return

    st.markdown("---")
    st.markdown("### 📉 Theta Decay Forecasts")
    st.caption("Day-by-day profit projections until expiration")

    # Position selector
    position_labels = [f"{p['Symbol']} ${p['Strike']:.2f} exp {p['Expiration']}"
                      for p in csp_positions]
    selected_idx = st.selectbox(
        "Select CSP position:",
        options=range(len(csp_positions)),
        format_func=lambda i: position_labels[i],
        key="theta_forecast_selector"
    )

    position = csp_positions[selected_idx]

    # Extract position details
    symbol = position.get('symbol_raw', position['Symbol'])
    strike = float(position.get('Strike', 0))
    exp_date = datetime.strptime(position['Expiration'], '%Y-%m-%d')
    current_premium = abs(float(position.get('Current', 0))) / 100  # Convert to per-share price
    entry_premium = abs(float(position.get('Premium', 0))) / 100  # Convert to per-share price
    quantity = int(position.get('Contracts', 1))

    # Get current stock price and IV
    try:
        ticker = yf.Ticker(symbol)
        current_stock_price = ticker.history(period='1d')['Close'].iloc[-1]

        # Try to get IV from options chain
        try:
            exp_date_str = exp_date.strftime('%Y-%m-%d')
            options = ticker.option_chain(exp_date_str)
            puts = options.puts

            # Find the closest strike to our position
            closest_strike_idx = abs(puts['strike'] - strike).idxmin()
            iv = puts.loc[closest_strike_idx, 'impliedVolatility']

            # If IV is not available, use default
            if pd.isna(iv):
                iv = 0.30
        except:
            iv = 0.30  # Default 30% IV if can't fetch from options chain

    except:
        # Fallback if yfinance fails
        current_stock_price = position.get('Stock Price', strike * 1.05)
        iv = 0.30

    # Calculate forecast
    calculator = ThetaCalculator()
    forecast = calculator.calculate_forecast(
        current_price=current_stock_price,
        strike_price=strike,
        expiration_date=exp_date,
        current_premium=current_premium,
        entry_premium=entry_premium,
        implied_volatility=iv,
        quantity=quantity
    )

    # Display summary metrics
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Current P/L", f"${forecast.cumulative_pnl[0]:,.2f}")
    with col2:
        st.metric("Projected P/L at Exp", f"${forecast.cumulative_pnl[-1]:,.2f}")
    with col3:
        st.metric("Max Profit", f"${forecast.max_profit:,.2f}")
    with col4:
        st.metric("Days to Expiration", forecast.days_remaining[0])

    # Additional metrics row
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Stock Price", f"${current_stock_price:.2f}")
    with col2:
        moneyness = ((strike - current_stock_price) / current_stock_price * 100)
        st.metric("Moneyness", f"{moneyness:.1f}% {'OTM' if moneyness > 0 else 'ITM'}")
    with col3:
        st.metric("Implied Vol", f"{iv*100:.1f}%")
    with col4:
        if len(forecast.theta_values) > 0:
            current_theta = forecast.theta_values[0] * quantity * 100
            st.metric("Theta/Day", f"${current_theta:.2f}")

    # Plot forecast
    fig = go.Figure()

    # Main P/L projection line
    fig.add_trace(go.Scatter(
        x=forecast.dates,
        y=forecast.cumulative_pnl,
        mode='lines+markers',
        name='Projected P/L',
        line=dict(color='#00AA00', width=3),
        marker=dict(size=6),
        hovertemplate='Date: %{x|%Y-%m-%d}<br>P/L: $%{y:,.2f}<br>Days Left: %{customdata}<extra></extra>',
        customdata=forecast.days_remaining
    ))

    # Current value marker
    fig.add_trace(go.Scatter(
        x=[forecast.dates[0]],
        y=[forecast.cumulative_pnl[0]],
        mode='markers',
        name='Current',
        marker=dict(size=15, color='#FFA500', symbol='star'),
        hovertemplate='Current P/L: $%{y:,.2f}<extra></extra>'
    ))

    # Max profit line
    fig.add_hline(
        y=forecast.max_profit,
        line_dash="dash",
        line_color="green",
        annotation_text="Max Profit",
        annotation_position="right"
    )

    # Break-even line
    fig.add_hline(
        y=0,
        line_dash="dot",
        line_color="gray",
        annotation_text="Break-even",
        annotation_position="left"
    )

    fig.update_layout(
        title=f"Theta Decay Forecast: {symbol} ${strike:.2f} CSP",
        xaxis_title="Date",
        yaxis_title="Cumulative P/L ($)",
        hovermode='x unified',
        height=400,
        showlegend=True,
        legend=dict(
            yanchor="top",
            y=0.99,
            xanchor="left",
            x=0.01
        )
    )

    st.plotly_chart(fig, use_container_width=True)

    # Data table
    df = calculator.create_forecast_dataframe(forecast)
    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    df['Theta/Day'] = df['Theta/Day'].apply(lambda x: f"${x*quantity*100:.2f}")  # Convert to total position theta
    df['Option Value'] = df['Option Value'].apply(lambda x: f"${x:.2f}")
    df['Cumulative P/L'] = df['Cumulative P/L'].apply(lambda x: f"${x:,.2f}")

    # Show every nth row for large datasets
    if len(df) > 30:
        # Show first, last, and every 5th day
        indices = list(range(0, len(df), 5))
        if len(df) - 1 not in indices:
            indices.append(len(df) - 1)
        df_display = df.iloc[indices].copy()
    else:
        df_display = df.copy()

    with st.expander("📊 View Daily Forecast Table", expanded=False):
        st.dataframe(df_display, hide_index=True, use_container_width=True)

        # Export button for full data
        csv = df.to_csv(index=False)
        st.download_button(
            label="📥 Export Full Forecast to CSV",
            data=csv,
            file_name=f"{symbol}_{strike}_theta_forecast.csv",
            mime="text/csv"
        )

        # Analysis summary
        st.markdown("---")
        st.markdown("**📊 Forecast Analysis:**")

        # Calculate key insights
        if len(forecast.theta_values) > 0:
            avg_daily_decay = sum(forecast.theta_values) / len(forecast.theta_values) * quantity * 100
            total_expected_decay = forecast.cumulative_pnl[-1] - forecast.cumulative_pnl[0]
            moneyness = ((strike - current_stock_price) / current_stock_price * 100)

            col1, col2 = st.columns(2)
            with col1:
                st.write(f"**Average Daily Theta:** ${avg_daily_decay:.2f}")
                st.write(f"**Expected Decay to Expiration:** ${total_expected_decay:,.2f}")
            with col2:
                profit_probability = "High" if moneyness > 10 else "Medium" if moneyness > 5 else "Low"
                st.write(f"**Profit Probability:** {profit_probability} (based on moneyness)")
                st.write(f"**Risk-Free Rate Used:** {calculator.risk_free_rate*100:.1f}%")