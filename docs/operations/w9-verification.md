# W9 local verification

Worktree: `C:\Users\koosh\Tracera-w9-unresolved-worker`.
Branch: `stubs/w9-unresolved-worker-20261016`.
Base: `2c871ff0e` from `origin/main` in `KooshaPari/Tracera`.
Compute placement: all on device, with `CARGO_BUILD_JOBS=2` for Rust gates.

| Exact required command                                     | Exit | Result                                 |
| ---------------------------------------------------------- | ---- | -------------------------------------- |
| `cargo fmt --check`                                        | 0    | Passed                                 |
| `cargo check --workspace --tests --locked`                 | 0    | Passed after final route-module layout |
| `cargo clippy --all-targets --all-features -- -D warnings` | 0    | Passed                                 |
| `cargo test -p tracera-server --locked`                    | 0    | Passed                                 |

Server test output:

```text
test result: ok. 107 passed; 0 failed; 0 ignored
test result: ok. 87 passed; 0 failed; 0 ignored
test result: ok. 4 passed; 0 failed; 0 ignored
test result: ok. 0 passed; 0 failed; 1 ignored (doctest)
```

The binary tests include the integrated 264-template / five-method 501 contract,
the existing project mutation and organization metric corrections, and the
unknown-route 404 negative control. Contract fixtures use migrated SQLite.

Additional commands:

```text
C:/Users/koosh/.bun/bin/bun.exe install --frozen-lockfile --ignore-scripts
  cwd: frontend; exit 0
C:/Users/koosh/.bun/bin/bun.exe test scripts/w9-contract.test.ts scripts/honest-gateway.test.ts
  cwd: repository root; exit 0; 400 passed, 0 failed
C:/Users/koosh/.bun/bin/bun.exe run test src/components/W9Unavailable.test.tsx src/api/availability.test.tsx src/hooks/useNotifications.availability.test.tsx src/views/projects-list/UnavailableProjectMutation.test.tsx --pool=threads --maxWorkers=1
  cwd: frontend/apps/web; exit 0; 36 passed, 0 failed (4 files)
```

UI verification uses the web app's Vitest script with one thread worker. The
default fork pool could not start workers on this host; it did not run tests.
This receipt covers local validation, not hosted CI, deployment, or runtime
acceptance. The docs-3 dossier was absent locally. No merge was performed.
