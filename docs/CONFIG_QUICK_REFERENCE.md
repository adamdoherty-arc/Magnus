# Configuration Manager - Quick Reference Card

## Import Statements

```python
# Main imports
from src.config_manager import get_config, get_page_config, is_feature_enabled
from src.config_manager import get_service_config, get_cache_ttl
```

---

## Common Operations

### 1. Get Basic Config Value
```python
config = get_config()
value = config.get("section.key", default_value)

# Examples
app_name = config.get("app.name")
pool_max = config.get("database.pool_max", 10)
```

### 2. Get Page Configuration
```python
page_config = get_page_config("page_name")

# Examples
ai_config = get_page_config("ai_options_agent")
default_dte = ai_config.get("default_dte_range", [20, 45])
```

### 3. Check Feature Flags
```python
if is_feature_enabled("feature_name"):
    # Feature is enabled

# Examples
if is_feature_enabled("enable_ai_reasoning"):
    show_ai_option()
```

### 4. Get Service Config
```python
service_config = get_service_config("service_name")

# Examples
rh_config = get_service_config("robinhood")
rate_limit = rh_config.get("rate_limit", 60)
```

### 5. Get LLM Provider Config
```python
config = get_config()
provider_config = config.get_llm_provider_config("provider_name")

# Examples
claude_config = config.get_llm_provider_config("claude")
model = claude_config.get("model")
```

### 6. Get Cache TTL
```python
ttl = get_cache_ttl("cache_type")

# Examples
short_ttl = get_cache_ttl("short")      # 1 minute
default_ttl = get_cache_ttl("default")  # 5 minutes
long_ttl = get_cache_ttl("long")        # 1 hour
```

### 7. Hot Reload
```python
config = get_config()
reloaded = config.reload_config()
```

---

## Configuration Files

```
config/
├── default.yaml     # App, database, cache, redis
├── pages.yaml       # Page-specific settings
├── features.yaml    # Feature flags
└── services.yaml    # External services, LLM providers
```

---

## Environment Variable Pattern

**Pattern**: `MAGNUS_SECTION_KEY`

```bash
# Override any config value
export MAGNUS_DATABASE_POOL_MAX=20
export MAGNUS_CACHE_DEFAULT_TTL=600
export MAGNUS_PAGES_AI_AGENT_MAX_RESULTS=500
export MAGNUS_FEATURES_ENABLE_DEBUG_MODE=true
```

---

## Migration Pattern

### Before (Hardcoded)
```python
max_results = 200
min_dte = 20
timeout = 30
```

### After (Using Config)
```python
from src.config_manager import get_page_config

page_config = get_page_config("my_page")
max_results = page_config.get("max_results", 200)
min_dte = page_config.get("min_dte", 20)
timeout = page_config.get("timeout", 30)
```

---

## Cache TTL Semantic Names

- `short` = 60s (1 minute) - Rapidly changing data
- `default` = 300s (5 minutes) - General purpose
- `medium` = 900s (15 minutes) - Moderately stable
- `long` = 3600s (1 hour) - Stable data
- `very_long` = 86400s (24 hours) - Rarely changing

---

## Common Config Paths

### App Settings
- `app.name`
- `app.version`
- `app.debug`

### Database
- `database.pool_max`
- `database.pool_min`
- `database.timeout`

### Cache
- `cache.default_ttl`
- `cache.short_ttl`
- `cache.long_ttl`

### Page Settings
- `pages.{page_name}.default_dte_range`
- `pages.{page_name}.max_results`
- `pages.{page_name}.refresh_interval`

### Features
- `features.enable_ai_reasoning`
- `features.enable_auto_trading`
- `features.enable_notifications`

### Services
- `services.robinhood.rate_limit`
- `services.robinhood.timeout`
- `services.llm.providers.claude.model`
- `services.llm.cache_ttl`

---

## Best Practices

1. ✅ **Always provide defaults**
   ```python
   value = config.get("key", default_value)
   ```

2. ✅ **Use semantic cache names**
   ```python
   ttl = get_cache_ttl("short")  # Not: ttl = 60
   ```

3. ✅ **Group related settings in YAML**
   ```yaml
   pages:
     my_page:
       setting1: value1
       setting2: value2
   ```

4. ✅ **Use feature flags for new features**
   ```python
   if is_feature_enabled("enable_new_feature"):
       render_feature()
   ```

5. ✅ **Document config values**
   ```yaml
   cache:
     default_ttl: 300  # 5 minutes - general purpose
   ```

---

## Validation

```python
config = get_config()
is_valid, errors = config.validate_config()

if not is_valid:
    for error in errors:
        print(f"Error: {error}")
```

---

## Testing

```bash
# Run config manager tests
python src/config_manager.py

# Find hardcoded values
python scripts/find_hardcoded_values.py

# Check migration report
cat CONFIG_MIGRATION_REPORT.md
```

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Config value is None | Check YAML file exists and key path is correct |
| Env var not working | Verify `MAGNUS_` prefix and restart app |
| Type mismatch | Check YAML syntax or use explicit conversion |
| Hot reload fails | Check file permissions and modification time |

---

## Examples

See complete examples in:
- `examples/config_usage_example.py`
- `docs/CONFIG_MIGRATION_GUIDE.md`

---

**Quick Start**:
1. Import: `from src.config_manager import get_config`
2. Get config: `config = get_config()`
3. Use it: `value = config.get("section.key", default)`

**Version**: 1.0 | **Last Updated**: 2025-01-07
