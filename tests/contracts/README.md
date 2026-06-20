# API Contract Testing

This directory contains contract tests for the TraceRTM API using Pact.

## Overview

Contract testing ensures that the API provider (Go backend) and consumers (TypeScript frontend, CLI, MCP) agree on the API contract. This catches integration issues early without requiring full integration tests.

## Architecture

```
tests/contracts/
├── consumer/           # Frontend consumer tests
│   ├── auth/          # Authentication contracts
│   ├── projects/      # Project management contracts
│   ├── items/         # Item management contracts
│   ├── graph/         # Graph analysis contracts
│   ├── specs/         # Specification contracts
│   └── ...
├── provider/          # Backend provider tests
│   └── provider_test.go
├── pacts/             # Generated pact files
│   └── *.json
├── versions/          # Contract versions by release
└── docs/              # Contract documentation

## Framework: Pact

We use [Pact](https://pact.io/) for consumer-driven contract testing:

- **Consumer**: TypeScript frontend generates contract expectations
- **Provider**: Go backend verifies it meets the contract
- **Pact Broker**: (Optional) Centralized contract management

## Directory Structure

### Consumer Tests (`consumer/`)

Consumer tests are written in TypeScript using `@pact-foundation/pact`:

```typescript
// Example: consumer/auth/login.contract.test.ts
import { pact } from '@pact-foundation/pact';

describe('Auth Login Contract', () => {
  it('should login with valid credentials', async () => {
    await provider.addInteraction({
      state: 'user exists',
      uponReceiving: 'a login request',
      withRequest: {
        method: 'POST',
        path: '/api/v1/auth/login',
        body: { email: 'user@example.com', password: 'password' }
      },
      willRespondWith: {
        status: 200,
        body: { token: like('abc123'), user: { id: like('uuid') } }
      }
    });
  });
});
```

### Provider Tests (`provider/`)

Provider tests are written in Go using `github.com/pact-foundation/pact-go/v2`:

```go
// Example: provider/provider_test.go
func TestProviderContracts(t *testing.T) {
    verifier := &pact.Verifier{
        Provider:        "TraceRTM-API",
        ProviderVersion: version.Get().GitVersion,
        PactFiles:       []string{"../pacts/*.json"},
    }

    err := verifier.VerifyProvider(t)
    assert.NoError(t, err)
}
```

## Running Tests

### Consumer Tests (Frontend)

```bash
# Run all consumer contract tests
cd frontend/apps/web
bun run test:contracts

# Run specific domain
bun run test:contracts auth
bun run test:contracts projects

# Generate pacts
bun run test:contracts:generate
```

### Provider Tests (Backend)

```bash
# Run provider verification
cd backend
make test-contracts

# Verify against specific pact
go test -v ./tests/contracts/provider -pact=auth

# Verify all pacts
go test -v ./tests/contracts/provider
```

### CI/CD Integration

Contract tests run in CI/CD:

1. **PR Stage**: Consumer tests generate pacts
2. **Verification Stage**: Provider verifies pacts
3. **Publish Stage**: Pacts published to broker (if configured)

```yaml
# .github/workflows/contracts.yml
- name: Run Consumer Tests
  run: cd frontend/apps/web && bun run test:contracts:generate

- name: Verify Provider
  run: cd backend && make test-contracts
```

## Contract Versioning

Contracts are versioned by release:

```
versions/
├── v1.0.0/
│   ├── auth-contracts.json
│   ├── projects-contracts.json
│   └── ...
├── v1.1.0/
│   └── ...
└── current -> v1.1.0/
```

### Breaking Changes

Breaking changes require:

1. New major version
2. Deprecation notice in previous version
3. Migration guide

## Coverage Goals

- **Target**: 100% API endpoint coverage
- **Current**: 70 endpoints
- **Status**: See [coverage report](./docs/coverage.md)

### Coverage by Domain

| Domain | Endpoints | Consumer Tests | Provider Tests | Status |
|--------|-----------|----------------|----------------|--------|
| Auth | 7 | ✅ | ✅ | Complete |
| Projects | 12 | ✅ | ✅ | Complete |
| Items | 15 | ✅ | ✅ | Complete |
| Graph | 10 | ✅ | ✅ | Complete |
| Specs | 8 | ✅ | ✅ | Complete |
| Workflows | 6 | ✅ | ✅ | Complete |
| Others | 12 | ✅ | ✅ | Complete |
| **Total** | **70** | **70** | **70** | **100%** |

## Best Practices

### 1. Consumer Tests

- **One interaction per test**: Each test should verify one API interaction
- **Use matchers**: Use `like()`, `eachLike()` for flexible matching
- **Provider states**: Define clear provider states for setup
- **Realistic data**: Use realistic test data, not minimal examples

### 2. Provider Tests

- **State handlers**: Implement provider state handlers for setup
- **Version verification**: Always verify against tagged consumer versions
- **Database state**: Use transactions or fixtures for consistent state

### 3. Maintenance

- **Review contracts**: Review contract changes in PRs
- **Document changes**: Document breaking changes in CHANGELOG.md
- **Clean old contracts**: Archive contracts from deprecated APIs

## Troubleshooting

### Consumer Test Failures

```bash
# Check mock server logs
bun run test:contracts -- --verbose

# Clear pact cache
rm -rf frontend/apps/web/pacts/*
```

### Provider Verification Failures

```bash
# Run with verbose output
go test -v ./tests/contracts/provider -args -verbose

# Check provider state
go test -v ./tests/contracts/provider -args -debug-states

# Verify single interaction
go test -v ./tests/contracts/provider -run TestProviderContracts/auth_login
```

### Common Issues

1. **Port conflicts**: Ensure mock server port is available (default: 8080)
2. **Provider state**: Ensure provider state handlers are implemented
3. **Version mismatch**: Check consumer and provider Pact library versions

## Resources

- [Pact Documentation](https://docs.pact.io/)
- [Pact Go](https://github.com/pact-foundation/pact-go)
- [Pact JS](https://github.com/pact-foundation/pact-js)
- [OpenAPI Spec](../frontend/apps/web/public/specs/openapi.json)

## Contract Examples

See [examples/](./docs/examples/) for complete contract examples:

- [Authentication Flow](./docs/examples/auth-flow.md)
- [CRUD Operations](./docs/examples/crud-operations.md)
- [Error Handling](./docs/examples/error-handling.md)
- [Pagination](./docs/examples/pagination.md)
