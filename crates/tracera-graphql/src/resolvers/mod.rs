//! Resolver modules for the GraphQL gateway.
//!
//! Each module is the GraphQL counterpart of a slice of the REST surface.
//! Algorithms are kept identical so a REST client and a GraphQL client see
//! the same numbers for the same input — that is the entire point of the
//! "mirror the REST surface" goal.

pub mod edge;
pub mod node;
pub mod subgraph;
