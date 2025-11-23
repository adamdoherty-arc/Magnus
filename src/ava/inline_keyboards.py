"""
AVA Inline Keyboards
====================

Rich interactive keyboards for Telegram bot using latest 2024-2025 API features.

Features:
- Inline keyboard builders for all bot interactions
- Callback button handlers
- Copy buttons for tickers and commands
- URL buttons for external links
- Action buttons for portfolio, positions, and analysis
- Pagination support for long lists

Usage:
    from src.ava.inline_keyboards import (
        build_portfolio_keyboard,
        build_position_keyboard,
        build_stock_analysis_keyboard
    )

    # Send message with inline keyboard
    await update.message.reply_text(
        "Your portfolio:",
        reply_markup=build_portfolio_keyboard()
    )
"""

from typing import List, Optional, Dict, Any
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


# ==================== Portfolio Keyboards ====================

def build_portfolio_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for portfolio actions.

    Returns:
        InlineKeyboardMarkup with portfolio action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="portfolio_refresh"),
            InlineKeyboardButton("📊 Detailed View", callback_data="portfolio_detailed"),
        ],
        [
            InlineKeyboardButton("📈 Balance Chart", callback_data="portfolio_chart"),
            InlineKeyboardButton("📋 Positions", callback_data="show_positions"),
        ],
        [
            InlineKeyboardButton("💰 P&L Summary", callback_data="portfolio_pnl"),
            InlineKeyboardButton("🎯 Performance", callback_data="portfolio_performance"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_positions_keyboard(positions: List[Dict[str, Any]] = None) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for options positions.

    Args:
        positions: List of position dictionaries (optional, for pagination)

    Returns:
        InlineKeyboardMarkup with position action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh Positions", callback_data="positions_refresh"),
            InlineKeyboardButton("📊 Show Greeks", callback_data="positions_greeks"),
        ],
        [
            InlineKeyboardButton("💹 P&L Analysis", callback_data="positions_pnl"),
            InlineKeyboardButton("⚠️ Risk Analysis", callback_data="positions_risk"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Portfolio", callback_data="show_portfolio"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_position_actions_keyboard(ticker: str, position_id: Optional[int] = None) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for individual position actions.

    Args:
        ticker: Stock ticker symbol
        position_id: Position ID in database

    Returns:
        InlineKeyboardMarkup with position-specific actions
    """
    callback_prefix = f"pos_{position_id}" if position_id else f"pos_{ticker}"

    keyboard = [
        [
            InlineKeyboardButton("📊 View Greeks", callback_data=f"{callback_prefix}_greeks"),
            InlineKeyboardButton("📈 Price Chart", callback_data=f"{callback_prefix}_chart"),
        ],
        [
            InlineKeyboardButton("🔄 Roll Position", callback_data=f"{callback_prefix}_roll"),
            InlineKeyboardButton("❌ Close Position", callback_data=f"{callback_prefix}_close"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Positions", callback_data="show_positions"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== Stock Analysis Keyboards ====================

def build_stock_analysis_keyboard(ticker: str) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for stock analysis actions.

    Args:
        ticker: Stock ticker symbol

    Returns:
        InlineKeyboardMarkup with analysis action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("💰 CSP Analysis", callback_data=f"analyze_csp_{ticker}"),
            InlineKeyboardButton("📊 View Greeks", callback_data=f"analyze_greeks_{ticker}"),
        ],
        [
            InlineKeyboardButton("📈 Price Chart", callback_data=f"chart_{ticker}"),
            InlineKeyboardButton("📅 Earnings", callback_data=f"earnings_{ticker}"),
        ],
        [
            InlineKeyboardButton("📰 News", callback_data=f"news_{ticker}"),
            InlineKeyboardButton("🎯 Options Flow", callback_data=f"flow_{ticker}"),
        ],
        [
            InlineKeyboardButton(f"📋 Copy {ticker}", callback_data=f"copy_{ticker}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_csp_opportunities_keyboard(opportunities: List[Dict[str, Any]] = None) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for CSP opportunities.

    Args:
        opportunities: List of CSP opportunity dictionaries

    Returns:
        InlineKeyboardMarkup with opportunity action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data="csp_refresh"),
            InlineKeyboardButton("🎯 Top 10", callback_data="csp_top10"),
        ],
        [
            InlineKeyboardButton("💎 High Premium", callback_data="csp_high_premium"),
            InlineKeyboardButton("🛡️ Safe Plays", callback_data="csp_safe"),
        ],
        [
            InlineKeyboardButton("📊 Filters", callback_data="csp_filters"),
        ],
    ]

    # Add individual opportunity buttons if provided
    if opportunities:
        for i, opp in enumerate(opportunities[:5]):  # Show max 5
            ticker = opp.get("ticker", "?")
            premium = opp.get("premium", 0)
            keyboard.append([
                InlineKeyboardButton(
                    f"🎯 {ticker} (${premium:.2f})",
                    callback_data=f"analyze_csp_{ticker}"
                )
            ])

    return InlineKeyboardMarkup(keyboard)


# ==================== TradingView Keyboards ====================

def build_tradingview_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for TradingView integration.

    Returns:
        InlineKeyboardMarkup with TradingView action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("📋 My Watchlists", callback_data="tv_watchlists"),
            InlineKeyboardButton("🔔 Recent Alerts", callback_data="tv_alerts"),
        ],
        [
            InlineKeyboardButton("📊 View Chart", callback_data="tv_chart"),
            InlineKeyboardButton("🎯 Top Movers", callback_data="tv_movers"),
        ],
        [
            InlineKeyboardButton("🌐 Open TradingView", url="https://www.tradingview.com"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_watchlist_keyboard(watchlist_name: str, symbols: List[str] = None) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for TradingView watchlist.

    Args:
        watchlist_name: Name of the watchlist
        symbols: List of ticker symbols in watchlist

    Returns:
        InlineKeyboardMarkup with watchlist action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔄 Refresh", callback_data=f"tv_watchlist_refresh_{watchlist_name}"),
            InlineKeyboardButton("📊 Summary", callback_data=f"tv_watchlist_summary_{watchlist_name}"),
        ],
    ]

    # Add individual symbol buttons
    if symbols:
        for symbol in symbols[:10]:  # Show max 10
            keyboard.append([
                InlineKeyboardButton(
                    f"📈 {symbol}",
                    callback_data=f"analyze_{symbol}"
                )
            ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back to Watchlists", callback_data="tv_watchlists")
    ])

    return InlineKeyboardMarkup(keyboard)


# ==================== Xtrades Keyboards ====================

def build_xtrades_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for Xtrades integration.

    Returns:
        InlineKeyboardMarkup with Xtrades action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("👥 Following", callback_data="xtrades_following"),
            InlineKeyboardButton("🔔 Recent Alerts", callback_data="xtrades_alerts"),
        ],
        [
            InlineKeyboardButton("🏆 Top Traders", callback_data="xtrades_top_traders"),
            InlineKeyboardButton("📊 My Tracked", callback_data="xtrades_tracked"),
        ],
        [
            InlineKeyboardButton("🌐 Open Xtrades", url="https://xtrades.net"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_trader_keyboard(trader_username: str, trader_id: Optional[str] = None) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for Xtrades trader profile.

    Args:
        trader_username: Username of the trader
        trader_id: Trader ID in database

    Returns:
        InlineKeyboardMarkup with trader action buttons
    """
    callback_prefix = f"trader_{trader_id}" if trader_id else f"trader_{trader_username}"

    keyboard = [
        [
            InlineKeyboardButton("📊 View Profile", callback_data=f"{callback_prefix}_profile"),
            InlineKeyboardButton("📈 Recent Trades", callback_data=f"{callback_prefix}_trades"),
        ],
        [
            InlineKeyboardButton("🔔 Enable Alerts", callback_data=f"{callback_prefix}_alerts_on"),
            InlineKeyboardButton("🔕 Disable Alerts", callback_data=f"{callback_prefix}_alerts_off"),
        ],
        [
            InlineKeyboardButton("🔙 Back to Following", callback_data="xtrades_following"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_alert_keyboard(alert_id: int, ticker: str) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for trade alert.

    Args:
        alert_id: Alert ID in database
        ticker: Stock ticker symbol

    Returns:
        InlineKeyboardMarkup with alert action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("📊 Analyze", callback_data=f"analyze_{ticker}"),
            InlineKeyboardButton("📈 Chart", callback_data=f"chart_{ticker}"),
        ],
        [
            InlineKeyboardButton("✅ Mark Reviewed", callback_data=f"alert_reviewed_{alert_id}"),
            InlineKeyboardButton("❌ Dismiss", callback_data=f"alert_dismiss_{alert_id}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== Task Management Keyboards ====================

def build_tasks_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for AVA task management.

    Returns:
        InlineKeyboardMarkup with task action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("📋 Active Tasks", callback_data="tasks_active"),
            InlineKeyboardButton("✅ Completed", callback_data="tasks_completed"),
        ],
        [
            InlineKeyboardButton("📊 Statistics", callback_data="tasks_stats"),
            InlineKeyboardButton("🔄 Refresh", callback_data="tasks_refresh"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_task_keyboard(task_id: int, task_status: str) -> InlineKeyboardMarkup:
    """
    Build inline keyboard for individual task.

    Args:
        task_id: Task ID in database
        task_status: Current task status

    Returns:
        InlineKeyboardMarkup with task action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("📄 View Details", callback_data=f"task_details_{task_id}"),
        ],
    ]

    if task_status == "in_progress":
        keyboard.append([
            InlineKeyboardButton("✅ Mark Complete", callback_data=f"task_complete_{task_id}"),
        ])

    keyboard.append([
        InlineKeyboardButton("🔙 Back to Tasks", callback_data="show_tasks"),
    ])

    return InlineKeyboardMarkup(keyboard)


# ==================== Settings & Help Keyboards ====================

def build_settings_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for bot settings.

    Returns:
        InlineKeyboardMarkup with settings buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("🔔 Notifications", callback_data="settings_notifications"),
            InlineKeyboardButton("⏰ Alerts", callback_data="settings_alerts"),
        ],
        [
            InlineKeyboardButton("🎯 Preferences", callback_data="settings_preferences"),
            InlineKeyboardButton("📊 Display", callback_data="settings_display"),
        ],
        [
            InlineKeyboardButton("📈 Rate Limits", callback_data="settings_rate_limits"),
            InlineKeyboardButton("ℹ️ About", callback_data="settings_about"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


def build_help_keyboard() -> InlineKeyboardMarkup:
    """
    Build inline keyboard for help menu.

    Returns:
        InlineKeyboardMarkup with help navigation buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("📚 Commands", callback_data="help_commands"),
            InlineKeyboardButton("🎯 Features", callback_data="help_features"),
        ],
        [
            InlineKeyboardButton("❓ FAQ", callback_data="help_faq"),
            InlineKeyboardButton("🐛 Report Issue", callback_data="help_report"),
        ],
        [
            InlineKeyboardButton("💬 Contact Support", url="https://t.me/your_support_channel"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== Pagination Keyboard ====================

def build_pagination_keyboard(
    current_page: int,
    total_pages: int,
    callback_prefix: str
) -> InlineKeyboardMarkup:
    """
    Build pagination keyboard for long lists.

    Args:
        current_page: Current page number (1-indexed)
        total_pages: Total number of pages
        callback_prefix: Prefix for callback data (e.g., "positions_page")

    Returns:
        InlineKeyboardMarkup with pagination buttons
    """
    keyboard = []

    # Navigation buttons
    nav_buttons = []

    if current_page > 1:
        nav_buttons.append(
            InlineKeyboardButton("⬅️ Previous", callback_data=f"{callback_prefix}_{current_page - 1}")
        )

    nav_buttons.append(
        InlineKeyboardButton(f"📄 {current_page}/{total_pages}", callback_data="pagination_info")
    )

    if current_page < total_pages:
        nav_buttons.append(
            InlineKeyboardButton("Next ➡️", callback_data=f"{callback_prefix}_{current_page + 1}")
        )

    keyboard.append(nav_buttons)

    # Quick jump buttons (if more than 3 pages)
    if total_pages > 3:
        jump_buttons = [
            InlineKeyboardButton("⏮️ First", callback_data=f"{callback_prefix}_1"),
            InlineKeyboardButton("⏭️ Last", callback_data=f"{callback_prefix}_{total_pages}"),
        ]
        keyboard.append(jump_buttons)

    return InlineKeyboardMarkup(keyboard)


# ==================== Confirmation Keyboards ====================

def build_confirmation_keyboard(action: str, data: str = "") -> InlineKeyboardMarkup:
    """
    Build confirmation keyboard for destructive actions.

    Args:
        action: Action to confirm (e.g., "close_position", "delete_alert")
        data: Additional data to pass with confirmation

    Returns:
        InlineKeyboardMarkup with confirmation buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("✅ Confirm", callback_data=f"confirm_{action}_{data}"),
            InlineKeyboardButton("❌ Cancel", callback_data=f"cancel_{action}"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# ==================== Quick Action Keyboards ====================

def build_quick_actions_keyboard() -> InlineKeyboardMarkup:
    """
    Build quick actions keyboard for main menu.

    Returns:
        InlineKeyboardMarkup with quick action buttons
    """
    keyboard = [
        [
            InlineKeyboardButton("💼 Portfolio", callback_data="show_portfolio"),
            InlineKeyboardButton("📊 Positions", callback_data="show_positions"),
        ],
        [
            InlineKeyboardButton("🎯 Opportunities", callback_data="show_opportunities"),
            InlineKeyboardButton("📺 TradingView", callback_data="show_tradingview"),
        ],
        [
            InlineKeyboardButton("👥 Xtrades", callback_data="show_xtrades"),
            InlineKeyboardButton("📋 Tasks", callback_data="show_tasks"),
        ],
        [
            InlineKeyboardButton("⚙️ Settings", callback_data="show_settings"),
            InlineKeyboardButton("❓ Help", callback_data="show_help"),
        ],
    ]
    return InlineKeyboardMarkup(keyboard)


# Example usage
if __name__ == "__main__":
    print("AVA Inline Keyboards - Example Usage\n")

    print("1. Portfolio Keyboard:")
    keyboard = build_portfolio_keyboard()
    print(f"   Buttons: {len(keyboard.inline_keyboard)} rows")

    print("\n2. Stock Analysis Keyboard (NVDA):")
    keyboard = build_stock_analysis_keyboard("NVDA")
    print(f"   Buttons: {len(keyboard.inline_keyboard)} rows")

    print("\n3. Pagination Keyboard (page 3 of 10):")
    keyboard = build_pagination_keyboard(3, 10, "positions_page")
    print(f"   Buttons: {len(keyboard.inline_keyboard)} rows")

    print("\n4. Quick Actions Keyboard:")
    keyboard = build_quick_actions_keyboard()
    print(f"   Buttons: {len(keyboard.inline_keyboard)} rows")

    print("\n✅ All keyboard builders ready!")
