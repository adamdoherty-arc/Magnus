#!/usr/bin/env python3
"""
MCP Server for Main Orchestrator
Provides orchestrator as a tool that Claude Code can call automatically
"""
import sys
from pathlib import Path
import json
import asyncio

# Add orchestrator directory to path
sys.path.insert(0, str(Path(__file__).parent))

from main_orchestrator import get_orchestrator


async def validate_request(request: str, context: dict = None) -> dict:
    """
    Validate a request before execution

    Args:
        request: The user's request/query
        context: Additional context (files, etc.)

    Returns:
        Validation result with pass/fail and guidance
    """
    orchestrator = get_orchestrator()
    result = orchestrator.orchestrate(request, context or {})

    return {
        "passed": result.validation_results.get("passed", True),
        "errors": result.validation_results.get("errors", []),
        "warnings": result.validation_results.get("warnings", []),
        "features": result.features_involved,
        "specialist_agents": result.specialist_agents,
        "rules": result.rules_to_enforce,
        "context": result.validation_results.get("context_injected", {}),
        "message": _format_validation_message(result)
    }


async def run_qa(files: list) -> dict:
    """
    Run QA checks on modified files

    Args:
        files: List of file paths that were modified

    Returns:
        QA results with violations
    """
    orchestrator = get_orchestrator()
    result = orchestrator.post_execution_qa(files)

    return {
        "passed": result.get("passed", False),
        "violations": result.get("violations", []),
        "warnings": result.get("warnings", []),
        "checks_run": result.get("checks_run", []),
        "message": _format_qa_message(result)
    }


async def get_feature_context(files: list) -> dict:
    """
    Get feature context for files

    Args:
        files: List of file paths

    Returns:
        Feature information and specs
    """
    orchestrator = get_orchestrator()
    features = orchestrator.identify_features(files)
    agents = orchestrator.get_specialist_agents(features)

    return {
        "features": features,
        "specialist_agents": agents,
        "specs": _get_specs_for_features(features)
    }


def _format_validation_message(result) -> str:
    """Format validation result as human-readable message"""
    if result.validation_results.get("passed"):
        msg = ["[PASS] Pre-flight validation PASSED"]

        if result.features_involved:
            msg.append(f"\nFeatures: {', '.join(result.features_involved)}")

        if result.specialist_agents:
            msg.append(f"Specialist agents: {', '.join(result.specialist_agents)}")

        if result.rules_to_enforce:
            msg.append(f"Rules enforced: {', '.join(result.rules_to_enforce)}")

        return "\n".join(msg)
    else:
        msg = ["[FAIL] Pre-flight validation FAILED\n"]

        errors = result.validation_results.get("errors", [])
        for error in errors:
            msg.append(f"ERROR: {error}")

        warnings = result.validation_results.get("warnings", [])
        for warning in warnings:
            msg.append(f"WARNING: {warning}")

        return "\n".join(msg)


def _format_qa_message(result) -> str:
    """Format QA result as human-readable message"""
    if result.get("passed"):
        return f"[PASS] QA validation PASSED - {result.get('files_checked', 0)} files checked"
    else:
        violations = result.get("violations", [])
        msg = [f"[FAIL] QA validation FAILED - {len(violations)} violations found\n"]

        for v in violations[:5]:  # Show first 5
            msg.append(f"  [{v.get('severity', 'unknown')}] {v.get('file', 'unknown')}: {v.get('message', '')}")

        if len(violations) > 5:
            msg.append(f"  ... and {len(violations) - 5} more")

        return "\n".join(msg)


def _get_specs_for_features(features: list) -> dict:
    """Get spec file paths for features"""
    specs = {}
    project_root = Path(__file__).parent.parent.parent

    for feature in features:
        spec_dir = project_root / ".claude" / "specs" / feature
        if spec_dir.exists():
            feature_specs = {}
            for spec_file in ["requirements.md", "design.md", "tasks.md"]:
                spec_path = spec_dir / spec_file
                if spec_path.exists():
                    feature_specs[spec_file] = str(spec_path)
            specs[feature] = feature_specs

    return specs


# CLI interface for testing
if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Orchestrator MCP Server")
    parser.add_argument("--validate", type=str, help="Validate a request")
    parser.add_argument("--qa", nargs="+", help="Run QA on files")
    parser.add_argument("--context", nargs="+", help="Get feature context for files")

    args = parser.parse_args()

    if args.validate:
        result = asyncio.run(validate_request(args.validate))
        print(json.dumps(result, indent=2))
    elif args.qa:
        result = asyncio.run(run_qa(args.qa))
        print(json.dumps(result, indent=2))
    elif args.context:
        result = asyncio.run(get_feature_context(args.context))
        print(json.dumps(result, indent=2))
    else:
        parser.print_help()
