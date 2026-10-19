# D04 preflight evidence tree

Generated: 2026-10-19T02:31:20.878007+00:00

Rendered from STATUS.json; no runtime promotion.

```
Non-clobbering preflight
  Implementation: PASS | env_config.rs; commands.rs; bundle.rs; compose.rs
  Usability: PASS | fixture-results.json: seven fake-backend cases
  Validation: PASS | workspace-tests.log: locked workspace 13/13; workspace-build.log; fixture-results.json:7/7
  Assurance: PASS | REVIEW.md independent static scope; locked workspace receipts. Windows execution excluded
Compose-valid dotenv syntax parity
  Implementation: FAIL | env_config.rs unsupported_compose_syntax_fails_closed_preserving_bytes: colon and double-quoted tab/carriage-return rejected
  Usability: FAIL | workspace-tests.log unsupported_compose_syntax_fails_closed_preserving_bytes; valid files rejected without writes
  Validation: PASS | workspace-tests.log: explicit regression witness executed
  Assurance: PASS | REVIEW.md: independent parser limitation review
Actual Desk readiness
  Implementation: UNKNOWN | installed binary/source equivalence unverified
  Usability: UNKNOWN | SSH 100.96.135.160 port22 timed out
  Validation: NOT_RUN | scope prohibits Desk root commands and starts
  Assurance: UNKNOWN | no fresh remote metadata
```

Owned disposable nonsecret fixtures only; fake Docker is a side-effect guard, not runtime qualification.
No environment values read. SSH metadata command timed out. No actual Desk root CLI executed.
No baseline executable RED; base source establishes old mutation behavior.
dotenvy validates supported dotenv syntax, not complete Compose grammar: colon separators and some double-quoted escapes may fail closed without changing bytes.
Windows create_new branch statically reviewed only; no Windows runtime qualification.
Compute: on device, isolated CLI only; no shared process kills or backend starts.
Exact workspace --locked --offline CLI test/build passed using isolated owned CARGO_TARGET_DIR; 13 unit tests and seven fake-backend fixtures. No production-complete claim; Compose syntax parity fails known cases.
