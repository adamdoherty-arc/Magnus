"""
Task Management Agent - Development task management
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def get_tasks_tool(status: str = "all", limit: int = 50) -> str:
    """Get development tasks"""
    try:
        from src.task_manager import TaskManager
        task_manager = TaskManager()
        if not task_manager.connect():
            return "Database connection failed"
        
        tasks = task_manager.fetch_tasks(status=[status] if status != "all" else None, limit=limit)
        task_manager.disconnect()
        return f"Found {len(tasks)} tasks"
    except Exception as e:
        return f"Error: {str(e)}"


class TaskManagementAgent(BaseAgent):
    """
    Task Management Agent - Development task management
    
    Capabilities:
    - Get tasks
    - Create tasks
    - Update tasks
    - Track progress
    - Task analytics
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize Task Management Agent"""
        tools = [get_tasks_tool]
        
        super().__init__(
            name="task_management_agent",
            description="Manages development tasks, tracks progress, and provides task analytics",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.metadata['capabilities'] = [
            'get_tasks',
            'create_tasks',
            'update_tasks',
            'track_progress',
            'task_analytics',
            'task_management'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute task management agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            status = context.get('status', 'all')
            limit = context.get('limit', 50)
            
            try:
                from src.task_manager import TaskManager
                task_manager = TaskManager()
                if task_manager.connect():
                    tasks = task_manager.fetch_tasks(status=[status] if status != "all" else None, limit=limit)
                    task_manager.disconnect()
                    
                    result = {
                        'action': 'get_tasks',
                        'tasks': tasks,
                        'count': len(tasks),
                        'status': status,
                        'timestamp': datetime.now().isoformat()
                    }
                else:
                    result = {'error': 'Database connection failed'}
            except Exception as e:
                result = {'error': str(e)}
            
            state['result'] = result
            return state
            
        except Exception as e:
            logger.error(f"TaskManagementAgent error: {e}")
            state['error'] = str(e)
            return state

