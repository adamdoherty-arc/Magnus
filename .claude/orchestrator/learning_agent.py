"""
Learning Agent - Learns from Existing Codebase
Analyzes existing code to generate specs, understand patterns, and build knowledge
Version: 1.0
"""
import os
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class LearningAgent:
    """
    Learns from existing codebase to:
    1. Generate spec files from existing code
    2. Understand coding patterns
    3. Extract business logic
    4. Build knowledge base
    """

    def __init__(self, project_root: str = "c:/code/Magnus"):
        self.project_root = Path(project_root)
        self.specs_dir = self.project_root / ".claude" / "specs"
        self.knowledge_base = {}

    def learn_from_codebase(self) -> Dict[str, Any]:
        """
        Main learning function - analyzes entire codebase

        Returns:
            Learning summary with insights
        """
        logger.info("Starting codebase learning...")

        summary = {
            "timestamp": datetime.now().isoformat(),
            "pages_analyzed": 0,
            "specs_generated": 0,
            "patterns_discovered": [],
            "insights": []
        }

        # Find all page files
        page_files = list(self.project_root.glob("*_page.py"))
        page_files.extend(list(self.project_root.glob("dashboard.py")))

        logger.info(f"Found {len(page_files)} page files to analyze")

        for page_file in page_files:
            try:
                insights = self.analyze_page(page_file)
                summary["pages_analyzed"] += 1

                # Generate spec if it doesn't exist
                if insights.get("should_generate_spec"):
                    self.generate_spec_from_code(page_file, insights)
                    summary["specs_generated"] += 1

            except Exception as e:
                logger.error(f"Error analyzing {page_file.name}: {e}")

        # Discover patterns across codebase
        summary["patterns_discovered"] = self.discover_patterns()

        # Generate insights
        summary["insights"] = self.generate_insights()

        return summary

    def analyze_page(self, page_file: Path) -> Dict[str, Any]:
        """
        Analyze a single page file to understand its purpose and structure

        Args:
            page_file: Path to page file

        Returns:
            Analysis results
        """
        logger.info(f"Analyzing: {page_file.name}")

        with open(page_file, 'r', encoding='utf-8') as f:
            content = f.read()

        insights = {
            "file": str(page_file),
            "name": page_file.stem,
            "features": [],
            "components": [],
            "api_calls": [],
            "database_queries": [],
            "ui_elements": [],
            "business_logic": [],
            "dependencies": [],
            "should_generate_spec": False
        }

        # Extract features from docstrings
        docstring = self._extract_docstring(content)
        if docstring:
            insights["description"] = docstring
            insights["features"].extend(self._extract_features_from_text(docstring))

        # Identify UI components
        insights["ui_elements"] = self._identify_ui_elements(content)

        # Identify API calls
        insights["api_calls"] = self._identify_api_calls(content)

        # Identify database queries
        insights["database_queries"] = self._identify_database_queries(content)

        # Identify business logic patterns
        insights["business_logic"] = self._identify_business_logic(content)

        # Extract dependencies (imports)
        insights["dependencies"] = self._extract_dependencies(content)

        # Determine if spec should be generated
        spec_file = self._get_spec_file(page_file)
        if not spec_file.exists():
            insights["should_generate_spec"] = True
            logger.info(f"  → Spec missing for {page_file.name}, will generate")

        return insights

    def _extract_docstring(self, content: str) -> Optional[str]:
        """Extract module-level docstring"""
        # Match triple-quoted strings at start of file
        match = re.search(r'^"""(.*?)"""', content, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip()

        match = re.search(r"^'''(.*?)'''", content, re.MULTILINE | re.DOTALL)
        if match:
            return match.group(1).strip()

        return None

    def _extract_features_from_text(self, text: str) -> List[str]:
        """Extract feature keywords from text"""
        features = []

        # Look for common feature indicators
        feature_keywords = [
            'positions', 'options', 'premium', 'scanner', 'calendar', 'spread',
            'earnings', 'sports', 'betting', 'prediction', 'xtrades', 'discord',
            'ava', 'chatbot', 'rag', 'dashboard', 'supply', 'demand', 'sector',
            'health', 'monitoring'
        ]

        text_lower = text.lower()
        for keyword in feature_keywords:
            if keyword in text_lower:
                features.append(keyword)

        return features

    def _identify_ui_elements(self, content: str) -> List[Dict[str, Any]]:
        """Identify Streamlit UI elements used"""
        ui_elements = []

        # Common Streamlit components
        patterns = {
            'header': r'st\.markdown\(["\']#{1,3}\s+(.+?)["\']',
            'metric': r'st\.metric\(',
            'chart': r'st\.(line_chart|bar_chart|area_chart|plotly_chart)',
            'dataframe': r'st\.dataframe\(',
            'selectbox': r'st\.selectbox\(',
            'multiselect': r'st\.multiselect\(',
            'slider': r'st\.slider\(',
            'button': r'st\.button\(',
            'tabs': r'st\.tabs\(',
            'expander': r'st\.expander\(',
            'columns': r'st\.columns\('
        }

        for element_type, pattern in patterns.items():
            matches = re.findall(pattern, content)
            if matches:
                ui_elements.append({
                    "type": element_type,
                    "count": len(matches)
                })

        return ui_elements

    def _identify_api_calls(self, content: str) -> List[str]:
        """Identify external API calls"""
        api_calls = []

        # Robinhood API patterns
        if 'rh.' in content or 'robinhood' in content.lower():
            api_calls.append("Robinhood API")

        # ESPN API
        if 'espn' in content.lower():
            api_calls.append("ESPN API")

        # Kalshi API
        if 'kalshi' in content.lower():
            api_calls.append("Kalshi API")

        # XTrades
        if 'xtrades' in content.lower():
            api_calls.append("XTrades API")

        # Discord
        if 'discord' in content.lower():
            api_calls.append("Discord API")

        return api_calls

    def _identify_database_queries(self, content: str) -> List[str]:
        """Identify database query patterns"""
        queries = []

        # SQL patterns
        if 'SELECT' in content or 'INSERT' in content or 'UPDATE' in content:
            queries.append("Direct SQL")

        # Database manager patterns
        if 'db_manager' in content or 'DatabaseManager' in content:
            queries.append("Database Manager")

        # Specific table access patterns
        table_patterns = [
            'options_data', 'positions', 'trades', 'game_cards',
            'kalshi_markets', 'discord_messages', 'xtrades_alerts'
        ]

        for table in table_patterns:
            if table in content:
                queries.append(f"Table: {table}")

        return queries

    def _identify_business_logic(self, content: str) -> List[str]:
        """Identify key business logic patterns"""
        logic = []

        # Options trading logic
        if 'delta' in content.lower() or 'theta' in content.lower() or 'greeks' in content.lower():
            logic.append("Options Greeks calculation")

        # P/L calculation
        if 'profit' in content.lower() or 'loss' in content.lower() or 'p_l' in content or 'pnl' in content.lower():
            logic.append("P/L calculation")

        # Calendar spread logic
        if 'spread' in content.lower() and ('calendar' in content.lower() or 'diagonal' in content.lower()):
            logic.append("Calendar spread analysis")

        # Earnings logic
        if 'earnings' in content.lower():
            logic.append("Earnings analysis")

        # Sports betting logic
        if 'odds' in content.lower() or 'betting' in content.lower():
            logic.append("Sports betting analysis")

        # AI/ML logic
        if 'predict' in content.lower() or 'model' in content.lower() or 'llm' in content.lower():
            logic.append("AI/ML predictions")

        return logic

    def _extract_dependencies(self, content: str) -> List[str]:
        """Extract import dependencies"""
        dependencies = []

        # Find all import statements
        import_pattern = r'^(?:from\s+(\S+)\s+import|import\s+(\S+))'
        matches = re.findall(import_pattern, content, re.MULTILINE)

        for match in matches:
            module = match[0] or match[1]
            if module and not module.startswith('.'):
                dependencies.append(module.split('.')[0])

        return list(set(dependencies))

    def _get_spec_file(self, page_file: Path) -> Path:
        """Get the corresponding spec file for a page"""
        # Map page file to feature name
        page_name = page_file.stem

        # Remove _page suffix
        if page_name.endswith('_page'):
            feature_name = page_name[:-5]
        elif page_name == 'dashboard':
            feature_name = 'dashboard'
        else:
            feature_name = page_name

        # Convert to kebab-case for directory name
        feature_dir = feature_name.replace('_', '-')

        spec_file = self.specs_dir / feature_dir / "requirements.md"
        return spec_file

    def generate_spec_from_code(self, page_file: Path, insights: Dict[str, Any]) -> bool:
        """
        Generate a requirements spec from existing code

        Args:
            page_file: Path to page file
            insights: Analysis insights from analyze_page()

        Returns:
            True if spec was generated
        """
        page_name = page_file.stem
        if page_name.endswith('_page'):
            feature_name = page_name[:-5].replace('_', '-')
        else:
            feature_name = page_name.replace('_', '-')

        feature_dir = self.specs_dir / feature_name
        feature_dir.mkdir(parents=True, exist_ok=True)

        requirements_file = feature_dir / "requirements.md"

        logger.info(f"Generating spec for {feature_name}...")

        # Generate requirements from code analysis
        requirements_content = self._generate_requirements_content(
            feature_name, page_file, insights
        )

        with open(requirements_file, 'w', encoding='utf-8') as f:
            f.write(requirements_content)

        logger.info(f"  ✓ Generated: {requirements_file}")

        return True

    def _generate_requirements_content(self, feature_name: str,
                                      page_file: Path, insights: Dict[str, Any]) -> str:
        """Generate requirements.md content from code analysis"""

        description = insights.get("description", f"{feature_name.replace('-', ' ').title()} feature")

        # Build user stories from insights
        user_stories = self._build_user_stories(insights)

        # Build functional requirements
        functional_reqs = self._build_functional_requirements(insights)

        # Build technical requirements
        technical_reqs = self._build_technical_requirements(insights)

        content = f"""# Requirements: {feature_name.replace('-', ' ').title()}

**Feature ID:** {feature_name}
**Status:** Reverse-Engineered from Existing Code
**Last Updated:** {datetime.now().strftime('%Y-%m-%d')}
**Source File:** {page_file.name}

---

## Overview

### Purpose
{description}

### Business Value
[AUTO-GENERATED] This feature is currently in production and provides value by:
- Enabling users to {feature_name.replace('-', ' ')}
- Providing insights through data visualization
- Supporting trading/betting decisions

### Success Metrics
- User engagement with {feature_name} page
- Data accuracy and reliability
- Page load performance < 3 seconds

---

## User Stories

{user_stories}

---

## Functional Requirements

{functional_reqs}

---

## Technical Requirements

{technical_reqs}

### Dependencies
{self._format_dependencies(insights.get('dependencies', []))}

### API Integrations
{self._format_api_calls(insights.get('api_calls', []))}

### Database Access
{self._format_database_queries(insights.get('database_queries', []))}

---

## UI Components

{self._format_ui_elements(insights.get('ui_elements', []))}

---

## Business Logic

{self._format_business_logic(insights.get('business_logic', []))}

---

## Notes

**This spec was automatically generated by analyzing existing code.**

To improve this spec:
1. Review and update the purpose and business value
2. Add specific acceptance criteria
3. Define success metrics
4. Add non-functional requirements
5. Document any assumptions

**Next Steps:**
1. Review this auto-generated spec
2. Fill in missing details
3. Add acceptance criteria
4. Generate design.md and tasks.md

---

## Change Log

| Date | Version | Change | Author |
|------|---------|--------|--------|
| {datetime.now().strftime('%Y-%m-%d')} | 1.0 | Auto-generated from existing code | LearningAgent |
"""

        return content

    def _build_user_stories(self, insights: Dict[str, Any]) -> str:
        """Build user stories from insights"""
        stories = []

        # Base story from UI elements
        if insights.get('ui_elements'):
            stories.append("""**US-1: View Data**
- **As a** trader
- **I want** to view the data on this page
- **So that** I can make informed decisions
- **Acceptance Criteria:**
  - Page loads successfully
  - Data is displayed accurately
  - Filters work correctly (if applicable)""")

        # API-specific story
        if insights.get('api_calls'):
            apis = ', '.join(insights['api_calls'])
            stories.append(f"""
**US-2: Access Live Data**
- **As a** trader
- **I want** to see live data from {apis}
- **So that** I can make timely decisions
- **Acceptance Criteria:**
  - Data refreshes automatically
  - API calls are rate-limited
  - Errors are handled gracefully""")

        if not stories:
            stories.append("""**US-1: Primary Feature**
- **As a** user
- **I want** to use this feature
- **So that** I can achieve my goal
- **Acceptance Criteria:**
  - [To be defined based on code review]""")

        return '\n'.join(stories)

    def _build_functional_requirements(self, insights: Dict[str, Any]) -> str:
        """Build functional requirements from insights"""
        reqs = []

        # Data display requirement
        reqs.append("""**FR-1: Data Display**
- **Description:** Display data to users in a clear, organized format
- **Priority:** Critical
- **Acceptance Criteria:**
  - All data fields are visible
  - Data is formatted correctly
  - No horizontal lines used (per UI guidelines)""")

        # Filtering requirement (if selectbox/multiselect detected)
        ui_types = [e['type'] for e in insights.get('ui_elements', [])]
        if 'selectbox' in ui_types or 'multiselect' in ui_types:
            reqs.append("""
**FR-2: Data Filtering**
- **Description:** Allow users to filter data based on criteria
- **Priority:** High
- **Acceptance Criteria:**
  - Filters update data in real-time
  - Multiple filters can be applied
  - Filter state is preserved""")

        # Chart requirement (if charts detected)
        chart_types = [e['type'] for e in insights.get('ui_elements', []) if 'chart' in e['type']]
        if chart_types:
            reqs.append("""
**FR-3: Data Visualization**
- **Description:** Provide visual charts/graphs for data analysis
- **Priority:** High
- **Acceptance Criteria:**
  - Charts render correctly
  - Charts are interactive (if applicable)
  - Charts update with filtered data""")

        return '\n'.join(reqs)

    def _build_technical_requirements(self, insights: Dict[str, Any]) -> str:
        """Build technical requirements from insights"""
        reqs = []

        # Performance requirement
        reqs.append("""**TR-1: Performance**
- Page load time: < 3 seconds
- API response time: < 500ms
- Support 10+ concurrent users""")

        # Data freshness (if API calls)
        if insights.get('api_calls'):
            reqs.append("""
**TR-2: Data Freshness**
- Live data updates every 30-60 seconds
- Cache where appropriate to reduce API calls
- Display last updated timestamp""")

        # Database performance
        if insights.get('database_queries'):
            reqs.append("""
**TR-3: Database Performance**
- Queries optimized with indexes
- Connection pooling enabled
- Query time < 100ms""")

        return '\n'.join(reqs)

    def _format_dependencies(self, deps: List[str]) -> str:
        """Format dependencies list"""
        if not deps:
            return "- None identified"
        return '\n'.join([f"- {dep}" for dep in sorted(set(deps))[:10]])

    def _format_api_calls(self, apis: List[str]) -> str:
        """Format API calls list"""
        if not apis:
            return "- No external APIs detected"
        return '\n'.join([f"- {api}" for api in apis])

    def _format_database_queries(self, queries: List[str]) -> str:
        """Format database queries list"""
        if not queries:
            return "- No database access detected"
        return '\n'.join([f"- {q}" for q in queries])

    def _format_ui_elements(self, elements: List[Dict[str, Any]]) -> str:
        """Format UI elements list"""
        if not elements:
            return "- No UI components detected"

        formatted = []
        for elem in elements:
            formatted.append(f"- **{elem['type'].title()}**: {elem['count']} instance(s)")

        return '\n'.join(formatted)

    def _format_business_logic(self, logic: List[str]) -> str:
        """Format business logic list"""
        if not logic:
            return "- No specific business logic patterns detected"
        return '\n'.join([f"- {l}" for l in logic])

    def discover_patterns(self) -> List[Dict[str, Any]]:
        """Discover common patterns across codebase"""
        patterns = []

        # This would analyze all code to find common patterns
        # For now, return placeholder
        patterns.append({
            "pattern": "Streamlit page structure",
            "description": "Standard page layout with headers, filters, and data display",
            "frequency": "common"
        })

        return patterns

    def generate_insights(self) -> List[str]:
        """Generate insights from learning"""
        insights = []

        # Count pages analyzed
        page_count = len(list(self.project_root.glob("*_page.py")))
        insights.append(f"Found {page_count} page files in the project")

        # Count specs that exist
        spec_count = len(list(self.specs_dir.glob("*/requirements.md")))
        insights.append(f"{spec_count}/{page_count} pages have requirement specs")

        return insights


def learn_from_codebase():
    """Main entry point for learning"""
    agent = LearningAgent()
    summary = agent.learn_from_codebase()

    print("=" * 80)
    print("LEARNING COMPLETE")
    print("=" * 80)
    print(f"\nPages analyzed: {summary['pages_analyzed']}")
    print(f"Specs generated: {summary['specs_generated']}")
    print(f"\nInsights:")
    for insight in summary['insights']:
        print(f"  - {insight}")

    if summary['specs_generated'] > 0:
        print(f"\n✓ Generated {summary['specs_generated']} new spec files!")
        print(f"  Location: .claude/specs/")
        print(f"\nNext steps:")
        print(f"  1. Review auto-generated specs")
        print(f"  2. Fill in missing details")
        print(f"  3. Add acceptance criteria")
        print(f"  4. Generate design.md and tasks.md")

    return summary


if __name__ == "__main__":
    learn_from_codebase()
