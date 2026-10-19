# D04 preflight evidence tree

Generated: 2026-10-19T00:55:43.622006+00:00

Rendered from STATUS.json; no runtime promotion.

```
Non-clobbering preflight
  Implementation: PASS | env_config.rs; commands.rs; bundle.rs; compose.rs
  Usability: PASS | fixture-results.json: seven fake-backend cases
  Validation: PASS | unit-tests.log: 11 passed; fixture-results.json
  Assurance: UNKNOWN | Windows cfg block not cross-compiled; isolated dependencies differ workspace lock
Actual Desk readiness
  Implementation: UNKNOWN | installed binary/source equivalence unverified
  Usability: UNKNOWN | SSH 100.96.135.160 port22 timed out
  Validation: NOT_RUN | scope prohibits Desk root commands and starts
  Assurance: UNKNOWN | no fresh remote metadata
```

Owned disposable nonsecret fixtures only; fake Docker is a side-effect guard, not runtime qualification.
No environment values read. SSH metadata command timed out. No actual Desk root CLI executed.
No baseline executable RED; base source establishes old mutation behavior.
Isolated source build uses cached dependency resolution, not workspace-locked dependencies.
dotenvy validates supported dotenv syntax, not complete Compose grammar: colon separators and some double-quoted escapes may fail closed without changing bytes.
Windows create_new branch statically reviewed only; no Windows runtime qualification.
Compute: on device, isolated CLI only; no shared process kills or backend starts.
