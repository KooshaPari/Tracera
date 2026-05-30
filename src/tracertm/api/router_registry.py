"""Central API router registration for the FastAPI app."""

from fastapi import FastAPI

from tracertm.api.routers import (
    accounts,
    adrs,
    agent,
    analysis,
    auth,
    auth_public,
    auth_refresh,
    auth_session,
    blockchain,
    cache,
    chat,
    code_trace,
    codex,
    comments,
    contracts,
    coverage,
    coverage_matrix,
    dup_conflict,
    execution,
    executions,
    features,
    github,
    graphs,
    health,
    impact,
    impact_scoring,
    ingest,
    integrations,
    items,
    items_summary,
    linear,
    links,
    mcp,
    mine,
    notifications,
    oauth,
    problems,
    processes,
    project_sync_search,
    projects,
    qa_metrics,
    quality,
    temporal,
    test_cases,
    test_run_results,
    test_runs,
    test_suites,
    traceability_score,
    webhooks,
    websocket,
    workflows,
)


def register_api_routers(app: FastAPI) -> None:
    """Register all API routers on the given application."""
    # Authentication endpoints (device flow, token management, etc.)
    app.include_router(auth.router)
    app.include_router(auth_refresh.router)
    app.include_router(auth_session.router)
    app.include_router(auth_public.router)
    app.include_router(health.router)
    app.include_router(accounts.router)
    app.include_router(cache.router)
    app.include_router(chat.router)
    app.include_router(items.router)
    app.include_router(items_summary.router)
    app.include_router(comments.router)
    app.include_router(projects.router)
    app.include_router(analysis.router)
    app.include_router(code_trace.router)
    app.include_router(links.router)
    app.include_router(graphs.router, prefix="/api/v1")
    app.include_router(test_cases.router)
    app.include_router(test_suites.router)
    app.include_router(test_runs.router)
    app.include_router(test_run_results.router)
    app.include_router(coverage.router)
    app.include_router(qa_metrics.router)
    app.include_router(problems.router)
    app.include_router(processes.router)
    app.include_router(executions.router)
    app.include_router(workflows.router, prefix="/api/v1")
    app.include_router(codex.router)

    # Specification routers
    app.include_router(adrs.router, prefix="/api/v1")
    app.include_router(contracts.router, prefix="/api/v1")
    app.include_router(features.router, prefix="/api/v1")
    app.include_router(quality.router, prefix="/api/v1")
    app.include_router(notifications.router, prefix="/api/v1")
    app.include_router(blockchain.router, prefix="/api/v1")
    app.include_router(execution.router, prefix="/api/v1")
    app.include_router(temporal.router)
    app.include_router(project_sync_search.router)

    # Agent sessions and workflow
    app.include_router(agent.router, prefix="/api/v1")

    # Impact analysis (Cypher forward/reverse traversal)
    app.include_router(impact.router, prefix="/api/v1")

    # Blast-radius risk-weighted scoring (FR-TRC-015)
    app.include_router(impact_scoring.router, prefix="/api/v1")

    # Duplicate / conflict detection (FR-TRC-012)
    app.include_router(dup_conflict.router, prefix="/api/v1")

    # Bulk external issue ingestion (FR-TRC-013)
    app.include_router(ingest.router, prefix="/api/v1")

    # Requirement miner (FR-TRC-011)
    app.include_router(mine.router, prefix="/api/v1")

    # Traceability quality scoring (FR-TRC-017)
    app.include_router(traceability_score.router, prefix="/api/v1")

    # Coverage matrix export (FR-TRC-014)
    app.include_router(coverage_matrix.router, prefix="/api/v1")

    # MCP router (Model Context Protocol over HTTP)
    app.include_router(mcp.router, prefix="/api/v1")

    # OAuth and integration management
    app.include_router(oauth.router)
    app.include_router(github.router)
    app.include_router(github.webhook_router)
    app.include_router(linear.router)
    app.include_router(integrations.router)
    app.include_router(webhooks.router)
    app.include_router(webhooks.project_router)
    app.include_router(websocket.router)
