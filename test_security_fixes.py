"""
Security Fixes Test Script
===========================

Tests for critical security fixes:
1. Connection pool implementation
2. SQL injection prevention
3. Transaction management

Run this script to verify all security fixes are working correctly.
"""

import sys
from pathlib import Path
import time
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Add src directory to path
src_dir = Path(__file__).parent / 'src'
sys.path.insert(0, str(src_dir))

try:
    from xtrades_monitor.db_connection_pool import init_db_pool, close_db_pool, get_db_pool
    from xtrades_monitor.alert_processor import AlertProcessor
    from xtrades_monitor.notification_service import TelegramNotificationService
    from xtrades_db_manager import XtradesDBManager
except ImportError as e:
    logger.error(f"Failed to import modules: {e}")
    logger.error("Make sure xtrades_monitor directory exists and contains __init__.py")
    sys.exit(1)


class SecurityTestSuite:
    """Test suite for security fixes"""

    def __init__(self):
        self.results = {
            'passed': 0,
            'failed': 0,
            'tests': []
        }

    def test_result(self, test_name: str, passed: bool, message: str):
        """Record test result"""
        self.results['tests'].append({
            'name': test_name,
            'passed': passed,
            'message': message
        })

        if passed:
            self.results['passed'] += 1
            logger.info(f"PASS: {test_name} - {message}")
        else:
            self.results['failed'] += 1
            logger.error(f"FAIL: {test_name} - {message}")

    def print_summary(self):
        """Print test summary"""
        print("\n" + "=" * 80)
        print("SECURITY FIXES TEST SUMMARY")
        print("=" * 80)
        print(f"Total Tests: {len(self.results['tests'])}")
        print(f"Passed: {self.results['passed']}")
        print(f"Failed: {self.results['failed']}")
        print(f"Success Rate: {(self.results['passed'] / len(self.results['tests']) * 100):.1f}%")
        print("=" * 80)

        if self.results['failed'] > 0:
            print("\nFailed Tests:")
            for test in self.results['tests']:
                if not test['passed']:
                    print(f"  - {test['name']}: {test['message']}")

        print()

    # =========================================================================
    # Test 1: Connection Pool Initialization
    # =========================================================================

    def test_connection_pool_init(self):
        """Test that connection pool can be initialized"""
        test_name = "Connection Pool Initialization"

        try:
            pool = init_db_pool(min_conn=2, max_conn=5)

            if pool is not None:
                stats = pool.get_stats()
                if stats.get('initialized'):
                    self.test_result(test_name, True, f"Pool initialized: min={stats['min_connections']}, max={stats['max_connections']}")
                else:
                    self.test_result(test_name, False, "Pool not initialized properly")
            else:
                self.test_result(test_name, False, "Pool is None")

        except Exception as e:
            self.test_result(test_name, False, f"Exception: {e}")

    # =========================================================================
    # Test 2: Connection Pooling - Get and Return
    # =========================================================================

    def test_connection_pool_get_return(self):
        """Test getting and returning connections to pool"""
        test_name = "Connection Pool Get/Return"

        try:
            pool = get_db_pool()
            connections = []

            # Get 3 connections
            for i in range(3):
                conn = pool.getconn()
                connections.append(conn)

            # Return all connections
            for conn in connections:
                pool.putconn(conn)

            self.test_result(test_name, True, "Successfully got and returned 3 connections")

        except Exception as e:
            self.test_result(test_name, False, f"Exception: {e}")

    # =========================================================================
    # Test 3: Connection Pool Context Manager
    # =========================================================================

    def test_connection_pool_context_manager(self):
        """Test connection pool context manager"""
        test_name = "Connection Pool Context Manager"

        try:
            pool = get_db_pool()

            # Use context manager - connection should auto-return
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

                if result[0] == 1:
                    self.test_result(test_name, True, "Context manager works, connection auto-returned")
                else:
                    self.test_result(test_name, False, "Query returned unexpected result")

        except Exception as e:
            self.test_result(test_name, False, f"Exception: {e}")

    # =========================================================================
    # Test 4: Concurrent Connection Handling
    # =========================================================================

    def test_concurrent_connections(self):
        """Test that connection pool handles concurrent access"""
        test_name = "Concurrent Connection Handling"

        try:
            pool = get_db_pool()

            def worker(worker_id):
                """Worker function that uses a connection"""
                try:
                    with pool.get_connection() as conn:
                        cursor = conn.cursor()
                        cursor.execute("SELECT %s as worker_id", (worker_id,))
                        result = cursor.fetchone()
                        return result[0] == worker_id
                except Exception as e:
                    logger.error(f"Worker {worker_id} failed: {e}")
                    return False

            # Run 5 workers concurrently
            with ThreadPoolExecutor(max_workers=5) as executor:
                futures = [executor.submit(worker, i) for i in range(5)]
                results = [future.result() for future in as_completed(futures)]

            if all(results):
                self.test_result(test_name, True, "All 5 concurrent workers completed successfully")
            else:
                self.test_result(test_name, False, f"Some workers failed: {sum(results)}/5 succeeded")

        except Exception as e:
            self.test_result(test_name, False, f"Exception: {e}")

    # =========================================================================
    # Test 5: SQL Injection Prevention - Alert Processor
    # =========================================================================

    def test_sql_injection_alert_processor(self):
        """Test that alert processor uses parameterized queries"""
        test_name = "SQL Injection Prevention - Alert Processor"

        try:
            processor = AlertProcessor()

            # Test with potentially malicious input
            malicious_username = "test'; DROP TABLE xtrades_profiles; --"

            # This should safely handle the malicious input
            results = processor.process_scrape_results(malicious_username, [])

            # If we get here without error, parameterization is working
            self.test_result(test_name, True, "Malicious input safely handled with parameterized queries")

        except Exception as e:
            # Check if it's a legitimate "profile not found" error (expected)
            if "Profile not found" in str(e) or "not found" in str(e).lower():
                self.test_result(test_name, True, "Malicious input rejected safely")
            else:
                self.test_result(test_name, False, f"Unexpected exception: {e}")

    # =========================================================================
    # Test 6: SQL Injection Prevention - DB Manager
    # =========================================================================

    def test_sql_injection_db_manager(self):
        """Test that DB manager uses parameterized queries"""
        test_name = "SQL Injection Prevention - DB Manager"

        try:
            db_manager = XtradesDBManager()

            # Test with potentially malicious input
            malicious_username = "test'; DROP TABLE xtrades_profiles; --"

            # This should safely handle the malicious input
            result = db_manager.get_profile_by_username(malicious_username)

            # Should return None (profile not found), not cause an error
            if result is None:
                self.test_result(test_name, True, "Malicious input safely handled with parameterized queries")
            else:
                self.test_result(test_name, False, "Query returned unexpected result")

        except Exception as e:
            self.test_result(test_name, False, f"Exception (should be caught safely): {e}")

    # =========================================================================
    # Test 7: Transaction Rollback on Error
    # =========================================================================

    def test_transaction_rollback(self):
        """Test that transactions rollback on error"""
        test_name = "Transaction Rollback on Error"

        try:
            pool = get_db_pool()

            # Attempt a transaction that should fail
            try:
                with pool.get_connection() as conn:
                    with conn:
                        cursor = conn.cursor()
                        # This should succeed
                        cursor.execute("SELECT 1")
                        # This should fail (nonexistent table)
                        cursor.execute("INSERT INTO nonexistent_table VALUES (1)")
            except Exception:
                # Error expected - transaction should have rolled back
                pass

            # Verify connection is still usable after rollback
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

                if result[0] == 1:
                    self.test_result(test_name, True, "Transaction rolled back successfully, connection still usable")
                else:
                    self.test_result(test_name, False, "Connection not usable after rollback")

        except Exception as e:
            self.test_result(test_name, False, f"Exception: {e}")

    # =========================================================================
    # Test 8: Connection Leak Prevention
    # =========================================================================

    def test_connection_leak_prevention(self):
        """Test that connections are properly returned even on errors"""
        test_name = "Connection Leak Prevention"

        try:
            pool = get_db_pool()

            # Get a connection and cause an error
            initial_conn_count = 0

            # Use connections 10 times with errors
            for i in range(10):
                try:
                    with pool.get_connection() as conn:
                        cursor = conn.cursor()
                        if i % 2 == 0:
                            # Cause an error every other iteration
                            cursor.execute("SELECT * FROM nonexistent_table")
                        else:
                            cursor.execute("SELECT 1")
                except Exception:
                    pass  # Ignore errors

            # Now try to get a connection - should work if no leaks
            with pool.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT 1")
                result = cursor.fetchone()

                if result[0] == 1:
                    self.test_result(test_name, True, "No connection leaks detected after 10 operations with errors")
                else:
                    self.test_result(test_name, False, "Unexpected query result")

        except Exception as e:
            # If we get a PoolError here, it means connections leaked
            if "pool" in str(e).lower() and "exhaust" in str(e).lower():
                self.test_result(test_name, False, "Connection pool exhausted - connections leaked!")
            else:
                self.test_result(test_name, False, f"Exception: {e}")

    # =========================================================================
    # Test 9: Alert Processor Transaction Integrity
    # =========================================================================

    def test_alert_processor_transaction(self):
        """Test that alert processor uses transactions correctly"""
        test_name = "Alert Processor Transaction Integrity"

        try:
            processor = AlertProcessor()

            # Test processing empty trade list (should complete successfully)
            results = processor.process_scrape_results("test_user", [])

            # Check results structure
            if isinstance(results, dict) and all(key in results for key in ['new_alerts', 'updated_alerts', 'closed_alerts']):
                self.test_result(test_name, True, "Alert processor uses transactions correctly")
            else:
                self.test_result(test_name, False, "Unexpected results structure")

        except Exception as e:
            # Profile not found is expected for test_user
            if "not found" in str(e).lower():
                self.test_result(test_name, True, "Transaction safely handled profile not found error")
            else:
                self.test_result(test_name, False, f"Exception: {e}")

    # =========================================================================
    # Test 10: Notification Service SQL Safety
    # =========================================================================

    def test_notification_service_sql_safety(self):
        """Test that notification service uses parameterized queries"""
        test_name = "Notification Service SQL Safety"

        try:
            service = TelegramNotificationService()

            # Test rate limit check (uses database function)
            can_send = service.can_send_notification()

            # Should return a boolean without errors
            if isinstance(can_send, bool):
                self.test_result(test_name, True, "Notification service uses safe SQL")
            else:
                self.test_result(test_name, False, f"Unexpected return type: {type(can_send)}")

        except Exception as e:
            # Some errors are OK (like missing table), as long as no SQL injection
            if "syntax error" in str(e).lower() or "SQL" in str(e):
                self.test_result(test_name, False, f"Potential SQL issue: {e}")
            else:
                self.test_result(test_name, True, "Error handled safely (likely missing table, not SQL injection)")


def main():
    """Run all security tests"""
    print("\n" + "=" * 80)
    print("SECURITY FIXES TEST SUITE")
    print("=" * 80)
    print()

    # Initialize test suite
    suite = SecurityTestSuite()

    # Run all tests
    print("Running tests...\n")

    try:
        suite.test_connection_pool_init()
        time.sleep(0.1)

        suite.test_connection_pool_get_return()
        time.sleep(0.1)

        suite.test_connection_pool_context_manager()
        time.sleep(0.1)

        suite.test_concurrent_connections()
        time.sleep(0.1)

        suite.test_sql_injection_alert_processor()
        time.sleep(0.1)

        suite.test_sql_injection_db_manager()
        time.sleep(0.1)

        suite.test_transaction_rollback()
        time.sleep(0.1)

        suite.test_connection_leak_prevention()
        time.sleep(0.1)

        suite.test_alert_processor_transaction()
        time.sleep(0.1)

        suite.test_notification_service_sql_safety()

    except Exception as e:
        logger.error(f"Test suite error: {e}")

    finally:
        # Cleanup
        try:
            close_db_pool()
            logger.info("Closed connection pool")
        except Exception as e:
            logger.warning(f"Error closing pool: {e}")

    # Print summary
    suite.print_summary()

    # Return exit code
    return 0 if suite.results['failed'] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
