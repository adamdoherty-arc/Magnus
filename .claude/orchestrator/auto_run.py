#!/usr/bin/env python3
"""
Auto-Run Wrapper for Claude Code Integration
This makes the orchestrator run automatically on every request

Usage: Add to your Claude Code workflow/hooks
"""
import sys
import os
from pathlib import Path

# Add orchestrator directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main_orchestrator import get_orchestrator


def check_request(request: str, context: dict = None) -> tuple[bool, str]:
    """
    Check a request against orchestrator rules

    Returns:
        (should_proceed, message)
    """
    orchestrator = get_orchestrator()
    result = orchestrator.orchestrate(request, context or {})

    # Check if validation passed
    if not result.validation_results.get("passed", True):
        errors = result.validation_results.get("errors", [])
        message = "\n".join([
            "ORCHESTRATOR: Pre-flight validation FAILED",
            "",
            "Violations:",
            *[f"  - {error}" for error in errors],
            "",
            "Please revise your request or acknowledge you want to bypass these rules."
        ])
        return False, message

    # Validation passed - provide context
    parts = ["ORCHESTRATOR: Pre-flight validation PASSED"]

    if result.features_involved:
        parts.append(f"Features: {', '.join(result.features_involved)}")

    if result.specialist_agents:
        parts.append(f"Recommended agents: {', '.join(result.specialist_agents)}")

    if result.rules_to_enforce:
        parts.append(f"Rules active: {', '.join(result.rules_to_enforce)}")

    if result.validation_results.get("warnings"):
        parts.append("\nWarnings:")
        for warning in result.validation_results["warnings"]:
            parts.append(f"  - {warning}")

    return True, "\n".join(parts)


def auto_validate(request: str) -> None:
    """
    Automatically validate request and print guidance
    Used by Claude Code to check requests
    """
    should_proceed, message = check_request(request)

    print(message)

    if not should_proceed:
        sys.exit(1)  # Exit with error to signal validation failure

    sys.exit(0)  # Exit successfully


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python auto_run.py 'your request here'")
        sys.exit(1)

    request = " ".join(sys.argv[1:])
    auto_validate(request)
