#!/usr/bin/env python3
"""
Simple quality analysis script.
"""

import sys
from pathlib import Path

# Add quality framework to path
sys.path.insert(0, str(Path(__file__).parent))

from quality.manager import quality_manager


def main():
    print("🔍 Running quality analysis...")

    # Run analysis
    report = quality_manager.analyze_project(
        project_path=".",
        enabled_tools=["pattern_detector", "code_smell_detector"],
        output_path="reports/quality_report.json",
    )

    # Generate summary
    summary = quality_manager.generate_summary(report)

    print("\n📊 Quality Analysis Results")
    print(f"Quality Score: {summary['quality_score']:.1f}/100")
    print(f"Total Issues: {summary['total_issues']}")
    print(f"Files Affected: {summary['files_affected']}")

    if summary["recommendations"]:
        print("\n🔧 Recommendations:")
        for rec in summary["recommendations"]:
            print(f"  {rec}")

    return 0 if summary["quality_score"] >= 70 else 1


if __name__ == "__main__":
    sys.exit(main())
