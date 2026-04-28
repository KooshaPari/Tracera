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


def verify_imports() -> bool:
    """Verify all required modules can be imported."""
    try:
        from tracertm.api.routers import mcp

        _ = mcp
    except ImportError:
        return False

    try:
        from tracertm.mcp.core import create_mcp_server

        _ = create_mcp_server
    except ImportError:
        return False

    try:
        from tracertm.mcp.auth import build_auth_provider

        _ = build_auth_provider
    except ImportError:
        return False

    try:
        from tracertm.core.context import current_account_id, current_user_id

        _ = (current_account_id, current_user_id)
    except ImportError:
        return False

    return True


def verify_router_endpoints() -> bool:
    """Verify MCP router has all expected endpoints."""
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
            pass
        else:
            return False

    return True


def verify_auth_integration() -> bool:
    """Verify auth_guard is used in endpoints."""
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
                pass
            else:
                return False
        else:
            return False

    return True


def verify_transport_modes() -> bool:
    """Verify MCP core supports transport modes."""
    from tracertm.mcp.auth import build_auth_provider

    # Test STDIO mode
    try:
        _ = build_auth_provider(transport="stdio")
    except Exception:
        return False

    # Test HTTP mode
    try:
        http_auth = build_auth_provider(transport="http")
        if http_auth is None:
            pass
        else:
            return False
    except Exception:
        return False

    return True


def verify_user_context_injection() -> bool:
    """Verify auth_guard sets user context."""
    import inspect

    from tracertm.api.deps import auth_guard

    # Check auth_guard source for current_user_id.set()
    source = inspect.getsource(auth_guard)

    if "current_user_id.set" in source:
        pass
    else:
        return False

    return True


def verify_fastapi_integration() -> bool:
    """Verify MCP router is mounted in FastAPI app."""
    try:
        from tracertm.api.main import app

    except ImportError:
        return False

    # Check if MCP router is mounted
    mcp_routes = [route for route in app.routes if "/mcp" in str(getattr(route, "path", ""))]

    if mcp_routes:
        for _route in mcp_routes:
            pass
    else:
        return False

    return True


def main() -> int:
    """Run all verification checks."""
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
        except Exception:
            import traceback

            traceback.print_exc()
            results.append((name, False))

    # Print summary

    all_passed = True
    for _name, result in results:
        if not result:
            all_passed = False

    if all_passed:
        return 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
