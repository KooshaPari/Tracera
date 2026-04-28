#!/usr/bin/env python3
"""Test SST adapter structure."""

import os
import sys

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))


def test_sst_imports():
    """Test SST imports."""
    try:
        from pheno.adapters.sst import (
            SSTAdapter,
            SSTConfig,
            SSTCredentialProvider,
            SSTResource,
        )

        print("✓ SST imports successful")

        # Test basic functionality
        config = SSTConfig()
        print(f"✓ SSTConfig created: {config}")

        provider = SSTCredentialProvider(config)
        print(f"✓ SSTCredentialProvider created: {provider}")

        from pheno.adapters.sst.adapter import DefaultSSTAdapter

        adapter = DefaultSSTAdapter(config, provider)
        print(f"✓ DefaultSSTAdapter created: {adapter}")

        return True
    except Exception as e:
        print(f"✗ SST imports failed: {e}")
        import traceback

        traceback.print_exc()
        return False


def test_adapter_imports():
    """Test main adapter imports."""
    try:
        from pheno.adapters import (
            SSTAdapter,
            SSTConfig,
            SSTCredentialProvider,
            SSTResource,
        )

        print("✓ Main adapter imports successful")
        return True
    except Exception as e:
        print(f"✗ Main adapter imports failed: {e}")
        import traceback

        traceback.print_exc()
        return False


if __name__ == "__main__":
    print("Testing SST adapter structure...")

    success1 = test_sst_imports()
    success2 = test_adapter_imports()

    if success1 and success2:
        print("\n✓ All tests passed!")
        sys.exit(0)
    else:
        print("\n✗ Some tests failed!")
        sys.exit(1)
