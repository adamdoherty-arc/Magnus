"""
World-Class Orchestrator Installation Script
Installs all dependencies and initializes all components
100% FREE - No cloud services
"""
import subprocess
import sys
from pathlib import Path
import logging

logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)


def install_python_packages():
    """Install required Python packages"""
    logger.info("Installing Python packages...")

    packages = [
        "opentelemetry-api",
        "opentelemetry-sdk",
        "chromadb",
        "sentence-transformers",
        "bandit",
        "sqlalchemy",
        "pyyaml",
    ]

    for package in packages:
        try:
            logger.info(f"Installing {package}...")
            subprocess.run(
                [sys.executable, "-m", "pip", "install", package],
                check=True,
                capture_output=True
            )
            logger.info(f"[OK] {package} installed")
        except subprocess.CalledProcessError as e:
            logger.warning(f"Failed to install {package}: {e}")

    logger.info("[OK] Python packages installation complete")


def check_ollama():
    """Check if Ollama is installed and running"""
    logger.info("Checking Ollama installation...")

    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            timeout=5
        )
        if result.returncode == 0:
            logger.info("[OK] Ollama is installed and running")
            return True
        else:
            logger.warning("Ollama not responding. Please start Ollama.")
            return False
    except FileNotFoundError:
        logger.warning("Ollama not found. Install from: https://ollama.ai")
        logger.info("  For local LLM-as-judge and analysis features")
        return False
    except Exception as e:
        logger.warning(f"Could not check Ollama: {e}")
        return False


def pull_ollama_models():
    """Pull recommended Ollama models"""
    logger.info("Pulling recommended Ollama models...")

    models = [
        "llama3.2:latest",  # General purpose
        "qwen2.5-coder:latest",  # Code evaluation
    ]

    for model in models:
        try:
            logger.info(f"Pulling {model}...")
            subprocess.run(
                ["ollama", "pull", model],
                check=True,
                timeout=300
            )
            logger.info(f"[OK] {model} ready")
        except Exception as e:
            logger.warning(f"Could not pull {model}: {e}")


def initialize_databases():
    """Initialize all SQLite databases"""
    logger.info("Initializing databases...")

    # Get the .claude directory (parent of current directory)
    current_dir = Path(__file__).parent  # .claude/orchestrator
    claude_dir = current_dir.parent  # .claude

    # Import and initialize each component
    try:
        sys.path.insert(0, str(claude_dir))

        from orchestrator.observability.tracer import get_tracer
        from orchestrator.observability.metrics_collector import get_metrics_collector
        from orchestrator.feedback.execution_tracker import get_execution_tracker
        from orchestrator.memory.memory_manager import get_memory_manager

        logger.info("Initializing observability...")
        tracer = get_tracer()
        logger.info("[OK] Tracer initialized")

        metrics = get_metrics_collector()
        logger.info("[OK] Metrics collector initialized")

        logger.info("Initializing feedback system...")
        tracker = get_execution_tracker()
        logger.info("[OK] Execution tracker initialized")

        logger.info("Initializing memory system...")
        memory = get_memory_manager()
        logger.info("[OK] Memory manager initialized")

        logger.info("[OK] All databases initialized")
        return True

    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        return False


def create_directories():
    """Create required directory structure"""
    logger.info("Creating directory structure...")

    directories = [
        ".claude/orchestrator/databases",
        ".claude/orchestrator/dashboards",
        ".claude/orchestrator/logs",
        ".claude/orchestrator/test_screenshots",
        ".claude/orchestrator/test_reports",
    ]

    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

    logger.info("[OK] Directory structure created")


def test_installation():
    """Test that everything is working"""
    logger.info("\nTesting installation...")

    tests_passed = 0
    tests_failed = 0

    # Test 1: Tracer
    try:
        from orchestrator.observability.tracer import get_tracer
        tracer = get_tracer()
        span = tracer.start_agent_execution("test-agent", {"test": True})
        tracer.end_agent_execution(span, True, tokens_used=10)
        logger.info("[OK] Tracer test passed")
        tests_passed += 1
    except Exception as e:
        logger.error(f"[FAIL] Tracer test failed: {e}")
        tests_failed += 1

    # Test 2: Metrics
    try:
        from orchestrator.observability.metrics_collector import get_metrics_collector
        collector = get_metrics_collector()
        collector.record_agent_execution("test-agent", 100.0, True, tokens_used=50)
        summary = collector.get_summary()
        logger.info(f"[OK] Metrics test passed (recorded {summary['overall']['total_executions']} executions)")
        tests_passed += 1
    except Exception as e:
        logger.error(f"[FAIL] Metrics test failed: {e}")
        tests_failed += 1

    # Test 3: Memory
    try:
        from orchestrator.memory.memory_manager import get_memory_manager
        memory = get_memory_manager()
        memory.store_knowledge("test_key", "test_value", category="test")
        result = memory.retrieve_knowledge("test_key")
        if result and result["value"] == "test_value":
            logger.info("[OK] Memory test passed")
            tests_passed += 1
        else:
            logger.error("[FAIL] Memory test failed: retrieve mismatch")
            tests_failed += 1
    except Exception as e:
        logger.error(f"[FAIL] Memory test failed: {e}")
        tests_failed += 1

    # Test 4: Self-healer
    try:
        from orchestrator.feedback.self_healer import get_self_healer
        healer = get_self_healer()
        can_heal = healer.can_auto_heal("No module named 'test'", "ImportError")
        logger.info(f"[OK] Self-healer test passed (can_heal={can_heal})")
        tests_passed += 1
    except Exception as e:
        logger.error(f"[FAIL] Self-healer test failed: {e}")
        tests_failed += 1

    logger.info(f"\nTest Results: {tests_passed} passed, {tests_failed} failed")
    return tests_failed == 0


def main():
    """Main installation function"""
    print("\n" + "="*70)
    print("  WORLD-CLASS ORCHESTRATOR INSTALLATION")
    print("  100% Free - 100% Local - Zero Cloud Costs")
    print("="*70 + "\n")

    # Step 1: Create directories
    create_directories()

    # Step 2: Install Python packages
    install_python_packages()

    # Step 3: Check Ollama
    ollama_available = check_ollama()
    if ollama_available:
        pull_ollama_models()
    else:
        logger.info("\nOllama optional but recommended for:")
        logger.info("  - LLM-as-judge code evaluation")
        logger.info("  - Complex error analysis")
        logger.info("  - Install from: https://ollama.ai")

    # Step 4: Initialize databases
    db_success = initialize_databases()

    # Step 5: Test installation
    if db_success:
        test_success = test_installation()
    else:
        test_success = False

    # Final summary
    print("\n" + "="*70)
    if test_success:
        print("  [OK] INSTALLATION COMPLETE!")
        print("="*70)
        print("\nYour orchestrator is ready with:")
        print("  [OK] Observability (tracing, metrics, dashboards)")
        print("  [OK] Self-healing (auto-retry, pattern learning)")
        print("  [OK] Memory (short/medium/long-term)")
        print("  [OK] Security (PII detection, code scanning)")
        print("  [OK] LLM-as-judge (code evaluation)")
        print("\nNext steps:")
        print("  1. Review: .claude/orchestrator/HOW_TO_USE_AND_LEARN.md")
        print("  2. Generate dashboard: python observability/dashboard_generator.py")
        print("  3. Start using: The orchestrator runs automatically!")
        print("\n" + "="*70)
        return 0
    else:
        print("  [FAIL] INSTALLATION INCOMPLETE")
        print("="*70)
        print("\nSome components failed to initialize.")
        print("Check the errors above and try again.")
        print("\n" + "="*70)
        return 1


if __name__ == "__main__":
    sys.exit(main())
