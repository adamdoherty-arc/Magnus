"""
Database Quality Review Script
===============================
Analyzes the AVA database schema for quality issues, optimization opportunities,
and generates a comprehensive quality report.

Checks:
- Table structure and column definitions
- Index usage and missing indexes
- Foreign key constraints
- Data types appropriateness
- Naming conventions
- Query performance
- Storage usage
- Duplicate/redundant tables
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv
from datetime import datetime
import json

load_dotenv()


class DatabaseQualityReviewer:
    def __init__(self):
        self.conn = psycopg2.connect(
            host=os.getenv('DB_HOST', 'localhost'),
            port=os.getenv('DB_PORT', 5432),
            database=os.getenv('DB_NAME', 'magnus'),
            user=os.getenv('DB_USER', 'postgres'),
            password=os.getenv('DB_PASSWORD')
        )
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        self.issues = []
        self.recommendations = []
        self.stats = {}

    def analyze_all(self):
        """Run all quality checks"""
        print("=" * 80)
        print("AVA DATABASE QUALITY REVIEW")
        print("=" * 80)
        print(f"Timestamp: {datetime.now().isoformat()}")
        print(f"Database: {os.getenv('DB_NAME')}")
        print(f"Host: {os.getenv('DB_HOST')}")
        print()

        checks = [
            ("Table Inventory", self.check_table_inventory),
            ("Column Quality", self.check_column_quality),
            ("Index Usage", self.check_indexes),
            ("Foreign Keys", self.check_foreign_keys),
            ("Data Types", self.check_data_types),
            ("Naming Conventions", self.check_naming_conventions),
            ("Storage Usage", self.check_storage_usage),
            ("Redundancy", self.check_redundancy),
            ("Missing Constraints", self.check_missing_constraints),
        ]

        for name, check_func in checks:
            print(f"🔍 Checking: {name}...")
            try:
                check_func()
                print(f"   ✅ {name} check complete")
            except Exception as e:
                print(f"   ❌ {name} check failed: {e}")
                self.issues.append({
                    "category": name,
                    "severity": "ERROR",
                    "message": f"Check failed: {str(e)}"
                })
            print()

        self.generate_report()

    def check_table_inventory(self):
        """Get comprehensive table inventory"""
        query = """
        SELECT
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as size,
            (SELECT COUNT(*) FROM information_schema.columns
             WHERE table_schema = t.schemaname AND table_name = t.tablename) as column_count
        FROM pg_tables t
        WHERE schemaname = 'public'
        ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
        """
        self.cursor.execute(query)
        tables = self.cursor.fetchall()

        self.stats['total_tables'] = len(tables)
        self.stats['tables'] = tables

        print(f"   📊 Found {len(tables)} tables")

        # Check for empty tables
        for table in tables[:10]:  # Top 10 by size
            self.cursor.execute(f"SELECT COUNT(*) as cnt FROM {table['tablename']}")
            count = self.cursor.fetchone()['cnt']
            if count == 0:
                self.issues.append({
                    "category": "Empty Tables",
                    "severity": "WARNING",
                    "table": table['tablename'],
                    "message": "Table exists but has no data"
                })

    def check_column_quality(self):
        """Check column definitions for issues"""
        query = """
        SELECT
            table_name,
            column_name,
            data_type,
            is_nullable,
            column_default,
            character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'public'
        ORDER BY table_name, ordinal_position;
        """
        self.cursor.execute(query)
        columns = self.cursor.fetchall()

        # Check for potential issues
        for col in columns:
            # VARCHAR without length
            if col['data_type'] == 'character varying' and col['character_maximum_length'] is None:
                self.issues.append({
                    "category": "Column Quality",
                    "severity": "WARNING",
                    "table": col['table_name'],
                    "column": col['column_name'],
                    "message": "VARCHAR column without length constraint"
                })

            # Overly long VARCHAR
            if col['character_maximum_length'] and col['character_maximum_length'] > 1000:
                self.recommendations.append({
                    "category": "Column Optimization",
                    "table": col['table_name'],
                    "column": col['column_name'],
                    "message": f"Consider using TEXT instead of VARCHAR({col['character_maximum_length']})"
                })

            # Nullable primary key columns (shouldn't happen but check)
            if col['is_nullable'] == 'YES' and 'id' in col['column_name'].lower():
                self.issues.append({
                    "category": "Column Quality",
                    "severity": "ERROR",
                    "table": col['table_name'],
                    "column": col['column_name'],
                    "message": "ID column is nullable (should be NOT NULL)"
                })

    def check_indexes(self):
        """Check index usage and recommendations"""
        query = """
        SELECT
            schemaname,
            tablename,
            indexname,
            indexdef
        FROM pg_indexes
        WHERE schemaname = 'public'
        ORDER BY tablename, indexname;
        """
        self.cursor.execute(query)
        indexes = self.cursor.fetchall()

        self.stats['total_indexes'] = len(indexes)

        # Check for missing indexes on foreign keys
        fk_query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
          AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
          AND ccu.table_schema = tc.table_schema
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='public';
        """
        self.cursor.execute(fk_query)
        foreign_keys = self.cursor.fetchall()

        indexed_columns = {}
        for idx in indexes:
            table = idx['tablename']
            if table not in indexed_columns:
                indexed_columns[table] = []
            # Extract column name from index definition
            if 'ON ' in idx['indexdef']:
                cols = idx['indexdef'].split('(')[1].split(')')[0]
                indexed_columns[table].extend([c.strip() for c in cols.split(',')])

        # Check if FK columns are indexed
        for fk in foreign_keys:
            table = fk['table_name']
            column = fk['column_name']
            if table not in indexed_columns or column not in indexed_columns.get(table, []):
                self.recommendations.append({
                    "category": "Missing Index",
                    "table": table,
                    "column": column,
                    "message": f"Foreign key column '{column}' should have an index for better join performance",
                    "sql": f"CREATE INDEX idx_{table}_{column} ON {table}({column});"
                })

    def check_foreign_keys(self):
        """Check foreign key constraints"""
        query = """
        SELECT
            tc.table_name,
            kcu.column_name,
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name,
            rc.update_rule,
            rc.delete_rule
        FROM information_schema.table_constraints AS tc
        JOIN information_schema.key_column_usage AS kcu
          ON tc.constraint_name = kcu.constraint_name
        JOIN information_schema.constraint_column_usage AS ccu
          ON ccu.constraint_name = tc.constraint_name
        JOIN information_schema.referential_constraints AS rc
          ON tc.constraint_name = rc.constraint_name
        WHERE tc.constraint_type = 'FOREIGN KEY' AND tc.table_schema='public';
        """
        self.cursor.execute(query)
        foreign_keys = self.cursor.fetchall()

        self.stats['total_foreign_keys'] = len(foreign_keys)

        # Check for potentially dangerous DELETE CASCADE
        for fk in foreign_keys:
            if fk['delete_rule'] == 'CASCADE':
                self.issues.append({
                    "category": "Foreign Key Safety",
                    "severity": "INFO",
                    "table": fk['table_name'],
                    "column": fk['column_name'],
                    "message": f"ON DELETE CASCADE to {fk['foreign_table_name']}.{fk['foreign_column_name']} - verify this is intentional"
                })

    def check_data_types(self):
        """Check for suboptimal data type choices"""
        query = """
        SELECT table_name, column_name, data_type, character_maximum_length
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND data_type IN ('character', 'character varying', 'text');
        """
        self.cursor.execute(query)
        text_columns = self.cursor.fetchall()

        # Check for CHAR type (usually VARCHAR is better)
        for col in text_columns:
            if col['data_type'] == 'character':
                self.recommendations.append({
                    "category": "Data Type",
                    "table": col['table_name'],
                    "column": col['column_name'],
                    "message": "Consider using VARCHAR instead of CHAR for flexibility"
                })

    def check_naming_conventions(self):
        """Check naming conventions"""
        query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
        self.cursor.execute(query)
        tables = self.cursor.fetchall()

        for table in tables:
            name = table['tablename']
            # Check for uppercase or camelCase
            if name != name.lower() or ' ' in name:
                self.issues.append({
                    "category": "Naming Convention",
                    "severity": "WARNING",
                    "table": name,
                    "message": "Table name should be lowercase with underscores"
                })

    def check_storage_usage(self):
        """Analyze storage usage"""
        query = """
        SELECT
            schemaname,
            tablename,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) as total_size,
            pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) as table_size,
            pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename) - pg_relation_size(schemaname||'.'||tablename)) as indexes_size,
            pg_total_relation_size(schemaname||'.'||tablename) as size_bytes
        FROM pg_tables
        WHERE schemaname = 'public'
        ORDER BY size_bytes DESC
        LIMIT 20;
        """
        self.cursor.execute(query)
        storage = self.cursor.fetchall()

        self.stats['storage'] = storage

        total_size = sum(s['size_bytes'] for s in storage)
        self.stats['total_storage_bytes'] = total_size
        self.stats['total_storage_readable'] = self._format_bytes(total_size)

    def check_redundancy(self):
        """Check for potentially redundant tables"""
        # This is heuristic-based
        query = "SELECT tablename FROM pg_tables WHERE schemaname = 'public';"
        self.cursor.execute(query)
        tables = [t['tablename'] for t in self.cursor.fetchall()]

        # Check for similar table names (potential duplicates)
        seen = set()
        for table in tables:
            base_name = table.replace('_', '').lower()
            if base_name in seen:
                self.recommendations.append({
                    "category": "Potential Redundancy",
                    "message": f"Table '{table}' has similar name to existing table - verify not duplicate"
                })
            seen.add(base_name)

    def check_missing_constraints(self):
        """Check for missing NOT NULL or CHECK constraints where appropriate"""
        query = """
        SELECT table_name, column_name, is_nullable, data_type
        FROM information_schema.columns
        WHERE table_schema = 'public'
        AND is_nullable = 'YES'
        AND (column_name LIKE '%_id' OR column_name LIKE '%date%' OR column_name = 'id');
        """
        self.cursor.execute(query)
        nullable_important = self.cursor.fetchall()

        for col in nullable_important:
            self.recommendations.append({
                "category": "Missing Constraint",
                "table": col['table_name'],
                "column": col['column_name'],
                "message": f"Consider adding NOT NULL constraint to {col['column_name']}"
            })

    def _format_bytes(self, bytes):
        """Format bytes to human readable"""
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes < 1024.0:
                return f"{bytes:.2f} {unit}"
            bytes /= 1024.0
        return f"{bytes:.2f} PB"

    def generate_report(self):
        """Generate comprehensive quality report"""
        print("\n" + "=" * 80)
        print("DATABASE QUALITY REPORT")
        print("=" * 80)

        # Summary Statistics
        print("\n📊 SUMMARY STATISTICS")
        print("-" * 80)
        print(f"Total Tables: {self.stats.get('total_tables', 'N/A')}")
        print(f"Total Indexes: {self.stats.get('total_indexes', 'N/A')}")
        print(f"Total Foreign Keys: {self.stats.get('total_foreign_keys', 'N/A')}")
        print(f"Total Storage: {self.stats.get('total_storage_readable', 'N/A')}")

        # Top 10 Largest Tables
        if 'storage' in self.stats:
            print("\n📦 TOP 10 LARGEST TABLES")
            print("-" * 80)
            for i, table in enumerate(self.stats['storage'][:10], 1):
                print(f"{i:2d}. {table['tablename']:40s} {table['total_size']:>15s}")

        # Issues
        if self.issues:
            print(f"\n⚠️  ISSUES FOUND ({len(self.issues)})")
            print("-" * 80)
            for issue in self.issues:
                severity = issue.get('severity', 'INFO')
                icon = "🔴" if severity == "ERROR" else "🟡" if severity == "WARNING" else "🔵"
                print(f"{icon} [{issue['category']}] {issue.get('table', '')} - {issue['message']}")
        else:
            print("\n✅ NO ISSUES FOUND")

        # Recommendations
        if self.recommendations:
            print(f"\n💡 RECOMMENDATIONS ({len(self.recommendations)})")
            print("-" * 80)
            for rec in self.recommendations[:20]:  # Top 20
                print(f"• [{rec['category']}] {rec.get('table', '')} - {rec['message']}")
                if 'sql' in rec:
                    print(f"  SQL: {rec['sql']}")

        # Overall Quality Score
        total_checks = len(self.issues) + len(self.recommendations)
        if total_checks == 0:
            score = 100
        elif len(self.issues) == 0:
            score = max(80, 100 - len(self.recommendations) * 2)
        else:
            score = max(50, 100 - len(self.issues) * 5 - len(self.recommendations) * 2)

        print(f"\n🎯 OVERALL QUALITY SCORE: {score}/100")
        print("-" * 80)

        if score >= 90:
            print("✅ EXCELLENT - Database schema is well-designed")
        elif score >= 75:
            print("✅ GOOD - Minor improvements recommended")
        elif score >= 60:
            print("⚠️  FAIR - Several issues should be addressed")
        else:
            print("❌ POOR - Significant improvements needed")

        print("\n" + "=" * 80)

        # Save detailed report
        report_file = f"database_quality_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(report_file, 'w') as f:
            json.dump({
                "timestamp": datetime.now().isoformat(),
                "stats": self.stats,
                "issues": self.issues,
                "recommendations": self.recommendations,
                "score": score
            }, f, indent=2, default=str)

        print(f"\n📄 Detailed report saved to: {report_file}")

    def close(self):
        """Close database connection"""
        self.cursor.close()
        self.conn.close()


if __name__ == "__main__":
    reviewer = DatabaseQualityReviewer()
    try:
        reviewer.analyze_all()
    finally:
        reviewer.close()
