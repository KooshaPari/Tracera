#!/usr/bin/env python3
"""
Security Policy Enforcer
Enforces security policies and generates compliance reports.
"""

import argparse
import json
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any


@dataclass
class SecurityViolation:
    """Represents a security policy violation."""
    severity: str
    category: str
    file: str
    line: int
    message: str
    suggestion: str
    policy_id: str


class SecurityPolicyEnforcer:
    """Enforces security policies across the codebase."""

    def __init__(self):
        self.violations = []
        self.policies = self._load_security_policies()

    def _load_security_policies(self) -> dict[str, Any]:
        """Load security policies configuration."""
        return {
            "password_policies": {
                "min_length": 12,
                "require_uppercase": True,
                "require_lowercase": True,
                "require_numbers": True,
                "require_special": True,
                "forbidden_patterns": ["password", "123456", "admin"],
            },
            "api_security": {
                "require_https": True,
                "require_authentication": True,
                "forbidden_headers": ["X-Forwarded-For", "X-Real-IP"],
                "required_headers": ["Authorization", "Content-Type"],
            },
            "data_protection": {
                "encrypt_sensitive_data": True,
                "no_hardcoded_secrets": True,
                "pii_detection": True,
                "data_retention": True,
            },
            "code_security": {
                "no_eval": True,
                "no_exec": True,
                "no_shell_injection": True,
                "no_sql_injection": True,
                "input_validation": True,
            },
            "dependency_security": {
                "vulnerability_scan": True,
                "license_compliance": True,
                "outdated_packages": True,
                "malicious_packages": True,
            },
        }

    def enforce_policies(self, target_path: str) -> dict[str, Any]:
        """Enforce all security policies."""
        print("🔒 Enforcing security policies...")

        target = Path(target_path)

        # Run different security checks
        self._check_password_policies(target)
        self._check_api_security(target)
        self._check_data_protection(target)
        self._check_code_security(target)
        self._check_dependency_security(target)

        # Generate compliance report
        compliance_score = self._calculate_compliance_score()

        return {
            "timestamp": datetime.now().isoformat(),
            "target_path": str(target),
            "total_violations": len(self.violations),
            "compliance_score": compliance_score,
            "violations": [
                {
                    "severity": v.severity,
                    "category": v.category,
                    "file": v.file,
                    "line": v.line,
                    "message": v.message,
                    "suggestion": v.suggestion,
                    "policy_id": v.policy_id,
                }
                for v in self.violations
            ],
            "summary": self._generate_summary(),
        }

    def _check_password_policies(self, target: Path) -> None:
        """Check password-related security policies."""
        policies = self.policies["password_policies"]

        # Check for hardcoded passwords
        for py_file in target.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                    for i, line in enumerate(lines, 1):
                        # Check for password patterns
                        if re.search(r'password\s*=\s*["\'][^"\']+["\']', line, re.IGNORECASE):
                            self.violations.append(SecurityViolation(
                                severity="high",
                                category="password_policies",
                                file=str(py_file),
                                line=i,
                                message="Hardcoded password detected",
                                suggestion="Use environment variables or secure configuration",
                                policy_id="PWD-001",
                            ))

                        # Check for weak passwords
                        if re.search(r'password\s*=\s*["\']([^"\']+)["\']', line, re.IGNORECASE):
                            password = re.search(r'password\s*=\s*["\']([^"\']+)["\']', line, re.IGNORECASE).group(1)
                            if self._is_weak_password(password, policies):
                                self.violations.append(SecurityViolation(
                                    severity="medium",
                                    category="password_policies",
                                    file=str(py_file),
                                    line=i,
                                    message=f"Weak password detected: {password}",
                                    suggestion="Use strong passwords with mixed case, numbers, and special characters",
                                    policy_id="PWD-002",
                                ))
            except Exception as e:
                print(f"Warning: Could not check {py_file}: {e}")

    def _is_weak_password(self, password: str, policies: dict[str, Any]) -> bool:
        """Check if password is weak according to policies."""
        if len(password) < policies["min_length"]:
            return True

        if policies["require_uppercase"] and not re.search(r"[A-Z]", password):
            return True

        if policies["require_lowercase"] and not re.search(r"[a-z]", password):
            return True

        if policies["require_numbers"] and not re.search(r"\d", password):
            return True

        if policies["require_special"] and not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
            return True

        for pattern in policies["forbidden_patterns"]:
            if pattern.lower() in password.lower():
                return True

        return False

    def _check_api_security(self, target: Path) -> None:
        """Check API security policies."""
        policies = self.policies["api_security"]

        for py_file in target.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                    for i, line in enumerate(lines, 1):
                        # Check for HTTP instead of HTTPS
                        if re.search(r"http://", line) and not re.search(r"localhost|127\.0\.0\.1", line):
                            self.violations.append(SecurityViolation(
                                severity="high",
                                category="api_security",
                                file=str(py_file),
                                line=i,
                                message="HTTP used instead of HTTPS",
                                suggestion="Use HTTPS for all external API calls",
                                policy_id="API-001",
                            ))

                        # Check for missing authentication
                        if re.search(r"requests\.(get|post|put|delete)", line) and not re.search(r"auth|headers.*Authorization", line):
                            self.violations.append(SecurityViolation(
                                severity="medium",
                                category="api_security",
                                file=str(py_file),
                                line=i,
                                message="API call without authentication",
                                suggestion="Add proper authentication headers",
                                policy_id="API-002",
                            ))
            except Exception as e:
                print(f"Warning: Could not check {py_file}: {e}")

    def _check_data_protection(self, target: Path) -> None:
        """Check data protection policies."""
        policies = self.policies["data_protection"]

        # PII patterns
        pii_patterns = {
            "email": r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b",
            "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
            "credit_card": r"\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b",
            "phone": r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b",
        }

        for py_file in target.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                    for i, line in enumerate(lines, 1):
                        for pii_type, pattern in pii_patterns.items():
                            if re.search(pattern, line):
                                self.violations.append(SecurityViolation(
                                    severity="high",
                                    category="data_protection",
                                    file=str(py_file),
                                    line=i,
                                    message=f"Potential PII detected: {pii_type}",
                                    suggestion="Remove or encrypt sensitive data",
                                    policy_id="DATA-001",
                                ))
            except Exception as e:
                print(f"Warning: Could not check {py_file}: {e}")

    def _check_code_security(self, target: Path) -> None:
        """Check code security policies."""
        policies = self.policies["code_security"]

        dangerous_patterns = {
            "eval": (r"\beval\s*\(", "Use of eval() function"),
            "exec": (r"\bexec\s*\(", "Use of exec() function"),
            "shell_injection": (r"os\.system|subprocess\.call.*shell=True", "Potential shell injection"),
            "sql_injection": (r'execute\s*\(\s*["\'].*%s', "Potential SQL injection"),
        }

        for py_file in target.rglob("*.py"):
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")

                    for i, line in enumerate(lines, 1):
                        for pattern_name, (pattern, message) in dangerous_patterns.items():
                            if re.search(pattern, line):
                                self.violations.append(SecurityViolation(
                                    severity="high",
                                    category="code_security",
                                    file=str(py_file),
                                    line=i,
                                    message=message,
                                    suggestion="Use safer alternatives",
                                    policy_id="CODE-001",
                                ))
            except Exception as e:
                print(f"Warning: Could not check {py_file}: {e}")

    def _check_dependency_security(self, target: Path) -> None:
        """Check dependency security."""
        try:
            # Run safety check
            result = subprocess.run(
                ["safety", "check", "--json"],
                check=False, capture_output=True,
                text=True,
                cwd=target,
            )

            if result.returncode != 0:
                try:
                    safety_data = json.loads(result.stdout)
                    for vuln in safety_data:
                        self.violations.append(SecurityViolation(
                            severity="high",
                            category="dependency_security",
                            file="requirements.txt",
                            line=0,
                            message=f"Vulnerable dependency: {vuln.get('package', 'unknown')}",
                            suggestion=f"Update to version {vuln.get('safe_version', 'latest')}",
                            policy_id="DEP-001",
                        ))
                except json.JSONDecodeError:
                    pass
        except FileNotFoundError:
            print("Warning: safety not installed, skipping dependency check")

    def _calculate_compliance_score(self) -> float:
        """Calculate security compliance score."""
        if not self.violations:
            return 100.0

        # Weight violations by severity
        severity_weights = {"high": 3, "medium": 2, "low": 1}
        total_weight = sum(severity_weights.get(v.severity, 1) for v in self.violations)

        # Calculate score (100 - weighted violations)
        score = max(0, 100 - (total_weight * 2))
        return round(score, 1)

    def _generate_summary(self) -> dict[str, Any]:
        """Generate summary statistics."""
        severity_counts = {}
        category_counts = {}

        for violation in self.violations:
            severity_counts[violation.severity] = severity_counts.get(violation.severity, 0) + 1
            category_counts[violation.category] = category_counts.get(violation.category, 0) + 1

        return {
            "severity_breakdown": severity_counts,
            "category_breakdown": category_counts,
            "files_affected": len(set(v.file for v in self.violations)),
        }


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Enforce security policies")
    parser.add_argument("target", help="Target directory to scan")
    parser.add_argument("--output", "-o", help="Output file for report")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    enforcer = SecurityPolicyEnforcer()
    report = enforcer.enforce_policies(args.target)

    if args.json:
        output = json.dumps(report, indent=2)
    else:
        # Pretty print format
        output = f"""
🔒 SECURITY POLICY COMPLIANCE REPORT
{'=' * 50}
Target: {report['target_path']}
Timestamp: {report['timestamp']}
Compliance Score: {report['compliance_score']}/100

Summary:
  Total Violations: {report['total_violations']}
  Files Affected: {report['summary']['files_affected']}

Severity Breakdown:
"""
        for severity, count in report["summary"]["severity_breakdown"].items():
            output += f"  {severity}: {count}\n"

        output += "\nCategory Breakdown:\n"
        for category, count in report["summary"]["category_breakdown"].items():
            output += f"  {category}: {count}\n"

        if report["violations"]:
            output += "\nViolations:\n"
            for i, violation in enumerate(report["violations"][:10], 1):  # Show first 10
                output += f"  {i}. [{violation['severity'].upper()}] {violation['file']}:{violation['line']}\n"
                output += f"     {violation['message']}\n"
                output += f"     Suggestion: {violation['suggestion']}\n\n"

            if len(report["violations"]) > 10:
                output += f"  ... and {len(report['violations']) - 10} more violations\n"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
