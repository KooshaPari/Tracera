use serde::{Deserialize, Serialize};
use uuid::Uuid;

macro_rules! id_type {
    ($name:ident, $prefix:literal) => {
        #[derive(Debug, Clone, PartialEq, Eq, PartialOrd, Ord, Hash, Serialize, Deserialize)]
        pub struct $name(String);

        impl $name {
            pub fn new() -> Self {
                Self(format!("{}-{}", $prefix, Uuid::new_v4()))
            }

            pub fn from_string(value: impl Into<String>) -> Self {
                let value = value.into();
                if value.starts_with(concat!($prefix, "-")) {
                    Self(value)
                } else {
                    Self(format!("{}-{}", $prefix, value))
                }
            }

            pub fn parse(value: impl Into<String>) -> Result<Self, String> {
                let value = value.into();
                if value.trim().is_empty() {
                    Err("id cannot be empty".to_string())
                } else {
                    Ok(Self::from_string(value))
                }
            }

            pub fn as_str(&self) -> &str {
                &self.0
            }
        }
    };
}

id_type!(RequirementId, "FR");
id_type!(NfrId, "NFR");

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn requirement_id_parse_rejects_empty() {
        assert_eq!(
            RequirementId::parse("").unwrap_err(),
            "id cannot be empty"
        );
        assert_eq!(
            RequirementId::parse("   ").unwrap_err(),
            "id cannot be empty"
        );
    }

    #[test]
    fn requirement_id_from_string_adds_prefix_when_missing() {
        let id = RequirementId::from_string("42");
        assert_eq!(id.as_str(), "FR-42");
    }

    #[test]
    fn requirement_id_from_string_preserves_prefix_when_present() {
        let id = RequirementId::from_string("FR-99");
        assert_eq!(id.as_str(), "FR-99");
    }

    #[test]
    fn nfr_id_parse_roundtrips() {
        let id = NfrId::parse("PERF-01").unwrap();
        assert_eq!(id.as_str(), "NFR-PERF-01");
    }
}
