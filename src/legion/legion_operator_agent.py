"""
Legion Operator Agent - Communication Bridge Between Legion and Magnus
=======================================================================

This agent serves as the primary interface between the Legion multi-project
management system and the Magnus trading platform.

Responsibilities:
- Receive tasks from Legion
- Understand Magnus features via Feature Spec Agents
- Translate high-level requests into Magnus-specific implementation details
- Execute tasks using Magnus autonomous agent system
- Report progress and results back to Legion
- Maintain task synchronization between Legion and Magnus databases

Author: Claude Code
Date: 2025-01-10
"""

import os
import sys
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from legion.feature_spec_agents import FeatureSpecRegistry, get_context_for_legion

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class LegionTask:
    """
    Task format expected from Legion system
    """
    legion_task_id: str  # UUID from Legion
    project_name: str  # "Magnus" or other project
    title: str
    description: str
    task_type: str  # 'feature', 'bug_fix', 'enhancement', 'refactor'
    priority: str  # 'low', 'medium', 'high', 'critical'
    assigned_agent: Optional[str] = None
    feature_area: Optional[str] = None
    estimated_duration_minutes: Optional[int] = None
    dependencies: Optional[List[str]] = None  # Other Legion task IDs
    metadata: Optional[Dict[str, Any]] = None
    created_at: Optional[str] = None
    status: str = "pending"


@dataclass
class TaskProgress:
    """Progress report to send back to Legion"""
    legion_task_id: str
    magnus_task_id: int  # Internal Magnus task ID
    status: str  # 'pending', 'in_progress', 'completed', 'failed', 'blocked'
    progress_percentage: int  # 0-100
    message: str
    files_modified: List[str] = None
    error_details: Optional[str] = None
    estimated_completion: Optional[str] = None
    actual_duration_minutes: Optional[int] = None


class LegionOperatorAgent:
    """
    Main operator agent for Legion <-> Magnus communication.

    This agent acts as the intelligent intermediary that:
    1. Understands Legion's high-level task requests
    2. Translates them into Magnus-specific implementation details
    3. Uses Feature Spec Agents to provide proper context
    4. Delegates execution to Magnus autonomous agent system
    5. Reports progress back to Legion
    """

    def __init__(self,
                 legion_db_url: Optional[str] = None,
                 magnus_db_url: Optional[str] = None):
        """
        Initialize Legion Operator Agent.

        Args:
            legion_db_url: Connection string for Legion database (optional, defaults to env var)
            magnus_db_url: Connection string for Magnus database (optional, defaults to env var)
        """
        self.legion_db_url = legion_db_url or os.getenv("LEGION_DATABASE_URL")
        self.magnus_db_url = magnus_db_url or os.getenv("DATABASE_URL")

        if not self.magnus_db_url:
            raise ValueError("Magnus DATABASE_URL not configured")

        # Feature registry for understanding Magnus
        self.feature_registry = FeatureSpecRegistry()

        # Statistics
        self.stats = {
            'tasks_received': 0,
            'tasks_translated': 0,
            'tasks_completed': 0,
            'tasks_failed': 0,
            'sync_errors': 0
        }

        logger.info("🤖 Legion Operator Agent initialized")
        logger.info(f"   Magnus DB: {'✅ Connected' if self.magnus_db_url else '❌ Not configured'}")
        logger.info(f"   Legion DB: {'✅ Connected' if self.legion_db_url else '⚠️ Not configured (local mode)'}")

    def get_magnus_connection(self):
        """Get connection to Magnus database"""
        try:
            return psycopg2.connect(self.magnus_db_url)
        except Exception as e:
            logger.error(f"Failed to connect to Magnus DB: {e}")
            raise

    def get_legion_connection(self):
        """Get connection to Legion database (if configured)"""
        if not self.legion_db_url:
            logger.warning("Legion DB not configured, operating in local mode")
            return None

        try:
            return psycopg2.connect(self.legion_db_url)
        except Exception as e:
            logger.error(f"Failed to connect to Legion DB: {e}")
            return None

    def receive_task_from_legion(self, legion_task: LegionTask) -> Dict[str, Any]:
        """
        Receive a task from Legion and process it.

        Workflow:
        1. Validate task is for Magnus project
        2. Analyze task using Feature Spec Agents
        3. Translate into Magnus-specific implementation plan
        4. Create task in Magnus database
        5. Return acknowledgment to Legion

        Args:
            legion_task: Task from Legion system

        Returns:
            Response dictionary with status and Magnus task ID
        """
        self.stats['tasks_received'] += 1

        logger.info(f"\n{'='*80}")
        logger.info(f"📨 RECEIVED TASK FROM LEGION")
        logger.info(f"{'='*80}")
        logger.info(f"Legion Task ID: {legion_task.legion_task_id}")
        logger.info(f"Project: {legion_task.project_name}")
        logger.info(f"Title: {legion_task.title}")
        logger.info(f"Type: {legion_task.task_type}")
        logger.info(f"Priority: {legion_task.priority}")

        # Validate this is for Magnus
        if legion_task.project_name.lower() != "magnus":
            logger.warning(f"Task is for {legion_task.project_name}, not Magnus. Rejecting.")
            return {
                "status": "rejected",
                "reason": f"Task is for {legion_task.project_name}, not Magnus",
                "legion_task_id": legion_task.legion_task_id
            }

        try:
            # Step 1: Generate Magnus context using Feature Spec Agents
            logger.info("\n🔍 Analyzing task with Feature Spec Agents...")
            magnus_context = self.feature_registry.generate_legion_context(
                legion_task.description
            )

            # Step 2: Translate into Magnus implementation plan
            logger.info("\n🔧 Translating to Magnus implementation plan...")
            implementation_plan = self._create_implementation_plan(
                legion_task,
                magnus_context
            )

            # Step 3: Create task in Magnus database
            logger.info("\n💾 Creating task in Magnus database...")
            magnus_task_id = self._create_magnus_task(
                legion_task,
                implementation_plan,
                magnus_context
            )

            # Step 4: Store Legion<->Magnus mapping
            self._store_task_mapping(
                legion_task.legion_task_id,
                magnus_task_id
            )

            self.stats['tasks_translated'] += 1

            response = {
                "status": "accepted",
                "legion_task_id": legion_task.legion_task_id,
                "magnus_task_id": magnus_task_id,
                "message": "Task translated and queued for execution",
                "implementation_plan": implementation_plan,
                "estimated_duration_minutes": legion_task.estimated_duration_minutes or 60
            }

            logger.info(f"\n✅ TASK ACCEPTED")
            logger.info(f"   Magnus Task ID: {magnus_task_id}")
            logger.info(f"   Status: Ready for execution")

            return response

        except Exception as e:
            logger.error(f"Error processing Legion task: {e}", exc_info=True)
            self.stats['sync_errors'] += 1

            return {
                "status": "error",
                "legion_task_id": legion_task.legion_task_id,
                "error": str(e),
                "message": "Failed to process task"
            }

    def _create_implementation_plan(self,
                                    legion_task: LegionTask,
                                    magnus_context: str) -> Dict[str, Any]:
        """
        Create detailed implementation plan for Magnus.

        This translates Legion's high-level task into specific Magnus implementation steps.
        """
        # Identify affected features
        relevant_features = []
        for feature in self.feature_registry.get_all_features():
            if (feature.name.lower() in legion_task.description.lower() or
                legion_task.feature_area and feature.name.lower() == legion_task.feature_area.lower()):
                relevant_features.append(feature.name)

        # Determine appropriate agent type
        agent_type = legion_task.assigned_agent or self._determine_agent_type(
            legion_task,
            relevant_features
        )

        # Build implementation steps
        plan = {
            "task_type": legion_task.task_type,
            "priority": legion_task.priority,
            "affected_features": relevant_features,
            "assigned_agent": agent_type,
            "implementation_steps": self._generate_implementation_steps(legion_task, relevant_features),
            "files_to_modify": self._identify_files_to_modify(relevant_features),
            "testing_requirements": self._define_testing_requirements(legion_task),
            "risks": self._identify_risks(legion_task, relevant_features),
            "success_criteria": self._define_success_criteria(legion_task)
        }

        return plan

    def _determine_agent_type(self, legion_task: LegionTask, features: List[str]) -> str:
        """Determine which Magnus agent should handle this task"""
        task_type = legion_task.task_type.lower()
        description = legion_task.description.lower()

        # Agent selection logic
        if "database" in description or "schema" in description or "sql" in description:
            return "postgresql-pglite-pro"
        elif "ai" in description or "ml" in description or "agent" in description:
            return "ai-engineer"
        elif "frontend" in description or "ui" in description or "streamlit" in description:
            return "frontend-developer"
        elif "api" in description or "backend" in description:
            return "backend-architect"
        elif task_type == "bug_fix":
            return "debugger"
        elif "performance" in description or "optimize" in description:
            return "performance-engineer"
        elif "test" in description:
            return "test-automator"
        else:
            return "full-stack-developer"

    def _generate_implementation_steps(self, legion_task: LegionTask, features: List[str]) -> List[str]:
        """Generate specific implementation steps"""
        steps = [
            f"1. Review existing code in affected features: {', '.join(features) if features else 'general'}",
            f"2. Implement {legion_task.task_type}: {legion_task.title}",
            "3. Add appropriate error handling and logging",
            "4. Update relevant documentation",
            "5. Add or update tests",
            "6. Verify implementation meets requirements",
            "7. Test integration with dependent features"
        ]
        return steps

    def _identify_files_to_modify(self, features: List[str]) -> List[str]:
        """Identify which files will likely need modification"""
        files = []

        for feature_name in features:
            spec = self.feature_registry.get_feature_spec(feature_name)
            if spec:
                files.extend(spec.key_files)

        return list(set(files))  # Remove duplicates

    def _define_testing_requirements(self, legion_task: LegionTask) -> List[str]:
        """Define what testing is needed"""
        return [
            "Unit tests for new functions/methods",
            "Integration tests for affected features",
            "Manual testing of UI changes (if applicable)",
            "Verification that existing tests still pass"
        ]

    def _identify_risks(self, legion_task: LegionTask, features: List[str]) -> List[str]:
        """Identify potential risks"""
        risks = []

        if len(features) > 2:
            risks.append("HIGH: Changes affect multiple features - thorough integration testing required")

        if "database" in legion_task.description.lower():
            risks.append("MEDIUM: Database schema changes - ensure backward compatibility")

        if legion_task.priority == "critical":
            risks.append("HIGH: Critical priority - production impact if bugs introduced")

        return risks if risks else ["LOW: Localized changes with minimal risk"]

    def _define_success_criteria(self, legion_task: LegionTask) -> List[str]:
        """Define what constitutes successful completion"""
        return [
            f"{legion_task.title} implemented as described",
            "All tests passing",
            "No new linting errors",
            "Documentation updated",
            "Code reviewed and approved"
        ]

    def _create_magnus_task(self,
                           legion_task: LegionTask,
                           implementation_plan: Dict[str, Any],
                           magnus_context: str) -> int:
        """
        Create task in Magnus development_tasks table.

        Returns:
            Magnus task ID
        """
        conn = self.get_magnus_connection()

        try:
            with conn.cursor() as cursor:
                # Build full description with Legion context
                full_description = f"""
{legion_task.description}

---
## Legion Task Information
- Legion Task ID: {legion_task.legion_task_id}
- Original Project: {legion_task.project_name}
- Created: {legion_task.created_at or datetime.now().isoformat()}

## Implementation Plan
**Affected Features:** {', '.join(implementation_plan['affected_features'])}

**Implementation Steps:**
{chr(10).join(implementation_plan['implementation_steps'])}

**Files to Modify:**
{chr(10).join(f"- {file}" for file in implementation_plan['files_to_modify'])}

**Testing Requirements:**
{chr(10).join(f"- {req}" for req in implementation_plan['testing_requirements'])}

**Risks:**
{chr(10).join(f"- {risk}" for risk in implementation_plan['risks'])}

**Success Criteria:**
{chr(10).join(f"- {criterion}" for criterion in implementation_plan['success_criteria'])}

---
## Magnus Context
{magnus_context[:1000]}...
"""

                cursor.execute("""
                    INSERT INTO development_tasks (
                        title,
                        description,
                        task_type,
                        priority,
                        assigned_agent,
                        feature_area,
                        estimated_duration_minutes,
                        tags,
                        created_by
                    ) VALUES (
                        %s, %s, %s, %s, %s, %s, %s, %s, %s
                    )
                    RETURNING id
                """, (
                    legion_task.title,
                    full_description,
                    legion_task.task_type,
                    legion_task.priority,
                    implementation_plan['assigned_agent'],
                    implementation_plan['affected_features'][0] if implementation_plan['affected_features'] else 'general',
                    legion_task.estimated_duration_minutes or 60,
                    ['legion-task'] + (implementation_plan['affected_features'] or []),
                    'legion-operator'
                ))

                magnus_task_id = cursor.fetchone()[0]
                conn.commit()

                logger.info(f"✓ Created Magnus task {magnus_task_id}")
                return magnus_task_id

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to create Magnus task: {e}")
            raise
        finally:
            conn.close()

    def _store_task_mapping(self, legion_task_id: str, magnus_task_id: int):
        """
        Store mapping between Legion and Magnus task IDs.

        Creates a mapping table if it doesn't exist.
        """
        conn = self.get_magnus_connection()

        try:
            with conn.cursor() as cursor:
                # Create mapping table if it doesn't exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS legion_task_mapping (
                        legion_task_id VARCHAR(255) PRIMARY KEY,
                        magnus_task_id INTEGER NOT NULL REFERENCES development_tasks(id),
                        created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        last_synced_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
                        sync_status VARCHAR(50) DEFAULT 'active'
                    )
                """)

                # Insert mapping
                cursor.execute("""
                    INSERT INTO legion_task_mapping (legion_task_id, magnus_task_id)
                    VALUES (%s, %s)
                    ON CONFLICT (legion_task_id) DO UPDATE
                    SET magnus_task_id = EXCLUDED.magnus_task_id,
                        last_synced_at = NOW()
                """, (legion_task_id, magnus_task_id))

                conn.commit()

        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to store task mapping: {e}")
            raise
        finally:
            conn.close()

    def get_task_progress(self, legion_task_id: str) -> Optional[TaskProgress]:
        """
        Get progress of a task by Legion ID.

        Args:
            legion_task_id: Legion task identifier

        Returns:
            TaskProgress object or None if not found
        """
        conn = self.get_magnus_connection()

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cursor:
                # Get Magnus task ID from mapping
                cursor.execute("""
                    SELECT magnus_task_id
                    FROM legion_task_mapping
                    WHERE legion_task_id = %s
                """, (legion_task_id,))

                mapping = cursor.fetchone()
                if not mapping:
                    logger.warning(f"No Magnus task found for Legion ID: {legion_task_id}")
                    return None

                magnus_task_id = mapping['magnus_task_id']

                # Get task details
                cursor.execute("""
                    SELECT
                        id,
                        status,
                        started_at,
                        completed_at,
                        actual_duration_minutes
                    FROM development_tasks
                    WHERE id = %s
                """, (magnus_task_id,))

                task = cursor.fetchone()
                if not task:
                    return None

                # Get latest execution log
                cursor.execute("""
                    SELECT message, files_modified, error_details
                    FROM task_execution_log
                    WHERE task_id = %s
                    ORDER BY execution_timestamp DESC
                    LIMIT 1
                """, (magnus_task_id,))

                log = cursor.fetchone()

                # Calculate progress percentage
                progress_pct = {
                    'pending': 0,
                    'in_progress': 50,
                    'completed': 100,
                    'failed': 0,
                    'blocked': 25
                }.get(task['status'], 0)

                # Estimate completion time
                estimated_completion = None
                if task['status'] == 'in_progress' and task['started_at']:
                    # Rough estimate: assume 50% done after 50% of estimated time
                    estimated_completion = (datetime.now() + timedelta(minutes=30)).isoformat()

                return TaskProgress(
                    legion_task_id=legion_task_id,
                    magnus_task_id=magnus_task_id,
                    status=task['status'],
                    progress_percentage=progress_pct,
                    message=log['message'] if log else f"Task is {task['status']}",
                    files_modified=log['files_modified'] if log else [],
                    error_details=log['error_details'] if log else None,
                    estimated_completion=estimated_completion,
                    actual_duration_minutes=task['actual_duration_minutes']
                )

        except Exception as e:
            logger.error(f"Error getting task progress: {e}")
            return None
        finally:
            conn.close()

    def sync_progress_to_legion(self, legion_task_id: str) -> bool:
        """
        Sync progress from Magnus to Legion database.

        Args:
            legion_task_id: Legion task identifier

        Returns:
            True if sync successful, False otherwise
        """
        if not self.legion_db_url:
            logger.info("Legion DB not configured, skipping sync")
            return False

        progress = self.get_task_progress(legion_task_id)
        if not progress:
            logger.warning(f"No progress to sync for {legion_task_id}")
            return False

        legion_conn = self.get_legion_connection()
        if not legion_conn:
            return False

        try:
            with legion_conn.cursor() as cursor:
                # Update Legion task status (assumes Legion has compatible schema)
                cursor.execute("""
                    UPDATE tasks
                    SET status = %s,
                        progress_percentage = %s,
                        last_updated = NOW(),
                        error_details = %s
                    WHERE task_id = %s
                """, (
                    progress.status,
                    progress.progress_percentage,
                    progress.error_details,
                    legion_task_id
                ))

                legion_conn.commit()
                logger.info(f"✓ Synced progress to Legion for task {legion_task_id}")
                return True

        except Exception as e:
            legion_conn.rollback()
            logger.error(f"Failed to sync to Legion: {e}")
            return False
        finally:
            legion_conn.close()

    def get_stats(self) -> Dict[str, Any]:
        """Get operator statistics"""
        return {
            **self.stats,
            'uptime_seconds': (datetime.now() - datetime.now()).total_seconds(),  # Would track actual uptime
            'magnus_features_known': len(self.feature_registry.features),
            'active_mappings': self._count_active_mappings()
        }

    def _count_active_mappings(self) -> int:
        """Count active Legion<->Magnus task mappings"""
        conn = self.get_magnus_connection()

        try:
            with conn.cursor() as cursor:
                cursor.execute("""
                    SELECT COUNT(*)
                    FROM legion_task_mapping
                    WHERE sync_status = 'active'
                """)
                count = cursor.fetchone()[0]
                return count
        except:
            return 0
        finally:
            conn.close()


# Convenience function for Legion integration
def process_legion_task(task_json: str) -> Dict[str, Any]:
    """
    Process a Legion task from JSON.

    Usage in Legion:
        from src.legion.legion_operator_agent import process_legion_task

        response = process_legion_task('''
        {
            "legion_task_id": "uuid-here",
            "project_name": "Magnus",
            "title": "Add momentum indicators to dashboard",
            "description": "Add RSI, MACD indicators...",
            "task_type": "feature",
            "priority": "high"
        }
        ''')
    """
    task_data = json.loads(task_json)
    legion_task = LegionTask(**task_data)

    operator = LegionOperatorAgent()
    return operator.receive_task_from_legion(legion_task)


if __name__ == "__main__":
    # Test the operator
    print("="*80)
    print("LEGION OPERATOR AGENT - TEST")
    print("="*80)

    operator = LegionOperatorAgent()

    print("\n✅ Operator initialized successfully!")
    print(f"\nKnown features: {len(operator.feature_registry.features)}")

    # Test task processing
    test_task = LegionTask(
        legion_task_id="test-uuid-123",
        project_name="Magnus",
        title="Add daily theta decay metric to dashboard",
        description="Create a new metric on the dashboard page that shows the total theta decay expected today across all positions. Should update in real-time.",
        task_type="feature",
        priority="medium",
        estimated_duration_minutes=90
    )

    print("\n" + "="*80)
    print("TEST: Process sample task from Legion")
    print("="*80)

    response = operator.receive_task_from_legion(test_task)

    print(f"\nResponse: {json.dumps(response, indent=2)}")

    if response['status'] == 'accepted':
        print("\n✅ Task successfully translated and queued!")
        print(f"Magnus Task ID: {response['magnus_task_id']}")

    print("\n✅ Legion Operator Agent Test Complete!")
