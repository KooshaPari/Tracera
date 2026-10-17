//! Remaining frontend route families; unavailable means unavailable, never empty.
use crate::AppState;
use axum::{routing::any, Router};

#[path = "accounts.rs"]
mod accounts;
#[path = "agent.rs"]
mod agent;
#[path = "ai.rs"]
mod ai;
#[path = "auth.rs"]
mod auth;
#[path = "branches.rs"]
mod branches;
#[path = "chat.rs"]
mod chat;
#[path = "codex.rs"]
mod codex;
#[path = "concepts.rs"]
mod concepts;
#[path = "coverage.rs"]
mod coverage;
#[path = "distributed_operations.rs"]
mod distributed_operations;
#[path = "docs.rs"]
mod docs;
#[path = "equivalence.rs"]
mod equivalence;
#[path = "equivalences.rs"]
mod equivalences;
#[path = "events.rs"]
mod events;
#[path = "execution_config.rs"]
mod execution_config;
#[path = "executions.rs"]
mod executions;
#[path = "graphs.rs"]
mod graphs;
#[path = "integrations.rs"]
mod integrations;
#[path = "item_specs.rs"]
mod item_specs;
#[path = "libraries.rs"]
mod libraries;
#[path = "matrix.rs"]
mod matrix;
#[path = "mcp.rs"]
mod mcp;
#[path = "metrics.rs"]
mod metrics;
#[path = "mutations.rs"]
mod mutations;
#[path = "notifications.rs"]
mod notifications;
#[path = "problems.rs"]
mod problems;
#[path = "processes.rs"]
mod processes;
#[path = "projects.rs"]
mod projects;
#[path = "qa.rs"]
mod qa;
#[path = "quality.rs"]
mod quality;
#[path = "reports.rs"]
mod reports;
#[path = "search.rs"]
mod search;
#[path = "settings.rs"]
mod settings;
#[path = "spec_analytics.rs"]
mod spec_analytics;
#[path = "storage.rs"]
mod storage;
#[path = "sync.rs"]
mod sync;
#[path = "test_cases.rs"]
mod test_cases;
#[path = "test_runs.rs"]
mod test_runs;
#[path = "test_suites.rs"]
mod test_suites;
#[path = "tokens.rs"]
mod tokens;
#[path = "versions.rs"]
mod versions;
#[path = "webhooks.rs"]
mod webhooks;
#[path = "workflows.rs"]
mod workflows;
#[path = "ws.rs"]
mod ws;

pub(super) fn unavailable_routes(paths: &[&str]) -> Router<AppState> {
    paths.iter().fold(Router::new(), |router, path| {
        router.route(path, any(crate::not_implemented::not_implemented))
    })
}

pub(super) fn routes() -> Router<AppState> {
    Router::new()
        .merge(accounts::routes())
        .merge(agent::routes())
        .merge(ai::routes())
        .merge(auth::routes())
        .merge(branches::routes())
        .merge(chat::routes())
        .merge(codex::routes())
        .merge(concepts::routes())
        .merge(coverage::routes())
        .merge(distributed_operations::routes())
        .merge(docs::routes())
        .merge(equivalence::routes())
        .merge(equivalences::routes())
        .merge(events::routes())
        .merge(execution_config::routes())
        .merge(executions::routes())
        .merge(super::graph_routes::w9_routes())
        .merge(graphs::routes())
        .merge(integrations::routes())
        .merge(item_specs::routes())
        .merge(super::item_routes::w9_routes())
        .merge(super::journeys_routes::w9_routes())
        .merge(libraries::routes())
        .merge(matrix::routes())
        .merge(mcp::routes())
        .merge(metrics::routes())
        .merge(mutations::routes())
        .merge(notifications::routes())
        .merge(problems::routes())
        .merge(processes::routes())
        .merge(projects::routes())
        .merge(qa::routes())
        .merge(quality::routes())
        .merge(reports::routes())
        .merge(search::routes())
        .merge(settings::routes())
        .merge(spec_analytics::routes())
        .merge(storage::routes())
        .merge(sync::routes())
        .merge(test_cases::routes())
        .merge(test_runs::routes())
        .merge(test_suites::routes())
        .merge(tokens::routes())
        .merge(versions::routes())
        .merge(webhooks::routes())
        .merge(workflows::routes())
        .merge(ws::routes())
}

#[cfg(test)]
fn templates() -> Vec<&'static str> {
    [
        accounts::ROUTES,
        agent::ROUTES,
        ai::ROUTES,
        auth::ROUTES,
        branches::ROUTES,
        chat::ROUTES,
        codex::ROUTES,
        concepts::ROUTES,
        coverage::ROUTES,
        distributed_operations::ROUTES,
        docs::ROUTES,
        equivalence::ROUTES,
        equivalences::ROUTES,
        events::ROUTES,
        execution_config::ROUTES,
        executions::ROUTES,
        super::graph_routes::W9_ROUTES,
        graphs::ROUTES,
        integrations::ROUTES,
        item_specs::ROUTES,
        super::item_routes::W9_ROUTES,
        super::journeys_routes::ROUTES,
        libraries::ROUTES,
        matrix::ROUTES,
        mcp::ROUTES,
        metrics::ROUTES,
        mutations::ROUTES,
        notifications::ROUTES,
        problems::ROUTES,
        processes::ROUTES,
        projects::ROUTES,
        qa::ROUTES,
        quality::ROUTES,
        reports::ROUTES,
        search::ROUTES,
        settings::ROUTES,
        spec_analytics::ROUTES,
        storage::ROUTES,
        sync::ROUTES,
        test_cases::ROUTES,
        test_runs::ROUTES,
        test_suites::ROUTES,
        tokens::ROUTES,
        versions::ROUTES,
        webhooks::ROUTES,
        workflows::ROUTES,
        ws::ROUTES,
    ]
    .concat()
}

#[cfg(test)]
#[path = "w9_tests.rs"]
mod tests;
