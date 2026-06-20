// SPDX-License-Identifier: MIT OR Apache-2.0
// Copyright 2026 Koosha Pari

//! Cargo workspace/package metadata exposed to downstream bindings.

use serde::{Deserialize, Serialize};

/// Cargo metadata for the tracera-core crate/workspace boundary.
#[derive(Debug, Clone, Copy, PartialEq, Eq, Serialize, Deserialize)]
pub struct WorkspaceMetadata {
    pub package: &'static str,
    pub version: &'static str,
    pub edition: &'static str,
    pub msrv: &'static str,
    pub license: &'static str,
}

impl WorkspaceMetadata {
    pub const fn current() -> Self {
        Self {
            package: env!("CARGO_PKG_NAME"),
            version: env!("CARGO_PKG_VERSION"),
            edition: "2021",
            msrv: "1.82",
            license: env!("CARGO_PKG_LICENSE"),
        }
    }
}

pub const WORKSPACE_METADATA: WorkspaceMetadata = WorkspaceMetadata::current();

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn exposes_cargo_workspace_metadata() {
        assert_eq!(WORKSPACE_METADATA.package, "tracera-core");
        assert_eq!(WORKSPACE_METADATA.version, "0.1.0");
        assert_eq!(WORKSPACE_METADATA.edition, "2021");
        assert_eq!(WORKSPACE_METADATA.msrv, "1.82");
        assert_eq!(WORKSPACE_METADATA.license, "MIT OR Apache-2.0");
    }

    #[test]
    fn serializes_metadata_keys() {
        let json = serde_json::to_value(WORKSPACE_METADATA).unwrap();
        assert_eq!(json["version"], "0.1.0");
        assert_eq!(json["edition"], "2021");
        assert_eq!(json["msrv"], "1.82");
        assert_eq!(json["license"], "MIT OR Apache-2.0");
    }
}
