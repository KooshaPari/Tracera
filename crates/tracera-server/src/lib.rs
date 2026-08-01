//! Reusable Tracera server components.
//!
//! The phenodag queue is exposed from the library target so its opt-in API is
//! compiled as a real public surface.  Keeping it out of the binary target
//! avoids treating intentionally unbound library operations as dead code when
//! CI checks the feature-enabled workspace.

#[cfg(feature = "phenodag-queue")]
pub mod queue;
