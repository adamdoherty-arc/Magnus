# Page Registry System Guide

## Overview

The Page Registry provides a centralized, type-safe system for managing all pages in the Magnus Trading Platform. It replaces magic string routing with a structured registry that includes metadata, dependencies, and navigation support.

## Benefits

✅ **Type Safety** - No more magic strings, use page IDs from registry
✅ **Centralized Management** - All pages registered in one place
✅ **Rich Metadata** - Each page has description, keywords, dependencies
✅ **Navigation Support** - Automatic category-based navigation menus
✅ **Search** - Built-in search by name, description, or keywords
✅ **Validation** - Check if page requirements are met before loading

## Quick Start

### Getting the Registry

```python
from src.page_registry import get_registry

registry = get_registry()
```

### Get a Page

```python
# Get page metadata
page = registry.get_page("dashboard")

print(f"Name: {page.display_name}")
print(f"Icon: {page.icon}")
print(f"File: {page.file_path}")
print(f"Description: {page.description}")
```

### Get Pages by Category

```python
from src.page_registry import PageCategory

# Get all options trading pages
options_pages = registry.get_pages_by_category(PageCategory.OPTIONS)

for page in options_pages:
    print(f"{page.icon} {page.display_name}")
```

## Page Categories

Pages are organized into categories:

- `DASHBOARD` - Main dashboard and overview pages
- `TRADING` - Position management and trade execution
- `OPTIONS` - Options analysis and strategy tools
- `SPORTS_BETTING` - Sports betting and prediction markets
- `ANALYTICS` - Technical analysis and market research
- `AI_TOOLS` - AI assistants and automated tools
- `SYSTEM` - System management and configuration
- `ADMIN` - Administrative tools

## Page Metadata

Each page registration includes:

```python
@dataclass
class PageMetadata:
    page_id: str              # Unique ID (e.g., "dashboard")
    display_name: str         # Display name (e.g., "Dashboard")
    icon: str                 # Emoji icon
    category: PageCategory    # Category for grouping
    file_path: str            # Path to page file
    description: str          # Brief description
    keywords: List[str]       # Search keywords
    requires_auth: bool       # Authentication required?
    requires_setup: bool      # Setup needed?
    is_active: bool           # Currently active?
    sort_order: int           # Order within category
    show_in_nav: bool         # Show in navigation?
    required_env_vars: List[str]      # Required env variables
    required_services: List[str]      # Required services
```

## Registering a New Page

Add a new page to the registry in `src/page_registry.py`:

```python
def _initialize_pages(self):
    # ... existing registrations ...

    self.register(PageMetadata(
        page_id="my-new-page",
        display_name="My New Page",
        icon="🎯",
        category=PageCategory.TRADING,
        file_path="my_new_page.py",
        description="Description of what this page does",
        keywords=["keyword1", "keyword2", "keyword3"],
        requires_setup=True,  # If setup is needed
        required_env_vars=["API_KEY", "SECRET"],  # Required env vars
        sort_order=5  # Position in category (lower = first)
    ))
```

## Navigation

### Automatic Sidebar Navigation

The registry provides a helper to render navigation:

```python
from src.page_registry import render_sidebar_navigation

# In your main app
render_sidebar_navigation()
```

This automatically creates a categorized sidebar menu with all active pages.

### Custom Navigation

Build custom navigation using the registry:

```python
import streamlit as st
from src.page_registry import get_registry

registry = get_registry()

# Get navigation structure
structure = registry.get_navigation_structure()

# Render custom navigation
for category, pages in structure.items():
    st.sidebar.markdown(f"### {category.value.title()}")

    for page in pages:
        if st.sidebar.button(f"{page.icon} {page.display_name}"):
            # Navigate to page
            st.switch_page(page.file_path)
```

## Search

Search pages by name, description, or keywords:

```python
# Search for pages
results = registry.search_pages("options")

for page in results:
    st.write(f"{page.icon} {page.display_name}")
    st.caption(page.description)
```

## Validation

Check if a page's requirements are met:

```python
# Validate page setup
is_valid, missing = registry.validate_page_setup("positions")

if not is_valid:
    st.error("Missing requirements:")
    for item in missing:
        st.write(f"- {item}")
else:
    # Load the page
    st.success("All requirements met!")
```

## Common Patterns

### Page Switcher

Create a page switcher dropdown:

```python
import streamlit as st
from src.page_registry import get_registry

registry = get_registry()
pages = registry.get_nav_pages()

# Create dropdown
page_names = {f"{p.icon} {p.display_name}": p for p in pages}
selected = st.selectbox("Go to page:", list(page_names.keys()))

if selected:
    page = page_names[selected]
    st.switch_page(page.file_path)
```

### Category Navigation

Show pages grouped by category:

```python
import streamlit as st
from src.page_registry import get_registry, PageCategory

registry = get_registry()

# Let user select category
category = st.selectbox(
    "Select category:",
    [c.value for c in PageCategory]
)

# Show pages in category
category_enum = PageCategory(category)
pages = registry.get_pages_by_category(category_enum)

for page in pages:
    col1, col2, col3 = st.columns([1, 3, 8])
    with col1:
        st.write(page.icon)
    with col2:
        st.write(page.display_name)
    with col3:
        st.caption(page.description)
```

### Required Setup Indicator

Show which pages need setup:

```python
import streamlit as st
from src.page_registry import get_registry

registry = get_registry()
pages = registry.get_all_pages()

# Filter pages needing setup
needs_setup = [p for p in pages if p.requires_setup]

if needs_setup:
    st.warning(f"{len(needs_setup)} pages need setup:")
    for page in needs_setup:
        is_valid, missing = registry.validate_page_setup(page.page_id)

        if not is_valid:
            st.write(f"❌ {page.display_name}")
            for item in missing:
                st.caption(f"  - {item}")
        else:
            st.write(f"✅ {page.display_name}")
```

### Page URLs

Get URLs for pages:

```python
from src.page_registry import get_page_url

# Get URL for a page
url = get_page_url("dashboard")
st.markdown(f"[Go to Dashboard]({url})")
```

## Integration with UI Theme

Combine the page registry with the UI theme system:

```python
from src.ui_theme import init_page, UIComponents
from src.page_registry import get_registry

# Initialize page
theme = init_page("My Page", "📊", "wide")
components = UIComponents(theme)

# Get current page info
registry = get_registry()
current_page = registry.get_page("my-page-id")

# Show page info
st.title(f"{current_page.icon} {current_page.display_name}")
st.caption(current_page.description)

# Validate setup
is_valid, missing = registry.validate_page_setup(current_page.page_id)
if not is_valid:
    components.warning_box("This page requires additional setup")
    for item in missing:
        st.write(f"- {item}")
```

## Complete Example

Here's a complete example of a page using both systems:

```python
"""
Example Page with Registry Integration
"""
from src.ui_theme import init_page, UIComponents
from src.page_registry import get_registry
import streamlit as st

# Initialize theme
theme = init_page("Example Page", "🎯", "wide")
components = UIComponents(theme)

# Get page metadata
registry = get_registry()
page_info = registry.get_page("example-page")

# Validate setup
is_valid, missing = registry.validate_page_setup("example-page")

if not is_valid:
    # Show setup requirements
    components.error_box("Missing Requirements")
    for item in missing:
        st.write(f"- {item}")
    st.stop()

# Page header
st.title(f"{page_info.icon} {page_info.display_name}")
st.caption(page_info.description)

# Navigation breadcrumb
st.markdown(
    f"Home > {page_info.category.value.title()} > {page_info.display_name}"
)

# Main content
st.write("Page content goes here...")

# Related pages
st.sidebar.markdown("### Related Pages")
related = registry.get_pages_by_category(page_info.category)
for related_page in related:
    if related_page.page_id != page_info.page_id:
        if st.sidebar.button(
            f"{related_page.icon} {related_page.display_name}",
            key=f"nav_{related_page.page_id}"
        ):
            st.switch_page(related_page.file_path)
```

## Best Practices

1. **Always use page IDs** - Never hardcode page names or paths
2. **Validate requirements** - Check setup before rendering page content
3. **Update metadata** - Keep descriptions and keywords current
4. **Use categories** - Organize pages logically
5. **Set sort order** - Control display order within categories
6. **Add keywords** - Make pages searchable
7. **Document dependencies** - Specify required env vars and services

## Migration from Magic Strings

### Before (Magic Strings)

```python
# Old way - brittle and error-prone
if st.button("Go to Options"):
    st.switch_page("options_analysis_page.py")  # Magic string!

# Old navigation
PAGES = {
    "Dashboard": "dashboard.py",
    "Options": "options_analysis_page.py",
    "Positions": "positions_page_improved.py"
}
```

### After (Registry)

```python
# New way - type-safe and maintainable
from src.page_registry import get_registry

registry = get_registry()

if st.button("Go to Options"):
    page = registry.get_page("options-analysis")
    st.switch_page(page.file_path)

# New navigation
pages = registry.get_nav_pages()
for page in pages:
    if st.button(f"{page.icon} {page.display_name}"):
        st.switch_page(page.file_path)
```

## Testing

Test page registration:

```python
from src.page_registry import get_registry

def test_page_registry():
    registry = get_registry()

    # Test page exists
    page = registry.get_page("dashboard")
    assert page is not None
    assert page.display_name == "Dashboard"

    # Test search
    results = registry.search_pages("options")
    assert len(results) > 0

    # Test validation
    is_valid, missing = registry.validate_page_setup("dashboard")
    assert is_valid or len(missing) > 0

    print("✅ All tests passed")

if __name__ == "__main__":
    test_page_registry()
```

## Troubleshooting

### Page not found

```python
page = registry.get_page("my-page")
if page is None:
    print("Page not registered - check page_registry.py")
```

### Missing requirements

```python
is_valid, missing = registry.validate_page_setup("my-page")
if not is_valid:
    for requirement in missing:
        print(f"Missing: {requirement}")
```

### Navigation not working

Make sure pages have `show_in_nav=True` and `is_active=True`:

```python
pages = registry.get_nav_pages()
if not pages:
    print("No pages enabled for navigation")
```

## Future Enhancements

Planned features:
- Permission-based access control
- Usage analytics per page
- A/B testing support
- Dynamic page loading
- Page preloading for performance
- Lazy loading support

## Support

- See `src/page_registry.py` for complete code
- Review existing page registrations for examples
- Run `python -m src.page_registry` to see all registered pages
