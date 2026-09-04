//! Tool registry for `tracera-mcp`.
//!
//! Every MCP tool exposed by this server is registered in exactly one of the
//! four submodules below. Each `#[tool]`-annotated method lives on
//! [`crate::McpServer`] and delegates to the underlying
//! [`tracera_server::store::Store`] trait.
//!
//! ## Module layout
//!
//! | Module        | Tools (count) | Purpose                                              |
//! |---------------|---------------|------------------------------------------------------|
//! | [`read`]      | 5             | `read_node`, `read_edge`, `read_subgraph`, `search`, `query` |
//! | [`write`]     | 4             | `create_node`, `update_node`, `create_edge`, `propose_change` |
//! | [`navigate`]  | 4             | `neighbors`, `path`, `impact`, `coverage`            |
//! | [`propose`]   | 2             | `propose_decision`, `propose_spec_change`            |
//!
//! ## Convention for tool authors
//!
//! 1. Every tool method must be `async` and return
//!    `Result<rmcp::model::CallToolResult, McpError>` — the `Ok` variant is
//!    the tool's documented output schema, the `Err` variant carries a typed
//!    [`crate::ToolError`].
//! 2. Every tool must carry a `#[tool(description = "...")]` attribute.
//!    rmcp surfaces this string in the `tools/list` response.
//! 3. Every tool input struct must `#[derive(serde::Deserialize, schemars::JsonSchema)]`
//!    so the macro can emit a JSON Schema for the `inputSchema` field.
//! 4. Every tool delegates to `self.store` (the `Arc<dyn StoreT>`) via the
//!    methods in [`crate::store_into`] / [`crate::ok`] / [`crate::ko`].
//! 5. **No tool may construct its own database handle.** All persistence
//!    flows through the trait.

pub mod navigate;
pub mod propose;
pub mod read;
pub mod write;

/// Total number of MCP tools exposed by this server.
///
/// Stable contract: 5 read + 4 write + 4 navigate + 2 propose = 15.
pub const TOOL_COUNT: usize = 15;

/// Names of every registered tool, in stable (registry-iteration) order.
pub const TOOL_NAMES: &[&str] = &[
    // read.rs
    "read_node",
    "read_edge",
    "read_subgraph",
    "search",
    "query",
    // write.rs
    "create_node",
    "update_node",
    "create_edge",
    "propose_change",
    // navigate.rs
    "neighbors",
    "path",
    "impact",
    "coverage",
    // propose.rs
    "propose_decision",
    "propose_spec_change",
];

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn tool_count_matches_constants() {
        assert_eq!(TOOL_COUNT, 15);
        assert_eq!(TOOL_NAMES.len(), 15);
        let unique: std::collections::HashSet<_> = TOOL_NAMES.iter().copied().collect();
        assert_eq!(unique.len(), TOOL_NAMES.len(), "tool names must be unique");
    }

    #[test]
    fn all_expected_tool_names_are_listed() {
        let expected = [
            "read_node", "read_edge", "read_subgraph", "search", "query",
            "create_node", "update_node", "create_edge", "propose_change",
            "neighbors", "path", "impact", "coverage",
            "propose_decision", "propose_spec_change",
        ];
        for name in expected {
            assert!(TOOL_NAMES.contains(&name), "missing tool: {name}");
        }
    }
}