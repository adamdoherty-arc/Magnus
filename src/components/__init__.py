"""Magnus UI Components"""

# AI Research Widget
from .ai_research_widget import (
    display_ai_research_button,
    display_ai_research_analysis,
    display_ai_research_expander,
    display_consolidated_ai_research_section,
    generate_external_links,
    display_quick_links_section
)

# Metrics Card Component
from .metrics_card import (
    MetricsCard,
    render_metric,
    render_metric_row
)

# Data Table Component
from .data_table import (
    DataTable,
    render_table,
    render_pnl_table
)

# Expandable Card Component
from .expandable_card import (
    ExpandableCard,
    expandable_card,
    render_expandable_list
)

# Filter Panel Component
from .filter_panel import (
    FilterPanel,
    render_filters,
    apply_filters
)

__all__ = [
    # AI Research
    'display_ai_research_button',
    'display_ai_research_analysis',
    'display_ai_research_expander',
    'display_consolidated_ai_research_section',
    'generate_external_links',
    'display_quick_links_section',
    # Metrics Card
    'MetricsCard',
    'render_metric',
    'render_metric_row',
    # Data Table
    'DataTable',
    'render_table',
    'render_pnl_table',
    # Expandable Card
    'ExpandableCard',
    'expandable_card',
    'render_expandable_list',
    # Filter Panel
    'FilterPanel',
    'render_filters',
    'apply_filters'
]
