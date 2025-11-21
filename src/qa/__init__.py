"""
Multi-Agent QA System
====================

Comprehensive QA system with multi-agent sign-offs, RAG expertise, and issue tracking.

Features:
- Multi-agent review and sign-off requirements
- Agent-specific RAG expertise for informed reviews
- QA issue tracking (separate from main tasks)
- Historical audit trail (NEVER delete)
- Integration with Legion agent system
- Automated workflow orchestration

Usage:
    from src.qa import MultiAgentQAService, get_expertise_registry

    # QA Service
    qa_service = MultiAgentQAService()

    # Trigger QA review after task completion
    qa_service.trigger_qa_review(task_id)

    # Agent performs review
    qa_service.perform_agent_review(sign_off_id, 'code-reviewer')

    # Complete review with findings
    qa_service.complete_agent_review(
        sign_off_id,
        'code-reviewer',
        approved=False,
        review_notes="Found code duplication issues",
        issues_found=[{
            'title': 'Duplicate code in auth module',
            'description': '...',
            'severity': 'high',
            'issue_type': 'code_quality'
        }]
    )

    # Fix QA issues
    qa_service.mark_qa_task_complete(qa_task_id, "Refactored code", 'code-reviewer')

    # Finalize task (all QA complete)
    qa_service.finalize_task_completion(task_id)

    # Agent Expertise
    registry = get_expertise_registry()
    agent = registry.get_agent_expertise('security-auditor')
    context = agent.get_review_context("Review authentication code")
"""

from .multi_agent_qa_service import MultiAgentQAService
from .agent_rag_expertise import (
    AgentRAGExpertise,
    QAAgentExpertiseRegistry,
    get_expertise_registry,
    ExpertiseDocument,
    RelevantExpertise
)

__all__ = [
    'MultiAgentQAService',
    'AgentRAGExpertise',
    'QAAgentExpertiseRegistry',
    'get_expertise_registry',
    'ExpertiseDocument',
    'RelevantExpertise'
]
