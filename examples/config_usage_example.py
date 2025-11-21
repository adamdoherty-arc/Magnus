"""
Configuration Manager Usage Examples

This file demonstrates how to use the ConfigManager to replace hardcoded values
in your dashboard pages and services.
"""

import streamlit as st
from src.config_manager import get_config, get_page_config, is_feature_enabled

# ============================================================================
# EXAMPLE 1: AI Options Agent Page
# ============================================================================

def ai_options_agent_page_with_config():
    """Example of using config manager in AI Options Agent page"""

    st.title("🤖 AI Options Agent")

    # Get page-specific configuration
    config = get_config()
    page_config = get_page_config("ai_options_agent")

    # BEFORE (Hardcoded):
    # min_dte = st.number_input("Min DTE", 1, 90, 20, 1)
    # max_dte = st.number_input("Max DTE", 1, 90, 40, 1)

    # AFTER (Using config):
    default_dte_range = page_config.get("default_dte_range", [20, 45])
    min_dte = st.number_input(
        "Min DTE",
        min_value=1,
        max_value=page_config.get("max_dte", 90),
        value=default_dte_range[0],
        step=1
    )
    max_dte = st.number_input(
        "Max DTE",
        min_value=1,
        max_value=page_config.get("max_dte", 90),
        value=default_dte_range[1],
        step=1
    )

    # BEFORE (Hardcoded):
    # min_delta = st.number_input("Min Delta", -0.50, -0.01, -0.45, 0.01)
    # max_delta = st.number_input("Max Delta", -0.50, -0.01, -0.15, 0.01)

    # AFTER (Using config):
    default_delta_range = page_config.get("default_delta_range", [-0.35, -0.25])
    min_delta = st.number_input(
        "Min Delta",
        min_value=page_config.get("min_delta", -0.50),
        max_value=page_config.get("max_delta", -0.01),
        value=default_delta_range[0],
        step=0.01
    )
    max_delta = st.number_input(
        "Max Delta",
        min_value=page_config.get("min_delta", -0.50),
        max_value=page_config.get("max_delta", -0.01),
        value=default_delta_range[1],
        step=0.01
    )

    # BEFORE (Hardcoded):
    # min_premium = st.number_input("Min Premium ($)", 0.0, 1000.0, 100.0, 10.0)

    # AFTER (Using config):
    min_premium = st.number_input(
        "Min Premium ($)",
        min_value=0.0,
        max_value=1000.0,
        value=page_config.get("default_min_premium", 100.0),
        step=10.0
    )

    # BEFORE (Hardcoded):
    # max_results = st.number_input("Max Results", 10, 1000, 200, 50)

    # AFTER (Using config):
    max_results = st.number_input(
        "Max Results",
        min_value=10,
        max_value=1000,
        value=page_config.get("max_results", 200),
        step=50
    )

    st.info(f"Using configuration from: pages.ai_options_agent")


# ============================================================================
# EXAMPLE 2: Positions Page
# ============================================================================

def positions_page_with_config():
    """Example of using config manager in Positions page"""

    st.title("💼 Active Positions")

    # Get page configuration
    page_config = get_page_config("positions_page")

    # BEFORE (Hardcoded):
    # auto_refresh = st.checkbox("🔄 Auto-Refresh", value=False)
    # refresh_freq = st.selectbox("Frequency", ["30s", "1m", "2m", "5m", "10m"], index=2)

    # AFTER (Using config):
    auto_refresh = st.checkbox(
        "🔄 Auto-Refresh",
        value=page_config.get("auto_refresh_default", False)
    )
    refresh_options = page_config.get("refresh_frequency_options", ["30s", "1m", "2m", "5m", "10m"])
    refresh_freq = st.selectbox("Frequency", refresh_options, index=2)

    # Auto-refresh logic using configured interval
    if auto_refresh:
        # BEFORE (Hardcoded):
        # freq_map = {"30s": 30, "1m": 60, "2m": 120, "5m": 300, "10m": 600}

        # AFTER (Using config):
        refresh_interval = page_config.get("refresh_interval", 300)
        st.markdown(
            f'<meta http-equiv="refresh" content="{refresh_interval}">',
            unsafe_allow_html=True
        )


# ============================================================================
# EXAMPLE 3: Feature Flags
# ============================================================================

def feature_flag_example():
    """Example of using feature flags"""

    st.title("Feature Flag Examples")

    # BEFORE (Hardcoded or manual checks):
    # if some_condition:
    #     display_ai_reasoning()

    # AFTER (Using feature flags):
    if is_feature_enabled("enable_ai_reasoning"):
        st.checkbox("🤖 Use LLM Reasoning", value=True)
    else:
        st.info("AI Reasoning feature is disabled in configuration")

    # Check multiple features
    features_to_check = [
        ("enable_calendar_spreads", "Calendar Spreads"),
        ("enable_recovery_strategies", "Recovery Strategies"),
        ("enable_theta_forecasts", "Theta Forecasts"),
        ("enable_auto_trading", "Auto Trading (Safety)"),
    ]

    st.markdown("### Available Features:")
    for feature_key, feature_name in features_to_check:
        enabled = is_feature_enabled(feature_key)
        status = "✅ Enabled" if enabled else "❌ Disabled"
        st.write(f"{feature_name}: {status}")


# ============================================================================
# EXAMPLE 4: Service Configuration
# ============================================================================

def robinhood_service_with_config():
    """Example of using config manager in Robinhood service"""

    from src.config_manager import get_service_config

    # Get service configuration
    rh_config = get_service_config("robinhood")

    # BEFORE (Hardcoded):
    # rate_limit = 60  # requests per minute
    # timeout = 30
    # retry_attempts = 3

    # AFTER (Using config):
    rate_limit = rh_config.get("rate_limit", 60)
    timeout = rh_config.get("timeout", 30)
    retry_attempts = rh_config.get("retry_attempts", 3)
    retry_delay = rh_config.get("retry_delay", 2)

    st.info(f"""
    Robinhood Service Configuration:
    - Rate Limit: {rate_limit} requests/min
    - Timeout: {timeout}s
    - Retry Attempts: {retry_attempts}
    - Retry Delay: {retry_delay}s
    """)


# ============================================================================
# EXAMPLE 5: LLM Provider Configuration
# ============================================================================

def llm_provider_with_config():
    """Example of using config manager for LLM providers"""

    config = get_config()

    # Get LLM provider configurations
    claude_config = config.get_llm_provider_config("claude")
    deepseek_config = config.get_llm_provider_config("deepseek")

    st.markdown("### LLM Provider Configuration")

    # BEFORE (Hardcoded):
    # model = "claude-sonnet-4-5"
    # max_tokens = 4000
    # temperature = 0.7

    # AFTER (Using config):
    st.write(f"**Claude:**")
    st.write(f"- Model: {claude_config.get('model')}")
    st.write(f"- Max Tokens: {claude_config.get('max_tokens')}")
    st.write(f"- Temperature: {claude_config.get('temperature')}")

    st.write(f"\n**DeepSeek:**")
    st.write(f"- Model: {deepseek_config.get('model')}")
    st.write(f"- Max Tokens: {deepseek_config.get('max_tokens')}")
    st.write(f"- Temperature: {deepseek_config.get('temperature')}")


# ============================================================================
# EXAMPLE 6: Cache TTL Configuration
# ============================================================================

def cache_with_config():
    """Example of using config manager for cache TTL"""

    from src.config_manager import get_cache_ttl

    # BEFORE (Hardcoded):
    # cache_ttl = 300  # 5 minutes

    # AFTER (Using config with semantic names):
    short_cache = get_cache_ttl("short")      # 1 minute
    default_cache = get_cache_ttl("default")  # 5 minutes
    medium_cache = get_cache_ttl("medium")    # 15 minutes
    long_cache = get_cache_ttl("long")        # 1 hour

    st.markdown("### Cache Configuration")
    st.write(f"- Short TTL: {short_cache}s (for frequently changing data)")
    st.write(f"- Default TTL: {default_cache}s (general purpose)")
    st.write(f"- Medium TTL: {medium_cache}s (moderately stable data)")
    st.write(f"- Long TTL: {long_cache}s (stable data)")


# ============================================================================
# EXAMPLE 7: Environment Variable Overrides
# ============================================================================

def environment_override_example():
    """Example demonstrating environment variable overrides"""

    config = get_config()

    st.markdown("### Environment Variable Overrides")

    st.code("""
    # You can override any config value using environment variables
    # Pattern: MAGNUS_SECTION_KEY

    # Override database pool size
    export MAGNUS_DATABASE_POOL_MAX=20

    # Override cache TTL
    export MAGNUS_CACHE_DEFAULT_TTL=600

    # Override page settings
    export MAGNUS_PAGES_AI_OPTIONS_AGENT_MAX_RESULTS=500

    # Override feature flags
    export MAGNUS_FEATURES_ENABLE_AI_REASONING=true
    """, language="bash")

    st.info("""
    Environment variables are applied at startup and override YAML config values.
    This is useful for:
    - Production vs development settings
    - Docker deployments
    - CI/CD pipelines
    - Quick testing without editing files
    """)


# ============================================================================
# EXAMPLE 8: Hot Reload
# ============================================================================

def hot_reload_example():
    """Example of hot-reloading configuration"""

    config = get_config()

    st.markdown("### Configuration Hot Reload")

    if st.button("🔄 Reload Configuration"):
        reloaded = config.reload_config()
        if reloaded:
            st.success("✅ Configuration reloaded from files")
        else:
            st.info("ℹ️ No changes detected in configuration files")

    st.info("""
    Hot reload allows you to update configuration files without restarting the app.

    Use cases:
    - Testing different settings
    - Enabling/disabling features
    - Adjusting performance parameters
    - Emergency changes in production
    """)


# ============================================================================
# Main Example Page
# ============================================================================

def main():
    """Main example page"""

    st.set_page_config(
        page_title="Config Manager Examples",
        page_icon="⚙️",
        layout="wide"
    )

    st.title("⚙️ Configuration Manager Examples")

    st.markdown("""
    This page demonstrates how to use the ConfigManager to replace hardcoded values
    throughout the Magnus Trading Dashboard.
    """)

    # Tabs for different examples
    tabs = st.tabs([
        "AI Agent",
        "Positions",
        "Features",
        "Services",
        "LLM",
        "Cache",
        "Env Vars",
        "Hot Reload"
    ])

    with tabs[0]:
        ai_options_agent_page_with_config()

    with tabs[1]:
        positions_page_with_config()

    with tabs[2]:
        feature_flag_example()

    with tabs[3]:
        robinhood_service_with_config()

    with tabs[4]:
        llm_provider_with_config()

    with tabs[5]:
        cache_with_config()

    with tabs[6]:
        environment_override_example()

    with tabs[7]:
        hot_reload_example()


if __name__ == "__main__":
    main()
