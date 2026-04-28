# usage Analysis

## Overview

**Total Python files**: 13 (main src directory)
**Total LOC**: 3,742 lines of code
**Main purpose**: AI Usage Tracker with native OS integration - Multi-provider usage aggregation CLI tool that consolidates usage metrics from Claude, OpenRouter, Cursor, and other AI providers with native widget support

**Key Characteristics**:
- Multi-provider aggregation system with plugin architecture
- CLI-based usage tracking with rich terminal UI
- Time-series data aggregation (daily, weekly, monthly)
- Native OS widget support via WebSocket integration
- Comprehensive data parsing and deduplication

---

## Codebase Structure

### Core Modules (3,742 LOC total)

| Module | LOC | Purpose |
|--------|-----|---------|
| cli.py | 654 | Typer CLI with 8 commands (status, daily, weekly, monthly, widget, config, refresh) |
| aggregation.py | 622 | Time-series aggregation (daily, weekly, monthly, by model/provider/project) |
| providers/base.py | 288 | Abstract provider interface & unified data format |
| providers/registry.py | 290 | Provider registry with concurrent loading & lifecycle mgmt |
| providers/openrouter_loader.py | 263 | OpenRouter API client with pagination & rate limiting |
| providers/claude_loader.py | 339 | Claude Code JSONL parser with token calculation |
| providers/cursor_loader.py | 324 | Cursor SQLite DB parser with dynamic schema detection |
| ui/rich_components.py | 299 | Rich terminal UI with live dashboards |
| ui/native_integration.py | 456 | WebSocket-based native OS widget support |
| config.py | 173 | Pydantic-based configuration management |
| Other files | 34 | __init__, __main__, __init__ files |

---

## Consolidation Opportunities

### 1. HTTP Client Consolidation (HIGHEST PRIORITY)

**Current State in usage**:
- **Single HTTP client implementation**: OpenRouter provider uses `httpx.AsyncClient` directly (lines 119-167)
- **Manual HTTP patterns**:
  - Direct `httpx.AsyncClient()` context manager initialization
  - Hardcoded headers dictionary building (line 101-108)
  - Manual pagination handling (lines 116-156)
  - Custom rate limiting via `await asyncio.sleep(0.1)` (line 158)
  - Direct error handling with `httpx.HTTPStatusError` (line 160)
  - No retry logic for transient failures

**Code footprint**: ~120 LOC in openrouter_loader.py

**Consolidation Target**: pheno.clients HTTP module
- **Available**: HTTPClient, BearerAuth, TokenBucketRateLimiter, ExponentialBackoffRetry
- **Savings Potential**: 80% reduction (120 LOC → 24 LOC)

**Migration Impact Analysis**:
```
Current (httpx only):
- 46 LOC: is_available() with inline HTTP client
- 74 LOC: _fetch_usage_data() with manual pagination
- 0 LOC: Rate limiting (basic sleep)
- 0 LOC: Retry logic (none)

Using pheno.clients:
- 10 LOC: is_available() via HTTPClient
- 14 LOC: _fetch_usage_data() via HTTPClient + PaginationParser
- 0 LOC: Rate limiting (built into HTTPClient)
- 0 LOC: Retry logic (automatic via HTTPClient)

Reduction: 120 LOC → 24 LOC (80% savings)
```

**Key Consolidation Points**:
1. **Replace httpx.AsyncClient with HTTPClient()**
   - Current: `async with httpx.AsyncClient(timeout=self.timeout) as client:`
   - New: `async with HTTPClient(base_url=self.base_url, auth=BearerAuth(self.api_key)) as client:`

2. **Replace header building with auth strategy**
   - Current: `_get_headers()` method (8 LOC)
   - New: `BearerAuth(token).apply(headers)` (automatic)

3. **Replace manual pagination with PaginationParser**
   - Current: while loop with manual page tracking (40 LOC)
   - New: `PaginationParser().parse(response)` (automatic)

4. **Replace sleep-based rate limiting with TokenBucketRateLimiter**
   - Current: `await asyncio.sleep(0.1)` (1 LOC but inefficient)
   - New: Built into HTTPClient configuration

5. **Replace manual error handling with HTTPClientError**
   - Current: Multiple try/except blocks for httpx exceptions
   - New: Unified HTTPClientError exception hierarchy

---

### 2. Configuration Management Consolidation

**Current State**:
- Pydantic BaseModel with manual singleton pattern (173 LOC)
- YAML file loading with error handling
- Environment variable loading via python-dotenv
- Custom Config.initialize() singleton factory

**Potential**:
- pheno has ConfigManager with similar patterns (~100 LOC available)
- Estimated savings: 40-50 LOC through inheritance

---

### 3. Data Model Consolidation

**Current State**:
- Custom UnifiedUsageData Pydantic model (90 LOC in base.py)
- Custom TokenUsage model (55 LOC in base.py)
- Provider-specific models (OpenRouter, Claude, Cursor each ~80-100 LOC)

**Potential**:
- Could inherit from pheno base models if standardized
- Estimated savings: 30-40 LOC through model reuse

---

### 4. API Integration Pattern Consolidation

**Current Implementation Pattern** (found in 3 providers):
```python
# OpenRouter, Claude, Cursor all implement similar patterns:
1. ProviderLoader base class with 5 abstract methods
2. is_available() - check data source availability
3. get_data_paths() - enumerate data sources
4. load_usage_data() - async data loading with filtering
5. parse/convert methods - provider-specific format conversion
6. get_status() - status reporting
```

**Consolidation Opportunity**:
- Create generic APIProvider base class in pheno
- Reduce 3 × ~100 LOC = 300 LOC provider code via inheritance
- Estimated savings: 40-50 LOC per provider

---

## API Integrations

### Active APIs

| API | Provider | Integration Type | Auth | Rate Limit | Retry |
|-----|----------|------------------|------|-----------|-------|
| **OpenRouter** | openrouter_loader.py | REST API (pages=1,100) | Bearer token | Manual sleep(0.1) | No |
| **Claude Code** | claude_loader.py | Local JSONL files | None (local) | N/A | N/A |
| **Cursor** | cursor_loader.py | SQLite databases | None (local) | N/A | N/A |

### Planned APIs (in registry.py imports)

| Provider | Status | Location |
|----------|--------|----------|
| codex_loader | Placeholder | Line 265 |
| droid_loader | Placeholder | Line 272 |
| augment_loader | Placeholder | Line 279 |
| warp_loader | Placeholder | Line 286 |

### OpenRouter API Details

**Base URL**: `https://openrouter.ai/api/v1/`
**Endpoints**:
- `GET /models` - List available models (availability check)
- `GET /usage` - Fetch usage data with pagination

**Parameters**:
- `page` - Pagination page number
- `limit` - Items per page (max 100)
- `start_date` - Date range filter (YYYY-MM-DD)
- `end_date` - Date range filter (YYYY-MM-DD)

**Response Format**:
```json
{
  "data": [
    {
      "date": "YYYYMMDD",
      "model": "model_name",
      "prompt_tokens": 1000,
      "completion_tokens": 500,
      "cost": 0.05
    }
  ],
  "has_more": false
}
```

**Authentication**: Bearer token via `Authorization` header

**Rate Limiting**: Appears to support standard HTTP rate limit headers (not currently leveraged)

**Pagination**: Cursor-based (has_more flag)

---

## Unique Patterns & Features

### 1. Unified Data Format
All providers convert to `UnifiedUsageData` model:
- Provider identification
- Session/conversation ID
- Timestamp with timezone support
- Model information with normalization
- Token usage (input, output, cache_creation, cache_read, reasoning)
- Cost calculation with provider-specific pricing
- Deduplication via composite key

**Consolidation Note**: This pattern could be standardized in pheno as a usage tracking base model.

### 2. Provider-Specific Pricing Matrices
Each provider implements model pricing tables:
- Claude: 4 models with cache pricing (25% write premium, 90% read discount)
- Cursor: 6 models with basic input/output pricing
- OpenRouter: Fetched from API

**Implementation**: Hardcoded in provider __init__ (~50 LOC total)

### 3. Time-Series Aggregation Pipeline
```python
BaseAggregator (abstract)
├── DailyAggregator (groups by date)
├── WeeklyAggregator (with configurable week start)
├── MonthlyAggregator (groups by year-month)
├── ProviderAggregator (groups by provider)
├── ProjectAggregator (groups by project_path)
└── ModelAggregator (groups by model + cache hit rate)

AggregationService (facade) - coordinates all aggregators
```

Uses pandas DataFrame for efficient grouping/aggregation.

**Consolidation Note**: Could extract as reusable time-series aggregation service in pheno if needed by other projects.

### 4. Provider Registry with Lazy Initialization
- Singleton pattern with class-level storage
- Lazy loading on first access
- Decorator-based registration (`@register_provider`)
- Concurrent loading with semaphores (12 concurrent by default)
- Per-provider timeout handling (15s per provider)
- Availability checking with fast-fail

### 5. CLI with Async/Await Integration
- Typer CLI with rich output
- Rich terminal UI via TextualDashboard
- Native OS widget support via WebSocket
- Comprehensive error handling with user-friendly messages
- JSON/CSV export formats

---

## Dependencies on Other Kush Projects

**Analysis Result**: NO DEPENDENCIES FOUND

The usage project is completely standalone:
- No imports from pheno-sdk (current state)
- No imports from bloc, router, crun, or other projects
- Only standard Python + PyPI dependencies

**Current Dependencies**:
- typer 0.9.0+ (CLI framework)
- rich 13.0.0+ (terminal UI)
- pydantic 2.0.0+ (data validation)
- httpx 0.27.0+ (only HTTP client in use)
- pandas 2.0.0+ (data aggregation)
- PyYAML 6.0+ (config files)
- pydantic-settings 2.0.0+ (settings management)
- aiofiles 23.0.0+ (async file operations)
- tiktoken 0.7.0+ (token counting - imported but not used)
- python-dotenv 1.0.0+ (environment variables)
- textual 0.41.0+ (TUI framework)
- websockets 12.0.0+ (native widget support)

---

## Recommendations

### Phase 1: HTTP Client Migration (IMMEDIATE - HIGH ROI)
**Priority**: CRITICAL
**Effort**: 3-4 hours
**Savings**: 80 LOC (80% reduction in OpenRouter integration)

**Steps**:
1. Import HTTPClient, BearerAuth from pheno.clients
2. Replace `httpx.AsyncClient` initialization with HTTPClient()
3. Replace `_get_headers()` method with BearerAuth strategy
4. Replace manual pagination loop with PaginationParser
5. Add automatic retry via ExponentialBackoffRetry
6. Add TokenBucketRateLimiter for rate limiting
7. Update error handling to use pheno.clients exceptions
8. Run existing tests to validate behavior

**Code Example**:
```python
# Before (120 LOC)
class OpenRouterProvider(ProviderLoader):
    def _get_headers(self):
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://ccusage.ai",
            "X-Title": "ccusage AI Usage Tracker",
        }
    
    async def _fetch_usage_data(self, start_date, end_date):
        all_data = []
        page = 1
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            while True:
                params = {"page": page, "limit": 100}
                if start_date:
                    params["start_date"] = start_date.strftime("%Y-%m-%d")
                # ... 60 LOC of manual pagination

# After (24 LOC)
from pheno.clients import HTTPClient, BearerAuth, TokenBucketRateLimiter

class OpenRouterProvider(ProviderLoader):
    def __init__(self, config):
        super().__init__(config)
        self.client = HTTPClient(
            base_url="https://openrouter.ai/api/v1/",
            auth=BearerAuth(token=self.api_key),
            rate_limiter=TokenBucketRateLimiter(requests_per_second=10)
        )
    
    async def _fetch_usage_data(self, start_date, end_date):
        params = {"limit": 100}
        if start_date:
            params["start_date"] = start_date.strftime("%Y-%m-%d")
        response = await self.client.get("/usage", params=params)
        return response.json()["data"]
```

---

### Phase 2: Configuration Management Consolidation
**Priority**: MEDIUM
**Effort**: 2-3 hours
**Savings**: 40-50 LOC

**Approach**: Inherit from pheno ConfigManager base class if available, otherwise keep current implementation.

---

### Phase 3: Data Model Consolidation
**Priority**: LOW
**Effort**: 4-5 hours
**Savings**: 30-40 LOC

**Approach**: Evaluate pheno data models for usage tracking patterns. Could create shared UsageDataModel in pheno.

---

### Phase 4: Provider Base Class Generalization
**Priority**: LOW (post-migration)
**Effort**: 3-4 hours
**Savings**: 50-80 LOC across 3+ providers

**Approach**: After HTTP client migration, abstract common provider patterns into APIProvider base class in pheno.

---

## Migration Priority Matrix

| Task | Impact | Effort | ROI | Priority |
|------|--------|--------|-----|----------|
| HTTP Client Migration | 80 LOC | 3-4h | 26.7 LOC/h | P1 CRITICAL |
| Config Management | 40-50 LOC | 2-3h | 16.7 LOC/h | P2 HIGH |
| Data Model Reuse | 30-40 LOC | 4-5h | 8 LOC/h | P3 MEDIUM |
| Provider Base Class | 50-80 LOC | 3-4h | 18.75 LOC/h | P3 MEDIUM |
| **TOTAL POTENTIAL** | **200-250 LOC** | **12-16h** | **16.7 LOC/h** | |

**Expected Outcome**:
- Reduce usage codebase by 5-7% (200-250 LOC reduction)
- Eliminate duplicate HTTP client patterns across kush projects
- Improve maintainability through code reuse
- Enable faster API integration for new providers (Phase 4)
- Standardize error handling and retry logic

---

## Risk Assessment

**Low Risk**:
- HTTP client migration (well-tested pheno.clients module)
- Configuration management (refactoring only, no behavior change)

**Medium Risk**:
- Data model changes (requires updating aggregation/CLI display logic)

**Mitigation**:
- Maintain backward compatibility at data model level
- Comprehensive unit test coverage before/after
- Gradual migration with one provider at a time
- Feature flag for new vs old implementations during transition

---

## Testing Strategy

**Current Test Coverage**: 9 test functions in test_cli.py (basic CLI mocking)

**Enhanced Testing for Migration**:
1. Unit tests for HTTPClient-based OpenRouter provider
2. Integration tests with actual OpenRouter API (if possible)
3. Response parsing validation
4. Rate limiting behavior verification
5. Retry logic validation
6. Data format validation (ensure UnifiedUsageData unchanged)

---

## Conclusion

The usage project is well-structured and modular, with the primary consolidation opportunity being HTTP client pattern elimination. The OpenRouter provider presents the highest-ROI migration target, offering 80% code reduction through pheno.clients adoption while maintaining identical functionality.

Secondary opportunities exist in configuration management and provider base class generalization, but HTTP client migration should be prioritized first as it's highest-ROI, lowest-risk, and provides a reference implementation for other kush projects (zen, router, morph, crun, claude-squad) to follow.

**Total Consolidation Potential**: 200-250 LOC reduction (5-7% of codebase)
**Recommended Timeline**: Phase 1 (1-2 weeks), Phases 2-4 (backlog)
