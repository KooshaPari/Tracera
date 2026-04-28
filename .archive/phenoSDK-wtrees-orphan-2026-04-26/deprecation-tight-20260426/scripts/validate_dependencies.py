#!/usr/bin/env python3
"""Dependency Validation Script for Pheno-SDK.

Automated dependency license and security validation.
"""

import argparse
import json
import subprocess
from typing import Any


def run_dependency_validation() -> dict[str, Any]:
    """
    Run comprehensive dependency validation.
    """
    try:
        # Run safety check for security vulnerabilities
        safety_result = subprocess.run(
            ["safety", "check", "--json"], check=False, capture_output=True, text=True,
        )

        # Run pip-audit for security audit
        pip_audit_result = subprocess.run(
            ["pip-audit", "--format=json"], check=False, capture_output=True, text=True,
        )

        # Run pip-licenses for license analysis
        licenses_result = subprocess.run(
            ["pip-licenses", "--format=json"], check=False, capture_output=True, text=True,
        )

        # Parse results
        safety_data = []
        if safety_result.returncode == 0 and safety_result.stdout:
            try:
                safety_data = json.loads(safety_result.stdout)
            except json.JSONDecodeError:
                safety_data = []

        pip_audit_data = []
        if pip_audit_result.returncode == 0 and pip_audit_result.stdout:
            try:
                pip_audit_data = json.loads(pip_audit_result.stdout)
            except json.JSONDecodeError:
                pip_audit_data = []

        licenses_data = []
        if licenses_result.returncode == 0 and licenses_result.stdout:
            try:
                licenses_data = json.loads(licenses_result.stdout)
            except json.JSONDecodeError:
                licenses_data = []

        # Analyze validation results
        validation_stats = analyze_validation_results(safety_data, pip_audit_data, licenses_data)

        return {
            "returncode": 0,
            "safety_data": safety_data,
            "pip_audit_data": pip_audit_data,
            "licenses_data": licenses_data,
            "validation_stats": validation_stats,
            "recommendations": generate_validation_recommendations(validation_stats),
        }
    except Exception as e:
        return {"error": str(e), "returncode": 1}


def analyze_validation_results(
    safety_data: list[dict], pip_audit_data: list[dict], licenses_data: list[dict],
) -> dict[str, Any]:
    """
    Analyze dependency validation results.
    """
    security_vulnerabilities = []
    license_issues = []
    compliance_issues = []

    # Analyze safety results
    for item in safety_data:
        if item.get("vulnerabilities"):
            for vuln in item["vulnerabilities"]:
                security_vulnerabilities.append(
                    {
                        "package": item.get("package_name", ""),
                        "version": item.get("installed_version", ""),
                        "vulnerability": vuln.get("vulnerability_id", ""),
                        "severity": vuln.get("severity", "unknown"),
                        "description": vuln.get("description", ""),
                    },
                )

    # Analyze pip-audit results
    for item in pip_audit_data:
        if item.get("vulnerabilities"):
            for vuln in item["vulnerabilities"]:
                security_vulnerabilities.append(
                    {
                        "package": item.get("package", ""),
                        "version": item.get("installed_version", ""),
                        "vulnerability": vuln.get("id", ""),
                        "severity": vuln.get("severity", "unknown"),
                        "description": vuln.get("description", ""),
                    },
                )

    # Analyze license data
    allowed_licenses = [
        "MIT",
        "Apache-2.0",
        "BSD-3-Clause",
        "BSD-2-Clause",
        "ISC",
        "Python-2.0",
        "PSF",
        "Public Domain",
        "Unlicense",
    ]

    for item in licenses_data:
        license_name = item.get("License", "")
        if license_name and license_name not in allowed_licenses:
            license_issues.append(
                {
                    "package": item.get("Name", ""),
                    "version": item.get("Version", ""),
                    "license": license_name,
                    "status": "restricted",
                },
            )

    # Check for GPL licenses (often problematic)
    gpl_licenses = ["GPL", "GPL-2.0", "GPL-3.0", "AGPL", "AGPL-3.0"]
    for item in licenses_data:
        license_name = item.get("License", "")
        if any(gpl in license_name for gpl in gpl_licenses):
            license_issues.append(
                {
                    "package": item.get("Name", ""),
                    "version": item.get("Version", ""),
                    "license": license_name,
                    "status": "gpl",
                },
            )

    return {
        "total_packages": len(licenses_data),
        "security_vulnerabilities": security_vulnerabilities,
        "license_issues": license_issues,
        "compliance_issues": compliance_issues,
        "security_score": calculate_security_score(security_vulnerabilities),
        "license_score": calculate_license_score(license_issues, len(licenses_data)),
    }


def calculate_security_score(vulnerabilities: list[dict]) -> dict[str, Any]:
    """
    Calculate security score based on vulnerabilities.
    """
    if not vulnerabilities:
        return {"score": 100, "grade": "A", "status": "secure"}

    critical_count = len(
        [v for v in vulnerabilities if v.get("severity", "").lower() == "critical"],
    )
    high_count = len([v for v in vulnerabilities if v.get("severity", "").lower() == "high"])
    medium_count = len([v for v in vulnerabilities if v.get("severity", "").lower() == "medium"])
    low_count = len([v for v in vulnerabilities if v.get("severity", "").lower() == "low"])

    # Calculate score (deduct points for vulnerabilities)
    score = 100
    score -= critical_count * 25
    score -= high_count * 15
    score -= medium_count * 10
    score -= low_count * 5

    score = max(score, 0)

    # Determine grade
    if score >= 90:
        grade = "A"
        status = "secure"
    elif score >= 80:
        grade = "B"
        status = "mostly_secure"
    elif score >= 70:
        grade = "C"
        status = "moderate_risk"
    elif score >= 60:
        grade = "D"
        status = "high_risk"
    else:
        grade = "F"
        status = "critical_risk"

    return {
        "score": score,
        "grade": grade,
        "status": status,
        "critical_vulnerabilities": critical_count,
        "high_vulnerabilities": high_count,
        "medium_vulnerabilities": medium_count,
        "low_vulnerabilities": low_count,
    }


def calculate_license_score(license_issues: list[dict], total_packages: int) -> dict[str, Any]:
    """
    Calculate license compliance score.
    """
    if total_packages == 0:
        return {"score": 100, "grade": "A", "status": "compliant"}

    restricted_count = len([l for l in license_issues if l.get("status") == "restricted"])
    gpl_count = len([l for l in license_issues if l.get("status") == "gpl"])

    # Calculate score
    score = 100
    score -= restricted_count * 10
    score -= gpl_count * 20

    score = max(score, 0)

    # Determine grade
    if score >= 90:
        grade = "A"
        status = "compliant"
    elif score >= 80:
        grade = "B"
        status = "mostly_compliant"
    elif score >= 70:
        grade = "C"
        status = "moderate_risk"
    elif score >= 60:
        grade = "D"
        status = "high_risk"
    else:
        grade = "F"
        status = "non_compliant"

    return {
        "score": score,
        "grade": grade,
        "status": status,
        "restricted_licenses": restricted_count,
        "gpl_licenses": gpl_count,
        "total_issues": len(license_issues),
    }


def generate_validation_recommendations(stats: dict) -> list[str]:
    """
    Generate dependency validation recommendations.
    """
    recommendations = []

    security_vulns = stats.get("security_vulnerabilities", [])
    license_issues = stats.get("license_issues", [])
    security_score = stats.get("security_score", {})
    license_score = stats.get("license_score", {})

    # Security recommendations
    if security_vulns:
        recommendations.append(f"Address {len(security_vulns)} security vulnerabilities")

        critical_vulns = [v for v in security_vulns if v.get("severity", "").lower() == "critical"]
        if critical_vulns:
            recommendations.append(
                f"  - {len(critical_vulns)} critical vulnerabilities require immediate attention",
            )

        high_vulns = [v for v in security_vulns if v.get("severity", "").lower() == "high"]
        if high_vulns:
            recommendations.append(
                f"  - {len(high_vulns)} high-severity vulnerabilities should be addressed soon",
            )

    # License recommendations
    if license_issues:
        recommendations.append(f"Review {len(license_issues)} license compliance issues")

        gpl_licenses = [l for l in license_issues if l.get("status") == "gpl"]
        if gpl_licenses:
            recommendations.append(
                f"  - {len(gpl_licenses)} GPL-licensed packages may require special handling",
            )

        restricted_licenses = [l for l in license_issues if l.get("status") == "restricted"]
        if restricted_licenses:
            recommendations.append(
                f"  - {len(restricted_licenses)} packages have restricted licenses",
            )

    # SDK-specific recommendations
    recommendations.extend(
        [
            "Regularly update dependencies to latest secure versions",
            "Use dependency pinning for production deployments",
            "Monitor security advisories for all dependencies",
            "Consider using dependency scanning in CI/CD pipeline",
            "Review license compatibility before adding new dependencies",
            "Use tools like safety and pip-audit for ongoing monitoring",
            "Minimize external dependencies for SDK stability",
            "Use semantic versioning for internal dependencies",
            "Consider vendoring critical dependencies",
            "Document license requirements for SDK users",
        ],
    )

    return recommendations


def generate_validation_report() -> str:
    """
    Generate a comprehensive dependency validation report.
    """
    analysis = run_dependency_validation()

    report = []
    report.append("Pheno-SDK Dependency Validation Report")
    report.append("=" * 45)

    if "error" in analysis:
        report.append(f"Error: {analysis['error']}")
        return "\n".join(report)

    stats = analysis.get("validation_stats", {})
    recommendations = analysis.get("recommendations", [])

    report.append(f"Total Packages: {stats.get('total_packages', 0)}")

    # Security section
    security_score = stats.get("security_score", {})
    report.append("\nSecurity Status:")
    report.append(
        f"  Score: {security_score.get('score', 0)}/100 ({security_score.get('grade', 'N/A')})",
    )
    report.append(f"  Status: {security_score.get('status', 'unknown')}")
    report.append(
        f"  Critical Vulnerabilities: {security_score.get('critical_vulnerabilities', 0)}",
    )
    report.append(f"  High Vulnerabilities: {security_score.get('high_vulnerabilities', 0)}")

    # License section
    license_score = stats.get("license_score", {})
    report.append("\nLicense Compliance:")
    report.append(
        f"  Score: {license_score.get('score', 0)}/100 ({license_score.get('grade', 'N/A')})",
    )
    report.append(f"  Status: {license_score.get('status', 'unknown')}")
    report.append(f"  Restricted Licenses: {license_score.get('restricted_licenses', 0)}")
    report.append(f"  GPL Licenses: {license_score.get('gpl_licenses', 0)}")

    # Security vulnerabilities
    security_vulns = stats.get("security_vulnerabilities", [])
    if security_vulns:
        report.append(f"\nSecurity Vulnerabilities: {len(security_vulns)}")
        for vuln in security_vulns[:5]:  # Show top 5
            report.append(
                f"  {vuln['package']} {vuln['version']}: {vuln['vulnerability']} ({vuln['severity']})",
            )

    # License issues
    license_issues = stats.get("license_issues", [])
    if license_issues:
        report.append(f"\nLicense Issues: {len(license_issues)}")
        for issue in license_issues[:5]:  # Show top 5
            report.append(
                f"  {issue['package']} {issue['version']}: {issue['license']} ({issue['status']})",
            )

    if recommendations:
        report.append("\nRecommendations:")
        for i, rec in enumerate(recommendations, 1):
            report.append(f"  {i}. {rec}")

    return "\n".join(report)


def main():
    """
    Main dependency validation function.
    """
    parser = argparse.ArgumentParser(description="Validate dependencies")
    parser.add_argument("--json", action="store_true", help="Output JSON format")
    parser.add_argument("--report", action="store_true", help="Generate detailed report")

    args = parser.parse_args()

    if args.report:
        report = generate_validation_report()
        print(report)
        return 0

    analysis = run_dependency_validation()

    if args.json:
        print(json.dumps(analysis, indent=2))
    else:
        print("Dependency Validation Results:")
        stats = analysis.get("validation_stats", {})
        security_score = stats.get("security_score", {})
        license_score = stats.get("license_score", {})
        print(
            f"  Security Score: {security_score.get('score', 0)}/100 ({security_score.get('grade', 'N/A')})",
        )
        print(
            f"  License Score: {license_score.get('score', 0)}/100 ({license_score.get('grade', 'N/A')})",
        )
        print(f"  Vulnerabilities: {len(stats.get('security_vulnerabilities', []))}")
        print(f"  License Issues: {len(stats.get('license_issues', []))}")

    return analysis.get("returncode", 1)


if __name__ == "__main__":
    raise SystemExit(main())
