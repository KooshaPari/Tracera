//! # tracera-server (library facade)
//!
//! Exposes the pure-data modules of the Tracera server as a reusable
//! library so partner crates (e.g. `tracera-mcp`, `tracera-atlas`,
//! `tracera-workos`) can depend on the canonical `Store` trait and the
//! SWEE graph taxonomy **without** pulling in the axum HTTP server graph.
//!
//! Only modules with no transport/IO coupling are re-exported here:
//!
//! - [`store`] — the `Store` trait + all row/domain types (`Test`, `Story`,
//!   `Sprint`, `TeamRow`, `ListParams`, `StoreError`, …)
//! - [`swee`] — the 30-node / 35-edge SWEE graph taxonomy
//!
//! The HTTP layer (`main.rs`) stays a binary-only crate: it glues this lib
//! to axum/axum-extra but contributes no types that other crates need.

pub mod store;
pub mod swee;