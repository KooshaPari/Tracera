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
//! - [`cache`] — optional Upstash Redis REST cache wrapper (auto-disabled
//!   when `CACHE_URL` env var is absent; `Ping` + `Get` + `Set` + `Del`)
//! - [`neo4j`] — optional Neo4j Bolt sync client (auto-disabled when
//!   `NEO4J_URL` env var is absent; pushes SWEE nodes/edges on `sync`)
//! - [`r2`] — optional Cloudflare R2 artifact uploader (auto-disabled
//!   when `R2_*` env vars are absent; PUT/GET helper for SWEE snapshots)
//!
//! The HTTP layer (`main.rs`) stays a binary-only crate: it glues this lib
//! to axum/axum-extra but contributes no types that other crates need.

pub mod store;
pub mod swee;
pub mod cache;
pub mod neo4j;
pub mod r2;