"""
Wishlist Migration Script
=========================

Migrates all existing markdown wishlist files to the CI database.
Replaces scattered markdown files with centralized database tracking.
"""

import os
import sys
import re
import psycopg2
from psycopg2.extras import execute_values
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Any
from dotenv import load_dotenv

# Fix Windows console encoding
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()


class WishlistMigrator:
    """Migrates wishlist markdown files to database"""

    def __init__(self):
        self.db_url = os.getenv("DATABASE_URL")
        self.conn = psycopg2.connect(self.db_url)
        self.stats = {
            'files_processed': 0,
            'enhancements_created': 0,
            'errors': []
        }

    def migrate_all(self):
        """Find and migrate all wishlist files"""

        # Find all wishlist markdown files
        root_path = Path(__file__).parent.parent.parent

        wishlist_files = list(root_path.glob("**/*WISHLIST*.md"))
        enhancement_files = list(root_path.glob("**/*ENHANC*.md"))

        all_files = wishlist_files + enhancement_files

        print(f"📋 Found {len(all_files)} files to migrate:")
        for f in all_files:
            print(f"   - {f.relative_to(root_path)}")

        print(f"\n🔄 Starting migration...\n")

        for file_path in all_files:
            try:
                self._migrate_file(file_path, root_path)
            except Exception as e:
                self.stats['errors'].append(f"{file_path.name}: {str(e)}")
                print(f"❌ Error processing {file_path.name}: {e}")

        self.conn.close()

        self._print_summary()

    def _migrate_file(self, file_path: Path, root_path: Path):
        """Migrate a single wishlist file"""

        print(f"📄 Processing: {file_path.relative_to(root_path)}")

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # Determine feature area from path
        feature_area = self._extract_feature_area(file_path, root_path)

        # Extract enhancements
        enhancements = self._parse_enhancements(content, feature_area, str(file_path))

        if not enhancements:
            print(f"   ⚠️ No enhancements found in {file_path.name}")
            self.stats['files_processed'] += 1
            return

        # Insert into database
        inserted = self._insert_enhancements(enhancements)

        print(f"   ✅ Migrated {inserted} enhancements from {file_path.name}")

        self.stats['files_processed'] += 1
        self.stats['enhancements_created'] += inserted

    def _extract_feature_area(self, file_path: Path, root_path: Path) -> str:
        """Extract feature area from file path"""
        relative = file_path.relative_to(root_path)
        parts = relative.parts

        if 'features' in parts:
            idx = parts.index('features')
            if idx + 1 < len(parts):
                return parts[idx + 1]

        return 'general'

    def _parse_enhancements(self, content: str, feature_area: str, source_path: str) -> List[Dict[str, Any]]:
        """Parse enhancement items from markdown content"""

        enhancements = []

        # Pattern 1: Checklist items (- [ ] or - [x])
        checklist_pattern = r'- \[([ x])\] (.+?)(?=\n|$)'
        matches = re.findall(checklist_pattern, content, re.MULTILINE)

        for checked, item_text in matches:
            status = 'completed' if checked.lower() == 'x' else 'proposed'

            enhancement = self._create_enhancement(
                title=item_text.strip(),
                description=item_text.strip(),
                feature_area=feature_area,
                status=status,
                category=self._infer_category(item_text),
                priority=self._infer_priority(item_text),
                source='wishlist_migration',
                source_url=source_path
            )

            enhancements.append(enhancement)

        # Pattern 2: Numbered lists (1. 2. 3.)
        numbered_pattern = r'^\d+\.\s+(.+?)(?=\n|$)'
        numbered_matches = re.findall(numbered_pattern, content, re.MULTILINE)

        for item_text in numbered_matches:
            # Skip if already captured in checklist
            if any(e['title'] == item_text.strip() for e in enhancements):
                continue

            enhancement = self._create_enhancement(
                title=item_text.strip(),
                description=item_text.strip(),
                feature_area=feature_area,
                status='proposed',
                category=self._infer_category(item_text),
                priority=self._infer_priority(item_text),
                source='wishlist_migration',
                source_url=source_path
            )

            enhancements.append(enhancement)

        # Pattern 3: Bullet lists (- or *)
        bullet_pattern = r'^[*-]\s+(?!\[)(.+?)(?=\n|$)'
        bullet_matches = re.findall(bullet_pattern, content, re.MULTILINE)

        for item_text in bullet_matches:
            # Skip if already captured
            if any(e['title'] == item_text.strip() for e in enhancements):
                continue

            # Skip headers and short items
            if len(item_text.strip()) < 10:
                continue

            enhancement = self._create_enhancement(
                title=item_text.strip()[:500],  # Limit title length
                description=item_text.strip(),
                feature_area=feature_area,
                status='proposed',
                category=self._infer_category(item_text),
                priority=self._infer_priority(item_text),
                source='wishlist_migration',
                source_url=source_path
            )

            enhancements.append(enhancement)

        return enhancements

    def _create_enhancement(self, **kwargs) -> Dict[str, Any]:
        """Create enhancement dict with defaults"""
        return {
            'title': kwargs.get('title', 'Untitled'),
            'description': kwargs.get('description', ''),
            'feature_area': kwargs.get('feature_area', 'general'),
            'category': kwargs.get('category', 'enhancement'),
            'priority': kwargs.get('priority', 'medium'),
            'status': kwargs.get('status', 'proposed'),
            'source': kwargs.get('source', 'wishlist_migration'),
            'source_url': kwargs.get('source_url'),
            'created_by': 'migration_script',
            'created_at': datetime.now()
        }

    def _infer_category(self, text: str) -> str:
        """Infer category from text"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['bug', 'fix', 'broken', 'error']):
            return 'bug_fix'
        elif any(word in text_lower for word in ['performance', 'optimize', 'speed', 'slow']):
            return 'performance'
        elif any(word in text_lower for word in ['security', 'encrypt', 'auth', 'vulnerability']):
            return 'security'
        elif any(word in text_lower for word in ['test', 'unit test', 'integration test']):
            return 'testing'
        elif any(word in text_lower for word in ['refactor', 'clean up', 'restructure']):
            return 'refactoring'
        elif any(word in text_lower for word in ['add', 'new', 'create', 'implement']):
            return 'new_feature'
        else:
            return 'enhancement'

    def _infer_priority(self, text: str) -> str:
        """Infer priority from text"""
        text_lower = text.lower()

        if any(word in text_lower for word in ['critical', 'urgent', 'must', 'asap', 'blocking']):
            return 'critical'
        elif any(word in text_lower for word in ['high', 'important', 'priority', 'soon']):
            return 'high'
        elif any(word in text_lower for word in ['low', 'nice to have', 'optional', 'future']):
            return 'low'
        else:
            return 'medium'

    def _insert_enhancements(self, enhancements: List[Dict[str, Any]]) -> int:
        """Bulk insert enhancements into database"""

        if not enhancements:
            return 0

        cursor = self.conn.cursor()

        # Prepare data for bulk insert
        values = [
            (
                e['title'],
                e['description'],
                e['feature_area'],
                e['category'],
                e['priority'],
                e['status'],
                e['source'],
                e['source_url'],
                e['created_by']
            )
            for e in enhancements
        ]

        # Bulk insert
        insert_query = """
            INSERT INTO ci_enhancements (
                title, description, feature_area, category, priority,
                status, source, source_url, created_by
            ) VALUES %s
            ON CONFLICT DO NOTHING
        """

        execute_values(cursor, insert_query, values)
        self.conn.commit()

        inserted_count = cursor.rowcount
        cursor.close()

        return inserted_count

    def _print_summary(self):
        """Print migration summary"""
        print(f"\n{'='*80}")
        print(f"📊 Migration Summary")
        print(f"{'='*80}")
        print(f"\nFiles processed: {self.stats['files_processed']}")
        print(f"Enhancements created: {self.stats['enhancements_created']}")

        if self.stats['errors']:
            print(f"\n❌ Errors ({len(self.stats['errors'])}):")
            for error in self.stats['errors']:
                print(f"   - {error}")
        else:
            print(f"\n✅ No errors!")

        print(f"\n{'='*80}\n")


def main():
    """Main entry point"""
    print("="*80)
    print("  Wishlist Migration to AI Continuous Improvement System")
    print("="*80)

    migrator = WishlistMigrator()
    migrator.migrate_all()

    print("\nMigration complete!\n")
    print("Next steps:")
    print("1. View enhancements: SELECT * FROM ci_enhancements ORDER BY created_at DESC;")
    print("2. Check top priorities: SELECT * FROM v_ci_top_priorities;")
    print("3. Archive old markdown files (keep as backup)")
    print("\nThe AI-native system is now ready to use!")


if __name__ == "__main__":
    main()
