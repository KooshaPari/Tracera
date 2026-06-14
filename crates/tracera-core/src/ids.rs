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
    fn parse_rejects_empty_string() {
        let result = RequirementId::parse("");
        assert_eq!(result, Err("id cannot be empty".to_string()));
    }
}
