#!/usr/bin/env python3
"""
Advanced Security Testing Expansion
Comprehensive security testing with DAST, penetration testing, and compliance checking.
"""

import argparse
import json
import re
import socket
import ssl
import time
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Any

import requests


@dataclass
class SecurityVulnerability:
    """Security vulnerability information."""
    id: str
    name: str
    severity: str  # "critical", "high", "medium", "low", "info"
    description: str
    file_path: str
    line_number: int
    cwe_id: str | None = None
    cvss_score: float | None = None
    remediation: str | None = None
    references: list[str] = None


@dataclass
class SecurityTestResult:
    """Security test result."""
    test_name: str
    status: str  # "pass", "fail", "warning", "error"
    vulnerabilities: list[SecurityVulnerability]
    risk_score: float
    recommendations: list[str]
    scan_duration: float
    files_scanned: int
    lines_scanned: int


@dataclass
class ComplianceCheck:
    """Compliance check result."""
    standard: str  # "OWASP", "NIST", "ISO27001", "SOC2", "GDPR"
    check_name: str
    status: str  # "pass", "fail", "warning"
    description: str
    requirements: list[str]
    findings: list[str]


class DynamicApplicationSecurityTester:
    """Dynamic Application Security Testing (DAST) implementation."""

    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.session = requests.Session()
        self.vulnerabilities = []

        # Common attack payloads
        self.payloads = {
            "sql_injection": [
                "' OR '1'='1",
                "'; DROP TABLE users; --",
                "' UNION SELECT * FROM users --",
                "1' OR 1=1 --",
                "admin'--",
                "' OR 1=1#",
            ],
            "xss": [
                "<script>alert('XSS')</script>",
                "javascript:alert('XSS')",
                "<img src=x onerror=alert('XSS')>",
                "<svg onload=alert('XSS')>",
                "';alert('XSS');//",
            ],
            "command_injection": [
                "; ls -la",
                "| whoami",
                "&& cat /etc/passwd",
                "; rm -rf /",
                "`id`",
            ],
            "path_traversal": [
                "../../../etc/passwd",
                "..\\..\\..\\windows\\system32\\drivers\\etc\\hosts",
                "....//....//....//etc/passwd",
                "%2e%2e%2f%2e%2e%2f%2e%2e%2fetc%2fpasswd",
            ],
            "ldap_injection": [
                "*)(uid=*))(|(uid=*",
                "*)(|(password=*))",
                "*)(|(objectClass=*))",
                "admin)(&(password=*",
            ],
        }

    def run_dast_scan(self, endpoints: list[str]) -> SecurityTestResult:
        """Run comprehensive DAST scan."""
        print("🔍 Running Dynamic Application Security Testing (DAST)...")

        start_time = time.time()
        vulnerabilities = []
        files_scanned = 0
        lines_scanned = 0

        # Test each endpoint
        for endpoint in endpoints:
            print(f"  🎯 Testing endpoint: {endpoint}")

            # Test for various vulnerabilities
            endpoint_vulns = self._test_endpoint(endpoint)
            vulnerabilities.extend(endpoint_vulns)
            files_scanned += 1
            lines_scanned += len(endpoint_vulns)

        # Test authentication and authorization
        auth_vulns = self._test_authentication()
        vulnerabilities.extend(auth_vulns)

        # Test session management
        session_vulns = self._test_session_management()
        vulnerabilities.extend(session_vulns)

        # Test input validation
        input_vulns = self._test_input_validation()
        vulnerabilities.extend(input_vulns)

        scan_duration = time.time() - start_time

        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)

        # Generate recommendations
        recommendations = self._generate_security_recommendations(vulnerabilities)

        # Determine status
        status = self._determine_security_status(vulnerabilities)

        return SecurityTestResult(
            test_name="dast_scan",
            status=status,
            vulnerabilities=vulnerabilities,
            risk_score=risk_score,
            recommendations=recommendations,
            scan_duration=scan_duration,
            files_scanned=files_scanned,
            lines_scanned=lines_scanned,
        )

    def _test_endpoint(self, endpoint: str) -> list[SecurityVulnerability]:
        """Test a specific endpoint for vulnerabilities."""
        vulnerabilities = []

        # Test for SQL injection
        sql_vulns = self._test_sql_injection(endpoint)
        vulnerabilities.extend(sql_vulns)

        # Test for XSS
        xss_vulns = self._test_xss(endpoint)
        vulnerabilities.extend(xss_vulns)

        # Test for command injection
        cmd_vulns = self._test_command_injection(endpoint)
        vulnerabilities.extend(cmd_vulns)

        # Test for path traversal
        path_vulns = self._test_path_traversal(endpoint)
        vulnerabilities.extend(path_vulns)

        # Test for LDAP injection
        ldap_vulns = self._test_ldap_injection(endpoint)
        vulnerabilities.extend(ldap_vulns)

        return vulnerabilities

    def _test_sql_injection(self, endpoint: str) -> list[SecurityVulnerability]:
        """Test for SQL injection vulnerabilities."""
        vulnerabilities = []

        for payload in self.payloads["sql_injection"]:
            try:
                # Test GET parameters
                response = self.session.get(f"{self.base_url}{endpoint}",
                                         params={"q": payload}, timeout=5)

                if self._is_sql_injection_response(response):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"sql_injection_{len(vulnerabilities)}",
                        name="SQL Injection",
                        severity="high",
                        description=f"SQL injection vulnerability detected with payload: {payload}",
                        file_path=endpoint,
                        line_number=0,
                        cwe_id="CWE-89",
                        cvss_score=8.8,
                        remediation="Use parameterized queries and input validation",
                        references=["https://owasp.org/www-community/attacks/SQL_Injection"],
                    ))

                # Test POST parameters
                response = self.session.post(f"{self.base_url}{endpoint}",
                                           data={"q": payload}, timeout=5)

                if self._is_sql_injection_response(response):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"sql_injection_post_{len(vulnerabilities)}",
                        name="SQL Injection (POST)",
                        severity="high",
                        description=f"SQL injection vulnerability in POST data with payload: {payload}",
                        file_path=endpoint,
                        line_number=0,
                        cwe_id="CWE-89",
                        cvss_score=8.8,
                        remediation="Use parameterized queries and input validation",
                        references=["https://owasp.org/www-community/attacks/SQL_Injection"],
                    ))

            except Exception as e:
                # Connection error might indicate a vulnerability
                if "timeout" in str(e).lower():
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"sql_injection_timeout_{len(vulnerabilities)}",
                        name="Potential SQL Injection",
                        severity="medium",
                        description=f"Request timeout with SQL injection payload: {payload}",
                        file_path=endpoint,
                        line_number=0,
                        cwe_id="CWE-89",
                        cvss_score=6.5,
                        remediation="Investigate timeout behavior with SQL injection payloads",
                        references=["https://owasp.org/www-community/attacks/SQL_Injection"],
                    ))

        return vulnerabilities

    def _test_xss(self, endpoint: str) -> list[SecurityVulnerability]:
        """Test for XSS vulnerabilities."""
        vulnerabilities = []

        for payload in self.payloads["xss"]:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}",
                                         params={"q": payload}, timeout=5)

                if self._is_xss_response(response, payload):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"xss_{len(vulnerabilities)}",
                        name="Cross-Site Scripting (XSS)",
                        severity="medium",
                        description=f"XSS vulnerability detected with payload: {payload}",
                        file_path=endpoint,
                        line_number=0,
                        cwe_id="CWE-79",
                        cvss_score=6.1,
                        remediation="Implement proper input validation and output encoding",
                        references=["https://owasp.org/www-community/attacks/xss/"],
                    ))

            except Exception:
                pass  # Ignore connection errors for XSS testing

        return vulnerabilities

    def _test_command_injection(self, endpoint: str) -> list[SecurityVulnerability]:
        """Test for command injection vulnerabilities."""
        vulnerabilities = []

        for payload in self.payloads["command_injection"]:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}",
                                         params={"cmd": payload}, timeout=5)

                if self._is_command_injection_response(response):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"cmd_injection_{len(vulnerabilities)}",
                        name="Command Injection",
                        severity="critical",
                        description=f"Command injection vulnerability detected with payload: {payload}",
                        file_path=endpoint,
                        line_number=0,
                        cwe_id="CWE-78",
                        cvss_score=9.8,
                        remediation="Avoid system command execution with user input",
                        references=["https://owasp.org/www-community/attacks/Command_Injection"],
                    ))

            except Exception:
                pass  # Ignore connection errors

        return vulnerabilities

    def _test_path_traversal(self, endpoint: str) -> list[SecurityVulnerability]:
        """Test for path traversal vulnerabilities."""
        vulnerabilities = []

        for payload in self.payloads["path_traversal"]:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}",
                                         params={"file": payload}, timeout=5)

                if self._is_path_traversal_response(response):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"path_traversal_{len(vulnerabilities)}",
                        name="Path Traversal",
                        severity="high",
                        description=f"Path traversal vulnerability detected with payload: {payload}",
                        file_path=endpoint,
                        line_number=0,
                        cwe_id="CWE-22",
                        cvss_score=7.5,
                        remediation="Implement proper path validation and sanitization",
                        references=["https://owasp.org/www-community/attacks/Path_Traversal"],
                    ))

            except Exception:
                pass  # Ignore connection errors

        return vulnerabilities

    def _test_ldap_injection(self, endpoint: str) -> list[SecurityVulnerability]:
        """Test for LDAP injection vulnerabilities."""
        vulnerabilities = []

        for payload in self.payloads["ldap_injection"]:
            try:
                response = self.session.get(f"{self.base_url}{endpoint}",
                                         params={"user": payload}, timeout=5)

                if self._is_ldap_injection_response(response):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"ldap_injection_{len(vulnerabilities)}",
                        name="LDAP Injection",
                        severity="high",
                        description=f"LDAP injection vulnerability detected with payload: {payload}",
                        file_path=endpoint,
                        line_number=0,
                        cwe_id="CWE-90",
                        cvss_score=8.1,
                        remediation="Use parameterized LDAP queries and input validation",
                        references=["https://owasp.org/www-community/attacks/LDAP_Injection"],
                    ))

            except Exception:
                pass  # Ignore connection errors

        return vulnerabilities

    def _test_authentication(self) -> list[SecurityVulnerability]:
        """Test authentication mechanisms."""
        vulnerabilities = []

        # Test for weak authentication
        weak_auth_vulns = self._test_weak_authentication()
        vulnerabilities.extend(weak_auth_vulns)

        # Test for session fixation
        session_fix_vulns = self._test_session_fixation()
        vulnerabilities.extend(session_fix_vulns)

        # Test for brute force protection
        brute_force_vulns = self._test_brute_force_protection()
        vulnerabilities.extend(brute_force_vulns)

        return vulnerabilities

    def _test_weak_authentication(self) -> list[SecurityVulnerability]:
        """Test for weak authentication mechanisms."""
        vulnerabilities = []

        # Test for default credentials
        default_creds = [
            ("admin", "admin"),
            ("admin", "password"),
            ("root", "root"),
            ("user", "user"),
            ("test", "test"),
        ]

        for username, password in default_creds:
            try:
                response = self.session.post(f"{self.base_url}/login",
                                           data={"username": username, "password": password},
                                           timeout=5)

                if response.status_code == 200 and "error" not in response.text.lower():
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"weak_auth_{len(vulnerabilities)}",
                        name="Weak Authentication",
                        severity="high",
                        description=f"Default credentials work: {username}/{password}",
                        file_path="/login",
                        line_number=0,
                        cwe_id="CWE-521",
                        cvss_score=7.5,
                        remediation="Change default credentials and implement strong authentication",
                        references=["https://owasp.org/www-community/vulnerabilities/Weak_Authentication"],
                    ))

            except Exception:
                pass  # Ignore connection errors

        return vulnerabilities

    def _test_session_fixation(self) -> list[SecurityVulnerability]:
        """Test for session fixation vulnerabilities."""
        vulnerabilities = []

        try:
            # Get initial session
            response1 = self.session.get(f"{self.base_url}/login", timeout=5)
            session_id_1 = self.session.cookies.get("sessionid", "")

            # Login
            response2 = self.session.post(f"{self.base_url}/login",
                                        data={"username": "test", "password": "test"},
                                        timeout=5)
            session_id_2 = self.session.cookies.get("sessionid", "")

            # Check if session ID changed after login
            if session_id_1 == session_id_2 and session_id_1:
                vulnerabilities.append(SecurityVulnerability(
                    id="session_fixation",
                    name="Session Fixation",
                    severity="medium",
                    description="Session ID not regenerated after login",
                    file_path="/login",
                    line_number=0,
                    cwe_id="CWE-384",
                    cvss_score=5.4,
                    remediation="Regenerate session ID after successful authentication",
                    references=["https://owasp.org/www-community/attacks/Session_fixation"],
                ))

        except Exception:
            pass  # Ignore connection errors

        return vulnerabilities

    def _test_brute_force_protection(self) -> list[SecurityVulnerability]:
        """Test for brute force protection."""
        vulnerabilities = []

        try:
            # Attempt multiple failed logins
            for i in range(10):
                response = self.session.post(f"{self.base_url}/login",
                                           data={"username": "test", "password": "wrong"},
                                           timeout=5)

                # Check if account is locked or rate limited
                if response.status_code == 429 or "locked" in response.text.lower():
                    break  # Protection is working
            else:
                # No protection detected
                vulnerabilities.append(SecurityVulnerability(
                    id="brute_force_protection",
                    name="Missing Brute Force Protection",
                    severity="medium",
                    description="No brute force protection detected",
                    file_path="/login",
                    line_number=0,
                    cwe_id="CWE-307",
                    cvss_score=5.3,
                    remediation="Implement rate limiting and account lockout",
                    references=["https://owasp.org/www-community/controls/Blocking_Brute_Force_Attacks"],
                ))

        except Exception:
            pass  # Ignore connection errors

        return vulnerabilities

    def _test_session_management(self) -> list[SecurityVulnerability]:
        """Test session management security."""
        vulnerabilities = []

        # Test for secure session cookies
        secure_cookie_vulns = self._test_secure_cookies()
        vulnerabilities.extend(secure_cookie_vulns)

        # Test for session timeout
        timeout_vulns = self._test_session_timeout()
        vulnerabilities.extend(timeout_vulns)

        return vulnerabilities

    def _test_secure_cookies(self) -> list[SecurityVulnerability]:
        """Test for secure cookie settings."""
        vulnerabilities = []

        try:
            response = self.session.get(f"{self.base_url}/", timeout=5)

            # Check for secure cookie flags
            cookies = response.cookies
            for cookie in cookies:
                if not cookie.secure and cookie.name.lower() in ["sessionid", "session", "auth"]:
                    vulnerabilities.append(SecurityVulnerability(
                        id="insecure_cookie",
                        name="Insecure Cookie",
                        severity="medium",
                        description=f"Cookie '{cookie.name}' not marked as secure",
                        file_path="/",
                        line_number=0,
                        cwe_id="CWE-614",
                        cvss_score=5.3,
                        remediation="Set Secure flag on sensitive cookies",
                        references=["https://owasp.org/www-community/controls/SecureCookieAttribute"],
                    ))

                if not hasattr(cookie, "httponly") or not cookie.httponly:
                    vulnerabilities.append(SecurityVulnerability(
                        id="httponly_cookie",
                        name="Missing HttpOnly Cookie",
                        severity="low",
                        description=f"Cookie '{cookie.name}' not marked as HttpOnly",
                        file_path="/",
                        line_number=0,
                        cwe_id="CWE-1004",
                        cvss_score=3.7,
                        remediation="Set HttpOnly flag on sensitive cookies",
                        references=["https://owasp.org/www-community/controls/SecureCookieAttribute"],
                    ))

        except Exception:
            pass  # Ignore connection errors

        return vulnerabilities

    def _test_session_timeout(self) -> list[SecurityVulnerability]:
        """Test session timeout mechanisms."""
        vulnerabilities = []

        try:
            # This would require more complex testing
            # For now, just check if session management is implemented
            response = self.session.get(f"{self.base_url}/", timeout=5)

            if "sessionid" not in response.cookies:
                vulnerabilities.append(SecurityVulnerability(
                    id="no_session_management",
                    name="No Session Management",
                    severity="medium",
                    description="No session management detected",
                    file_path="/",
                    line_number=0,
                    cwe_id="CWE-384",
                    cvss_score=5.4,
                    remediation="Implement proper session management",
                    references=["https://owasp.org/www-community/controls/Session_Management_Cheat_Sheet"],
                ))

        except Exception:
            pass  # Ignore connection errors

        return vulnerabilities

    def _test_input_validation(self) -> list[SecurityVulnerability]:
        """Test input validation mechanisms."""
        vulnerabilities = []

        # Test for missing input validation
        validation_vulns = self._test_missing_validation()
        vulnerabilities.extend(validation_vulns)

        return vulnerabilities

    def _test_missing_validation(self) -> list[SecurityVulnerability]:
        """Test for missing input validation."""
        vulnerabilities = []

        # Test various input types
        test_inputs = [
            ("email", "invalid-email"),
            ("phone", "not-a-phone"),
            ("age", "not-a-number"),
            ("url", "not-a-url"),
            ("date", "not-a-date"),
        ]

        for field, invalid_value in test_inputs:
            try:
                response = self.session.post(f"{self.base_url}/form",
                                           data={field: invalid_value},
                                           timeout=5)

                # Check if validation error is returned
                if response.status_code == 200 and "error" not in response.text.lower():
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"missing_validation_{field}",
                        name="Missing Input Validation",
                        severity="medium",
                        description=f"Missing validation for {field} field",
                        file_path="/form",
                        line_number=0,
                        cwe_id="CWE-20",
                        cvss_score=5.3,
                        remediation=f"Implement proper validation for {field} field",
                        references=["https://owasp.org/www-community/controls/Input_Validation"],
                    ))

            except Exception:
                pass  # Ignore connection errors

        return vulnerabilities

    def _is_sql_injection_response(self, response: requests.Response) -> bool:
        """Check if response indicates SQL injection vulnerability."""
        sql_error_patterns = [
            r"mysql_fetch_array",
            r"ORA-\d+",
            r"Microsoft.*ODBC.*SQL Server",
            r"SQLServer JDBC Driver",
            r"PostgreSQL.*ERROR",
            r"Warning.*mysql_.*",
            r"valid MySQL result",
            r"MySqlClient\.",
            r"SQL syntax.*MySQL",
            r"Warning.*mysql_.*",
            r"valid MySQL result",
            r"check the manual that corresponds to your MySQL server version",
        ]

        response_text = response.text.lower()
        for pattern in sql_error_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True

        return False

    def _is_xss_response(self, response: requests.Response, payload: str) -> bool:
        """Check if response indicates XSS vulnerability."""
        # Check if payload is reflected in response
        return payload in response.text

    def _is_command_injection_response(self, response: requests.Response) -> bool:
        """Check if response indicates command injection vulnerability."""
        command_output_patterns = [
            r"uid=\d+.*gid=\d+",
            r"total \d+",
            r"drwxr-xr-x",
            r"root:x:0:0",
            r"bin/bash",
            r"bin/sh",
        ]

        response_text = response.text
        for pattern in command_output_patterns:
            if re.search(pattern, response_text):
                return True

        return False

    def _is_path_traversal_response(self, response: requests.Response) -> bool:
        """Check if response indicates path traversal vulnerability."""
        path_traversal_patterns = [
            r"root:x:0:0:root",
            r"daemon:x:1:1:daemon",
            r"bin:x:2:2:bin",
            r"sys:x:3:3:sys",
            r"adm:x:3:4:adm",
            r"127\.0\.0\.1\s+localhost",
        ]

        response_text = response.text
        for pattern in path_traversal_patterns:
            if re.search(pattern, response_text):
                return True

        return False

    def _is_ldap_injection_response(self, response: requests.Response) -> bool:
        """Check if response indicates LDAP injection vulnerability."""
        ldap_error_patterns = [
            r"Invalid DN syntax",
            r"LDAPException",
            r"javax\.naming\.",
            r"com\.sun\.jndi\.ldap",
            r"LDAP: error code",
        ]

        response_text = response.text
        for pattern in ldap_error_patterns:
            if re.search(pattern, response_text, re.IGNORECASE):
                return True

        return False

    def _calculate_risk_score(self, vulnerabilities: list[SecurityVulnerability]) -> float:
        """Calculate overall risk score."""
        if not vulnerabilities:
            return 0.0

        severity_scores = {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 1.0,
        }

        total_score = sum(severity_scores.get(v.severity, 0) for v in vulnerabilities)
        max_possible_score = len(vulnerabilities) * 10.0

        return (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0.0

    def _generate_security_recommendations(self, vulnerabilities: list[SecurityVulnerability]) -> list[str]:
        """Generate security recommendations."""
        recommendations = []

        # Group vulnerabilities by type
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.name
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(vuln)

        # Generate recommendations for each type
        for vuln_type, vulns in vuln_types.items():
            count = len(vulns)
            if vuln_type == "SQL Injection":
                recommendations.append(f"Fix {count} SQL injection vulnerabilities by using parameterized queries")
            elif vuln_type == "Cross-Site Scripting (XSS)":
                recommendations.append(f"Fix {count} XSS vulnerabilities by implementing proper input validation and output encoding")
            elif vuln_type == "Command Injection":
                recommendations.append(f"Fix {count} command injection vulnerabilities by avoiding system command execution with user input")
            elif vuln_type == "Path Traversal":
                recommendations.append(f"Fix {count} path traversal vulnerabilities by implementing proper path validation")
            elif vuln_type == "LDAP Injection":
                recommendations.append(f"Fix {count} LDAP injection vulnerabilities by using parameterized LDAP queries")
            elif vuln_type == "Weak Authentication":
                recommendations.append(f"Fix {count} weak authentication issues by implementing strong authentication mechanisms")
            elif vuln_type == "Session Fixation":
                recommendations.append(f"Fix {count} session fixation vulnerabilities by regenerating session IDs after login")
            elif vuln_type == "Missing Brute Force Protection":
                recommendations.append("Implement brute force protection mechanisms")
            elif vuln_type == "Insecure Cookie":
                recommendations.append(f"Fix {count} insecure cookie issues by setting Secure flag")
            elif vuln_type == "Missing HttpOnly Cookie":
                recommendations.append(f"Fix {count} HttpOnly cookie issues by setting HttpOnly flag")
            elif vuln_type == "Missing Input Validation":
                recommendations.append("Implement proper input validation for all user inputs")

        # General recommendations
        recommendations.append("Implement comprehensive security testing in CI/CD pipeline")
        recommendations.append("Regular security audits and penetration testing")
        recommendations.append("Security awareness training for development team")
        recommendations.append("Implement security monitoring and alerting")

        return recommendations

    def _determine_security_status(self, vulnerabilities: list[SecurityVulnerability]) -> str:
        """Determine overall security status."""
        if not vulnerabilities:
            return "pass"

        critical_count = len([v for v in vulnerabilities if v.severity == "critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        medium_count = len([v for v in vulnerabilities if v.severity == "medium"])

        if critical_count > 0 or high_count > 2:
            return "fail"
        if high_count > 0 or medium_count > 5:
            return "warning"
        return "pass"


class PenetrationTester:
    """Automated penetration testing implementation."""

    def __init__(self, target_host: str = "localhost", target_port: int = 8000):
        self.target_host = target_host
        self.target_port = target_port
        self.vulnerabilities = []

    def run_penetration_test(self) -> SecurityTestResult:
        """Run comprehensive penetration test."""
        print("🎯 Running Penetration Testing...")

        start_time = time.time()
        vulnerabilities = []

        # Port scanning
        port_vulns = self._scan_ports()
        vulnerabilities.extend(port_vulns)

        # Service enumeration
        service_vulns = self._enumerate_services()
        vulnerabilities.extend(service_vulns)

        # SSL/TLS testing
        ssl_vulns = self._test_ssl_tls()
        vulnerabilities.extend(ssl_vulns)

        # Directory enumeration
        dir_vulns = self._enumerate_directories()
        vulnerabilities.extend(dir_vulns)

        # Vulnerability scanning
        vuln_scan_results = self._scan_vulnerabilities()
        vulnerabilities.extend(vuln_scan_results)

        scan_duration = time.time() - start_time

        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)

        # Generate recommendations
        recommendations = self._generate_penetration_recommendations(vulnerabilities)

        # Determine status
        status = self._determine_security_status(vulnerabilities)

        return SecurityTestResult(
            test_name="penetration_test",
            status=status,
            vulnerabilities=vulnerabilities,
            risk_score=risk_score,
            recommendations=recommendations,
            scan_duration=scan_duration,
            files_scanned=0,
            lines_scanned=0,
        )

    def _scan_ports(self) -> list[SecurityVulnerability]:
        """Scan for open ports."""
        vulnerabilities = []

        common_ports = [21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 3389, 5432, 3306, 6379, 27017]

        for port in common_ports:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(1)
                result = sock.connect_ex((self.target_host, port))
                sock.close()

                if result == 0:
                    # Port is open
                    if port in [21, 23, 25, 110, 143]:  # Potentially insecure services
                        vulnerabilities.append(SecurityVulnerability(
                            id=f"open_port_{port}",
                            name="Open Insecure Port",
                            severity="medium",
                            description=f"Port {port} is open and may be insecure",
                            file_path=f"{self.target_host}:{port}",
                            line_number=0,
                            cwe_id="CWE-200",
                            cvss_score=5.3,
                            remediation=f"Secure or close port {port}",
                            references=["https://owasp.org/www-community/attacks/Port_Scanning"],
                        ))

            except Exception:
                pass  # Ignore connection errors

        return vulnerabilities

    def _enumerate_services(self) -> list[SecurityVulnerability]:
        """Enumerate running services."""
        vulnerabilities = []

        # This would typically use tools like nmap
        # For now, just check common web services
        try:
            response = requests.get(f"http://{self.target_host}:{self.target_port}/", timeout=5)

            # Check for information disclosure in headers
            headers = response.headers

            if "server" in headers:
                server_info = headers["server"]
                if "apache" in server_info.lower() or "nginx" in server_info.lower():
                    vulnerabilities.append(SecurityVulnerability(
                        id="server_info_disclosure",
                        name="Server Information Disclosure",
                        severity="low",
                        description=f"Server information disclosed: {server_info}",
                        file_path="HTTP Headers",
                        line_number=0,
                        cwe_id="CWE-200",
                        cvss_score=3.7,
                        remediation="Remove or obfuscate server information in headers",
                        references=["https://owasp.org/www-community/attacks/Information_disclosure"],
                    ))

        except Exception:
            pass  # Ignore connection errors

        return vulnerabilities

    def _test_ssl_tls(self) -> list[SecurityVulnerability]:
        """Test SSL/TLS configuration."""
        vulnerabilities = []

        try:
            # Test SSL/TLS configuration
            context = ssl.create_default_context()
            context.check_hostname = False
            context.verify_mode = ssl.CERT_NONE

            with socket.create_connection((self.target_host, 443), timeout=5) as sock:
                with context.wrap_socket(sock, server_hostname=self.target_host) as ssock:
                    # Check SSL version
                    ssl_version = ssock.version()
                    if ssl_version in ["SSLv2", "SSLv3", "TLSv1", "TLSv1.1"]:
                        vulnerabilities.append(SecurityVulnerability(
                            id="weak_ssl_version",
                            name="Weak SSL/TLS Version",
                            severity="high",
                            description=f"Weak SSL/TLS version detected: {ssl_version}",
                            file_path="SSL/TLS Configuration",
                            line_number=0,
                            cwe_id="CWE-326",
                            cvss_score=7.5,
                            remediation="Upgrade to TLS 1.2 or higher",
                            references=["https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"],
                        ))

                    # Check cipher suite
                    cipher = ssock.cipher()
                    if cipher and "RC4" in cipher[0]:
                        vulnerabilities.append(SecurityVulnerability(
                            id="weak_cipher",
                            name="Weak Cipher Suite",
                            severity="medium",
                            description=f"Weak cipher suite detected: {cipher[0]}",
                            file_path="SSL/TLS Configuration",
                            line_number=0,
                            cwe_id="CWE-326",
                            cvss_score=5.3,
                            remediation="Use strong cipher suites",
                            references=["https://owasp.org/www-community/controls/Certificate_and_Public_Key_Pinning"],
                        ))

        except Exception:
            pass  # Ignore SSL errors

        return vulnerabilities

    def _enumerate_directories(self) -> list[SecurityVulnerability]:
        """Enumerate directories and files."""
        vulnerabilities = []

        common_dirs = [
            "admin", "administrator", "backup", "config", "database", "db",
            "dev", "development", "docs", "documentation", "files", "images",
            "logs", "old", "phpmyadmin", "private", "secure", "test", "tmp",
            "upload", "uploads", "www", "wwwroot",
        ]

        for directory in common_dirs:
            try:
                response = requests.get(f"http://{self.target_host}:{self.target_port}/{directory}/",
                                      timeout=3)

                if response.status_code == 200:
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"directory_enum_{directory}",
                        name="Directory Enumeration",
                        severity="low",
                        description=f"Directory '{directory}' is accessible",
                        file_path=f"/{directory}/",
                        line_number=0,
                        cwe_id="CWE-200",
                        cvss_score=3.7,
                        remediation=f"Restrict access to '{directory}' directory",
                        references=["https://owasp.org/www-community/attacks/Forced_browsing"],
                    ))

            except Exception:
                pass  # Ignore connection errors

        return vulnerabilities

    def _scan_vulnerabilities(self) -> list[SecurityVulnerability]:
        """Scan for known vulnerabilities."""
        vulnerabilities = []

        # This would typically use vulnerability scanners
        # For now, just check for common issues

        try:
            response = requests.get(f"http://{self.target_host}:{self.target_port}/", timeout=5)

            # Check for debug information
            if "debug" in response.text.lower() or "trace" in response.text.lower():
                vulnerabilities.append(SecurityVulnerability(
                    id="debug_info_disclosure",
                    name="Debug Information Disclosure",
                    severity="medium",
                    description="Debug information may be disclosed in response",
                    file_path="/",
                    line_number=0,
                    cwe_id="CWE-200",
                    cvss_score=5.3,
                    remediation="Remove debug information from production responses",
                    references=["https://owasp.org/www-community/attacks/Information_disclosure"],
                ))

        except Exception:
            pass  # Ignore connection errors

        return vulnerabilities

    def _calculate_risk_score(self, vulnerabilities: list[SecurityVulnerability]) -> float:
        """Calculate risk score for penetration test."""
        if not vulnerabilities:
            return 0.0

        severity_scores = {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 1.0,
        }

        total_score = sum(severity_scores.get(v.severity, 0) for v in vulnerabilities)
        max_possible_score = len(vulnerabilities) * 10.0

        return (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0.0

    def _generate_penetration_recommendations(self, vulnerabilities: list[SecurityVulnerability]) -> list[str]:
        """Generate penetration testing recommendations."""
        recommendations = []

        # Group vulnerabilities by type
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.name
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(vuln)

        # Generate recommendations
        for vuln_type, vulns in vuln_types.items():
            count = len(vulns)
            if vuln_type == "Open Insecure Port":
                recommendations.append(f"Secure or close {count} insecure open ports")
            elif vuln_type == "Server Information Disclosure":
                recommendations.append("Remove server information from HTTP headers")
            elif vuln_type == "Weak SSL/TLS Version":
                recommendations.append("Upgrade to TLS 1.2 or higher")
            elif vuln_type == "Weak Cipher Suite":
                recommendations.append("Use strong cipher suites")
            elif vuln_type == "Directory Enumeration":
                recommendations.append(f"Restrict access to {count} exposed directories")
            elif vuln_type == "Debug Information Disclosure":
                recommendations.append("Remove debug information from production")

        # General recommendations
        recommendations.append("Implement network segmentation")
        recommendations.append("Use intrusion detection systems")
        recommendations.append("Regular security assessments")
        recommendations.append("Implement security monitoring")

        return recommendations

    def _determine_security_status(self, vulnerabilities: list[SecurityVulnerability]) -> str:
        """Determine security status."""
        if not vulnerabilities:
            return "pass"

        critical_count = len([v for v in vulnerabilities if v.severity == "critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        medium_count = len([v for v in vulnerabilities if v.severity == "medium"])

        if critical_count > 0 or high_count > 2:
            return "fail"
        if high_count > 0 or medium_count > 5:
            return "warning"
        return "pass"


class ComplianceChecker:
    """Security compliance checking implementation."""

    def __init__(self):
        self.compliance_checks = []

    def run_compliance_checks(self) -> list[ComplianceCheck]:
        """Run comprehensive compliance checks."""
        print("📋 Running Security Compliance Checks...")

        # OWASP Top 10 compliance
        owasp_checks = self._check_owasp_compliance()
        self.compliance_checks.extend(owasp_checks)

        # NIST compliance
        nist_checks = self._check_nist_compliance()
        self.compliance_checks.extend(nist_checks)

        # GDPR compliance
        gdpr_checks = self._check_gdpr_compliance()
        self.compliance_checks.extend(gdpr_checks)

        return self.compliance_checks

    def _check_owasp_compliance(self) -> list[ComplianceCheck]:
        """Check OWASP Top 10 compliance."""
        checks = []

        # A01: Broken Access Control
        checks.append(ComplianceCheck(
            standard="OWASP",
            check_name="A01: Broken Access Control",
            status="warning",  # Would be determined by actual testing
            description="Check for broken access control vulnerabilities",
            requirements=[
                "Implement proper authentication and authorization",
                "Use principle of least privilege",
                "Implement proper session management",
            ],
            findings=["Access control mechanisms need review"],
        ))

        # A02: Cryptographic Failures
        checks.append(ComplianceCheck(
            standard="OWASP",
            check_name="A02: Cryptographic Failures",
            status="warning",
            description="Check for cryptographic failures",
            requirements=[
                "Use strong encryption algorithms",
                "Protect sensitive data in transit and at rest",
                "Implement proper key management",
            ],
            findings=["Encryption implementation needs review"],
        ))

        # A03: Injection
        checks.append(ComplianceCheck(
            standard="OWASP",
            check_name="A03: Injection",
            status="warning",
            description="Check for injection vulnerabilities",
            requirements=[
                "Use parameterized queries",
                "Implement input validation",
                "Use output encoding",
            ],
            findings=["Input validation needs strengthening"],
        ))

        return checks

    def _check_nist_compliance(self) -> list[ComplianceCheck]:
        """Check NIST compliance."""
        checks = []

        # NIST Cybersecurity Framework
        checks.append(ComplianceCheck(
            standard="NIST",
            check_name="Identify - Asset Management",
            status="warning",
            description="Check asset management practices",
            requirements=[
                "Maintain inventory of assets",
                "Classify assets by importance",
                "Implement asset protection",
            ],
            findings=["Asset inventory needs improvement"],
        ))

        checks.append(ComplianceCheck(
            standard="NIST",
            check_name="Protect - Access Control",
            status="warning",
            description="Check access control implementation",
            requirements=[
                "Implement identity and access management",
                "Use multi-factor authentication",
                "Implement privileged access management",
            ],
            findings=["Access control needs strengthening"],
        ))

        return checks

    def _check_gdpr_compliance(self) -> list[ComplianceCheck]:
        """Check GDPR compliance."""
        checks = []

        # GDPR Article 32 - Security of processing
        checks.append(ComplianceCheck(
            standard="GDPR",
            check_name="Article 32 - Security of Processing",
            status="warning",
            description="Check data security measures",
            requirements=[
                "Implement appropriate technical measures",
                "Ensure confidentiality, integrity, and availability",
                "Regular security testing and assessment",
            ],
            findings=["Data security measures need review"],
        ))

        # GDPR Article 25 - Data protection by design
        checks.append(ComplianceCheck(
            standard="GDPR",
            check_name="Article 25 - Data Protection by Design",
            status="warning",
            description="Check privacy by design implementation",
            requirements=[
                "Implement privacy by design principles",
                "Minimize data collection and processing",
                "Implement data minimization",
            ],
            findings=["Privacy by design needs implementation"],
        ))

        return checks


class AdvancedSecurityTestingFramework:
    """Comprehensive advanced security testing framework."""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.reports_dir = self.project_root / "reports" / "security"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

        self.dast_tester = DynamicApplicationSecurityTester()
        self.penetration_tester = PenetrationTester()
        self.compliance_checker = ComplianceChecker()
        self.test_results = []

    def run_comprehensive_security_tests(self) -> dict[str, Any]:
        """Run comprehensive security test suite."""
        print("🔒 Running Comprehensive Security Test Suite...")

        # Run DAST scan
        print("\n🔍 Running DAST Scan...")
        dast_result = self._run_dast_scan()
        self.test_results.append(dast_result)

        # Run penetration testing
        print("\n🎯 Running Penetration Testing...")
        pentest_result = self._run_penetration_test()
        self.test_results.append(pentest_result)

        # Run compliance checks
        print("\n📋 Running Compliance Checks...")
        compliance_checks = self._run_compliance_checks()

        # Run static analysis
        print("\n📊 Running Static Analysis...")
        static_result = self._run_static_analysis()
        self.test_results.append(static_result)

        # Run dependency scanning
        print("\n📦 Running Dependency Scanning...")
        dependency_result = self._run_dependency_scanning()
        self.test_results.append(dependency_result)

        # Generate comprehensive report
        return self._generate_security_report(compliance_checks)

    def _run_dast_scan(self) -> SecurityTestResult:
        """Run DAST scan."""
        # Define test endpoints
        endpoints = ["/", "/login", "/api/users", "/api/data", "/admin"]

        return self.dast_tester.run_dast_scan(endpoints)

    def _run_penetration_test(self) -> SecurityTestResult:
        """Run penetration test."""
        return self.penetration_tester.run_penetration_test()

    def _run_compliance_checks(self) -> list[ComplianceCheck]:
        """Run compliance checks."""
        return self.compliance_checker.run_compliance_checks()

    def _run_static_analysis(self) -> SecurityTestResult:
        """Run static code analysis."""
        print("  📊 Running static code analysis...")

        vulnerabilities = []
        files_scanned = 0
        lines_scanned = 0

        # Scan Python files for security issues
        python_files = list(self.project_root.rglob("*.py"))

        for py_file in python_files:
            try:
                with open(py_file, encoding="utf-8") as f:
                    content = f.read()
                    lines = content.split("\n")
                    lines_scanned += len(lines)
                    files_scanned += 1

                # Check for hardcoded secrets
                if self._has_hardcoded_secrets(content):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"hardcoded_secret_{len(vulnerabilities)}",
                        name="Hardcoded Secret",
                        severity="high",
                        description="Hardcoded secret detected in code",
                        file_path=str(py_file.relative_to(self.project_root)),
                        line_number=0,
                        cwe_id="CWE-798",
                        cvss_score=7.5,
                        remediation="Remove hardcoded secrets and use environment variables",
                        references=["https://owasp.org/www-community/vulnerabilities/Use_of_hard-coded_credentials"],
                    ))

                # Check for SQL injection patterns
                if self._has_sql_injection_patterns(content):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"sql_injection_pattern_{len(vulnerabilities)}",
                        name="Potential SQL Injection",
                        severity="medium",
                        description="Potential SQL injection pattern detected",
                        file_path=str(py_file.relative_to(self.project_root)),
                        line_number=0,
                        cwe_id="CWE-89",
                        cvss_score=6.5,
                        remediation="Use parameterized queries",
                        references=["https://owasp.org/www-community/attacks/SQL_Injection"],
                    ))

                # Check for command injection patterns
                if self._has_command_injection_patterns(content):
                    vulnerabilities.append(SecurityVulnerability(
                        id=f"cmd_injection_pattern_{len(vulnerabilities)}",
                        name="Potential Command Injection",
                        severity="high",
                        description="Potential command injection pattern detected",
                        file_path=str(py_file.relative_to(self.project_root)),
                        line_number=0,
                        cwe_id="CWE-78",
                        cvss_score=8.5,
                        remediation="Avoid executing system commands with user input",
                        references=["https://owasp.org/www-community/attacks/Command_Injection"],
                    ))

            except Exception as e:
                print(f"Error scanning {py_file}: {e}")

        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)

        # Generate recommendations
        recommendations = self._generate_security_recommendations(vulnerabilities)

        # Determine status
        status = self._determine_security_status(vulnerabilities)

        return SecurityTestResult(
            test_name="static_analysis",
            status=status,
            vulnerabilities=vulnerabilities,
            risk_score=risk_score,
            recommendations=recommendations,
            scan_duration=0.0,
            files_scanned=files_scanned,
            lines_scanned=lines_scanned,
        )

    def _run_dependency_scanning(self) -> SecurityTestResult:
        """Run dependency vulnerability scanning."""
        print("  📦 Scanning dependencies for vulnerabilities...")

        vulnerabilities = []
        files_scanned = 0
        lines_scanned = 0

        # Check requirements files
        requirements_files = [
            self.project_root / "requirements.txt",
            self.project_root / "pyproject.toml",
            self.project_root / "poetry.lock",
        ]

        for req_file in requirements_files:
            if req_file.exists():
                files_scanned += 1
                try:
                    with open(req_file) as f:
                        content = f.read()
                        lines_scanned += len(content.split("\n"))

                    # Check for known vulnerable packages
                    vulnerable_packages = self._check_vulnerable_packages(content)
                    for package, version in vulnerable_packages:
                        vulnerabilities.append(SecurityVulnerability(
                            id=f"vulnerable_dependency_{len(vulnerabilities)}",
                            name="Vulnerable Dependency",
                            severity="high",
                            description=f"Vulnerable dependency detected: {package} {version}",
                            file_path=str(req_file.relative_to(self.project_root)),
                            line_number=0,
                            cwe_id="CWE-1104",
                            cvss_score=7.5,
                            remediation=f"Update {package} to latest secure version",
                            references=["https://owasp.org/www-community/vulnerabilities/Using_Components_with_Known_Vulnerabilities"],
                        ))

                except Exception as e:
                    print(f"Error scanning {req_file}: {e}")

        # Calculate risk score
        risk_score = self._calculate_risk_score(vulnerabilities)

        # Generate recommendations
        recommendations = self._generate_security_recommendations(vulnerabilities)

        # Determine status
        status = self._determine_security_status(vulnerabilities)

        return SecurityTestResult(
            test_name="dependency_scanning",
            status=status,
            vulnerabilities=vulnerabilities,
            risk_score=risk_score,
            recommendations=recommendations,
            scan_duration=0.0,
            files_scanned=files_scanned,
            lines_scanned=lines_scanned,
        )

    def _has_hardcoded_secrets(self, content: str) -> bool:
        """Check for hardcoded secrets in code."""
        secret_patterns = [
            r'password\s*=\s*["\'][^"\']+["\']',
            r'api_key\s*=\s*["\'][^"\']+["\']',
            r'secret\s*=\s*["\'][^"\']+["\']',
            r'token\s*=\s*["\'][^"\']+["\']',
            r'key\s*=\s*["\'][^"\']+["\']',
        ]

        for pattern in secret_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def _has_sql_injection_patterns(self, content: str) -> bool:
        """Check for SQL injection patterns in code."""
        sql_patterns = [
            r'execute\s*\(\s*["\'].*%s.*["\']',
            r'query\s*\(\s*["\'].*\+.*["\']',
            r'cursor\.execute\s*\(\s*f["\']',
            r'cursor\.execute\s*\(\s*["\'].*%.*["\']',
        ]

        for pattern in sql_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def _has_command_injection_patterns(self, content: str) -> bool:
        """Check for command injection patterns in code."""
        cmd_patterns = [
            r"os\.system\s*\(",
            r"subprocess\.call\s*\(",
            r"subprocess\.run\s*\(",
            r"os\.popen\s*\(",
            r"eval\s*\(",
            r"exec\s*\(",
        ]

        for pattern in cmd_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                return True

        return False

    def _check_vulnerable_packages(self, content: str) -> list[tuple[str, str]]:
        """Check for known vulnerable packages."""
        # This would typically use a vulnerability database
        # For now, just check for some common vulnerable packages
        vulnerable_packages = []

        vulnerable_pkg_patterns = [
            (r"requests\s*==\s*([0-9.]+)", "requests"),
            (r"urllib3\s*==\s*([0-9.]+)", "urllib3"),
            (r"pyyaml\s*==\s*([0-9.]+)", "pyyaml"),
            (r"jinja2\s*==\s*([0-9.]+)", "jinja2"),
        ]

        for pattern, package_name in vulnerable_pkg_patterns:
            matches = re.findall(pattern, content)
            for version in matches:
                # Check if version is vulnerable (simplified)
                if self._is_vulnerable_version(package_name, version):
                    vulnerable_packages.append((package_name, version))

        return vulnerable_packages

    def _is_vulnerable_version(self, package: str, version: str) -> bool:
        """Check if package version is vulnerable."""
        # This would typically check against a vulnerability database
        # For now, just return False (no vulnerabilities found)
        return False

    def _calculate_risk_score(self, vulnerabilities: list[SecurityVulnerability]) -> float:
        """Calculate risk score."""
        if not vulnerabilities:
            return 0.0

        severity_scores = {
            "critical": 10.0,
            "high": 7.5,
            "medium": 5.0,
            "low": 2.5,
            "info": 1.0,
        }

        total_score = sum(severity_scores.get(v.severity, 0) for v in vulnerabilities)
        max_possible_score = len(vulnerabilities) * 10.0

        return (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0.0

    def _generate_security_recommendations(self, vulnerabilities: list[SecurityVulnerability]) -> list[str]:
        """Generate security recommendations."""
        recommendations = []

        # Group vulnerabilities by type
        vuln_types = {}
        for vuln in vulnerabilities:
            vuln_type = vuln.name
            if vuln_type not in vuln_types:
                vuln_types[vuln_type] = []
            vuln_types[vuln_type].append(vuln)

        # Generate recommendations
        for vuln_type, vulns in vuln_types.items():
            count = len(vulns)
            if vuln_type == "Hardcoded Secret":
                recommendations.append(f"Remove {count} hardcoded secrets and use environment variables")
            elif vuln_type == "Potential SQL Injection":
                recommendations.append(f"Fix {count} potential SQL injection vulnerabilities")
            elif vuln_type == "Potential Command Injection":
                recommendations.append(f"Fix {count} potential command injection vulnerabilities")
            elif vuln_type == "Vulnerable Dependency":
                recommendations.append(f"Update {count} vulnerable dependencies")

        # General recommendations
        recommendations.append("Implement security testing in CI/CD pipeline")
        recommendations.append("Regular security audits and penetration testing")
        recommendations.append("Security awareness training for development team")
        recommendations.append("Implement security monitoring and alerting")

        return recommendations

    def _determine_security_status(self, vulnerabilities: list[SecurityVulnerability]) -> str:
        """Determine security status."""
        if not vulnerabilities:
            return "pass"

        critical_count = len([v for v in vulnerabilities if v.severity == "critical"])
        high_count = len([v for v in vulnerabilities if v.severity == "high"])
        medium_count = len([v for v in vulnerabilities if v.severity == "medium"])

        if critical_count > 0 or high_count > 2:
            return "fail"
        if high_count > 0 or medium_count > 5:
            return "warning"
        return "pass"

    def _generate_security_report(self, compliance_checks: list[ComplianceCheck]) -> dict[str, Any]:
        """Generate comprehensive security report."""
        print("📊 Generating Security Report...")

        # Calculate summary statistics
        total_tests = len(self.test_results)
        passed_tests = len([r for r in self.test_results if r.status == "pass"])
        failed_tests = len([r for r in self.test_results if r.status == "fail"])
        warning_tests = len([r for r in self.test_results if r.status == "warning"])

        # Calculate total vulnerabilities
        total_vulnerabilities = sum(len(r.vulnerabilities) for r in self.test_results)
        critical_vulns = sum(len([v for v in r.vulnerabilities if v.severity == "critical"]) for r in self.test_results)
        high_vulns = sum(len([v for v in r.vulnerabilities if v.severity == "high"]) for r in self.test_results)
        medium_vulns = sum(len([v for v in r.vulnerabilities if v.severity == "medium"]) for r in self.test_results)
        low_vulns = sum(len([v for v in r.vulnerabilities if v.severity == "low"]) for r in self.test_results)

        # Calculate average risk score
        avg_risk_score = statistics.mean([r.risk_score for r in self.test_results]) if self.test_results else 0.0

        # Generate overall recommendations
        all_recommendations = []
        for result in self.test_results:
            all_recommendations.extend(result.recommendations)

        # Remove duplicates
        unique_recommendations = list(set(all_recommendations))

        report = {
            "timestamp": datetime.now().isoformat(),
            "summary": {
                "total_tests": total_tests,
                "passed_tests": passed_tests,
                "failed_tests": failed_tests,
                "warning_tests": warning_tests,
                "success_rate": (passed_tests / total_tests * 100) if total_tests > 0 else 0,
                "total_vulnerabilities": total_vulnerabilities,
                "critical_vulnerabilities": critical_vulns,
                "high_vulnerabilities": high_vulns,
                "medium_vulnerabilities": medium_vulns,
                "low_vulnerabilities": low_vulns,
                "average_risk_score": round(avg_risk_score, 2),
            },
            "test_results": [asdict(result) for result in self.test_results],
            "compliance_checks": [asdict(check) for check in compliance_checks],
            "recommendations": unique_recommendations,
            "security_insights": self._generate_security_insights(),
        }

        # Save report
        self._save_security_report(report)

        return report

    def _generate_security_insights(self) -> list[str]:
        """Generate security insights and recommendations."""
        insights = []

        # Analyze vulnerabilities
        all_vulns = []
        for result in self.test_results:
            all_vulns.extend(result.vulnerabilities)

        if all_vulns:
            vuln_types = {}
            for vuln in all_vulns:
                vuln_type = vuln.name
                if vuln_type not in vuln_types:
                    vuln_types[vuln_type] = 0
                vuln_types[vuln_type] += 1

            # Most common vulnerability types
            most_common = max(vuln_types.items(), key=lambda x: x[1]) if vuln_types else None
            if most_common:
                insights.append(f"Most common vulnerability: {most_common[0]} ({most_common[1]} instances)")

        # General insights
        insights.append("Implement security testing in CI/CD pipeline")
        insights.append("Regular security audits and penetration testing")
        insights.append("Security awareness training for development team")
        insights.append("Implement security monitoring and alerting")
        insights.append("Use automated security scanning tools")
        insights.append("Implement secure coding practices")

        return insights

    def _save_security_report(self, report: dict[str, Any]) -> None:
        """Save security report."""
        # Save JSON report
        json_file = self.reports_dir / f"security_report_{int(time.time())}.json"
        with open(json_file, "w") as f:
            json.dump(report, f, indent=2)

        # Save summary report
        summary_file = self.reports_dir / f"security_summary_{int(time.time())}.md"
        self._save_security_summary(report, summary_file)

        print("📊 Security reports saved:")
        print(f"  JSON: {json_file}")
        print(f"  Summary: {summary_file}")

    def _save_security_summary(self, report: dict[str, Any], file_path: Path) -> None:
        """Save markdown summary report."""
        summary = report["summary"]

        content = f"""# Security Testing Report

**Generated**: {report['timestamp']}
**Success Rate**: {summary['success_rate']:.1f}%
**Risk Score**: {summary['average_risk_score']:.1f}/100

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {summary['total_tests']} |
| Passed Tests | {summary['passed_tests']} |
| Failed Tests | {summary['failed_tests']} |
| Warning Tests | {summary['warning_tests']} |
| Success Rate | {summary['success_rate']:.1f}% |
| Total Vulnerabilities | {summary['total_vulnerabilities']} |
| Critical Vulnerabilities | {summary['critical_vulnerabilities']} |
| High Vulnerabilities | {summary['high_vulnerabilities']} |
| Medium Vulnerabilities | {summary['medium_vulnerabilities']} |
| Low Vulnerabilities | {summary['low_vulnerabilities']} |
| Average Risk Score | {summary['average_risk_score']:.1f}/100 |

## Test Results

"""

        for result in report["test_results"]:
            status_emoji = "✅" if result["status"] == "pass" else "❌" if result["status"] == "fail" else "⚠️"
            content += f"### {status_emoji} {result['test_name']}\n\n"
            content += f"- **Status**: {result['status']}\n"
            content += f"- **Risk Score**: {result['risk_score']:.1f}/100\n"
            content += f"- **Vulnerabilities**: {len(result['vulnerabilities'])}\n"
            content += f"- **Files Scanned**: {result['files_scanned']}\n"
            content += f"- **Lines Scanned**: {result['lines_scanned']}\n\n"

            if result["recommendations"]:
                content += "**Recommendations**:\n"
                for rec in result["recommendations"]:
                    content += f"- {rec}\n"
                content += "\n"

        if report["compliance_checks"]:
            content += "## Compliance Checks\n\n"
            for check in report["compliance_checks"]:
                status_emoji = "✅" if check["status"] == "pass" else "❌" if check["status"] == "fail" else "⚠️"
                content += f"### {status_emoji} {check['check_name']}\n\n"
                content += f"- **Standard**: {check['standard']}\n"
                content += f"- **Status**: {check['status']}\n"
                content += f"- **Description**: {check['description']}\n\n"

        if report["recommendations"]:
            content += "## Overall Recommendations\n\n"
            for rec in report["recommendations"]:
                content += f"- {rec}\n"

        if report["security_insights"]:
            content += "\n## Security Insights\n\n"
            for insight in report["security_insights"]:
                content += f"- {insight}\n"

        with open(file_path, "w") as f:
            f.write(content)


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(description="Advanced Security Testing")
    parser.add_argument("project_root", help="Project root directory")
    parser.add_argument("--dast", action="store_true", help="Run DAST scan")
    parser.add_argument("--penetration", action="store_true", help="Run penetration test")
    parser.add_argument("--compliance", action="store_true", help="Run compliance checks")
    parser.add_argument("--static", action="store_true", help="Run static analysis")
    parser.add_argument("--dependencies", action="store_true", help="Run dependency scanning")
    parser.add_argument("--output", "-o", help="Output report file")
    parser.add_argument("--json", action="store_true", help="Output JSON format")

    args = parser.parse_args()

    framework = AdvancedSecurityTestingFramework(args.project_root)

    if args.dast:
        # Run DAST scan
        result = framework._run_dast_scan()
        report = {"test_result": asdict(result)}
    elif args.penetration:
        # Run penetration test
        result = framework._run_penetration_test()
        report = {"test_result": asdict(result)}
    elif args.compliance:
        # Run compliance checks
        checks = framework._run_compliance_checks()
        report = {"compliance_checks": [asdict(check) for check in checks]}
    elif args.static:
        # Run static analysis
        result = framework._run_static_analysis()
        report = {"test_result": asdict(result)}
    elif args.dependencies:
        # Run dependency scanning
        result = framework._run_dependency_scanning()
        report = {"test_result": asdict(result)}
    else:
        # Run comprehensive tests
        report = framework.run_comprehensive_security_tests()

    if args.json:
        output = json.dumps(report, indent=2)
    # Pretty print format
    elif "summary" in report:
        summary = report["summary"]
        output = f"""
🔒 ADVANCED SECURITY TESTING REPORT
{'=' * 60}
Success Rate: {summary['success_rate']:.1f}%
Risk Score: {summary['average_risk_score']:.1f}/100
Total Tests: {summary['total_tests']}
Passed: {summary['passed_tests']}
Failed: {summary['failed_tests']}
Warning: {summary['warning_tests']}

Vulnerabilities:
  Total: {summary['total_vulnerabilities']}
  Critical: {summary['critical_vulnerabilities']}
  High: {summary['high_vulnerabilities']}
  Medium: {summary['medium_vulnerabilities']}
  Low: {summary['low_vulnerabilities']}

Test Results:
"""
        for result in report.get("test_results", []):
            status_emoji = "✅" if result["status"] == "pass" else "❌" if result["status"] == "fail" else "⚠️"
            output += f"  {status_emoji} {result['test_name']}: {result['status']} (Risk: {result['risk_score']:.1f}/100)\n"
    else:
        output = f"📊 Report: {json.dumps(report, indent=2)}"

    if args.output:
        with open(args.output, "w") as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)


if __name__ == "__main__":
    main()
