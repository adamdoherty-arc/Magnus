# Unified Agent Architecture Plan

**Date:** November 15, 2025  
**Goal:** Migrate all agents to unified LangGraph/LangChain architecture with Hugging Face integration

---

## Current Agent Inventory

### 1. AVA Core Agents (LangGraph-based)
- **Location:** `src/ava/core/multi_agent.py`
- **Agents:**
  - Market Agent (placeholder)
  - Strategy Agent (placeholder)
  - Risk Agent (placeholder)
  - Knowledge Agent (RAG-based)

### 2. AI Research Agents (CrewAI-based)
- **Location:** `src/agents/ai_research/`
- **Agents:**
  - FundamentalAgent (Alpha Vantage)
  - TechnicalAgent (yfinance + TA)
  - SentimentAgent (Reddit + news)
  - OptionsAgent (yfinance options)

### 3. Runtime Agents (Custom async)
- **Location:** `src/agents/runtime/`
- **Agents:**
  - MarketDataAgent (yfinance + TradingView)
  - WheelStrategyAgent (options analysis)
  - RiskManagementAgent (portfolio risk)
  - AlertAgent (notifications)

### 4. Options Analysis Agent
- **Location:** `src/ai_options_agent/options_analysis_agent.py`
- **Purpose:** Options opportunity scoring and analysis

### 5. Betting Agent
- **Location:** `src/advanced_betting_ai_agent.py`
- **Purpose:** Sports betting predictions

### 6. Other Agents
- `src/ava/autonomous_agent.py` - Autonomous agent
- `src/ava/research_agent.py` - Research agent
- `src/legion/legion_operator_agent.py` - Legion operator
- `src/qa/` - QA agents

---

## Unified Architecture Design

### Base Agent Class
All agents will inherit from a base class that provides:
- LangChain tool integration
- Hugging Face model support
- State management
- Error handling
- Logging
- Caching

### Agent Registry
Central registry to:
- Register all agents
- Route requests to appropriate agents
- Track agent capabilities
- Manage agent lifecycle

### Supervisor Pattern
Enhanced supervisor that:
- Routes to specialized agents
- Coordinates multi-agent workflows
- Synthesizes results
- Handles agent failures

---

## Implementation Plan

### Phase 1: Base Infrastructure
1. Create base agent class
2. Create agent registry
3. Add Hugging Face integration
4. Create agent state management

### Phase 2: Migrate Existing Agents
1. Migrate AI Research agents
2. Migrate Runtime agents
3. Migrate Options Analysis agent
4. Migrate Betting agent

### Phase 3: Create New Specialized Agents
1. Portfolio Management Agent
2. Watchlist Analysis Agent
3. Earnings Analysis Agent
4. Supply/Demand Zone Agent
5. Xtrades Monitor Agent
6. Task Management Agent

### Phase 4: Integration
1. Update multi-agent supervisor
2. Integrate with AVA Core
3. Update all adapters (Streamlit, Telegram, API)
4. Testing

---

## Agent Categories

### Trading Agents
- Market Data Agent
- Options Analysis Agent
- Strategy Recommendation Agent
- Risk Management Agent
- Portfolio Management Agent

### Analysis Agents
- Fundamental Analysis Agent
- Technical Analysis Agent
- Sentiment Analysis Agent
- Earnings Analysis Agent
- Supply/Demand Zone Agent

### Monitoring Agents
- Watchlist Monitor Agent
- Xtrades Monitor Agent
- Alert Agent
- Price Action Monitor Agent

### Research Agents
- Research Orchestrator
- Knowledge Agent (RAG)
- Documentation Agent

### Management Agents
- Task Management Agent
- Position Management Agent
- Watchlist Management Agent

---

## Next Steps

1. Create base agent infrastructure
2. Migrate agents one by one
3. Add Hugging Face support
4. Test and document

