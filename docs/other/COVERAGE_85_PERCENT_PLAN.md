# Coverage 85%+ Plan: All Modules ≥80%

## Executive Summary

**Target**: 85% overall coverage, no individual module below 80%

| Metric | Current | Target | Gap |
|--------|---------|--------|-----|
| **Python Overall** | 12.1% | 85% | +9,702 lines |
| **Frontend** | ~0% | 85% | ~24,000 lines |
| **Go Backend** | ~60% | 85% | ~2,000 lines |

---

## Current State

### Python Modules (13,876 lines total)

| Module | Current | Target | Lines Needed | Priority |
|--------|---------|--------|--------------|----------|
| services | 4.8% | 80% | 2,906 | P0-CRITICAL |
| cli | 15.3% | 80% | 3,827 | P0-CRITICAL |
| tui | 0.0% | 80% | 810 | P0-CRITICAL |
| storage | 28.6% | 80% | 794 | P1-HIGH |
| api | 20.7% | 80% | 323 | P1-HIGH |
| repositories | 27.7% | 80% | 152 | P1-HIGH |
| utils | 0.0% | 80% | 76 | P2-MEDIUM |
| root files | 2.6% | 80% | 58 | P2-MEDIUM |
| schemas | 0.0% | 80% | 33 | P2-MEDIUM |
| core | 49.5% | 80% | 32 | P2-MEDIUM |
| database | 58.9% | 80% | 15 | P3-LOW |
| config | 81.2% | 80% | 0 | DONE |
| models | 94.0% | 80% | 0 | DONE |

### Frontend (28,129 lines in apps/web)

| Area | Files | Estimated Lines | Priority |
|------|-------|-----------------|----------|
| Components | ~80 | ~12,000 | P0-CRITICAL |
| Hooks | ~20 | ~2,000 | P0-CRITICAL |
| Stores | ~10 | ~1,500 | P0-CRITICAL |
| Utils/Helpers | ~15 | ~1,000 | P1-HIGH |
| API Client | ~10 | ~800 | P1-HIGH |
| Pages/Routes | ~30 | ~8,000 | P1-HIGH |

### Go Backend (estimated ~15,000 lines)

| Area | Current | Target | Priority |
|------|---------|--------|----------|
| Services | ~65% | 85% | P1-HIGH |
| Handlers | ~50% | 85% | P1-HIGH |
| Graph | ~40% | 85% | P1-HIGH |
| WebSocket | ~30% | 85% | P2-MEDIUM |

---

## Phase 1: Python Critical Modules (Week 1-2)

### 1.1 Services Module (2,906 lines needed)

**51 files, currently 4.8%**

#### Tier 1: Zero-coverage large files (Day 1-3)
```
bulk_operation_service.py      196 lines → need 157 lines
advanced_traceability_*.py     191 lines → need 153 lines
stateless_ingestion_service.py 364 lines → need 291 lines (partial)
cycle_detection_service.py     150 lines → need 120 lines
chaos_mode_service.py          138 lines → need 110 lines
critical_path_service.py        80 lines → need 64 lines
```

#### Tier 2: Agent services (Day 3-4)
```
agent_coordination_service.py   53 lines → need 42 lines
agent_metrics_service.py        47 lines → need 38 lines
agent_monitoring_service.py     60 lines → need 48 lines
agent_performance_service.py    72 lines → need 58 lines
```

#### Tier 3: Integration services (Day 4-5)
```
api_webhooks_service.py         74 lines → need 59 lines
cache_service.py                88 lines → need 70 lines
commit_linking_service.py       45 lines → need 36 lines
conflict_resolution_service.py  39 lines → need 31 lines
```

#### Tier 4: Remaining services (Day 5-7)
- Cover all remaining 0% files
- Increase partial coverage files to 80%

### 1.2 CLI Module (3,827 lines needed)

**40 files, currently 15.3%**

#### Tier 1: Storage helper & core (Day 1-2)
```
storage_helper.py              206 lines → need 165 lines
performance.py                  70 lines → need 56 lines
aliases.py                      64 lines → need 51 lines
completion.py                   37 lines → need 30 lines
help_system.py                  19 lines → need 15 lines
```

#### Tier 2: Low-coverage commands (Day 2-4)
```
agents.py        6.4%  → 80%
history.py       5.8%  → 80%
chaos.py         9.7%  → 80%
design.py        9.3%  → 80%
export.py       12.2%  → 80%
```

#### Tier 3: Medium-coverage commands (Day 4-5)
```
benchmark.py    17.1%  → 80%
cursor.py       20.3%  → 80%
droid.py        20.3%  → 80%
drill.py        22.0%  → 80%
dashboard.py    24.2%  → 80%
```

#### Tier 4: Higher-coverage commands (Day 5-6)
- Push all commands from 30-60% to 80%

### 1.3 TUI Module (810 lines needed)

**15 files, currently 0%**

#### Complete test suite needed:
```
tui/
├── apps/           → Dashboard, browser, graph app tests
├── widgets/        → All widget tests
├── adapters/       → Storage adapter tests
└── screens/        → Screen tests
```

**Strategy**: Create comprehensive unit tests with mocked Textual components

---

## Phase 2: Python Support Modules (Week 2)

### 2.1 Storage Module (794 lines needed)
- local_storage.py enhancement
- sync_engine.py edge cases
- file_watcher.py complete coverage
- markdown_parser.py edge cases

### 2.2 API Module (323 lines needed)
- main.py endpoint tests
- sync_client.py coverage
- Error handling paths

### 2.3 Repositories (152 lines needed)
- Edge cases for all repositories
- Error handling
- Query variations

### 2.4 Smaller Modules (Day 5-7)
- utils (76 lines)
- root files (58 lines)
- schemas (33 lines)
- core (32 lines)
- database (15 lines)

---

## Phase 3: Frontend Coverage (Week 2-3)

### 3.1 Test Infrastructure Setup (Day 1)

```typescript
// vitest.config.ts enhancements
export default defineConfig({
  test: {
    coverage: {
      provider: 'v8',
      reporter: ['text', 'json', 'html'],
      thresholds: {
        global: { lines: 85, functions: 85, branches: 80 }
      }
    }
  }
})
```

### 3.2 Component Tests (Day 2-5)

**UI Package (15 files)**
```
packages/ui/src/components/
├── Button.test.tsx
├── Input.test.tsx
├── Select.test.tsx
├── Dialog.test.tsx
├── Alert.test.tsx
├── Avatar.test.tsx
├── Badge.test.tsx
├── DropdownMenu.test.tsx
├── Progress.test.tsx
├── Skeleton.test.tsx
├── Tabs.test.tsx
├── Tooltip.test.tsx
└── utils.test.ts
```

**App Components (~80 files)**
- Group by feature area
- Use React Testing Library
- Mock API calls with MSW (already set up)

### 3.3 Store Tests (Day 5-6)

```
src/stores/
├── itemsStore.test.ts
├── syncStore.test.ts
├── websocketStore.test.ts
└── [other stores].test.ts
```

### 3.4 Hook Tests (Day 6-7)

```
src/hooks/
├── useItems.test.ts
├── useSync.test.ts
├── useWebSocket.test.ts
└── [other hooks].test.ts
```

### 3.5 Integration & E2E (Day 7-10)

- Expand existing 10 E2E specs
- Add component integration tests
- Visual regression tests (4 exist, expand)

---

## Phase 4: Go Backend (Week 3)

### 4.1 Service Coverage Expansion

```go
// internal/services/ - Target 85%
- item_service_test.go      → Add edge cases
- link_service_test.go      → Add edge cases
- project_service_test.go   → Add edge cases
- agent_service_test.go     → New comprehensive tests
```

### 4.2 Handler Coverage

```go
// internal/handlers/ - Target 85%
- item_handler_test.go      → Expand error paths
- link_handler_test.go      → Expand error paths
- project_handler_test.go   → Expand error paths
- agent_handler_test.go     → Expand error paths
```

### 4.3 Graph & WebSocket

```go
// internal/graph/ - Target 85%
- graph_algorithms_test.go  → Edge cases
- neo4j_queries_test.go     → Error handling

// internal/websocket/ - Target 85%
- presence_test.go          → Expand
- subscription_manager_test.go → Expand
```

---

## Execution DAG

```
                    ┌─────────────────────┐
                    │   Phase 0: Setup    │
                    │  Coverage Infra     │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Phase 1A:       │ │  Phase 1B:       │ │  Phase 1C:       │
│  Python Services │ │  Python CLI      │ │  Python TUI      │
│  (2,906 lines)   │ │  (3,827 lines)   │ │  (810 lines)     │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
           ┌──────────────────┼──────────────────┐
           │                  │                  │
           ▼                  ▼                  ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Phase 2A:       │ │  Phase 2B:       │ │  Phase 2C:       │
│  Storage (794)   │ │  API (323)       │ │  Repos (152)     │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Phase 2D:         │
                    │   Small Modules     │
                    │   (214 lines)       │
                    └──────────┬──────────┘
                               │
           ┌───────────────────┼───────────────────┐
           │                   │                   │
           ▼                   ▼                   ▼
┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐
│  Phase 3A:       │ │  Phase 3B:       │ │  Phase 3C:       │
│  Frontend UI     │ │  Frontend Stores │ │  Frontend Hooks  │
│  Components      │ │  & Utils         │ │  & Pages         │
└────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘
         │                    │                    │
         └────────────────────┼────────────────────┘
                              │
                              ▼
                    ┌─────────────────────┐
                    │   Phase 4:          │
                    │   Go Backend        │
                    │   Enhancement       │
                    └──────────┬──────────┘
                               │
                              ▼
                    ┌─────────────────────┐
                    │   Phase 5:          │
                    │   Validation &      │
                    │   Final Report      │
                    └─────────────────────┘
```

---

## Parallel Execution Strategy

### Batch 1 (Can run in parallel)
- [ ] Phase 1A: Services tests
- [ ] Phase 1B: CLI tests
- [ ] Phase 1C: TUI tests

### Batch 2 (After Batch 1)
- [ ] Phase 2A: Storage tests
- [ ] Phase 2B: API tests
- [ ] Phase 2C: Repository tests

### Batch 3 (After Batch 2)
- [ ] Phase 2D: Small modules
- [ ] Phase 3A: Frontend components

### Batch 4 (After Batch 3)
- [ ] Phase 3B: Frontend stores
- [ ] Phase 3C: Frontend hooks/pages
- [ ] Phase 4: Go backend

### Batch 5 (Final)
- [ ] Validation run
- [ ] Gap filling
- [ ] Final report

---

## Test Templates

### Python Service Test Template
```python
"""Tests for {service_name} - targeting 80%+ coverage."""
import pytest
from unittest.mock import Mock, patch, AsyncMock
from tracertm.services.{service_file} import {ServiceClass}

class Test{ServiceClass}:
    """Comprehensive tests for {ServiceClass}."""

    @pytest.fixture
    def service(self):
        """Create service instance with mocked dependencies."""
        return {ServiceClass}(
            repository=Mock(),
            # other deps
        )

    # Happy path tests
    def test_{method}_success(self, service):
        """Test {method} with valid input."""
        pass

    # Edge cases
    def test_{method}_empty_input(self, service):
        """Test {method} with empty input."""
        pass

    def test_{method}_invalid_input(self, service):
        """Test {method} with invalid input."""
        pass

    # Error handling
    def test_{method}_repository_error(self, service):
        """Test {method} when repository raises error."""
        pass

    # Async tests if applicable
    @pytest.mark.asyncio
    async def test_{method}_async(self, service):
        """Test async {method}."""
        pass
```

### Frontend Component Test Template
```typescript
import { render, screen, fireEvent } from '@testing-library/react'
import { describe, it, expect, vi } from 'vitest'
import { ComponentName } from './ComponentName'

describe('ComponentName', () => {
  // Rendering tests
  it('renders correctly with default props', () => {
    render(<ComponentName />)
    expect(screen.getByRole('...')).toBeInTheDocument()
  })

  // Props tests
  it('applies custom className', () => {
    render(<ComponentName className="custom" />)
    expect(screen.getByRole('...')).toHaveClass('custom')
  })

  // Interaction tests
  it('handles click events', () => {
    const onClick = vi.fn()
    render(<ComponentName onClick={onClick} />)
    fireEvent.click(screen.getByRole('...'))
    expect(onClick).toHaveBeenCalled()
  })

  // State tests
  it('updates state on interaction', () => {
    render(<ComponentName />)
    // test state changes
  })

  // Edge cases
  it('handles empty data gracefully', () => {
    render(<ComponentName data={[]} />)
    expect(screen.getByText('No data')).toBeInTheDocument()
  })
})
```

---

## Success Criteria

### Python
- [ ] Overall coverage ≥ 85%
- [ ] services ≥ 80%
- [ ] cli ≥ 80%
- [ ] tui ≥ 80%
- [ ] storage ≥ 80%
- [ ] api ≥ 80%
- [ ] repositories ≥ 80%
- [ ] All other modules ≥ 80%

### Frontend
- [ ] Overall coverage ≥ 85%
- [ ] Components ≥ 80%
- [ ] Stores ≥ 80%
- [ ] Hooks ≥ 80%
- [ ] Utils ≥ 80%

### Go Backend
- [ ] Overall coverage ≥ 85%
- [ ] Services ≥ 80%
- [ ] Handlers ≥ 80%
- [ ] Graph ≥ 80%

---

## Estimated Effort

| Phase | Lines | Est. Tests | Est. Hours |
|-------|-------|------------|------------|
| 1A: Services | 2,906 | ~200 | 20-25 |
| 1B: CLI | 3,827 | ~250 | 25-30 |
| 1C: TUI | 810 | ~60 | 8-10 |
| 2A: Storage | 794 | ~50 | 6-8 |
| 2B: API | 323 | ~30 | 4-5 |
| 2C: Repos | 152 | ~20 | 3-4 |
| 2D: Small | 214 | ~25 | 3-4 |
| 3: Frontend | ~24,000 | ~400 | 40-50 |
| 4: Go | ~2,000 | ~100 | 15-20 |
| **TOTAL** | ~35,000 | ~1,135 | **120-156** |

---

## Next Steps

1. **Immediate**: Start Phase 1A/1B/1C in parallel
2. **Setup**: Configure coverage thresholds in CI
3. **Monitor**: Run coverage reports after each phase
4. **Adjust**: Fill gaps as discovered
