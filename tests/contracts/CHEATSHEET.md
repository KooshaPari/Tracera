# Contract Testing Cheatsheet

Quick reference for common contract testing tasks.

## Commands

| Task | Command |
|------|---------|
| Run consumer tests | `cd frontend/apps/web && bun run test:contracts` |
| Run provider tests | `cd backend && make test-contracts-provider` |
| Run all tests | `cd backend && make test-contracts-all` |
| Generate coverage | `cd tests/contracts && ./scripts/generate-coverage-report.sh` |
| Watch mode | `cd frontend/apps/web && bun run test:contracts:watch` |

## Test Structure

### Consumer Test Template

```typescript
import { describe, it, beforeAll, afterAll } from 'vitest';
import {
  createPactProvider,
  setupPact,
  teardownPact,
  like,
  uuid,
  standardResponse,
  withAuth,
} from '../setup';

const provider = createPactProvider('Consumer-Name');

describe('Feature Contract', () => {
  beforeAll(async () => await setupPact(provider));
  afterAll(async () => await teardownPact(provider));

  it('should do something', async () => {
    await provider.addInteraction({
      states: [{ description: 'state description' }],
      uponReceiving: 'a request',
      withRequest: {
        method: 'GET',
        path: '/endpoint',
        headers: withAuth(),
      },
      willRespondWith: standardResponse({ data: like('value') }),
    });

    const response = await fetch('http://localhost:8080/endpoint', {
      headers: { Authorization: 'Bearer test-token' },
    });
    console.assert(response.status === 200);
  });
});
```

### Provider State Handler

```go
StateHandlers: provider.StateHandlers{
    "state description": func(setup bool, state provider.State) (provider.StateResponse, error) {
        if setup {
            // Setup test data
        } else {
            // Cleanup
        }
        return provider.StateResponse{}, nil
    },
}
```

## Matchers

| Matcher | Usage | Example |
|---------|-------|---------|
| `like()` | Type match | `like('text')` matches any string |
| `eachLike()` | Array | `eachLike({id: 1})` matches array of objects |
| `uuid()` | UUID | `uuid('123')` matches any UUID |
| `integer()` | Integer | `integer(42)` matches any integer |
| `decimal()` | Decimal | `decimal(3.14)` matches any decimal |
| `iso8601DateTime()` | DateTime | Matches ISO 8601 datetime |
| `regex()` | Regex | `regex({generate: 'abc', matcher: '^[a-z]+$'})` |

## Response Helpers

```typescript
// Standard response
standardResponse({ id: uuid('123'), name: like('Name') })

// Error response
errorResponse('Error message', 'ERROR_CODE', 400)

// Paginated response
paginatedResponse([{ id: uuid('123') }])

// With auth headers
withAuth()
```

## HTTP Methods

```typescript
// GET
withRequest: {
  method: 'GET',
  path: '/resource/123',
  headers: withAuth(),
}

// POST
withRequest: {
  method: 'POST',
  path: '/resource',
  headers: withAuth(),
  body: { name: 'New Resource' }
}

// PUT
withRequest: {
  method: 'PUT',
  path: '/resource/123',
  headers: withAuth(),
  body: { name: 'Updated' }
}

// DELETE
withRequest: {
  method: 'DELETE',
  path: '/resource/123',
  headers: withAuth(),
}
```

## Common Provider States

| State | Description |
|-------|-------------|
| `"user exists"` | Test user exists |
| `"user is authenticated"` | Valid session |
| `"resource exists"` | Resource available |
| `"resource not found"` | Resource doesn't exist |
| `"database is empty"` | No data |
| `"database is seeded with test data"` | Test fixtures loaded |

## Debugging

```bash
# Verbose consumer tests
bun run test:contracts -- --verbose

# Verbose provider tests
go test -v ./tests/contracts/provider -args -verbose

# Single test
go test -v ./tests/contracts/provider -run TestProviderContracts/auth

# Check pact files
ls -la tests/contracts/pacts/
cat tests/contracts/pacts/*.json | jq .
```

## Coverage

```bash
# Generate coverage report
cd tests/contracts
./scripts/generate-coverage-report.sh

# View coverage
cat docs/coverage.md
```

## Versioning

| Change | Version Bump |
|--------|--------------|
| Add optional field | Patch (1.0.1) |
| Add new endpoint | Minor (1.1.0) |
| Change required field | Major (2.0.0) |
| Remove endpoint | Major (2.0.0) |

## Files

| File | Purpose |
|------|---------|
| `consumer/setup.ts` | Test helpers and matchers |
| `consumer/<domain>/*.contract.test.ts` | Consumer tests |
| `provider/provider_test.go` | Provider verification |
| `pacts/*.json` | Generated contracts |
| `versions/` | Versioned contracts |
| `scripts/run-consumer-tests.sh` | Run consumer tests |
| `scripts/run-provider-tests.sh` | Run provider tests |
| `scripts/generate-coverage-report.sh` | Coverage report |

## CI/CD

Contract tests run on:
- Pull requests
- Pushes to main/develop

Workflow: `.github/workflows/contract-tests.yml`

## Resources

- [README](./README.md) - Full documentation
- [Quick Start](./QUICK_START.md) - Getting started guide
- [Versioning](./VERSIONING.md) - Version management
- [Completion Report](../../docs/reports/TASK_107_CONTRACT_TESTING_COMPLETION.md) - Implementation details
