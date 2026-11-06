# Independent static review

Reviewer: /root/tracera_d04_contract_review, 2026-10-19T00:55Z.
Fresh reread confirmed Windows create_new fix; no remaining blocking static findings for narrowly scoped nonclobber/status-readonly contract. Parser compatibility and Windows execution remain limitations.

Executed validation at the time of this review: isolated source CLI 11 unit tests and seven disposable blackbox cases. Binary built before the Windows-only cfg change (historical, superseded below): SHA256 d29a875f7a0a746c649ced7a74d59e3d1f48ae53ba4989076aa2ae03e98ab9af. Windows cfg change does not execute on macOS; Windows target was not compiled.

Reproduce: cargo test with the tracera-cli crate (workspace dependency availability required); python3 docs/sessions/20261018-d04-preflight/fixture_probe.py /absolute/path/to/tracera.

No existing Desk configuration was read or changed. No backend service started. No installed binary equivalence verified. SSH to 100.96.135.160:22 timed out.

Follow-up (historical, superseded below): exact workspace `cargo test -p tracera-cli --locked --offline` PASS 13/13; `cargo build -p tracera-cli --locked --offline` PASS. Own CARGO_TARGET_DIR=/tmp/tracera-d04-cli-test/target; SDK26/system clang. At that point Compose syntax compatibility was an observed FAIL; no production-complete claim was made.

Historical binary SHA256: 5e6e370227d4ec9f5a88186ea50e230bd30fcafb2a4b438dcb4a7e90ea6e2d23, with seven fixture cases PASS. Current authoritative values are in STATUS.json (`binary_sha256` and `qualified_source_sha`); the numbers below supersede this line.

Compatibility oracle: Docker official env-file syntax https://docs.docker.com/compose/how-tos/environment-variables/variable-interpolation/#env-file-syntax supports colon separators, double-quoted escapes, and `${VAR}` interpolation. Closure was required to accept the non-secret positive fixtures without changing file bytes while retaining the malformed/empty negative cases. The declaration subset is now closed (see the hardening pass below); interpolation remains deliberately unimplemented and is excluded from the intent's claim.

## 2026-10-19 hardening pass

Reviewer: jcode agent, 2026-10-19T22:07Z, revised 2026-10-20T00:10Z.

Replaced dotenvy with a custom Compose-compatible parser. The parser now lives in
`crates/tracera-cli/src/env_file.rs` (197 lines) with its tests in
`crates/tracera-cli/src/env_file/tests.rs` (156 lines), so neither file exceeds the
350-line target. The parser accepts:

- Colon and equals separators (`KEY: value`, `KEY=value`)
- Double-quoted escape sequences (`\a`, `\b`, `\c`, `\f`, `\n`, `\r`, `\t`, `\v`,
  `\\`, `\"`, `\$`, and octal `\0NNN`)
- Single-quoted literal values, with an escape-aware closing-quote scan so that
  `KEY='a\'b'` yields `a'b` rather than truncating
- `export` prefix
- Inline comments recognised only at the two character sequence `" #"`, matching
  Docker Compose, so `POSTGRES_PASSWORD=pa#ss` keeps its `#`
- Last-assignment-wins for duplicate keys, including mixed `=` and `:` separators

Verified on the current tree: `cargo test -p tracera-cli --offline --locked` PASS
26/26 and `cargo test --workspace --offline --locked` PASS 398/398 (1 ignored),
both captured in `unit-tests.log` and `workspace-tests.log`.
`cargo clippy -p tracera-cli --offline --all-targets -- -D warnings` is clean and
`cargo fmt -p tracera-cli -- --check` is clean. Fail-closed property verified:
unterminated quotes and malformed lines do not echo secret values.

Scope boundary: the parser does **not** perform `${VAR}` interpolation, which
Docker Compose does implement. `env_file::tests::interpolation_is_not_performed`
pins that a placeholder is preserved verbatim. The intent is therefore named
"Compose-valid dotenv declaration syntax (interpolation excluded)"; it is not a
claim of full Compose env-file parity. A key containing whitespace is rejected,
and a comment-only value parses to an empty string that `validate_env_file` then
rejects, so a commented-out credential fails closed.

STATUS.json and STATUS.md updated to these figures. Desk readiness unchanged
(UNKNOWN/NOT_RUN).

Python files `render_status.py` and `fixture_probe.py` pass `ruff check` and
`ruff format --check`. `STATUS.md` is regenerated from `STATUS.json` and the
render output is itself Prettier-clean, so regenerating it does not break the
format gate.
