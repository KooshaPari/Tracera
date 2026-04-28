#!/usr/bin/env python3
"""
Test script for quality framework integration.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from pheno.quality.integration import integrate_quality_framework


def main():
    print("🔧 Testing quality framework integration...")

    # Test integration
    success = integrate_quality_framework(".", "pheno-sdk")

    if success:
        print("✅ Quality framework integrated successfully!")
        print("📁 Framework files added to ./quality/")
        print("🚀 You can now run: python quality/analyze.py .")
    else:
        print("❌ Failed to integrate quality framework")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
