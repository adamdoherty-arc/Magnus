"""
Create Development Tasks for Magnus Financial Assistant Feature
=================================================================

This script creates all development tasks for the Financial Assistant feature
in the Magnus development_tasks table, properly structured for Legion integration.

Author: Claude Code
Date: 2025-01-10
"""

import psycopg2
from psycopg2.extras import RealDictCursor
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

# Database connection
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'port': os.getenv('DB_PORT', '5432'),
    'database': os.getenv('DB_NAME', 'magnus'),
    'user': os.getenv('DB_USER', 'postgres'),
    'password': os.getenv('DB_PASSWORD', '')
}

def create_tasks():
    """Create all Financial Assistant tasks"""

    conn = psycopg2.connect(**DB_CONFIG)
    cursor = conn.cursor(cursor_factory=RealDictCursor)

    tasks = [
        # PHASE 1: FOUNDATION (Week 1-2)
        {
            "title": "Set up RAG infrastructure with ChromaDB",
            "description": """
Install and configure ChromaDB for vector storage.

Requirements:
- Install chromadb package
- Create ChromaDB client configuration
- Set up persistent storage directory
- Test basic CRUD operations
- Configure distance metrics (cosine)

Acceptance Criteria:
- ChromaDB operational and accessible
- Can store and retrieve vectors
- Persistence works across restarts

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (RAG System section)
Spec: features/financial_assistant/SPEC.md (FR-2.2.1)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-1", "rag", "infrastructure"]
        },
        {
            "title": "Create embedding pipeline with sentence-transformers",
            "description": """
Build embedding generation system using sentence-transformers.

Requirements:
- Install sentence-transformers library
- Load all-MiniLM-L6-v2 model (384 dimensions)
- Create embedding function for text chunks
- Implement batch embedding for performance
- Add error handling for encoding failures

Acceptance Criteria:
- Can generate embeddings for documents
- Batch processing works efficiently
- Embeddings stored in correct format

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Embedding Strategy section)
Spec: features/financial_assistant/SPEC.md (FR-2.2.2)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-1", "rag", "embeddings"]
        },
        {
            "title": "Index all Magnus documentation (48 documents)",
            "description": """
Index all Magnus feature documentation into ChromaDB.

Requirements:
- Read all files from features/*/{README,SPEC,ARCHITECTURE,WISHLIST}.md
- Chunk documents (500 tokens per chunk)
- Generate embeddings for each chunk
- Store in ChromaDB with metadata (feature, doc_type)
- Create index mapping file

Acceptance Criteria:
- All 48 documents indexed
- Metadata preserved correctly
- Can retrieve relevant docs via query
- Index rebuild script created

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (What Gets Embedded section)
Spec: features/financial_assistant/SPEC.md (FR-2.2.1)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-1", "rag", "knowledge-base"]
        },
        {
            "title": "Create financial knowledge base (200+ concepts)",
            "description": """
Curate and index financial trading concepts.

Requirements:
- Create markdown files for 200+ financial concepts:
  - Options strategies (CSP, covered calls, spreads)
  - Greeks (Delta, Theta, Vega, Gamma, Rho)
  - Risk management principles
  - Position sizing guidelines
  - IV concepts
- Organize by category and difficulty level
- Embed and index in ChromaDB
- Create concept search function

Acceptance Criteria:
- 200+ concepts documented
- All concepts indexed
- Can retrieve by category
- Search works accurately

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Financial Knowledge section)
Spec: features/financial_assistant/SPEC.md (FR-2.2.1)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 360,
            "tags": ["phase-1", "knowledge-base", "content"]
        },
        {
            "title": "Implement hybrid retrieval (semantic + keyword + rerank)",
            "description": """
Build hybrid search combining vector search, keyword search, and reranking.

Requirements:
- Implement semantic search (ChromaDB query)
- Add keyword search (BM25 using rank_bm25)
- Implement cross-encoder reranking
- Combine results with score fusion
- Return top-K with metadata

Acceptance Criteria:
- Retrieval accuracy >90% on test queries
- Response time <500ms
- Handles edge cases (empty results, etc.)

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Retrieval Strategy section)
Spec: features/financial_assistant/SPEC.md (FR-2.2.2)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-1", "rag", "retrieval"]
        },
        {
            "title": "Set up LangChain and LangGraph orchestration",
            "description": """
Configure LangChain/LangGraph for conversation orchestration.

Requirements:
- Install langchain and langgraph packages
- Create LangGraph state machine for conversations
- Define conversation states (classify, retrieve, respond, execute)
- Implement state transitions
- Add conversation memory

Acceptance Criteria:
- LangGraph state machine operational
- States transition correctly
- Conversation flow works end-to-end

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Architecture section)
Spec: features/financial_assistant/SPEC.md (Section 5)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 300,
            "tags": ["phase-1", "orchestration", "langchain"]
        },
        {
            "title": "Create intent classification system",
            "description": """
Build intent classifier to route user queries to appropriate agents.

Requirements:
- Define 7 intent categories:
  portfolio_query, market_research, strategy_advice,
  risk_management, trade_execution, education, data_query
- Create few-shot examples for each intent (5-10 examples)
- Implement classifier using LLM (Groq FREE)
- Add confidence scoring (>0.8 threshold)
- Handle multi-intent queries

Acceptance Criteria:
- Classification accuracy >95% on test set
- Response time <1 second
- Confidence scores reliable

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Conversation Interface section)
Spec: features/financial_assistant/SPEC.md (FR-2.1.3)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-1", "nlp", "intent-classification"]
        },
        {
            "title": "Build Streamlit chat interface (basic version)",
            "description": """
Create basic chat interface using Streamlit.

Requirements:
- Create financial_assistant_page.py
- Use streamlit-chat for message display
- Implement chat input box
- Display user and assistant messages
- Store conversation history in session state
- Add typing indicators

Acceptance Criteria:
- Chat interface loads without errors
- Messages display correctly
- Conversation history preserved
- UI is responsive and clean

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (UI section)
Spec: features/financial_assistant/SPEC.md (Section 4.1)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "frontend-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-1", "ui", "streamlit"]
        },
        {
            "title": "Connect RAG system to chat interface",
            "description": """
Integrate RAG retrieval with chat interface.

Requirements:
- Connect chat input to intent classifier
- Use intent to query RAG system
- Display retrieved context (optional debug mode)
- Generate response using LLM + context
- Stream response to UI

Acceptance Criteria:
- Can answer questions about Magnus features
- RAG context improves response accuracy
- Responses are coherent and helpful

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Data Flow section)
Spec: features/financial_assistant/SPEC.md (FR-2.2.2, FR-2.5.1)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-1", "integration", "rag"]
        },
        {
            "title": "Create conversation database schema",
            "description": """
Design and implement database schema for conversations.

Requirements:
- Create tables:
  - mfa_conversations (messages)
  - mfa_user_preferences (settings)
  - mfa_agent_logs (agent execution)
  - mfa_knowledge_base (metadata)
- Add indexes for performance
- Implement CRUD functions
- Add migration script

Acceptance Criteria:
- All tables created successfully
- Indexes improve query performance
- CRUD operations work correctly

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Database Schema section)
Spec: features/financial_assistant/SPEC.md (Section 5.3)
""",
            "task_type": "feature",
            "priority": "medium",
            "assigned_agent": "postgresql-pglite-pro",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-1", "database", "schema"]
        },

        # PHASE 2: MULTI-AGENT SYSTEM (Week 3-4)
        {
            "title": "Set up CrewAI framework for multi-agent system",
            "description": """
Install and configure CrewAI for agent coordination.

Requirements:
- Install crewai package
- Create base agent class structure
- Configure LLM connections (Groq, Claude, Gemini)
- Set up agent crew framework
- Define agent communication protocols

Acceptance Criteria:
- CrewAI installed and operational
- Can create and run basic agents
- LLM connections work correctly

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Multi-Agent Architecture section)
Spec: features/financial_assistant/SPEC.md (FR-2.3, Section 5.1)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-2", "agents", "infrastructure"]
        },
        {
            "title": "Build Portfolio Analyst Agent",
            "description": """
Create Portfolio Analyst agent for portfolio analysis.

Requirements:
- Define agent role, goal, backstory
- Implement tools:
  - fetch_positions (from Robinhood)
  - calculate_portfolio_metrics
  - analyze_greeks
  - project_theta_decay
- Add position analysis logic
- Generate portfolio summary reports

Acceptance Criteria:
- Agent fetches positions correctly
- Portfolio metrics accurate
- Summary reports are comprehensive

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Agent definitions)
Spec: features/financial_assistant/SPEC.md (FR-2.3.1)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 300,
            "tags": ["phase-2", "agents", "portfolio"]
        },
        {
            "title": "Build Market Researcher Agent",
            "description": """
Create Market Researcher agent for market data gathering.

Requirements:
- Define agent role and tools
- Implement tools:
  - fetch_options_chain
  - get_market_news
  - analyze_unusual_activity
  - check_earnings_dates
  - query_prediction_markets (Kalshi)
- Add IV rank checking
- Implement unusual activity detection

Acceptance Criteria:
- Agent fetches market data correctly
- IV calculations accurate
- Earnings dates retrieved correctly

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Agent definitions)
Spec: features/financial_assistant/SPEC.md (FR-2.3.2)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 300,
            "tags": ["phase-2", "agents", "market-data"]
        },
        {
            "title": "Build Strategy Advisor Agent",
            "description": """
Create Strategy Advisor agent for trade recommendations.

Requirements:
- Define agent with strategy expertise
- Implement tools:
  - rag_query_strategies
  - evaluate_csp_opportunity
  - analyze_calendar_spread
  - calculate_expected_value
  - assess_risk_reward
- Use RAG for strategy knowledge
- Generate trade recommendations with reasoning

Acceptance Criteria:
- Agent provides accurate recommendations
- Reasoning is clear and sound
- EV calculations correct

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Agent definitions)
Spec: features/financial_assistant/SPEC.md (FR-2.3.3)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 360,
            "tags": ["phase-2", "agents", "strategy"]
        },
        {
            "title": "Build Risk Manager Agent",
            "description": """
Create Risk Manager agent for portfolio risk assessment.

Requirements:
- Define agent with risk management focus
- Implement tools:
  - calculate_portfolio_delta
  - check_concentration_risk
  - monitor_margin_usage
  - suggest_hedges
  - alert_earnings_risk
- Add risk threshold checking
- Generate risk warnings

Acceptance Criteria:
- Risk calculations accurate
- Warnings trigger appropriately
- Hedge suggestions reasonable

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Agent definitions)
Spec: features/financial_assistant/SPEC.md (FR-2.3.4)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 300,
            "tags": ["phase-2", "agents", "risk"]
        },
        {
            "title": "Build Financial Educator Agent",
            "description": """
Create Educator agent for teaching financial concepts.

Requirements:
- Define agent with teaching focus
- Implement tools:
  - rag_query_concepts
  - generate_examples
  - create_visualizations
  - recommend_resources
- Use RAG for concept explanations
- Generate beginner-friendly explanations

Acceptance Criteria:
- Explanations are clear and accurate
- Examples are relevant
- Suitable for beginners

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Agent definitions)
Spec: features/financial_assistant/SPEC.md (FR-2.3.6)
""",
            "task_type": "feature",
            "priority": "medium",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-2", "agents", "education"]
        },
        {
            "title": "Implement all agent tools (25+ functions)",
            "description": """
Build all tool functions for agents to call.

Requirements:
- Portfolio tools (4 functions)
- Market data tools (5 functions)
- Opportunity scanning tools (4 functions)
- Analysis tools (4 functions)
- Data retrieval tools (4 functions)
- RAG system tools (3 functions)
- Integration tools (3 functions)
- Add error handling for all tools
- Log tool usage

Acceptance Criteria:
- All 25+ tools implemented
- Tool calls succeed >98% of time
- Error handling robust

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Tools section)
Spec: features/financial_assistant/SPEC.md (FR-2.4)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 480,
            "tags": ["phase-2", "tools", "backend"]
        },
        {
            "title": "Create agent crew coordinator",
            "description": """
Build coordination system for multi-agent collaboration.

Requirements:
- Create Crew with all 5 agents
- Set up hierarchical process (manager coordinates)
- Configure Claude as manager LLM
- Implement task routing logic
- Add parallel execution where possible
- Handle agent failures gracefully

Acceptance Criteria:
- Agents collaborate correctly
- Manager routes tasks appropriately
- Parallel execution works
- Failures handled without crashes

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Multi-Agent System section)
Spec: features/financial_assistant/SPEC.md (FR-2.3, Section 5.2)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "ai-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 360,
            "tags": ["phase-2", "agents", "coordination"]
        },
        {
            "title": "Integrate agents with chat interface",
            "description": """
Connect multi-agent system to Streamlit chat.

Requirements:
- Route classified intents to appropriate agents
- Display agent thinking process (optional)
- Show which agents are working
- Stream agent responses
- Handle multi-agent responses
- Add action buttons for agent suggestions

Acceptance Criteria:
- Agent responses display correctly
- Multi-agent coordination visible
- UI updates in real-time

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (System Overview section)
Spec: features/financial_assistant/SPEC.md (Section 4.1)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-2", "integration", "ui"]
        },
        {
            "title": "Add conversation memory and context management",
            "description": """
Implement conversation memory to maintain context.

Requirements:
- Store last 20 messages in session state
- Track conversation state across turns
- Implement context window management
- Add context retrieval for follow-up questions
- Handle context switches gracefully

Acceptance Criteria:
- Follow-up questions work correctly
- Context preserved across turns
- Memory doesn't grow unbounded

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Conversation Management section)
Spec: features/financial_assistant/SPEC.md (FR-2.5)
""",
            "task_type": "feature",
            "priority": "medium",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-2", "conversation", "memory"]
        },
        {
            "title": "Implement response caching for performance",
            "description": """
Add caching to reduce LLM API calls and improve response time.

Requirements:
- Cache RAG retrieval results (5-min TTL)
- Cache market data (1-min TTL)
- Cache portfolio data (30-sec TTL)
- Use Redis or in-memory cache
- Implement cache invalidation
- Add cache hit rate metrics

Acceptance Criteria:
- Cache hit rate >80% for common queries
- Response time improves by >50%
- No stale data served

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Performance section)
Spec: features/financial_assistant/SPEC.md (NFR-3.1.3)
""",
            "task_type": "enhancement",
            "priority": "medium",
            "assigned_agent": "performance-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-2", "performance", "caching"]
        },

        # PHASE 3: ADVANCED FEATURES (Week 5-6)
        {
            "title": "Integrate Whisper for voice input",
            "description": """
Add voice input capability using Whisper.

Requirements:
- Install whisper or openai-whisper
- Create audio recording component in Streamlit
- Implement voice → text transcription
- Add microphone button to chat interface
- Handle audio file uploads
- Display transcription before processing

Acceptance Criteria:
- Voice input works reliably
- Transcription accuracy >95%
- Audio recording smooth
- Transcription displayed correctly

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Voice Interface section)
Spec: features/financial_assistant/SPEC.md (FR-2.1.2)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-3", "voice", "whisper"]
        },
        {
            "title": "Add TTS for voice output",
            "description": """
Implement text-to-speech for voice responses.

Requirements:
- Install pyttsx3 or elevenlabs SDK
- Create TTS synthesis function
- Add voice playback to chat interface
- Implement voice enable/disable toggle
- Generate voice files for responses
- Auto-play voice responses (optional)

Acceptance Criteria:
- TTS sounds natural
- Voice playback works smoothly
- Toggle works correctly
- No audio glitches

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Voice Interface section)
Spec: features/financial_assistant/SPEC.md (FR-2.1.2)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-3", "voice", "tts"]
        },
        {
            "title": "Create Trade Executor Agent",
            "description": """
Build agent for executing trades via Robinhood.

Requirements:
- Define Trade Executor agent
- Implement tools:
  - submit_robinhood_order
  - check_order_status
  - update_trade_database
  - send_notification
  - log_execution
- Add order verification
- Implement confirmation dialogs
- Update database on fills

Acceptance Criteria:
- Can submit orders successfully
- Order status tracking works
- Database updated correctly
- Zero errors in execution

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Agent definitions)
Spec: features/financial_assistant/SPEC.md (FR-2.3.5)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 360,
            "tags": ["phase-3", "agents", "execution"]
        },
        {
            "title": "Implement trade verification and confirmation flow",
            "description": """
Add safety checks and confirmations for trade execution.

Requirements:
- Preview order before submission
- Show order details (symbol, strike, premium, risk)
- Add confirmation dialog with warnings
- Require explicit user confirmation
- Log all confirmations
- Add double-check for parameters

Acceptance Criteria:
- Preview shows all details correctly
- Confirmation required for all trades
- Warnings display appropriately
- All steps logged

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Safety section)
Spec: features/financial_assistant/SPEC.md (FR-2.6.3)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-3", "safety", "execution"]
        },
        {
            "title": "Add financial disclaimer system",
            "description": """
Implement disclaimer display and acknowledgment tracking.

Requirements:
- Create disclaimer text (legal)
- Display disclaimer on first use
- Require user acknowledgment
- Store acknowledgment in database
- Repeat disclaimer for trade executions
- Add disclaimer to settings page

Acceptance Criteria:
- Disclaimer displays correctly
- Users must acknowledge before using
- All acknowledgments logged
- Disclaimer text legally sound

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Safety & Compliance section)
Spec: features/financial_assistant/SPEC.md (FR-2.6.1)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 120,
            "tags": ["phase-3", "safety", "compliance"]
        },
        {
            "title": "Implement risk warning system",
            "description": """
Add automated risk warnings for dangerous trades.

Requirements:
- Check for overleveraging (>30% buying power)
- Detect concentration risk (duplicate symbols)
- Flag earnings before expiration
- Warn on low liquidity (<50 volume)
- Display warnings prominently
- Require acknowledgment for warnings

Acceptance Criteria:
- All risk checks implemented
- Warnings trigger correctly
- Warnings are clear and actionable
- Can proceed after acknowledgment

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Risk Warnings section)
Spec: features/financial_assistant/SPEC.md (FR-2.6.2)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-3", "safety", "risk"]
        },
        {
            "title": "Create daily portfolio summary notifications",
            "description": """
Implement proactive daily portfolio summaries.

Requirements:
- Create scheduled job (runs daily at 8am)
- Fetch current positions
- Calculate overnight changes
- Generate summary message
- Send via Telegram (if enabled)
- Display in chat on first visit

Acceptance Criteria:
- Summary sends daily at 8am
- Summary is accurate and useful
- Telegram integration works
- Users can enable/disable

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Proactive Assistance section)
Spec: features/financial_assistant/SPEC.md (FR-2.7.1)
""",
            "task_type": "feature",
            "priority": "medium",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-3", "proactive", "notifications"]
        },
        {
            "title": "Add risk monitoring and alerts",
            "description": """
Implement continuous risk monitoring with alerts.

Requirements:
- Monitor portfolio delta (check every hour)
- Alert when delta exceeds threshold
- Check concentration risk
- Monitor earnings dates
- Send alerts via Telegram/chat
- Allow users to configure thresholds

Acceptance Criteria:
- Monitoring runs continuously
- Alerts trigger correctly
- Thresholds configurable
- No false positives

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Proactive Assistance section)
Spec: features/financial_assistant/SPEC.md (FR-2.7.2)
""",
            "task_type": "feature",
            "priority": "medium",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-3", "proactive", "risk-monitoring"]
        },
        {
            "title": "Create opportunity notification system",
            "description": """
Build proactive opportunity scanning and notification.

Requirements:
- Scan for CSP opportunities (every 4 hours)
- Check watchlist for good setups
- Detect IV spikes
- Identify calendar spread opportunities
- Send notifications for high-quality setups
- Allow users to configure preferences

Acceptance Criteria:
- Scanning runs automatically
- Notifications timely and relevant
- Users can customize preferences
- No notification spam

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Proactive Assistance section)
Spec: features/financial_assistant/SPEC.md (FR-2.7.3)
""",
            "task_type": "feature",
            "priority": "medium",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 300,
            "tags": ["phase-3", "proactive", "opportunities"]
        },
        {
            "title": "Enhance Telegram bot with MFA integration",
            "description": """
Integrate Financial Assistant with enhanced Telegram bot.

Requirements:
- Update existing AVA bot
- Add MFA conversation handling
- Implement voice message support
- Add inline keyboards for actions
- Create bot commands (/portfolio, /findtrade, /help)
- Test end-to-end flow

Acceptance Criteria:
- Bot responds via MFA
- Voice messages work
- Commands execute correctly
- User experience smooth

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Telegram Bot section)
Spec: features/financial_assistant/SPEC.md (Section 4.2)
""",
            "task_type": "enhancement",
            "priority": "medium",
            "assigned_agent": "full-stack-developer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-3", "telegram", "integration"]
        },

        # PHASE 4: PRODUCTION READY (Week 7-8)
        {
            "title": "Implement comprehensive error handling",
            "description": """
Add robust error handling throughout MFA system.

Requirements:
- Wrap all API calls in try-except
- Add retry logic for transient failures
- Implement graceful degradation
- Create meaningful error messages for users
- Log all errors with context
- Add error recovery flows

Acceptance Criteria:
- No unhandled exceptions
- Errors logged appropriately
- Users see helpful error messages
- System recovers automatically

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Reliability section)
Spec: features/financial_assistant/SPEC.md (NFR-3.3.2)
""",
            "task_type": "enhancement",
            "priority": "high",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-4", "reliability", "error-handling"]
        },
        {
            "title": "Add comprehensive logging and monitoring",
            "description": """
Implement logging and monitoring infrastructure.

Requirements:
- Log all conversations (anonymized if needed)
- Log all agent executions
- Log all tool calls and results
- Track performance metrics (response time, etc.)
- Create monitoring dashboard
- Set up alerts for errors

Acceptance Criteria:
- All actions logged
- Metrics collected correctly
- Dashboard shows key stats
- Alerts work reliably

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Monitoring section)
Spec: features/financial_assistant/SPEC.md (Section 10.3)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "backend-architect",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-4", "monitoring", "logging"]
        },
        {
            "title": "Optimize performance for production scale",
            "description": """
Optimize MFA for 100+ concurrent users.

Requirements:
- Profile slow operations
- Optimize database queries
- Implement connection pooling
- Add parallel agent execution
- Optimize embedding generation
- Load test system

Acceptance Criteria:
- 95th percentile response time <3s
- Can handle 100 concurrent users
- No memory leaks
- Performance degrades gracefully

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Performance section)
Spec: features/financial_assistant/SPEC.md (NFR-3.1, NFR-3.2)
""",
            "task_type": "enhancement",
            "priority": "high",
            "assigned_agent": "performance-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 300,
            "tags": ["phase-4", "performance", "optimization"]
        },
        {
            "title": "Create comprehensive test suite",
            "description": """
Build test suite covering all MFA functionality.

Requirements:
- Unit tests for all agents (80% coverage)
- Integration tests for workflows
- End-to-end conversation tests
- Performance tests
- Load tests
- Voice interface tests
- Create test data fixtures

Acceptance Criteria:
- Test coverage >80%
- All tests pass
- CI/CD pipeline integrated
- Tests run in <5 minutes

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Testing section)
Spec: features/financial_assistant/SPEC.md (Section 9)
""",
            "task_type": "qa",
            "priority": "high",
            "assigned_agent": "test-automator",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 360,
            "tags": ["phase-4", "testing", "qa"]
        },
        {
            "title": "Write comprehensive user documentation",
            "description": """
Create complete user guide for MFA.

Requirements:
- Write user guide (README.md)
- Document all features
- Create example conversations (20+)
- Write troubleshooting guide
- Create video tutorial (10 min)
- Add inline help in UI

Acceptance Criteria:
- Documentation complete and clear
- Examples cover common scenarios
- Video tutorial professional
- Help accessible in UI

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Documentation section)
Spec: features/financial_assistant/SPEC.md (AC-7.4.3)
""",
            "task_type": "documentation",
            "priority": "high",
            "assigned_agent": "general-purpose",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 300,
            "tags": ["phase-4", "documentation"]
        },
        {
            "title": "Create API documentation for Legion integration",
            "description": """
Document all MFA APIs for external integration.

Requirements:
- Document REST API endpoints
- Provide request/response examples
- Document websocket interface (if added)
- Create Postman collection
- Write integration guide for Legion
- Document rate limits and quotas

Acceptance Criteria:
- All endpoints documented
- Examples work correctly
- Postman collection functional
- Integration guide clear

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (API section)
Spec: features/financial_assistant/SPEC.md (Section 6)
""",
            "task_type": "documentation",
            "priority": "medium",
            "assigned_agent": "general-purpose",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-4", "documentation", "api"]
        },
        {
            "title": "Conduct security audit and fixes",
            "description": """
Perform security audit and address findings.

Requirements:
- Audit API key storage
- Check for SQL injection vectors
- Verify authentication/authorization
- Test input validation
- Check for XSS vulnerabilities
- Implement security headers
- Fix all critical/high findings

Acceptance Criteria:
- No critical vulnerabilities
- All API keys encrypted
- Input validation robust
- Security best practices followed

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Security section)
Spec: features/financial_assistant/SPEC.md (NFR-3.4)
""",
            "task_type": "qa",
            "priority": "critical",
            "assigned_agent": "security-auditor",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-4", "security", "audit"]
        },
        {
            "title": "Prepare for production deployment",
            "description": """
Finalize production deployment preparation.

Requirements:
- Create deployment checklist
- Set up production environment
- Configure monitoring/alerting
- Prepare rollback plan
- Create runbook for operations
- Conduct deployment dry-run

Acceptance Criteria:
- All deployment steps documented
- Production environment ready
- Rollback plan tested
- Team trained on runbook

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Deployment section)
Spec: features/financial_assistant/SPEC.md (Section 10)
""",
            "task_type": "feature",
            "priority": "high",
            "assigned_agent": "deployment-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 240,
            "tags": ["phase-4", "deployment", "production"]
        },
        {
            "title": "Conduct user acceptance testing with beta users",
            "description": """
Run UAT with 10-20 beta users.

Requirements:
- Recruit 10-20 beta users
- Create UAT scenarios (20+)
- Conduct 2-week beta test
- Collect feedback via surveys
- Track usage metrics
- Address critical issues
- Iterate based on feedback

Acceptance Criteria:
- All scenarios tested
- User satisfaction >4.5/5
- Critical issues resolved
- Feedback incorporated

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Testing section)
Spec: features/financial_assistant/SPEC.md (Section 9.4)
""",
            "task_type": "qa",
            "priority": "high",
            "assigned_agent": "general-purpose",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 480,
            "tags": ["phase-4", "uat", "testing"]
        },
        {
            "title": "Launch MFA v1.0 to production",
            "description": """
Execute production launch of Financial Assistant.

Requirements:
- Deploy to production
- Monitor for 24 hours
- Verify all features working
- Monitor error rates
- Track user adoption
- Be ready for rollback
- Announce launch to users

Acceptance Criteria:
- Deployment successful
- No critical errors in first 24h
- Users can access MFA
- Monitoring shows healthy metrics

Documentation: FINANCIAL_ASSISTANT_MASTER_PLAN.md (Deployment section)
Spec: features/financial_assistant/SPEC.md (Section 10.1)
""",
            "task_type": "feature",
            "priority": "critical",
            "assigned_agent": "deployment-engineer",
            "feature_area": "financial_assistant",
            "estimated_duration_minutes": 180,
            "tags": ["phase-4", "deployment", "launch"]
        }
    ]

    created_tasks = []

    for task_data in tasks:
        try:
            cursor.execute("""
                INSERT INTO development_tasks (
                    title,
                    description,
                    task_type,
                    priority,
                    assigned_agent,
                    feature_area,
                    estimated_duration_minutes,
                    tags,
                    created_by
                ) VALUES (
                    %(title)s,
                    %(description)s,
                    %(task_type)s,
                    %(priority)s,
                    %(assigned_agent)s,
                    %(feature_area)s,
                    %(estimated_duration_minutes)s,
                    %(tags)s,
                    'legion-financial-assistant'
                )
                RETURNING id, title
            """, task_data)

            result = cursor.fetchone()
            created_tasks.append(result)

            print(f"[OK] Created task {result['id']}: {result['title']}")

        except Exception as e:
            print(f"[ERROR] Error creating task '{task_data['title']}': {e}")
            conn.rollback()
            continue

    conn.commit()
    cursor.close()
    conn.close()

    print(f"\n{'='*80}")
    print(f"[SUCCESS] TASK CREATION COMPLETE")
    print(f"{'='*80}")
    print(f"Total tasks created: {len(created_tasks)}")
    print(f"\nBreakdown by phase:")
    print(f"  Phase 1 (Foundation): 10 tasks")
    print(f"  Phase 2 (Multi-Agent): 10 tasks")
    print(f"  Phase 3 (Advanced): 9 tasks")
    print(f"  Phase 4 (Production): 11 tasks")
    print(f"\nAll tasks are now in the development_tasks table and ready for:")
    print(f"  - Legion to pick up and assign")
    print(f"  - Autonomous agent to execute")
    print(f"  - Progress tracking via Legion Operator")
    print(f"\n{'='*80}\n")

    return created_tasks


if __name__ == "__main__":
    print("="*80)
    print("CREATING FINANCIAL ASSISTANT DEVELOPMENT TASKS")
    print("="*80)
    print("\nThis will create 40 comprehensive tasks for the Magnus Financial")
    print("Assistant feature, properly structured for Legion integration.\n")

    # Running in non-interactive mode - proceeding automatically
    created_tasks = create_tasks()

    print(f"\n*** SUCCESS! Created {len(created_tasks)} tasks. ***")
    print("\nNext steps:")
    print("  1. Review tasks in enhancement_manager_page.py")
    print("  2. Legion can now discover and assign these tasks")
    print("  3. Autonomous agent can execute them")
    print("  4. Track progress via Legion Operator Agent")
    print("\nDocumentation references:")
    print("  - FINANCIAL_ASSISTANT_MASTER_PLAN.md (complete architecture)")
    print("  - features/financial_assistant/SPEC.md (detailed specifications)")
    print("  - LEGION_INTEGRATION_COMPLETE.md (Legion integration guide)")
