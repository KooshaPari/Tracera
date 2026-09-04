//! Tracera GraphQL gateway.
//!
//! This crate mirrors the Tracera REST surface (`tracera-server`) as
//! GraphQL queries and mutations, and adds a `graph_events` subscription
//! that streams node/edge mutations and domain events to live clients.
//!
//! # Layout
//!
//! ```text
//! src/
//! ├── lib.rs                    — crate root, re-exports the public surface
//! ├── schema.rs                 — Query + Mutation + Subscription roots
//! ├── events.rs                 — broadcast bus + GraphEvent union
//! ├── resolvers/
//! │   ├── mod.rs
//! │   ├── node.rs               — SWEE node CRUD + NodeKind enum
//! │   ├── edge.rs               — SWEE edge CRUD + EdgeKind enum
//! │   └── subgraph.rs           — coverage / impact / blast / neighbours
//! └── bin/
//!     └── graphql-server.rs     — HTTP/WS gateway bound to :8081
//! ```
//!
//! # REST ↔ GraphQL parity
//!
//! | REST endpoint                                | GraphQL field             |
//! | -------------------------------------------- | ------------------------- |
//! | `GET  /api/v1/graph/nodes/{id}`              | `node(id)`                |
//! | `GET  /api/v1/graph/nodes`                   | `nodes(filter)`           |
//! | `POST /api/v1/graph/nodes`                   | `createNode(input)`       |
//! | `GET  /api/v1/graph/edges`                   | `edges(filter)`           |
//! | `POST /api/v1/graph/edges`                   | `createEdge(input)`       |
//! | `GET  /api/v1/trace/{id}/links`              | `incidentLinks(id)`       |
//! | `POST /api/v1/trace`                         | `createTraceLink(input)`  |
//! | `POST /api/v1/coverage-matrix`               | `coverageMatrix(input)`   |
//! | `POST /api/v1/impact`                        | `impact(input)`           |
//! | `POST /api/v1/blast-radius`                  | `blastRadius(input)`      |
//! | `POST /api/v1/trace/{forward,reverse}/{id}`  | `traceNeighbors(...)`     |
//! | `POST /api/v1/governance/spec-check`         | `specCheck(input)`        |
//!
//! # Storage abstraction
//!
//! The schema depends on the [`GraphStore`] trait so the binary can plug in
//! either an in-memory store (tests / demo) or the production
//! `tracera_server::Store` (real Postgres / SQLite). State is held in
//! [`GraphContext`] and injected via `async_graphql::Schema::data`.
//!
//! # Subscriptions
//!
//! `graph_events(filter)` streams:
//!  - `NODE_CREATED` / `NODE_UPDATED`
//!  - `EDGE_CREATED` / `EDGE_UPDATED`
//!  - `DOMAIN_EVENT`
//!
//! The bus is a `tokio::sync::broadcast` channel wrapped by
//! [`tokio_stream::wrappers::BroadcastStream`] so subscribers can attach
//! with normal `futures::Stream` combinators.

#![deny(rust_2018_idioms)]
#![warn(missing_debug_implementations)]

pub mod events;
pub mod resolvers;
pub mod schema;

pub use events::{
    DomainEvent, EdgeCreatedEvent, EdgeUpdatedEvent, GraphEvent, GraphEventBus, GraphEventFilter,
    NodeCreatedEvent, NodeUpdatedEvent,
};

pub use resolvers::edge::{
    EdgeCreateInput, EdgeKind, EdgeListFilter, GraphEdge, NodeRef as EdgeNodeRef,
    PersistedTraceLink, TraceDirection, TraceLinkCreateInput, TraceNeighbors,
};

pub use resolvers::node::{
    GraphNode, NodeCreateInput, NodeKind, NodeListFilter, NodeRef as GraphNodeRef,
};

pub use resolvers::subgraph::{
    BlastNode, BlastRadiusInput, BlastRadiusReport, CoverageMatrix, CoverageMatrixInput,
    GovernanceReport, GovernanceSpecInput, GovernanceTraceInput, GovernanceViolation,
    ImpactInput, ImpactNode, ImpactReport, MatrixCell, SpecCheckInput, TraceLinkInput,
    TraceNeighborsInput, MAX_COVERAGE_LINKS,
};

pub use schema::{
    build_schema, GraphContext, GraphStore, MutationRoot, QueryRoot, SubscriptionRoot, TraceraSchema,
};
