//! Typed IDs for the tracera-core entity model.

use serde::{Deserialize, Serialize};
use uuid::Uuid;

macro_rules! typed_id {
    ($name:ident, $prefix:literal) => {
        #[derive(Debug, Clone, PartialEq, Eq, Hash, Serialize, Deserialize)]
        #[serde(transparent)]
        pub struct $name(String);

        impl $name {
            pub fn new() -> Self {
                Self(format!("{}{}", $prefix, Uuid::new_v4().simple()))
            }
            pub fn from_string(s: impl Into<String>) -> Self {
                Self(s.into())
            }
            pub fn as_str(&self) -> &str {
                &self.0
            }
        }

        impl Default for $name {
            fn default() -> Self {
                Self::new()
            }
        }
    };
}

typed_id!(TraceLinkId, "tl-");
typed_id!(RequirementId, "FR-");
typed_id!(NfrId, "NFR-");

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn ids_are_unique() {
        let a = TraceLinkId::new();
        let b = TraceLinkId::new();
        assert_ne!(a, b);
        assert!(a.as_str().starts_with("tl-"));
        assert!(RequirementId::new().as_str().starts_with("FR-"));
        assert!(NfrId::new().as_str().starts_with("NFR-"));
    }
}
