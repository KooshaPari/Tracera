#!/usr/bin/env python3
"""
Test script for CI/CD generation and synchronization system.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))


def test_cicd_system():
    """
    Test the CI/CD system.
    """
    try:
        from pheno.cicd.core import CICDConfig, ProjectType
        from pheno.cicd.generator import CICDGeneratorFactory
        from pheno.cicd.manager import CICDManager

        print("🔍 Testing CI/CD system...")

        # Test configuration creation
        config = CICDConfig(
            project_name="test-project",
            project_type=ProjectType.PHENO_SDK,
            python_versions=["3.11", "3.12"],
            os_versions=["ubuntu-latest"],
        )

        print(f"✅ Created configuration for {config.project_name}")

        # Test generator creation
        generator = CICDGeneratorFactory.create_generator_from_config(config)
        print(f"✅ Created generator for {config.project_type.value}")

        # Test manager creation
        manager = CICDManager()
        print("✅ Created CI/CD manager")

        # Test project registry
        projects = list(manager.project_registry.keys())
        print(f"✅ Found {len(projects)} projects in registry: {', '.join(projects)}")

        # Test status check
        status = manager.status_all()
        print(f"✅ Status check completed for {len(status)} projects")

        print("\\n🎉 CI/CD system test completed successfully!")
        return True

    except Exception as e:
        print(f"❌ Error testing CI/CD system: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    success = test_cicd_system()
    sys.exit(0 if success else 1)
