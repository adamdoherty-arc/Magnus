# Magnus Configuration Directory

This directory contains all configuration files for the Magnus Wheel Strategy Dashboard.

## Files

### `default.yaml`
**General application settings**
- App metadata (name, version, debug mode)
- Database connection settings
- Cache TTL values
- Redis configuration
- Session management

### `pages.yaml`
**Page-specific configuration**
- Default values for each dashboard page
- Input field limits
- Display settings
- Refresh intervals
- Page-specific behavior

### `features.yaml`
**Feature flags**
- Enable/disable features
- A/B testing flags
- Safety switches
- Experimental features
- Integration toggles

### `services.yaml`
**External service configuration**
- API settings and endpoints
- Rate limits and timeouts
- Retry configurations
- LLM provider settings
- Integration parameters

## Usage

### In Python Code

```python
from src.config_manager import get_config, get_page_config, is_feature_enabled

# Get configuration instance
config = get_config()

# Access values with dot notation
app_name = config.get("app.name")
pool_max = config.get("database.pool_max", 10)

# Get page-specific config
page_config = get_page_config("ai_options_agent")
max_results = page_config.get("max_results", 200)

# Check feature flags
if is_feature_enabled("enable_ai_reasoning"):
    # Feature is enabled
    pass
```

## Environment Variable Overrides

You can override any configuration value using environment variables with the pattern:

```
MAGNUS_SECTION_KEY
```

**Examples:**

```bash
# Override database settings
export MAGNUS_DATABASE_POOL_MAX=20
export MAGNUS_DATABASE_TIMEOUT=60

# Override cache settings
export MAGNUS_CACHE_DEFAULT_TTL=600

# Override page settings
export MAGNUS_PAGES_AI_OPTIONS_AGENT_MAX_RESULTS=500

# Override feature flags
export MAGNUS_FEATURES_ENABLE_DEBUG_MODE=true
```

## Adding New Configuration

### Step 1: Choose the right file

- **General settings** → `default.yaml`
- **Page-specific** → `pages.yaml`
- **Feature flags** → `features.yaml`
- **External services** → `services.yaml`

### Step 2: Add the configuration

```yaml
# Example: Adding a new page configuration to pages.yaml
pages:
  my_new_page:
    default_value: 100
    max_results: 500
    refresh_interval: 300
```

### Step 3: Use in code

```python
from src.config_manager import get_page_config

page_config = get_page_config("my_new_page")
default_value = page_config.get("default_value", 100)
```

### Step 4: Document it

Add a comment explaining what the setting does:

```yaml
pages:
  my_new_page:
    default_value: 100  # Default calculation value
    max_results: 500    # Maximum results to display
```

## Configuration Guidelines

### DO:
✅ Use semantic names (e.g., `short_ttl` instead of `ttl_60`)
✅ Provide defaults in code: `config.get("key", default)`
✅ Group related settings together
✅ Document complex settings with comments
✅ Use appropriate types (int, float, bool, string)

### DON'T:
❌ Store API keys or secrets (use environment variables)
❌ Use magic numbers (add them to config instead)
❌ Create deeply nested structures (max 3 levels)
❌ Use abbreviations without comments
❌ Duplicate settings across files

## Hot Reload

Configuration changes are automatically detected on next access if files are modified. You can also force a reload:

```python
config = get_config()
config.reload_config()
```

## Validation

Test your configuration changes:

```python
config = get_config()
is_valid, errors = config.validate_config()

if not is_valid:
    for error in errors:
        print(f"Config error: {error}")
```

Or run the test script:

```bash
python src/config_manager.py
```

## Migration from Hardcoded Values

See the comprehensive migration guide:
- 📖 `docs/CONFIG_MIGRATION_GUIDE.md`
- 📋 `docs/CONFIG_QUICK_REFERENCE.md`

Run the migration helper to find hardcoded values:

```bash
python scripts/find_hardcoded_values.py
```

## Common Configuration Patterns

### Cache TTL
```python
from src.config_manager import get_cache_ttl

short_ttl = get_cache_ttl("short")      # 1 minute
default_ttl = get_cache_ttl("default")  # 5 minutes
long_ttl = get_cache_ttl("long")        # 1 hour
```

### Service Configuration
```python
from src.config_manager import get_service_config

rh_config = get_service_config("robinhood")
rate_limit = rh_config.get("rate_limit", 60)
```

### Feature Flags
```python
from src.config_manager import is_feature_enabled

if is_feature_enabled("enable_new_feature"):
    render_new_feature()
```

## Troubleshooting

### Config value is None
**Check:** YAML file exists and key path is correct
```bash
ls config/
# Verify file exists

# Check YAML syntax
python -c "import yaml; yaml.safe_load(open('config/default.yaml'))"
```

### Environment override not working
**Check:** Variable name and app restart
```bash
# Verify variable
echo $MAGNUS_DATABASE_POOL_MAX

# Restart the application
```

### Type mismatch
**Check:** YAML type syntax
```yaml
# Correct
value: 100      # Integer
value: 100.0    # Float
value: true     # Boolean
value: "text"   # String

# Incorrect
value: "100"    # String (should be 100)
```

## Documentation

- **Full Guide**: `docs/CONFIG_MIGRATION_GUIDE.md`
- **Quick Reference**: `docs/CONFIG_QUICK_REFERENCE.md`
- **Examples**: `examples/config_usage_example.py`
- **Implementation Report**: `CONFIG_SYSTEM_IMPLEMENTATION_REPORT.md`

## Support

For questions or issues:
1. Check this README
2. Review the migration guide
3. Run the test script
4. Check the examples file

---

**Last Updated**: 2025-01-07
**Version**: 1.0
