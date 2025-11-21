"""
Knowledge Agent - RAG-based knowledge queries
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def query_knowledge_tool(question: str) -> str:
    """Query knowledge base using RAG"""
    try:
        from src.rag.rag_service import RAGService
        rag = RAGService()
        result = rag.query(question=question, use_cache=True)
        return result.answer
    except Exception as e:
        return f"Error: {str(e)}"


class KnowledgeAgent(BaseAgent):
    """
    Knowledge Agent - RAG-based knowledge queries
    
    Capabilities:
    - Query knowledge base
    - RAG search
    - Documentation retrieval
    - Project knowledge
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize Knowledge Agent"""
        tools = [query_knowledge_tool]
        
        super().__init__(
            name="knowledge_agent",
            description="Queries knowledge base using RAG for project documentation and information",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.metadata['capabilities'] = [
            'query_knowledge_base',
            'rag_search',
            'documentation_retrieval',
            'project_knowledge',
            'information_retrieval'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute knowledge agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            question = input_text or context.get('question', '')
            
            try:
                from src.rag.rag_service import RAGService
                rag = RAGService()
                rag_result = rag.query(question=question, use_cache=True)
                
                result = {
                    'question': question,
                    'answer': rag_result.answer,
                    'sources': rag_result.sources if hasattr(rag_result, 'sources') else [],
                    'timestamp': datetime.now().isoformat()
                }
            except Exception as e:
                result = {
                    'error': str(e),
                    'message': 'RAG service not available'
                }
            
            state['result'] = result
            return state
            
        except Exception as e:
            logger.error(f"KnowledgeAgent error: {e}")
            state['error'] = str(e)
            return state

