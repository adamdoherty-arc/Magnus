# Conversational AI Implementation Patterns: Code Examples and Architecture

**Purpose:** Practical code patterns and architecture examples based on 2024-2025 Medium research
**Language:** Python (primary), JavaScript/TypeScript (where relevant)
**Frameworks:** LangChain, LangGraph, FastAPI

---

## 1. BASIC RAG IMPLEMENTATION PATTERN

### 1.1 Simple RAG Pipeline (LangChain)

```python
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.schema.runnable import RunnablePassthrough

# Initialize components
embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
vectorstore = Weaviate.from_existing_index(
    embedding=embeddings,
    index_name="documents",
    weaviate_url="http://localhost:8080"
)

llm = ChatOpenAI(model="gpt-4", temperature=0.7)

# Create RAG chain
template = """Use the following context to answer the question.
If you cannot find the answer in the context, say "I don't know".

Context: {context}

Question: {question}

Answer:"""

prompt = ChatPromptTemplate.from_template(template)

# Build retriever
retriever = vectorstore.as_retriever(
    search_kwargs={"k": 4}  # Retrieve top 4 documents
)

def format_docs(docs):
    return "\n\n".join(doc.page_content for doc in docs)

# Chain everything together
rag_chain = (
    {
        "context": retriever | RunnablePassthrough(format_docs),
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
)

# Use it
response = rag_chain.invoke("What is RAG?")
print(response.content)
```

### 1.2 RAG with Fact-Checking Layer

```python
from langchain.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage

class FactCheckingRAG:
    def __init__(self, retriever, llm):
        self.retriever = retriever
        self.llm = llm

    def retrieve_and_answer(self, query: str):
        # Step 1: Retrieve context
        docs = self.retriever.get_relevant_documents(query)
        context = "\n\n".join([d.page_content for d in docs])

        # Step 2: Generate answer with context
        answer_prompt = f"""Answer based on this context:
        {context}

        Question: {query}"""

        answer = self.llm(answer_prompt)

        # Step 3: Fact-check against context
        fact_check_prompt = f"""Check if this answer is grounded in the provided context.

        Context: {context}

        Answer: {answer}

        For each claim in the answer, indicate:
        1. Is this explicitly stated in context? (YES/NO)
        2. Is this implied in context? (YES/NO)
        3. Is this outside context? (YES/NO)

        Provide your assessment."""

        fact_check = self.llm(fact_check_prompt)

        # Step 4: Extract confidence score
        confidence_prompt = f"""Based on the fact-checking, give a confidence score 0-100 for this answer.

        Fact-check result: {fact_check}

        Score:"""

        confidence = int(self.llm(confidence_prompt).strip())

        return {
            "answer": answer,
            "context": context,
            "fact_check": fact_check,
            "confidence": confidence,
            "should_escalate": confidence < 70
        }

# Usage
rag = FactCheckingRAG(retriever, llm)
result = rag.retrieve_and_answer("What is our return policy?")

if result["should_escalate"]:
    print(f"Low confidence ({result['confidence']}), escalating to human")
else:
    print(f"High confidence answer: {result['answer']}")
```

### 1.3 Hybrid RAG (Semantic + Keyword)

```python
from langchain.retrievers import BM25Retriever, EnsembleRetriever
from langchain.vectorstores import Weaviate
from langchain.embeddings import OpenAIEmbeddings

# Create vector store retriever (semantic search)
embeddings = OpenAIEmbeddings()
vectorstore = Weaviate.from_documents(
    documents,
    embeddings,
    index_name="hybrid_search"
)
semantic_retriever = vectorstore.as_retriever(
    search_kwargs={"k": 3}
)

# Create BM25 retriever (keyword search)
keyword_retriever = BM25Retriever.from_documents(documents)

# Combine using ensemble
ensemble_retriever = EnsembleRetriever(
    retrievers=[semantic_retriever, keyword_retriever],
    weights=[0.6, 0.4]  # 60% semantic, 40% keyword
)

# Use in RAG chain
rag_chain = (
    {
        "context": ensemble_retriever | format_docs,
        "question": RunnablePassthrough()
    }
    | prompt
    | llm
)
```

---

## 2. MEMORY AND PERSONALIZATION PATTERNS

### 2.1 Conversation Memory with Summarization

```python
from langchain.memory import ConversationSummaryBufferMemory
from langchain.chat_models import ChatOpenAI

# Initialize memory with automatic summarization
memory = ConversationSummaryBufferMemory(
    llm=ChatOpenAI(),
    max_token_limit=1000,  # Keep summarized history under 1000 tokens
    buffer="Summary of conversation so far:\n",
    human_prefix="User",
    ai_prefix="Assistant"
)

# Create conversation chain
from langchain.chains import ConversationChain

conversation = ConversationChain(
    llm=ChatOpenAI(temperature=0.7),
    memory=memory,
    verbose=True
)

# Use in conversation
response1 = conversation.run("Hi! My name is Alice and I'm interested in mutual funds.")
response2 = conversation.run("Can you recommend something for long-term growth?")
response3 = conversation.run("What was my name again?")  # Should remember Alice

print(memory.buffer)  # See summarized history
```

### 2.2 User Profile-Based Personalization

```python
from typing import Dict, List
import json

class UserProfileManager:
    def __init__(self, db_connection):
        self.db = db_connection

    def get_user_profile(self, user_id: str) -> Dict:
        """Fetch user preferences, history, and traits"""
        query = """
        SELECT
            user_id,
            name,
            preferences,
            interaction_count,
            favorite_topics,
            communication_style,
            last_interaction
        FROM user_profiles
        WHERE user_id = %s
        """
        return self.db.fetchone(query, (user_id,))

    def build_context_prompt(self, user_id: str, query: str) -> str:
        """Build personalized system prompt based on user profile"""
        profile = self.get_user_profile(user_id)

        context = f"""You are a helpful financial assistant.

User Profile:
- Name: {profile['name']}
- Communication Style: {profile['communication_style']}
- Preferred Topics: {profile['favorite_topics']}
- Interaction History: {profile['interaction_count']} previous conversations

Personalization Notes:
- Use the user's name when appropriate
- Prefer explaining topics in their preferred style
- Reference their past interests when relevant
- Adapt complexity to their knowledge level

User Query: {query}"""

        return context

    def update_preferences(self, user_id: str, interaction_feedback: Dict):
        """Learn from user interactions"""
        update_query = """
        UPDATE user_profiles
        SET interaction_count = interaction_count + 1,
            last_interaction = NOW(),
            preferences = %s
        WHERE user_id = %s
        """
        self.db.execute(
            update_query,
            (json.dumps(interaction_feedback), user_id)
        )

# Usage in conversation
profile_manager = UserProfileManager(db)

def personalized_response(user_id: str, query: str):
    context_prompt = profile_manager.build_context_prompt(user_id, query)

    response = llm.invoke(context_prompt)

    # Track this interaction for learning
    feedback = {
        "query_type": "financial_question",
        "response_helpful": True,
        "topics_mentioned": ["stocks", "diversification"]
    }
    profile_manager.update_preferences(user_id, feedback)

    return response
```

### 2.3 Multi-Tier Memory System (Best of 2025)

```python
from datetime import datetime, timedelta
from langchain.vectorstores import Weaviate

class HybridMemorySystem:
    """
    Combines:
    - Recent context (buffer window)
    - Summarized history (SQL)
    - Long-term facts (vector DB)
    """

    def __init__(self, db, vector_db):
        self.db = db
        self.vector_db = vector_db
        self.recent_window_size = 5  # Keep last 5 turns

    def get_conversation_context(self, user_id: str, conversation_id: str) -> str:
        """Build complete context from all memory tiers"""

        # Tier 1: Recent messages (buffer window)
        recent = self.get_recent_messages(user_id, conversation_id)
        recent_context = self._format_messages(recent)

        # Tier 2: Session summary
        summary = self.get_session_summary(conversation_id)

        # Tier 3: Long-term user facts
        facts = self.get_long_term_facts(user_id)
        facts_context = self._format_facts(facts)

        complete_context = f"""
Recent Conversation:
{recent_context}

Session Summary:
{summary}

User Profile:
{facts_context}
"""
        return complete_context

    def get_recent_messages(self, user_id: str, conv_id: str, window: int = None):
        window = window or self.recent_window_size
        query = """
        SELECT message, sender, timestamp
        FROM messages
        WHERE user_id = %s AND conversation_id = %s
        ORDER BY timestamp DESC
        LIMIT %s
        """
        return self.db.fetchall(query, (user_id, conv_id, window))

    def get_session_summary(self, conversation_id: str) -> str:
        """Fetch or generate session summary"""
        query = "SELECT summary FROM conversations WHERE id = %s"
        result = self.db.fetchone(query, (conversation_id,))
        return result['summary'] if result else "No summary yet"

    def get_long_term_facts(self, user_id: str) -> List[Dict]:
        """Retrieve semantic memory from vector DB"""
        query = f"user_id={user_id} AND importance>0.7"
        facts = self.vector_db.similarity_search(query, k=5)
        return facts

    def store_fact(self, user_id: str, fact: str, importance: float):
        """Store important fact in long-term memory"""
        embedding = embed_text(fact)
        self.vector_db.add_documents([{
            "content": fact,
            "user_id": user_id,
            "importance": importance,
            "timestamp": datetime.now(),
            "embedding": embedding
        }])

    def _format_messages(self, messages: List) -> str:
        """Format message history for context"""
        formatted = []
        for msg in reversed(messages):  # Reverse to show chronologically
            formatted.append(f"{msg['sender']}: {msg['message']}")
        return "\n".join(formatted)

    def _format_facts(self, facts: List) -> str:
        """Format facts for context"""
        return "\n".join([f"- {fact.page_content}" for fact in facts])

# Usage
memory_system = HybridMemorySystem(db, vector_db)

context = memory_system.get_conversation_context(
    user_id="user123",
    conversation_id="conv456"
)

# In response generation
response = llm.invoke(f"User context:\n{context}\n\nUser: {query}")

# Learn from conversation
memory_system.store_fact(
    user_id="user123",
    fact="User prefers growth stocks over dividend stocks",
    importance=0.9
)
```

---

## 3. MULTI-AGENT PATTERNS

### 3.1 Simple Supervisor-Worker Pattern

```python
from langchain.agents import Tool, initialize_agent, AgentType
from langchain.chat_models import ChatOpenAI
from langchain.chains import LLMChain
from langchain.prompts import ChatPromptTemplate

# Define specialist agents
def portfolio_analyzer(query: str) -> str:
    """Analyze portfolio composition and performance"""
    # Complex portfolio analysis logic
    return f"Portfolio analysis: {query}"

def market_researcher(query: str) -> str:
    """Research market conditions and trends"""
    # Market research logic
    return f"Market research: {query}"

def risk_assessor(query: str) -> str:
    """Assess portfolio risk metrics"""
    # Risk assessment logic
    return f"Risk assessment: {query}"

# Create tools for supervisor
tools = [
    Tool(
        name="portfolio_analyzer",
        func=portfolio_analyzer,
        description="Analyze portfolio composition and returns"
    ),
    Tool(
        name="market_researcher",
        func=market_researcher,
        description="Research current market conditions"
    ),
    Tool(
        name="risk_assessor",
        func=risk_assessor,
        description="Assess portfolio risk metrics"
    )
]

# Create supervisor agent
llm = ChatOpenAI(model="gpt-4", temperature=0)
supervisor_agent = initialize_agent(
    tools,
    llm,
    agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
    verbose=True,
    agent_kwargs={
        "prefix": """You are a financial advisor supervisor.
You have access to specialist agents:
1. Portfolio Analyzer - for portfolio analysis
2. Market Researcher - for market research
3. Risk Assessor - for risk analysis

Coordinate between agents to provide comprehensive financial advice.
Use the most appropriate agent(s) for each task."""
    }
)

# Use supervisor
result = supervisor_agent.run(
    "Should I rebalance my portfolio given current market conditions?"
)
```

### 3.2 LangGraph Multi-Agent Orchestration

```python
from langgraph.graph import StateGraph, END
from langchain.schema import HumanMessage, AIMessage
from typing import TypedDict, List

class AgentState(TypedDict):
    messages: List
    current_agent: str
    analysis_results: dict
    user_query: str

# Define agent nodes
def portfolio_analysis_node(state: AgentState):
    """Portfolio analysis agent"""
    messages = state["messages"]
    query = state["user_query"]

    # Portfolio analysis logic
    analysis = llm.invoke(f"Analyze portfolio: {query}")

    return {
        **state,
        "messages": messages + [AIMessage(content=str(analysis))],
        "analysis_results": {**state["analysis_results"], "portfolio": str(analysis)}
    }

def market_analysis_node(state: AgentState):
    """Market analysis agent"""
    messages = state["messages"]
    query = state["user_query"]

    # Market analysis logic
    analysis = llm.invoke(f"Analyze market for: {query}")

    return {
        **state,
        "messages": messages + [AIMessage(content=str(analysis))],
        "analysis_results": {**state["analysis_results"], "market": str(analysis)}
    }

def recommendation_node(state: AgentState):
    """Final recommendation based on analysis"""
    analysis_results = state["analysis_results"]

    # Synthesize recommendations
    prompt = f"""Based on the analysis:
Portfolio: {analysis_results.get('portfolio', '')}
Market: {analysis_results.get('market', '')}

Provide a recommendation."""

    recommendation = llm.invoke(prompt)

    return {
        **state,
        "messages": state["messages"] + [AIMessage(content=str(recommendation))],
        "final_recommendation": str(recommendation)
    }

def route_agents(state: AgentState) -> str:
    """Determine which agents to use"""
    query = state["user_query"].lower()

    if any(word in query for word in ["portfolio", "allocation", "rebalance"]):
        return "portfolio_analysis"
    elif any(word in query for word in ["market", "economy", "rates"]):
        return "market_analysis"
    else:
        return "recommendation"

# Build graph
workflow = StateGraph(AgentState)

# Add nodes
workflow.add_node("portfolio_analysis", portfolio_analysis_node)
workflow.add_node("market_analysis", market_analysis_node)
workflow.add_node("recommendation", recommendation_node)

# Add edges
workflow.add_conditional_edges(
    "START",
    route_agents,
    {
        "portfolio_analysis": "portfolio_analysis",
        "market_analysis": "market_analysis",
        "recommendation": "recommendation"
    }
)

workflow.add_edge("portfolio_analysis", "recommendation")
workflow.add_edge("market_analysis", "recommendation")
workflow.add_edge("recommendation", END)

# Compile and run
app = workflow.compile()

initial_state = {
    "messages": [],
    "current_agent": None,
    "analysis_results": {},
    "user_query": "Should I rebalance my portfolio?"
}

result = app.invoke(initial_state)
print(result["final_recommendation"])
```

### 3.3 Jury Pattern (Debate for Accuracy)

```python
from concurrent.futures import ThreadPoolExecutor
from typing import List

class JuryVoting:
    """Multiple agents debate and vote on answer"""

    def __init__(self, num_agents: int = 3):
        self.num_agents = num_agents
        self.agents = [
            ChatOpenAI(model="gpt-4", temperature=i/10)
            for i in range(num_agents)
        ]

    def get_agent_response(self, agent_idx: int, query: str, context: str) -> str:
        """Get response from one agent"""
        prompt = f"""Context: {context}

Question: {query}

Provide a brief, direct answer."""

        response = self.agents[agent_idx].invoke(prompt)
        return response.content

    def debate_and_vote(self, query: str, context: str) -> dict:
        """Multiple agents debate and reach consensus"""

        # Phase 1: Get initial responses
        initial_responses = []
        with ThreadPoolExecutor(max_workers=self.num_agents) as executor:
            futures = [
                executor.submit(self.get_agent_response, i, query, context)
                for i in range(self.num_agents)
            ]
            initial_responses = [f.result() for f in futures]

        # Phase 2: Debate - each agent critiques others
        critiques = []
        for i in range(self.num_agents):
            critique_prompt = f"""
You proposed: {initial_responses[i]}

Other proposals:
{chr(10).join([f'{j}: {initial_responses[j]}' for j in range(self.num_agents) if j != i])}

Critique these responses and refine your answer."""

            critique = self.agents[i].invoke(critique_prompt)
            critiques.append(critique.content)

        # Phase 3: Final decision by vote
        voting_prompt = f"""
Proposals after debate:
{chr(10).join([f'{i}: {critiques[i]}' for i in range(self.num_agents)])}

Question was: {query}

Which response best answers the question? Explain your choice."""

        decision = self.agents[0].invoke(voting_prompt)

        return {
            "initial_responses": initial_responses,
            "debate_responses": critiques,
            "final_decision": decision.content,
            "consensus": True
        }

# Usage
jury = JuryVoting(num_agents=3)

result = jury.debate_and_vote(
    query="Is this a good time to invest in tech stocks?",
    context="Current market data and trends..."
)

print(result["final_decision"])
```

---

## 4. REAL-TIME DATA INTEGRATION

### 4.1 Streaming Data with WebSocket

```python
import asyncio
import json
from fastapi import FastAPI, WebSocket
from langchain.callbacks.base import BaseCallbackHandler

app = FastAPI()

class StreamingCallbackHandler(BaseCallbackHandler):
    """Send LLM streaming output to WebSocket"""

    def __init__(self, websocket: WebSocket):
        self.websocket = websocket

    async def on_llm_new_token(self, token: str, **kwargs):
        """Called when LLM generates a new token"""
        await self.websocket.send_json({
            "type": "token",
            "content": token
        })

    async def on_llm_end(self, response, **kwargs):
        """Called when LLM finishes"""
        await self.websocket.send_json({
            "type": "end",
            "content": "Response complete"
        })

@app.websocket("/ws/chat/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await websocket.accept()

    try:
        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            # Get streaming response with real-time context
            callback = StreamingCallbackHandler(websocket)

            # Fetch real-time data in parallel
            market_data = await fetch_market_data()
            account_data = await fetch_account_data(user_id)

            context = f"""Real-time Context:
Market Data: {market_data}
Account Status: {account_data}

User Query: {message['content']}"""

            # Stream response
            response = llm.invoke(
                context,
                callbacks=[callback]
            )

    except Exception as e:
        await websocket.send_json({
            "type": "error",
            "content": str(e)
        })
    finally:
        await websocket.close()

# Client-side (JavaScript)
"""
const ws = new WebSocket('ws://localhost:8000/ws/chat/user123');

ws.onopen = () => {
    ws.send(JSON.stringify({
        content: "What's my current portfolio?"
    }));
};

ws.onmessage = (event) => {
    const message = JSON.parse(event.data);

    if (message.type === 'token') {
        document.getElementById('response').textContent += message.content;
    } else if (message.type === 'end') {
        console.log('Response complete');
    }
};
"""
```

### 4.2 Real-Time Market Data Integration

```python
from kafka import KafkaConsumer
import json
from datetime import datetime
import asyncio

class RealTimeMarketContext:
    """Integrate real-time market data into LLM context"""

    def __init__(self, kafka_broker: str):
        self.consumer = KafkaConsumer(
            'market-data',
            bootstrap_servers=[kafka_broker],
            value_deserializer=lambda m: json.loads(m.decode('utf-8')),
            auto_offset_reset='latest',
            group_id='llm-agent'
        )
        self.latest_prices = {}
        self.start_consumer()

    def start_consumer(self):
        """Start consuming market data"""
        asyncio.create_task(self._consume_messages())

    async def _consume_messages(self):
        """Continuously consume Kafka messages"""
        for message in self.consumer:
            data = message.value
            self.latest_prices[data['symbol']] = {
                'price': data['price'],
                'change': data['change'],
                'timestamp': data['timestamp']
            }

    def get_current_prices(self, symbols: List[str]) -> Dict:
        """Get current prices for symbols"""
        return {
            symbol: self.latest_prices.get(symbol, "No data")
            for symbol in symbols
        }

    def build_market_context(self, user_portfolio: Dict) -> str:
        """Build context with real-time data"""
        portfolio_symbols = user_portfolio.keys()
        prices = self.get_current_prices(portfolio_symbols)

        context = "Current Market Data:\n"
        for symbol, price_data in prices.items():
            if price_data != "No data":
                context += f"- {symbol}: ${price_data['price']} ({price_data['change']:+.2f}%)\n"

        return context

# Usage
market_context = RealTimeMarketContext("localhost:9092")

async def get_market_advice(user_id: str, query: str):
    # Fetch user portfolio
    user_portfolio = await db.get_portfolio(user_id)

    # Get real-time market context
    market_context_str = market_context.build_market_context(user_portfolio)

    # Generate response with real-time data
    full_context = f"""{market_context_str}

User Portfolio: {user_portfolio}

User Question: {query}

Provide advice based on current market conditions."""

    response = llm.invoke(full_context)
    return response
```

---

## 5. PRODUCTION MONITORING AND EVALUATION

### 5.1 Comprehensive Metrics Collection

```python
from datetime import datetime
from typing import Dict, Any
import logging

class ConversationMetrics:
    """Track 45+ metrics for conversational AI"""

    def __init__(self, db_connection):
        self.db = db_connection
        self.logger = logging.getLogger(__name__)

    def record_conversation(
        self,
        conversation_id: str,
        user_id: str,
        query: str,
        response: str,
        metadata: Dict[str, Any]
    ):
        """Record conversation with comprehensive metrics"""

        metrics = {
            # Timing metrics
            "start_time": datetime.now(),
            "end_time": datetime.now(),
            "latency_ms": metadata.get("latency_ms", 0),
            "ttfb_ms": metadata.get("ttfb_ms", 0),  # Time to first byte

            # Token metrics
            "input_tokens": metadata.get("input_tokens", 0),
            "output_tokens": metadata.get("output_tokens", 0),
            "total_tokens": metadata.get("total_tokens", 0),

            # Cost metrics
            "api_cost": metadata.get("api_cost", 0),
            "compute_cost": metadata.get("compute_cost", 0),

            # Quality metrics
            "response_length": len(response),
            "query_intent": self._detect_intent(query),
            "response_coherence": metadata.get("coherence_score", 0),
            "hallucination_detected": metadata.get("hallucination", False),

            # User satisfaction
            "user_rating": None,  # Collected later via feedback
            "task_completed": metadata.get("task_completed", False),
            "escalated_to_human": metadata.get("escalated", False),

            # RAG metrics (if applicable)
            "documents_retrieved": metadata.get("doc_count", 0),
            "retrieval_relevance": metadata.get("retrieval_relevance", 0),
            "fact_check_passed": metadata.get("fact_check", True),

            # Model metrics
            "model_used": metadata.get("model", "unknown"),
            "temperature": metadata.get("temperature", 0.7),
            "confidence_score": metadata.get("confidence", 0),

            # Business metrics
            "conversation_id": conversation_id,
            "user_id": user_id,
            "feature_used": metadata.get("feature", "unknown"),
            "outcome": metadata.get("outcome", "unknown"),
        }

        # Store in database
        self._store_metrics(metrics)

        return metrics

    def _detect_intent(self, query: str) -> str:
        """Classify query intent"""
        intents = {
            "question": ["what", "how", "why", "when", "where"],
            "request": ["please", "can you", "could you", "help"],
            "statement": ["i", "my", "tell"],
            "command": ["do", "make", "create", "delete"]
        }

        query_lower = query.lower()
        for intent, keywords in intents.items():
            if any(kw in query_lower for kw in keywords):
                return intent
        return "unknown"

    def _store_metrics(self, metrics: Dict):
        """Store metrics in database"""
        query = """
        INSERT INTO conversation_metrics (
            conversation_id, user_id, latency_ms, tokens_used,
            api_cost, user_rating, task_completed, model_used,
            hallucination_detected, escalated, timestamp
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """

        self.db.execute(query, (
            metrics["conversation_id"],
            metrics["user_id"],
            metrics["latency_ms"],
            metrics["total_tokens"],
            metrics["api_cost"] + metrics["compute_cost"],
            metrics["user_rating"],
            metrics["task_completed"],
            metrics["model_used"],
            metrics["hallucination_detected"],
            metrics["escalated_to_human"],
            datetime.now()
        ))

    def get_performance_dashboard(self, time_period: str = "24h") -> Dict:
        """Get comprehensive performance metrics"""
        query = """
        SELECT
            AVG(latency_ms) as avg_latency,
            PERCENTILE_CONT(0.95) WITHIN GROUP (ORDER BY latency_ms) as p95_latency,
            PERCENTILE_CONT(0.99) WITHIN GROUP (ORDER BY latency_ms) as p99_latency,

            AVG(tokens_used) as avg_tokens,
            SUM(api_cost) as total_api_cost,
            AVG(user_rating) as avg_user_rating,
            COUNT(*) as total_conversations,

            SUM(CASE WHEN task_completed THEN 1 ELSE 0 END) as successful_tasks,
            SUM(CASE WHEN escalated THEN 1 ELSE 0 END) as escalations,
            SUM(CASE WHEN hallucination_detected THEN 1 ELSE 0 END) as hallucinations,

            COUNT(DISTINCT user_id) as unique_users
        FROM conversation_metrics
        WHERE timestamp > NOW() - INTERVAL %s
        """

        result = self.db.fetchone(query, (time_period,))

        return {
            "latency": {
                "avg_ms": result["avg_latency"],
                "p95_ms": result["p95_latency"],
                "p99_ms": result["p99_latency"]
            },
            "cost": {
                "total_usd": result["total_api_cost"],
                "avg_per_conversation": result["total_api_cost"] / result["total_conversations"]
            },
            "quality": {
                "avg_user_rating": result["avg_user_rating"],
                "task_completion_rate": result["successful_tasks"] / result["total_conversations"],
                "escalation_rate": result["escalations"] / result["total_conversations"],
                "hallucination_rate": result["hallucinations"] / result["total_conversations"]
            },
            "usage": {
                "total_conversations": result["total_conversations"],
                "unique_users": result["unique_users"],
                "avg_tokens": result["avg_tokens"]
            }
        }

# Usage
metrics = ConversationMetrics(db)

# During conversation
response = llm.invoke(query)

# Record with metadata
metrics.record_conversation(
    conversation_id="conv_123",
    user_id="user_456",
    query=query,
    response=response,
    metadata={
        "latency_ms": 1250,
        "ttfb_ms": 50,
        "input_tokens": 450,
        "output_tokens": 280,
        "api_cost": 0.0035,
        "task_completed": True,
        "hallucination": False,
        "user_rating": 5
    }
)

# Get dashboard
dashboard = metrics.get_performance_dashboard("24h")
print(f"Avg Latency: {dashboard['latency']['avg_ms']}ms")
print(f"Task Completion Rate: {dashboard['quality']['task_completion_rate']:.2%}")
```

---

## 6. ERROR HANDLING AND FALLBACK PATTERNS

### 6.1 Robust Fallback Chain

```python
from typing import Optional, Callable, List
import logging

class FallbackChain:
    """Chain of fallback strategies for resilient responses"""

    def __init__(self):
        self.strategies: List[Callable] = []
        self.logger = logging.getLogger(__name__)

    def add_strategy(self, name: str, strategy: Callable, priority: int = 0):
        """Add fallback strategy"""
        self.strategies.append({
            "name": name,
            "func": strategy,
            "priority": priority
        })
        # Sort by priority (higher = tried first)
        self.strategies.sort(key=lambda x: x["priority"], reverse=True)

    async def execute(self, query: str, context: str) -> dict:
        """Execute fallback chain"""
        last_error = None

        for strategy in self.strategies:
            try:
                self.logger.info(f"Trying strategy: {strategy['name']}")
                result = await strategy['func'](query, context)

                if result and result.get("success"):
                    self.logger.info(f"Success with {strategy['name']}")
                    return {
                        "success": True,
                        "response": result.get("response"),
                        "strategy_used": strategy["name"],
                        "confidence": result.get("confidence", 0.5)
                    }

            except Exception as e:
                self.logger.warning(f"Strategy {strategy['name']} failed: {str(e)}")
                last_error = e
                continue

        # All strategies failed
        return {
            "success": False,
            "response": "I apologize, but I'm unable to answer that question. Please try a different question or contact support.",
            "strategy_used": "fallback",
            "last_error": str(last_error)
        }

# Build fallback chain
fallback = FallbackChain()

# Strategy 1: Direct LLM response (highest priority, fastest)
async def llm_response_strategy(query: str, context: str) -> dict:
    try:
        response = llm.invoke(f"Context: {context}\n\nQ: {query}")
        return {
            "success": True,
            "response": response.content,
            "confidence": 0.8
        }
    except Exception as e:
        raise e

# Strategy 2: RAG with retrieval
async def rag_strategy(query: str, context: str) -> dict:
    try:
        docs = retriever.get_relevant_documents(query)
        if not docs:
            return {"success": False}

        response = llm.invoke(f"Context: {context}\nDocs: {docs}\n\nQ: {query}")
        return {
            "success": True,
            "response": response.content,
            "confidence": 0.9
        }
    except Exception as e:
        raise e

# Strategy 3: Simple template-based response
async def template_strategy(query: str, context: str) -> dict:
    templates = {
        "greeting": "Hello! How can I help you with financial questions?",
        "help": "I can help you with financial advice, portfolio analysis, and market information.",
        "unknown": "I'm not sure about that. Could you rephrase your question?"
    }

    if "hello" in query.lower() or "hi" in query.lower():
        return {"success": True, "response": templates["greeting"], "confidence": 1.0}
    elif "help" in query.lower():
        return {"success": True, "response": templates["help"], "confidence": 1.0}

    return {"success": False}

# Strategy 4: Escalate to human
async def human_escalation_strategy(query: str, context: str) -> dict:
    return {
        "success": True,
        "response": "This question requires human expertise. Connecting you to a financial advisor...",
        "confidence": 0.5
    }

fallback.add_strategy("llm", llm_response_strategy, priority=3)
fallback.add_strategy("rag", rag_strategy, priority=2)
fallback.add_strategy("template", template_strategy, priority=1)
fallback.add_strategy("escalate", human_escalation_strategy, priority=0)

# Usage
result = await fallback.execute(query, context)
print(result["response"])
print(f"Strategy: {result['strategy_used']}")
```

---

## SUMMARY OF KEY PATTERNS

| Pattern | Use Case | Complexity | Cost | Latency |
|---------|----------|-----------|------|---------|
| **Simple RAG** | Q&A, lookup | Low | Low | 1-3s |
| **RAG + Fact-Check** | Financial, critical | Medium | Medium | 2-5s |
| **Supervisor-Worker** | Multi-domain | Medium | Medium | 3-8s |
| **LangGraph Multi-Agent** | Complex reasoning | High | Medium | 5-15s |
| **Jury Voting** | High accuracy needed | High | High | 10-20s |
| **Real-Time Streaming** | Interactive chat | Medium | Medium | 0.5-2s |
| **Hybrid Memory** | Personalized service | Medium | Low | 1-3s |
| **Fallback Chain** | Reliability critical | Low | Low | Variable |

**2025 Recommendation:** Combine RAG + Supervisor-Worker + Fallback Chain for production financial AI systems.

---

**Last Updated:** November 2025
**Based on:** 50+ Medium articles from 2024-2025
**Framework Versions:** LangChain 0.2+, LangGraph 0.1+, FastAPI 0.100+
