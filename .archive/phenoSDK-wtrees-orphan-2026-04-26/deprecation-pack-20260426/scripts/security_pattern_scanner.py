#!/usr/bin/env python3
"""Security Pattern Scanner.

Comprehensive security vulnerability detection, OWASP pattern analysis, and secure
coding practice validation.
"""

import argparse
import ast
import json
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any


@dataclass
class SecurityFinding:
    """
    Represents a security-related finding.
    """

    file_path: str
    line_number: int
    vulnerability_type: str
    severity: str  # 'critical', 'high', 'medium', 'low'
    owasp_category: str = ""
    cwe_id: str = ""
    message: str = ""
    suggestion: str = ""
    context: str = ""
    confidence: float = 1.0
    exploitability: str = ""  # 'high', 'medium', 'low'
    impact: str = ""  # 'high', 'medium', 'low'
    autofix: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "file": self.file_path,
            "line": self.line_number,
            "vulnerability_type": self.vulnerability_type,
            "severity": self.severity,
            "owasp_category": self.owasp_category,
            "cwe_id": self.cwe_id,
            "message": self.message,
            "suggestion": self.suggestion,
            "context": self.context,
            "confidence": self.confidence,
            "exploitability": self.exploitability,
            "impact": self.impact,
            "autofix": self.autofix,
        }


class SecurityPatternVisitor(ast.NodeVisitor):
    """
    Detects security vulnerabilities and anti-patterns.
    """

    def __init__(self, file_path: Path, lines: list[str]):
        self.file_path = str(file_path)
        self.lines = lines
        self.findings: list[SecurityFinding] = []
        self.current_function = None
        self.current_class = None
        self.imports = set()
        self.user_input_sources = set()
        self.database_queries = []
        self.file_operations = []
        self.network_calls = []

    def add_finding(
        self,
        line_number: int,
        vuln_type: str,
        severity: str,
        message: str,
        suggestion: str = "",
        owasp_category: str = "",
        cwe_id: str = "",
        exploitability: str = "",
        impact: str = "",
        confidence: float = 1.0,
        autofix: dict[str, Any] = None,
    ):
        """
        Add a security finding.
        """
        context = ""
        if 0 < line_number <= len(self.lines):
            context = self.lines[line_number - 1].strip()

        finding = SecurityFinding(
            file_path=self.file_path,
            line_number=line_number,
            vulnerability_type=vuln_type,
            severity=severity,
            owasp_category=owasp_category,
            cwe_id=cwe_id,
            message=message,
            suggestion=suggestion,
            context=context,
            confidence=confidence,
            exploitability=exploitability,
            impact=impact,
            autofix=autofix or {},
        )

        self.findings.append(finding)

    def visit_Import(self, node: ast.Import) -> None:
        """
        Check for dangerous imports.
        """
        for alias in node.names:
            self.imports.add(alias.name)

            # Check for dangerous modules
            dangerous_modules = {
                "pickle": ("pickle_deserialization", "high", "A03:2021 – Injection", "CWE-502"),
                "marshal": ("marshal_deserialization", "high", "A03:2021 – Injection", "CWE-502"),
                "subprocess": ("subprocess_usage", "medium", "A03:2021 – Injection", "CWE-78"),
                "os": ("os_module_usage", "medium", "A03:2021 – Injection", "CWE-78"),
                "eval": ("eval_usage", "critical", "A03:2021 – Injection", "CWE-95"),
                "exec": ("exec_usage", "critical", "A03:2021 – Injection", "CWE-95"),
                "compile": ("compile_usage", "high", "A03:2021 – Injection", "CWE-95"),
            }

            if alias.name in dangerous_modules:
                vuln_type, severity, owasp, cwe = dangerous_modules[alias.name]
                self.add_finding(
                    node.lineno,
                    vuln_type,
                    severity,
                    f"Dangerous module '{alias.name}' imported",
                    f"Review usage of {alias.name} for security implications",
                    owasp_category=owasp,
                    cwe_id=cwe,
                    exploitability="high" if severity in ["critical", "high"] else "medium",
                    impact="high" if severity in ["critical", "high"] else "medium",
                )

    def visit_Call(self, node: ast.Call) -> None:
        """
        Check for dangerous function calls.
        """
        # Check for eval/exec usage
        if isinstance(node.func, ast.Name):
            if node.func.id in ["eval", "exec", "compile"]:
                self.add_finding(
                    node.lineno,
                    f"{node.func.id}_usage",
                    "critical",
                    f"Dangerous {node.func.id}() function call detected",
                    "Avoid using eval/exec/compile with user input - use safer alternatives",
                    owasp_category="A03:2021 – Injection",
                    cwe_id="CWE-95",
                    exploitability="high",
                    impact="high",
                )

        # Check for subprocess calls
        elif isinstance(node.func, ast.Attribute):
            if isinstance(node.func.value, ast.Name) and node.func.value.id == "subprocess":
                self._check_subprocess_usage(node)

            # Check for SQL injection patterns
            elif node.func.attr in ["execute", "executemany", "query"]:
                self._check_sql_injection(node)

            # Check for file operations
            elif node.func.attr in ["open", "read", "write"]:
                self._check_file_operations(node)

            # Check for network operations
            elif node.func.attr in ["get", "post", "put", "delete"]:
                self._check_network_operations(node)

        self.generic_visit(node)

    def _check_subprocess_usage(self, node: ast.Call) -> None:
        """
        Check subprocess usage for command injection.
        """
        if node.args and isinstance(node.args[0], ast.Str):
            # Check for shell=True
            shell_arg = False
            for keyword in node.keywords:
                if (
                    keyword.arg == "shell"
                    and isinstance(keyword.value, ast.Constant)
                    and keyword.value.value
                ):
                    shell_arg = True
                    break

            if shell_arg:
                self.add_finding(
                    node.lineno,
                    "subprocess_shell_injection",
                    "high",
                    "subprocess with shell=True detected - vulnerable to command injection",
                    "Use shell=False and pass command as list of arguments",
                    owasp_category="A03:2021 – Injection",
                    cwe_id="CWE-78",
                    exploitability="high",
                    impact="high",
                )

            # Check for user input in command
            command_str = node.args[0].s
            if any(
                keyword in command_str.lower() for keyword in ["input", "user", "request", "form"]
            ):
                self.add_finding(
                    node.lineno,
                    "subprocess_user_input",
                    "high",
                    "subprocess command contains potential user input",
                    "Validate and sanitize all user input before using in subprocess",
                    owasp_category="A03:2021 – Injection",
                    cwe_id="CWE-78",
                    exploitability="high",
                    impact="high",
                )

    def _check_sql_injection(self, node: ast.Call) -> None:
        """
        Check for SQL injection vulnerabilities.
        """
        if node.args:
            query_arg = node.args[0]

            # Check for string formatting in SQL
            if isinstance(query_arg, ast.BinOp) and isinstance(query_arg.op, ast.Mod):
                self.add_finding(
                    node.lineno,
                    "sql_string_formatting",
                    "high",
                    "SQL query uses string formatting - vulnerable to SQL injection",
                    "Use parameterized queries instead of string formatting",
                    owasp_category="A03:2021 – Injection",
                    cwe_id="CWE-89",
                    exploitability="high",
                    impact="high",
                )

            # Check for f-strings in SQL
            elif isinstance(query_arg, ast.JoinedStr):
                self.add_finding(
                    node.lineno,
                    "sql_f_string",
                    "high",
                    "SQL query uses f-string - vulnerable to SQL injection",
                    "Use parameterized queries instead of f-strings",
                    owasp_category="A03:2021 – Injection",
                    cwe_id="CWE-89",
                    exploitability="high",
                    impact="high",
                )

            # Check for .format() in SQL
            elif isinstance(query_arg, ast.Call) and isinstance(query_arg.func, ast.Attribute):
                if query_arg.func.attr == "format":
                    self.add_finding(
                        node.lineno,
                        "sql_format_method",
                        "high",
                        "SQL query uses .format() - vulnerable to SQL injection",
                        "Use parameterized queries instead of .format()",
                        owasp_category="A03:2021 – Injection",
                        cwe_id="CWE-89",
                        exploitability="high",
                        impact="high",
                    )

    def _check_file_operations(self, node: ast.Call) -> None:
        """
        Check file operations for security issues.
        """
        if node.args and isinstance(node.args[0], ast.Str):
            file_path = node.args[0].s

            # Check for path traversal
            if ".." in file_path or file_path.startswith("/"):
                self.add_finding(
                    node.lineno,
                    "path_traversal",
                    "high",
                    f"File path '{file_path}' may be vulnerable to path traversal",
                    "Validate and sanitize file paths, use os.path.join()",
                    owasp_category="A01:2021 – Broken Access Control",
                    cwe_id="CWE-22",
                    exploitability="high",
                    impact="high",
                )

            # Check for sensitive file access
            sensitive_files = ["passwd", "shadow", "hosts", "id_rsa", "id_dsa", "known_hosts"]
            if any(sensitive in file_path.lower() for sensitive in sensitive_files):
                self.add_finding(
                    node.lineno,
                    "sensitive_file_access",
                    "medium",
                    f"Accessing potentially sensitive file: {file_path}",
                    "Ensure proper permissions and access controls",
                    owasp_category="A01:2021 – Broken Access Control",
                    cwe_id="CWE-200",
                    exploitability="medium",
                    impact="medium",
                )

    def _check_network_operations(self, node: ast.Call) -> None:
        """
        Check network operations for security issues.
        """
        # Check for HTTP without HTTPS
        if isinstance(node.func.value, ast.Name) and node.func.value.id == "requests":
            # Check URL argument
            url_arg = None
            for keyword in node.keywords:
                if keyword.arg == "url":
                    url_arg = keyword.value
                    break

            if not url_arg and node.args:
                url_arg = node.args[0]

            if url_arg and isinstance(url_arg, ast.Str):
                url = url_arg.s
                if url.startswith("http://") and not url.startswith("http://localhost"):
                    self.add_finding(
                        node.lineno,
                        "insecure_http",
                        "medium",
                        f"HTTP request to {url} - data transmitted in plain text",
                        "Use HTTPS for secure communication",
                        owasp_category="A02:2021 – Cryptographic Failures",
                        cwe_id="CWE-319",
                        exploitability="medium",
                        impact="medium",
                    )

            # Check for verify=False
            for keyword in node.keywords:
                if (
                    keyword.arg == "verify"
                    and isinstance(keyword.value, ast.Constant)
                    and not keyword.value.value
                ):
                    self.add_finding(
                        node.lineno,
                        "ssl_verification_disabled",
                        "high",
                        "SSL verification disabled - vulnerable to man-in-the-middle attacks",
                        "Enable SSL verification or use proper certificate validation",
                        owasp_category="A02:2021 – Cryptographic Failures",
                        cwe_id="CWE-295",
                        exploitability="high",
                        impact="high",
                    )

    def visit_Assign(self, node: ast.Assign) -> None:
        """
        Check assignments for security issues.
        """
        # Check for hardcoded secrets
        for target in node.targets:
            if isinstance(target, ast.Name):
                if any(
                    secret_word in target.id.lower()
                    for secret_word in ["password", "secret", "key", "token", "api_key"]
                ):
                    if isinstance(node.value, ast.Str):
                        self.add_finding(
                            node.lineno,
                            "hardcoded_secret",
                            "high",
                            f"Hardcoded secret in variable '{target.id}'",
                            "Use environment variables or secure configuration management",
                            owasp_category="A07:2021 – Identification and Authentication Failures",
                            cwe_id="CWE-798",
                            exploitability="high",
                            impact="high",
                        )

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        """
        Check function definitions for security issues.
        """
        self.current_function = node.name

        # Check for authentication bypass
        if "auth" in node.name.lower() or "login" in node.name.lower():
            self._check_authentication_logic(node)

        # Check for authorization issues
        if "admin" in node.name.lower() or "privilege" in node.name.lower():
            self._check_authorization_logic(node)

        self.generic_visit(node)
        self.current_function = None

    def _check_authentication_logic(self, node: ast.FunctionDef) -> None:
        """
        Check authentication logic for vulnerabilities.
        """
        # Look for weak authentication patterns
        for child in ast.walk(node):
            if isinstance(child, ast.Compare):
                # Check for simple password comparison
                if isinstance(child.left, ast.Name) and "password" in child.left.id.lower():
                    if isinstance(child.comparators[0], ast.Str):
                        self.add_finding(
                            child.lineno,
                            "hardcoded_password_check",
                            "high",
                            "Hardcoded password comparison detected",
                            "Use secure password hashing and comparison methods",
                            owasp_category="A07:2021 – Identification and Authentication Failures",
                            cwe_id="CWE-256",
                            exploitability="high",
                            impact="high",
                        )

    def _check_authorization_logic(self, node: ast.FunctionDef) -> None:
        """
        Check authorization logic for vulnerabilities.
        """
        # Look for missing authorization checks
        has_auth_check = False
        for child in ast.walk(node):
            if isinstance(child, ast.If):
                # Check if there's any authorization logic
                if isinstance(child.test, ast.Name) and "auth" in child.test.id.lower():
                    has_auth_check = True
                    break

        if not has_auth_check:
            self.add_finding(
                node.lineno,
                "missing_authorization",
                "medium",
                f"Function '{node.name}' may lack proper authorization checks",
                "Implement proper authorization checks before sensitive operations",
                owasp_category="A01:2021 – Broken Access Control",
                cwe_id="CWE-285",
                exploitability="medium",
                impact="medium",
            )


class OWASPPatternDetector(ast.NodeVisitor):
    """
    Detects OWASP Top 10 patterns.
    """

    def __init__(self, file_path: Path, lines: list[str]):
        self.file_path = str(file_path)
        self.lines = lines
        self.findings: list[SecurityFinding] = []

    def add_finding(
        self,
        line_number: int,
        vuln_type: str,
        severity: str,
        message: str,
        suggestion: str = "",
        owasp_category: str = "",
        cwe_id: str = "",
    ):
        """
        Add an OWASP finding.
        """
        context = ""
        if 0 < line_number <= len(self.lines):
            context = self.lines[line_number - 1].strip()

        finding = SecurityFinding(
            file_path=self.file_path,
            line_number=line_number,
            vulnerability_type=vuln_type,
            severity=severity,
            owasp_category=owasp_category,
            cwe_id=cwe_id,
            message=message,
            suggestion=suggestion,
            context=context,
            confidence=1.0,
            exploitability="high" if severity in ["critical", "high"] else "medium",
            impact="high" if severity in ["critical", "high"] else "medium",
        )

        self.findings.append(finding)

    def visit_Call(self, node: ast.Call) -> None:
        """
        Check for OWASP vulnerabilities.
        """
        # A01:2021 – Broken Access Control
        self._check_broken_access_control(node)

        # A02:2021 – Cryptographic Failures
        self._check_cryptographic_failures(node)

        # A03:2021 – Injection
        self._check_injection(node)

        # A04:2021 – Insecure Design
        self._check_insecure_design(node)

        # A05:2021 – Security Misconfiguration
        self._check_security_misconfiguration(node)

        # A06:2021 – Vulnerable Components
        self._check_vulnerable_components(node)

        # A07:2021 – Authentication Failures
        self._check_authentication_failures(node)

        # A08:2021 – Software and Data Integrity
        self._check_data_integrity(node)

        # A09:2021 – Logging Failures
        self._check_logging_failures(node)

        # A10:2021 – Server-Side Request Forgery
        self._check_ssrf(node)

        self.generic_visit(node)

    def _check_broken_access_control(self, node: ast.Call) -> None:
        """
        Check for broken access control patterns.
        """
        if isinstance(node.func, ast.Attribute):
            # Check for direct file access without proper checks
            if node.func.attr in ["open", "read", "write"]:
                if node.args and isinstance(node.args[0], ast.Str):
                    file_path = node.args[0].s
                    if not any(check in file_path for check in ["/tmp/", "/var/", "/etc/"]):
                        self.add_finding(
                            node.lineno,
                            "unrestricted_file_access",
                            "medium",
                            f"File access without proper access control: {file_path}",
                            "Implement proper access control checks",
                            owasp_category="A01:2021 – Broken Access Control",
                            cwe_id="CWE-284",
                        )

    def _check_cryptographic_failures(self, node: ast.Call) -> None:
        """
        Check for cryptographic failures.
        """
        if isinstance(node.func, ast.Attribute):
            # Check for weak hashing algorithms
            if node.func.attr in ["md5", "sha1"]:
                self.add_finding(
                    node.lineno,
                    "weak_hashing",
                    "high",
                    f"Weak hashing algorithm {node.func.attr} detected",
                    "Use SHA-256 or stronger hashing algorithms",
                    owasp_category="A02:2021 – Cryptographic Failures",
                    cwe_id="CWE-327",
                )

    def _check_injection(self, node: ast.Call) -> None:
        """
        Check for injection vulnerabilities.
        """
        if isinstance(node.func, ast.Name) and node.func.id in ["eval", "exec"]:
            self.add_finding(
                node.lineno,
                "code_injection",
                "critical",
                f"Code injection vulnerability: {node.func.id}()",
                "Avoid using eval/exec with user input",
                owasp_category="A03:2021 – Injection",
                cwe_id="CWE-95",
            )

    def _check_insecure_design(self, node: ast.Call) -> None:
        """
        Check for insecure design patterns.
        """
        if isinstance(node.func, ast.Attribute):
            # Check for insecure random number generation
            if (
                node.func.attr == "random"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "random"
            ):
                self.add_finding(
                    node.lineno,
                    "insecure_random",
                    "medium",
                    "Using insecure random number generation",
                    "Use secrets module for cryptographically secure random numbers",
                    owasp_category="A04:2021 – Insecure Design",
                    cwe_id="CWE-330",
                )

    def _check_security_misconfiguration(self, node: ast.Call) -> None:
        """
        Check for security misconfiguration.
        """
        if isinstance(node.func, ast.Attribute):
            # Check for debug mode in production
            if node.func.attr == "debug" and isinstance(node.func.value, ast.Name):
                self.add_finding(
                    node.lineno,
                    "debug_mode",
                    "low",
                    "Debug mode may be enabled in production",
                    "Ensure debug mode is disabled in production",
                    owasp_category="A05:2021 – Security Misconfiguration",
                    cwe_id="CWE-489",
                )

    def _check_vulnerable_components(self, node: ast.Call) -> None:
        """
        Check for vulnerable components.
        """
        # This would typically check against a vulnerability database
        # For now, we'll check for known vulnerable patterns
        if isinstance(node.func, ast.Attribute):
            if (
                node.func.attr == "pickle"
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "pickle"
            ):
                self.add_finding(
                    node.lineno,
                    "pickle_deserialization",
                    "high",
                    "Pickle deserialization can lead to code execution",
                    "Use safer serialization formats like JSON",
                    owasp_category="A06:2021 – Vulnerable Components",
                    cwe_id="CWE-502",
                )

    def _check_authentication_failures(self, node: ast.Call) -> None:
        """
        Check for authentication failures.
        """
        if isinstance(node.func, ast.Attribute):
            # Check for weak password requirements
            if "password" in node.func.attr.lower():
                self.add_finding(
                    node.lineno,
                    "weak_password_handling",
                    "medium",
                    "Weak password handling detected",
                    "Implement strong password policies and secure storage",
                    owasp_category="A07:2021 – Identification and Authentication Failures",
                    cwe_id="CWE-521",
                )

    def _check_data_integrity(self, node: ast.Call) -> None:
        """
        Check for data integrity issues.
        """
        if isinstance(node.func, ast.Attribute):
            # Check for unsigned data
            if node.func.attr in ["load", "loads"] and isinstance(node.func.value, ast.Name):
                if node.func.value.id in ["pickle", "marshal"]:
                    self.add_finding(
                        node.lineno,
                        "unsigned_data",
                        "medium",
                        "Loading unsigned data can lead to integrity issues",
                        "Implement data integrity checks and signatures",
                        owasp_category="A08:2021 – Software and Data Integrity Failures",
                        cwe_id="CWE-345",
                    )

    def _check_logging_failures(self, node: ast.Call) -> None:
        """
        Check for logging failures.
        """
        if isinstance(node.func, ast.Attribute):
            # Check for sensitive data in logs
            if node.func.attr in ["log", "info", "debug", "warning", "error"]:
                if node.args and isinstance(node.args[0], ast.Str):
                    log_message = node.args[0].s
                    if any(
                        sensitive in log_message.lower()
                        for sensitive in ["password", "secret", "key", "token"]
                    ):
                        self.add_finding(
                            node.lineno,
                            "sensitive_data_logging",
                            "medium",
                            "Sensitive data may be logged",
                            "Avoid logging sensitive information",
                            owasp_category="A09:2021 – Security Logging and Monitoring Failures",
                            cwe_id="CWE-532",
                        )

    def _check_ssrf(self, node: ast.Call) -> None:
        """
        Check for Server-Side Request Forgery.
        """
        if isinstance(node.func, ast.Attribute):
            if (
                node.func.attr in ["get", "post", "put", "delete"]
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "requests"
            ):
                # Check if URL comes from user input
                if node.args and isinstance(node.args[0], ast.Name):
                    self.add_finding(
                        node.lineno,
                        "potential_ssrf",
                        "high",
                        "Potential SSRF vulnerability - URL from variable",
                        "Validate and whitelist allowed URLs",
                        owasp_category="A10:2021 – Server-Side Request Forgery",
                        cwe_id="CWE-918",
                    )


class SecurityPatternScanner:
    """
    Main scanner for security patterns.
    """

    def __init__(self, root_path: Path):
        self.root_path = root_path
        self.all_findings: list[SecurityFinding] = []

    def scan_file(self, file_path: Path) -> None:
        """
        Scan a single file for security issues.
        """
        try:
            content = file_path.read_text(encoding="utf-8", errors="ignore")
            lines = content.splitlines()

            # Parse AST
            tree = ast.parse(content, filename=str(file_path))

            # Run security visitors
            security_visitor = SecurityPatternVisitor(file_path, lines)
            security_visitor.visit(tree)

            owasp_visitor = OWASPPatternDetector(file_path, lines)
            owasp_visitor.visit(tree)

            # Collect findings
            self.all_findings.extend(security_visitor.findings)
            self.all_findings.extend(owasp_visitor.findings)

        except Exception as e:
            print(f"Error scanning {file_path}: {e}")

    def scan_directory(self, directory: Path) -> None:
        """
        Scan a directory for security issues.
        """
        for file_path in directory.rglob("*.py"):
            if file_path.is_file():
                # Skip certain directories
                if any(
                    part in str(file_path)
                    for part in ["__pycache__", ".git", ".venv", "node_modules"]
                ):
                    continue

                self.scan_file(file_path)

    def generate_report(self) -> str:
        """
        Generate a security analysis report.
        """
        if not self.all_findings:
            return "No security issues found."

        # Group findings by OWASP category
        owasp_counts = Counter(f.owasp_category for f in self.all_findings if f.owasp_category)
        severity_counts = Counter(f.severity for f in self.all_findings)
        vuln_counts = Counter(f.vulnerability_type for f in self.all_findings)

        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("SECURITY PATTERN ANALYSIS REPORT")
        report_lines.append("=" * 80)
        report_lines.append(f"Total findings: {len(self.all_findings)}")
        report_lines.append("")

        # OWASP Top 10 breakdown
        report_lines.append("OWASP TOP 10 CATEGORIES:")
        report_lines.append("-" * 50)
        for category, count in owasp_counts.most_common():
            report_lines.append(f"{category:<40} {count:>6}")
        report_lines.append("")

        # Severity breakdown
        report_lines.append("FINDINGS BY SEVERITY:")
        report_lines.append("-" * 40)
        for severity, count in severity_counts.most_common():
            report_lines.append(f"{severity:<20} {count:>6}")
        report_lines.append("")

        # Top vulnerability types
        report_lines.append("TOP VULNERABILITY TYPES:")
        report_lines.append("-" * 40)
        for vuln_type, count in vuln_counts.most_common(10):
            report_lines.append(f"{vuln_type:<30} {count:>6}")
        report_lines.append("")

        # Detailed findings by severity
        for severity in ["critical", "high", "medium", "low"]:
            findings = [f for f in self.all_findings if f.severity == severity]
            if findings:
                report_lines.append(f"{severity.upper()} SEVERITY FINDINGS:")
                report_lines.append("-" * 50)
                for finding in findings[:10]:  # Show top 10
                    report_lines.append(
                        f"{finding.file_path}:{finding.line_number} - {finding.vulnerability_type}",
                    )
                    report_lines.append(f"  {finding.message}")
                    if finding.suggestion:
                        report_lines.append(f"  Suggestion: {finding.suggestion}")
                    if finding.owasp_category:
                        report_lines.append(f"  OWASP: {finding.owasp_category}")
                    if finding.cwe_id:
                        report_lines.append(f"  CWE: {finding.cwe_id}")
                    report_lines.append("")

        return "\n".join(report_lines)


def main():
    """
    Main function.
    """
    parser = argparse.ArgumentParser(description="Security Pattern Scanner")
    parser.add_argument("--path", type=str, default=".", help="Path to scan")
    parser.add_argument("--output", type=str, help="Output file for report")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--severity", type=str, help="Filter by severity")
    parser.add_argument("--owasp", type=str, help="Filter by OWASP category")

    args = parser.parse_args()

    root_path = Path(args.path)
    scanner = SecurityPatternScanner(root_path)

    print("🔍 Scanning for security patterns...")
    scanner.scan_directory(root_path)

    if args.json:
        # Output JSON
        output = {"findings": [f.to_dict() for f in scanner.all_findings]}

        if args.severity:
            output["findings"] = [f for f in output["findings"] if f["severity"] == args.severity]

        if args.owasp:
            output["findings"] = [
                f for f in output["findings"] if args.owasp in f["owasp_category"]
            ]

        json_output = json.dumps(output, indent=2)

        if args.output:
            with open(args.output, "w") as f:
                f.write(json_output)
        else:
            print(json_output)
    else:
        # Output text report
        report = scanner.generate_report()

        if args.output:
            with open(args.output, "w") as f:
                f.write(report)
        else:
            print(report)


if __name__ == "__main__":
    main()
