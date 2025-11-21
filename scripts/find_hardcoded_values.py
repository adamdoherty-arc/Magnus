"""
Configuration Migration Helper

Scans Python files to identify hardcoded values that should be moved to configuration files.
Generates a report with recommendations for each finding.
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
from collections import defaultdict


@dataclass
class HardcodedValue:
    """Represents a hardcoded value found in code"""
    file_path: str
    line_number: int
    line_content: str
    value: any
    value_type: str
    context: str
    suggested_config_key: str
    confidence: str  # high, medium, low


class HardcodedValueFinder:
    """Find hardcoded values that should be in configuration"""

    def __init__(self, root_dir: str):
        self.root_dir = Path(root_dir)
        self.findings: List[HardcodedValue] = []

        # Patterns to look for
        self.numeric_patterns = {
            # Common configuration values
            r'refresh_interval\s*=\s*(\d+)': 'Refresh interval',
            r'cache_ttl\s*=\s*(\d+)': 'Cache TTL',
            r'timeout\s*=\s*(\d+)': 'Timeout',
            r'max_results\s*=\s*(\d+)': 'Max results',
            r'rate_limit\s*=\s*(\d+)': 'Rate limit',
            r'max_tokens\s*=\s*(\d+)': 'Max tokens',
            r'temperature\s*=\s*([\d.]+)': 'Temperature',
            r'min_dte\s*=\s*(\d+)': 'Minimum DTE',
            r'max_dte\s*=\s*(\d+)': 'Maximum DTE',
            r'delta\s*=\s*([-\d.]+)': 'Delta value',
            r'min_premium\s*=\s*([\d.]+)': 'Minimum premium',
            r'pool_size\s*=\s*(\d+)': 'Pool size',
        }

        self.string_patterns = {
            r'model\s*=\s*["\']([^"\']+)["\']': 'Model name',
            r'api_base_url\s*=\s*["\']([^"\']+)["\']': 'API base URL',
        }

        self.range_patterns = {
            r'\[(\d+),\s*(\d+)\]': 'Numeric range',
            r'\[([-\d.]+),\s*([-\d.]+)\]': 'Float range',
        }

    def scan_files(self, extensions: List[str] = None) -> List[HardcodedValue]:
        """
        Scan all Python files in the directory for hardcoded values

        Args:
            extensions: List of file extensions to scan (default: ['.py'])

        Returns:
            List of HardcodedValue objects
        """
        if extensions is None:
            extensions = ['.py']

        print(f"Scanning {self.root_dir} for hardcoded values...\n")

        # Get all Python files
        python_files = []
        for ext in extensions:
            python_files.extend(self.root_dir.rglob(f'*{ext}'))

        # Filter out virtual environment and cache files
        python_files = [
            f for f in python_files
            if 'venv' not in str(f) and '__pycache__' not in str(f)
        ]

        print(f"Found {len(python_files)} Python files to scan\n")

        for file_path in python_files:
            self._scan_file(file_path)

        return self.findings

    def _scan_file(self, file_path: Path):
        """Scan a single file for hardcoded values"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            for line_num, line in enumerate(lines, start=1):
                # Skip comments
                if line.strip().startswith('#'):
                    continue

                # Check numeric patterns
                for pattern, context in self.numeric_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1)
                        self._add_finding(
                            file_path=str(file_path.relative_to(self.root_dir.parent)),
                            line_number=line_num,
                            line_content=line.strip(),
                            value=value,
                            value_type='numeric',
                            context=context,
                            confidence='high'
                        )

                # Check string patterns
                for pattern, context in self.string_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        value = match.group(1)
                        # Skip empty strings and common non-config values
                        if value and not self._is_excluded_string(value):
                            self._add_finding(
                                file_path=str(file_path.relative_to(self.root_dir.parent)),
                                line_number=line_num,
                                line_content=line.strip(),
                                value=value,
                                value_type='string',
                                context=context,
                                confidence='medium'
                            )

                # Check range patterns
                for pattern, context in self.range_patterns.items():
                    matches = re.finditer(pattern, line)
                    for match in matches:
                        if len(match.groups()) == 2:
                            value = f"[{match.group(1)}, {match.group(2)}]"
                            self._add_finding(
                                file_path=str(file_path.relative_to(self.root_dir.parent)),
                                line_number=line_num,
                                line_content=line.strip(),
                                value=value,
                                value_type='range',
                                context=context,
                                confidence='high'
                            )

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def _is_excluded_string(self, value: str) -> bool:
        """Check if string should be excluded from findings"""
        excluded = [
            'utf-8', 'localhost', 'http', 'https',
            'GET', 'POST', 'PUT', 'DELETE',
            'True', 'False', 'None',
        ]
        return value in excluded or len(value) < 3

    def _add_finding(self, file_path: str, line_number: int, line_content: str,
                    value: any, value_type: str, context: str, confidence: str):
        """Add a finding to the list"""
        # Generate suggested config key based on context and file
        suggested_key = self._suggest_config_key(file_path, context, value_type)

        finding = HardcodedValue(
            file_path=file_path,
            line_number=line_number,
            line_content=line_content,
            value=value,
            value_type=value_type,
            context=context,
            suggested_config_key=suggested_key,
            confidence=confidence
        )

        self.findings.append(finding)

    def _suggest_config_key(self, file_path: str, context: str, value_type: str) -> str:
        """Suggest a configuration key based on file and context"""
        # Extract page/component name from file path
        path_parts = Path(file_path).parts

        if 'pages' in str(file_path) or '_page.py' in str(file_path):
            # Page configuration
            page_name = Path(file_path).stem.replace('_page', '').replace('_', '')
            if context == 'Refresh interval':
                return f"pages.{page_name}.refresh_interval"
            elif context == 'Max results':
                return f"pages.{page_name}.max_results"
            elif context == 'Cache TTL':
                return f"cache.{page_name}_ttl"
            else:
                key_name = context.lower().replace(' ', '_')
                return f"pages.{page_name}.{key_name}"

        elif 'service' in str(file_path).lower() or 'client' in str(file_path).lower():
            # Service configuration
            service_name = Path(file_path).stem.replace('_service', '').replace('_client', '')
            key_name = context.lower().replace(' ', '_')
            return f"services.{service_name}.{key_name}"

        else:
            # General configuration
            key_name = context.lower().replace(' ', '_')
            return f"app.{key_name}"

    def generate_report(self, output_file: str = None) -> str:
        """
        Generate a migration report

        Args:
            output_file: Optional file path to write report to

        Returns:
            Report string
        """
        # Group findings by file
        by_file = defaultdict(list)
        for finding in self.findings:
            by_file[finding.file_path].append(finding)

        # Build report
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("Configuration Migration Report")
        report_lines.append("=" * 80)
        report_lines.append(f"\nTotal hardcoded values found: {len(self.findings)}")
        report_lines.append(f"Files with hardcoded values: {len(by_file)}")
        report_lines.append("\n")

        # Summary by confidence
        by_confidence = defaultdict(int)
        for finding in self.findings:
            by_confidence[finding.confidence] += 1

        report_lines.append("Confidence Levels:")
        for conf, count in sorted(by_confidence.items()):
            report_lines.append(f"  {conf.upper()}: {count}")
        report_lines.append("\n")

        # Detailed findings by file
        report_lines.append("-" * 80)
        report_lines.append("DETAILED FINDINGS BY FILE")
        report_lines.append("-" * 80)
        report_lines.append("")

        for file_path, findings in sorted(by_file.items()):
            report_lines.append(f"\n📄 {file_path}")
            report_lines.append(f"   {len(findings)} hardcoded value(s) found\n")

            for finding in findings:
                report_lines.append(f"  Line {finding.line_number}: {finding.context}")
                report_lines.append(f"    Value: {finding.value} ({finding.value_type})")
                report_lines.append(f"    Code: {finding.line_content[:80]}")
                report_lines.append(f"    Suggested config: {finding.suggested_config_key}")
                report_lines.append(f"    Confidence: {finding.confidence.upper()}")
                report_lines.append("")

        # Migration steps
        report_lines.append("-" * 80)
        report_lines.append("MIGRATION STEPS")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append("1. Review the findings above")
        report_lines.append("2. Add appropriate values to config YAML files:")
        report_lines.append("   - config/default.yaml (general settings)")
        report_lines.append("   - config/pages.yaml (page-specific settings)")
        report_lines.append("   - config/features.yaml (feature flags)")
        report_lines.append("   - config/services.yaml (external services)")
        report_lines.append("")
        report_lines.append("3. Replace hardcoded values with config manager calls:")
        report_lines.append("   Example:")
        report_lines.append("   Before: max_results = 200")
        report_lines.append("   After:  max_results = get_config().get('pages.ai_agent.max_results', 200)")
        report_lines.append("")
        report_lines.append("4. Test each change to ensure functionality is preserved")
        report_lines.append("5. Add environment variable overrides where needed")
        report_lines.append("")

        # Estimated savings
        report_lines.append("-" * 80)
        report_lines.append("ESTIMATED IMPACT")
        report_lines.append("-" * 80)
        report_lines.append("")
        report_lines.append(f"Lines of hardcoded configuration: ~{len(self.findings)}")
        report_lines.append(f"Potential lines saved: ~{len(self.findings) * 0.5:.0f}")
        report_lines.append(f"Maintainability improvement: HIGH")
        report_lines.append(f"Flexibility improvement: HIGH")
        report_lines.append("")

        report = "\n".join(report_lines)

        # Write to file if specified
        if output_file:
            with open(output_file, 'w') as f:
                f.write(report)
            print(f"\nReport written to: {output_file}")

        return report


def main():
    """Main execution"""
    import sys

    # Get project root directory
    if len(sys.argv) > 1:
        root_dir = sys.argv[1]
    else:
        # Assume script is in scripts/ folder
        root_dir = Path(__file__).parent.parent

    finder = HardcodedValueFinder(root_dir)

    # Scan files
    findings = finder.scan_files()

    # Generate and display report
    output_file = root_dir / "CONFIG_MIGRATION_REPORT.md"
    report = finder.generate_report(str(output_file))

    print(report)

    # Summary
    print("\n" + "=" * 80)
    print(f"✅ Found {len(findings)} hardcoded values across your codebase")
    print(f"📝 Full report saved to: {output_file}")
    print("=" * 80)


if __name__ == "__main__":
    main()
