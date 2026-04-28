# Contract Testing Quick Start

Quick reference for running and maintaining contract tests.

## Running Tests

### Consumer Tests (Frontend)

```bash
# Run all consumer tests
cd frontend/apps/web
bun run test:contracts

# Watch mode (auto-rerun on changes)
bun run test:contracts:watch

# Run with coverage report
bun run test:contracts:coverage
```

### Provider Tests (Backend)

```bash
# Run provider verification
cd backend
make test-contracts-provider

# Or from tests directory
cd tests/contracts
./scripts/run-provider-tests.sh
```

### Both Consumer and Provider

```bash
# Run everything
cd backend
make test-contracts-all

# Or step by step
make test-contracts-consumer
make test-contracts-provider
make test-contracts-coverage
```

## Writing New Contract Tests

### 1. Create Consumer Test

Create file: `tests/contracts/consumer/<domain>/<feature>.contract.test.ts`

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

const provider = createPactProvider('TraceRTM-Web-MyFeature');

describe('My Feature Contract Tests', () => {
  beforeAll(async () => {
    await setupPact(provider);
  });

  afterAll(async () => {
    await teardownPact(provider);
  });

  it('should get my resource', async () => {
    await provider.addInteraction({
      states: [{ description: 'resource exists' }],
      uponReceiving: 'a request for my resource',
      withRequest: {
        method: 'GET',
        path: '/my-resource/123',
        headers: withAuth(),
      },
      willRespondWith: standardResponse({
        id: uuid('123'),
        name: like('Resource Name'),
      }),
    });

    const response = await fetch('http://localhost:8080/my-resource/123', {
      headers: { Authorization: 'Bearer test-token' },
    });

    console.assert(response.status === 200);
  });
});
```

### 2. Add Provider State Handler

Edit: `tests/contracts/provider/provider_test.go`

```go
StateHandlers: provider.StateHandlers{
    "resource exists": func(setup bool, state provider.State) (provider.StateResponse, error) {
        if setup {
            log.Println("Setting up: resource exists")
            // Create test resource in database
        } else {
            log.Println("Cleaning up: resource exists")
            // Remove test resource
        }
        return provider.StateResponse{}, nil
    },
}
```

### 3. Run Tests

```bash
# Generate pact from consumer test
cd frontend/apps/web
bun run test:contracts

# Verify provider meets contract
cd backend
make test-contracts-provider
```

## Common Matchers

```typescript
import {
  like,        // Matches type: like('text') matches any string
  eachLike,    // Array matcher: eachLike({id: 1}) matches [{id: 1}, {id: 2}, ...]
  uuid,        // UUID matcher: uuid('123') matches any valid UUID
  integer,     // Integer matcher: integer(42) matches any integer
  decimal,     // Decimal matcher: decimal(3.14) matches any decimal
  iso8601DateTime, // ISO 8601 datetime: matches any valid ISO datetime
  regex,       // Regex matcher: regex({generate: 'abc', matcher: '^[a-z]+$'})
} from './setup';
```

## Common Patterns

### Success Response
```typescript
willRespondWith: standardResponse({
  id: uuid('123'),
  name: like('Item Name'),
  count: integer(42),
})
```

### Error Response
```typescript
willRespondWith: errorResponse(
  'Resource not found',
  'NOT_FOUND',
  404
)
```

### Paginated Response
```typescript
willRespondWith: paginatedResponse([
  {
    id: uuid('123'),
    name: like('Item 1'),
  }
])
```

### With Authentication
```typescript
withRequest: {
  method: 'GET',
  path: '/protected',
  headers: withAuth(),
}
```

## Provider States

Use descriptive provider states:

- `"user exists"` - User with test credentials exists
- `"user is authenticated"` - Valid auth session exists
- `"project exists"` - Project with test ID exists
- `"database is empty"` - No data in database
- `"database is seeded with test data"` - Test fixtures loaded

## Troubleshooting

### Consumer Test Fails

1. Check mock server is running on port 8080
2. Verify request format matches
3. Check provider state is correct
4. Run with verbose: `bun run test:contracts -- --verbose`

### Provider Verification Fails

1. Check provider state handler exists
2. Verify test data is created correctly
3. Check database connection
4. Run with debug: `go test -v ./tests/contracts/provider -args -debug`

### No Pact Files Generated

1. Consumer tests must pass
2. Check `tests/contracts/pacts/` directory exists
3. Verify `teardownPact(provider)` is called in `afterAll`

## Coverage Check

```bash
# Generate coverage report
cd tests/contracts
./scripts/generate-coverage-report.sh

# View report
cat docs/coverage.md
```

## CI/CD

Contract tests run automatically on:
- Pull requests
- Pushes to main/develop

Check `.github/workflows/contract-tests.yml` for details.

## Resources

- [Full Documentation](./README.md)
- [Pact Documentation](https://docs.pact.io/)
- [Completion Report](../../docs/reports/TASK_107_CONTRACT_TESTING_COMPLETION.md)
