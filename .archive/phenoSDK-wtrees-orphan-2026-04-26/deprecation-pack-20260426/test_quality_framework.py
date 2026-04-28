#!/usr/bin/env python3
"""
Test script for quality framework.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_quality_framework():
    """
    Test the quality framework directly.
    """
    try:
        from pheno.quality.config import get_config
        from pheno.quality.manager import quality_manager

        print("🔍 Testing quality framework...")

        # Get configuration
        config = get_config("pheno-sdk")
        print(f"✅ Configuration loaded: {config.enabled_tools}")

        # Create manager
        manager = quality_manager
        manager.config = config

        # Test with a small sample
        print("🔍 Running quality analysis on src/...")

        report = manager.analyze_project(
            project_path="src",
            enabled_tools=["pattern_detector", "code_smell_detector"],
            output_path="reports/test_quality_report.json",
        )

        # Generate summary
        summary = manager.generate_summary(report)

        print("\\n📊 Quality Analysis Results")
        print(f"Quality Score: {summary['quality_score']:.1f}/100")
        print(f"Total Issues: {summary['total_issues']}")
        print(f"Files Affected: {summary['files_affected']}")
        print(f"Analysis Duration: {summary['analysis_duration']:.2f}s")

        if summary["recommendations"]:
            print("\\n🔧 Recommendations:")
            for rec in summary["recommendations"]:
                print(f"  {rec}")

        print("\\n✅ Quality framework test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error testing quality framework: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_quality_framework()
    sys.exit(0 if success else 1)
