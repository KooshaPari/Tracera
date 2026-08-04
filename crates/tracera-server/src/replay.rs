//! Replay-v2 verification primitives.
//!
//! Private signing material never crosses into Tracera; producers publish a
//! JSON object of key IDs to canonical base64-encoded Ed25519 public keys.

use base64::{engine::general_purpose::STANDARD, Engine as _};
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use serde_json::Value;
use sha2::{Digest, Sha256};
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

    fn get(&self, key_id: &str) -> Option<&VerifyingKey> {
        self.keys.get(key_id)
    }
}

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum VerificationError {
    Schema(String),
    UnknownKey(String),
    InvalidEncoding(String),
    InvalidSignature,
    ReplayHashMismatch { expected: String, actual: String },
}

impl std::fmt::Display for VerificationError {
    fn fmt(&self, f: &mut std::fmt::Formatter<'_>) -> std::fmt::Result {
        match self {
            Self::Schema(message) => write!(f, "invalid benchmark replay schema: {message}"),
            Self::UnknownKey(key_id) => write!(f, "unknown replay signing key_id: {key_id}"),
            Self::InvalidEncoding(message) => {
                write!(f, "invalid replay signature encoding: {message}")
            }
            Self::InvalidSignature => write!(f, "invalid replay signature"),
            Self::ReplayHashMismatch { expected, actual } => write!(
                f,
                "replay_hash mismatch: envelope={expected}, recomputed={actual}"
            ),
        }
    }
}

impl std::error::Error for VerificationError {}

/// The verified fields needed by the persistence adapter in the next slice.
#[derive(Debug, Clone, PartialEq, Eq)]
pub struct VerifiedBenchmark {
    pub key_id: String,
    pub replay_hash: String,
    pub signature_digest: String,
}

/// Serialize JSON using the producer's sorted-key, compact UTF-8 contract.
pub fn canonical_json_bytes(value: &Value) -> Vec<u8> {
    let mut output = Vec::new();
    write_canonical(value, &mut output);
    output
}

fn write_canonical(value: &Value, output: &mut Vec<u8>) {
    match value {
        Value::Null => output.extend_from_slice(b"null"),
        Value::Bool(value) => output.extend_from_slice(if *value { b"true" } else { b"false" }),
        Value::Number(value) => output.extend_from_slice(value.to_string().as_bytes()),
        Value::String(value) => serde_json::to_writer(output, value).expect("strings serialize"),
        Value::Array(values) => {
            output.push(b'[');
            for (index, value) in values.iter().enumerate() {
                if index > 0 {
                    output.push(b',');
                }
                write_canonical(value, output);
            }
            output.push(b']');
        }
        Value::Object(values) => {
            let mut keys: Vec<&String> = values.keys().collect();
            keys.sort_unstable();
            output.push(b'{');
            for (index, key) in keys.into_iter().enumerate() {
                if index > 0 {
                    output.push(b',');
                }
                serde_json::to_writer(&mut *output, key).expect("keys serialize");
                output.push(b':');
                write_canonical(&values[key], output);
            }
            output.push(b'}');
        }
    }
}

pub fn sha256_hex(value: &[u8]) -> String {
    let digest = Sha256::digest(value);
    digest.iter().map(|byte| format!("{byte:02x}")).collect()
}

pub fn replay_hash(events: &Value) -> Result<String, VerificationError> {
    if !events.is_array() {
        return Err(VerificationError::Schema(
            "events must be an array".to_string(),
        ));
    }
    Ok(sha256_hex(&canonical_json_bytes(events)))
}

pub fn signed_envelope_bytes(envelope: &Value) -> Result<Vec<u8>, VerificationError> {
    let object = envelope
        .as_object()
        .ok_or_else(|| VerificationError::Schema("envelope must be an object".to_string()))?;
    let mut unsigned = object.clone();
    unsigned.remove("signature");
    Ok(canonical_json_bytes(&Value::Object(unsigned)))
}

/// Verify schema version, replay hash, and detached Ed25519 signature.
pub fn verify_benchmark_envelope(
    envelope: &Value,
    keyring: &PublicKeyring,
) -> Result<VerifiedBenchmark, VerificationError> {
    let object = envelope
        .as_object()
        .ok_or_else(|| VerificationError::Schema("envelope must be an object".to_string()))?;
    if object.get("schema_version").and_then(Value::as_str) != Some("2.0.0") {
        return Err(VerificationError::Schema(
            "schema_version must be 2.0.0".to_string(),
        ));
    }
    let events = object
        .get("events")
        .ok_or_else(|| VerificationError::Schema("events is required".to_string()))?;
    let actual_hash = replay_hash(events)?;
    let result = object
        .get("result")
        .and_then(Value::as_object)
        .ok_or_else(|| VerificationError::Schema("result must be an object".to_string()))?;
    let expected_hash = result
        .get("replay_hash")
        .and_then(Value::as_str)
        .ok_or_else(|| VerificationError::Schema("result.replay_hash is required".to_string()))?;
    if expected_hash != actual_hash {
        return Err(VerificationError::ReplayHashMismatch {
            expected: expected_hash.to_string(),
            actual: actual_hash,
        });
    }
    let signature = object
        .get("signature")
        .and_then(Value::as_object)
        .ok_or_else(|| VerificationError::Schema("signature must be an object".to_string()))?;
    if signature.get("algorithm").and_then(Value::as_str) != Some("ed25519") {
        return Err(VerificationError::Schema(
            "signature.algorithm must be ed25519".to_string(),
        ));
    }
    let key_id = signature
        .get("key_id")
        .and_then(Value::as_str)
        .ok_or_else(|| VerificationError::Schema("signature.key_id is required".to_string()))?;
    let verifying_key = keyring
        .get(key_id)
        .ok_or_else(|| VerificationError::UnknownKey(key_id.to_string()))?;
    let encoded = signature
        .get("signature_b64")
        .and_then(Value::as_str)
        .ok_or_else(|| {
            VerificationError::Schema("signature.signature_b64 is required".to_string())
        })?;
    let signature_bytes = STANDARD.decode(encoded).map_err(|error| {
        VerificationError::InvalidEncoding(format!("base64 decode failed: {error}"))
    })?;
    if STANDARD.encode(&signature_bytes) != encoded || signature_bytes.len() != 64 {
        return Err(VerificationError::InvalidEncoding(
            "signature must be canonical base64 encoding of 64 bytes".to_string(),
        ));
    }
    let signature_array: [u8; 64] = signature_bytes.try_into().expect("length checked");
    verifying_key
        .verify(
            &signed_envelope_bytes(envelope)?,
            &Signature::from_bytes(&signature_array),
        )
        .map_err(|_| VerificationError::InvalidSignature)?;

    Ok(VerifiedBenchmark {
        key_id: key_id.to_string(),
        replay_hash: expected_hash.to_string(),
        signature_digest: sha256_hex(&signature_array),
    })
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
    use ed25519_dalek::{Signer, SigningKey};
    use rand_core::OsRng;
    use std::sync::{Mutex, OnceLock};

    fn generated_signing_key() -> SigningKey {
        SigningKey::generate(&mut OsRng)
    }

    fn generated_keyring(signing_key: &SigningKey) -> PublicKeyring {
        let public_key = STANDARD.encode(signing_key.verifying_key().to_bytes());
        PublicKeyring::from_json_str(
            &serde_json::json!({"producer-20260804-a": public_key}).to_string(),
        )
        .expect("generated public key should parse")
    }

    fn signed_fixture(signing_key: &SigningKey) -> Value {
        let events = serde_json::json!([
            {"type": "run_started", "seq": 0, "details": {"suite": "synthetic"}},
            {"type": "run_finished", "seq": 1, "details": {"status": "passed"}}
        ]);
        let mut envelope = serde_json::json!({
            "schema_version": "2.0.0",
            "events": events,
            "result": {"replay_hash": replay_hash(&events).expect("events hash")}
        });
        resign(&mut envelope, signing_key);
        envelope
    }

    fn resign(envelope: &mut Value, signing_key: &SigningKey) {
        let bytes = signed_envelope_bytes(envelope).expect("unsigned envelope bytes");
        let signature = signing_key.sign(&bytes);
        envelope["signature"] = serde_json::json!({
            "algorithm": "ed25519",
            "key_id": "producer-20260804-a",
            "signature_b64": STANDARD.encode(signature.to_bytes())
        });
    }

    #[test]
    fn parses_generated_public_key_json() {
        let signing_key = generated_signing_key();
        let keyring = generated_keyring(&signing_key);
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
        let signing_key = generated_signing_key();
        let key_id = "producer-20260804-a";
        let public_key = STANDARD.encode(signing_key.verifying_key().to_bytes());
        std::env::set_var(
            KEYRING_ENV,
            serde_json::json!({key_id: public_key}).to_string(),
        );
        let loaded = PublicKeyring::from_env().expect("environment keyring should parse");
        std::env::remove_var(KEYRING_ENV);
        assert_eq!(loaded.len(), 1);
    }

    #[test]
    fn verifies_generated_detached_signature_and_replay_hash() {
        let signing_key = generated_signing_key();
        let envelope = signed_fixture(&signing_key);
        let verified = verify_benchmark_envelope(&envelope, &generated_keyring(&signing_key))
            .expect("generated envelope should verify");
        assert_eq!(verified.key_id, "producer-20260804-a");
        assert_eq!(
            verified.replay_hash,
            replay_hash(&envelope["events"]).unwrap()
        );
        assert_eq!(verified.signature_digest.len(), 64);
    }

    #[test]
    fn rejects_unknown_key_and_bad_signature_encoding() {
        let signing_key = generated_signing_key();
        let envelope = signed_fixture(&signing_key);
        let other = generated_signing_key();
        assert!(matches!(
            verify_benchmark_envelope(&envelope, &generated_keyring(&other)),
            Err(VerificationError::UnknownKey(_))
        ));

        let mut bad_encoding = envelope.clone();
        bad_encoding["signature"]["signature_b64"] = Value::String("%%%".to_string());
        assert!(matches!(
            verify_benchmark_envelope(&bad_encoding, &generated_keyring(&signing_key)),
            Err(VerificationError::InvalidEncoding(_))
        ));
    }

    #[test]
    fn rejects_tampering_and_re_signed_hash_mismatch() {
        let signing_key = generated_signing_key();
        let mut tampered = signed_fixture(&signing_key);
        tampered["events"][0]["details"]["suite"] = Value::String("tampered".to_string());
        assert!(matches!(
            verify_benchmark_envelope(&tampered, &generated_keyring(&signing_key)),
            Err(VerificationError::InvalidSignature)
        ));

        let mut hash_mismatch = signed_fixture(&signing_key);
        hash_mismatch["result"]["replay_hash"] = Value::String("b".repeat(64));
        resign(&mut hash_mismatch, &signing_key);
        assert!(matches!(
            verify_benchmark_envelope(&hash_mismatch, &generated_keyring(&signing_key)),
            Err(VerificationError::ReplayHashMismatch { .. })
        ));
    }

    #[test]
    fn canonical_bytes_sort_keys_without_ascii_escaping() {
        assert_eq!(
            canonical_json_bytes(&serde_json::json!({"z": "mu", "a": "αλφα"})),
            "{\"a\":\"αλφα\",\"z\":\"mu\"}".as_bytes()
        );
    }
}
