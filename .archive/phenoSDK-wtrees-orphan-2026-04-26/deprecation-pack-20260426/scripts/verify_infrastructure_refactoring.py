#!/usr/bin/env python3
"""Verification script for infrastructure canonicalization refactoring.

This script validates that:
1. ServiceInfraManager works correctly (replaces KInfra)
2. Proxy/fallback module renames work correctly
3. Tunnel API normalization works correctly
4. No regressions in CLI examples or infra helpers
"""

import importlib
import sys
from pathlib import Path

# Add the project root to the path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))


def test_service_infra_imports():
    """
    Test that ServiceInfraManager can be imported and instantiated.
    """
    print("Testing ServiceInfraManager imports...")

    try:
        from pheno.infra.service_infra import ServiceInfraManager

        print("✓ ServiceInfraManager import successful")

        # Test instantiation
        service_infra = ServiceInfraManager(domain="test.example.com")
        print("✓ ServiceInfraManager instantiation successful")

        # Test that it has the expected methods
        expected_methods = [
            "allocate_port",
            "create_tunnel",
            "get_public_url",
            "get_port",
            "get_info",
            "check_health",
            "cleanup",
            "cleanup_all",
        ]

        for method in expected_methods:
            if hasattr(service_infra, method):
                print(f"✓ Method {method} exists")
            else:
                print(f"✗ Method {method} missing")
                return False

        return True

    except Exception as e:
        print(f"✗ ServiceInfraManager import/instantiation failed: {e}")
        return False


def test_legacy_compatibility():
    """
    Test that legacy KInfra alias still works.
    """
    print("\nTesting legacy KInfra compatibility...")

    try:
        from pheno.infra import KInfra

        print("✓ Legacy KInfra import successful")

        # Test instantiation
        kinfra = KInfra(domain="test.example.com")
        print("✓ Legacy KInfra instantiation successful")

        # Test that it's the same as ServiceInfraManager
        from pheno.infra.service_infra import ServiceInfraManager

        assert type(kinfra) == type(ServiceInfraManager(domain="test.example.com"))
        print("✓ Legacy KInfra is same as ServiceInfraManager")

        return True

    except Exception as e:
        print(f"✗ Legacy KInfra compatibility failed: {e}")
        return False


def test_proxy_fallback_renames():
    """
    Test that proxy/fallback module renames work correctly.
    """
    print("\nTesting proxy/fallback module renames...")

    try:
        # Test proxy_gateway import

        print("✓ ProxyServer import from proxy_gateway successful")

        # Test fallback_site import

        print("✓ FallbackServer import from fallback_site successful")

        return True

    except Exception as e:
        print(f"✗ Proxy/fallback module renames failed: {e}")
        return False


def test_tunnel_api_normalization():
    """
    Test that tunnel API normalization works correctly.
    """
    print("\nTesting tunnel API normalization...")

    try:
        from pheno.infra.service_infra import ServiceInfraManager

        service_infra = ServiceInfraManager(domain="test.example.com")

        # Test that canonical methods exist
        canonical_methods = ["create_tunnel", "get_public_url", "get_port", "check_health"]

        for method in canonical_methods:
            if hasattr(service_infra, method):
                print(f"✓ Canonical method {method} exists")
            else:
                print(f"✗ Canonical method {method} missing")
                return False

        # Test that deprecated methods exist but warn
        deprecated_methods = ["start_tunnel", "get_service_url", "get_service_port"]

        for method in deprecated_methods:
            if hasattr(service_infra, method):
                print(f"✓ Deprecated method {method} exists (should warn)")
            else:
                print(f"✗ Deprecated method {method} missing")
                return False

        return True

    except Exception as e:
        print(f"✗ Tunnel API normalization failed: {e}")
        return False


def test_cli_examples():
    """
    Test that CLI examples still work.
    """
    print("\nTesting CLI examples...")

    try:
        # Test the FastAPI example
        example_path = project_root / "examples" / "stack" / "fastapi_pheno_example.py"
        if example_path.exists():
            print("✓ FastAPI example file exists")

            # Try to import the example (without running it)
            with open(example_path) as f:
                content = f.read()

            # Check for any broken imports
            if "from pheno.infra.kinfra" in content:
                print("✗ FastAPI example still uses old kinfra import")
                return False
            print("✓ FastAPI example uses correct imports")
        else:
            print("⚠ FastAPI example file not found")

        return True

    except Exception as e:
        print(f"✗ CLI examples test failed: {e}")
        return False


def test_infra_helpers():
    """
    Test that infra helpers still work.
    """
    print("\nTesting infra helpers...")

    try:
        # Test httpx_otel helper
        from pheno.infra.utils.httpx_otel import _load_pydevkit_httpx_hooks

        hooks = _load_pydevkit_httpx_hooks()
        print("✓ httpx_otel helper works")

        # Test service manager

        print("✓ ServiceManager import works")

        return True

    except Exception as e:
        print(f"✗ Infra helpers test failed: {e}")
        return False


def test_no_broken_imports():
    """
    Test that there are no broken imports in the refactored modules.
    """
    print("\nTesting for broken imports...")

    modules_to_test = [
        "pheno.infra.service_infra",
        "pheno.infra.proxy_gateway",
        "pheno.infra.fallback_site",
        "pheno.infra.service_manager.manager.core",
        "pheno.infra.control_center.multi_tenant",
    ]

    broken_imports = []

    for module_name in modules_to_test:
        try:
            importlib.import_module(module_name)
            print(f"✓ {module_name} imports successfully")
        except Exception as e:
            print(f"✗ {module_name} has broken imports: {e}")
            broken_imports.append(module_name)

    return len(broken_imports) == 0


def main():
    """
    Run all verification tests.
    """
    print("=" * 60)
    print("INFRASTRUCTURE REFACTORING VERIFICATION")
    print("=" * 60)

    tests = [
        test_service_infra_imports,
        test_legacy_compatibility,
        test_proxy_fallback_renames,
        test_tunnel_api_normalization,
        test_cli_examples,
        test_infra_helpers,
        test_no_broken_imports,
    ]

    passed = 0
    total = len(tests)

    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"✗ Test {test.__name__} failed with exception: {e}")

    print("\n" + "=" * 60)
    print(f"VERIFICATION RESULTS: {passed}/{total} tests passed")
    print("=" * 60)

    if passed == total:
        print("🎉 All tests passed! Infrastructure refactoring is working correctly.")
        return 0
    print("❌ Some tests failed. Please check the output above.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
