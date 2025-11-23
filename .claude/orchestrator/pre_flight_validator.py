"""
Pre-Flight Validator - Validates requests before execution
Checks against project rules, specs, and known anti-patterns
"""
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
import logging


class PreFlightValidator:
    """
    Pre-flight validation before code execution

    Checks:
    1. UI style guide compliance
    2. Known anti-patterns
    3. Feature spec existence
    4. Breaking change detection
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize validator"""
        self.config = config
        self.logger = logging.getLogger("PreFlightValidator")
        self.project_root = Path(__file__).parent.parent.parent

        # Load rules
        self.ui_rules = config.get("rules", {}).get("ui", {})
        self.code_rules = config.get("rules", {}).get("code", {})

    def validate(
        self,
        request: str,
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run pre-flight validation

        Args:
            request: User's request
            context: Current context (files, state, etc.)

        Returns:
            Validation results with passed/failed status
        """
        results = {
            "passed": True,
            "errors": [],
            "warnings": [],
            "features": [],
            "rules": [],
            "agents": [],
            "context_injected": {}
        }

        try:
            # Check 1: Known anti-patterns in request
            self._check_anti_patterns(request, results)

            # Check 2: If modifying files, check against rules
            if context.get("files"):
                self._check_file_rules(context["files"], results)

            # Check 3: Identify features involved
            if context.get("files"):
                results["features"] = self._identify_features(context["files"])

            # Check 4: Load relevant specs
            if results["features"]:
                specs = self._load_feature_specs(results["features"])
                results["context_injected"]["specs"] = specs

            # Check 5: Identify required specialist agents
            if results["features"]:
                results["agents"] = self._get_specialist_agents(results["features"])

            # Check 6: Validate against feature-specific rules
            if results["features"]:
                self._check_feature_rules(results["features"], results)

            # Set overall pass/fail
            results["passed"] = len(results["errors"]) == 0

            if not results["passed"]:
                self.logger.warning(f"Pre-flight validation failed with {len(results['errors'])} errors")
            else:
                self.logger.info(f"Pre-flight validation passed")

            return results

        except Exception as e:
            self.logger.error(f"Pre-flight validation error: {e}", exc_info=True)
            results["passed"] = False
            results["errors"].append(f"Validation error: {str(e)}")
            return results

    def _check_anti_patterns(self, request: str, results: Dict[str, Any]):
        """Check for known anti-patterns in request"""
        request_lower = request.lower()

        # Anti-pattern: Horizontal lines
        forbidden_phrases = ["add divider", "add separator", "add ---", "horizontal line", "horizontal divider"]
        if any(phrase in request_lower for phrase in forbidden_phrases):
            results["errors"].append(
                "FORBIDDEN: Request contains horizontal line/divider. "
                "See UI_STYLE_GUIDE.md - NO horizontal lines allowed."
            )
            results["rules"].append("no_horizontal_lines")

        # Anti-pattern: Hardcoded deltas
        if "delta" in request_lower and any(word in request_lower for word in ["estimate", "hardcode", "assume"]):
            results["warnings"].append(
                "WARNING: Request mentions delta estimation. Use real Greeks from API instead."
            )
            results["rules"].append("use_real_greeks")

    def _check_file_rules(self, files: List[str], results: Dict[str, Any]):
        """Check files against project rules"""
        for file_path in files:
            if file_path.endswith(".py"):
                # Check if it's a page file
                if "_page" in file_path:
                    results["rules"].append("no_horizontal_lines")
                    results["context_injected"]["ui_style_guide"] = str(
                        self.project_root / "UI_STYLE_GUIDE.md"
                    )

    def _identify_features(self, files: List[str]) -> List[str]:
        """Identify features from file paths"""
        features = set()

        # Load feature registry
        registry_path = self.project_root / ".claude" / "orchestrator" / "feature_registry.yaml"
        if not registry_path.exists():
            return []

        import yaml
        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        for file_path in files:
            file_name = Path(file_path).name
            for feature_name, feature_config in registry.get("features", {}).items():
                if file_name in feature_config.get("pages", []):
                    features.add(feature_name)

        return list(features)

    def _load_feature_specs(self, features: List[str]) -> Dict[str, str]:
        """Load specifications for features"""
        specs = {}

        for feature in features:
            spec_path = self.project_root / ".claude" / "specs" / feature
            if spec_path.exists():
                # Look for requirements.md, design.md, etc.
                for spec_file in ["requirements.md", "design.md", "tasks.md"]:
                    file_path = spec_path / spec_file
                    if file_path.exists():
                        specs[f"{feature}/{spec_file}"] = str(file_path)

        return specs

    def _get_specialist_agents(self, features: List[str]) -> List[str]:
        """Get specialist agents for features"""
        agents = set()

        # Load feature registry
        registry_path = self.project_root / ".claude" / "orchestrator" / "feature_registry.yaml"
        if not registry_path.exists():
            return []

        import yaml
        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        for feature in features:
            feature_config = registry.get("features", {}).get(feature, {})
            specialist = feature_config.get("specialist_agent")
            if specialist:
                agents.add(specialist)

        return list(agents)

    def _check_feature_rules(self, features: List[str], results: Dict[str, Any]):
        """Check feature-specific rules"""
        # Load feature registry
        registry_path = self.project_root / ".claude" / "orchestrator" / "feature_registry.yaml"
        if not registry_path.exists():
            return

        import yaml
        with open(registry_path) as f:
            registry = yaml.safe_load(f)

        for feature in features:
            feature_config = registry.get("features", {}).get(feature, {})
            critical_rules = feature_config.get("critical_rules", [])

            for rule in critical_rules:
                if rule not in results["rules"]:
                    results["rules"].append(rule)

    def get_validation_summary(self, results: Dict[str, Any]) -> str:
        """Get human-readable validation summary"""
        summary = []

        if results["passed"]:
            summary.append("[PASS] Pre-flight validation PASSED")
        else:
            summary.append("[FAIL] Pre-flight validation FAILED")

        if results["errors"]:
            summary.append("\nErrors:")
            for error in results["errors"]:
                summary.append(f"  {error}")

        if results["warnings"]:
            summary.append("\nWarnings:")
            for warning in results["warnings"]:
                summary.append(f"  {warning}")

        if results["features"]:
            summary.append(f"\nFeatures involved: {', '.join(results['features'])}")

        if results["agents"]:
            summary.append(f"Specialist agents: {', '.join(results['agents'])}")

        if results["rules"]:
            summary.append(f"Rules enforced: {', '.join(results['rules'])}")

        return "\n".join(summary)
