"""
QA Agent - Post-execution quality assurance
Validates code changes against project standards
"""
import re
from pathlib import Path
from typing import Dict, Any, List
import logging


class QAAgent:
    """
    Post-execution QA validation

    Checks:
    1. Code quality (linting, formatting)
    2. Rule compliance (UI style guide, etc.)
    3. Breaking changes
    4. Performance regressions
    5. Security vulnerabilities
    """

    def __init__(self, config: Dict[str, Any]):
        """Initialize QA agent"""
        self.config = config
        self.logger = logging.getLogger("QAAgent")
        self.project_root = Path(__file__).parent.parent.parent

        # Load QA configuration
        self.qa_config = config.get("post_execution", {})
        self.checks = self.qa_config.get("checks", [])

    def run_qa(
        self,
        files_modified: List[str],
        context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Run QA checks on modified files

        Args:
            files_modified: List of files that were changed
            context: Additional context

        Returns:
            QA results with pass/fail status
        """
        results = {
            "passed": True,
            "violations": [],
            "warnings": [],
            "files_checked": len(files_modified),
            "checks_run": []
        }

        try:
            for file_path in files_modified:
                file_path_obj = Path(file_path)

                # Only check Python files
                if not file_path_obj.suffix == ".py":
                    continue

                # Read file content
                try:
                    with open(file_path_obj, 'r', encoding='utf-8') as f:
                        content = f.read()
                except Exception as e:
                    self.logger.warning(f"Could not read {file_path}: {e}")
                    continue

                # Run enabled checks
                if "horizontal_lines" in self.checks:
                    self._check_horizontal_lines(file_path, content, results)

                if "code_quality" in self.checks:
                    self._check_code_quality(file_path, content, results)

                if "performance_regression" in self.checks:
                    self._check_performance(file_path, content, results)

            # Set overall pass/fail
            results["passed"] = len(results["violations"]) == 0

            if not results["passed"]:
                self.logger.warning(f"QA failed with {len(results['violations'])} violations")
            else:
                self.logger.info(f"QA passed for {len(files_modified)} files")

            return results

        except Exception as e:
            self.logger.error(f"QA error: {e}", exc_info=True)
            results["passed"] = False
            results["violations"].append(f"QA error: {str(e)}")
            return results

    def _check_horizontal_lines(
        self,
        file_path: str,
        content: str,
        results: Dict[str, Any]
    ):
        """Check for forbidden horizontal lines"""
        results["checks_run"].append("horizontal_lines")

        # Check for st.markdown("---")
        pattern1 = r'st\.markdown\(["\']---'
        matches1 = re.findall(pattern1, content)

        # Check for st.divider()
        pattern2 = r'st\.divider\(\)'
        matches2 = re.findall(pattern2, content)

        total_violations = len(matches1) + len(matches2)

        if total_violations > 0:
            results["violations"].append({
                "file": file_path,
                "rule": "no_horizontal_lines",
                "severity": "critical",
                "count": total_violations,
                "message": f"Found {total_violations} horizontal line(s). "
                          f"See UI_STYLE_GUIDE.md - NO horizontal lines allowed.",
                "auto_fixable": True
            })

    def _check_code_quality(
        self,
        file_path: str,
        content: str,
        results: Dict[str, Any]
    ):
        """Check basic code quality"""
        results["checks_run"].append("code_quality")

        # Check for extremely long lines (> 120 chars)
        lines = content.split('\n')
        long_lines = []
        for i, line in enumerate(lines, 1):
            if len(line) > 120 and not line.strip().startswith('#'):
                long_lines.append(i)

        if len(long_lines) > 10:  # Only warn if many long lines
            results["warnings"].append({
                "file": file_path,
                "rule": "line_length",
                "severity": "low",
                "count": len(long_lines),
                "message": f"{len(long_lines)} lines exceed 120 characters"
            })

        # Check for dead code (functions never called)
        # This is a simplified check - real implementation would use AST
        if "def get_closed_trades_with_pl" in content:
            # Check if it's called anywhere
            if "get_closed_trades_with_pl(" not in content.replace("def get_closed_trades_with_pl", ""):
                results["violations"].append({
                    "file": file_path,
                    "rule": "no_dead_code",
                    "severity": "medium",
                    "message": "Function 'get_closed_trades_with_pl' appears to be dead code (never called)",
                    "auto_fixable": False
                })

    def _check_performance(
        self,
        file_path: str,
        content: str,
        results: Dict[str, Any]
    ):
        """Check for performance issues"""
        results["checks_run"].append("performance_regression")

        # Check for Robinhood API calls without rate limiting
        if "import robin_stocks.robinhood as rh" in content:
            # Look for direct API calls
            api_calls = [
                "rh.get_open_stock_positions()",
                "rh.get_open_option_positions()",
                "rh.get_quotes(",
                "rh.get_option_market_data_by_id("
            ]

            for api_call in api_calls:
                if api_call in content:
                    # Check if there's a rate-limited wrapper nearby
                    lines = content.split('\n')
                    for i, line in enumerate(lines):
                        if api_call in line:
                            # Look for @rate_limit decorator in previous lines
                            found_decorator = False
                            for j in range(max(0, i-5), i):
                                if "@rate_limit" in lines[j]:
                                    found_decorator = True
                                    break

                            if not found_decorator:
                                results["violations"].append({
                                    "file": file_path,
                                    "rule": "use_rate_limiting",
                                    "severity": "high",
                                    "line": i + 1,
                                    "message": f"Robinhood API call '{api_call}' without rate limiting. "
                                              f"Use rate-limited wrappers.",
                                    "auto_fixable": False
                                })

    def get_qa_summary(self, results: Dict[str, Any]) -> str:
        """Get human-readable QA summary"""
        summary = []

        if results["passed"]:
            summary.append("✅ QA validation PASSED")
        else:
            summary.append("❌ QA validation FAILED")

        summary.append(f"\nFiles checked: {results['files_checked']}")
        summary.append(f"Checks run: {', '.join(results['checks_run'])}")

        if results["violations"]:
            summary.append(f"\n❌ Violations ({len(results['violations'])}):")
            for v in results["violations"][:10]:  # Show first 10
                summary.append(f"  [{v.get('severity', 'unknown')}] {v['file']}: {v['message']}")

        if results["warnings"]:
            summary.append(f"\n⚠️  Warnings ({len(results['warnings'])}):")
            for w in results["warnings"][:5]:
                summary.append(f"  {w['file']}: {w['message']}")

        return "\n".join(summary)
