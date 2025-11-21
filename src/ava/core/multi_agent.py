"""
Multi-Agent Orchestration for AVA
Supervisor pattern for agent collaboration
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging
from .ava_core import AVACore

logger = logging.getLogger(__name__)


class MultiAgentState(TypedDict):
    """State for multi-agent system"""
    messages: List[BaseMessage]
    user_id: str
    platform: str
    current_agent: Optional[str]
    agent_results: Dict[str, Any]
    supervisor_decision: Optional[str]
    final_response: Optional[str]


class AgentSupervisor:
    """
    Supervisor for multi-agent orchestration
    
    Routes requests to specialized agents:
    - Market Agent: Market data, prices, trends
    - Strategy Agent: Trading strategies, opportunities
    - Risk Agent: Risk analysis, position management
    - Knowledge Agent: RAG queries, documentation
    """

    def __init__(self, ava_core: AVACore):
        """
        Initialize supervisor

        Args:
            ava_core: AVA Core instance
        """
        self.ava = ava_core
        self.workflow = self._build_supervisor_workflow()
        logger.info("AgentSupervisor initialized")

    def _build_supervisor_workflow(self) -> StateGraph:
        """Build supervisor workflow"""
        workflow = StateGraph(MultiAgentState)

        # Add nodes
        workflow.add_node("supervisor", self._supervisor_node)
        workflow.add_node("market_agent", self._market_agent_node)
        workflow.add_node("strategy_agent", self._strategy_agent_node)
        workflow.add_node("risk_agent", self._risk_agent_node)
        workflow.add_node("knowledge_agent", self._knowledge_agent_node)
        workflow.add_node("synthesize", self._synthesize_node)

        # Set entry point
        workflow.set_entry_point("supervisor")

        # Add conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {
                "market": "market_agent",
                "strategy": "strategy_agent",
                "risk": "risk_agent",
                "knowledge": "knowledge_agent",
                "direct": "synthesize"
            }
        )

        # All agents go to synthesize
        workflow.add_edge("market_agent", "synthesize")
        workflow.add_edge("strategy_agent", "synthesize")
        workflow.add_edge("risk_agent", "synthesize")
        workflow.add_edge("knowledge_agent", "synthesize")
        workflow.add_edge("synthesize", END)

        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)

    def _supervisor_node(self, state: MultiAgentState) -> MultiAgentState:
        """Supervisor decides which agent to use"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Simple routing logic (can be enhanced with LLM)
        message_lower = last_message.lower()
        
        if any(word in message_lower for word in ["price", "market", "trend", "quote"]):
            agent = "market"
        elif any(word in message_lower for word in ["strategy", "opportunity", "trade", "csp", "watchlist"]):
            agent = "strategy"
        elif any(word in message_lower for word in ["risk", "position", "portfolio", "balance"]):
            agent = "risk"
        elif any(word in message_lower for word in ["what", "how", "explain", "tell me about"]):
            agent = "knowledge"
        else:
            agent = "direct"
        
        state["supervisor_decision"] = agent
        state["current_agent"] = agent
        
        logger.info(f"Supervisor routed to: {agent}")
        return state

    def _route_to_agent(self, state: MultiAgentState) -> str:
        """Route to appropriate agent"""
        return state.get("supervisor_decision", "direct")

    def _market_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Market data agent"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Use AVA tools for market data
        result = "Market agent processing: " + last_message
        state["agent_results"]["market"] = result
        
        return state

    def _strategy_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Strategy agent"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Use AVA tools for strategy analysis
        result = "Strategy agent processing: " + last_message
        state["agent_results"]["strategy"] = result
        
        return state

    def _risk_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Risk analysis agent"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Use AVA tools for risk analysis
        result = "Risk agent processing: " + last_message
        state["agent_results"]["risk"] = result
        
        return state

    def _knowledge_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Knowledge agent (RAG)"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Use AVA RAG
        try:
            rag_result = self.ava.rag_service.query(
                question=last_message,
                use_cache=True
            )
            result = rag_result.answer
        except Exception as e:
            result = f"Knowledge agent error: {str(e)}"
        
        state["agent_results"]["knowledge"] = result
        return state

    def _synthesize_node(self, state: MultiAgentState) -> MultiAgentState:
        """Synthesize results from agents"""
        agent_results = state.get("agent_results", {})
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Combine results
        if agent_results:
            combined = "\n\n".join([
                f"{agent}: {result}"
                for agent, result in agent_results.items()
            ])
            final_response = f"Based on analysis:\n\n{combined}"
        else:
            # Fallback to direct AVA response
            response = self.ava.process_message_sync(
                message=last_message,
                user_id=state["user_id"],
                platform=state["platform"]
            )
            final_response = response.content
        
        state["final_response"] = final_response
        return state

    async def process(self, message: str, user_id: str, platform: str = "web"):
        """
        Process message with multi-agent system

        Args:
            message: User message
            user_id: User identifier
            platform: Platform identifier

        Returns:
            Final response
        """
        initial_state: MultiAgentState = {
            "messages": [HumanMessage(content=message)],
            "user_id": user_id,
            "platform": platform,
            "current_agent": None,
            "agent_results": {},
            "supervisor_decision": None,
            "final_response": None
        }

        config = {"configurable": {"thread_id": f"{platform}:{user_id}"}}
        
        final_state = await self.workflow.ainvoke(initial_state, config=config)
        return final_state.get("final_response", "Error processing message")

