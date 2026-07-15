use std::env;

#[derive(Debug)]
pub(super) enum SigningMode {
    Hs256(String),
    Rs256(String),
}

#[derive(Debug)]
pub(super) struct AuthConfig {
    pub(super) audience: String,
    pub(super) issuer: String,
    pub(super) signing: SigningMode,
}

impl AuthConfig {
    pub(super) fn from_env() -> Result<Self, String> {
        Self::from_values(
            env::var("TRACERA_JWT_AUDIENCE").ok(),
            env::var("TRACERA_JWT_ISSUER").ok(),
            env::var("TRACERA_JWT_SECRET").ok(),
            env::var("TRACERA_JWT_PUBLIC_KEY").ok(),
        )
    }

    pub(super) fn from_values(
        audience: Option<String>,
        issuer: Option<String>,
        secret: Option<String>,
        public_key: Option<String>,
    ) -> Result<Self, String> {
        let audience = required_value("TRACERA_JWT_AUDIENCE", audience)?;
        let issuer = required_value("TRACERA_JWT_ISSUER", issuer)?;
        let secret = non_empty(secret);
        let public_key = non_empty(public_key).map(|value| value.replace("\\n", "\n"));

        let signing = match (secret, public_key) {
            (Some(secret), None) => {
                if secret.as_bytes().len() < 32 {
                    return Err("TRACERA_JWT_SECRET must contain at least 32 bytes".to_string());
                }
                SigningMode::Hs256(secret)
            }
            (None, Some(public_key)) => SigningMode::Rs256(public_key),
            (Some(_), Some(_)) | (None, None) => {
                return Err(
                    "configure exactly one of TRACERA_JWT_SECRET or TRACERA_JWT_PUBLIC_KEY"
                        .to_string(),
                );
            }
        };

        Ok(Self {
            audience,
            issuer,
            signing,
        })
    }
}

fn required_value(name: &str, value: Option<String>) -> Result<String, String> {
    non_empty(value).ok_or_else(|| format!("{name} must be configured"))
}

fn non_empty(value: Option<String>) -> Option<String> {
    value.and_then(|value| {
        let value = value.trim().to_string();
        (!value.is_empty()).then_some(value)
    })
}
