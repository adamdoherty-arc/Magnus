"""
Legion Integration Package for Magnus
======================================

This package provides integration between the Legion multi-project management system
and the Magnus trading platform.

Main Components:
- Feature Spec Agents: AI specifications for every Magnus feature
- Legion Operator Agent: Communication bridge between Legion and Magnus
- Task synchronization: Bidirectional sync of tasks and progress

Quick Start:
    # Process a task from Legion
    from src.legion import process_legion_task

    response = process_legion_task(task_json)

    # Get progress for a task
    from src.legion import get_task_progress

    progress = get_task_progress(legion_task_id)

    # Get Magnus context for Legion
    from src.legion import get_context_for_legion

    context = get_context_for_legion("Add feature X to dashboard")
"""

from .feature_spec_agents import (
    FeatureSpecRegistry,
    FeatureSpec,
    FeatureCategory,
    get_context_for_legion
)

from .legion_operator_agent import (
    LegionOperatorAgent,
    LegionTask,
    TaskProgress,
    process_legion_task
)

__all__ = [
    'FeatureSpecRegistry',
    'FeatureSpec',
    'FeatureCategory',
    'get_context_for_legion',
    'LegionOperatorAgent',
    'LegionTask',
    'TaskProgress',
    'process_legion_task'
]

__version__ = '1.0.0'
