# Autonomous AI Financial Agents: Technical Implementation Guide

**Companion to**: AUTONOMOUS_AI_AGENTS_RESEARCH_2025.md
**Target Audience**: Engineers implementing production financial agents
**Code Examples**: Python 3.10+

---

## TABLE OF CONTENTS

1. [LangGraph Agent Setup](#1-langgraph-agent-setup)
2. [Memory System Implementation](#2-memory-system-implementation)
3. [RAG System with Hybrid Search](#3-rag-system-with-hybrid-search)
4. [Guardrails & Safety Layer](#4-guardrails--safety-layer)
5. [Observability & Monitoring](#5-observability--monitoring)
6. [Reinforcement Learning Integration](#6-reinforcement-learning-integration)

---

## 1. LANGGRAPH AGENT SETUP

### Basic Agent Structure

```python
"""
Financial Trading Agent using LangGraph
Implements multi-agent orchestration with state management
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List, Dict, Any
from enum import Enum
import anthropic

# Define the agent state
class AgentState(TypedDict):
    messages: List[Dict[str, str]]
    market_data: Dict[str, Any]
    risk_assessment: Dict[str, float]
    compliance_check: bool
    trading_decision: Dict[str, Any]
    execution_result: str

class TradeAction(Enum):
    BUY = "buy"
    SELL = "sell"
    HOLD = "hold"

# Initialize LLM
client = anthropic.Anthropic()

class FinancialAgents:
    """Multi-agent orchestration for trading decisions"""

    def __init__(self):
        self.graph = StateGraph(AgentState)
        self.memory = MemorySaver()
        self.build_graph()

    def build_graph(self):
        """Build the agent workflow graph"""

        # Add nodes (agents)
        self.graph.add_node("market_analyzer", self.market_analyst_agent)
        self.graph.add_node("risk_manager", self.risk_manager_agent)
        self.graph.add_node("compliance_officer", self.compliance_officer_agent)
        self.graph.add_node("executor", self.executor_agent)
        self.graph.add_node("guardian", self.guardian_agent)

        # Define edges (transitions)
        self.graph.set_entry_point("market_analyzer")

        self.graph.add_edge("market_analyzer", "risk_manager")
        self.graph.add_edge("risk_manager", "compliance_officer")

        # Conditional edge based on compliance check
        self.graph.add_conditional_edges(
            "compliance_officer",
            lambda state: "executor" if state["compliance_check"] else END,
            {"executor": "executor"}
        )

        self.graph.add_edge("executor", "guardian")

        # Guardian can veto
        self.graph.add_conditional_edges(
            "guardian",
            lambda state: "market_analyzer" if needs_revision(state) else END,
            {"market_analyzer": "market_analyzer"}
        )

        self.compiled_graph = self.graph.compile(checkpointer=self.memory)

    def market_analyst_agent(self, state: AgentState) -> AgentState:
        """Analyze market conditions and news"""

        analysis_prompt = f"""
        You are a market analyst for a trading firm.
        Current market data: {state['market_data']}

        Provide:
        1. Market sentiment (bullish/bearish/neutral)
        2. Technical analysis (support/resistance, trends)
        3. News impact assessment
        4. Recommended trading bias (long/short/neutral)

        Be concise and data-driven.
        """

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": analysis_prompt}
            ]
        )

        analysis = response.content[0].text

        state["messages"].append({
            "agent": "market_analyst",
            "analysis": analysis
        })

        return state

    def risk_manager_agent(self, state: AgentState) -> AgentState:
        """Assess portfolio risk"""

        risk_prompt = f"""
        You are a risk manager. Evaluate the trading recommendation from the market analyst.

        Current portfolio: {state.get('portfolio', {})}
        Proposed trade: {state['messages'][-1]['analysis']}

        Calculate:
        1. Current portfolio VAR
        2. Impact of proposed trade on concentration
        3. Correlation with existing positions
        4. Overall risk score (0-100)

        Return risk assessment as JSON.
        """

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=1024,
            messages=[
                {"role": "user", "content": risk_prompt}
            ]
        )

        risk_text = response.content[0].text

        state["risk_assessment"] = {
            "assessment": risk_text,
            "approved": extract_risk_score(risk_text) < 70  # Example threshold
        }

        state["messages"].append({
            "agent": "risk_manager",
            "risk_assessment": risk_text
        })

        return state

    def compliance_officer_agent(self, state: AgentState) -> AgentState:
        """Check regulatory compliance"""

        compliance_prompt = f"""
        You are a compliance officer. Check if the proposed trade complies with:
        1. Pattern day trader rules
        2. Margin requirements
        3. Sector rotation limits
        4. Regulatory restrictions on asset class

        Proposed trade: {state['messages'][-1]['analysis']}
        Account type: {state.get('account_type', 'standard')}

        Return compliance status as JSON: {{"compliant": true/false, "reason": "..."}}
        """

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {"role": "user", "content": compliance_prompt}
            ]
        )

        compliance_text = response.content[0].text
        state["compliance_check"] = "compliant" in compliance_text.lower()

        state["messages"].append({
            "agent": "compliance_officer",
            "compliance": compliance_text
        })

        return state

    def executor_agent(self, state: AgentState) -> AgentState:
        """Execute the trade"""

        execution_prompt = f"""
        You are a trading executor. Based on all analyses, prepare the trade execution.

        Market analysis: {state['messages'][0]['analysis']}
        Risk assessment: {state['risk_assessment']}

        Prepare:
        1. Order details (symbol, quantity, order type)
        2. Entry point rationale
        3. Stop loss level
        4. Profit target

        Return as JSON.
        """

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {"role": "user", "content": execution_prompt}
            ]
        )

        execution_plan = response.content[0].text

        state["trading_decision"] = {
            "plan": execution_plan,
            "timestamp": datetime.now().isoformat()
        }

        state["messages"].append({
            "agent": "executor",
            "execution_plan": execution_plan
        })

        return state

    def guardian_agent(self, state: AgentState) -> AgentState:
        """Independent validation of trading decision"""

        validation_prompt = f"""
        You are an independent guardian agent with veto authority.
        Review the proposed trade for safety and reasonableness.

        Trade plan: {state['trading_decision']['plan']}
        All previous analysis: {state['messages']}

        Check:
        1. Is the risk/reward ratio acceptable?
        2. Does the analysis support the trade?
        3. Are there any red flags or inconsistencies?
        4. Would you approve this trade?

        Return: {{"approved": true/false, "reasoning": "..."}}
        """

        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=512,
            messages=[
                {"role": "user", "content": validation_prompt}
            ]
        )

        guardian_review = response.content[0].text

        state["execution_result"] = guardian_review

        state["messages"].append({
            "agent": "guardian",
            "review": guardian_review
        })

        return state

    async def run(self, market_data: Dict[str, Any]) -> AgentState:
        """Run the agent pipeline"""

        initial_state = AgentState(
            messages=[],
            market_data=market_data,
            risk_assessment={},
            compliance_check=False,
            trading_decision={},
            execution_result=""
        )

        # Execute graph
        result = self.compiled_graph.invoke(initial_state)

        return result

# Helper functions
def extract_risk_score(risk_text: str) -> float:
    """Extract risk score from risk assessment"""
    # Implementation would parse the response
    return 50.0

def needs_revision(state: AgentState) -> bool:
    """Check if guardian agent requested revision"""
    return "revision" in state["execution_result"].lower()

from datetime import datetime
```

### Running the Agent

```python
# Initialize agent
agent = FinancialAgents()

# Sample market data
market_data = {
    "ticker": "AAPL",
    "current_price": 150.50,
    "day_high": 151.00,
    "day_low": 149.50,
    "volume": 45_000_000,
    "rsi": 55,
    "macd": "bullish_crossover",
    "news": [
        "Apple reports record earnings",
        "Supply chain constraints ease"
    ]
}

# Run analysis
result = await agent.run(market_data)

# Print results
print("Trading Decision:")
print(result["trading_decision"]["plan"])
print("\nGuardian Review:")
print(result["execution_result"])
```

---

## 2. MEMORY SYSTEM IMPLEMENTATION

### Three-Tier Memory Architecture

```python
"""
Memory system for trading agents
Short-term: Conversation history
Mid-term: Episodic memory in vector DB
Long-term: Semantic knowledge base
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import numpy as np
from dataclasses import dataclass, asdict
from enum import Enum

# Vector DB setup (Qdrant)
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct

# Embeddings
from sentence_transformers import SentenceTransformer

class MemoryType(Enum):
    SHORT_TERM = "short_term"
    EPISODIC = "episodic"
    SEMANTIC = "semantic"

@dataclass
class TradeRecord:
    """Individual trade record for episodic memory"""
    timestamp: str
    ticker: str
    side: str  # BUY or SELL
    quantity: int
    entry_price: float
    exit_price: Optional[float]
    pnl: Optional[float]
    market_regime: str
    reasoning: str
    outcome: str  # WIN, LOSS, NEUTRAL

class FinancialAgentMemory:
    """Multi-tier memory system for trading agents"""

    def __init__(self, qdrant_url: str = "localhost:6333"):
        # Short-term: In-memory conversation buffer
        self.conversation_buffer = []
        self.max_conversation_length = 20

        # Mid-term: Vector DB for episodic memory
        self.vector_client = QdrantClient(url=qdrant_url)
        self.embedding_model = SentenceTransformer('all-MiniLM-L6-v2')

        # Initialize Qdrant collection
        self.initialize_qdrant()

        # Long-term: Semantic memory (in-memory for MVP)
        self.semantic_memory = {
            "market_regimes": {},
            "strategy_performance": {},
            "correlations": {},
            "regulations": {},
            "learned_patterns": []
        }

    def initialize_qdrant(self):
        """Set up Qdrant collection for episodic memory"""

        collection_name = "trading_episodes"

        try:
            self.vector_client.recreate_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(
                    size=384,  # MiniLM embedding dimension
                    distance=Distance.COSINE
                )
            )
        except Exception as e:
            print(f"Qdrant collection setup: {e}")

        self.collection_name = collection_name

    def add_to_short_term(self, role: str, content: str):
        """Add message to conversation buffer"""

        self.conversation_buffer.append({
            "role": role,
            "content": content,
            "timestamp": datetime.now().isoformat()
        })

        # Keep buffer size bounded
        if len(self.conversation_buffer) > self.max_conversation_length:
            self.conversation_buffer.pop(0)

    def add_episodic_memory(self, trade: TradeRecord):
        """Store completed trade in episodic memory"""

        # Create summary
        summary = f"""
        Trade: {trade.ticker} {trade.side} {trade.quantity} shares
        Entry: ${trade.entry_price:.2f}
        Exit: ${trade.exit_price:.2f if trade.exit_price else 'N/A'}
        P&L: ${trade.pnl if trade.pnl else 'N/A'}
        Market Regime: {trade.market_regime}
        Reasoning: {trade.reasoning}
        Outcome: {trade.outcome}
        """

        # Embed the summary
        embedding = self.embedding_model.encode(summary)

        # Store in Qdrant with metadata
        point = PointStruct(
            id=int(datetime.now().timestamp() * 1000),  # Unique ID
            vector=embedding.tolist(),
            payload={
                "ticker": trade.ticker,
                "side": trade.side,
                "pnl": trade.pnl or 0.0,
                "market_regime": trade.market_regime,
                "outcome": trade.outcome,
                "timestamp": trade.timestamp,
                "reasoning": trade.reasoning,
                "entry_price": trade.entry_price,
                "exit_price": trade.exit_price or 0.0,
                "quantity": trade.quantity
            }
        )

        self.vector_client.upsert(
            collection_name=self.collection_name,
            points=[point]
        )

    def retrieve_similar_trades(self, query: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Find similar past trades using vector search"""

        query_embedding = self.embedding_model.encode(query)

        results = self.vector_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=limit
        )

        return [
            {
                "score": result.score,
                "trade": result.payload
            }
            for result in results
        ]

    def retrieve_by_regime(self, regime: str, limit: int = 5) -> List[Dict[str, Any]]:
        """Retrieve trades from specific market regime"""

        # Use Qdrant filtering
        from qdrant_client.models import Filter, FieldCondition, MatchValue

        results = self.vector_client.search(
            collection_name=self.collection_name,
            query_vector=[0] * 384,  # Dummy vector for filter-only search
            query_filter=Filter(
                must=[
                    FieldCondition(
                        key="market_regime",
                        match=MatchValue(value=regime)
                    )
                ]
            ),
            limit=limit
        )

        return [result.payload for result in results]

    def update_semantic_memory(self, key: str, value: Dict[str, Any]):
        """Update long-term semantic knowledge"""

        if key in self.semantic_memory:
            self.semantic_memory[key].update(value)
        else:
            self.semantic_memory[key] = value

    def get_semantic_memory(self, key: str) -> Optional[Dict[str, Any]]:
        """Retrieve semantic knowledge"""

        return self.semantic_memory.get(key)

    def get_conversation_context(self) -> str:
        """Get formatted conversation history for LLM"""

        return "\n".join([
            f"{msg['role']}: {msg['content']}"
            for msg in self.conversation_buffer
        ])

    def get_decision_context(self, ticker: str, market_regime: str) -> str:
        """Build decision context from all memory sources"""

        # Short-term: Recent conversation
        short_context = f"Recent conversation:\n{self.get_conversation_context()}"

        # Mid-term: Similar trades
        similar = self.retrieve_similar_trades(f"{ticker} {market_regime}")
        mid_context = f"\nSimilar past trades ({len(similar)} found):\n"
        for trade in similar:
            mid_context += f"  - {trade['trade']['ticker']}: {trade['trade']['outcome']} "
            mid_context += f"(P&L: ${trade['trade']['pnl']:.2f})\n"

        # Long-term: Semantic knowledge
        correlations = self.get_semantic_memory("correlations") or {}
        long_context = f"\nKnown correlations: {json.dumps(correlations, indent=2)}"

        return f"{short_context}\n{mid_context}\n{long_context}"

# Usage example
memory = FinancialAgentMemory()

# Record a trade
trade = TradeRecord(
    timestamp=datetime.now().isoformat(),
    ticker="AAPL",
    side="BUY",
    quantity=100,
    entry_price=150.50,
    exit_price=152.00,
    pnl=150.00,
    market_regime="bull",
    reasoning="Bullish breakout on earnings",
    outcome="WIN"
)

memory.add_episodic_memory(trade)

# Retrieve context for next decision
decision_context = memory.get_decision_context("AAPL", "bull")
print(decision_context)
```

---

## 3. RAG SYSTEM WITH HYBRID SEARCH

### Hybrid Search Implementation

```python
"""
RAG system with hybrid search (vector + keyword)
For retrieving financial data and documents
"""

from typing import List, Dict, Any, Tuple
from dataclasses import dataclass
import numpy as np

@dataclass
class RetrievedDocument:
    content: str
    source: str
    score: float
    rank: int
    metadata: Dict[str, Any]

class FinancialRAG:
    """Retrieve-Augmented Generation for financial data"""

    def __init__(self, qdrant_client, embedding_model):
        self.vector_client = qdrant_client
        self.embedding_model = embedding_model
        self.collection_name = "financial_documents"

    def ingest_document(self, doc_id: str, content: str, metadata: Dict[str, Any]):
        """Store document for later retrieval"""

        # Chunk large documents
        chunks = self._chunk_document(content, chunk_size=512)

        for i, chunk in enumerate(chunks):
            embedding = self.embedding_model.encode(chunk)

            from qdrant_client.models import PointStruct

            point = PointStruct(
                id=hash(f"{doc_id}_{i}") % (2**31),
                vector=embedding.tolist(),
                payload={
                    "doc_id": doc_id,
                    "chunk_index": i,
                    "content": chunk,
                    **metadata
                }
            )

            self.vector_client.upsert(
                collection_name=self.collection_name,
                points=[point]
            )

    def hybrid_search(
        self,
        query: str,
        filters: Dict[str, Any] = None,
        k: int = 5,
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4
    ) -> List[RetrievedDocument]:
        """
        Hybrid search combining vector + keyword search
        Uses Reciprocal Rank Fusion (RRF) for merging
        """

        # Vector search
        query_embedding = self.embedding_model.encode(query)
        vector_results = self.vector_client.search(
            collection_name=self.collection_name,
            query_vector=query_embedding.tolist(),
            limit=k * 2,  # Get more for ranking
            query_filter=self._build_filter(filters) if filters else None
        )

        vector_ranked = {
            i: {
                "score": result.score,
                "payload": result.payload,
                "rank": i + 1
            }
            for i, result in enumerate(vector_results)
        }

        # Keyword search (BM25-like using Qdrant)
        keyword_results = self._keyword_search(query, filters, limit=k * 2)
        keyword_ranked = {
            i: {
                "score": result.get("score", 1.0),
                "payload": result,
                "rank": i + 1
            }
            for i, result in enumerate(keyword_results)
        }

        # Merge using RRF
        merged = self._reciprocal_rank_fusion(
            vector_ranked,
            keyword_ranked,
            vector_weight=vector_weight,
            keyword_weight=keyword_weight
        )

        # Return top-k
        return [
            RetrievedDocument(
                content=item["payload"]["content"],
                source=item["payload"].get("source", "unknown"),
                score=item["rrf_score"],
                rank=item["rrf_rank"],
                metadata=item["payload"]
            )
            for item in sorted(merged, key=lambda x: x["rrf_score"], reverse=True)[:k]
        ]

    def _keyword_search(
        self,
        query: str,
        filters: Dict[str, Any],
        limit: int = 10
    ) -> List[Dict[str, Any]]:
        """Simple keyword search implementation"""

        # In production, use Qdrant's text search or Elasticsearch
        # For MVP, implement basic string matching

        query_terms = set(query.lower().split())

        # Scroll through collection and score documents
        from qdrant_client.models import Filter

        results = self.vector_client.scroll(
            collection_name=self.collection_name,
            limit=limit * 5,
            query_filter=self._build_filter(filters) if filters else None
        )

        scored = []
        for point, _ in results:
            content = point.payload.get("content", "").lower()
            score = sum(1 for term in query_terms if term in content) / len(query_terms)

            if score > 0:
                scored.append({
                    "score": score,
                    **point.payload
                })

        return sorted(scored, key=lambda x: x["score"], reverse=True)[:limit]

    def _reciprocal_rank_fusion(
        self,
        vector_results: Dict[int, Dict[str, Any]],
        keyword_results: Dict[int, Dict[str, Any]],
        vector_weight: float = 0.6,
        keyword_weight: float = 0.4
    ) -> List[Dict[str, Any]]:
        """
        Merge two ranked lists using Reciprocal Rank Fusion

        RRF Score = vector_weight * (1 / (k + vector_rank)) +
                    keyword_weight * (1 / (k + keyword_rank))
        """

        k = 60  # Constant for RRF formula

        # Extract unique documents
        all_docs = {}

        for rank, item in vector_results.items():
            doc_id = item["payload"].get("doc_id", rank)
            all_docs[doc_id] = {
                "payload": item["payload"],
                "vector_rank": item["rank"],
                "vector_score": item["score"]
            }

        for rank, item in keyword_results.items():
            doc_id = item["payload"].get("doc_id", rank)
            if doc_id not in all_docs:
                all_docs[doc_id] = {"payload": item["payload"]}
            all_docs[doc_id]["keyword_rank"] = item["rank"]
            all_docs[doc_id]["keyword_score"] = item["score"]

        # Calculate RRF scores
        merged = []
        for doc_id, item in all_docs.items():
            vector_rank = item.get("vector_rank", len(vector_results) + 1)
            keyword_rank = item.get("keyword_rank", len(keyword_results) + 1)

            rrf_score = (
                vector_weight * (1 / (k + vector_rank)) +
                keyword_weight * (1 / (k + keyword_rank))
            )

            merged.append({
                "doc_id": doc_id,
                "payload": item["payload"],
                "rrf_score": rrf_score,
                "rrf_rank": None  # Will be set after sorting
            })

        # Rank by RRF score
        merged = sorted(merged, key=lambda x: x["rrf_score"], reverse=True)
        for i, item in enumerate(merged):
            item["rrf_rank"] = i + 1

        return merged

    def _build_filter(self, filters: Dict[str, Any]):
        """Build Qdrant filter from metadata"""

        from qdrant_client.models import Filter, FieldCondition, MatchValue

        conditions = []
        for key, value in filters.items():
            conditions.append(
                FieldCondition(
                    key=key,
                    match=MatchValue(value=value)
                )
            )

        return Filter(must=conditions) if conditions else None

    def _chunk_document(self, content: str, chunk_size: int = 512) -> List[str]:
        """Split document into chunks"""

        words = content.split()
        chunks = []

        for i in range(0, len(words), chunk_size):
            chunk = " ".join(words[i:i + chunk_size])
            if chunk.strip():
                chunks.append(chunk)

        return chunks

# Usage
"""
rag = FinancialRAG(qdrant_client, embedding_model)

# Ingest financial documents
rag.ingest_document(
    doc_id="AAPL_10K_2024",
    content=apple_10k_content,
    metadata={
        "ticker": "AAPL",
        "doc_type": "10-K",
        "year": 2024,
        "source": "SEC"
    }
)

# Hybrid search
results = rag.hybrid_search(
    query="What are Apple's dividend policies?",
    filters={"ticker": "AAPL", "doc_type": "10-K"},
    k=5
)

# Use results in LLM prompt
context = "\n".join([r.content for r in results])
llm_prompt = f"Based on these financial documents:\n\n{context}\n\nAnswer: ..."
"""
```

---

## 4. GUARDRAILS & SAFETY LAYER

### Safety Guardrails Implementation

```python
"""
Safety guardrails for autonomous trading
Immutable, deterministic checks that cannot be overridden
"""

from datetime import datetime, time
from dataclasses import dataclass
from enum import Enum
from typing import Tuple, List
import json

class GuardrailLevel(Enum):
    CRITICAL = "critical"      # Block immediately
    WARNING = "warning"        # Alert but allow
    INFO = "info"             # Log only

@dataclass
class GuardrailViolation:
    level: GuardrailLevel
    rule: str
    reason: str
    trade: 'Trade'
    timestamp: str
    requires_approval: bool

@dataclass
class Trade:
    """Trading decision to be evaluated"""
    ticker: str
    side: str  # BUY or SELL
    quantity: int
    order_type: str  # MARKET, LIMIT, etc.
    limit_price: float = None
    user_id: str = None
    account_id: str = None

class SafetyGuardrails:
    """Immutable, deterministic safety checks"""

    def __init__(self):
        # Configuration (should be immutable in production)
        self.config = {
            "max_trade_size_usd": 100_000,
            "max_daily_trades": 20,
            "max_position_concentration": 0.10,  # 10%
            "human_approval_threshold": 50_000,
            "restricted_hours_start": "16:00",
            "restricted_hours_end": "09:30",
            "approved_asset_classes": ["stocks", "etfs"],
            "sector_rotation_limit": 0.05,
            "pattern_day_trader_rule": True
        }

        # Trading history for rate limiting
        self.trade_history = []
        self.violation_log = []

    def validate_trade(self, trade: Trade) -> Tuple[bool, List[GuardrailViolation]]:
        """
        Validate trade against all safety guardrails
        Returns: (is_valid, violations)
        """

        violations = []

        # Check 1: Size limit (absolute)
        size_violation = self._check_trade_size(trade)
        if size_violation:
            violations.append(size_violation)

        # Check 2: Daily rate limit
        daily_violation = self._check_daily_limit(trade)
        if daily_violation:
            violations.append(daily_violation)

        # Check 3: Position concentration
        concentration_violation = self._check_concentration(trade)
        if concentration_violation:
            violations.append(concentration_violation)

        # Check 4: Trading hours
        hours_violation = self._check_trading_hours(trade)
        if hours_violation:
            violations.append(hours_violation)

        # Check 5: Asset class approval
        asset_violation = self._check_approved_asset(trade)
        if asset_violation:
            violations.append(asset_violation)

        # Check 6: Pattern day trader rules
        pdt_violation = self._check_pdt_rules(trade)
        if pdt_violation:
            violations.append(pdt_violation)

        # Critical violations block trade
        critical_violations = [v for v in violations if v.level == GuardrailLevel.CRITICAL]
        is_valid = len(critical_violations) == 0

        # Log all violations
        for violation in violations:
            self._log_violation(violation)

        return is_valid, violations

    def _check_trade_size(self, trade: Trade) -> GuardrailViolation:
        """Absolute size limit (cannot be overridden)"""

        trade_value = trade.quantity * get_current_price(trade.ticker)

        if trade_value > self.config["max_trade_size_usd"]:
            return GuardrailViolation(
                level=GuardrailLevel.CRITICAL,
                rule="MAX_TRADE_SIZE",
                reason=f"Trade size ${trade_value:,.0f} exceeds max ${self.config['max_trade_size_usd']:,}",
                trade=trade,
                timestamp=datetime.now().isoformat(),
                requires_approval=False
            )

        return None

    def _check_daily_limit(self, trade: Trade) -> GuardrailViolation:
        """Rate limit on daily trades"""

        today = datetime.now().date()
        trades_today = sum(
            1 for t in self.trade_history
            if datetime.fromisoformat(t['timestamp']).date() == today
        )

        if trades_today >= self.config["max_daily_trades"]:
            return GuardrailViolation(
                level=GuardrailLevel.CRITICAL,
                rule="DAILY_LIMIT",
                reason=f"Daily trade limit {self.config['max_daily_trades']} reached",
                trade=trade,
                timestamp=datetime.now().isoformat(),
                requires_approval=False
            )

        return None

    def _check_concentration(self, trade: Trade) -> GuardrailViolation:
        """Position concentration limit"""

        current_position_value = get_position_value(trade.account_id, trade.ticker)
        portfolio_value = get_portfolio_value(trade.account_id)

        trade_value = trade.quantity * get_current_price(trade.ticker)
        new_position_value = current_position_value + trade_value

        position_pct = new_position_value / portfolio_value

        if position_pct > self.config["max_position_concentration"]:
            return GuardrailViolation(
                level=GuardrailLevel.CRITICAL,
                rule="CONCENTRATION_LIMIT",
                reason=f"Position would be {position_pct:.1%}, max {self.config['max_position_concentration']:.1%}",
                trade=trade,
                timestamp=datetime.now().isoformat(),
                requires_approval=True
            )

        return None

    def _check_trading_hours(self, trade: Trade) -> GuardrailViolation:
        """Restrict trading outside market hours"""

        current_time = datetime.now().time()
        start = datetime.strptime(self.config["restricted_hours_start"], "%H:%M").time()
        end = datetime.strptime(self.config["restricted_hours_end"], "%H:%M").time()

        if start <= current_time <= end:  # After hours
            return GuardrailViolation(
                level=GuardrailLevel.WARNING,
                rule="AFTER_HOURS",
                reason=f"Trade submitted outside market hours",
                trade=trade,
                timestamp=datetime.now().isoformat(),
                requires_approval=True
            )

        return None

    def _check_approved_asset(self, trade: Trade) -> GuardrailViolation:
        """Ensure only approved assets"""

        asset_class = get_asset_class(trade.ticker)

        if asset_class not in self.config["approved_asset_classes"]:
            return GuardrailViolation(
                level=GuardrailLevel.CRITICAL,
                rule="ASSET_CLASS_RESTRICTION",
                reason=f"Asset class '{asset_class}' not approved",
                trade=trade,
                timestamp=datetime.now().isoformat(),
                requires_approval=False
            )

        return None

    def _check_pdt_rules(self, trade: Trade) -> GuardrailViolation:
        """Check pattern day trader rules"""

        if not self.config["pattern_day_trader_rule"]:
            return None

        today = datetime.now().date()
        round_trips = count_round_trips(trade.account_id, days=5)

        if round_trips >= 3:
            return GuardrailViolation(
                level=GuardrailLevel.WARNING,
                rule="PDT_RULE",
                reason=f"Account has {round_trips} round trips in last 5 days",
                trade=trade,
                timestamp=datetime.now().isoformat(),
                requires_approval=True
            )

        return None

    def _log_violation(self, violation: GuardrailViolation):
        """Immutable violation log for audit trail"""

        log_entry = {
            "id": str(datetime.now().timestamp()),
            "level": violation.level.value,
            "rule": violation.rule,
            "reason": violation.reason,
            "trade": {
                "ticker": violation.trade.ticker,
                "side": violation.trade.side,
                "quantity": violation.trade.quantity
            },
            "timestamp": violation.timestamp,
            "requires_approval": violation.requires_approval
        }

        self.violation_log.append(log_entry)

        # In production: write to immutable ledger (blockchain, append-only DB, etc.)
        print(f"GUARDRAIL VIOLATION: {log_entry}")

    def log_trade_execution(self, trade: Trade, execution_id: str):
        """Log executed trade for rate limiting"""

        self.trade_history.append({
            "execution_id": execution_id,
            "ticker": trade.ticker,
            "side": trade.side,
            "quantity": trade.quantity,
            "timestamp": datetime.now().isoformat()
        })

# Helper functions (implementations would vary)
def get_current_price(ticker: str) -> float:
    """Get current market price"""
    return 150.00  # Placeholder

def get_position_value(account_id: str, ticker: str) -> float:
    """Get current position value"""
    return 10000.00  # Placeholder

def get_portfolio_value(account_id: str) -> float:
    """Get total portfolio value"""
    return 500000.00  # Placeholder

def get_asset_class(ticker: str) -> str:
    """Get asset class of ticker"""
    return "stocks"  # Placeholder

def count_round_trips(account_id: str, days: int) -> int:
    """Count round trips in last N days"""
    return 0  # Placeholder

# Usage
guardrails = SafetyGuardrails()

trade = Trade(
    ticker="AAPL",
    side="BUY",
    quantity=1000,
    order_type="MARKET",
    user_id="user_123",
    account_id="account_456"
)

is_valid, violations = guardrails.validate_trade(trade)

if is_valid:
    print("Trade passed all safety checks")
else:
    print(f"Trade blocked by {len(violations)} violations")
    for v in violations:
        print(f"  - {v.rule}: {v.reason}")
```

---

## 5. OBSERVABILITY & MONITORING

### MELT Framework Implementation

```python
"""
MELT Observability Framework for AI Agents
Metrics, Events, Logs, Traces
"""

from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Dict, Any, List
import json
from enum import Enum
import time

# OpenTelemetry imports
from opentelemetry import trace, metrics
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from opentelemetry.sdk.resources import SERVICE_NAME, Resource
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor

class EventType(Enum):
    TRADE_EXECUTED = "trade_executed"
    POSITION_LIQUIDATED = "position_liquidated"
    RISK_BREACH = "risk_breach"
    COMPLIANCE_CHECK = "compliance_check"
    GUARDRAIL_VIOLATION = "guardrail_violation"
    HUMAN_ESCALATION = "human_escalation"
    MARKET_REGIME_CHANGE = "market_regime_change"
    AGENT_ERROR = "agent_error"

@dataclass
class MELTEvent:
    """Base event for observability"""
    timestamp: str
    event_type: EventType
    agent_name: str
    user_id: str
    metadata: Dict[str, Any]

    def to_json(self) -> str:
        return json.dumps({
            "timestamp": self.timestamp,
            "event_type": self.event_type.value,
            "agent_name": self.agent_name,
            "user_id": self.user_id,
            "metadata": self.metadata
        })

class ObservabilityManager:
    """Comprehensive observability for trading agents"""

    def __init__(self, service_name: str = "trading-agent"):
        # OpenTelemetry setup
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )

        trace.set_tracer_provider(
            TracerProvider(
                resource=Resource.create({SERVICE_NAME: service_name})
            )
        )

        trace.get_tracer_provider().add_span_processor(
            BatchSpanProcessor(jaeger_exporter)
        )

        self.tracer = trace.get_tracer(__name__)
        self.metrics_data = []
        self.events_log = []
        self.traces = {}

    def record_metric(
        self,
        metric_name: str,
        value: float,
        attributes: Dict[str, str] = None
    ):
        """Record a metric (M in MELT)"""

        metric_entry = {
            "timestamp": datetime.now().isoformat(),
            "name": metric_name,
            "value": value,
            "attributes": attributes or {}
        }

        self.metrics_data.append(metric_entry)

        # Common financial metrics
        if "tokens" in metric_name:
            print(f"Token usage: {value}")
        elif "latency" in metric_name:
            print(f"Latency (ms): {value}")
        elif "trade" in metric_name:
            print(f"Trade metric ({metric_name}): {value}")

    def record_event(self, event: MELTEvent):
        """Record an event (E in MELT)"""

        self.events_log.append({
            "timestamp": event.timestamp,
            "event_type": event.event_type.value,
            "agent_name": event.agent_name,
            "user_id": event.user_id,
            "metadata": event.metadata
        })

        print(f"EVENT [{event.event_type.value}]: {event.metadata}")

    def start_trace(self, span_name: str, attributes: Dict[str, Any] = None) -> Any:
        """Start a trace span (T in MELT)"""

        span = self.tracer.start_span(span_name)

        if attributes:
            for key, value in attributes.items():
                span.set_attribute(key, value)

        return span

    def record_log(
        self,
        level: str,
        message: str,
        context: Dict[str, Any] = None
    ):
        """Record a log entry (L in MELT)"""

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "context": context or {}
        }

        # In production: send to logging service (ELK, DataDog, etc.)
        print(f"[{level}] {message}")
        if context:
            print(f"Context: {json.dumps(context, indent=2)}")

    def trace_trade_execution(self, trade: Dict[str, Any]):
        """Full trace of a trade execution"""

        with self.start_trace("execute_trade", attributes={
            "ticker": trade["ticker"],
            "side": trade["side"],
            "quantity": trade["quantity"]
        }) as root_span:

            # Trace 1: Risk assessment
            start_time = time.time()
            with self.start_trace("risk_assessment") as risk_span:
                risk_result = assess_risk(trade)
                latency = (time.time() - start_time) * 1000
                self.record_metric("risk_assessment_latency_ms", latency)
                risk_span.set_attribute("risk_score", risk_result["score"])

            # Trace 2: Compliance check
            start_time = time.time()
            with self.start_trace("compliance_check") as comp_span:
                compliance_result = check_compliance(trade)
                latency = (time.time() - start_time) * 1000
                self.record_metric("compliance_latency_ms", latency)
                comp_span.set_attribute("compliant", compliance_result["passed"])

            # Trace 3: Broker API call
            start_time = time.time()
            with self.start_trace("broker_api_call") as broker_span:
                execution_result = execute_with_broker(trade)
                latency = (time.time() - start_time) * 1000
                self.record_metric("broker_latency_ms", latency)
                broker_span.set_attribute("order_id", execution_result["order_id"])

            # Trace 4: Update memory
            start_time = time.time()
            with self.start_trace("memory_update") as mem_span:
                update_memory(trade, execution_result)
                latency = (time.time() - start_time) * 1000
                self.record_metric("memory_update_latency_ms", latency)

            # Record overall metrics
            total_latency = (time.time() - start_time) * 1000
            self.record_metric("total_execution_latency_ms", total_latency)

            # Record event
            event = MELTEvent(
                timestamp=datetime.now().isoformat(),
                event_type=EventType.TRADE_EXECUTED,
                agent_name="executor_agent",
                user_id=trade.get("user_id", "unknown"),
                metadata={
                    "ticker": trade["ticker"],
                    "order_id": execution_result["order_id"],
                    "status": "success"
                }
            )
            self.record_event(event)

    def report_alerts(self, alert_conditions: List[Dict[str, Any]]):
        """Monitor and report alerts"""

        for condition in alert_conditions:
            if condition["triggered"]:
                self.record_event(MELTEvent(
                    timestamp=datetime.now().isoformat(),
                    event_type=EventType.RISK_BREACH,
                    agent_name="monitor_agent",
                    user_id=condition.get("user_id", "system"),
                    metadata={
                        "alert": condition["name"],
                        "threshold": condition["threshold"],
                        "current_value": condition["value"],
                        "severity": condition["severity"]
                    }
                ))

                # Record metric
                self.record_metric(
                    f"alert_{condition['name']}",
                    condition["value"],
                    {"threshold": str(condition["threshold"])}
                )

    def export_metrics(self) -> Dict[str, Any]:
        """Export collected metrics"""

        return {
            "timestamp": datetime.now().isoformat(),
            "metrics": self.metrics_data,
            "events": self.events_log,
            "total_trades": len([e for e in self.events_log if e["event_type"] == "trade_executed"]),
            "total_violations": len([e for e in self.events_log if e["event_type"] == "guardrail_violation"])
        }

# Helper functions
def assess_risk(trade: Dict[str, Any]) -> Dict[str, Any]:
    return {"score": 35.5}  # Placeholder

def check_compliance(trade: Dict[str, Any]) -> Dict[str, Any]:
    return {"passed": True}  # Placeholder

def execute_with_broker(trade: Dict[str, Any]) -> Dict[str, Any]:
    return {"order_id": f"ORD_{int(time.time())}", "status": "filled"}  # Placeholder

def update_memory(trade: Dict[str, Any], result: Dict[str, Any]):
    pass  # Placeholder

# Usage
observability = ObservabilityManager(service_name="trading-agent")

# Simulate trade execution with observability
trade = {
    "ticker": "AAPL",
    "side": "BUY",
    "quantity": 100,
    "user_id": "user_123"
}

observability.trace_trade_execution(trade)

# Check metrics
print(observability.export_metrics())
```

---

## 6. REINFORCEMENT LEARNING INTEGRATION

### RL Trading Agent

```python
"""
Reinforcement Learning for trading
DQN agent learning to optimize trade timing
"""

import numpy as np
from typing import Tuple, List
from dataclasses import dataclass

@dataclass
class TradingState:
    """Market state for RL agent"""
    price_history: List[float]  # Last 20 prices
    rsi: float
    macd: float
    volume: float
    position: str  # LONG, SHORT, FLAT
    pnl_percent: float

class DQNTradingAgent:
    """Deep Q-Network for trading"""

    def __init__(self, learning_rate: float = 0.01, gamma: float = 0.95):
        self.learning_rate = learning_rate
        self.gamma = gamma  # Discount factor
        self.epsilon = 1.0   # Exploration rate
        self.epsilon_decay = 0.995

        # Action space: {0: BUY, 1: HOLD, 2: SELL}
        self.action_space = [0, 1, 2]

        # Simple Q-table (in production: use neural network)
        self.q_table = {}

    def get_state_key(self, state: TradingState) -> str:
        """Convert state to hashable key"""

        # Discretize continuous values
        rsi_bucket = int(state.rsi / 10)
        pnl_bucket = int(state.pnl_percent / 5)

        return f"rsi_{rsi_bucket}_pnl_{pnl_bucket}_pos_{state.position}"

    def select_action(self, state: TradingState, training: bool = True) -> int:
        """Select action using epsilon-greedy strategy"""

        state_key = self.get_state_key(state)

        if training and np.random.random() < self.epsilon:
            # Exploration: random action
            return np.random.choice(self.action_space)
        else:
            # Exploitation: best known action
            if state_key not in self.q_table:
                self.q_table[state_key] = {a: 0.0 for a in self.action_space}

            q_values = self.q_table[state_key]
            return max(self.action_space, key=lambda a: q_values[a])

    def update_q_value(
        self,
        state: TradingState,
        action: int,
        reward: float,
        next_state: TradingState
    ):
        """Update Q-value using Bellman equation"""

        state_key = self.get_state_key(state)
        next_state_key = self.get_state_key(next_state)

        # Initialize Q-table entries if needed
        if state_key not in self.q_table:
            self.q_table[state_key] = {a: 0.0 for a in self.action_space}

        if next_state_key not in self.q_table:
            self.q_table[next_state_key] = {a: 0.0 for a in self.action_space}

        # Current Q-value
        current_q = self.q_table[state_key][action]

        # Maximum Q-value for next state
        max_next_q = max(
            self.q_table[next_state_key][a] for a in self.action_space
        )

        # Bellman update
        new_q = current_q + self.learning_rate * (
            reward + self.gamma * max_next_q - current_q
        )

        self.q_table[state_key][action] = new_q

    def train_on_episode(self, market_data: List[Dict[str, float]]):
        """Train on one episode of market data"""

        for i in range(len(market_data) - 1):
            # Build state
            current_data = market_data[i]
            state = TradingState(
                price_history=current_data["prices"],
                rsi=current_data["rsi"],
                macd=current_data["macd"],
                volume=current_data["volume"],
                position="FLAT",  # Simplified for example
                pnl_percent=current_data.get("pnl_percent", 0)
            )

            # Select action
            action = self.select_action(state, training=True)

            # Execute action and get reward
            price_change = market_data[i+1]["price"] - market_data[i]["price"]

            # Reward function: profit from action
            if action == 0:  # BUY
                reward = price_change
            elif action == 2:  # SELL
                reward = -price_change
            else:  # HOLD
                reward = 0

            # Build next state
            next_data = market_data[i + 1]
            next_state = TradingState(
                price_history=next_data["prices"],
                rsi=next_data["rsi"],
                macd=next_data["macd"],
                volume=next_data["volume"],
                position="FLAT",
                pnl_percent=next_data.get("pnl_percent", 0)
            )

            # Update Q-value
            self.update_q_value(state, action, reward, next_state)

        # Decay exploration rate
        self.epsilon *= self.epsilon_decay

    def predict(self, state: TradingState) -> int:
        """Make trading decision on new data"""

        return self.select_action(state, training=False)

# Usage and integration with financial agent
"""
# Initialize RL agent
rl_agent = DQNTradingAgent()

# Train on historical data
historical_data = load_historical_prices("AAPL", days=252)
for epoch in range(10):
    rl_agent.train_on_episode(historical_data)
    print(f"Epoch {epoch}, Epsilon: {rl_agent.epsilon:.3f}")

# Use in trading agent
class RLAugmentedTradingAgent:
    def __init__(self, rl_agent: DQNTradingAgent):
        self.rl_agent = rl_agent

    def make_decision(self, market_data: Dict[str, float]) -> str:
        '''Combine RL with LLM analysis'''

        # Get RL recommendation
        state = build_state(market_data)
        rl_action = self.rl_agent.predict(state)

        # Map action to recommendation
        action_names = {0: "BUY", 1: "HOLD", 2: "SELL"}
        rl_recommendation = action_names[rl_action]

        # Get LLM analysis
        llm_recommendation = get_llm_analysis(market_data)

        # Combine both signals
        combined_decision = combine_signals(rl_recommendation, llm_recommendation)

        return combined_decision

    def learn_from_trade(self, trade_result: Dict[str, Any]):
        '''Update RL agent after real trade'''

        state = build_state(trade_result['initial_state'])
        action = trade_result['action']
        reward = trade_result['pnl']
        next_state = build_state(trade_result['final_state'])

        self.rl_agent.update_q_value(state, action, reward, next_state)
```

---

## NEXT STEPS

1. **Set Up Infrastructure**
   - Deploy Qdrant for episodic memory
   - Configure PostgreSQL with pgvector
   - Set up Langfuse for observability

2. **Implement Core Loop**
   - Build basic LangGraph agent
   - Integrate memory system
   - Add guardrails

3. **Add Learning**
   - Implement RL training loop
   - Connect episodic memory
   - Enable continuous updates

4. **Monitor & Optimize**
   - Deploy observability
   - Monitor guardrail violations
   - Iterate on safety rules

---

**References**:
- LangGraph Docs: https://langchain-ai.github.io/langgraph/
- Qdrant Docs: https://qdrant.tech/documentation/
- OpenTelemetry: https://opentelemetry.io/
