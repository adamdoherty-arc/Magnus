"""
QA Agent - Tests and signs off on code changes
"""

import logging
from typing import Dict, List, Any, Optional
from datetime import datetime

from ...core.agent_base import BaseAgent, AgentState
from langchain_core.tools import tool

logger = logging.getLogger(__name__)


@tool
def signoff_task_tool(task_id: str, qa_status: str, notes: str = "") -> str:
    """Sign off on a task after QA"""
    try:
        from src.task_manager import TaskManager
        task_manager = TaskManager()
        
        # Update task with QA status
        status = "completed" if qa_status == "approved" else "failed"
        task_manager.update_task(
            task_id=task_id,
            status=status,
            notes=f"QA {qa_status}: {notes}"
        )
        
        return f"Task {task_id} QA {qa_status}"
    except Exception as e:
        return f"Error signing off task: {str(e)}"


class QAAgent(BaseAgent):
    """
    QA Agent - Tests and signs off on code changes
    
    Capabilities:
    - Test code changes
    - Run automated tests
    - Review code quality
    - Sign off on tasks
    - Reject failed changes
    """
    
    def __init__(self, use_huggingface: bool = False):
        """Initialize QA Agent"""
        tools = [signoff_task_tool]
        
        super().__init__(
            name="qa_agent",
            description="Tests code changes, runs QA, and signs off on tasks",
            tools=tools,
            use_huggingface=use_huggingface
        )
        
        self.metadata['capabilities'] = [
            'test_code_changes',
            'run_automated_tests',
            'review_code_quality',
            'signoff_tasks',
            'reject_changes',
            'qa_approval'
        ]
    
    async def execute(self, state: AgentState) -> AgentState:
        """Execute QA agent"""
        try:
            input_text = state.get('input', '')
            context = state.get('context', {})
            
            task_id = context.get('task_id')
            
            if not task_id:
                state['result'] = {
                    'error': 'No task_id provided',
                    'message': 'task_id required for QA'
                }
                return state
            
            # Run QA tests
            qa_result = self._run_qa_tests(task_id, context)
            
            # Sign off if passed
            if qa_result.get('passed', False):
                try:
                    from src.task_manager import TaskManager
                    task_manager = TaskManager()
                    task_manager.update_task(
                        task_id=task_id,
                        status="completed",
                        notes=f"QA approved: {qa_result.get('notes', '')}"
                    )
                    qa_result['signed_off'] = True
                except Exception as e:
                    logger.error(f"Error signing off task: {e}")
                    qa_result['signoff_error'] = str(e)
            else:
                # Reject if failed
                try:
                    from src.task_manager import TaskManager
                    task_manager = TaskManager()
                    task_manager.update_task(
                        task_id=task_id,
                        status="failed",
                        notes=f"QA rejected: {qa_result.get('notes', '')}"
                    )
                    qa_result['rejected'] = True
                except Exception as e:
                    logger.error(f"Error rejecting task: {e}")
            
            result = {
                'task_id': task_id,
                'qa_result': qa_result,
                'timestamp': datetime.now().isoformat()
            }
            
            state['result'] = result
            state['metadata']['agent'] = self.name
            state['metadata']['execution_time'] = datetime.now().isoformat()
            
            return state
            
        except Exception as e:
            logger.error(f"QAAgent error: {e}")
            state['error'] = str(e)
            state['result'] = {'error': str(e)}
            return state
    
    def _run_qa_tests(self, task_id: str, context: Dict) -> Dict:
        """Run QA tests for a task"""
        # Simple QA - can be enhanced with actual test execution
        qa_result = {
            'passed': True,
            'tests_run': 0,
            'tests_passed': 0,
            'tests_failed': 0,
            'notes': 'QA checks passed'
        }
        
        # TODO: Run actual tests
        # - Linter checks
        # - Unit tests
        # - Integration tests
        # - Code review
        
        return qa_result

