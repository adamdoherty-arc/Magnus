"""
Kalshi Team Names Migration Script

Fixes corrupted team names in kalshi_markets table caused by parsing bug.
Supports dry-run, validation, backup, and rollback operations.

Usage:
    python fix_kalshi_team_names_migration.py --dry-run     # Preview changes
    python fix_kalshi_team_names_migration.py --validate    # Check data quality
    python fix_kalshi_team_names_migration.py               # Execute migration
    python fix_kalshi_team_names_migration.py --rollback    # Restore from backup
"""

import argparse
import json
import logging
import os
import re
from datetime import datetime
from typing import Dict, List, Optional, Tuple

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

# Configure logging
log_filename = f"migration_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(log_filename),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# NFL Team Abbreviation to Full Name Mapping
NFL_TEAM_MAPPING = {
    # AFC East
    'NE': 'New England Patriots',
    'BUF': 'Buffalo Bills',
    'MIA': 'Miami Dolphins',
    'NYJ': 'New York Jets',

    # AFC North
    'BAL': 'Baltimore Ravens',
    'CIN': 'Cincinnati Bengals',
    'CLE': 'Cleveland Browns',
    'PIT': 'Pittsburgh Steelers',

    # AFC South
    'HOU': 'Houston Texans',
    'IND': 'Indianapolis Colts',
    'JAX': 'Jacksonville Jaguars',
    'JAC': 'Jacksonville Jaguars',  # Kalshi uses JAC
    'TEN': 'Tennessee Titans',

    # AFC West
    'DEN': 'Denver Broncos',
    'KC': 'Kansas City Chiefs',
    'LV': 'Las Vegas Raiders',
    'LAC': 'Los Angeles Chargers',

    # NFC East
    'DAL': 'Dallas Cowboys',
    'NYG': 'New York Giants',
    'PHI': 'Philadelphia Eagles',
    'WAS': 'Washington Commanders',

    # NFC North
    'CHI': 'Chicago Bears',
    'DET': 'Detroit Lions',
    'GB': 'Green Bay Packers',
    'MIN': 'Minnesota Vikings',

    # NFC South
    'ATL': 'Atlanta Falcons',
    'CAR': 'Carolina Panthers',
    'NO': 'New Orleans Saints',
    'TB': 'Tampa Bay Buccaneers',

    # NFC West
    'ARI': 'Arizona Cardinals',
    'LAR': 'Los Angeles Rams',
    'LA': 'Los Angeles Rams',  # Kalshi uses LA for Rams (primary LA team)
    'SF': 'San Francisco 49ers',
    'SEA': 'Seattle Seahawks',
}

# Corrupted patterns to detect
CORRUPTED_PATTERNS = [
    'England',  # Should be "New England"
    'Bay',      # Should be "Tampa Bay" or "Green Bay"
    'City',     # Should be "Kansas City"
    'Angeles',  # Should be "Los Angeles"
    'York',     # Should be "New York"
    'Vegas',    # Should be "Las Vegas"
    'Orleans',  # Should be "New Orleans"
    'Francisco' # Should be "San Francisco"
]


class KalshiTeamMigration:
    """Handles migration of corrupted Kalshi team names."""

    def __init__(self, dry_run: bool = False):
        """Initialize migration handler.

        Args:
            dry_run: If True, only preview changes without executing
        """
        self.dry_run = dry_run
        self.conn = None
        self.backup_file = None
        self.changes_made = []

    def connect_db(self) -> None:
        """Establish database connection using environment variables."""
        load_dotenv()

        try:
            self.conn = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5432'),
                database=os.getenv('DB_NAME', 'trading'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD')
            )
            self.conn.autocommit = False  # Manual transaction control
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    def close_db(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")

    def create_backup(self) -> str:
        """Create backup of kalshi_markets table.

        Returns:
            Path to backup file
        """
        backup_filename = f"kalshi_markets_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("SELECT * FROM kalshi_markets")
                records = cur.fetchall()

                # Convert to JSON-serializable format
                backup_data = []
                for record in records:
                    record_dict = dict(record)
                    # Convert datetime and Decimal objects to JSON-serializable types
                    for key, value in record_dict.items():
                        if hasattr(value, 'isoformat'):
                            record_dict[key] = value.isoformat()
                        elif isinstance(value, (int, float, str, bool, type(None))):
                            pass  # Already JSON-serializable
                        else:
                            # Convert other types (like Decimal) to string
                            record_dict[key] = str(value)
                    backup_data.append(record_dict)

                with open(backup_filename, 'w') as f:
                    json.dump(backup_data, f, indent=2)

                logger.info(f"Backup created: {backup_filename} ({len(backup_data)} records)")
                self.backup_file = backup_filename
                return backup_filename

        except Exception as e:
            logger.error(f"Failed to create backup: {e}")
            raise

    def parse_ticker_teams(self, ticker: str) -> Optional[Tuple[str, str]]:
        """Extract team abbreviations from Kalshi ticker.

        Examples:
            KXNFLGAME-25NOV23NECIN-NE → (NE, CIN)
            KXNFLGAME-28NOV24TBKC-TB → (TB, KC)
            KXNFLGAME-25NOV16LACJAC-LAC → (LAC, JAC)

        Args:
            ticker: Kalshi market ticker

        Returns:
            Tuple of (away_abbr, home_abbr) or None if parsing fails
        """
        # Pattern: KXNFLGAME-DDmmmYYTEAMS-RESULT
        # Extract the concatenated team string after the date
        match = re.search(r'KXNFLGAME-\d{2}[A-Z]{3}\d{2}([A-Z]+)-', ticker)

        if not match:
            return None

        teams_str = match.group(1)

        # Try to split the concatenated team abbreviations
        # Teams can be 2 or 3 letters (e.g., "NE", "CIN", "LAC", "JAC")
        # Try all possible split points
        for i in range(2, len(teams_str)):
            team1 = teams_str[:i]
            team2 = teams_str[i:]

            # Check if both are valid team abbreviations (2-3 letters)
            if (2 <= len(team1) <= 3 and 2 <= len(team2) <= 3):
                if team1 in NFL_TEAM_MAPPING and team2 in NFL_TEAM_MAPPING:
                    # Return in order: team1 = away, team2 = home
                    return (team1, team2)

        return None

    def is_corrupted(self, team_name: Optional[str]) -> bool:
        """Check if team name shows corruption patterns.

        Args:
            team_name: Team name to check

        Returns:
            True if corrupted
        """
        if not team_name:
            return False

        # Check for partial team names
        for pattern in CORRUPTED_PATTERNS:
            if team_name == pattern or team_name.endswith(pattern):
                return True

        # Check if it's not a full team name in our mapping
        full_names = set(NFL_TEAM_MAPPING.values())
        if team_name not in full_names:
            # Allow for variations like "New England" without "Patriots"
            for full_name in full_names:
                if team_name in full_name:
                    return False
            return True

        return False

    def validate_data_quality(self) -> Dict:
        """Analyze current data quality in kalshi_markets table.

        Returns:
            Dictionary with validation statistics
        """
        logger.info("Running data quality validation...")

        stats = {
            'total_records': 0,
            'corrupted_home_team': 0,
            'corrupted_away_team': 0,
            'unparseable_tickers': 0,
            'valid_records': 0,
            'corrupted_records': []
        }

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                cur.execute("""
                    SELECT id, ticker, home_team, away_team, title
                    FROM kalshi_markets
                    WHERE ticker LIKE 'KXNFLGAME%'
                    ORDER BY id
                """)
                records = cur.fetchall()
                stats['total_records'] = len(records)

                for record in records:
                    is_corrupted = False
                    issues = []

                    # Check home team
                    if self.is_corrupted(record['home_team']):
                        stats['corrupted_home_team'] += 1
                        is_corrupted = True
                        issues.append(f"home_team: {record['home_team']}")

                    # Check away team
                    if self.is_corrupted(record['away_team']):
                        stats['corrupted_away_team'] += 1
                        is_corrupted = True
                        issues.append(f"away_team: {record['away_team']}")

                    # Check if ticker is parseable
                    teams = self.parse_ticker_teams(record['ticker'])
                    if not teams:
                        stats['unparseable_tickers'] += 1
                        is_corrupted = True
                        issues.append("unparseable ticker")

                    if is_corrupted:
                        stats['corrupted_records'].append({
                            'id': record['id'],
                            'ticker': record['ticker'],
                            'home_team': record['home_team'],
                            'away_team': record['away_team'],
                            'title': record['title'],
                            'issues': issues
                        })
                    else:
                        stats['valid_records'] += 1

                # Calculate percentages
                if stats['total_records'] > 0:
                    stats['corruption_rate'] = (
                        (stats['total_records'] - stats['valid_records']) /
                        stats['total_records'] * 100
                    )
                else:
                    stats['corruption_rate'] = 0.0

                logger.info(f"Validation complete: {stats['total_records']} total, "
                          f"{stats['valid_records']} valid, "
                          f"{len(stats['corrupted_records'])} corrupted "
                          f"({stats['corruption_rate']:.1f}%)")

                return stats

        except Exception as e:
            logger.error(f"Validation failed: {e}")
            raise

    def fix_team_names(self, record: Dict) -> Optional[Dict]:
        """Fix team names for a single record.

        Args:
            record: Database record dictionary

        Returns:
            Dictionary with corrected team names or None if no fix needed
        """
        # Parse ticker to get team abbreviations
        teams = self.parse_ticker_teams(record['ticker'])

        if not teams:
            logger.warning(f"Cannot parse ticker: {record['ticker']}")
            return None

        team1_abbr, team2_abbr = teams
        team1_full = NFL_TEAM_MAPPING[team1_abbr]
        team2_full = NFL_TEAM_MAPPING[team2_abbr]

        # Determine which team is home/away based on current data or ticker pattern
        # Kalshi ticker pattern: KXNFLGAME-DDmmmYYAWAYHOME-RESULT
        # team1 = AWAY team, team2 = HOME team
        corrected = {
            'id': record['id'],
            'ticker': record['ticker'],
            'old_home_team': record['home_team'],
            'old_away_team': record['away_team'],
            'new_home_team': None,
            'new_away_team': None,
            'needs_update': False
        }

        # Check if home team needs fixing
        if self.is_corrupted(record['home_team']):
            # Home team is team2 in ticker (second position)
            corrected['new_home_team'] = team2_full
            corrected['needs_update'] = True

        # Check if away team needs fixing
        if self.is_corrupted(record['away_team']):
            # Away team is team1 in ticker (first position)
            corrected['new_away_team'] = team1_full
            corrected['needs_update'] = True

        # If no updates needed, return None
        if not corrected['needs_update']:
            return None

        # Keep existing values if not corrupted
        if not corrected['new_home_team']:
            corrected['new_home_team'] = record['home_team']
        if not corrected['new_away_team']:
            corrected['new_away_team'] = record['away_team']

        return corrected

    def execute_migration(self) -> int:
        """Execute the migration to fix all corrupted team names.

        Returns:
            Number of records updated
        """
        logger.info("Starting migration...")

        if not self.dry_run:
            # Create backup before making changes
            self.create_backup()

        updated_count = 0

        try:
            with self.conn.cursor(cursor_factory=RealDictCursor) as cur:
                # Fetch all NFL game records
                cur.execute("""
                    SELECT id, ticker, home_team, away_team, title
                    FROM kalshi_markets
                    WHERE ticker LIKE 'KXNFLGAME%'
                    ORDER BY id
                """)
                records = cur.fetchall()

                logger.info(f"Processing {len(records)} records...")

                for record in records:
                    correction = self.fix_team_names(dict(record))

                    if correction:
                        log_msg = (
                            f"ID {correction['id']}: "
                            f"home_team: '{correction['old_home_team']}' → '{correction['new_home_team']}', "
                            f"away_team: '{correction['old_away_team']}' → '{correction['new_away_team']}'"
                        )

                        if self.dry_run:
                            logger.info(f"[DRY RUN] Would update: {log_msg}")
                        else:
                            # Execute update
                            cur.execute("""
                                UPDATE kalshi_markets
                                SET home_team = %s, away_team = %s
                                WHERE id = %s
                            """, (
                                correction['new_home_team'],
                                correction['new_away_team'],
                                correction['id']
                            ))
                            logger.info(f"Updated: {log_msg}")
                            self.changes_made.append(correction)

                        updated_count += 1

                if not self.dry_run:
                    self.conn.commit()
                    logger.info(f"Migration committed: {updated_count} records updated")
                else:
                    logger.info(f"[DRY RUN] Would update {updated_count} records")

                return updated_count

        except Exception as e:
            if not self.dry_run:
                self.conn.rollback()
            logger.error(f"Migration failed: {e}")
            raise

    def rollback_from_backup(self, backup_file: str) -> int:
        """Restore kalshi_markets table from backup file.

        Args:
            backup_file: Path to backup JSON file

        Returns:
            Number of records restored
        """
        logger.info(f"Rolling back from backup: {backup_file}")

        try:
            with open(backup_file, 'r') as f:
                backup_data = json.load(f)

            restored_count = 0

            with self.conn.cursor() as cur:
                for record in backup_data:
                    # Update only the team name fields
                    cur.execute("""
                        UPDATE kalshi_markets
                        SET home_team = %s, away_team = %s
                        WHERE id = %s
                    """, (
                        record.get('home_team'),
                        record.get('away_team'),
                        record['id']
                    ))
                    restored_count += 1

                self.conn.commit()
                logger.info(f"Rollback completed: {restored_count} records restored")
                return restored_count

        except Exception as e:
            self.conn.rollback()
            logger.error(f"Rollback failed: {e}")
            raise

    def generate_report(self, stats: Dict, updated_count: int) -> None:
        """Generate migration report.

        Args:
            stats: Validation statistics
            updated_count: Number of records updated
        """
        report_file = f"migration_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"

        report_lines = [
            "=" * 80,
            "KALSHI TEAM NAMES MIGRATION REPORT",
            "=" * 80,
            f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
            f"Mode: {'DRY RUN' if self.dry_run else 'LIVE MIGRATION'}",
            "",
            "DATA QUALITY BEFORE MIGRATION:",
            f"  Total Records: {stats['total_records']}",
            f"  Valid Records: {stats['valid_records']}",
            f"  Corrupted Records: {len(stats['corrupted_records'])}",
            f"  Corruption Rate: {stats['corruption_rate']:.1f}%",
            f"  Corrupted Home Teams: {stats['corrupted_home_team']}",
            f"  Corrupted Away Teams: {stats['corrupted_away_team']}",
            f"  Unparseable Tickers: {stats['unparseable_tickers']}",
            "",
            "MIGRATION RESULTS:",
            f"  Records Updated: {updated_count}",
            f"  Backup File: {self.backup_file or 'N/A (dry run)'}",
            "",
        ]

        if self.changes_made:
            report_lines.extend([
                "DETAILED CHANGES:",
                "-" * 80,
            ])
            for change in self.changes_made[:50]:  # Limit to first 50
                report_lines.append(
                    f"ID {change['id']} ({change['ticker']}):\n"
                    f"  Home: '{change['old_home_team']}' → '{change['new_home_team']}'\n"
                    f"  Away: '{change['old_away_team']}' → '{change['new_away_team']}'\n"
                )

            if len(self.changes_made) > 50:
                report_lines.append(f"... and {len(self.changes_made) - 50} more changes")

        report_lines.extend([
            "",
            "=" * 80,
        ])

        report_content = "\n".join(report_lines)

        with open(report_file, 'w') as f:
            f.write(report_content)

        logger.info(f"Report generated: {report_file}")
        print("\n" + report_content)


def main():
    """Main entry point for migration script."""
    parser = argparse.ArgumentParser(
        description="Fix corrupted Kalshi team names in database"
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview changes without executing migration'
    )
    parser.add_argument(
        '--validate',
        action='store_true',
        help='Only validate data quality, do not migrate'
    )
    parser.add_argument(
        '--rollback',
        type=str,
        metavar='BACKUP_FILE',
        help='Rollback using specified backup file'
    )

    args = parser.parse_args()

    migration = KalshiTeamMigration(dry_run=args.dry_run)

    try:
        migration.connect_db()

        if args.rollback:
            # Rollback mode
            restored = migration.rollback_from_backup(args.rollback)
            print(f"\nRollback complete: {restored} records restored")

        elif args.validate:
            # Validation only mode
            stats = migration.validate_data_quality()

            print("\n" + "=" * 80)
            print("DATA QUALITY VALIDATION RESULTS")
            print("=" * 80)
            print(f"Total Records: {stats['total_records']}")
            print(f"Valid Records: {stats['valid_records']}")
            print(f"Corrupted Records: {len(stats['corrupted_records'])} ({stats['corruption_rate']:.1f}%)")
            print(f"  - Corrupted Home Teams: {stats['corrupted_home_team']}")
            print(f"  - Corrupted Away Teams: {stats['corrupted_away_team']}")
            print(f"  - Unparseable Tickers: {stats['unparseable_tickers']}")

            if stats['corrupted_records']:
                print("\nSample Corrupted Records (first 10):")
                for record in stats['corrupted_records'][:10]:
                    print(f"\n  ID: {record['id']}")
                    print(f"  Ticker: {record['ticker']}")
                    print(f"  Home Team: {record['home_team']}")
                    print(f"  Away Team: {record['away_team']}")
                    print(f"  Issues: {', '.join(record['issues'])}")

                if len(stats['corrupted_records']) > 10:
                    print(f"\n  ... and {len(stats['corrupted_records']) - 10} more")

            print("\nRecommendation:")
            if len(stats['corrupted_records']) > 0:
                print("  Run migration to fix corrupted records:")
                print("    python fix_kalshi_team_names_migration.py --dry-run  # Preview changes")
                print("    python fix_kalshi_team_names_migration.py            # Execute migration")
            else:
                print("  No corrupted records found. Database is clean!")

        else:
            # Migration mode
            stats = migration.validate_data_quality()

            if len(stats['corrupted_records']) == 0:
                print("\nNo corrupted records found. Nothing to migrate.")
            else:
                updated_count = migration.execute_migration()
                migration.generate_report(stats, updated_count)

                if args.dry_run:
                    print(f"\n[DRY RUN] Would update {updated_count} records")
                    print("Run without --dry-run to execute migration")
                else:
                    print(f"\nMigration successful: {updated_count} records updated")
                    print(f"Backup saved: {migration.backup_file}")
                    print(f"To rollback: python {__file__} --rollback {migration.backup_file}")

    except Exception as e:
        logger.error(f"Migration failed with error: {e}")
        print(f"\nERROR: {e}")
        return 1

    finally:
        migration.close_db()

    return 0


if __name__ == '__main__':
    exit(main())
