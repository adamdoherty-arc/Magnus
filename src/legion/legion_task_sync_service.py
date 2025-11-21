"""
Legion Task Synchronization Service
====================================

Bidirectional synchronization between Legion and Magnus task systems.
Enables task management from Legion with automatic status updates.

Features:
- Sync tasks from Legion to Magnus
- Push status updates back to Legion
- QA sign-off sync
- Conflict resolution
- Real-time updates
"""

import os
import sys
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime
import psycopg2
from psycopg2.extras import RealDictCursor, Json
from dotenv import load_dotenv
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from task_db_manager import TaskDBManager
from task_completion_with_qa import TaskCompletionWithQA

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class LegionTaskSyncService:
    """
    Bidirectional synchronization service between Legion and Magnus.

    Responsibilities:
    1. Pull tasks from Legion database
    2. Create/update Magnus tasks
    3. Monitor Magnus task status changes
    4. Push updates back to Legion
    5. Sync QA approval status
    """

    def __init__(self,
                 legion_db_config: Optional[Dict] = None,
                 magnus_db_config: Optional[Dict] = None):
        """
        Initialize sync service with database connections.

        Args:
            legion_db_config: Legion database configuration (optional)
            magnus_db_config: Magnus database configuration (optional)
        """
        # Magnus database (local)
        self.magnus_db_config = magnus_db_config or {
            'host': os.getenv('DB_HOST', 'localhost'),
            'port': os.getenv('DB_PORT', '5432'),
            'database': os.getenv('DB_NAME', 'magnus'),
            'user': os.getenv('DB_USER', 'postgres'),
            'password': os.getenv('DB_PASSWORD', '')
        }

        # Legion database (could be remote)
        self.legion_db_config = legion_db_config or {
            'host': os.getenv('LEGION_DB_HOST', 'localhost'),
            'port': os.getenv('LEGION_DB_PORT', '5432'),
            'database': os.getenv('LEGION_DB_NAME', 'legion'),
            'user': os.getenv('LEGION_DB_USER', 'postgres'),
            'password': os.getenv('LEGION_DB_PASSWORD', '')
        }

        self.task_mgr = TaskDBManager()
        self.completion_mgr = TaskCompletionWithQA()

        # Track sync mapping
        self.sync_map_file = "legion_magnus_sync_map.json"
        self.load_sync_map()

    def load_sync_map(self):
        """Load Legion <-> Magnus task ID mapping from file"""
        try:
            if os.path.exists(self.sync_map_file):
                with open(self.sync_map_file, 'r') as f:
                    self.sync_map = json.load(f)
            else:
                self.sync_map = {
                    'legion_to_magnus': {},  # legion_id -> magnus_id
                    'magnus_to_legion': {}   # magnus_id -> legion_id
                }
        except Exception as e:
            logger.error(f"Error loading sync map: {e}")
            self.sync_map = {'legion_to_magnus': {}, 'magnus_to_legion': {}}

    def save_sync_map(self):
        """Save sync mapping to file"""
        try:
            with open(self.sync_map_file, 'w') as f:
                json.dump(self.sync_map, f, indent=2)
        except Exception as e:
            logger.error(f"Error saving sync map: {e}")

    def get_legion_connection(self):
        """Get connection to Legion database"""
        try:
            return psycopg2.connect(**self.legion_db_config)
        except Exception as e:
            logger.error(f"Cannot connect to Legion database: {e}")
            return None

    def get_magnus_connection(self):
        """Get connection to Magnus database"""
        return psycopg2.connect(**self.magnus_db_config)

    def pull_tasks_from_legion(self, project_name: str = "Magnus") -> List[Dict]:
        """
        Pull new tasks assigned to Magnus from Legion.

        Args:
            project_name: Name of project to filter (default: "Magnus")

        Returns:
            List of new tasks to create in Magnus
        """
        conn = self.get_legion_connection()
        if not conn:
            logger.warning("Legion database not available, skipping pull")
            return []

        try:
            with conn.cursor(cursor_factory=RealDictCursor) as cur:
                query = """
                    SELECT
                        id as legion_task_id,
                        title,
                        description,
                        task_type,
                        priority,
                        status,
                        assigned_agent,
                        feature_area,
                        estimated_duration_minutes,
                        dependencies,
                        metadata,
                        created_at,
                        updated_at
                    FROM legion_tasks
                    WHERE project_name = %s
                        AND status NOT IN ('completed', 'cancelled')
                        AND synced_to_project = false
                    ORDER BY priority DESC, created_at ASC;
                """

                cur.execute(query, (project_name,))
                tasks = [dict(row) for row in cur.fetchall()]

                logger.info(f"Pulled {len(tasks)} new tasks from Legion for {project_name}")
                return tasks

        except Exception as e:
            logger.error(f"Error pulling tasks from Legion: {e}")
            return []
        finally:
            conn.close()

    def create_magnus_task_from_legion(self, legion_task: Dict) -> Optional[int]:
        """
        Create a task in Magnus from a Legion task.

        Args:
            legion_task: Task data from Legion

        Returns:
            Magnus task ID if successful, None otherwise
        """
        try:
            # Prepare metadata to include Legion tracking
            metadata = legion_task.get('metadata', {}) or {}
            metadata['legion_task_id'] = legion_task['legion_task_id']
            metadata['sync_source'] = 'legion'
            metadata['synced_at'] = datetime.now().isoformat()

            # Create task in Magnus
            magnus_task_id = self.task_mgr.create_task(
                title=legion_task['title'],
                description=legion_task['description'],
                task_type=legion_task['task_type'],
                priority=legion_task['priority'],
                assigned_agent=legion_task.get('assigned_agent'),
                feature_area=legion_task.get('feature_area'),
                estimated_duration_minutes=legion_task.get('estimated_duration_minutes'),
                tags=['legion-sync'],
                metadata=metadata
            )

            # Update sync map
            legion_id = str(legion_task['legion_task_id'])
            self.sync_map['legion_to_magnus'][legion_id] = magnus_task_id
            self.sync_map['magnus_to_legion'][str(magnus_task_id)] = legion_id
            self.save_sync_map()

            logger.info(f"Created Magnus task #{magnus_task_id} from Legion task {legion_id}")

            return magnus_task_id

        except Exception as e:
            logger.error(f"Error creating Magnus task from Legion: {e}")
            return None

    def mark_legion_task_synced(self, legion_task_id: str, magnus_task_id: int):
        """Mark a Legion task as synced to Magnus"""
        conn = self.get_legion_connection()
        if not conn:
            return

        try:
            with conn.cursor() as cur:
                query = """
                    UPDATE legion_tasks
                    SET synced_to_project = true,
                        synced_task_id = %s,
                        synced_at = %s
                    WHERE id = %s;
                """

                cur.execute(query, (magnus_task_id, datetime.now(), legion_task_id))
                conn.commit()

                logger.info(f"Marked Legion task {legion_task_id} as synced")

        except Exception as e:
            logger.error(f"Error marking Legion task as synced: {e}")
            conn.rollback()
        finally:
            conn.close()

    def push_status_to_legion(self, magnus_task_id: int):
        """
        Push Magnus task status update to Legion.

        Args:
            magnus_task_id: Magnus task ID to sync
        """
        # Get Legion task ID from sync map
        legion_task_id = self.sync_map['magnus_to_legion'].get(str(magnus_task_id))
        if not legion_task_id:
            logger.debug(f"Magnus task #{magnus_task_id} not tracked by Legion, skipping")
            return

        conn = self.get_legion_connection()
        if not conn:
            return

        try:
            # Get Magnus task details
            with self.get_magnus_connection() as magnus_conn:
                with magnus_conn.cursor(cursor_factory=RealDictCursor) as cur:
                    cur.execute("""
                        SELECT
                            t.*,
                            (
                                SELECT COUNT(*)
                                FROM qa_agent_sign_offs
                                WHERE task_id = t.id AND status = 'approved'
                            ) as approved_sign_offs,
                            (
                                SELECT COUNT(*)
                                FROM qa_agent_sign_offs
                                WHERE task_id = t.id
                            ) as total_sign_offs
                        FROM development_tasks t
                        WHERE t.id = %s;
                    """, (magnus_task_id,))

                    magnus_task = cur.fetchone()

                    if not magnus_task:
                        logger.warning(f"Magnus task #{magnus_task_id} not found")
                        return

                    magnus_task = dict(magnus_task)

            # Update Legion task
            with conn.cursor() as cur:
                update_query = """
                    UPDATE legion_tasks
                    SET status = %s,
                        progress_percentage = %s,
                        updated_at = %s,
                        metadata = jsonb_set(
                            COALESCE(metadata, '{}'::jsonb),
                            '{magnus_sync}',
                            %s::jsonb
                        )
                    WHERE id = %s;
                """

                # Calculate progress percentage
                if magnus_task['status'] == 'qa_approved':
                    progress = 100
                elif magnus_task['status'] == 'completed':
                    progress = 90
                elif magnus_task['status'] == 'in_progress':
                    progress = 50
                else:
                    progress = 10

                # Prepare sync metadata
                sync_metadata = {
                    'last_synced': datetime.now().isoformat(),
                    'magnus_status': magnus_task['status'],
                    'qa_sign_offs': f"{magnus_task.get('approved_sign_offs', 0)}/{magnus_task.get('total_sign_offs', 0)}",
                    'completed_at': magnus_task['completed_at'].isoformat() if magnus_task.get('completed_at') else None
                }

                cur.execute(update_query, (
                    magnus_task['status'],
                    progress,
                    datetime.now(),
                    json.dumps(sync_metadata),
                    legion_task_id
                ))

                conn.commit()

                logger.info(f"Pushed status update to Legion task {legion_task_id}")

        except Exception as e:
            logger.error(f"Error pushing status to Legion: {e}")
            if conn:
                conn.rollback()
        finally:
            if conn:
                conn.close()

    def sync_all(self):
        """
        Perform complete bidirectional sync:
        1. Pull new tasks from Legion
        2. Create them in Magnus
        3. Push updates for changed tasks back to Legion
        """
        logger.info("Starting bidirectional sync...")

        # Step 1: Pull and create new tasks
        new_legion_tasks = self.pull_tasks_from_legion()

        for legion_task in new_legion_tasks:
            magnus_task_id = self.create_magnus_task_from_legion(legion_task)

            if magnus_task_id:
                # Mark as synced in Legion
                self.mark_legion_task_synced(
                    str(legion_task['legion_task_id']),
                    magnus_task_id
                )

        # Step 2: Push status updates for tracked tasks
        tracked_magnus_ids = self.sync_map['magnus_to_legion'].keys()

        for magnus_id in tracked_magnus_ids:
            self.push_status_to_legion(int(magnus_id))

        logger.info(f"Sync complete: {len(new_legion_tasks)} new tasks pulled")

    def get_sync_status(self) -> Dict:
        """Get current synchronization status"""
        return {
            'total_tracked_tasks': len(self.sync_map['legion_to_magnus']),
            'legion_to_magnus_mapping': self.sync_map['legion_to_magnus'],
            'magnus_to_legion_mapping': self.sync_map['magnus_to_legion'],
            'last_sync': datetime.now().isoformat()
        }


def main():
    """Run sync service"""
    logger.info("Legion Task Sync Service starting...")

    service = LegionTaskSyncService()

    # Perform sync
    service.sync_all()

    # Display status
    status = service.get_sync_status()
    logger.info(f"Sync Status: {status['total_tracked_tasks']} tasks tracked")

    print("\n=== Legion <-> Magnus Sync Complete ===")
    print(f"Total Tracked Tasks: {status['total_tracked_tasks']}")
    print(f"Last Sync: {status['last_sync']}")


if __name__ == "__main__":
    main()
