# Playwright Python: Comparison Matrices & Decision Tables

**Purpose:** Quick decision-making reference for common Playwright scenarios
**Format:** Matrices, decision trees, and comparison tables

---

## 1. Video Recording: Configuration Comparison

### Video Size Options

| Use Case | Width | Height | Quality | File Size | Notes |
|----------|-------|--------|---------|-----------|-------|
| CI/CD Logs | 640 | 480 | Standard | 5-10 MB | Minimal for storage |
| Developer Debug | 1280 | 720 | HD | 15-25 MB | **Recommended default** |
| High-Res Archive | 1920 | 1080 | Full HD | 30-50 MB | Maximum quality |
| Mobile Testing | 375 | 667 | Mobile | 3-8 MB | Phone viewport |
| Tablet Testing | 768 | 1024 | Tablet | 8-15 MB | Tablet viewport |
| Default | 800 | 800 | Standard | 10-15 MB | Auto aspect ratio |

**Decision Table:**
```
IF test_type == "CI":
  THEN use_size = (1280, 720)
ELSE IF test_type == "mobile":
  THEN use_size = (375, 667)
ELSE IF test_type == "archive":
  THEN use_size = (1920, 1080)
ELSE:
  THEN use_size = (1280, 720)  # Default
```

### Video Retention Strategies

| Strategy | Use Case | Retention | Storage | CI-Friendly |
|----------|----------|-----------|---------|-------------|
| **No Recording** | Dev only, fast feedback | N/A | None | Yes |
| **Retain All** | Debugging, investigation | All tests | 50+ GB | No |
| **Retain on Failure** | Standard testing | Failed only | 5-10 GB | **Yes** |
| **Retain on Error** | Error tracking | Errors only | 2-5 GB | Yes |
| **Sampling** | Performance analysis | Random 5% | 500 MB | Yes |
| **Time-Based** | Temporary logs | 7 days | Rolling | Yes |

**Recommended Approach for Different Environments:**

| Environment | Strategy | Configuration |
|-------------|----------|---|
| Local Development | No Recording (video on demand) | `record_video_dir="videos/"` only when needed |
| Feature Branch | Retain on Failure | `--video=retain-on-failure` |
| Main Branch CI | Retain on Failure + Archive | Save to external storage |
| Release Testing | Retain All | Full recording, archival storage |
| Performance Test | Sampling | Record 10% of tests |

---

## 2. Screenshot Strategies Comparison

### Screenshot Types Matrix

| Type | Scope | Use Case | Performance | Reliability |
|------|-------|----------|-------------|-------------|
| **Full Page** | Entire scrollable | Visual regression, complete state | Slower (100-500ms) | High |
| **Viewport** | Visible area only | Quick status checks | Fast (50-150ms) | Medium |
| **Element** | Single component | Detailed element testing | Fastest (20-50ms) | High |
| **Clipped** | Region of interest | Focused testing | Fast (30-100ms) | High |
| **Base64** | In-memory bytes | API/comparison | Fastest (10-30ms) | High |

### Screenshot Capture Decision Tree

```
START: Need screenshot?
  |
  ├─ "Need complete page?"
  |   ├─ YES → full_page=True
  |   |   └─ "Multiple pages in test?"
  |   |       ├─ YES → Use asyncio.gather() for parallel
  |   |       └─ NO → Sequential capture
  |   |
  |   └─ NO → "Specific element?"
  |       ├─ YES → locator.screenshot()
  |       |   └─ "Need precise region?"
  |       |       ├─ YES → Use clip parameter
  |       |       └─ NO → Element bounding box
  |       |
  |       └─ NO → Viewport only (default)
  |
  ├─ "Save to disk?"
  |   ├─ YES → path="screenshot.png"
  |   └─ NO → await page.screenshot() → bytes
  |
  └─ "Format preference?"
      ├─ PNG → type="png" (default, lossless)
      └─ JPEG → type="jpeg", quality=85
```

### Screenshot Timing Strategies

| Wait Strategy | Timing | Use Case | Reliability |
|---------------|--------|----------|-------------|
| **No Wait** | Immediate | Static content | Low |
| **Load State** | DOM ready | Initial render | Medium |
| **Network Idle** | Network done | API calls completed | High |
| **Custom Wait** | Element visible | Dynamic content loaded | High |
| **Fixed Delay** | await.wait_for_timeout() | Animation complete | Medium |
| **Combined** | Multiple conditions | Complex flows | **Highest** |

**Recommended Combinations:**

```python
# Static page - fast
await page.wait_for_load_state("domcontentloaded")
await page.screenshot()

# Dynamic content - reliable
await page.wait_for_selector(".content-loaded")
await page.wait_for_load_state("networkidle")
await page.screenshot()

# Complex animation
await page.wait_for_load_state("networkidle")
await page.evaluate("() => new Promise(r => setTimeout(r, 500))")
await page.screenshot()
```

---

## 3. Trace Recording: Capabilities Comparison

### Trace Data Components

| Component | Enabled | Size Impact | Use Case | Recovery Value |
|-----------|---------|-------------|----------|---|
| **Screenshots** | `True` | +50% | Visual debugging | High |
| **Snapshots** | `True` | +100% | DOM inspection | High |
| **Sources** | `True` | +20% | Code reference | Medium |
| **Network** | Auto | +30% | API/request debug | High |
| **Logs** | Auto | +10% | Error tracking | Medium |
| All Enabled | Full | +200% | Investigation | **Highest** |
| Minimal | Screenshots only | +50% | Balanced | Medium |

### Trace Storage Comparison

| Configuration | Trace Size | Retrieval Time | Use Case |
|---------------|-----------|---|---|
| Screenshots only | 30-50 MB | Fast (5s) | Quick analysis |
| Screenshots + Snapshots | 60-100 MB | Medium (10s) | Detailed debug |
| Full (all components) | 150-250 MB | Slow (30s) | Investigation |
| Multiple chunks | ~100 MB total | Fast (5s per chunk) | **Long tests** |

---

## 4. Async vs Sync API Decision Matrix

### Capability Comparison

| Capability | Sync | Async | Difference |
|-----------|------|-------|-----------|
| **Blocking** | Blocks thread | Non-blocking | Async allows concurrent ops |
| **Learning Curve** | Easy | Intermediate | Async requires asyncio knowledge |
| **Context Manager** | `with` | `async with await` | Syntax differs |
| **Performance** | Single-threaded | Parallel capable | Async ~30% faster in CI |
| **Fixtures** | @pytest.fixture | @pytest_asyncio.fixture | Different fixture decorators |
| **Error Handling** | try/except | try/except | Same pattern |
| **Browser Count** | Sequential | Concurrent | Critical for scale |
| **Code Complexity** | Lower | Higher | More await keywords |
| **Team Familiarity** | Standard | Less common | Async less familiar to QA |

### Decision Tree: Sync vs Async

```
START: Choosing API type
  |
  ├─ "Need parallel test execution?"
  |   ├─ YES → "CI/CD environment?"
  |   |   ├─ YES → ASYNC (use -n 4)
  |   |   └─ NO → ASYNC or SYNC
  |   └─ NO → SYNC (simpler)
  |
  ├─ "Team expertise?"
  |   ├─ "Async familiar" → ASYNC
  |   ├─ "Only Python" → SYNC
  |   └─ "Python + async" → ASYNC
  |
  ├─ "Performance critical?"
  |   ├─ "Need sub-second" → ASYNC
  |   └─ "Standard timing OK" → SYNC
  |
  └─ DECISION:
      IF parallel_needed OR async_expert OR performance_critical:
        THEN use ASYNC
      ELSE:
        THEN use SYNC
```

### Resource Usage Comparison

| Aspect | Sync | Async |
|--------|------|-------|
| Memory per browser | ~150 MB | ~150 MB |
| Memory per context | ~50 MB | ~50 MB |
| CPU overhead | Low | Medium |
| Thread count | N (tests) | 1 + event loop |
| Parallel tests (CI) | N × duration | (N × duration) / 4 |
| GIL impact | Yes | No (event loop) |

---

## 5. Headless vs Headed Mode Comparison

### Mode Selection Matrix

| Factor | Headless | Headed | Recommendation |
|--------|----------|--------|---|
| **Speed** | 20-30% faster | Baseline | Headless in CI |
| **Memory** | Lower | Higher | Headless for scale |
| **Visual Debug** | None | Full | Headed for development |
| **Automation** | Full | Full | Either works |
| **Devtools** | Limited | Full | Headed for debugging |
| **CI-Friendly** | Yes | No | Headless required |
| **Local Dev** | Possible | Better | Headed recommended |

### Performance Metrics

```
Test Type: 10 tests (each 3 seconds)

HEADLESS:
- Chromium:  18s total (parallel: 4.5s with 4 workers)
- Firefox:   20s total (parallel: 5s with 4 workers)
- WebKit:    22s total (parallel: 5.5s with 4 workers)

HEADED:
- Chromium:  22s total (parallel: 5.5s with 4 workers)
- Firefox:   25s total (parallel: 6.5s with 4 workers)
- WebKit:    27s total (parallel: 7s with 4 workers)

SLOWMO 500ms:
- Headless:  65s total
- Headed:    75s total

Result: Headless + parallel = 3-4x faster
```

### Environment Decision Table

| Environment | Mode | Slowmo | Devtools | Video | Trace |
|---|---|---|---|---|---|
| **CI (Main)** | Headless | 0 | No | retain-on-failure | on |
| **CI (Feature)** | Headless | 0 | No | retain-on-failure | retain-on-failure |
| **Local Dev** | Headed | 100-500 | Yes | on | on |
| **Debug Session** | Headed | 500+ | Yes | on | on |
| **Performance** | Headless | 0 | No | No | No |
| **Pull Request** | Headless | 0 | No | retain-on-failure | No |

---

## 6. pytest Configuration Comparison

### Fixture Scope Matrix

| Fixture | Scope | Teardown | Use Case | Memory |
|---------|-------|----------|----------|--------|
| **Function** | Per test | After each | Isolation | Low |
| **Class** | Per class | After class | Group tests | Medium |
| **Module** | Per file | After file | Shared setup | Medium |
| **Session** | All tests | After all | Once only | High |

### Configuration Strategy Matrix

| Aspect | Development | CI/CD | Production |
|--------|---|---|---|
| Browser | Chromium | Multi (Chromium + Firefox) | Chromium + Safari |
| Headless | False | True | True |
| Video | Always | Retain-on-failure | Never |
| Trace | Always | Retain-on-failure | Never |
| Screenshot | On failure | Only-on-failure | Never |
| Parallel | -n 2 | -n auto | -n 4 |
| Timeout | 30s | 10s | 5s |
| Slowmo | 100ms | 0ms | 0ms |

---

## 7. Debugging Strategy Comparison

### Debugging Tools Matrix

| Tool | Trigger | Access | Learning | Effectiveness |
|------|---------|--------|----------|---|
| **PWDEBUG** | `PWDEBUG=1` | Inspector GUI | Medium | **Highest** |
| **page.pause()** | Code | Inspector pause | Low | High |
| **--headed** | Flag | Visual execution | Low | Medium |
| **--slowmo** | Flag | Slow execution | Low | Medium |
| **Videos** | Flag/Config | Post-analysis | Low | Medium |
| **Traces** | Flag/Config | trace.playwright.dev | High | High |
| **Screenshots** | Code/Flag | File inspection | Low | Low |
| **Logs** | DEBUG env | Console output | Medium | Medium |

### Debugging Workflow Decision Tree

```
Test Failed!
  |
  ├─ "Can reproduce locally?"
  |   ├─ YES → Run with PWDEBUG=1
  |   |   └─ Use Inspector to step through
  |   |
  |   └─ NO → "CI failure only?"
  |       └─ Review video + trace
  |
  ├─ "Quick fix needed?"
  |   ├─ YES → Review video in slow motion
  |   |
  |   └─ NO → "Deep investigation?"
  |       └─ Open trace in trace.playwright.dev
  |
  ├─ "Intermittent failure?"
  |   ├─ "Timing issue?" → Add wait strategy
  |   ├─ "Network issue?" → Check trace network tab
  |   └─ "Selector issue?" → Use pick locator in inspector
  |
  └─ "Fixed?"
      ├─ YES → Commit & test
      └─ NO → Escalate (file issue)
```

---

## 8. Performance & Resource Planning

### CI/CD Resource Allocation

| Metric | Value | Notes |
|--------|-------|-------|
| Test duration baseline | 3-5s per test | Including setup/teardown |
| Parallel tests (4 workers) | ~1.2x overhead | Shared resources |
| Memory per browser | 150-200 MB | Includes context |
| Memory per context | 50-100 MB | Depends on page complexity |
| Video encoding | ~15% CPU | Background process |
| Trace overhead | ~10% slowdown | DOM snapshots |
| Maximum parallel (4 CPU) | -n 4 | Diminishing returns beyond 4 |

### Storage Planning

| Artifact | Size Per Test | Retention | Annual Storage |
|----------|---|---|---|
| Video (720p) | 10-20 MB | 7 days | 100 GB (2000 tests) |
| Trace | 30-50 MB | 30 days | 300 GB (2000 tests) |
| Screenshot | 100-500 KB | On failure | 10 GB (2000 tests) |
| Logs | 10-50 KB | On failure | 1 GB (2000 tests) |
| **Total** | **~50 MB** | **Mixed** | **~411 GB** |

**Mitigation:**
- Compress old videos (75% reduction)
- Delete traces after 7 days
- Archive to S3/cloud storage
- Estimate ~100-150 GB for active retention

---

## 9. Browser Selection Matrix

### Browser Feature Support

| Feature | Chromium | Firefox | WebKit | Recommended |
|---------|----------|---------|--------|---|
| **CSS** | Full | Full | Full | All equal |
| **JavaScript** | Full | Full | Full | All equal |
| **Canvas** | Full | Full | Full | All equal |
| **WebGL** | Full | Full | Partial | Chromium |
| **Cookies/Storage** | Full | Full | Full | All equal |
| **Network** | Full | Full | Full | All equal |
| **Audio/Video** | Full | Full | Full | All equal |
| **Speed** | Fast | Fast | Slower | Chromium/Firefox |
| **Image** | Largest | Medium | Small | Chromium |
| **Stability** | Highest | High | Medium | Chromium |
| **CI Time** | Baseline | +15% | +30% | Chromium first |

### Testing Strategy by Browser

```
Cross-Browser Testing Approach:

TIER 1 - Always:
  ├─ Chromium (main browser, fast)
  └─ Firefox (alternative engine)

TIER 2 - Nightly:
  └─ WebKit (less common, slower)

TIER 3 - Release:
  ├─ Chromium (Windows, Mac, Linux variants)
  ├─ Firefox (Windows, Mac, Linux variants)
  └─ WebKit (Mac only, Windows via direct)

CI Recommendation:
- Feature branch: Chromium only (speed)
- Main branch: Chromium + Firefox (coverage)
- Release: All 3 browsers (comprehensive)
```

---

## 10. Implementation Complexity vs Capability Matrix

### Feature Implementation Effort

```
                    Implementation Effort
        Low              Medium             High
        |                  |                 |
Easy    | Basic video      | Fixture arch.   | Parallel async
        | Screenshots      | Trace recording | Multi-browser
        | Simple pytest    | Video mgmt      | CI/CD pipeline
        |                  |                 |
Medium  | Error capture    | Async impl.     | Enterprise arch.
        | Artifact org.    | Wait strategies | Performance opt.
        | Debug commands   | Chunked traces  |
        |                  |                 |
Hard    | Visual regress.  | Custom fixtures | Full scale-out
        | Flaky detection  | Perf analysis   | Global CI setup
        |                  |                 |

Recommended Path:
Week 1: Start with Low effort items
Week 2: Add Medium items
Week 3: Implement High items as needed
```

---

## 11. Common Issues & Solutions Matrix

| Issue | Cause | Quick Fix | Root Cause | Long-term Solution |
|-------|-------|-----------|-----------|---|
| Videos not saved | context not closed | Add `context.close()` | Missing cleanup | Implement fixture |
| Slow timing | `time.sleep()` | Use `await wait_for_timeout()` | Blocking call | Update wait strategy |
| Out of memory | No cleanup | Close contexts | Resource leak | Implement fixture teardown |
| Flaky tests | Timing issues | Add wait strategies | Poor selectors | Implement robust waits |
| CI failures | Headless issues | Use `--headed --slowmo 500` | Environment diff | Debug locally first |
| Screenshots blank | Page not rendered | Add `networkidle` wait | Async timing | Wait for load state |
| Trace too large | All components on | Disable snapshots | Over-instrumentation | Selective tracing |
| Parallel conflicts | Shared resources | Use `-n 4` (not more) | Resource contention | Fixture isolation |

---

## Summary: Decision Quick Lookup

**What should I use?**

| Question | Answer | Why |
|----------|--------|-----|
| "Video or not?" | Yes, retain-on-failure | Debugging aid, minimal storage |
| "Record traces?" | Yes, on failures | Comprehensive debugging |
| "Sync or async?" | Async in CI, sync locally | Performance vs simplicity |
| "Headed or headless?" | Headless in CI, headed local | Speed vs visibility |
| "Which browser?" | Chromium first, +Firefox in CI | Coverage vs speed |
| "Screenshot on every step?" | No, only key states | Storage and maintenance |
| "Parallel tests?" | Yes, -n 4 in CI | Speed without issues |
| "How many workers?" | 4 (1 per CPU core) | Optimal performance |
| "Debug tool?" | PWDEBUG=1 locally, video in CI | Best ROI for effort |

