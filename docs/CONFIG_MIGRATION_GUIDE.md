# Configuration Management System - Migration Guide

## Table of Contents
1. [Overview](#overview)
2. [System Architecture](#system-architecture)
3. [Configuration Files](#configuration-files)
4. [Migration Steps](#migration-steps)
5. [Usage Examples](#usage-examples)
6. [Best Practices](#best-practices)
7. [Environment Variables](#environment-variables)
8. [Troubleshooting](#troubleshooting)

---

## Overview

The Configuration Management System eliminates hardcoded values across the Magnus Trading Dashboard by centralizing all configuration in YAML files. This provides:

- **Single Source of Truth**: All settings in one place
- **Environment Overrides**: Easy production vs development configuration
- **Hot Reload**: Update settings without restarting
- **Type Safety**: Validated configuration with sensible defaults
- **Maintainability**: No more hunting for hardcoded values

### Estimated Impact
- **~150-200** hardcoded values eliminated
- **~50-100** lines of code saved
- **5x** faster configuration changes
- **Significant** maintainability improvement

---

## System Architecture

```
config/
├── default.yaml      # App-wide settings (database, cache, redis)
├── pages.yaml        # Page-specific defaults and limits
├── features.yaml     # Feature flags for A/B testing
└── services.yaml     # External service configurations

src/
└── config_manager.py # Singleton config manager with hot reload

Usage:
  from src.config_manager import get_config, get_page_config, is_feature_enabled
```

### Key Features

1. **Singleton Pattern**: One instance shared across the application
2. **Thread-Safe**: Concurrent access with locking
3. **Environment Overrides**: `MAGNUS_SECTION_KEY` pattern
4. **Validation**: Schema validation for required fields
5. **Hot Reload**: Detect and reload changed config files

---

## Configuration Files

### 1. `config/default.yaml` - General Settings

**Purpose**: App-wide configuration for database, cache, and core services

```yaml
app:
  name: "Magnus - Wheel Strategy Dashboard"
  version: "2.0"
  debug: false

database:
  pool_min: 2
  pool_max: 10
  timeout: 30

cache:
  default_ttl: 300      # 5 minutes
  short_ttl: 60         # 1 minute
  medium_ttl: 900       # 15 minutes
  long_ttl: 3600        # 1 hour
```

**When to use**:
- Database connection settings
- Cache TTL values
- Redis configuration
- Session management

### 2. `config/pages.yaml` - Page-Specific Settings

**Purpose**: Default values, limits, and behavior for each dashboard page

```yaml
pages:
  ai_options_agent:
    default_dte_range: [20, 45]
    default_delta_range: [-0.35, -0.25]
    default_min_premium: 100.0
    max_results: 200

  positions_page:
    refresh_interval: 300
    auto_refresh_default: false
    show_closed_positions: true
```

**When to use**:
- Input field defaults
- Display limits
- Page-specific behavior
- User preference defaults

### 3. `config/features.yaml` - Feature Flags

**Purpose**: Enable/disable features for gradual rollouts and A/B testing

```yaml
features:
  enable_ai_reasoning: true
  enable_multi_model_consensus: true
  enable_auto_trading: false  # Safety feature
  enable_notifications: false
```

**When to use**:
- Feature rollouts
- A/B testing
- Safety switches
- Experimental features

### 4. `config/services.yaml` - External Services

**Purpose**: Configuration for external APIs and integrations

```yaml
services:
  robinhood:
    rate_limit: 60  # requests per minute
    timeout: 30
    retry_attempts: 3

  llm:
    providers:
      claude:
        model: "claude-sonnet-4-5"
        max_tokens: 4000
        temperature: 0.7
```

**When to use**:
- API settings
- Rate limits
- Timeouts and retries
- LLM provider settings

---

## Migration Steps

### Step 1: Identify Hardcoded Values

Run the migration helper script:

```bash
python scripts/find_hardcoded_values.py
```

This generates `CONFIG_MIGRATION_REPORT.md` with all findings.

### Step 2: Add Values to Config Files

Review the report and add values to appropriate config files:

```yaml
# Example: Adding AI Options Agent settings to config/pages.yaml

pages:
  ai_options_agent:
    default_dte_range: [20, 45]    # From hardcoded value
    default_delta_range: [-0.35, -0.25]  # From hardcoded value
    max_results: 200                # From hardcoded value
```

### Step 3: Replace Hardcoded Values

**Before:**
```python
def ai_options_agent_page():
    min_dte = st.number_input("Min DTE", 1, 90, 20, 1)  # 20 is hardcoded
    max_dte = st.number_input("Max DTE", 1, 90, 40, 1)  # 40 is hardcoded
    max_results = st.number_input("Max Results", 10, 1000, 200, 50)  # 200 is hardcoded
```

**After:**
```python
from src.config_manager import get_page_config

def ai_options_agent_page():
    page_config = get_page_config("ai_options_agent")
    default_dte_range = page_config.get("default_dte_range", [20, 45])

    min_dte = st.number_input("Min DTE", 1, 90, default_dte_range[0], 1)
    max_dte = st.number_input("Max DTE", 1, 90, default_dte_range[1], 1)
    max_results = st.number_input(
        "Max Results",
        10,
        1000,
        page_config.get("max_results", 200),
        50
    )
```

### Step 4: Test Each Change

1. **Unit Test**: Verify config values are retrieved correctly
2. **Integration Test**: Ensure page behaves identically
3. **Edge Cases**: Test with missing config (should use defaults)

### Step 5: Add Environment Overrides

For production/development differences:

```bash
# .env or environment
export MAGNUS_PAGES_AI_OPTIONS_AGENT_MAX_RESULTS=500
export MAGNUS_CACHE_DEFAULT_TTL=600
export MAGNUS_FEATURES_ENABLE_DEBUG_MODE=false
```

---

## Usage Examples

### Example 1: Basic Configuration Access

```python
from src.config_manager import get_config

config = get_config()

# Access with dot notation
app_name = config.get("app.name")
pool_max = config.get("database.pool_max", 10)  # with default

# Access nested values
claude_model = config.get("services.llm.providers.claude.model")
```

### Example 2: Page Configuration

```python
from src.config_manager import get_page_config

def my_dashboard_page():
    page_config = get_page_config("positions_page")

    # Get page-specific settings
    refresh_interval = page_config.get("refresh_interval", 300)
    show_closed = page_config.get("show_closed_positions", True)

    # Use in UI
    auto_refresh = st.checkbox(
        "Auto Refresh",
        value=page_config.get("auto_refresh_default", False)
    )
```

### Example 3: Feature Flags

```python
from src.config_manager import is_feature_enabled

def render_features():
    # Check if feature is enabled
    if is_feature_enabled("enable_ai_reasoning"):
        display_ai_reasoning_option()

    if is_feature_enabled("enable_calendar_spreads"):
        display_calendar_spreads_tab()

    # Safety check
    if is_feature_enabled("enable_auto_trading"):
        st.warning("⚠️ Auto-trading is enabled")
```

### Example 4: Service Configuration

```python
from src.config_manager import get_service_config

class RobinhoodService:
    def __init__(self):
        service_config = get_service_config("robinhood")

        self.rate_limit = service_config.get("rate_limit", 60)
        self.timeout = service_config.get("timeout", 30)
        self.retry_attempts = service_config.get("retry_attempts", 3)
        self.retry_delay = service_config.get("retry_delay", 2)
```

### Example 5: LLM Provider Configuration

```python
from src.config_manager import get_config

config = get_config()

# Get provider-specific config
claude_config = config.get_llm_provider_config("claude")

llm_client = create_llm_client(
    model=claude_config.get("model"),
    max_tokens=claude_config.get("max_tokens"),
    temperature=claude_config.get("temperature")
)
```

### Example 6: Cache TTL

```python
from src.config_manager import get_cache_ttl

# Use semantic cache names
stock_prices_ttl = get_cache_ttl("short")      # 1 minute
options_data_ttl = get_cache_ttl("medium")     # 15 minutes
company_info_ttl = get_cache_ttl("long")       # 1 hour

# Set in Redis
redis_client.setex(key, stock_prices_ttl, value)
```

### Example 7: Hot Reload

```python
from src.config_manager import get_config

config = get_config()

# In admin panel or on-demand
if st.button("Reload Configuration"):
    reloaded = config.reload_config()
    if reloaded:
        st.success("Configuration reloaded!")
    else:
        st.info("No changes detected")
```

---

## Best Practices

### 1. Always Provide Defaults

```python
# Good
max_results = config.get("pages.my_page.max_results", 200)

# Bad
max_results = config.get("pages.my_page.max_results")  # Could be None
```

### 2. Use Semantic Names

```python
# Good
cache_ttl = get_cache_ttl("short")  # Clear intent

# Bad
cache_ttl = 60  # Magic number
```

### 3. Group Related Settings

```yaml
# Good
pages:
  ai_agent:
    default_dte_range: [20, 45]
    default_delta_range: [-0.35, -0.25]
    max_results: 200

# Bad (flat structure)
ai_agent_default_dte_min: 20
ai_agent_default_dte_max: 45
```

### 4. Use Feature Flags for New Features

```python
# When adding a new feature
if is_feature_enabled("enable_new_feature"):
    render_new_feature()
else:
    st.info("Feature coming soon!")
```

### 5. Document Configuration Values

```yaml
# Good
cache:
  default_ttl: 300  # 5 minutes - general purpose caching
  short_ttl: 60     # 1 minute - rapidly changing data

# Bad (no context)
cache:
  default_ttl: 300
  short_ttl: 60
```

---

## Environment Variables

### Override Pattern

Environment variables follow the pattern: `MAGNUS_SECTION_KEY`

**Examples:**

```bash
# Override database settings
export MAGNUS_DATABASE_POOL_MAX=20
export MAGNUS_DATABASE_TIMEOUT=60

# Override cache TTL
export MAGNUS_CACHE_DEFAULT_TTL=600
export MAGNUS_CACHE_LONG_TTL=7200

# Override page settings
export MAGNUS_PAGES_AI_OPTIONS_AGENT_MAX_RESULTS=500
export MAGNUS_PAGES_POSITIONS_PAGE_REFRESH_INTERVAL=600

# Override feature flags
export MAGNUS_FEATURES_ENABLE_AI_REASONING=true
export MAGNUS_FEATURES_ENABLE_AUTO_TRADING=false

# Override service settings
export MAGNUS_SERVICES_ROBINHOOD_RATE_LIMIT=30
export MAGNUS_SERVICES_LLM_CACHE_TTL=7200
```

### Type Conversion

The config manager automatically converts environment variable types:

- `true`, `yes`, `1` → Boolean `True`
- `false`, `no`, `0` → Boolean `False`
- Numbers with `.` → Float
- Numbers without `.` → Integer
- Everything else → String

### Docker Example

```dockerfile
# Dockerfile or docker-compose.yml
ENV MAGNUS_DATABASE_POOL_MAX=20
ENV MAGNUS_CACHE_DEFAULT_TTL=600
ENV MAGNUS_FEATURES_ENABLE_DEBUG_MODE=false
```

---

## Troubleshooting

### Issue 1: Config Value Not Found

**Symptom**: `get()` returns `None` or default value

**Solutions**:
1. Check YAML file exists in `config/` directory
2. Verify key path is correct: `section.subsection.key`
3. Check for typos in key names
4. Run config validation: `config.validate_config()`

### Issue 2: Environment Override Not Working

**Symptom**: Environment variable set but config still uses YAML value

**Solutions**:
1. Verify environment variable naming: `MAGNUS_SECTION_KEY`
2. Restart the application (env vars loaded at startup)
3. Check for typos in env var name
4. Use uppercase for section and key names

### Issue 3: Type Mismatch

**Symptom**: Config value has wrong type (e.g., string instead of int)

**Solutions**:
1. Check YAML syntax (use proper types)
2. For env vars, ensure proper format (no quotes for numbers)
3. Use explicit type conversion: `int(config.get(...))`

### Issue 4: Hot Reload Not Working

**Symptom**: Changes to YAML files not reflected

**Solutions**:
1. Ensure you call `config.reload_config()`
2. Check file permissions (config files must be readable)
3. Verify file modification time is newer
4. Clear any file system caches

### Validation

Run validation to check configuration health:

```python
from src.config_manager import get_config

config = get_config()
is_valid, errors = config.validate_config()

if not is_valid:
    for error in errors:
        print(f"Config error: {error}")
```

---

## Migration Checklist

Use this checklist when migrating a page or component:

- [ ] Run `find_hardcoded_values.py` to identify values
- [ ] Add identified values to appropriate config file
- [ ] Import config manager in the file
- [ ] Replace hardcoded values with `config.get()` calls
- [ ] Provide sensible defaults for all `get()` calls
- [ ] Test page functionality (should behave identically)
- [ ] Test with missing config (defaults should work)
- [ ] Test with environment variable overrides
- [ ] Update documentation if needed
- [ ] Remove old comments about hardcoded values

---

## Lines of Code Saved

### Estimated Savings per Page

**Before (Hardcoded Values):**
```python
# ~20 lines of hardcoded values per page
refresh_interval = 300
max_results = 200
default_dte_min = 20
default_dte_max = 45
default_delta_min = -0.35
default_delta_max = -0.25
min_premium = 100.0
cache_ttl = 300
rate_limit = 60
timeout = 30
# ... and so on
```

**After (Configuration):**
```python
# ~2 lines per page
from src.config_manager import get_page_config
page_config = get_page_config("ai_options_agent")
```

**Savings**: ~18 lines per page × 10 pages = **~180 lines saved**

### Maintainability Benefits

- **5x faster** to change settings (edit YAML vs hunting through code)
- **Zero code changes** for environment-specific settings
- **Single source of truth** for all configuration
- **Type safety** and validation built-in

---

## Next Steps

1. **Phase 1**: Migrate dashboard.py and core pages (Week 1)
2. **Phase 2**: Migrate service integrations (Week 2)
3. **Phase 3**: Migrate remaining pages and utilities (Week 3)
4. **Phase 4**: Add comprehensive config validation and testing (Week 4)

---

## Support

For questions or issues:
1. Check this guide first
2. Review `examples/config_usage_example.py`
3. Run the test suite: `python src/config_manager.py`
4. Check the migration report: `CONFIG_MIGRATION_REPORT.md`

---

**Last Updated**: 2025-01-07
**Version**: 1.0
