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

#[cfg(test)]
mod tests {
    use super::validate_text;

    #[test]
    fn required_text_rejects_whitespace_only_values() {
        assert_eq!(validate_text(" \n\t", "name", 8, true), Err("name"));
    }

    #[test]
    fn optional_empty_text_is_allowed() {
        assert_eq!(validate_text("", "description", 8, false), Ok(()));
    }

    #[test]
    fn character_limit_is_unicode_safe() {
        assert_eq!(validate_text("éé", "label", 1, false), Err("label"));
        assert_eq!(validate_text("é", "label", 1, false), Ok(()));
    }
}
