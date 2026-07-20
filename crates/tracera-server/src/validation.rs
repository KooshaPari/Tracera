//! Shared request-boundary validation primitives.
pub(crate) const MAX_ID_CHARS: usize = 256;
pub(crate) const MAX_SHORT_TEXT_CHARS: usize = 256;
pub(crate) const MAX_LONG_TEXT_CHARS: usize = 16 * 1024;
pub(crate) const MAX_URL_CHARS: usize = 2048;
pub(crate) const MAX_METADATA_BYTES: usize = 64 * 1024;
pub(crate) const MAX_INGEST_ISSUES: usize = 1_000;
pub(crate) fn validate_text(
    value: &str,
    field: &'static str,
    max: usize,
    required: bool,
) -> Result<(), &'static str> {
    if required && value.trim().is_empty() {
        return Err(field);
    }
    if value.chars().count() > max {
        return Err(field);
    }
    Ok(())
}
