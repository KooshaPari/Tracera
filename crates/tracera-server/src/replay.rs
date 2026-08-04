//! Replay-v2 verification primitives.
//!
//! This slice owns only the public-key keyring boundary.  Private signing
//! material never crosses into Tracera; producers publish a JSON object of
//! key IDs to canonical base64-encoded Ed25519 public keys.

use base64::{engine::general_purpose::STANDARD, Engine as _};
use ed25519_dalek::VerifyingKey;
use serde_json::Value;
use std::collections::BTreeMap;

const KEYRING_ENV: &str = "TRACERA_REPLAY_PUBLIC_KEYS_JSON";

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum KeyringError {
    InvalidJson(String),
    InvalidKeyId(String),
    InvalidKeyEncoding(String),
}

impl std::fmt::Display for KeyringError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::InvalidJson(message) => write!(f, "invalid replay public-key JSON: {message}"),
            Self::InvalidKeyId(message) => write!(f, "invalid replay key_id: {message}"),
            Self::InvalidKeyEncoding(message) => {
                write!(f, "invalid replay public-key encoding: {message}")
            }
        }
    }
}

impl std::error::Error for KeyringError {}

/// Rotation-safe Ed25519 public keys indexed by stable producer key IDs.
#[derive(Clone, Default)]
pub struct PublicKeyring {
    keys: BTreeMap<String, VerifyingKey>,
}

impl PublicKeyring {
    /// Load the keyring from `TRACERA_REPLAY_PUBLIC_KEYS_JSON`.
    ///
    /// Missing or blank configuration yields an empty keyring so existing
    /// non-replay routes can start; replay verification remains fail-closed
    /// because an empty keyring cannot resolve any producer key ID.
    pub fn from_env() -> Result<Self, KeyringError> {
        match std::env::var(KEYRING_ENV) {
            Ok(raw) if !raw.trim().is_empty() => Self::from_json_str(&raw),
            _ => Ok(Self::default()),
        }
    }

    /// Parse a JSON object shaped as `{ "key-id": "base64-public-key" }`.
    pub fn from_json_str(raw: &str) -> Result<Self, KeyringError> {
        let value: Value = serde_json::from_str(raw)
            .map_err(|error| KeyringError::InvalidJson(error.to_string()))?;
        let entries = value.as_object().ok_or_else(|| {
            KeyringError::InvalidJson("keyring must be a JSON object".to_string())
        })?;
        if entries.is_empty() {
            return Err(KeyringError::InvalidJson(
                "keyring must contain at least one key".to_string(),
            ));
        }

        let mut keys = BTreeMap::new();
        for (key_id, encoded) in entries {
            validate_key_id(key_id)?;
            let encoded = encoded.as_str().ok_or_else(|| {
                KeyringError::InvalidKeyEncoding(format!("{key_id} must be a string"))
            })?;
            let raw = STANDARD.decode(encoded).map_err(|error| {
                KeyringError::InvalidKeyEncoding(format!("{key_id} is not valid base64: {error}"))
            })?;
            if STANDARD.encode(&raw) != encoded {
                return Err(KeyringError::InvalidKeyEncoding(format!(
                    "{key_id} must use canonical base64"
                )));
            }
            let bytes: [u8; 32] = raw.try_into().map_err(|_| {
                KeyringError::InvalidKeyEncoding(format!("{key_id} must encode 32 bytes"))
            })?;
            let key = VerifyingKey::from_bytes(&bytes).map_err(|error| {
                KeyringError::InvalidKeyEncoding(format!("{key_id} is not an Ed25519 key: {error}"))
            })?;
            keys.insert(key_id.clone(), key);
        }
        Ok(Self { keys })
    }

    pub fn contains(&self, key_id: &str) -> bool {
        self.keys.contains_key(key_id)
    }

    pub fn len(&self) -> usize {
        self.keys.len()
    }
}

fn validate_key_id(key_id: &str) -> Result<(), KeyringError> {
    let mut chars = key_id.chars();
    let first = chars.next().ok_or_else(|| {
        KeyringError::InvalidKeyId("must be 1-128 safe identifier characters".to_string())
    })?;
    if !first.is_ascii_alphanumeric()
        || key_id.len() > 128
        || chars.any(|ch| !(ch.is_ascii_alphanumeric() || matches!(ch, '.' | '_' | '-')))
    {
        return Err(KeyringError::InvalidKeyId(format!(
            "{key_id:?} must match [A-Za-z0-9][A-Za-z0-9._-]{{0,127}}"
        )));
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    use ed25519_dalek::SigningKey;
    use rand_core::OsRng;
    use std::sync::{Mutex, OnceLock};

    fn generated_keyring() -> (String, String) {
        let signing_key = SigningKey::generate(&mut OsRng);
        let public_key = STANDARD.encode(signing_key.verifying_key().to_bytes());
        ("producer-20260804-a".to_string(), public_key)
    }

    #[test]
    fn parses_generated_public_key_json() {
        let (key_id, public_key) = generated_keyring();
        let keyring =
            PublicKeyring::from_json_str(&serde_json::json!({key_id: public_key}).to_string())
                .expect("generated public key should parse");
        assert_eq!(keyring.len(), 1);
        assert!(keyring.contains("producer-20260804-a"));
    }

    #[test]
    fn rejects_bad_base64_and_wrong_length() {
        let invalid = PublicKeyring::from_json_str(r#"{"producer-a":"not base64"}"#);
        assert!(matches!(invalid, Err(KeyringError::InvalidKeyEncoding(_))));

        let short = STANDARD.encode([1_u8; 31]);
        let invalid =
            PublicKeyring::from_json_str(&serde_json::json!({"producer-a": short}).to_string());
        assert!(matches!(invalid, Err(KeyringError::InvalidKeyEncoding(_))));
    }

    #[test]
    fn rejects_unsafe_key_ids_and_empty_keyrings() {
        let key = STANDARD.encode([1_u8; 32]);
        let invalid =
            PublicKeyring::from_json_str(&serde_json::json!({"producer/a": key}).to_string());
        assert!(matches!(invalid, Err(KeyringError::InvalidKeyId(_))));
        assert!(matches!(
            PublicKeyring::from_json_str("{}"),
            Err(KeyringError::InvalidJson(_))
        ));
    }

    #[test]
    fn loads_keyring_from_environment() {
        static ENV_LOCK: OnceLock<Mutex<()>> = OnceLock::new();
        let _guard = ENV_LOCK.get_or_init(|| Mutex::new(())).lock().unwrap();
        let (key_id, public_key) = generated_keyring();
        std::env::set_var(
            KEYRING_ENV,
            serde_json::json!({key_id: public_key}).to_string(),
        );
        let loaded = PublicKeyring::from_env().expect("environment keyring should parse");
        std::env::remove_var(KEYRING_ENV);
        assert_eq!(loaded.len(), 1);
    }
}
