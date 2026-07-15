use serde::Deserialize;

#[derive(Debug, Deserialize)]
pub(super) struct Claims {
    pub(super) sub: String,
    #[allow(dead_code)]
    exp: usize,
    #[allow(dead_code)]
    iss: String,
    #[allow(dead_code)]
    aud: String,
    #[serde(default)]
    pub(super) scope: String,
    #[serde(default)]
    pub(super) permissions: Vec<String>,
}
