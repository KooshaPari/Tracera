# Critical Tier Test Requirements

**Project:** TracerTM
**Criticality Tier:** Critical
**Last Updated:** 2026-02-14

## Overview

Critical-tier projects require **7 test types** to ensure comprehensive quality coverage:

| Test Type | Status | Priority |
|-----------|--------|----------|
| Unit | ✅ Implemented | Required |
| Integration | ✅ Implemented | Required |
| E2E | ✅ Implemented | Required |
| Property-Based | ⚠️ Missing | High |
| Contract | ⚠️ Missing | Medium |
| Mutation | ⚠️ Missing | Medium |
| Security | ✅ Implemented | Required |

## Current Implementation

### ✅ Unit Tests (Implemented)
- **Python:** 1,346 collected tests using pytest
- **Go:** Unit tests with table-driven patterns
- **TypeScript:** 3,939 vitest tests

### ✅ Integration Tests (Implemented)
- Database integration tests (PostgreSQL)
- API endpoint integration tests
- Service-to-service integration

### ✅ E2E Tests (Implemented)
- Frontend E2E tests using vitest
- Full user flow testing

### ✅ Security Tests (Implemented)
- **Bandit:** Python security scanning (186 low severity baseline)
- **Govulncheck:** Go vulnerability scanning (0 vulnerabilities)
- **Semgrep:** Static analysis security testing

## Missing Test Types - Implementation Guide

### ⚠️ Property-Based Testing

**Purpose:** Generate random test inputs to find edge cases

**Python - Hypothesis**

```bash
# Install
pip install hypothesis

# Example test
from hypothesis import given, strategies as st

@given(st.integers(), st.integers())
def test_addition_commutative(a, b):
    assert a + b == b + a
```

**TypeScript - fast-check**

```bash
# Install
bun add -d fast-check

# Example test
import fc from 'fast-check';

test('string concatenation is associative', () => {
  fc.assert(
    fc.property(fc.string(), fc.string(), fc.string(), (a, b, c) => {
      return (a + b) + c === a + (b + c);
    })
  );
});
```

**Go - gopter**

```bash
# Install
go get github.com/leanovate/gopter

# Example test
import "github.com/leanovate/gopter"

func TestAdditionCommutative(t *testing.T) {
    properties := gopter.NewProperties(nil)
    properties.Property("addition is commutative", prop.ForAll(
        func(a, b int) bool {
            return a + b == b + a
        },
        gen.Int(),
        gen.Int(),
    ))
    properties.TestingRun(t)
}
```

**Target:**
- 10+ property-based tests per critical module
- Focus on: API input validation, data transformations, state machines

---

### ⚠️ Contract Testing

**Purpose:** Verify API contracts between services/consumers

**Python - Pact**

```bash
# Install
pip install pact-python

# Provider test
from pact import Provider

def test_provider_honors_contract():
    provider = Provider('TracerTM API')
    provider.verify_with_provider(
        provider_base_url='http://localhost:8000',
        pact_url='./pacts/consumer-tracertm.json'
    )
```

**TypeScript - Pact-JS**

```bash
# Install
bun add -d @pact-foundation/pact

# Consumer test
import { PactV3 } from '@pact-foundation/pact';

const provider = new PactV3({
  consumer: 'Frontend',
  provider: 'TracerTM API'
});

test('get requirements', () => {
  provider
    .given('requirements exist')
    .uponReceiving('a request for requirements')
    .withRequest({ method: 'GET', path: '/api/requirements' })
    .willRespondWith({ status: 200, body: [] });

  return provider.executeTest(async (mockServer) => {
    const response = await fetch(`${mockServer.url}/api/requirements`);
    expect(response.status).toBe(200);
  });
});
```

**Go - Pact-Go**

```bash
# Install
go get github.com/pact-foundation/pact-go/v2

# Provider verification
import "github.com/pact-foundation/pact-go/v2/provider"

func TestPactVerification(t *testing.T) {
    verifier := provider.NewVerifier()
    verifier.VerifyProvider(t, provider.VerifyRequest{
        ProviderBaseURL: "http://localhost:8080",
        PactURLs:        []string{"./pacts/consumer-provider.json"},
    })
}
```

**Target:**
- Contracts for all external API endpoints
- Consumer-driven contract tests for frontend → backend
- Provider verification tests for backend APIs

---

### ⚠️ Mutation Testing

**Purpose:** Verify test quality by mutating code and ensuring tests fail

**Python - mutmut**

```bash
# Install
pip install mutmut

# Run mutation testing
mutmut run --paths-to-mutate src/tracertm/
mutmut results
mutmut html  # Generate HTML report
```

**Configuration (setup.cfg):**
```ini
[mutmut]
paths_to_mutate=src/tracertm/
backup=False
runner=python -m pytest -x
tests_dir=tests/
```

**TypeScript - Stryker**

```bash
# Install
bun add -d @stryker-mutator/core @stryker-mutator/vitest-runner

# Configuration (stryker.config.json)
{
  "packageManager": "bun",
  "testRunner": "vitest",
  "coverageAnalysis": "perTest",
  "mutate": ["src/**/*.ts", "!src/**/*.test.ts"]
}

# Run
bunx stryker run
```

**Go - go-mutesting**

```bash
# Install
go install github.com/zimmski/go-mutesting/cmd/go-mutesting@latest

# Run
go-mutesting ./backend/...
```

**Target:**
- Mutation score ≥ 80% for critical modules
- Focus on: business logic, validation, error handling

---

## Implementation Roadmap

### Phase 1 - Security (Complete) ✅
- Bandit, govulncheck, semgrep integrated

### Phase 2 - Property-Based (Next Priority) 🔜
**Effort:** ~1 week
1. Install hypothesis, fast-check, gopter
2. Identify 20+ critical properties to test
3. Write property-based tests for:
   - API input validation
   - Graph algorithms (cycle detection, path finding)
   - Data transformations
4. Integrate into CI pipeline

### Phase 3 - Contract Testing 📅
**Effort:** ~2 weeks
1. Install Pact for Python, TypeScript, Go
2. Define API contracts for:
   - Frontend ↔ Backend REST APIs
   - Backend ↔ Go Backend gRPC
   - External integrations (GitHub, Jira)
3. Set up contract verification in CI
4. Create contract broker (optional: Pact Broker)

### Phase 4 - Mutation Testing 📅
**Effort:** ~1 week
1. Install mutmut, Stryker, go-mutesting
2. Run baseline mutation tests
3. Improve test suites to achieve ≥80% mutation score
4. Add mutation testing to CI (warning-only initially)

---

## Tier Enforcer Bypass (Temporary)

While implementing missing test types, you can bypass the tier enforcer:

```bash
export QA_TIER_FAIL_CLOSED=false
```

**WARNING:** This should only be used during active implementation. Re-enable enforcement once test types are in place.

---

## References

### Property-Based Testing
- [Hypothesis](https://hypothesis.readthedocs.io/)
- [fast-check](https://fast-check.dev/)
- [gopter](https://github.com/leanovate/gopter)

### Contract Testing
- [Pact](https://docs.pact.io/)
- [Pact Python](https://github.com/pact-foundation/pact-python)
- [Pact-JS](https://docs.pact.io/implementation_guides/javascript)
- [Pact-Go](https://github.com/pact-foundation/pact-go)

### Mutation Testing
- [mutmut](https://mutmut.readthedocs.io/)
- [Stryker](https://stryker-mutator.io/)
- [go-mutesting](https://github.com/zimmski/go-mutesting)

---

## Success Criteria

Critical tier requirements will be satisfied when:

- ✅ All 7 test types implemented
- ✅ Property-based: ≥10 tests per critical module
- ✅ Contract: All external APIs covered
- ✅ Mutation: ≥80% mutation score
- ✅ Attestation metadata reflects all test types
- ✅ Tier enforcer passes without bypass
