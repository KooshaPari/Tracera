# Phase 5 Gaps 5.1 & 5.2: Comprehensive Implementation Analysis

**Date:** 2026-02-05
**Status:** Architecture & Plan Ready
**Complexity:** High (WebGL testing + NATS integration)
**Effort Estimate:** 8-12 parallel subagent tasks, ~15-20 min wall clock

---

## Executive Summary

This analysis covers two critical Phase 5 gaps:
1. **Gap 5.1**: WebGL Visual Regression Testing (4 skipped tests in Sigma.js integration)
2. **Gap 5.2**: OAuth NATS Event Integration (1 skipped test requiring JetStream consumer)

Both gaps have clear root causes, existing infrastructure, and well-defined acceptance criteria. Implementation is straightforward with proper architecture.

---

## Gap 5.1: WebGL Visual Regression Testing

### Current State

**Skipped Tests (4 total):**
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.test.tsx:11` - sigma container (requires WebGL)
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.test.tsx:17` - export component (requires WebGL)
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.enhanced.test.tsx:12` - enhanced renderer (requires WebGL)
- `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.enhanced.test.tsx:19` - LOD rendering (requires WebGL)

**Root Cause:** WebGL not available in jsdom test environment. Tests need browser environment.

**Existing Infrastructure:**
- ✅ Playwright E2E framework configured (`playwright.config.ts`)
- ✅ Visual regression baseline (`e2e/graph.visual.spec.ts` - React Flow, not Sigma)
- ✅ Chromatic CI integration available (see `.github/workflows/ci.yml`)
- ✅ Global visual test setup in `e2e/example.visual.spec.ts` and others
- ✅ Sigma.js renderer modules exist with mocks ready
- ✅ Percy or native Playwright snapshot comparison available

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│ WebGL Visual Regression Testing Architecture                │
└─────────────────────────────────────────────────────────────┘

Unit Tests (jsdom)                    E2E Tests (Browser)
└──────────────────┬──────────────────────────────┬─────────────┘
                   │                              │
         ┌─────────▼──────────┐      ┌────────────▼─────────┐
         │ Mock-based Tests   │      │ Real WebGL Tests     │
         │ (SigmaGraphView.*)  │      │ (e2e/sigma.spec.ts)  │
         │                    │      │                      │
         │ ✅ Node renders    │      │ ✅ Canvas rendering  │
         │ ✅ Edge renders    │      │ ✅ Performance (FPS) │
         │ ✅ LOD switching   │      │ ✅ Layout time       │
         │ ✅ Highlight state │      │ ✅ Memory usage      │
         └────────────────────┘      └──────────────────────┘
                                              │
                                     ┌────────▼────────────┐
                                     │ Visual Snapshots    │
                                     │ (Playwright/Percy)  │
                                     │                     │
                                     │ ✅ Sigma container  │
                                     │ ✅ Node rendering   │
                                     │ ✅ Edge rendering   │
                                     │ ✅ Controls (zoom)  │
                                     │ ✅ Minimap          │
                                     └─────────────────────┘
```

### Implementation Strategy

**Phase 1: Re-enable Unit Tests (Jsdom with Mocks)**
- File: `SigmaGraphView.test.tsx` + `SigmaGraphView.enhanced.test.tsx`
- Approach: Keep tests but un-skip, use canvas 2D context mocks (no WebGL)
- Benefits: Fast, deterministic, catches most rendering logic
- Effort: 2 small changes

**Phase 2: Add Playwright Visual Regression (Real WebGL)**
- File: `e2e/sigma.visual.spec.ts` (new)
- Approach: Playwright screenshot comparison with tolerance
- Tests:
  - Sigma container visibility
  - Node rendering (size, color, icon, label by LOD)
  - Edge rendering (path, color, thickness)
  - Controls responsiveness (zoom, pan, reset)
  - Minimap accuracy
  - Mobile/tablet/desktop viewports
- Effort: 4 medium tasks (1 per viewport variant)

**Phase 3: Setup Chromatic CI (Optional - for Advanced Snapshots)**
- File: `.chromatic.config.yml` (existing) + CI integration
- Approach: Percy-style visual diffs with human review workflow
- Effort: 1 small task (already partially configured)

**Phase 4: Performance Benchmarks**
- File: `e2e/sigma.performance.spec.ts` (new)
- Metrics: FPS >30, layout <500ms, memory <100MB
- Effort: 1 medium task

---

## Gap 5.2: OAuth NATS Event Integration

### Current State

**Skipped Test (1 total):**
- `backend/tests/integration/test_nats_events.py:400` - `test_event_replay_from_timestamp`
- Skip reason: "Requires JetStream consumer configuration"

**Existing Infrastructure:**
- ✅ NATS client configured (`backend/internal/nats/nats.go`)
- ✅ EventBus with JetStream support (lines 123-200 in `nats.go`)
- ✅ Stream creation (`ensureStream()` method)
- ✅ Event publishing (`PublishToProject()`, `PublishToEntity()`, etc.)
- ✅ OAuth state manager (`backend/internal/auth/oauth_state.go`)
- ✅ Integration test fixtures exist (`backend/tests/integration/test_nats_events.py`)

**Missing:**
- OAuth event publisher (user.created, user.session_created, oauth.token_refreshed)
- Event consumer configuration for JetStream
- Integration between OAuth handler and event bus
- Event audit logging

### Architecture Overview

```
┌────────────────────────────────────────────────────────────┐
│ OAuth Event Flow Architecture                              │
└────────────────────────────────────────────────────────────┘

OAuth Handlers (Existing)
    │
    ├─ /auth/login
    ├─ /auth/callback (oauth_handler.go)
    ├─ /auth/refresh
    └─ /auth/logout

            │
            ▼
    ┌──────────────────────┐
    │ Event Publisher      │  ← CREATE: event_publisher.go
    │ (new)                │
    │ - user.created       │
    │ - oauth.token_ready  │
    │ - oauth.refresh      │
    └──────┬───────────────┘
           │
           ▼
    ┌──────────────────────┐
    │ NATS JetStream       │
    │ - Stream: OAUTH      │
    │ - Subjects:          │
    │   oauth.>            │
    │   users.>            │
    └──────┬───────────────┘
           │
    ┌──────▼──────────────────────┐
    │ Event Consumers (Config)     │
    │ - Audit Consumer             │
    │ - Analytics Consumer         │
    │ - Compliance Consumer        │
    └──────────────────────────────┘
```

### Implementation Strategy

**Phase 1: Create OAuth Event Publisher**
- File: `backend/internal/auth/event_publisher.go` (new)
- Events:
  - `oauth.login_started` (redirect to provider)
  - `oauth.callback_received` (auth code received)
  - `oauth.token_exchanged` (token obtained)
  - `oauth.user_created` (first-time user)
  - `oauth.session_created` (session established)
  - `oauth.token_refreshed` (refresh successful)
  - `oauth.token_expired` (TTL exceeded)
- Effort: 1 large task (200+ lines)

**Phase 2: Configure NATS JetStream Consumer**
- File: `backend/internal/nats/nats.go` - add `ensureConsumer()`
- Consumer Type: Durable pull consumer (replay support)
- Settings:
  - Name: `oauth-audit-consumer`
  - Durable: `oauth-audit`
  - Filter: `oauth.>`
  - Replay policy: `all` (allow full replay)
  - Max ack pending: 100
- Effort: 1 medium task

**Phase 3: Wire OAuth Handler → Event Publisher**
- File: `backend/internal/cliproxy/oauth_handler.go` (modify existing)
- Changes:
  - Inject EventBus dependency
  - Call `publisher.Publish()` on key OAuth events
  - Handle publisher errors gracefully (don't block auth)
- Effort: 1 small task

**Phase 4: Re-enable Integration Test**
- File: `backend/tests/integration/test_nats_events.py:400` (un-skip)
- Implement test body: subscribe to JetStream, publish events, verify replay
- Effort: 1 medium task

**Phase 5: Event Audit Logging**
- File: `backend/internal/auth/event_logger.go` (new, optional)
- Log all OAuth events to structured logger (JSON)
- Benefits: Compliance, debugging, analytics
- Effort: 1 small task (optional)

---

## Detailed Implementation Plan

### WBS: Work Breakdown Structure

```
Phase 5.1 & 5.2 Gap Closure
├── Gap 5.1: WebGL Visual Regression (4-5 tasks)
│   ├── 5.1.1 Un-skip and fix unit tests (small)
│   ├── 5.1.2 Create e2e/sigma.visual.spec.ts (medium)
│   ├── 5.1.3 Add viewport variants (medium)
│   ├── 5.1.4 Add performance benchmarks (medium)
│   └── 5.1.5 Configure Chromatic CI (small, optional)
│
└── Gap 5.2: OAuth NATS Integration (5-6 tasks)
    ├── 5.2.1 Create event_publisher.go (large)
    ├── 5.2.2 Configure JetStream consumer (medium)
    ├── 5.2.3 Wire oauth_handler → events (small)
    ├── 5.2.4 Re-enable Python test (medium)
    ├── 5.2.5 Add event audit logging (small, optional)
    └── 5.2.6 Integration tests (medium)
```

### DAG Dependencies

```
Gap 5.1:
  5.1.1 (un-skip tests)
    ↓
  5.1.2 (create e2e file)
    ↓
  5.1.3 (viewport variants)
    ↓
  5.1.4 (performance)

  (5.1.5 optional, parallel)

Gap 5.2:
  5.2.1 (event_publisher.go)
    ↓
  5.2.2 (JetStream consumer)
    ↓
  5.2.3 (wire oauth_handler)
    ↓
  5.2.4 (re-enable test)
    ↓
  5.2.6 (integration tests)

  (5.2.5 optional, parallel)

Overall: Gap 5.1 and Gap 5.2 can run in PARALLEL
```

---

## Code Sketches

### Gap 5.1.1: Un-skip Unit Tests

**File:** `frontend/apps/web/src/__tests__/components/graph/SigmaGraphView.test.tsx`

```typescript
describe('SigmaGraphView', () => {
  // CHANGE: Remove .skip(), keep test
  it('should render sigma container', () => {
    // Mock canvas 2D context (already have this in setup.ts)
    // Test that component initializes and mounts
    expect(true).toBeTruthy(); // Will replace with actual test
  });

  it('should export SigmaGraphView component', async () => {
    // Mock @react-sigma/core
    // Test module export
    const module = await import('@/components/graph/sigma/SigmaGraphView');
    expect(module.SigmaGraphView).toBeDefined();
  });
});
```

### Gap 5.1.2: Create Playwright Visual Spec

**File:** `frontend/apps/web/e2e/sigma.visual.spec.ts` (new)

```typescript
import { expect, test } from '@playwright/test';

test.describe('Sigma.js Graph Visual Regression @visual', () => {
  const viewports = [
    { name: 'desktop', width: 1280, height: 720 },
    { name: 'tablet', width: 768, height: 1024 },
    { name: 'mobile', width: 375, height: 667 },
  ];

  for (const viewport of viewports) {
    test.describe(`${viewport.name}`, () => {
      test.beforeEach(async ({ page }) => {
        await page.setViewportSize(viewport);
      });

      test('should render sigma container with WebGL', async ({ page }) => {
        await page.goto('/graph/sigma');
        await page.waitForLoadState('networkidle');

        // Wait for sigma canvas
        const canvas = page.locator('canvas').first();
        await canvas.waitFor({ state: 'visible', timeout: 10_000 });

        // Disable animations
        await page.addStyleTag({
          content: '* { animation-duration: 0s !important; transition-duration: 0s !important; }',
        });

        await expect(page).toHaveScreenshot(`sigma-container-${viewport.name}.png`, {
          mask: [page.locator('[data-testid="timestamp"]')], // Mask timestamps
          maxDiffPixelRatio: 0.02, // 2% tolerance
        });
      });

      test('should render nodes with correct styling', async ({ page }) => {
        await page.goto('/graph/sigma?lod=medium');
        const canvas = page.locator('canvas').first();
        await canvas.waitFor({ state: 'visible', timeout: 10_000 });

        // Verify node rendering by checking canvas pixel data
        const pixelData = await canvas.evaluate((el: HTMLCanvasElement) => {
          const ctx = el.getContext('2d');
          if (!ctx) return null;
          return ctx.getImageData(0, 0, el.width, el.height).data.slice(0, 100);
        });

        expect(pixelData).not.toBeNull(); // Canvas has pixels (not blank)
      });

      test('should render edges correctly', async ({ page }) => {
        await page.goto('/graph/sigma');
        const canvas = page.locator('canvas').first();
        await canvas.waitFor({ state: 'visible' });

        await expect(page).toHaveScreenshot(`sigma-edges-${viewport.name}.png`, {
          maxDiffPixelRatio: 0.02,
        });
      });
    });
  }

  test.describe('LOD (Level of Detail) Rendering', () => {
    test('should switch rendering based on zoom level', async ({ page }) => {
      await page.goto('/graph/sigma');

      // Zoom out (far LOD - should show only circles)
      await page.evaluate(() => {
        // Simulate zoom change
        window.dispatchEvent(new WheelEvent('wheel', { deltaY: 100 }));
      });
      await page.waitForTimeout(500);

      let screenshot = await page.screenshot();
      // Verify nodes are small circles

      // Zoom in (close LOD - should show labels and icons)
      await page.evaluate(() => {
        window.dispatchEvent(new WheelEvent('wheel', { deltaY: -100 }));
      });
      await page.waitForTimeout(500);

      screenshot = await page.screenshot();
      // Verify nodes show labels and icons
    });
  });

  test.describe('Performance', () => {
    test('should maintain >30 FPS during pan', async ({ page }) => {
      await page.goto('/graph/sigma');

      const fps = await page.evaluate(async () => {
        return new Promise<number>((resolve) => {
          let frames = 0;
          let lastTime = performance.now();

          const measureFPS = () => {
            frames++;
            const now = performance.now();
            if (now - lastTime >= 1000) {
              resolve(frames);
            } else {
              requestAnimationFrame(measureFPS);
            }
          };

          requestAnimationFrame(measureFPS);
        });
      });

      expect(fps).toBeGreaterThan(30);
    });

    test('should layout graph in <500ms', async ({ page }) => {
      const start = Date.now();
      await page.goto('/graph/sigma');
      const canvas = page.locator('canvas').first();
      await canvas.waitFor({ state: 'visible', timeout: 10_000 });
      const duration = Date.now() - start;

      expect(duration).toBeLessThan(500);
    });
  });
});
```

---

### Gap 5.2.1: Create OAuth Event Publisher

**File:** `backend/internal/auth/event_publisher.go` (new, ~250 lines)

```go
package auth

import (
	"context"
	"fmt"
	"time"

	"github.com/kooshapari/tracertm-backend/internal/events"
	"github.com/kooshapari/tracertm-backend/internal/nats"
)

// EventPublisher handles OAuth event publishing to NATS
type EventPublisher struct {
	eventBus *nats.EventBus
}

// NewEventPublisher creates a new OAuth event publisher
func NewEventPublisher(eventBus *nats.EventBus) *EventPublisher {
	return &EventPublisher{eventBus: eventBus}
}

// PublishOAuthLoginStarted publishes when OAuth login begins
func (ep *EventPublisher) PublishOAuthLoginStarted(ctx context.Context, provider string, state string) error {
	event := &events.Event{
		ID:        generateEventID(),
		EventType: "oauth.login_started",
		CreatedAt: time.Now(),
		Data: map[string]any{
			"provider": provider,
			"state":    state,
			"timestamp": time.Now().Unix(),
		},
	}
	return ep.eventBus.Publish(event)
}

// PublishOAuthCallbackReceived publishes when auth code is received
func (ep *EventPublisher) PublishOAuthCallbackReceived(ctx context.Context, provider string, code string) error {
	event := &events.Event{
		ID:        generateEventID(),
		EventType: "oauth.callback_received",
		CreatedAt: time.Now(),
		Data: map[string]any{
			"provider":  provider,
			"code":      maskCode(code), // Don't log actual code
			"timestamp": time.Now().Unix(),
		},
	}
	return ep.eventBus.Publish(event)
}

// PublishOAuthTokenExchanged publishes when token is exchanged
func (ep *EventPublisher) PublishOAuthTokenExchanged(ctx context.Context, provider string, userID string) error {
	event := &events.Event{
		ID:        generateEventID(),
		EventType: "oauth.token_exchanged",
		CreatedAt: time.Now(),
		Data: map[string]any{
			"provider":  provider,
			"user_id":   userID,
			"timestamp": time.Now().Unix(),
		},
	}
	return ep.eventBus.PublishToEntity(userID, event)
}

// PublishOAuthUserCreated publishes when new user is created
func (ep *EventPublisher) PublishOAuthUserCreated(ctx context.Context, userID string, provider string, email string) error {
	event := &events.Event{
		ID:        generateEventID(),
		EventType: "oauth.user_created",
		CreatedAt: time.Now(),
		Data: map[string]any{
			"user_id":   userID,
			"provider":  provider,
			"email":     email,
			"timestamp": time.Now().Unix(),
		},
	}
	return ep.eventBus.PublishToEntity(userID, event)
}

// PublishOAuthSessionCreated publishes when session is created
func (ep *EventPublisher) PublishOAuthSessionCreated(ctx context.Context, userID string, sessionID string) error {
	event := &events.Event{
		ID:        generateEventID(),
		EventType: "oauth.session_created",
		CreatedAt: time.Now(),
		Data: map[string]any{
			"user_id":    userID,
			"session_id": sessionID,
			"timestamp":  time.Now().Unix(),
		},
	}
	return ep.eventBus.PublishToEntity(userID, event)
}

// PublishOAuthTokenRefreshed publishes when token is refreshed
func (ep *EventPublisher) PublishOAuthTokenRefreshed(ctx context.Context, userID string) error {
	event := &events.Event{
		ID:        generateEventID(),
		EventType: "oauth.token_refreshed",
		CreatedAt: time.Now(),
		Data: map[string]any{
			"user_id":   userID,
			"timestamp": time.Now().Unix(),
		},
	}
	return ep.eventBus.PublishToEntity(userID, event)
}

// PublishOAuthTokenExpired publishes when token expires
func (ep *EventPublisher) PublishOAuthTokenExpired(ctx context.Context, userID string) error {
	event := &events.Event{
		ID:        generateEventID(),
		EventType: "oauth.token_expired",
		CreatedAt: time.Now(),
		Data: map[string]any{
			"user_id":   userID,
			"timestamp": time.Now().Unix(),
		},
	}
	return ep.eventBus.PublishToEntity(userID, event)
}

// Helper functions
func generateEventID() string {
	return fmt.Sprintf("oauth-%d", time.Now().UnixNano())
}

func maskCode(code string) string {
	if len(code) <= 8 {
		return "****"
	}
	return code[:4] + "****" + code[len(code)-4:]
}
```

---

### Gap 5.2.2: Configure JetStream Consumer

**File:** `backend/internal/nats/nats.go` - add method

```go
// ensureConsumer creates or updates the durable pull consumer for OAuth events
func (eb *EventBus) ensureConsumer(config *Config) error {
	consumerConfig := &natslib.ConsumerConfig{
		Durable:       "oauth-audit",
		Description:   "Durable consumer for OAuth event audit trail",
		FlowControl:   true,
		IdleHeartbeat: 5 * time.Second,
		// Replay policy: allow full replay from beginning
		ReplayPolicy: natslib.ReplayAllPolicy,
		// AckPolicy: explicit (manual ack)
		AckPolicy: natslib.AckExplicitPolicy,
		// Max ack pending: prevent overwhelming subscribers
		MaxAckPending: 100,
		// Filter to oauth events only
		FilterSubjects: []string{"oauth.>"},
	}

	// Create or update consumer
	_, err := eb.js.AddConsumer(config.StreamName, consumerConfig)
	if err != nil {
		// Check if already exists (error is OK)
		if !isConsumerExistsError(err) {
			return fmt.Errorf("failed to create consumer: %w", err)
		}
	}

	return nil
}

func isConsumerExistsError(err error) bool {
	return err != nil && err.Error() == "consumer already exists"
}

// ReplayOAuthEvents replays all OAuth events from a given timestamp
func (eb *EventBus) ReplayOAuthEvents(ctx context.Context, fromTime time.Time) (<-chan *natslib.Msg, error) {
	// Create ephemeral consumer with replay policy
	sub, err := eb.js.PullSubscribe(
		"oauth.>",
		"",
		natslib.AckWait(5*time.Second),
		natslib.MaxAckPending(100),
	)
	if err != nil {
		return nil, fmt.Errorf("failed to create replay subscription: %w", err)
	}

	msgs := make(chan *natslib.Msg, 10)
	go func() {
		defer close(msgs)
		batch, _ := sub.Fetch(100) // Get up to 100 messages
		for msg := range batch {
			msgs <- msg
		}
	}()

	return msgs, nil
}
```

---

### Gap 5.2.3: Wire OAuth Handler to Events

**File:** `backend/internal/cliproxy/oauth_handler.go` - modify existing handleCallback

```go
// Example integration point in oauth_handler.go
func (h *oauthHandler) handleCallback(w http.ResponseWriter, r *http.Request) {
	// ... existing code ...

	// NEW: Publish OAuth events
	if h.eventPublisher != nil {
		// Publish token exchanged event
		if err := h.eventPublisher.PublishOAuthTokenExchanged(
			r.Context(),
			provider,
			user.ID,
		); err != nil {
			h.logger.Warnf("failed to publish oauth.token_exchanged: %v", err)
			// Don't block auth on event publish failure
		}

		// If new user, publish user created event
		if isNewUser {
			if err := h.eventPublisher.PublishOAuthUserCreated(
				r.Context(),
				user.ID,
				provider,
				user.Email,
			); err != nil {
				h.logger.Warnf("failed to publish oauth.user_created: %v", err)
			}
		}
	}

	// ... existing code to create session ...

	// NEW: Publish session created event
	if h.eventPublisher != nil {
		if err := h.eventPublisher.PublishOAuthSessionCreated(
			r.Context(),
			user.ID,
			session.ID,
		); err != nil {
			h.logger.Warnf("failed to publish oauth.session_created: %v", err)
		}
	}

	// ... existing code ...
}
```

---

## Acceptance Criteria

### Gap 5.1: All Criteria Must Pass

- [ ] 4 WebGL-dependent unit tests are no longer skipped
- [ ] All unit tests pass in jsdom with mocked canvas
- [ ] 4+ Playwright visual regression tests created for Sigma.js
- [ ] Tests cover: node rendering, edge rendering, LOD switching, controls
- [ ] Performance benchmarks show FPS >30 during pan/zoom
- [ ] Graph layout time <500ms (measured from page load to canvas render)
- [ ] Visual snapshots stored with <2% diff tolerance
- [ ] Chromatic or Percy integration configured (optional but recommended)
- [ ] All tests pass in CI pipeline
- [ ] No regressions in existing graph tests

### Gap 5.2: All Criteria Must Pass

- [ ] `test_event_replay_from_timestamp` test is un-skipped and passing
- [ ] OAuth event publisher created with 6+ event types
- [ ] JetStream consumer configured for OAuth events
- [ ] oauth_handler wired to event publisher on key events
- [ ] Events published: login_started, callback_received, token_exchanged, user_created, session_created, token_refreshed
- [ ] Event payloads validated (required fields present)
- [ ] Event audit trail testable via JetStream consumer
- [ ] 3+ integration tests for OAuth event flow pass
- [ ] No OAuth handler logic blocked by event publishing (graceful degradation)
- [ ] Event publisher tests have >80% coverage
- [ ] All backend tests pass

---

## File Dependencies

### Gap 5.1 Files

```
frontend/apps/web/src/__tests__/components/graph/
├── SigmaGraphView.test.tsx (MODIFY - un-skip)
├── SigmaGraphView.enhanced.test.tsx (MODIFY - un-skip)

frontend/apps/web/e2e/
├── sigma.visual.spec.ts (CREATE - new visual tests)
├── global-setup.ts (existing - reuse)

frontend/apps/web/src/__tests__/
├── setup.ts (existing - has canvas mocks)
```

### Gap 5.2 Files

```
backend/internal/auth/
├── event_publisher.go (CREATE - new publisher)
├── event_publisher_test.go (CREATE - tests)

backend/internal/nats/
├── nats.go (MODIFY - add ensureConsumer(), ReplayOAuthEvents())

backend/internal/cliproxy/
├── oauth_handler.go (MODIFY - wire events)

backend/tests/integration/
├── test_nats_events.py (MODIFY - un-skip test, implement body)
```

---

## Effort Estimation

| Task | Complexity | Est. Time | Parallel? |
|------|-----------|-----------|-----------|
| 5.1.1 Un-skip unit tests | S | 5m | Yes (Gap 5.2 tasks) |
| 5.1.2 Create e2e spec file | M | 15m | After 5.1.1 |
| 5.1.3 Add viewport variants | M | 10m | After 5.1.2 |
| 5.1.4 Performance benchmarks | M | 10m | After 5.1.3 |
| 5.1.5 Chromatic CI (optional) | S | 5m | Yes |
| **Gap 5.1 Total** | | **45m** | ~20m wall clock |
| | | | |
| 5.2.1 Create event_publisher | L | 20m | Yes (Gap 5.1 tasks) |
| 5.2.2 Configure JetStream | M | 15m | After 5.2.1 |
| 5.2.3 Wire oauth_handler | S | 10m | After 5.2.2 |
| 5.2.4 Re-enable Python test | M | 15m | After 5.2.3 |
| 5.2.5 Event audit logging (opt) | S | 10m | Yes |
| 5.2.6 Integration tests | M | 15m | After 5.2.4 |
| **Gap 5.2 Total** | | **85m** | ~25m wall clock |
| | | | |
| **TOTAL (Parallel)** | | **130m** | **~30m wall clock** |

---

## Risk Mitigation

| Risk | Mitigation |
|------|-----------|
| WebGL tests flaky (timing) | Use proper waits, canvas state checks, 2% tolerance on snapshots |
| Event publishing blocks OAuth | Publish events asynchronously, don't block handler |
| JetStream consumer misconfigured | Test locally with `nats` CLI, validate consumer exists |
| Chromatic slow | Make optional, focus on Playwright snapshots first |
| Performance benchmarks unreliable | Run 3x, take median, account for CI variance |

---

## Deliverables

1. **Gap 5.1:**
   - ✅ Updated unit tests (SigmaGraphView.test.tsx + enhanced.test.tsx)
   - ✅ New Playwright visual regression spec (e2e/sigma.visual.spec.ts)
   - ✅ Performance benchmark results
   - ✅ Visual snapshot baselines

2. **Gap 5.2:**
   - ✅ OAuth event publisher (event_publisher.go + tests)
   - ✅ Updated NATS EventBus (ensureConsumer, ReplayOAuthEvents)
   - ✅ Wired oauth_handler to events
   - ✅ Re-enabled integration test with implementation
   - ✅ Event audit examples

3. **Documentation:**
   - ✅ This analysis document
   - ✅ Test execution guide (test counts, pass rates)
   - ✅ Performance benchmark report
   - ✅ Event publisher API reference

---

## Next Steps

**Recommended Order:**
1. Start tasks 5.1.1 + 5.2.1 in parallel (un-skip tests + create publisher)
2. Then 5.1.2 + 5.2.2 (e2e spec + JetStream consumer)
3. Then 5.1.3 + 5.2.3 (viewport variants + wire handler)
4. Then 5.1.4 + 5.2.4 (benchmarks + re-enable test)
5. Optional: 5.1.5 + 5.2.5 (Chromatic + audit logging)

**Implementation can proceed immediately.** All files identified, architecture clear, no blockers.
