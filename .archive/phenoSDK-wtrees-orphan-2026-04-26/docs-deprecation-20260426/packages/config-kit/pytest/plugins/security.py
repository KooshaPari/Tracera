"""
Security testing plugin for pytest.

This plugin provides security testing capabilities including:
- Security vulnerability scanning
- Authentication testing
- Authorization testing
- Input validation testing
- Security compliance checking
"""

import ast
import re
from pathlib import Path

import pytest


class SecurityPlugin:
    """Pytest plugin for security testing."""

    def __init__(self, config):
        self.config = config
        self.security_rules = self._load_security_rules()
        self.vulnerability_patterns = self._load_vulnerability_patterns()

    def _load_security_rules(self) -> dict[str, list[str]]:
        """Load security rules configuration."""
        return {
            "forbidden_imports": [
                "pickle",
                "marshal",
                "shelve",
                "dbm",
                "sqlite3",
                "subprocess",
                "os.system",
                "eval",
                "exec",
                "compile",
            ],
            "forbidden_functions": [
                "eval",
                "exec",
                "compile",
                "input",
                "raw_input",
                "reload",
                "__import__",
            ],
            "required_imports": [
                "hashlib",
                "secrets",
                "hmac",
            ],
            "password_patterns": [
                r"password\s*=\s*['\"][^'\"]+['\"]",
                r"passwd\s*=\s*['\"][^'\"]+['\"]",
                r"pwd\s*=\s*['\"][^'\"]+['\"]",
            ],
            "hardcoded_secrets": [
                r"api_key\s*=\s*['\"][^'\"]+['\"]",
                r"secret\s*=\s*['\"][^'\"]+['\"]",
                r"token\s*=\s*['\"][^'\"]+['\"]",
                r"key\s*=\s*['\"][^'\"]+['\"]",
            ],
        }

    def _load_vulnerability_patterns(self) -> dict[str, str]:
        """Load vulnerability detection patterns."""
        return {
            "sql_injection": r"(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER).*\+.*%",
            "xss": r"<script.*>.*</script>",
            "path_traversal": r"\.\./",
            "command_injection": r"(os\.system|subprocess\.call|subprocess\.run)",
            "unsafe_deserialization": r"(pickle\.loads|marshal\.loads)",
            "weak_crypto": r"(md5|sha1|des|rc4)",
            "hardcoded_credentials": r"(username|password|api_key|secret)\s*=\s*['\"][^'\"]+['\"]",
        }

    @pytest.hookimpl(tryfirst=True)
    def pytest_collection_modifyitems(self, config, items):
        """Add security validation tests."""
        security_items = []

        # Add vulnerability scanning
        security_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_vulnerability_scan",
                callobj=self._test_vulnerability_scan,
                markers=[pytest.mark.security, pytest.mark.vulnerability],
            ),
        )

        # Add forbidden imports check
        security_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_forbidden_imports",
                callobj=self._test_forbidden_imports,
                markers=[pytest.mark.security, pytest.mark.imports],
            ),
        )

        # Add hardcoded secrets check
        security_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_hardcoded_secrets",
                callobj=self._test_hardcoded_secrets,
                markers=[pytest.mark.security, pytest.mark.secrets],
            ),
        )

        # Add password security check
        security_items.append(
            pytest.Function.from_parent(
                parent=items[0].parent if items else None,
                name="test_password_security",
                callobj=self._test_password_security,
                markers=[pytest.mark.security, pytest.mark.passwords],
            ),
        )

        items.extend(security_items)

    def _test_vulnerability_scan(self):
        """Scan code for common vulnerabilities."""
        violations = []

        for py_file in self._get_python_files():
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

                for vuln_type, pattern in self.vulnerability_patterns.items():
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        violations.append(f"{py_file}: {vuln_type} - {matches}")

        if violations:
            pytest.fail("Security vulnerabilities found:\n" + "\n".join(violations))

    def _test_forbidden_imports(self):
        """Check for forbidden imports that could be security risks."""
        violations = []

        for py_file in self._get_python_files():
            with open(py_file, encoding="utf-8") as f:
                try:
                    tree = ast.parse(f.read())
                except SyntaxError:
                    continue

                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        for alias in node.names:
                            if alias.name in self.security_rules["forbidden_imports"]:
                                violations.append(f"{py_file}: Forbidden import '{alias.name}'")
                    elif isinstance(node, ast.ImportFrom):
                        if node.module in self.security_rules["forbidden_imports"]:
                            violations.append(f"{py_file}: Forbidden import '{node.module}'")

        if violations:
            pytest.fail("Forbidden imports found:\n" + "\n".join(violations))

    def _test_hardcoded_secrets(self):
        """Check for hardcoded secrets in the code."""
        violations = []

        for py_file in self._get_python_files():
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

                for pattern in self.security_rules["hardcoded_secrets"]:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        violations.append(f"{py_file}: Hardcoded secret - {matches}")

        if violations:
            pytest.fail("Hardcoded secrets found:\n" + "\n".join(violations))

    def _test_password_security(self):
        """Check for insecure password handling."""
        violations = []

        for py_file in self._get_python_files():
            with open(py_file, encoding="utf-8") as f:
                content = f.read()

                for pattern in self.security_rules["password_patterns"]:
                    matches = re.findall(pattern, content, re.IGNORECASE)
                    if matches:
                        violations.append(f"{py_file}: Insecure password handling - {matches}")

        if violations:
            pytest.fail("Insecure password handling found:\n" + "\n".join(violations))

    def _get_python_files(self) -> list[Path]:
        """Get all Python files in the project."""
        python_files = []
        for root, dirs, files in Path().rglob("*.py"):
            # Skip certain directories
            if any(skip in str(root) for skip in (".git", "__pycache__", ".pytest_cache", "htmlcov", "dist", "build")):
                continue
            python_files.append(root)

        return python_files


def security_test(func: Callable) -> Callable:
    """Decorator for marking functions as security tests."""
    return pytest.mark.security(func)


def auth_test(func: Callable) -> Callable:
    """Decorator for marking functions as authentication tests."""
    return pytest.mark.auth(func)


def injection_test(func: Callable) -> Callable:
    """Decorator for marking functions as injection tests."""
    return pytest.mark.injection(func)


def xss_test(func: Callable) -> Callable:
    """Decorator for marking functions as XSS tests."""
    return pytest.mark.xss(func)


def csrf_test(func: Callable) -> Callable:
    """Decorator for marking functions as CSRF tests."""
    return pytest.mark.csrf(func)


def sql_injection_test(func: Callable) -> Callable:
    """Decorator for marking functions as SQL injection tests."""
    return pytest.mark.sql_injection(func)


def pytest_configure(config):
    """Configure the security plugin."""
    config.pluginmanager.register(SecurityPlugin(config), "security")
