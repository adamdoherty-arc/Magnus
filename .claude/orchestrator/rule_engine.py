"""
Rule Engine - Loads and enforces project rules
Can auto-fix violations when configured
"""
import re
from pathlib import Path
from typing import Dict, Any, List
import logging


class RuleEngine:
    """
    Rule engine for project standards

    Features:
    1. Load rules from config
    2. Check files against rules
    3. Auto-fix violations
    4. Learn new patterns
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize rule engine"""
        self.config = config
        self.logger = logging.getLogger("RuleEngine")
        self.project_root = Path(__file__).parent.parent.parent

        # Load rules
        self.ui_rules = config.get("rules", {}).get("ui", {})
        self.code_rules = config.get("rules", {}).get("code", {})

    def auto_fix(self, violations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Auto-fix violations if possible

        Args:
            violations: List of violations from QA

        Returns:
            Fix results
        """
        results = {
            "fixed": [],
            "not_fixable": [],
            "errors": []
        }

        for violation in violations:
            if not violation.get("auto_fixable", False):
                results["not_fixable"].append(violation)
                continue

            try:
                if violation["rule"] == "no_horizontal_lines":
                    success = self._fix_horizontal_lines(violation["file"])
                    if success:
                        results["fixed"].append(violation)
                    else:
                        results["not_fixable"].append(violation)
                else:
                    results["not_fixable"].append(violation)

            except Exception as e:
                self.logger.error(f"Error fixing {violation['file']}: {e}")
                results["errors"].append({
                    "violation": violation,
                    "error": str(e)
                })

        self.logger.info(f"Auto-fix: {len(results['fixed'])} fixed, "
                        f"{len(results['not_fixable'])} not fixable, "
                        f"{len(results['errors'])} errors")

        return results

    def _fix_horizontal_lines(self, file_path: str) -> bool:
        """Remove horizontal lines from file"""
        try:
            file_path_obj = Path(file_path)

            with open(file_path_obj, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            # Remove lines with st.markdown("---") or st.divider()
            fixed_lines = []
            for line in lines:
                if re.search(r'st\.markdown\(["\']---', line):
                    self.logger.info(f"Removed horizontal line from {file_path}")
                    continue  # Skip this line
                if re.search(r'st\.divider\(\)', line):
                    self.logger.info(f"Removed divider from {file_path}")
                    continue  # Skip this line
                fixed_lines.append(line)

            # Write back
            with open(file_path_obj, 'w', encoding='utf-8') as f:
                f.writelines(fixed_lines)

            return True

        except Exception as e:
            self.logger.error(f"Error fixing horizontal lines in {file_path}: {e}")
            return False

    def check_file(self, file_path: str) -> List[Dict[str, Any]]:
        """
        Check file against all rules

        Args:
            file_path: Path to file to check

        Returns:
            List of violations
        """
        violations = []

        try:
            file_path_obj = Path(file_path)

            if not file_path_obj.exists():
                return violations

            with open(file_path_obj, 'r', encoding='utf-8') as f:
                content = f.read()

            # Check UI rules
            for rule_name, rule_config in self.ui_rules.items():
                violations.extend(self._check_rule(
                    file_path,
                    content,
                    rule_name,
                    rule_config,
                    "ui"
                ))

            # Check code rules
            for rule_name, rule_config in self.code_rules.items():
                violations.extend(self._check_rule(
                    file_path,
                    content,
                    rule_name,
                    rule_config,
                    "code"
                ))

        except Exception as e:
            self.logger.error(f"Error checking file {file_path}: {e}")

        return violations

    def _check_rule(
        self,
        file_path: str,
        content: str,
        rule_name: str,
        rule_config: Dict[str, Any],
        rule_type: str
    ) -> List[Dict[str, Any]]:
        """Check a single rule"""
        violations = []

        patterns = rule_config.get("patterns", [])
        exclude_patterns = rule_config.get("exclude_patterns", [])

        for pattern in patterns:
            matches = re.findall(pattern, content)

            # Check exclude patterns
            filtered_matches = []
            for match in matches:
                excluded = False
                for exclude_pattern in exclude_patterns:
                    if re.search(exclude_pattern, match):
                        excluded = True
                        break
                if not excluded:
                    filtered_matches.append(match)

            if filtered_matches:
                violations.append({
                    "file": file_path,
                    "rule": rule_name,
                    "rule_type": rule_type,
                    "severity": rule_config.get("severity", "medium"),
                    "count": len(filtered_matches),
                    "message": rule_config.get("message", f"Rule {rule_name} violated"),
                    "auto_fixable": rule_config.get("auto_fix", False),
                    "matches": filtered_matches[:5]  # Show first 5 matches
                })

        return violations

    def get_rule_summary(self) -> str:
        """Get summary of all rules"""
        ui_count = len(self.ui_rules)
        code_count = len(self.code_rules)

        summary = [
            f"Rule Engine:",
            f"  UI rules: {ui_count}",
            f"  Code rules: {code_count}",
            f"  Total: {ui_count + code_count}"
        ]

        # List critical rules
        critical = []
        for rule_name, rule_config in {**self.ui_rules, **self.code_rules}.items():
            if rule_config.get("severity") == "critical":
                critical.append(rule_name)

        if critical:
            summary.append(f"  Critical rules: {', '.join(critical)}")

        return "\n".join(summary)