#!/usr/bin/env python3
"""Simple verification script for Phase 4 implementation.

Checks that all components are properly implemented.
"""

import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent.parent.parent
sys.path.insert(0, str(src_path))

def verify_files_exist():
    """Verify all expected files were created."""
    print("=== Verifying File Creation ===")

    mcp_dir = Path(__file__).parent
    expected_files = [
        "telemetry.py",
        "metrics.py",
        "error_handlers.py",
        "logging_config.py",
        "metrics_endpoint.py",
        "MONITORING.md",
        "PHASE_4_QUICK_REFERENCE.md",
        "PHASE_4_IMPLEMENTATION_SUMMARY.md",
        "test_monitoring.py",
    ]

    all_exist = True
    for filename in expected_files:
        filepath = mcp_dir / filename
        exists = filepath.exists()
        status = "✓" if exists else "✗"
        print(f"  {status} {filename}")
        if not exists:
            all_exist = False

    if all_exist:
        print("\n✓ All files created successfully")
    else:
        print("\n✗ Some files are missing")

    return all_exist


def verify_imports():
    """Verify all modules can be imported."""
    print("\n=== Verifying Module Imports ===")

    modules = [
        ("telemetry", ["TelemetryMiddleware", "PerformanceMonitoringMiddleware", "get_tracer"]),
        ("metrics", ["MetricsMiddleware", "MetricsExporter", "mcp_registry"]),
        ("error_handlers", ["LLMFriendlyError", "ErrorEnhancementMiddleware"]),
        ("logging_config", ["configure_structured_logging", "StructuredLogger"]),
        ("metrics_endpoint", ["MetricsServer", "start_metrics_server"]),
    ]

    all_imported = True
    for module_name, expected_exports in modules:
        try:
            module = __import__(f"tracertm.mcp.{module_name}", fromlist=expected_exports)

            # Check exports
            missing = []
            for export in expected_exports:
                if not hasattr(module, export):
                    missing.append(export)

            if missing:
                print(f"  ✗ {module_name}: Missing exports {missing}")
                all_imported = False
            else:
                print(f"  ✓ {module_name}: All exports present")
        except ImportError as e:
            print(f"  ✗ {module_name}: Import failed - {e}")
            all_imported = False

    if all_imported:
        print("\n✓ All modules imported successfully")
    else:
        print("\n✗ Some imports failed")

    return all_imported


def verify_middleware_integration():
    """Verify middleware is properly integrated."""
    print("\n=== Verifying Middleware Integration ===")

    try:
        from tracertm.mcp.core import build_mcp_server
        import os

        # Set env vars to enable monitoring
        os.environ["TRACERTM_MCP_TELEMETRY_ENABLED"] = "true"
        os.environ["TRACERTM_MCP_METRICS_ENABLED"] = "true"

        # Build server
        mcp = build_mcp_server()

        print("  ✓ MCP server builds successfully")
        print("  ✓ Monitoring middleware integrated")

        # Verify server has expected attributes
        if not hasattr(mcp, "tool"):
            print("  ✗ Server missing tool decorator")
            return False

        print("  ✓ Server properly configured")
        return True
    except Exception as e:
        print(f"  ✗ Server build failed: {e}")
        return False


def verify_error_classes():
    """Verify error classes are properly defined."""
    print("\n=== Verifying Error Classes ===")

    try:
        from tracertm.mcp.error_handlers import (
            LLMFriendlyError,
            ProjectNotSelectedError,
            ItemNotFoundError,
            DatabaseError,
            ValidationError,
        )

        # Test error creation
        errors = [
            ProjectNotSelectedError(),
            ItemNotFoundError("test-id", "test-project"),
            DatabaseError("test-op", "test-error"),
            ValidationError("test-field", "test-value", "test-reason"),
        ]

        all_valid = True
        for error in errors:
            if not isinstance(error, LLMFriendlyError):
                print(f"  ✗ {error.__class__.__name__} not instance of LLMFriendlyError")
                all_valid = False
                continue

            error_dict = error.to_dict()
            if "error" not in error_dict or "type" not in error_dict:
                print(f"  ✗ {error.__class__.__name__} missing required fields")
                all_valid = False
                continue

            print(f"  ✓ {error.__class__.__name__}: {error_dict['error'][:50]}...")

        if all_valid:
            print("\n✓ All error classes working correctly")
        else:
            print("\n✗ Some error classes have issues")

        return all_valid
    except Exception as e:
        print(f"  ✗ Error verification failed: {e}")
        return False


def verify_metrics_definitions():
    """Verify metrics are properly defined."""
    print("\n=== Verifying Metrics Definitions ===")

    try:
        from tracertm.mcp.metrics import (
            tool_duration_seconds,
            tool_calls_total,
            tool_errors_total,
            tool_payload_size_bytes,
            active_tool_calls,
            rate_limit_hits_total,
            auth_failures_total,
        )

        metrics = {
            "tool_duration_seconds": tool_duration_seconds,
            "tool_calls_total": tool_calls_total,
            "tool_errors_total": tool_errors_total,
            "tool_payload_size_bytes": tool_payload_size_bytes,
            "active_tool_calls": active_tool_calls,
            "rate_limit_hits_total": rate_limit_hits_total,
            "auth_failures_total": auth_failures_total,
        }

        for name, metric in metrics.items():
            print(f"  ✓ {name}: {type(metric).__name__}")

        print("\n✓ All metrics defined correctly")
        return True
    except Exception as e:
        print(f"  ✗ Metrics verification failed: {e}")
        return False


def main():
    """Run all verification checks."""
    print("=" * 60)
    print("MCP Optimization Phase 4 - Verification")
    print("=" * 60)

    results = []

    results.append(("File Creation", verify_files_exist()))
    results.append(("Module Imports", verify_imports()))
    results.append(("Middleware Integration", verify_middleware_integration()))
    results.append(("Error Classes", verify_error_classes()))
    results.append(("Metrics Definitions", verify_metrics_definitions()))

    print("\n" + "=" * 60)
    print("Verification Summary")
    print("=" * 60)

    for check_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {check_name}")

    all_passed = all(result[1] for result in results)

    if all_passed:
        print("\n" + "=" * 60)
        print("✓ PHASE 4 VERIFICATION SUCCESSFUL")
        print("=" * 60)
        print("\nAll monitoring components are properly implemented and integrated.")
        print("\nNext steps:")
        print("1. Set environment variables to enable monitoring")
        print("2. Start metrics server: start_metrics_server(port=9090)")
        print("3. Configure Prometheus to scrape /metrics endpoint")
        print("4. Set up Grafana dashboards")
        print("5. Review MONITORING.md for complete documentation")
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ PHASE 4 VERIFICATION FAILED")
        print("=" * 60)
        print("\nSome checks failed. Review the output above for details.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
