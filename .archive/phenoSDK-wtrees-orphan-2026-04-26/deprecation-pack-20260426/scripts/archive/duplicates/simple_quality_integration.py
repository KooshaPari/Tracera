#!/usr/bin/env python3
"""
Simple quality framework integration test.
"""

import shutil
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def integrate_quality_framework():
    """
    Simple integration of quality framework.
    """
    try:
        # Create quality directory
        quality_dir = Path("quality")
        quality_dir.mkdir(exist_ok=True)

        # Copy framework files
        framework_dir = src_path / "pheno" / "quality"

        # Copy core files
        core_files = [
            "core.py",
            "plugins.py",
            "exporters.py",
            "importers.py",
            "registry.py",
            "utils.py",
            "manager.py",
            "config.py",
        ]

        for file_name in core_files:
            src_file = framework_dir / file_name
            if src_file.exists():
                dst_file = quality_dir / file_name
                shutil.copy2(src_file, dst_file)

        # Copy tools directory
        tools_src = framework_dir / "tools"
        tools_dst = quality_dir / "tools"
        if tools_src.exists():
            shutil.copytree(tools_src, tools_dst, dirs_exist_ok=True)

        # Create simple analyze script
        analyze_script = quality_dir / "analyze.py"
        analyze_script.write_text(
            '''#!/usr/bin/env python3
"""
Simple quality analysis script
"""

import sys
from pathlib import Path

# Add quality framework to path
sys.path.insert(0, str(Path(__file__).parent))

from manager import quality_manager

def main():
    print("🔍 Running quality analysis...")

    # Run analysis
    report = quality_manager.analyze_project(
        project_path='.',
        enabled_tools=['pattern_detector', 'code_smell_detector'],
        output_path='reports/quality_report.json'
    )

    # Generate summary
    summary = quality_manager.generate_summary(report)

    print(f"\\n📊 Quality Analysis Results")
    print(f"Quality Score: {summary['quality_score']:.1f}/100")
    print(f"Total Issues: {summary['total_issues']}")
    print(f"Files Affected: {summary['files_affected']}")

    if summary['recommendations']:
        print("\\n🔧 Recommendations:")
        for rec in summary['recommendations']:
            print(f"  {rec}")

    return 0 if summary['quality_score'] >= 70 else 1

if __name__ == "__main__":
    sys.exit(main())
''',
        )
        analyze_script.chmod(0o755)

        print("✅ Quality framework integrated successfully!")
        print(f"📁 Framework files added to {quality_dir}/")
        print("🚀 You can now run: python quality/analyze.py")

        return True

    except Exception as e:
        print(f"❌ Error integrating quality framework: {e}")
        return False


if __name__ == "__main__":
    success = integrate_quality_framework()
    sys.exit(0 if success else 1)
