# Playwright Python Quick Reference: Code Snippets & Templates

**Purpose:** Production-ready code templates for common Playwright Python testing scenarios
**Last Updated:** January 28, 2026

---

## Table of Contents

1. [Video Recording Workflows](#video-recording-workflows)
2. [Screenshot Capture Templates](#screenshot-capture-templates)
3. [Trace File Management](#trace-file-management)
4. [Async/Await Patterns](#asyncawait-patterns)
5. [pytest Integration Fixtures](#pytest-integration-fixtures)
6. [Debugging Commands](#debugging-commands)

---

## Video Recording Workflows

### Minimal Video Recording

```python
from playwright.sync_api import sync_playwright

with sync_playwright() as p:
    browser = p.chromium.launch()
    context = browser.new_context(record_video_dir="videos/")
    page = context.new_page()

    page.goto("https://example.com")
    page.click("button")

    context.close()  # Video saved after close
    browser.close()

    video_path = page.video.path()
    print(f"Video: {video_path}")
```

### Custom Video Size

```python
context = browser.new_context(
    record_video_dir="videos/",
    record_video_size={"width": 1920, "height": 1080}
)
```

### Async Video Recording with Error Handling

```python
import asyncio
import os
from pathlib import Path

async def record_with_error_handling():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()

        video_dir = Path("test_videos")
        video_dir.mkdir(exist_ok=True)

        context = await browser.new_context(
            record_video_dir=str(video_dir),
            record_video_size={"width": 1280, "height": 720}
        )

        page = await context.new_page()
        test_passed = False

        try:
            await page.goto("https://example.com")
            await page.click("button#submit")
            test_passed = True
        except Exception as e:
            print(f"Test failed: {e}")
        finally:
            await context.close()

        video_path = await page.video.path()
        if video_path and not test_passed:
            print(f"Failure video saved: {video_path}")
        elif video_path:
            os.remove(video_path)  # Clean up on success

        await browser.close()

asyncio.run(record_with_error_handling())
```

### Video Only on Failure

```python
import shutil
from pathlib import Path

def record_video_on_failure(test_name: str):
    """Context manager for failure-only video retention."""

    from playwright.sync_api import sync_playwright

    with sync_playwright() as p:
        browser = p.chromium.launch()

        video_dir = f"videos/{test_name}"
        Path(video_dir).mkdir(parents=True, exist_ok=True)

        context = browser.new_context(record_video_dir=video_dir)
        page = context.new_page()
        test_passed = True

        try:
            # Test code here
            page.goto("https://example.com")
            assert "Example" in page.title()

        except AssertionError as e:
            test_passed = False
            print(f"Test failed: {e}")

        finally:
            context.close()

            if test_passed:
                shutil.rmtree(video_dir, ignore_errors=True)
                print("Test passed - video deleted")
            else:
                video = list(Path(video_dir).glob("*.webm"))[0]
                print(f"Test failed - video retained: {video}")

            browser.close()
```

---

## Screenshot Capture Templates

### Full Page Screenshot

```python
# Sync
page.screenshot(path="full_page.png", full_page=True)

# Async
await page.screenshot(path="full_page.png", full_page=True)
```

### Viewport Screenshot

```python
# Only visible portion
page.screenshot(path="viewport.png", full_page=False)
```

### Element Screenshot

```python
# Single element
page.locator(".header").screenshot(path="header.png")

# Async
await page.locator(".button-group").screenshot(path="buttons.png")
```

### Screenshot to Base64

```python
import base64

# Sync
screenshot_bytes = page.screenshot()
base64_str = base64.b64encode(screenshot_bytes).decode()
data_url = f"data:image/png;base64,{base64_str}"

# Async
screenshot_bytes = await page.screenshot()
```

### Clipped Region

```python
# Capture specific region
page.screenshot(
    path="region.png",
    clip={"x": 0, "y": 0, "width": 500, "height": 500}
)

# Async with coordinates
await page.screenshot(
    path="region.png",
    clip={"x": 100, "y": 100, "width": 300, "height": 300}
)
```

### JPEG Compression

```python
# PNG (default)
page.screenshot(path="image.png", type="png")

# JPEG with quality
page.screenshot(path="image.jpg", type="jpeg", quality=80)

# Async JPEG
await page.screenshot(path="image.jpg", type="jpeg", quality=85)
```

### Screenshot Before & After Actions

```python
# Before action
page.screenshot(path="before_click.png")

page.click("button#toggle")
page.wait_for_timeout(500)

# After action
page.screenshot(path="after_click.png")
```

### Continuous Screenshots During Test

```python
def continuous_screenshots(page, interval_ms: int = 500):
    """Capture screenshots at regular intervals."""

    import time
    start_time = time.time()
    counter = 0

    while (time.time() - start_time) < 10:  # 10 seconds total
        filename = f"screenshot_{counter:03d}.png"
        page.screenshot(path=filename)
        counter += 1
        time.sleep(interval_ms / 1000)
```

---

## Trace File Management

### Start & Stop Trace

```python
# Sync
context.tracing.start(screenshots=True, snapshots=True, sources=True)

# ... perform actions ...

context.tracing.stop(path="trace.zip")
```

### Async Trace

```python
await context.tracing.start(
    screenshots=True,
    snapshots=True,
    sources=True
)

# ... actions ...

await context.tracing.stop(path="trace.zip")
```

### Trace Chunking

```python
# Start
await context.tracing.start(screenshots=True, snapshots=True)

# Actions...
await page.goto("https://example.com")

# Stop chunk
await context.tracing.stop_chunk(path="trace_part1.zip")

# Continue tracing (start again)
await context.tracing.start(screenshots=True, snapshots=True)

# More actions...
await page.click("button")

# Final chunk
await context.tracing.stop(path="trace_part2.zip")
```

### Open Trace

```bash
# CLI viewer
playwright show-trace trace.zip

# Web viewer
# Go to https://trace.playwright.dev/ and drag/drop trace.zip
```

### Conditional Trace Recording

```python
def record_trace_on_failure(context, test_name: str, test_passed: bool):
    """Save trace only if test failed."""

    if test_passed:
        # Discard trace
        context.tracing.stop_chunk()
    else:
        # Save trace
        context.tracing.stop(path=f"trace_{test_name}_failed.zip")
```

---

## Async/Await Patterns

### Proper Context Lifecycle

```python
async def proper_lifecycle():
    from playwright.async_api import async_playwright

    async with async_playwright() as playwright:
        browser = await playwright.chromium.launch()
        context = await browser.new_context()

        try:
            page = await context.new_page()
            await page.goto("https://example.com")
            # ... operations ...
        finally:
            await context.close()  # BEFORE browser.close()
            await browser.close()
```

### Parallel Pages in Context

```python
async def parallel_pages():
    from playwright.async_api import async_playwright
    import asyncio

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context()

        # Create multiple pages
        page1 = await context.new_page()
        page2 = await context.new_page()
        page3 = await context.new_page()

        # Navigate all in parallel
        await asyncio.gather(
            page1.goto("https://example.com/1"),
            page2.goto("https://example.com/2"),
            page3.goto("https://example.com/3"),
        )

        # Parallel screenshots
        screenshots = await asyncio.gather(
            page1.screenshot(),
            page2.screenshot(),
            page3.screenshot(),
        )

        await context.close()
        await browser.close()

        return screenshots
```

### Waiting Without Blocking

```python
async def wait_correctly():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        page = await browser.new_page()

        # WRONG - blocks event loop
        # import time
        # time.sleep(2)

        # CORRECT - non-blocking
        await page.wait_for_timeout(2000)

        # Also correct
        await page.wait_for_load_state("networkidle")

        await browser.close()
```

### Resource Cleanup with try/finally

```python
async def safe_cleanup():
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        browser = await p.chromium.launch()
        context = await browser.new_context(record_video_dir="videos/")

        try:
            page = await context.new_page()
            await page.goto("https://example.com")
            # ... test operations ...
        except Exception as e:
            print(f"Error: {e}")
        finally:
            # Guaranteed to run even on exception
            try:
                await context.close()
            except:
                pass
            try:
                await browser.close()
            except:
                pass
```

---

## pytest Integration Fixtures

### Basic conftest.py Setup

```python
# conftest.py
import pytest
from playwright.sync_api import sync_playwright

@pytest.fixture(scope="session")
def browser():
    """Session-scoped browser for all tests."""
    with sync_playwright() as p:
        browser = p.chromium.launch()
        yield browser
        browser.close()

@pytest.fixture(scope="function")
def context(browser):
    """Function-scoped context per test."""
    context = browser.new_context(record_video_dir="videos/")
    yield context
    context.close()

@pytest.fixture(scope="function")
def page(context):
    """Function-scoped page per test."""
    page = context.new_page()
    yield page
    page.close()
```

### Custom Fixture with Configuration

```python
# conftest.py
import pytest
from pathlib import Path

@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Override context arguments."""
    return {
        **browser_context_args,
        "record_video_dir": "test_videos/",
        "record_video_size": {"width": 1280, "height": 720},
        "viewport": {"width": 1280, "height": 720},
        "extra_http_headers": {
            "Accept-Language": "en-US,en;q=0.9"
        }
    }

@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Override launch arguments."""
    return {
        **browser_type_launch_args,
        "headless": True,
        "args": ["--disable-dev-shm-usage"],
    }
```

### Async pytest Fixture

```python
# conftest.py
import pytest
import pytest_asyncio

@pytest_asyncio.fixture(scope="function")
async def async_page(async_browser):
    """Async page fixture."""
    context = await async_browser.new_context(
        record_video_dir="async_videos/"
    )
    page = await context.new_page()
    yield page
    await context.close()

# Use in test:
@pytest.mark.asyncio
async def test_async_navigation(async_page):
    await async_page.goto("https://example.com")
    assert "Example" in await async_page.title()
```

### Fixture for Artifact Capture

```python
# conftest.py
from pathlib import Path
from datetime import datetime

@pytest.fixture
def artifact_dir(request):
    """Create test-specific artifact directory."""
    test_name = request.node.name
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    artifact_path = Path(f"artifacts/{test_name}_{timestamp}")
    artifact_path.mkdir(parents=True, exist_ok=True)
    return artifact_path

# Use in test:
def test_with_artifacts(page, artifact_dir):
    page.goto("https://example.com")
    page.screenshot(path=str(artifact_dir / "screenshot.png"))
```

---

## Debugging Commands

### Enable Playwright Inspector

```bash
# Run with inspector
PWDEBUG=1 pytest tests/test_example.py -s

# Run specific test with inspector
PWDEBUG=1 pytest tests/test_example.py::test_function -s

# Inspector + headed mode
PWDEBUG=1 pytest tests/ --headed -s
```

### Verbose Logging

```bash
# Enable API debugging
DEBUG=pw:api pytest tests/test_example.py -s

# All debug output
DEBUG=pw:* pytest tests/test_example.py -s

# Specific module
DEBUG=pw:browser pytest tests/ -s
```

### Run in Headed Mode with Slowdown

```bash
pytest tests/ --headed --slowmo 500 -s
```

### Screenshot on Failure

```bash
pytest tests/ --screenshot only-on-failure
```

### Video Recording Options

```bash
# Record all tests
pytest tests/ --video on

# Only retain on failure
pytest tests/ --video retain-on-failure

# Custom path (if configured)
pytest tests/ --video-dir custom_videos/
```

### Trace Recording

```bash
# Trace all tests
pytest tests/ --trace on

# Only on failure
pytest tests/ --trace retain-on-failure
```

### Combined Debugging Setup

```bash
# Full debugging experience
PWDEBUG=1 pytest tests/test_example.py \
  --headed \
  --slowmo 500 \
  --video on \
  --trace on \
  --screenshot on \
  -s -v
```

### Page Pause in Code

```python
def test_with_pause(page):
    page.goto("https://example.com")

    # Pause execution here when PWDEBUG=1
    page.pause()

    page.click("button")
```

---

## pytest Command Reference

### Basic Execution

```bash
# Run all tests
pytest tests/

# Run specific file
pytest tests/test_login.py

# Run specific test
pytest tests/test_login.py::test_valid_login

# Run tests matching pattern
pytest tests/ -k "login" -v

# Run with verbose output
pytest tests/ -v

# Run with print statements
pytest tests/ -s

# Stop on first failure
pytest tests/ -x

# Show local variables on failure
pytest tests/ -l
```

### Parallel Execution

```bash
# Run with 4 workers
pytest tests/ -n 4

# Auto detect CPU count
pytest tests/ -n auto

# Distribute by test scope
pytest tests/ -n auto --dist loadscope
```

### Reporting

```bash
# HTML report
pytest tests/ --html=report.html --self-contained-html

# JUnit XML report
pytest tests/ --junit-xml=results.xml

# Coverage report
pytest tests/ --cov=src --cov-report=html

# ALLURE report
pytest tests/ --alluredir=allure-results
```

### Browser Selection

```bash
# Chromium only
pytest tests/ --browser chromium

# Multiple browsers
pytest tests/ --browser chromium --browser firefox --browser webkit

# Firefox only
pytest tests/ --browser firefox
```

---

## Environment Variables

### Playwright Configuration

```bash
# Browser path (override default)
export PW_CHROMIUM_DOWNLOAD_HOST="https://custom-mirror.com"

# Disable Chromium download
export PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=1

# Timeout (milliseconds)
export PW_TIMEOUT=30000

# Screenshot/video path
export PLAYWRIGHT_JUNIT_OUTPUT_NAME=results.xml
```

### Testing Configuration

```bash
# CI detection
export CI=true

# Headless mode
export PW_HEADLESS=true

# Debug mode
export DEBUG=pw:api

# Slow motion
export PW_SLOWMO=1000
```

---

## Summary Table: Sync vs Async

| Operation | Sync | Async |
|-----------|------|-------|
| Launch | `p.chromium.launch()` | `await p.chromium.launch()` |
| Navigate | `page.goto(url)` | `await page.goto(url)` |
| Click | `page.click(sel)` | `await page.click(sel)` |
| Screenshot | `page.screenshot()` | `await page.screenshot()` |
| Wait | `page.wait_for_timeout(ms)` | `await page.wait_for_timeout(ms)` |
| Close | `context.close()` | `await context.close()` |
| Context Mgr | `with sync_playwright()` | `async with async_playwright()` |

---

## Common Patterns Checklist

- [ ] Always close context before browser
- [ ] Use `await page.wait_for_timeout()` NOT `time.sleep()` in async
- [ ] Configure `record_video_dir` and `record_video_size` at context creation
- [ ] Call `page.video.path()` AFTER context.close()
- [ ] Enable traces with `screenshots=True, snapshots=True, sources=True`
- [ ] Use `pytest.ini` or `pyproject.toml` for environment-specific config
- [ ] Implement artifact capture for failed tests
- [ ] Use `PWDEBUG=1` for interactive debugging locally
- [ ] Default to headless in CI, headed locally
- [ ] Clean up old traces/videos with age-based policies

