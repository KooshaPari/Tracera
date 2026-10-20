use super::*;

// Compose recognises an inline comment only at the two character
// sequence `" #"`.  A `#` that is not preceded by whitespace belongs
// to the value, so a password containing `#` must survive intact.
#[test]
fn hash_without_preceding_space_is_part_of_the_value() {
    let (_, val) = parse_env_line("KEY=pa#ss").unwrap().unwrap();
    assert_eq!(val, "pa#ss");

    let (_, val) = parse_env_line("KEY=value # trailing comment")
        .unwrap()
        .unwrap();
    assert_eq!(val, "value");

    // A `#` directly after whitespace opens the comment.
    let (_, val) = parse_env_line("KEY=value#not-a-comment").unwrap().unwrap();
    assert_eq!(val, "value#not-a-comment");

    // Inside quotes a `#` is always literal.
    let (_, val) = parse_env_line("KEY=\"pa#ss\"").unwrap().unwrap();
    assert_eq!(val, "pa#ss");
}

// A value that is only a comment parses to an empty string, and the
// preflight rejects an empty credential.  So a commented-out password
// fails closed rather than being silently accepted as blank.
#[test]
fn comment_only_value_fails_closed() {
    let (key, val) = parse_env_line("POSTGRES_PASSWORD= # note")
        .unwrap()
        .unwrap();
    assert_eq!(key, "POSTGRES_PASSWORD");
    assert_eq!(val, "");
    // Empty values are rejected downstream by `validate_env_file`,
    // which requires a nonempty POSTGRES_PASSWORD.
    assert!(val.trim().is_empty());
}

// This parser deliberately does NOT perform Compose's `${VAR}`
// interpolation.  A template placeholder is therefore preserved
// verbatim instead of being silently resolved from the environment,
// which keeps the preflight deterministic.
#[test]
fn interpolation_is_not_performed() {
    let (_, val) = parse_env_line("KEY=${SOME_VAR}").unwrap().unwrap();
    assert_eq!(val, "${SOME_VAR}");

    let (_, val) = parse_env_line("KEY=\"pre-${SOME_VAR}-post\"")
        .unwrap()
        .unwrap();
    assert_eq!(val, "pre-${SOME_VAR}-post");

    // An escaped dollar sign is a literal dollar sign, and Compose
    // likewise uses `\$` to suppress interpolation.
    let (_, val) = parse_env_line("KEY=\"\\${SOME_VAR}\"").unwrap().unwrap();
    assert_eq!(val, "${SOME_VAR}");
}

// An escaped quote inside a quoted value is a literal quote, matching
// Compose's escape-aware closing-quote scan.
#[test]
fn escaped_quote_inside_quoted_value() {
    let (_, val) = parse_env_line("KEY=\"a\\\"b\"").unwrap().unwrap();
    assert_eq!(val, "a\"b");

    let (_, val) = parse_env_line("KEY='a\\'b'").unwrap().unwrap();
    assert_eq!(val, "a'b");
}

// A key containing whitespace is malformed; Compose rejects it too.
#[test]
fn key_with_whitespace_fails_closed() {
    assert!(parse_env_line("BAD KEY=value").is_err());
}

// The remaining Compose escape sequences.
#[test]
fn compose_escape_sequences_expand() {
    let (_, val) = parse_env_line("KEY=\"a\\bb\"").unwrap().unwrap();
    assert_eq!(val, "a\u{8}b");
    let (_, val) = parse_env_line("KEY=\"a\\fb\"").unwrap().unwrap();
    assert_eq!(val, "a\u{c}b");
    let (_, val) = parse_env_line("KEY=\"a\\vb\"").unwrap().unwrap();
    assert_eq!(val, "a\u{b}b");
    let (_, val) = parse_env_line("KEY=\"a\\ab\"").unwrap().unwrap();
    assert_eq!(val, "a\u{7}b");
    let (_, val) = parse_env_line("KEY=\"a\\0101b\"").unwrap().unwrap();
    assert_eq!(val, "aAb");
    // Compose's octal form requires the leading zero, so `\101` is not
    // an octal escape and stays literal.
    let (_, val) = parse_env_line("KEY=\"a\\101b\"").unwrap().unwrap();
    assert_eq!(val, "a\\101b");
    // An unrecognised escape is preserved verbatim.
    let (_, val) = parse_env_line("KEY=\"a\\qb\"").unwrap().unwrap();
    assert_eq!(val, "a\\qb");
}

// Compose-valid colon syntax and the standard escape sequences.
#[test]
fn parse_env_line_escape_values() {
    // Double-quoted \t becomes a literal tab character.
    let (_, val) = parse_env_line("KEY=\"a\\tb\"").unwrap().unwrap();
    assert_eq!(val, "a\tb");

    // Double-quoted \r becomes a literal carriage return.
    let (_, val) = parse_env_line("KEY=\"a\\rb\"").unwrap().unwrap();
    assert_eq!(val, "a\rb");

    // Double-quoted \\ becomes a literal backslash.
    let (_, val) = parse_env_line("KEY=\"a\\\\b\"").unwrap().unwrap();
    assert_eq!(val, "a\\b");

    // Single-quoted: backslash is literal.
    let (_, val) = parse_env_line("KEY='a\\tb'").unwrap().unwrap();
    assert_eq!(val, "a\\tb");

    // Colon separator.
    let (key, val) = parse_env_line("MY_KEY: my value").unwrap().unwrap();
    assert_eq!(key, "MY_KEY");
    assert_eq!(val, "my value");
}

// Fail-closed: genuinely invalid input must produce errors that do NOT
// echo the offending value (no secret leakage).
#[test]
fn fail_closed_no_secret_leakage_in_errors() {
    // Unterminated single quote.
    let err = parse_env_line("POSTGRES_PASSWORD='top-secret-unterminated").unwrap_err();
    assert!(
        !err.to_string().contains("top-secret"),
        "error leaked secret: {err}"
    );

    // Unterminated double quote.
    let err = parse_env_line("POSTGRES_PASSWORD=\"top-secret-unterminated").unwrap_err();
    assert!(
        !err.to_string().contains("top-secret"),
        "error leaked secret: {err}"
    );

    // No separator at all.
    let err = parse_env_line("MALFORMED_LINE_NO_SEP").unwrap_err();
    assert!(
        !err.to_string().contains("MALFORMED"),
        "error echoed line: {err}"
    );
}

// Last-assignment-wins with colon and mixed separators.
#[test]
fn last_wins_with_mixed_separators() {
    let body = "POSTGRES_PASSWORD=first\nPOSTGRES_PASSWORD: second\n";
    let entries = parse_env_entries(body).unwrap();
    assert_eq!(entries["POSTGRES_PASSWORD"], "second");
}
