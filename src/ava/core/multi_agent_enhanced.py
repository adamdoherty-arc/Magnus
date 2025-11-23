"""
Enhanced Multi-Agent Orchestration for AVA
Unified supervisor pattern with agent registry integration
"""

from langgraph.graph import StateGraph, END
from langgraph.checkpoint.memory import MemorySaver
from typing import TypedDict, List, Dict, Any, Optional
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import logging

from .ava_core import AVACore
from .agent_registry import AgentRegistry
from .agent_base import BaseAgent, AgentState

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
    required_capabilities: List[str]


class EnhancedAgentSupervisor:
    """
    Enhanced Supervisor for multi-agent orchestration
    
    Features:
    - Agent registry integration
    - Capability-based routing
    - Multi-agent collaboration
    - Result synthesis
    """
    
    def __init__(self, ava_core: AVACore, agent_registry: AgentRegistry):
        """
        Initialize enhanced supervisor
        
        Args:
            ava_core: AVA Core instance
            agent_registry: Agent registry with all agents
        """
        self.ava = ava_core
        self.registry = agent_registry
        self.workflow = self._build_supervisor_workflow()
        logger.info("EnhancedAgentSupervisor initialized")
    
    def _build_supervisor_workflow(self) -> StateGraph:
        """Build supervisor workflow with dynamic agent nodes"""
        workflow = StateGraph(MultiAgentState)
        
        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_node)
        
        # Add dynamic agent nodes based on registry
        # For now, add common agents
        workflow.add_node("market_agent", self._agent_node)
        workflow.add_node("strategy_agent", self._agent_node)
        workflow.add_node("risk_agent", self._agent_node)
        workflow.add_node("analysis_agent", self._agent_node)
        workflow.add_node("knowledge_agent", self._knowledge_agent_node)
        workflow.add_node("synthesize", self._synthesize_node)
        
        # Set entry point
        workflow.set_entry_point("supervisor")
        
        # Add conditional edges
        workflow.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {
                "market": "market_agent",
                "strategy": "strategy_agent",
                "risk": "risk_agent",
                "analysis": "analysis_agent",
                "knowledge": "knowledge_agent",
                "direct": "synthesize"
            }
        )
        
        # All agents go to synthesize
        workflow.add_edge("market_agent", "synthesize")
        workflow.add_edge("strategy_agent", "synthesize")
        workflow.add_edge("risk_agent", "synthesize")
        workflow.add_edge("analysis_agent", "synthesize")
        workflow.add_edge("knowledge_agent", "synthesize")
        workflow.add_edge("synthesize", END)
        
        # Compile with memory
        memory = MemorySaver()
        return workflow.compile(checkpointer=memory)
    
    def _supervisor_node(self, state: MultiAgentState) -> MultiAgentState:
        """Supervisor decides which agent(s) to use"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
        # Determine required capabilities
        required_capabilities = self._determine_capabilities(last_message)
        state["required_capabilities"] = required_capabilities
        
        # Find matching agents
        matching_agents = self.registry.route_request(last_message, required_capabilities)
        
        if not matching_agents:
            # Fallback to keyword-based routing
            agent = self._keyword_routing(last_message)
            state["supervisor_decision"] = agent
        else:
            # Use first matching agent (can be enhanced for multi-agent)
            agent_name = matching_agents[0].name
            state["supervisor_decision"] = self._map_agent_to_node(agent_name)
            state["current_agent"] = agent_name
        
        logger.info(f"Supervisor routed to: {state['supervisor_decision']}")
        return state
    
    def _determine_capabilities(self, message: str) -> List[str]:
        """Determine required capabilities from message"""
        message_lower = message.lower()
        capabilities = []
        
        if any(word in message_lower for word in ["price", "market", "quote", "stock price"]):
            capabilities.append("get_stock_price")
        if any(word in message_lower for word in ["strategy", "opportunity", "trade", "csp", "cc"]):
            capabilities.append("strategy_analysis")
        if any(word in message_lower for word in ["risk", "position", "portfolio"]):
            capabilities.append("risk_analysis")
        if any(word in message_lower for word in ["analyze", "fundamental", "technical", "sentiment"]):
            capabilities.append("stock_analysis")
        if any(word in message_lower for word in ["what", "how", "explain", "tell me about"]):
            capabilities.append("knowledge_query")
        
        return capabilities
    
    def _keyword_routing(self, message: str) -> str:
        """Fallback keyword-based routing"""
        message_lower = message.lower()
        
        if any(word in message_lower for word in ["price", "market", "trend", "quote"]):
            return "market"
        elif any(word in message_lower for word in ["strategy", "opportunity", "trade", "csp", "watchlist"]):
            return "strategy"
        elif any(word in message_lower for word in ["risk", "position", "portfolio", "balance"]):
            return "risk"
        elif any(word in message_lower for word in ["analyze", "fundamental", "technical"]):
            return "analysis"
        elif any(word in message_lower for word in ["what", "how", "explain", "tell me about"]):
            return "knowledge"
        else:
            return "direct"
    
    def _map_agent_to_node(self, agent_name: str) -> str:
        """Map agent name to workflow node"""
        mapping = {
            "market_data_agent": "market",
            "options_analysis_agent": "strategy",
            "strategy_agent": "strategy",
            "risk_management_agent": "risk",
            "fundamental_analysis_agent": "analysis",
            "technical_analysis_agent": "analysis",
            "sentiment_analysis_agent": "analysis",
        }
        return mapping.get(agent_name, "direct")
    
    def _route_to_agent(self, state: MultiAgentState) -> str:
        """Route to appropriate agent"""
        return state.get("supervisor_decision", "direct")
    
    def _agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Generic agent execution node"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        agent_name = state.get("current_agent")
        
        if agent_name:
            agent = self.registry.get_agent(agent_name)
            if agent:
                # Execute agent
                agent_state: AgentState = {
                    "input": last_message,
                    "context": {"user_id": state["user_id"], "platform": state["platform"]},
                    "tools": agent.tools,
                    "result": None,
                    "error": None,
                    "metadata": {}
                }
                
                # Run agent (sync for now, can be async)
                import asyncio
                try:
                    result_state = asyncio.run(agent.execute(agent_state))
                    state["agent_results"][agent_name] = result_state.get("result", {})
                except Exception as e:
                    logger.error(f"Agent {agent_name} error: {e}")
                    state["agent_results"][agent_name] = {"error": str(e)}
        else:
            # Fallback processing
            result = f"Agent processing: {last_message}"
            state["agent_results"]["generic"] = result
        
        return state
    
    def _knowledge_agent_node(self, state: MultiAgentState) -> MultiAgentState:
        """Knowledge agent (RAG)"""
        last_message = state["messages"][-1].content if state["messages"] else ""
        
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
        Process message with enhanced multi-agent system
        
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
            "final_response": None,
            "required_capabilities": []
        }
        
        config = {"configurable": {"thread_id": f"{platform}:{user_id}"}}
        
        final_state = await self.workflow.ainvoke(initial_state, config=config)
        return final_state.get("final_response", "Error processing message")

