#!/usr/bin/env python3
"""
Integration Quality Gates Comprehensive end-to-end validation, API contract validation,
data flow analysis, and integration testing for Python codebases.
"""
import argparse
import ast
import json
import subprocess
from collections import defaultdict
from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class QualityGateViolation:
    """
    Represents a quality gate violation.
    """

    gate: str
    severity: str
    file: str
    line: int
    column: int
    message: str
    suggestion: str
    confidence: float
    category: str


class IntegrationQualityGates:
    """
    Comprehensive integration quality validation.
    """

    def __init__(self):
        self.violations = []
        self.test_results = {}
        self.api_contracts = {}
        self.data_flows = {}

        # Quality gates configuration
        self.gates = {
            "api_contracts": True,
            "data_flow_validation": True,
            "integration_tests": True,
            "performance_benchmarks": True,
            "security_validation": True,
            "error_handling": True,
            "logging_validation": True,
            "monitoring_integration": True,
            "deployment_readiness": True,
            "backward_compatibility": True,
        }

        # API contract validation rules
        self.api_rules = {
            "versioning_required": True,
            "error_responses_required": True,
            "authentication_required": True,
            "rate_limiting_required": True,
            "documentation_required": True,
            "schema_validation_required": True,
        }

        # Performance benchmarks
        self.performance_thresholds = {
            "response_time_ms": 1000,
            "memory_usage_mb": 512,
            "cpu_usage_percent": 80,
            "concurrent_requests": 100,
            "error_rate_percent": 1.0,
        }

    def analyze_file(self, file_path: Path) -> dict[str, Any]:
        """
        Analyze a single file for quality gate violations.
        """
        try:
            with open(file_path, encoding="utf-8") as f:
                content = f.read()

            tree = ast.parse(content)
            file_violations = []

            # Run all enabled quality gates
            if self.gates["api_contracts"]:
                file_violations.extend(self._validate_api_contracts(tree, file_path))

            if self.gates["data_flow_validation"]:
                file_violations.extend(self._validate_data_flow(tree, file_path))

            if self.gates["error_handling"]:
                file_violations.extend(self._validate_error_handling(tree, file_path))

            if self.gates["logging_validation"]:
                file_violations.extend(self._validate_logging(tree, file_path))

            if self.gates["security_validation"]:
                file_violations.extend(self._validate_security(tree, file_path))

            if self.gates["monitoring_integration"]:
                file_violations.extend(self._validate_monitoring(tree, file_path))

            self.violations.extend(file_violations)

            return {
                "file": str(file_path),
                "violations": file_violations,
                "violation_count": len(file_violations),
                "severity_counts": self._count_by_severity(file_violations),
            }

        except Exception as e:
            return {"file": str(file_path), "error": str(e), "violations": [], "violation_count": 0}

    def _validate_api_contracts(self, tree: ast.AST, file_path: Path) -> list[QualityGateViolation]:
        """
        Validate API contracts and endpoints.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                class_name = node.name.lower()

                # Check for API endpoint classes
                if any(
                    keyword in class_name for keyword in ["api", "endpoint", "controller", "route"]
                ):
                    violations.extend(self._validate_endpoint_contract(node, file_path))

                # Check for service classes
                elif "service" in class_name:
                    violations.extend(self._validate_service_contract(node, file_path))

        return violations

    def _validate_endpoint_contract(
        self, node: ast.ClassDef, file_path: Path,
    ) -> list[QualityGateViolation]:
        """
        Validate API endpoint contract.
        """
        violations = []

        # Check for versioning
        if self.api_rules["versioning_required"]:
            if not self._has_api_versioning(node):
                violations.append(
                    QualityGateViolation(
                        gate="api_contracts",
                        severity="high",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"API endpoint '{node.name}' lacks versioning",
                        suggestion="Add API versioning to ensure backward compatibility",
                        confidence=0.8,
                        category="API Contract",
                    ),
                )

        # Check for error handling
        if self.api_rules["error_responses_required"]:
            if not self._has_error_handling(node):
                violations.append(
                    QualityGateViolation(
                        gate="api_contracts",
                        severity="high",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"API endpoint '{node.name}' lacks proper error handling",
                        suggestion="Implement comprehensive error handling with proper HTTP status codes",
                        confidence=0.9,
                        category="API Contract",
                    ),
                )

        # Check for authentication
        if self.api_rules["authentication_required"]:
            if not self._has_authentication(node):
                violations.append(
                    QualityGateViolation(
                        gate="api_contracts",
                        severity="medium",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"API endpoint '{node.name}' lacks authentication",
                        suggestion="Implement proper authentication and authorization",
                        confidence=0.7,
                        category="API Contract",
                    ),
                )

        # Check for rate limiting
        if self.api_rules["rate_limiting_required"]:
            if not self._has_rate_limiting(node):
                violations.append(
                    QualityGateViolation(
                        gate="api_contracts",
                        severity="medium",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"API endpoint '{node.name}' lacks rate limiting",
                        suggestion="Implement rate limiting to prevent abuse",
                        confidence=0.6,
                        category="API Contract",
                    ),
                )

        # Check for documentation
        if self.api_rules["documentation_required"]:
            if not self._has_documentation(node):
                violations.append(
                    QualityGateViolation(
                        gate="api_contracts",
                        severity="low",
                        file=str(file_path),
                        line=node.lineno,
                        column=node.col_offset,
                        message=f"API endpoint '{node.name}' lacks documentation",
                        suggestion="Add comprehensive API documentation",
                        confidence=0.8,
                        category="API Contract",
                    ),
                )

        return violations

    def _validate_service_contract(
        self, node: ast.ClassDef, file_path: Path,
    ) -> list[QualityGateViolation]:
        """
        Validate service contract.
        """
        violations = []

        # Check for proper interface implementation
        if not self._implements_interface(node):
            violations.append(
                QualityGateViolation(
                    gate="api_contracts",
                    severity="medium",
                    file=str(file_path),
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Service '{node.name}' should implement an interface",
                    suggestion="Define and implement a service interface",
                    confidence=0.7,
                    category="Service Contract",
                ),
            )

        # Check for proper error handling
        if not self._has_service_error_handling(node):
            violations.append(
                QualityGateViolation(
                    gate="api_contracts",
                    severity="high",
                    file=str(file_path),
                    line=node.lineno,
                    column=node.col_offset,
                    message=f"Service '{node.name}' lacks proper error handling",
                    suggestion="Implement comprehensive error handling with proper exception types",
                    confidence=0.8,
                    category="Service Contract",
                ),
            )

        return violations

    def _validate_data_flow(self, tree: ast.AST, file_path: Path) -> list[QualityGateViolation]:
        """
        Validate data flow and transformations.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for data validation
                if not self._has_data_validation(node):
                    violations.append(
                        QualityGateViolation(
                            gate="data_flow_validation",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' lacks data validation",
                            suggestion="Add input validation and data sanitization",
                            confidence=0.6,
                            category="Data Flow",
                        ),
                    )

                # Check for data transformation safety
                if self._has_unsafe_data_transformation(node):
                    violations.append(
                        QualityGateViolation(
                            gate="data_flow_validation",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has unsafe data transformation",
                            suggestion="Implement safe data transformation with proper error handling",
                            confidence=0.8,
                            category="Data Flow",
                        ),
                    )

        return violations

    def _validate_error_handling(
        self, tree: ast.AST, file_path: Path,
    ) -> list[QualityGateViolation]:
        """
        Validate error handling patterns.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for proper exception handling
                if not self._has_proper_exception_handling(node):
                    violations.append(
                        QualityGateViolation(
                            gate="error_handling",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' lacks proper exception handling",
                            suggestion="Add try-catch blocks and proper exception handling",
                            confidence=0.8,
                            category="Error Handling",
                        ),
                    )

                # Check for error logging
                if not self._has_error_logging(node):
                    violations.append(
                        QualityGateViolation(
                            gate="error_handling",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' lacks error logging",
                            suggestion="Add proper error logging for debugging and monitoring",
                            confidence=0.7,
                            category="Error Handling",
                        ),
                    )

        return violations

    def _validate_logging(self, tree: ast.AST, file_path: Path) -> list[QualityGateViolation]:
        """
        Validate logging implementation.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for proper logging
                if not self._has_proper_logging(node):
                    violations.append(
                        QualityGateViolation(
                            gate="logging_validation",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' lacks proper logging",
                            suggestion="Add structured logging for monitoring and debugging",
                            confidence=0.6,
                            category="Logging",
                        ),
                    )

                # Check for sensitive data logging
                if self._logs_sensitive_data(node):
                    violations.append(
                        QualityGateViolation(
                            gate="logging_validation",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' may log sensitive data",
                            suggestion="Remove or mask sensitive data from logs",
                            confidence=0.7,
                            category="Logging",
                        ),
                    )

        return violations

    def _validate_security(self, tree: ast.AST, file_path: Path) -> list[QualityGateViolation]:
        """
        Validate security patterns.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for SQL injection vulnerabilities
                if self._has_sql_injection_risk(node):
                    violations.append(
                        QualityGateViolation(
                            gate="security_validation",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has SQL injection risk",
                            suggestion="Use parameterized queries to prevent SQL injection",
                            confidence=0.9,
                            category="Security",
                        ),
                    )

                # Check for XSS vulnerabilities
                if self._has_xss_risk(node):
                    violations.append(
                        QualityGateViolation(
                            gate="security_validation",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has XSS risk",
                            suggestion="Sanitize user input to prevent XSS attacks",
                            confidence=0.8,
                            category="Security",
                        ),
                    )

                # Check for insecure deserialization
                if self._has_insecure_deserialization(node):
                    violations.append(
                        QualityGateViolation(
                            gate="security_validation",
                            severity="high",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' has insecure deserialization",
                            suggestion="Use safe deserialization methods and validate input",
                            confidence=0.8,
                            category="Security",
                        ),
                    )

        return violations

    def _validate_monitoring(self, tree: ast.AST, file_path: Path) -> list[QualityGateViolation]:
        """
        Validate monitoring integration.
        """
        violations = []

        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                # Check for metrics collection
                if not self._has_metrics_collection(node):
                    violations.append(
                        QualityGateViolation(
                            gate="monitoring_integration",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Function '{node.name}' lacks metrics collection",
                            suggestion="Add metrics collection for monitoring and alerting",
                            confidence=0.6,
                            category="Monitoring",
                        ),
                    )

                # Check for health checks
                if "health" in node.name.lower() and not self._has_proper_health_check(node):
                    violations.append(
                        QualityGateViolation(
                            gate="monitoring_integration",
                            severity="medium",
                            file=str(file_path),
                            line=node.lineno,
                            column=node.col_offset,
                            message=f"Health check function '{node.name}' is incomplete",
                            suggestion="Implement comprehensive health checks",
                            confidence=0.7,
                            category="Monitoring",
                        ),
                    )

        return violations

    def run_integration_tests(self, test_path: str) -> dict[str, Any]:
        """
        Run integration tests.
        """
        if not self.gates["integration_tests"]:
            return {"status": "disabled", "tests": []}

        try:
            # Run pytest for integration tests
            result = subprocess.run(
                ["python", "-m", "pytest", test_path, "-v", "--tb=short"],
                check=False, capture_output=True,
                text=True,
                timeout=300,
            )

            return {
                "status": "completed",
                "exit_code": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "tests_passed": "passed" in result.stdout,
                "tests_failed": "failed" in result.stdout,
            }
        except subprocess.TimeoutExpired:
            return {"status": "timeout", "tests": []}
        except Exception as e:
            return {"status": "error", "error": str(e), "tests": []}

    def run_performance_benchmarks(self, benchmark_path: str) -> dict[str, Any]:
        """
        Run performance benchmarks.
        """
        if not self.gates["performance_benchmarks"]:
            return {"status": "disabled", "benchmarks": []}

        try:
            # Run performance benchmarks
            result = subprocess.run(
                ["python", "-m", "pytest", benchmark_path, "--benchmark-only"],
                check=False, capture_output=True,
                text=True,
                timeout=600,
            )

            # Parse benchmark results
            benchmarks = self._parse_benchmark_results(result.stdout)

            # Check against thresholds
            violations = []
            for benchmark in benchmarks:
                if benchmark["response_time"] > self.performance_thresholds["response_time_ms"]:
                    violations.append(
                        {
                            "benchmark": benchmark["name"],
                            "metric": "response_time",
                            "value": benchmark["response_time"],
                            "threshold": self.performance_thresholds["response_time_ms"],
                        },
                    )

            return {
                "status": "completed",
                "benchmarks": benchmarks,
                "violations": violations,
                "thresholds": self.performance_thresholds,
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "benchmarks": []}

    def validate_api_contracts(self, api_spec_path: str) -> dict[str, Any]:
        """
        Validate API contracts against OpenAPI specification.
        """
        if not self.gates["api_contracts"]:
            return {"status": "disabled", "contracts": []}

        try:
            with open(api_spec_path) as f:
                api_spec = yaml.safe_load(f)

            violations = []

            # Validate API specification
            if "openapi" not in api_spec:
                violations.append(
                    {
                        "type": "missing_openapi_version",
                        "severity": "high",
                        "message": "OpenAPI version not specified",
                    },
                )

            if "paths" not in api_spec:
                violations.append(
                    {
                        "type": "missing_paths",
                        "severity": "high",
                        "message": "API paths not defined",
                    },
                )

            # Validate each endpoint
            for path, methods in api_spec.get("paths", {}).items():
                for method, spec in methods.items():
                    if method.upper() in ["GET", "POST", "PUT", "DELETE", "PATCH"]:
                        endpoint_violations = self._validate_endpoint_spec(path, method, spec)
                        violations.extend(endpoint_violations)

            return {
                "status": "completed",
                "violations": violations,
                "endpoints_validated": len(api_spec.get("paths", {})),
                "spec_version": api_spec.get("openapi", "unknown"),
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "contracts": []}

    def validate_deployment_readiness(self, deployment_config: str) -> dict[str, Any]:
        """
        Validate deployment readiness.
        """
        if not self.gates["deployment_readiness"]:
            return {"status": "disabled", "checks": []}

        try:
            with open(deployment_config) as f:
                config = yaml.safe_load(f)

            checks = []

            # Check for required deployment configurations
            required_configs = ["replicas", "resources", "health_checks", "environment_variables"]
            for config_key in required_configs:
                if config_key not in config:
                    checks.append(
                        {
                            "type": "missing_config",
                            "severity": "high",
                            "config": config_key,
                            "message": f"Missing required deployment configuration: {config_key}",
                        },
                    )
                else:
                    checks.append(
                        {
                            "type": "config_present",
                            "severity": "info",
                            "config": config_key,
                            "message": f"Configuration present: {config_key}",
                        },
                    )

            # Check resource limits
            if "resources" in config:
                resources = config["resources"]
                if "limits" not in resources:
                    checks.append(
                        {
                            "type": "missing_resource_limits",
                            "severity": "medium",
                            "message": "Resource limits not specified",
                        },
                    )

            return {
                "status": "completed",
                "checks": checks,
                "deployment_ready": all(c["severity"] != "high" for c in checks),
            }
        except Exception as e:
            return {"status": "error", "error": str(e), "checks": []}

    # Helper methods for validation

    def _has_api_versioning(self, node: ast.ClassDef) -> bool:
        """
        Check if API has versioning.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Str):
                if "version" in child.s.lower() or "v1" in child.s.lower():
                    return True
        return False

    def _has_error_handling(self, node: ast.ClassDef) -> bool:
        """
        Check if class has error handling.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False

    def _has_authentication(self, node: ast.ClassDef) -> bool:
        """
        Check if class has authentication.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                if "auth" in child.name.lower() or "login" in child.name.lower():
                    return True
        return False

    def _has_rate_limiting(self, node: ast.ClassDef) -> bool:
        """
        Check if class has rate limiting.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.FunctionDef):
                if "rate" in child.name.lower() or "limit" in child.name.lower():
                    return True
        return False

    def _has_documentation(self, node: ast.ClassDef) -> bool:
        """
        Check if class has documentation.
        """
        return node.docstring is not None and len(node.docstring.strip()) > 50

    def _implements_interface(self, node: ast.ClassDef) -> bool:
        """
        Check if class implements an interface.
        """
        for base in node.bases:
            if isinstance(base, ast.Name):
                if "interface" in base.id.lower() or "protocol" in base.id.lower():
                    return True
        return False

    def _has_service_error_handling(self, node: ast.ClassDef) -> bool:
        """
        Check if service has error handling.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False

    def _has_data_validation(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has data validation.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id.lower() in ["validate", "check", "verify"]:
                        return True
        return False

    def _has_unsafe_data_transformation(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has unsafe data transformation.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id.lower() in ["eval", "exec", "compile"]:
                        return True
        return False

    def _has_proper_exception_handling(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has proper exception handling.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Try):
                return True
        return False

    def _has_error_logging(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has error logging.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in ["error", "exception", "critical"]:
                        return True
        return False

    def _has_proper_logging(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has proper logging.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in ["info", "debug", "warning", "error"]:
                        return True
        return False

    def _logs_sensitive_data(self, node: ast.FunctionDef) -> bool:
        """
        Check if function logs sensitive data.
        """
        sensitive_keywords = ["password", "token", "key", "secret", "credit", "ssn"]

        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in ["info", "debug", "warning", "error"]:
                        # Check if any arguments contain sensitive keywords
                        for arg in child.args:
                            if isinstance(arg, ast.Str):
                                if any(keyword in arg.s.lower() for keyword in sensitive_keywords):
                                    return True
        return False

    def _has_sql_injection_risk(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has SQL injection risk.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in ["execute", "query"]:
                        # Check if string formatting is used
                        for arg in child.args:
                            if isinstance(arg, ast.BinOp) and isinstance(arg.op, ast.Mod):
                                return True
        return False

    def _has_xss_risk(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has XSS risk.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in ["render", "template", "html"]:
                        # Check if user input is directly used
                        for arg in child.args:
                            if isinstance(arg, ast.Name):
                                return True
        return False

    def _has_insecure_deserialization(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has insecure deserialization.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Name):
                    if child.func.id.lower() in ["pickle", "marshal", "eval"]:
                        return True
        return False

    def _has_metrics_collection(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has metrics collection.
        """
        for child in ast.walk(node):
            if isinstance(child, ast.Call):
                if isinstance(child.func, ast.Attribute):
                    if child.func.attr.lower() in ["counter", "gauge", "histogram", "timer"]:
                        return True
        return False

    def _has_proper_health_check(self, node: ast.FunctionDef) -> bool:
        """
        Check if function has proper health check.
        """
        # Check for return value and proper structure
        if not node.body:
            return False

        # Check if function returns a boolean or status
        for child in ast.walk(node):
            if isinstance(child, ast.Return):
                return True

        return False

    def _parse_benchmark_results(self, output: str) -> list[dict[str, Any]]:
        """
        Parse benchmark results from pytest-benchmark output.
        """
        benchmarks = []

        # Simple parsing of benchmark output
        lines = output.split("\n")
        for line in lines:
            if "benchmark" in line.lower() and "ms" in line:
                # Extract benchmark name and timing
                parts = line.split()
                if len(parts) >= 2:
                    name = parts[0]
                    timing = float(parts[1].replace("ms", ""))
                    benchmarks.append({"name": name, "response_time": timing})

        return benchmarks

    def _validate_endpoint_spec(
        self, path: str, method: str, spec: dict[str, Any],
    ) -> list[dict[str, Any]]:
        """
        Validate individual endpoint specification.
        """
        violations = []

        # Check for required fields
        required_fields = ["responses", "summary"]
        for field in required_fields:
            if field not in spec:
                violations.append(
                    {
                        "type": f"missing_{field}",
                        "severity": "medium",
                        "endpoint": f"{method.upper()} {path}",
                        "message": f"Missing required field: {field}",
                    },
                )

        # Check for error responses
        if "responses" in spec:
            error_codes = [
                str(code)
                for code in spec["responses"].keys()
                if code.startswith("4") or code.startswith("5")
            ]
            if not error_codes:
                violations.append(
                    {
                        "type": "missing_error_responses",
                        "severity": "medium",
                        "endpoint": f"{method.upper()} {path}",
                        "message": "No error responses defined",
                    },
                )

        return violations

    def _count_by_severity(self, violations: list[QualityGateViolation]) -> dict[str, int]:
        """
        Count violations by severity.
        """
        counts = defaultdict(int)
        for violation in violations:
            counts[violation.severity] += 1
        return dict(counts)

    def generate_report(self) -> dict[str, Any]:
        """
        Generate comprehensive quality gate report.
        """
        total_violations = len(self.violations)
        severity_counts = self._count_by_severity(self.violations)

        # Group by gate
        gate_counts = defaultdict(int)
        for violation in self.violations:
            gate_counts[violation.gate] += 1

        # Group by category
        category_counts = defaultdict(int)
        for violation in self.violations:
            category_counts[violation.category] += 1

        # Group by file
        file_violations = defaultdict(list)
        for violation in self.violations:
            file_violations[violation.file].append(violation)

        return {
            "summary": {
                "total_violations": total_violations,
                "severity_counts": severity_counts,
                "gate_counts": dict(gate_counts),
                "category_counts": dict(category_counts),
                "files_affected": len(file_violations),
            },
            "violations": [
                {
                    "gate": violation.gate,
                    "severity": violation.severity,
                    "file": violation.file,
                    "line": violation.line,
                    "column": violation.column,
                    "message": violation.message,
                    "suggestion": violation.suggestion,
                    "confidence": violation.confidence,
                    "category": violation.category,
                }
                for violation in self.violations
            ],
            "files": {
                file: {
                    "violation_count": len(violations),
                    "severity_counts": self._count_by_severity(violations),
                }
                for file, violations in file_violations.items()
            },
        }


def main():
    """
    Main entry point.
    """
    parser = argparse.ArgumentParser(description="Integration Quality Gates")
    parser.add_argument("path", help="Path to analyze")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--severity", choices=["low", "medium", "high"], help="Filter by severity")
    parser.add_argument("--gate", help="Filter by quality gate")
    parser.add_argument("--category", help="Filter by category")
    parser.add_argument("--disable", nargs="+", help="Disable specific gates")
    parser.add_argument("--run-tests", help="Run integration tests")
    parser.add_argument("--run-benchmarks", help="Run performance benchmarks")
    parser.add_argument("--validate-api", help="Validate API contracts")
    parser.add_argument("--validate-deployment", help="Validate deployment readiness")

    args = parser.parse_args()

    gates = IntegrationQualityGates()

    # Disable gates if requested
    if args.disable:
        for gate in args.disable:
            if gate in gates.gates:
                gates.gates[gate] = False

    # Analyze files
    path = Path(args.path)
    if path.is_file():
        files = [path]
    else:
        files = list(path.rglob("*.py"))

    for file_path in files:
        gates.analyze_file(file_path)

    # Run additional validations if requested
    if args.run_tests:
        test_results = gates.run_integration_tests(args.run_tests)
        print(f"Integration tests: {test_results['status']}")

    if args.run_benchmarks:
        benchmark_results = gates.run_performance_benchmarks(args.run_benchmarks)
        print(f"Performance benchmarks: {benchmark_results['status']}")

    if args.validate_api:
        api_results = gates.validate_api_contracts(args.validate_api)
        print(f"API validation: {api_results['status']}")

    if args.validate_deployment:
        deployment_results = gates.validate_deployment_readiness(args.validate_deployment)
        print(f"Deployment validation: {deployment_results['status']}")

    # Generate report
    report = gates.generate_report()

    # Filter results if requested
    if args.severity or args.gate or args.category:
        filtered_violations = []
        for violation in report["violations"]:
            if args.severity and violation["severity"] != args.severity:
                continue
            if args.gate and violation["gate"] != args.gate:
                continue
            if args.category and violation["category"] != args.category:
                continue
            filtered_violations.append(violation)
        report["violations"] = filtered_violations
        report["summary"]["total_violations"] = len(filtered_violations)

    if args.json:
        print(json.dumps(report, indent=2))
    else:
        # Pretty print report
        print("🚪 INTEGRATION QUALITY GATES REPORT")
        print("=" * 60)
        print(f"Total violations found: {report['summary']['total_violations']}")
        print(f"Files affected: {report['summary']['files_affected']}")
        print()

        print("Severity breakdown:")
        for severity, count in report["summary"]["severity_counts"].items():
            print(f"  {severity}: {count}")
        print()

        print("Gate breakdown:")
        for gate, count in report["summary"]["gate_counts"].items():
            print(f"  {gate}: {count}")
        print()

        print("Category breakdown:")
        for category, count in report["summary"]["category_counts"].items():
            print(f"  {category}: {count}")
        print()

        if report["violations"]:
            print("Detailed findings:")
            for violation in report["violations"]:
                print(
                    f"  {violation['severity'].upper()}: {violation['gate']} - {violation['category']}",
                )
                print(f"    {violation['file']}:{violation['line']}")
                print(f"    {violation['message']}")
                print(f"    Suggestion: {violation['suggestion']}")
                print()


if __name__ == "__main__":
    main()
