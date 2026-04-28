# Backend lint fixes checklist (mnd, noctx, nolintlint, perfsprint)

Apply in the **backend** repo. See `REVIVE_FIX_REFERENCE.md` for pattern details.

**Note:** The full linter output contains hundreds of mnd reports and many perfsprint/noctx/nolintlint items across `internal/`, `cmd/`, and `main.go`. This doc lists representative fixes; for bulk work, run the linter per package and apply the patterns from `REVIVE_FIX_REFERENCE.md` (mnd strategy, noctx API swaps, nolint removal/format, perfsprint replacements).

## mnd (Magic number)

| File | Line | Change |
|------|------|--------|
| main.go | 129 | Replace `6` with a const (e.g. `preflightMaxAttempts = 6`). |
| main.go | 233 | Replace `10*time.Second` with a const (e.g. `requestTimeout = 10 * time.Second`). |

## noctx (context-aware APIs)

| File | Line | Change |
|------|------|--------|
| cmd/build/main.go | 62, 72, 82 | Use `exec.CommandContext(ctx, "pip", ...)` etc. Pass context from caller or `context.Background()`. |
| cmd/nats-test-diagnostic/main.go | 145 | Use `net.DefaultResolver.LookupIPAddr(ctx, "ip", host)` (or custom resolver). |
| cmd/synadia-api-test/main.go | 56 | Use `http.NewRequestWithContext(ctx, "GET", endpoint, nil)`. |
| internal/auth/token_bridge.go | 264 | Build `req` with `NewRequestWithContext`, then `tb.jwksClient.Do(req)`. |
| internal/autoupdate/autoupdate.go | 73, 104 | Same: `NewRequestWithContext` + `client.Do(req)`. |
| internal/grpc/server.go | 340 | Use `(&net.ListenConfig{}).Listen(ctx, "tcp", addr)`. |
| internal/handlers/temporal_handler_test.go | 198, 201 | Use `http.NewRequestWithContext(ctx, method, path, body)`. |
| internal/preflight/preflight.go | 196 | Use `net.Dialer{Timeout: timeout}.DialContext(ctx, "tcp", addr)`. |
| internal/resilience/retry_test.go | 256, 286, 339 | Use `http.NewRequestWithContext(ctx, "GET", ...)`. |

## nolintlint

| File | Change |
|------|--------|
| internal/config/config_test.go | Remove all `//nolint:errcheck` (and similar) on `os.Setenv`/`os.Unsetenv` lines if the linter reports them as unused; or fix directive to match the linter actually run on that line. |
| internal/handlers/search_handler_test.go | Fix format: `// nolint:unused` → `//nolint:unused` (no space after `//`). |

## perfsprint (by file)

- **cmd/nats-test-diagnostic/main.go:158** — `fmt.Sprintf("%d", port)` → `strconv.Itoa(port)`.
- **cmd/package/main.go:85** — `fmt.Sprintf("dist/tracertm-%s", version)` → `"dist/tracertm-" + version`.
- **cmd/setup/main.go** — All `fmt.Errorf("...")` with no format verbs → `errors.New("...")` (87, 143, 212, 218, 224, 230).
- **cmd/synadia-api-test/main.go:62** — `fmt.Sprintf("Bearer %s", pat)` → `"Bearer " + pat`.
- **internal/adapters/factory.go** — All listed `fmt.Errorf` → `errors.New` (63, 66, 83, 89).
- **internal/agents/coordination.go:432** — `fmt.Errorf` → `errors.New`.
- **internal/agents/distributed_coordination.go:96, 142** — `fmt.Errorf` → `errors.New`.
- **internal/auth/api_keys.go** — All listed `fmt.Errorf` → `errors.New`.
- **internal/auth/authkit_adapter.go** — JWKS URL: `"https://api.workos.com/sso/jwks/" + clientID`; other `fmt.Errorf` → `errors.New`.
- **internal/auth/bridge_adapter.go, password.go, token_bridge.go** — All listed `fmt.Errorf` → `errors.New`.
- **internal/autoupdate/autoupdate_test.go** — Line 179: `strconv.Itoa(tc.statusCode)`; 521–522: string concat for `"os="+runtime.GOOS` and `"arch="+runtime.GOARCH`.
- **internal/cache/cache_middleware.go** — Line 207: `hex.EncodeToString(hash)`; 209, 216: string concat.
- **internal/cache/redis_cache.go** — All `fmt.Sprintf("project:%s", ...)` style → `"project:" + projectID` etc.
- **internal/cache/redis_coverage_test.go** — Concat loop: use `strings.Builder`; line 714: `strconv.Itoa(i)`.
- **internal/cache/redis_error_handling_test.go** — Concat loop: use `strings.Builder`.
- **internal/clients/chaos_client.go, execution_client.go, workflow_client.go** — Replace `fmt.Errorf` / `fmt.Sprintf` with `errors.New` and string concat as listed.
- **internal/clients/python_client.go:91** — `errors.New`.
- **internal/clients/spec_analytics_client.go:176** — `hex.EncodeToString(h.Sum(nil)[:16])`.
- **internal/cliproxy/config.go** — `errors.New` for host/provider errors; `b.WriteString("CLIProxy Config:\n")` (no Sprintf).
- **internal/cliproxy/service.go** — `errors.New` and `"unknown provider: " + provider` (or keep Sprintf if you need to satisfy an error type that requires formatting).
- **internal/codeindex/integration_test.go:359** — Concat in loop → `strings.Builder`.
- **internal/codeindex/linker.go:105** — `"Matched pattern: " + pattern.Name`.

Ensure imports: `errors`, `strconv`, `encoding/hex`, `strings` where used.

---

## Bulk mnd (magic number) – priority order

When fixing hundreds of mnd reports, tackle in this order:

1. **Entrypoints:** `main.go` (e.g. preflight 6, timeout 10s), `cmd/build/main.go`, `cmd/setup/main.go`, `cmd/package/main.go`, `cmd/synadia-api-test/main.go`, `cmd/nats-test-diagnostic/main.go`. Use named constants for attempts, timeouts, and buffer sizes.
2. **noctx (do these with context):** All noctx locations from the reference (exec, LookupIP, NewRequest, Client.Get, Listen, DialTimeout). Fix these so context propagates; then you can keep or name any timeouts used there.
3. **Config and connection defaults:** `internal/config/`, `internal/database/connection_pool.go`, `internal/preflight/preflight.go`. Centralize defaults (e.g. `DefaultPreflightTimeout`, `DefaultDBMaxConns`) in one place and reference them.
4. **Timeouts and limits in services:** `internal/services/*.go`, `internal/clients/*.go`, `internal/handlers/*.go`. Replace repeated `2*time.Second`, `5*time.Minute`, `Limit: 500` with package or file constants.
5. **Confidence/threshold literals:** In `internal/codeindex/`, `internal/docindex/`, `internal/equivalence/`, many `0.9`, `0.95`, `0.7` etc. Add a small `const` block per package (e.g. `DefaultConfidenceHigh = 0.95`) and use those names.
6. **Tests:** Either add constants for test data (e.g. `const wantLen = 2`) or configure mnd to ignore `*_test.go` so assertion literals and test-only values don’t need constants.
