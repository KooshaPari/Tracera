//! Strongly-typed requirement identifiers.
//! Re-exports from shared core where available, with local fallback impl.

// Try re-export from traceability_core first; if the dep is available, use it.
// The local macro-based impl below is the fallback for standalone builds.

pub use traceability_core::{NfrId, RequirementId};

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn parse_rejects_empty_string() {
        let result = RequirementId::parse("");
        assert!(result.is_err());
        assert_eq!(result.unwrap_err(), "id cannot be empty");
    }

    #[test]
    fn parse_accepts_prefixed_id() {
        let id = RequirementId::parse("FR-123").unwrap();
        assert_eq!(id.as_str(), "FR-123");
    }

    #[test]
    fn parse_adds_prefix_when_missing() {
        let id = RequirementId::parse("123").unwrap();
        assert_eq!(id.as_str(), "FR-123");
    }

    #[test]
    fn parse_rejects_whitespace_only() {
        let result = RequirementId::parse("   ");
        assert!(result.is_err());
    }
}
