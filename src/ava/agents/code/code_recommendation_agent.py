"""
Code Recommendation Agent - Recommends code changes based on user requests
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def create_code_task_tool(title: str, description: str, priority: str = "medium") -> str:
    """Create a development task for code changes"""
    try:
        from src.task_manager import TaskManager
        task_manager = TaskManager()
        
        task = task_manager.create_task(
            title=title,
            description=description,
            priority=priority,
            category="code_improvement"
        )
        
        return f"Task created: {task.get('id')} - {title}"
    except Exception as e:
        return f"Error creating task: {str(e)}"


class CodeRecommendationAgent(BaseAgent):
    """
    Code Recommendation Agent - Recommends code changes and creates tasks
    
    Capabilities:
    - Analyze codebase for improvements
    - Recommend code changes
    - Create development tasks
    - Suggest refactoring
    - Identify technical debt
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize Code Recommendation Agent"""
        tools = [create_code_task_tool]
        
        super().__init__(
            name="code_recommendation_agent",
            description="Recommends code changes, improvements, and creates development tasks",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.metadata['capabilities'] = [
            'recommend_code_changes',
            'create_development_tasks',
            'suggest_refactoring',
            'identify_technical_debt',
            'analyze_codebase',
            'code_improvement_suggestions'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute code recommendation agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            # Analyze request and recommend code changes
            recommendation = {
                'recommendation': self._analyze_code_request(input_text, context),
                'task_created': False,
                'task_id': None,
                'timestamp': datetime.now().isoformat()
            }
            
            # Create task if recommendation is actionable
            if recommendation['recommendation'].get('actionable', False):
                try:
                    from src.task_manager import TaskManager
                    task_manager = TaskManager()
                    
                    task = task_manager.create_task(
                        title=recommendation['recommendation'].get('title', 'Code Improvement'),
                        description=recommendation['recommendation'].get('description', ''),
                        priority=recommendation['recommendation'].get('priority', 'medium'),
                        category="code_improvement"
                    )
                    
                    recommendation['task_created'] = True
                    recommendation['task_id'] = task.get('id')
                    
                except Exception as e:
                    logger.error(f"Error creating task: {e}")
                    recommendation['task_error'] = str(e)
            
            state['result'] = recommendation
            state['metadata']['agent'] = self.name
            state['metadata']['execution_time'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"CodeRecommendationAgent error: {e}")
            state['error'] = str(e)
            state['result'] = {'error': str(e)}
            return state
    
    def _analyze_code_request(self, input_text: str, context: Dict) -> Dict:
        """Analyze code request and generate recommendation"""
        # Simple analysis - can be enhanced with LLM
        recommendation = {
            'actionable': True,
            'title': f"Code Improvement: {input_text[:50]}",
            'description': input_text,
            'priority': 'medium',
            'suggested_changes': [],
            'files_affected': []
        }
        
        # Extract file mentions
        if '.py' in input_text:
            recommendation['files_affected'] = [
                word for word in input_text.split() if '.py' in word
            ]
        
        return recommendation

