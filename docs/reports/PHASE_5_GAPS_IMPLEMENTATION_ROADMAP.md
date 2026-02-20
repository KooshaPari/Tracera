# Phase 5 Gaps 5.1 & 5.2: Implementation Roadmap & Task Breakdown

**Status:** Ready for execution
**Created:** 2026-02-05
**Target:** Parallel execution across frontend (Gap 5.1) and backend (Gap 5.2)

---

## Executive Summary

This roadmap breaks Phase 5 gaps into discrete, parallel, parallelizable tasks:

- **Gap 5.1 (WebGL Tests):** 5 frontend tasks, ~20 min wall clock
- **Gap 5.2 (NATS Events):** 6 backend tasks, ~25 min wall clock
- **Total:** ~30 min wall clock (with parallelization)
- **Complexity:** Medium (no architectural changes, clear acceptance criteria)

Both gaps can execute **fully in parallel**. No cross-team blocking.

---

## Gap 5.1: WebGL Visual Regression (Frontend)

### Architecture

```
┌──────────────────────────────────────────────────────────────────┐
│ Gap 5.1: WebGL Visual Regression Testing                         │
├──────────────────────────────────────────────────────────────────┤
│                                                                   │
│  Task 5.1.1 (SMALL)          Task 5.1.2 (MEDIUM)                │
│  Un-skip Unit Tests          Create E2E Visual Spec             │
│  ├─ SigmaGraphView.test.tsx   ├─ e2e/sigma.visual.spec.ts       │
│  └─ Remove .skip()           └─ 5 test cases                    │
│       ↓ (sequential)              ↓ (sequential)                 │
│                                                                   │
│  Task 5.1.3 (MEDIUM)         Task 5.1.4 (MEDIUM)                │
│  Add Viewport Variants       Performance Benchmarks              │
│  ├─ Desktop 1280×720         ├─ FPS >30 during pan              │
│  ├─ Tablet 768×1024          ├─ Layout <500ms                   │
│  └─ Mobile 375×667           └─ Memory baseline                  │
│       ↓ (sequential)              ↓ (sequential)                 │
│                                                                   │
│  Task 5.1.5 (SMALL, OPTIONAL)                                   │
│  Chromatic CI Integration                                       │
│  └─ Setup .chromatic.config.yml                                 │
│                                                                   │
└──────────────────────────────────────────────────────────────────┘
```

### Task 5.1.1: Un-skip Unit Tests

**Effort:** 5 minutes
**Complexity:** Small (regex find-replace)

**Files:**
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.test.tsx:11`
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.test.tsx:17`
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.enhanced.test.tsx:12`
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.enhanced.test.tsx:19`

**Changes:**
```diff
- it.skip('should render sigma container...
+ it('should render sigma container...

- it.skip('should export SigmaGraphView...
+ it('should export SigmaGraphView...

- it.skip('should export enhanced renderer...
+ it('should export enhanced renderer...

- it.skip('should implement LOD rendering...
+ it('should implement LOD rendering...
```

**Acceptance:**
- [ ] 4 `.skip` directives removed
- [ ] `bun run test SigmaGraphView` passes
- [ ] No new test logic added (keep existing mocks)

---

### Task 5.1.2: Create Playwright E2E Visual Spec

**Effort:** 15 minutes
**Complexity:** Medium (boilerplate + 5 test cases)
**Depends on:** 5.1.1

**File:** `frontend/apps/web/e2e/sigma.visual.spec.ts` (new)

**Template source:** `e2e/graph.visual.spec.ts` (React Flow visual tests)

**Content required:**
```typescript
import { expect, test } from '@playwright/test';

test.describe('Sigma.js Visual Regression @visual', () => {
  // Test 1: Sigma container renders (desktop)
  test('should render sigma container', async ({ page }) => {
    await page.goto('/graph');
    await page.waitForLoadState('networkidle');
    const canvas = page.locator('canvas').first();
    await canvas.waitFor({ state: 'visible', timeout: 10_000 });
    await expect(page).toHaveScreenshot('sigma-container.png', {
      maxDiffPixelRatio: 0.02,
    });
  });

  // Test 2: Node rendering with styling
  // Test 3: Edge rendering
  // Test 4: LOD level switching
  // Test 5: Performance (FPS >30)
});
```

**Key points:**
- Use Playwright's `toHaveScreenshot()` for visual comparison
- Set `maxDiffPixelRatio: 0.02` (2% tolerance for WebGL variance)
- Mask dynamic content (timestamps, IDs) with `mask` parameter
- Disable animations with CSS injection
- Wait for canvas to be visible before capturing

**Acceptance:**
- [ ] File `e2e/sigma.visual.spec.ts` created
- [ ] 5 test cases defined
- [ ] All tests have snapshot paths defined
- [ ] `bun x playwright test e2e/sigma.visual.spec.ts` runs without errors

---

### Task 5.1.3: Add Viewport Variants

**Effort:** 10 minutes
**Complexity:** Medium (loop + viewport config)
**Depends on:** 5.1.2

**Changes to:** `e2e/sigma.visual.spec.ts`

**Add viewport loop:**
```typescript
const VIEWPORTS = [
  { name: 'desktop', width: 1280, height: 720 },
  { name: 'tablet', width: 768, height: 1024 },
  { name: 'mobile', width: 375, height: 667 },
];

for (const viewport of VIEWPORTS) {
  test.describe(`${viewport.name}`, () => {
    test.beforeEach(async ({ page }) => {
      await page.setViewportSize({
        width: viewport.width,
        height: viewport.height,
      });
    });

    test(`should render sigma container at ${viewport.name}`, async ({ page }) => {
      // Test body (reuse from 5.1.2)
    });
  });
}
```

**Acceptance:**
- [ ] 3 viewports configured (desktop, tablet, mobile)
- [ ] Each test duplicated for each viewport
- [ ] Snapshot names include viewport (e.g., `sigma-container-desktop.png`)
- [ ] All 15 tests (5 test cases × 3 viewports) pass

---

### Task 5.1.4: Performance Benchmarks

**Effort:** 10 minutes
**Complexity:** Medium (metrics collection)
**Depends on:** 5.1.3

**Add to:** `e2e/sigma.visual.spec.ts`

**Add performance tests:**
```typescript
test.describe('Performance Metrics', () => {
  test('should maintain >30 FPS during pan', async ({ page }) => {
    await page.goto('/graph');
    const canvas = page.locator('canvas').first();
    await canvas.waitFor({ state: 'visible' });

    const fps = await page.evaluate(async () => {
      let frames = 0;
      const start = performance.now();
      while (performance.now() - start < 1000) {
        frames++;
        await new Promise(r => requestAnimationFrame(r));
      }
      return frames;
    });

    console.log(`FPS: ${fps}`);
    expect(fps).toBeGreaterThan(30);
  });

  test('should layout graph in <500ms', async ({ page }) => {
    const start = Date.now();
    await page.goto('/graph');
    const canvas = page.locator('canvas').first();
    await canvas.waitFor({ state: 'visible', timeout: 10_000 });
    const elapsed = Date.now() - start;

    console.log(`Layout time: ${elapsed}ms`);
    expect(elapsed).toBeLessThan(500);
  });

  test('should use <100MB memory', async ({ page }) => {
    await page.goto('/graph');
    const canvas = page.locator('canvas').first();
    await canvas.waitFor({ state: 'visible' });

    const memory = await page.evaluate(() => {
      if (!performance.memory) return null;
      return performance.memory.usedJSHeapSize / 1_000_000;
    });

    console.log(`Memory: ${memory}MB`);
    expect(memory).toBeLessThan(100);
  });
});
```

**Acceptance:**
- [ ] 3 performance metrics added: FPS, layout time, memory
- [ ] FPS baseline: >30
- [ ] Layout time: <500ms
- [ ] Memory: <100MB
- [ ] Tests report metrics to console

---

### Task 5.1.5: Chromatic CI Integration (Optional)

**Effort:** 5 minutes
**Complexity:** Small (config file)
**Depends on:** None (independent)

**File:** `.chromatic.config.yml` or setup in `.github/workflows/ci.yml`

**Already configured?** Check if `chromatic.config.json` exists in project root.

**If not:**
```yaml
# chromatic.config.yml
projectToken: ${{ secrets.CHROMATIC_PROJECT_TOKEN }}
storybookConfigDir: frontend/apps/storybook
exitOnceUploaded: true
```

**Acceptance:**
- [ ] Chromatic config verified/created
- [ ] GitHub Actions secret configured
- [ ] `bun run chromatic` works locally

---

## Gap 5.2: OAuth NATS Event Integration (Backend)

### Architecture

```
┌────────────────────────────────────────────────────────────────┐
│ Gap 5.2: OAuth → NATS Event Publishing                         │
├────────────────────────────────────────────────────────────────┤
│                                                                 │
│  Task 5.2.1 (LARGE)                                            │
│  Create OAuth Event Publisher                                  │
│  ├─ event_publisher.go (6 event methods)                       │
│  └─ event_publisher_test.go                                    │
│       ↓ (sequential)                                            │
│                                                                 │
│  Task 5.2.2 (MEDIUM)                                           │
│  Configure JetStream Consumer                                  │
│  ├─ Add ensureConsumer() to nats.go                            │
│  └─ Add ReplayOAuthEvents()                                    │
│       ↓ (sequential)                                            │
│                                                                 │
│  Task 5.2.3 (SMALL)                                            │
│  Wire oauth_handler to Events                                  │
│  ├─ Inject EventPublisher dependency                           │
│  └─ Call Publish on key OAuth events                           │
│       ↓ (sequential)                                            │
│                                                                 │
│  Task 5.2.4 (MEDIUM)                                           │
│  Re-enable Integration Test                                    │
│  ├─ Remove @pytest.mark.skip                                  │
│  ├─ Implement test body                                        │
│  └─ Verify event replay works                                  │
│       ↓ (sequential)                                            │
│                                                                 │
│  Task 5.2.5 (SMALL, OPTIONAL)                                  │
│  Event Audit Logging                                           │
│  └─ Add audit_logger.go for compliance                         │
│                                                                 │
│  Task 5.2.6 (MEDIUM, OPTIONAL)                                 │
│  Additional Integration Tests                                  │
│  └─ Verify event flow end-to-end                               │
│                                                                 │
└────────────────────────────────────────────────────────────────┘
```

### Task 5.2.1: Create OAuth Event Publisher

**Effort:** 20 minutes
**Complexity:** Large (250+ lines, 6 methods)

**Files:**
- `backend/internal/auth/event_publisher.go` (create)
- `backend/internal/auth/event_publisher_test.go` (create)

**Required methods:**
1. `NewEventPublisher(eventBus *EventBus) *EventPublisher`
2. `PublishOAuthLoginStarted(provider, state)`
3. `PublishOAuthCallbackReceived(provider)`
4. `PublishOAuthTokenExchanged(provider, userID)`
5. `PublishOAuthUserCreated(userID, provider, email)`
6. `PublishOAuthSessionCreated(userID, sessionID)`
7. `PublishOAuthTokenRefreshed(userID)`

**Event payloads:**
```go
// oauth.login_started
{
  "provider": "google",
  "state": "state-abc123",
  "timestamp": 1707100000
}

// oauth.token_exchanged
{
  "provider": "google",
  "user_id": "user-123",
  "timestamp": 1707100010
}

// oauth.user_created
{
  "user_id": "user-123",
  "provider": "google",
  "email": "user@example.com",
  "timestamp": 1707100010
}

// oauth.session_created
{
  "user_id": "user-123",
  "session_id": "session-abc",
  "timestamp": 1707100015
}

// oauth.token_refreshed
{
  "user_id": "user-123",
  "timestamp": 1707100100
}
```

**Tests required:**
```go
func TestPublishOAuthLoginStarted(t *testing.T) { ... }
func TestPublishOAuthCallbackReceived(t *testing.T) { ... }
func TestPublishOAuthTokenExchanged(t *testing.T) { ... }
func TestPublishOAuthUserCreated(t *testing.T) { ... }
func TestPublishOAuthSessionCreated(t *testing.T) { ... }
func TestPublishOAuthTokenRefreshed(t *testing.T) { ... }
```

**Acceptance:**
- [ ] File `event_publisher.go` created with 7 methods
- [ ] File `event_publisher_test.go` created with 6 test functions
- [ ] All tests pass: `go test ./internal/auth -v -run EventPublisher`
- [ ] No errors in package build

---

### Task 5.2.2: Configure JetStream Consumer

**Effort:** 15 minutes
**Complexity:** Medium (config + one-time consumer setup)
**Depends on:** 5.2.1

**File:** `backend/internal/nats/nats.go` (modify)

**Add two methods to `EventBus`:**

1. **`ensureConsumer(config *Config) error`**
   - Creates durable consumer named `oauth-audit`
   - Filters subjects: `oauth.>`
   - Replay policy: `ReplayAllPolicy` (allow full replay)
   - Ack policy: `AckExplicitPolicy` (manual ack)
   - Max ack pending: 100

2. **`ReplayOAuthEvents(ctx context.Context) (<-chan *natslib.Msg, error)`**
   - Subscribes to `oauth.>` using `oauth-audit` consumer
   - Returns channel of messages
   - Auto-acks on receive

**Also:** Call `ensureConsumer()` in `NewEventBus()` after `ensureStream()`

**Acceptance:**
- [ ] `ensureConsumer()` method added and callable
- [ ] `ReplayOAuthEvents()` method added and callable
- [ ] Consumer created with durable name `oauth-audit`
- [ ] Tests pass: `go test ./internal/nats -v -run Consumer`
- [ ] No panics on duplicate consumer creation

---

### Task 5.2.3: Wire OAuth Handler to Events

**Effort:** 10 minutes
**Complexity:** Small (4-5 method calls)
**Depends on:** 5.2.2

**File:** `backend/internal/cliproxy/oauth_handler.go` (modify)

**Find:** The OAuth callback/session creation logic (search for `handleCallback` or `processOAuth`)

**Add event publishing:**
```go
// After successful token exchange
if h.eventPublisher != nil {
  if err := h.eventPublisher.PublishOAuthTokenExchanged(
    r.Context(),
    provider,
    user.ID,
  ); err != nil {
    h.logger.Warnf("failed to publish oauth.token_exchanged: %v", err)
    // Don't block auth on event failure
  }
}

// After creating session
if h.eventPublisher != nil {
  if err := h.eventPublisher.PublishOAuthSessionCreated(
    r.Context(),
    user.ID,
    session.ID,
  ); err != nil {
    h.logger.Warnf("failed to publish oauth.session_created: %v", err)
  }
}
```

**Key:** Always wrap in `if h.eventPublisher != nil` to handle graceful degradation.

**Acceptance:**
- [ ] OAuth handler calls event publisher methods
- [ ] Event publishing doesn't block OAuth flow
- [ ] Handler tests pass: `go test ./internal/cliproxy -v -run OAuth`
- [ ] No new dependencies required

---

### Task 5.2.4: Re-enable Integration Test

**Effort:** 15 minutes
**Complexity:** Medium (test implementation)
**Depends on:** 5.2.3

**File:** `backend/tests/integration/test_nats_events.py:400`

**Current:**
```python
@pytest.mark.skip(reason="Requires JetStream consumer configuration")
async def test_event_replay_from_timestamp(...):
    pass
```

**New:**
```python
@pytest.mark.e2e
@pytest.mark.slow
@pytest.mark.asyncio
async def test_event_replay_from_timestamp(
    db_session,
    neo4j_driver,
    nats_client,
    event_publisher,
):
    """Test OAuth event replay from JetStream consumer."""

    # 1. Setup: Create test session
    session_data = await create_test_session(
        db_session=db_session,
        neo4j_driver=neo4j_driver,
    )
    user_id = session_data.get("user_id", "test-user-123")

    # 2. Subscribe to oauth.> events
    collector = EventCollector()
    await nats_client.subscribe("oauth.>", cb=collector.callback)
    await asyncio.sleep(0.1)

    # 3. Publish test events
    await event_publisher.publish_oauth_login_started(
        provider="google",
        state="state-test",
    )
    await event_publisher.publish_oauth_callback_received(
        provider="google",
        code="code-test",
    )
    await event_publisher.publish_oauth_token_exchanged(
        provider="google",
        user_id=user_id,
    )
    await event_publisher.publish_oauth_user_created(
        user_id=user_id,
        provider="google",
        email="test@example.com",
    )
    await event_publisher.publish_oauth_session_created(
        user_id=user_id,
        session_id="session-test",
    )

    # 4. Wait for events to propagate
    await asyncio.sleep(0.3)

    # 5. Verify events received
    events = collector.get_all_events()
    assert len(events) >= 5, f"Expected 5+ events, got {len(events)}"

    # 6. Verify event types
    event_types = {e["event_type"] for e in events}
    expected = {
        "oauth.login_started",
        "oauth.callback_received",
        "oauth.token_exchanged",
        "oauth.user_created",
        "oauth.session_created",
    }
    assert expected.issubset(event_types), f"Missing: {expected - event_types}"

    # 7. Verify payload structure
    for event in events:
        assert "event_type" in event
        assert "data" in event
        assert isinstance(event["data"], dict)

    # 8. Cleanup
    await cleanup_test_session(db_session, neo4j_driver, session_data["session_id"])
```

**Acceptance:**
- [ ] `@pytest.mark.skip` removed
- [ ] Test body implemented (7 steps as above)
- [ ] All assertions pass
- [ ] Test passes: `pytest test_nats_events.py::test_event_replay_from_timestamp -v`

---

### Task 5.2.5: Event Audit Logging (Optional)

**Effort:** 10 minutes
**Complexity:** Small (structured logging)
**Depends on:** 5.2.3

**File:** `backend/internal/auth/event_logger.go` (create)

**Purpose:** Log all OAuth events to structured logger for compliance/audit

**Methods:**
```go
type EventLogger struct {
  logger Logger // structured logger
}

func (el *EventLogger) LogOAuthEvent(event *events.Event) error {
  // Log event to structured logger (JSON format)
  // Include: timestamp, event type, user ID, provider
}
```

**Integration:** Call from event publisher or oauth handler

**Acceptance:**
- [ ] File `event_logger.go` created
- [ ] Logs OAuth events to JSON structured format
- [ ] No test failures from logging

---

### Task 5.2.6: Additional Integration Tests (Optional)

**Effort:** 15 minutes
**Complexity:** Medium (test fixtures)
**Depends on:** 5.2.4

**File:** `backend/tests/integration/test_nats_events.py` (add new test functions)

**Tests to add:**
1. `test_oauth_event_payload_validation` - Verify event structure
2. `test_oauth_events_ordered` - Events arrive in correct order
3. `test_oauth_consumer_durable` - Consumer survives disconnection

**Acceptance:**
- [ ] 3 new test functions added
- [ ] All pass: `pytest test_nats_events.py -k oauth -v`

---

## Execution Plan: Recommended Order

### Phase 1: Setup (Parallel, ~2 min)

**Start both:**
- Gap 5.1: Task 5.1.1 (un-skip tests)
- Gap 5.2: Task 5.2.1 (create event publisher)

**Why parallel:** No dependencies, independent codebases (frontend vs backend)

### Phase 2: Core Implementation (Sequential within each gap)

**Gap 5.1 (Frontend):**
1. 5.1.1 → 5.1.2 → 5.1.3 → 5.1.4 (dependent chain)

**Gap 5.2 (Backend):**
1. 5.2.1 → 5.2.2 → 5.2.3 → 5.2.4 (dependent chain)

### Phase 3: Optional Enhancements (Parallel, after core)

- 5.1.5 (Chromatic CI)
- 5.2.5 (Audit logging)
- 5.2.6 (Extra tests)

### Phase 4: Verification (Parallel)

**Frontend:**
```bash
bun run test:e2e
bun x playwright test e2e/sigma.visual.spec.ts
```

**Backend:**
```bash
go test ./internal/auth ./internal/nats ./internal/cliproxy -v
pytest backend/tests/integration/test_nats_events.py -v
```

---

## DAG: Task Dependencies

```
┌─────────────┐          ┌─────────────┐
│ 5.1.1       │          │ 5.2.1       │
│ Un-skip     │          │ Publisher   │
└──────┬──────┘          └──────┬──────┘
       │                        │
       ▼                        ▼
┌─────────────┐          ┌─────────────┐
│ 5.1.2       │          │ 5.2.2       │
│ E2E Spec    │          │ Consumer    │
└──────┬──────┘          └──────┬──────┘
       │                        │
       ▼                        ▼
┌─────────────┐          ┌─────────────┐
│ 5.1.3       │          │ 5.2.3       │
│ Viewports   │          │ Wire Events │
└──────┬──────┘          └──────┬──────┘
       │                        │
       ▼                        ▼
┌─────────────┐          ┌─────────────┐
│ 5.1.4       │          │ 5.2.4       │
│ Performance │          │ Re-enable   │
└──────┬──────┘          │ Test        │
       │                 └──────┬──────┘
       │                        │
       ├─────────────┬──────────┘
       │             │
       ▼             ▼
   ┌──────────────────┐
   │ Optional Tasks   │
   │ 5.1.5, 5.2.5, 5.2.6
   └──────────────────┘
       │
       ▼
   ┌──────────────────┐
   │ Verify All Tests │
   └──────────────────┘
```

---

## Effort Breakdown (Wall Clock Time)

| Phase | Task | Est. | Notes |
|-------|------|------|-------|
| 1 | 5.1.1 + 5.2.1 (parallel) | 20m | Large publisher requires care |
| 2 | 5.1.2 + 5.2.2 (parallel) | 15m | E2E spec setup + consumer config |
| 3 | 5.1.3 + 5.2.3 (parallel) | 10m | Viewport loop + oauth handler wiring |
| 4 | 5.1.4 + 5.2.4 (parallel) | 15m | Performance metrics + test impl |
| 5 | 5.1.5 + 5.2.5 + 5.2.6 (opt) | 10m | Optional, can defer |
| 6 | Verification | 5m | Run test suites |
| **TOTAL** | | **30m wall clock** | With parallelization |

---

## Success Metrics

### Gap 5.1 Completion

```
✓ 4 unit tests un-skipped and passing
✓ 5 Playwright visual regression tests created
✓ 3 viewport variants tested (desktop, tablet, mobile)
✓ Performance benchmarks: FPS >30, layout <500ms
✓ Visual snapshots stored with <2% tolerance
✓ All E2E tests passing
✓ No regressions in existing tests
```

### Gap 5.2 Completion

```
✓ OAuth event publisher created with 6+ event types
✓ JetStream consumer configured and durable
✓ OAuth handler wired to event publisher
✓ Integration test un-skipped and passing
✓ Event payload validation passing
✓ Event audit trail verified via consumer
✓ No OAuth handler blocking on event publishing
✓ >80% test coverage on new code
```

---

## Rollback Plan

If any phase fails:

1. **Gap 5.1 fails:** Revert Playwright changes, keep unit test un-skips (they work with mocks)
2. **Gap 5.2 fails:** Revert event publisher wiring from oauth_handler, keep consumer config
3. **Acceptance tests fail:** Debug specific test case, don't affect other tasks

---

## Sign-Off Checklist

**Frontend (5.1):**
- [ ] All 4 unit tests passing
- [ ] 5+ Playwright tests created and passing
- [ ] Visual snapshots baseline captured
- [ ] CI/CD pipeline green

**Backend (5.2):**
- [ ] Event publisher implemented and tested
- [ ] JetStream consumer configured
- [ ] OAuth handler wired to events
- [ ] Integration test passing
- [ ] CI/CD pipeline green

**Documentation:**
- [ ] This roadmap reviewed
- [ ] Quick start guide available
- [ ] API reference for event publisher documented

---

## References

1. **Full Analysis:** `docs/reports/PHASE_5_GAPS_5_1_5_2_ANALYSIS.md`
2. **Quick Start:** `docs/guides/PHASE_5_GAPS_IMPLEMENTATION_QUICK_START.md`
3. **Playwright Docs:** https://playwright.dev/docs/intro
4. **NATS JetStream:** https://docs.nats.io/nats-concepts/jetstream
5. **Existing Tests:**
   - Frontend: `frontend/apps/web/src/__tests__/components/graph/`
   - Backend: `backend/tests/integration/test_nats_events.py`

---

## Questions / Blockers

**Q: What if Sigma.js canvas doesn't render in Playwright?**
A: Check route (`/graph` vs `/graph/sigma`), add explicit wait for WebGL context, adjust timeout.

**Q: What if JetStream consumer creation fails?**
A: Normal on first run (creates consumer). Check for "consumer already exists" error (it's OK).

**Q: Can I defer optional tasks (5.1.5, 5.2.5, 5.2.6)?**
A: Yes—focus on core 4 tasks per gap. Optionals can be Phase 5.3+ work.

---

**Ready to implement!** Both gaps are clear, scoped, and parallelizable.
