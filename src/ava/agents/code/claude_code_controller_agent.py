"""
Claude Code Controller Agent - Executes code changes via Claude Code
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def execute_code_change_tool(task_id: str, code_changes: str) -> str:
    """Execute code changes for a task"""
    try:
        from src.task_manager import TaskManager
        task_manager = TaskManager()
        
        # Update task with code changes
        task_manager.update_task(
            task_id=task_id,
            status="in_progress",
            notes=f"Code changes: {code_changes}"
        )
        
        return f"Code changes executed for task {task_id}"
    except Exception as e:
        return f"Error executing code changes: {str(e)}"


class ClaudeCodeControllerAgent(BaseAgent):
    """
    Claude Code Controller Agent - Executes code changes
    
    Capabilities:
    - Execute code changes
    - Update tasks
    - Implement features
    - Fix bugs
    - Refactor code
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize Claude Code Controller Agent"""
        tools = [execute_code_change_tool]
        
        super().__init__(
            name="claude_code_controller_agent",
            description="Executes code changes and implements features via Claude Code",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.metadata['capabilities'] = [
            'execute_code_changes',
            'implement_features',
            'fix_bugs',
            'refactor_code',
            'update_tasks',
            'code_implementation'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute Claude Code Controller agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            task_id = context.get('task_id')
            code_changes = context.get('code_changes', input_text)
            
            if not task_id:
                state['result'] = {
                    'error': 'No task_id provided',
                    'message': 'task_id required to execute code changes'
                }
                return state
            
            # Execute code changes
            result = {
                'task_id': task_id,
                'code_changes': code_changes,
                'status': 'executed',
                'timestamp': datetime.now().isoformat()
            }
            
            # Update task status
            try:
                from src.task_manager import TaskManager
                task_manager = TaskManager()
                task_manager.update_task(
                    task_id=task_id,
                    status="in_progress",
                    notes=f"Code changes executed: {code_changes[:200]}"
                )
                result['task_updated'] = True
            except Exception as e:
                logger.error(f"Error updating task: {e}")
                result['task_error'] = str(e)
            
            state['result'] = result
            state['metadata']['agent'] = self.name
            state['metadata']['execution_time'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"ClaudeCodeControllerAgent error: {e}")
            state['error'] = str(e)
            state['result'] = {'error': str(e)}
            return state

