#!/usr/bin/env python3
"""Verification script for MCP HTTP authentication integration.

This script verifies that:
1. MCP router is properly mounted in FastAPI
2. Auth guard integration works
3. User context injection is implemented
4. All expected endpoints exist
"""

import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))


def verify_imports():
    """Verify all required modules can be imported."""
    print("✓ Verifying imports...")

    try:
        from tracertm.api.routers import mcp  # noqa: F401

        print("  ✓ MCP router imported")
    except ImportError as e:
        print(f"  ✗ Failed to import MCP router: {e}")
        return False

    try:
        from tracertm.mcp.core import create_mcp_server  # noqa: F401

        print("  ✓ MCP core imported")
    except ImportError as e:
        print(f"  ✗ Failed to import MCP core: {e}")
        return False

    try:
        from tracertm.mcp.auth import build_auth_provider  # noqa: F401

        print("  ✓ MCP auth imported")
    except ImportError as e:
        print(f"  ✗ Failed to import MCP auth: {e}")
        return False

    try:
        from tracertm.core.context import current_account_id, current_user_id  # noqa: F401

        print("  ✓ Context variables imported")
    except ImportError as e:
        print(f"  ✗ Failed to import context variables: {e}")
        return False

    return True


def verify_router_endpoints():
    """Verify MCP router has all expected endpoints."""
    print("\n✓ Verifying MCP router endpoints...")

    from tracertm.api.main import app

    # Get all MCP routes from the mounted app
    mcp_routes = [getattr(route, "path", "") for route in app.routes if "/mcp" in str(getattr(route, "path", ""))]

    expected_routes = {
        "/api/v1/mcp/health",
        "/api/v1/mcp/tools",
        "/api/v1/mcp/messages",
        "/api/v1/mcp/sse",
    }

    found_routes = set(mcp_routes)

    for route in expected_routes:
        if route in found_routes:
            print(f"  ✓ {route} endpoint exists")
        else:
            print(f"  ✗ {route} endpoint missing (found: {found_routes})")
            return False

    return True


def verify_auth_integration():
    """Verify auth_guard is used in endpoints."""
    print("\n✓ Verifying auth integration...")

    import inspect

    from tracertm.api.routers import mcp

    # Check that endpoints use auth_guard
    endpoints_to_check = ["mcp_tools", "mcp_messages", "mcp_sse"]

    for endpoint_name in endpoints_to_check:
        if hasattr(mcp, endpoint_name):
            endpoint = getattr(mcp, endpoint_name)
            sig = inspect.signature(endpoint)

            # Check for claims parameter (injected by auth_guard)
            if "claims" in sig.parameters:
                print(f"  ✓ {endpoint_name} uses auth_guard")
            else:
                print(f"  ✗ {endpoint_name} missing auth_guard dependency")
                return False
        else:
            print(f"  ✗ {endpoint_name} function not found")
            return False

    return True


def verify_transport_modes():
    """Verify MCP core supports transport modes."""
    print("\n✓ Verifying transport modes...")

    from tracertm.mcp.auth import build_auth_provider

    # Test STDIO mode
    try:
        _ = build_auth_provider(transport="stdio")
        print("  ✓ STDIO transport mode supported")
    except Exception as e:
        print(f"  ✗ STDIO mode failed: {e}")
        return False

    # Test HTTP mode
    try:
        http_auth = build_auth_provider(transport="http")
        if http_auth is None:
            print("  ✓ HTTP transport mode returns None (FastAPI handles auth)")
        else:
            print("  ✗ HTTP mode should return None")
            return False
    except Exception as e:
        print(f"  ✗ HTTP mode failed: {e}")
        return False

    return True


def verify_user_context_injection():
    """Verify auth_guard sets user context."""
    print("\n✓ Verifying user context injection...")

    import inspect

    from tracertm.api.deps import auth_guard

    # Check auth_guard source for current_user_id.set()
    source = inspect.getsource(auth_guard)

    if "current_user_id.set" in source:
        print("  ✓ auth_guard sets user context")
    else:
        print("  ✗ auth_guard does not set user context")
        return False

    return True


def verify_fastapi_integration():
    """Verify MCP router is mounted in FastAPI app."""
    print("\n✓ Verifying FastAPI integration...")

    try:
        from tracertm.api.main import app

        print("  ✓ FastAPI app imported")
    except ImportError as e:
        print(f"  ✗ Failed to import FastAPI app: {e}")
        return False

    # Check if MCP router is mounted
    mcp_routes = [route for route in app.routes if "/mcp" in str(getattr(route, "path", ""))]

    if mcp_routes:
        print(f"  ✓ MCP router mounted ({len(mcp_routes)} routes)")
        for route in mcp_routes:
            print(f"    - {getattr(route, 'path', '')}")
    else:
        print("  ✗ MCP router not mounted")
        return False

    return True


def main():
    """Run all verification checks."""
    print("=" * 70)
    print("MCP HTTP Authentication Integration Verification")
    print("=" * 70)

    checks = [
        ("Imports", verify_imports),
        ("Router Endpoints", verify_router_endpoints),
        ("Auth Integration", verify_auth_integration),
        ("Transport Modes", verify_transport_modes),
        ("User Context Injection", verify_user_context_injection),
        ("FastAPI Integration", verify_fastapi_integration),
    ]

    results = []
    for name, check_fn in checks:
        try:
            result = check_fn()
            results.append((name, result))
        except Exception as e:
            print(f"\n✗ {name} check failed with error: {e}")
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Print summary
    print("\n" + "=" * 70)
    print("Summary")
    print("=" * 70)

    all_passed = True
    for name, result in results:
        status = "✓ PASS" if result else "✗ FAIL"
        print(f"{status}: {name}")
        if not result:
            all_passed = False

    print("=" * 70)

    if all_passed:
        print("\n🎉 All verification checks passed!")
        return 0
    print("\n❌ Some verification checks failed")
    return 1


if __name__ == "__main__":
    sys.exit(main())
