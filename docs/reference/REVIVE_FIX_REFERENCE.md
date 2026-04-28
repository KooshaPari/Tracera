# Revive Lint Fix Reference

Use this when running `golangci-lint run` (or revive) from the **backend** directory. The paths below are relative to the backend root (e.g. `backend/internal/...`).

## Quick fixes by rule

### unused-parameter
Rename the parameter to `_` so the signature stays compatible (e.g. interface impls).

```go
// Before
func (m *Mock) Do(ctx context.Context, id string) error {

// After
func (m *Mock) Do(_ context.Context, id string) error {
```

### package-comments
Add a one-line package comment at the top of the file.

```go
// Package sync provides GitHub and file sync for the code index.
package sync
```

### exported (exported type/function/const should have comment)
Add a godoc comment in the form `// Name ...` (or block comment for const groups).

```go
// Config holds application configuration.
type Config struct { ... }

// LoadConfig loads configuration from environment/files.
func LoadConfig() *Config { ... }
```

### exported (type name stutters; consider calling this X)
Rename the type so it doesn’t repeat the package name when used as `pkg.TypeName`.

- `sync.SyncResult` → `sync.Result`
- `sync.SyncFileResult` → `sync.FileResult`
- `config.Config` → keep as is or document; often kept for clarity.
- Same idea for `export.ExportFormat` → `export.Format`, etc.

Update all references and call sites after renaming.

### var-naming
- Struct field: `RedisUrl` → `RedisURL` (acronyms all caps).
- Test names: `TestNewIndexer_Defaults_Additional` → `TestNewIndexerDefaultsAdditional` (no underscores in Go names).

### blank-imports
Add a comment justifying the blank import.

```go
import (
    _ "github.com/lib/pq" // PostgreSQL driver
)
```

### empty-block
Either remove the block or add a single-line comment + keep the block; avoid completely empty blocks.

```go
// Before
if err != nil {
}

// After (if you want to ignore)
if err != nil {
    // ignore error
}
// Or remove the if if there's no side effect needed.
```

### context-keys-type
Don’t use a raw string as context key. Use a custom type.

```go
type contextKey string
const projectContextKey contextKey = "project_context"
ctx = context.WithValue(ctx, projectContextKey, value)
```

### redefines-builtin-id
Rename the variable that shadows a builtin (e.g. `new`).

```go
// Before
func CompareNodeVersions(old *Node, new *Node) SyncComparison {

// After
func CompareNodeVersions(old, newVer *Node) SyncComparison {
```

### comment form (exported comment should be "Name ...")
Use the exact symbol name at the start of the comment.

```go
// GitDeltaSync performs incremental sync based on git changes.
func SyncWithGit(...) { ... }
```

### perfsprint (error-format, string-format, integer-format, hex-format, concat-loop)

- **error-format:** When the message has no format verbs, use `errors.New` instead of `fmt.Errorf`.
  - `return fmt.Errorf("item ID is required")` → `return errors.New("item ID is required")` (add `"errors"` to imports).
- **string-format:** Simple `fmt.Sprintf("prefix:%s", x)` with one `%s` → use concatenation: `"prefix:" + x`. For no format args at all, use the string literal: `fmt.Sprintf("CLIProxy Config:\n")` → `"CLIProxy Config\n"`.
- **integer-format:** `fmt.Sprintf("%d", n)` → `strconv.Itoa(n)` (add `"strconv"` to imports). For int64 use `strconv.FormatInt(n, 10)`.
- **hex-format:** `fmt.Sprintf("%x", data)` → `hex.EncodeToString(data)` (add `"encoding/hex"` to imports).
- **concat-loop:** String concatenation in a loop → use `var b strings.Builder` and `b.WriteString(...)`, then `b.String()`.

### mnd (Magic number)

Replace naked numeric literals in arguments/assignments with named constants (e.g. at package or file level).

```go
// Before
preflight.RunWithPoll(ctx, checks, names, 6, 2*time.Second)
context.WithTimeout(ctx, 10*time.Second)

// After
const preflightMaxAttempts = 6
const preflightPollInterval = 2 * time.Second
const requestTimeout = 10 * time.Second
preflight.RunWithPoll(ctx, checks, names, preflightMaxAttempts, preflightPollInterval)
context.WithTimeout(ctx, requestTimeout)
```

**Bulk strategy when there are hundreds of mnd reports:**

1. **Fix high-value ones first:** Timeouts, limits, buffer sizes, and config defaults (e.g. `10*time.Second`, `Limit: 500`, `1024` dimensions). Define package-level or file-level constants and use them.
2. **Domain literals:** Regex group counts (e.g. `len(matches) >= 2`), percentage base (e.g. `* 100`), Unix file modes (`0o750`, `0o600`), and well-known thresholds (e.g. HTTP 400/500) can be given named constants in a small `const` block at the top of the file or in a shared `constants.go` for the package.
3. **Tests:** In test files, either define constants (e.g. `const testLimit = 50`) or relax mnd for `*_test.go` in linter config so test data literals don’t need constants.
4. **Optional config relaxation:** If the mnd linter supports it (e.g. [mnd](https://github.com/tommy-muehle/go-mnd) `ignored-numbers`), you can ignore common non-magic values (e.g. `0`, `1`, `2` for indices/counts, or `100` for percentage scale) and only enforce constants for larger or configurable values. Prefer fixing real magic numbers over disabling the rule globally.

### noctx (use context-aware APIs)

- **exec:** `exec.Command("pip", "install", "-e", ".")` → `exec.CommandContext(ctx, "pip", "install", "-e", ".")`. Pass a context (e.g. from the caller or `context.Background()` with a timeout). Run with `cmd.Run()` or `cmd.Output()` as before.
- **net.LookupIP:** Use a resolver with context: `r := &net.Resolver{}` then `r.LookupIPAddr(ctx, "ip", host)` (or use `net.DefaultResolver`). Convert `[]net.IPAddr` to `[]net.IP` if needed.
- **http.NewRequest:** `http.NewRequest("GET", url, nil)` → `http.NewRequestWithContext(ctx, "GET", url, nil)`.
- **http.Client.Get:** Build a request with `http.NewRequestWithContext(ctx, "GET", url, nil)` and call `client.Do(req)` instead of `client.Get(url)`.
- **net.Listen:** `net.Listen("tcp", addr)` → create a `net.ListenConfig` and call `lc.Listen(ctx, "tcp", addr)`.
- **net.DialTimeout:** Use `net.Dialer{Timeout: timeout}.DialContext(ctx, "tcp", addr)` instead of `net.DialTimeout("tcp", addr, timeout)`.

### nolintlint (unused or malformed nolint directives)

- **Unused directive:** If the linter says `//nolint:errcheck` is unused, either remove the directive (and fix the errcheck if needed, e.g. assign to `_` and document why) or use the correct linter name. For `os.Setenv`/`os.Unsetenv` in tests, errcheck may not be run on that line; remove the nolint if nothing is reported, or use `_ = os.Setenv(...)` and add a single file-level or block nolint if your config allows it.
- **Format:** Use no space after `//`: `//nolint:unused` not `// nolint:unused`.

### dupl (Duplicate code)

Extract the repeated logic into a shared function (or shared type + method) and call it from both places.

- **Same package:** Add a package-level helper, e.g. `func calculateExportStatistics(concepts, projections, links) ExportStatistics` in `internal/equivalence/export/` and have both JSON and YAML exporters (and service) call it instead of inlining the same block.
- **Same file:** e.g. `ImportJSON` and `ImportYAML` in equivalence import service—extract the common flow (load existing, create validator/resolver, parse, validate, apply) into `applyImportFromReader(ctx, projectID, r, opts, parseFn)` or similar; each entrypoint only provides the parser.
- **Repository row-scan loops:** Extract a `scanCanonicalConcept(rows) (CanonicalConcept, error)` (and similar for projections/milestones/sprints) and reuse in `GetByProjectID`, `GetByParent`, etc. Pass query/args from the caller.
- **Handlers:** e.g. `createSessionToken` and `extractSession`—extract shared “build session data + store in Redis + sign JWT” into a helper that both use. Temporal/journey list handlers: extract “parse query params → build filter → list + count → respond” into a shared helper parameterized by param source (query vs path).
- **Tests:** Extract a test helper (e.g. `runListProjectsTest(t, limit, offset, wantLen)`) or table-driven test so one loop covers multiple cases instead of copy-pasted test functions.
- **NATS auth:** One shared `buildNATSAuthOptions(credsPath, userJWT, userNkeySeed)` returning `[]Option`; both `NewNATSClientWithAuth` and `NewEventPublisherWithAuth` call it and then connect with their own client type.

### errcheck (Unchecked error return)

Every function that returns an error must have that return checked (handle or assign to `_` only when intentionally ignoring, with a short comment).

- **defer close:** Prefer explicit close with check. For `defer x.Close()` where the linter complains, use:
  - `defer func() { _ = x.Close() }()` and add a comment `// best-effort close`, or
  - a small helper: `defer closeAndIgnore(x)` with `func closeAndIgnore(c io.Closer) { _ = c.Close() }` in test/package.
  For `defer conn.Close(ctx)` (pgx), use `defer func() { _ = conn.Close(ctx) }()`.
- **HTTP response body:** Always close and check: `defer func() { _ = resp.Body.Close() }()` or `defer resp.Body.Close()` only if your linter allows it for `Body.Close()`; otherwise assign and check in a defer.
- **JSON encode in tests:** `_ = json.NewEncoder(w).Encode(response)` or `require.NoError(t, json.NewEncoder(w).Encode(response))`.
- **Test setup/cleanup:** In tests, either `require.NoError(t, cache.Set(...))` or `_ = cache.Set(...)` with comment. For cleanup (e.g. `defer cache.Close()`), use `defer func() { _ = cache.Close() }()` so errcheck is satisfied.
- **Intentional ignore:** Use `_ = fn()` with a one-line comment (e.g. `// best-effort cleanup`) so it’s clear the ignore is deliberate. Do not leave returns unchecked without a comment.

---

## Where to run fixes

- **This repo (trace):** Only `tests/contracts/provider/` has Go code; package comment was added.
- **Backend repo/dir:** All paths in your revive output (`internal/codeindex/`, `internal/config/`, `internal/database/`, etc.) live in the backend. Open that backend directory (or add it to the workspace) and re-run the linter there, then apply the fixes above per file.
