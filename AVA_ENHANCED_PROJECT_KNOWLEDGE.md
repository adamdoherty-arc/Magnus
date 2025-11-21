# AVA Enhanced Project Knowledge

**Date:** November 11, 2025
**Status:** COMPLETE - AVA Now Understands Magnus Project

---

## Executive Summary

AVA financial assistant has been enhanced with comprehensive knowledge about the Magnus project itself. AVA can now answer questions about features, explain how to use components, provide code references, and guide users through the system.

### New Capabilities ✅

1. **Feature Explanations** - AVA knows all 14 Magnus features and can explain each one
2. **Usage Guidance** - Step-by-step instructions for common tasks
3. **Code References** - Can locate files and functions related to queries
4. **Architecture Knowledge** - Understands database schemas, APIs, and integrations
5. **Intelligent Routing** - Automatically detects project questions vs. trading queries

---

## Implementation Summary

### 1. Magnus Project Knowledge Builder

**File:** `src/ava/magnus_project_knowledge.py` (450 lines)

**What It Does:**
- Catalogs all Magnus features with descriptions and capabilities
- Documents database schemas and purposes
- Maps API endpoints and integrations
- Provides common task workflows
- Describes AI/ML capabilities

**Output:**
- `MAGNUS_PROJECT_KNOWLEDGE.md` - Comprehensive project reference (auto-generated)
- RAG-indexed knowledge chunks for semantic search

**Features Cataloged:** 14 major features
```
1. Dashboard - Portfolio overview
2. Positions Page - Live Robinhood tracking
3. Opportunities Finder - CSP scanner
4. Premium Scanner - Options flow analysis
5. AI Options Agent - Position recommendations
6. Comprehensive Strategy - Multi-factor analysis
7. Database Scan - Market-wide scanning
8. XTrades Integration - Professional signals
9. Earnings Calendar - Event tracking
10. Calendar Spreads - AI spread analysis
11. Prediction Markets - Kalshi integration
12. Supply/Demand Zones - Technical levels
13. AVA Financial Assistant - Natural language interface
14. Task Management - Development tracking with QA
```

### 2. Enhanced Project Handler

**File:** `src/ava/enhanced_project_handler.py` (350 lines)

**What It Does:**
- Detects when user asks about Magnus project itself
- Retrieves relevant context from RAG knowledge base
- Generates comprehensive answers using LLM + context
- Provides source references and code locations
- Falls back to cached answers if LLM unavailable

**Key Methods:**
```python
# Detect project questions
is_project_question(user_text) -> bool

# Answer with RAG + LLM
answer_project_question(user_text) -> Dict

# Specific lookups
get_feature_info(feature_name) -> Dict
get_usage_guide(task) -> Dict
search_code(search_term) -> Dict

# Integration
integrate_with_ava(ava_handler) -> EnhancedHandler
```

### 3. Knowledge Base

**Magnus Project Knowledge Summary:**
- **14 Features** with detailed descriptions and capabilities
- **5 Core Integrations** (Robinhood, TradingView, XTrades, Kalshi, ChromaDB)
- **7 Database Schemas** with table listings
- **5 API Services** with endpoint documentation
- **5 Common Task Workflows** with step-by-step instructions
- **4 AI/ML Systems** (RAG, Agents, Recommendations, Predictions)

---

## How It Works

### Question Detection

AVA automatically detects project-related questions using keywords:

**Triggers:**
- "Magnus", "features", "capabilities", "how to"
- "What can", "where is", "show me", "explain"
- "Dashboard", "integrate", "use the", "access"
- "Database", "API", "function", "code", "file"
- "Page", "module", "system", "architecture"

### Answer Generation Flow

```
User Question
     ↓
Is Project Question?
     ↓ (yes)
Query RAG Knowledge Base
     ↓
Retrieve 5 most relevant context chunks
     ↓
Build LLM Prompt with Context
     ↓
Generate Answer
     ↓
Format with Sources & Code References
     ↓
Return to User
```

### Example Interactions

**Question:** "What features does Magnus have?"

**AVA Answer:**
```
Magnus is a comprehensive options trading dashboard with 14 major features:

1. Dashboard (dashboard.py) - Portfolio overview with balance forecast
2. Positions Page (positions_page_improved.py) - Live Robinhood tracking
3. Opportunities Finder (src/csp_opportunities_finder.py) - CSP scanning
4. Premium Scanner (premium_scanner_page.py) - Options flow analysis
5. AI Options Agent (ai_options_agent_page.py) - Position recommendations
...

Each feature integrates with the centralized data layer and RAG knowledge base.
For details on a specific feature, just ask!
```

**Question:** "How do I find CSP opportunities?"

**AVA Answer:**
```
To find CSP opportunities in Magnus:

1. Run the Opportunities Finder:
   - Navigate to "Opportunities" in the dashboard sidebar
   - Or run: csp_opportunities_finder.py

2. The scanner automatically filters for:
   - IV Percentile > 30%
   - Delta between 0.15-0.35
   - Earnings conflicts (checks earnings calendar)
   - Supply/demand zone confirmation

3. Results show quality-scored opportunities with:
   - Expected premium
   - Risk metrics
   - Technical analysis
   - AI recommendations

Code reference: src/csp_opportunities_finder.py:156
```

**Question:** "Where is the database schema?"

**AVA Answer:**
```
Magnus uses PostgreSQL with 7 specialized schemas:

1. development_tasks - Task and QA tracking
   Tables: development_tasks, qa_agent_sign_offs, qa_tasks

2. xtrades - Professional trader alerts
   Tables: alerts, alert_metadata, profiles, watchlists

3. earnings - Earnings calendar
   Tables: earnings_calendar, earnings_history

...

Schema files located at:
- src/xtrades_schema.sql
- src/kalshi_schema.sql
- src/supply_demand_schema.sql

For specific table details, check the schema files or ask about a specific schema!
```

---

## Usage Instructions

### Testing AVA's Knowledge

```bash
# Run test suite
python test_ava_project_knowledge.py
```

**Expected Output:**
- Tests 5 common project questions
- Verifies keyword coverage in answers
- Checks feature lookup capabilities
- Reports overall knowledge quality

### Asking AVA Questions

**Via Telegram Bot:**
```
User: What features does Magnus have?
AVA: [Comprehensive feature list with descriptions]

User: How do I use the premium scanner?
AVA: [Step-by-step guide with code references]

User: Where is the earnings calendar code?
AVA: [File location with relevant functions]
```

**Via Python:**
```python
from src.ava.enhanced_project_handler import EnhancedProjectHandler

handler = EnhancedProjectHandler()

# Ask any project question
result = handler.answer_project_question("What integrations does Magnus have?")
print(result['answer'])

# Get specific feature info
feature_info = handler.get_feature_info("AI Options Agent")
print(feature_info['answer'])

# Get usage guide
guide = handler.get_usage_guide("sync TradingView watchlists")
print(guide['answer'])

# Search code
code_ref = handler.search_code("CSP opportunities")
print(code_ref['answer'])
```

### Integration with Existing AVA

```python
from src.ava.nlp_handler import NaturalLanguageHandler
from src.ava.enhanced_project_handler import integrate_with_ava

# Create standard AVA handler
ava = NaturalLanguageHandler()

# Enhance with project knowledge
ava = integrate_with_ava(ava)

# Now AVA handles both trading queries AND project questions
result = ava.parse_intent("What features does Magnus have?")
# Returns: intent='PROJECT_QUESTION' with full answer in response_hint

result = ava.parse_intent("Show my portfolio")
# Returns: intent='PORTFOLIO' (standard AVA intent)
```

---

## Knowledge Sources

### What AVA Knows

1. **All Features & Capabilities**
   - 14 major features with detailed descriptions
   - File locations and module structure
   - Usage patterns and best practices

2. **Database Architecture**
   - 7 schemas with table details
   - Data relationships and purposes
   - Query patterns and optimization tips

3. **API Integrations**
   - Robinhood, TradingView, XTrades, Kalshi
   - Authentication methods
   - Endpoint descriptions
   - Error handling approaches

4. **Common Tasks**
   - Portfolio balance checking
   - CSP opportunity finding
   - Position analysis
   - XTrades monitoring
   - RAG knowledge queries

5. **AI/ML Systems**
   - RAG semantic search capabilities
   - Multi-agent QA system
   - Position recommendation engine
   - Prediction market analysis

### Knowledge Maintenance

**Auto-Generated File:**
`MAGNUS_PROJECT_KNOWLEDGE.md` is automatically regenerated whenever:
```bash
python -m src.ava.magnus_project_knowledge
```

**Manual Updates:**
Edit `MagnusProjectKnowledge` class methods to add:
- New features as they're developed
- Updated API endpoints
- New database schemas
- Additional integrations

**RAG Indexing:**
Once Task #202 completes (ChromaDB indexing), all project knowledge will be semantically searchable via RAG.

---

## Benefits

### For Users

1. **Self-Service Help** - Users can ask AVA instead of reading docs
2. **Contextual Guidance** - Get answers specific to their task
3. **Code Discovery** - Find relevant files without searching
4. **Learning Aid** - Understand Magnus architecture naturally

### For Development

1. **Onboarding** - New developers can query Magnus structure
2. **Feature Discovery** - Find existing capabilities before building
3. **Integration Help** - Understand how components connect
4. **Documentation** - Self-updating knowledge base

### For AVA

1. **Smarter Routing** - Knows when question is about Magnus vs. trading
2. **Better Context** - Understands system it operates within
3. **Proactive Suggestions** - Can recommend relevant features
4. **Complete Assistant** - Handles both domain (trading) and system (Magnus) questions

---

## Technical Details

### RAG Integration

**Collection:** `magnus_knowledge`

**Document Structure:**
```json
{
  "content": "Feature description with capabilities...",
  "metadata": {
    "source": "magnus_project_knowledge",
    "type": "project_summary",
    "section_index": 3,
    "indexed_at": "2025-11-11T12:32:29"
  }
}
```

**Query Process:**
1. User asks project question
2. RAG retrieves 5 most relevant chunks
3. Chunks provide context for LLM
4. LLM generates comprehensive answer
5. Sources returned with answer

### LLM Usage

**Service:** FREE LLM service (Groq/Gemini/DeepSeek)
**Cost:** $0.00 (using free tiers)
**Temperature:** 0.3 (balanced creativity/accuracy)
**Max Tokens:** 800 (comprehensive answers)
**Caching:** Enabled for repeated questions

**Prompt Structure:**
```
You are AVA, the Magnus Trading Dashboard financial assistant.

Answer this question about the Magnus project using the provided context.

**Question:** [user question]

**Magnus Project Context:**
[RAG-retrieved relevant chunks]

**Instructions:**
1. Provide clear, concise answer
2. Reference specific features/files when relevant
3. Include practical usage examples
4. Mention file paths using "file_path:line" pattern
5. Acknowledge what you don't know if context insufficient

**Answer:**
```

### Fallback Mechanism

If LLM or RAG unavailable, AVA uses cached fallback answers:
- General feature list for "what features" questions
- Basic usage guide for "how to" questions
- Database schema summary for "database" questions
- Prompt for more specificity on vague questions

---

## Future Enhancements

### Planned Improvements

1. **Code Snippet Retrieval**
   - Return actual code snippets from files
   - Show relevant function signatures
   - Display usage examples from codebase

2. **Interactive Tutorials**
   - Step-by-step walkthroughs
   - Live command execution
   - Progress tracking

3. **Visual Responses**
   - Architecture diagrams
   - Feature relationship maps
   - Database schema visualizations

4. **Proactive Suggestions**
   - "You might also be interested in..."
   - Related features discovery
   - Optimization recommendations

5. **Historical Knowledge**
   - Track feature usage patterns
   - Learn from user questions
   - Improve answers over time

### Integration Opportunities

1. **Telegram Bot** - Project questions via chat
2. **Dashboard Help** - In-app contextual help
3. **Documentation Site** - Auto-generated from knowledge base
4. **Developer Tools** - Code navigation assistant
5. **Onboarding Flow** - Guided new user experience

---

## Summary

AVA now has comprehensive knowledge about Magnus project and can answer questions about features, usage, code structure, and architecture. This creates a more complete assistant that understands both the trading domain and the system it operates within.

**Key Achievement:** AVA transitions from "trading assistant" to "comprehensive Magnus guide"

**Next Step:** Once Task #202 completes ChromaDB indexing, all documentation will be semantically searchable, making AVA even more powerful.

**Try It:**
```bash
python test_ava_project_knowledge.py
```

Or ask AVA directly:
- "What can Magnus do?"
- "How do I find good trades?"
- "Where is the positions page?"
- "Explain the database structure"
- "What integrations does Magnus have?"

AVA knows! 🎯
