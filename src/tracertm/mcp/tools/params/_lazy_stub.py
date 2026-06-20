"""Lazy loading stub for tools not yet fully migrated.

This temporary module provides stub implementations that avoid importing
the monolithic param.py file, preventing duplicate tool registrations.

Once these tools are fully migrated to their own modules, this stub can be removed.
"""

from __future__ import annotations


# Import-on-use pattern to avoid loading all of param.py
async def agent_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Agent management - imports only when called."""
    # Deferred import to avoid loading param.py at module level
    from tracertm.mcp.tools.param import agents_manage

    return await agents_manage(action, payload, ctx)


async def progress_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Progress management - imports only when called."""
    from tracertm.mcp.tools.param import progress_manage

    return await progress_manage(action, payload, ctx)


async def saved_query_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Saved query management - imports only when called."""
    from tracertm.mcp.tools.param import saved_queries_manage

    return await saved_queries_manage(action, payload, ctx)


async def test_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Test management - imports only when called."""
    from tracertm.mcp.tools.param import test_manage

    return await test_manage(action, payload, ctx)


async def tui_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """TUI management - imports only when called."""
    from tracertm.mcp.tools.param import tui_manage

    return await tui_manage(action, payload, ctx)


async def benchmark_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Benchmark management - imports only when called."""
    from tracertm.mcp.tools.param import benchmark_manage

    return await benchmark_manage(action, payload, ctx)


async def chaos_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Chaos management - imports only when called."""
    from tracertm.mcp.tools.param import chaos_manage

    return await chaos_manage(action, payload, ctx)


async def design_manage(
    action: str,
    payload: dict[str, object] | None = None,
    ctx: object | None = None,
) -> dict[str, object]:
    """Design management - imports only when called."""
    from tracertm.mcp.tools.param import design_manage

    return await design_manage(action, payload, ctx)
