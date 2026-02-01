# Playwright Python Test Automation: Implementation Guide

**Purpose:** Step-by-step guide for implementing production-grade Playwright test automation
**Target Audience:** QA Engineers, SDETs, DevOps Engineers
**Complexity Level:** Intermediate to Advanced

---

## Project Setup & Configuration

### Step 1: Environment Setup

```bash
# Create project directory
mkdir playwright-tests
cd playwright-tests

# Create Python virtual environment
python3.11 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install playwright pytest pytest-asyncio pytest-xdist pytest-html pytest-cov

# Install Playwright browsers
playwright install chromium firefox webkit

# Verify installation
pytest --version
playwright --version
```

### Step 2: Project Structure

```
playwright-tests/
├── tests/
│   ├── conftest.py              # pytest configuration and fixtures
│   ├── test_authentication.py   # Auth-related tests
│   ├── test_dashboard.py        # Dashboard tests
│   ├── test_checkout.py         # E2E flow tests
│   └── fixtures/
│       ├── api_mocks.py         # Mock data fixtures
│       └── test_data.py         # Test data management
├── artifacts/
│   ├── videos/                  # Video recordings
│   ├── traces/                  # Trace files
│   ├── screenshots/             # Screenshot captures
│   └── logs/                    # Test logs
├── conftest.py                  # Root-level pytest configuration
├── pytest.ini                   # pytest configuration
├── pyproject.toml               # Project metadata
├── requirements.txt             # Dependencies
└── README.md                    # Documentation
```

### Step 3: Configuration Files

**requirements.txt:**
```
playwright>=1.48.0
pytest>=7.4.0
pytest-asyncio>=0.23.0
pytest-xdist>=3.5.0
pytest-html>=4.1.0
pytest-cov>=4.1.0
python-dotenv>=1.0.0
allure-pytest>=2.13.2
```

**pytest.ini:**
```ini
[pytest]
minversion = 7.0
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
asyncio_mode = auto

# Playwright options
addopts =
    --trace=retain-on-failure
    --video=retain-on-failure
    --screenshot=only-on-failure
    -v
    --tb=short
    --strict-markers

markers =
    smoke: marks tests as smoke tests
    e2e: marks tests as end-to-end
    critical: marks tests as critical path
    slow: marks tests as slow
    integration: marks tests as integration tests

testpaths = tests
```

**pyproject.toml:**
```toml
[build-system]
requires = ["setuptools>=65.0"]
build-backend = "setuptools.build_meta"

[project]
name = "playwright-tests"
version = "1.0.0"
description = "Enterprise-grade Playwright test automation suite"
requires-python = ">=3.11"

[tool.pytest.ini_options]
minversion = "7.0"
testpaths = ["tests"]
asyncio_mode = "auto"
addopts = [
    "--trace=retain-on-failure",
    "--video=retain-on-failure",
    "--screenshot=only-on-failure",
    "-v",
]

[tool.coverage.run]
source = ["src"]
omit = ["*/tests/*"]

[tool.coverage.report]
exclude_lines = [
    "pragma: no cover",
    "def __repr__",
    "raise AssertionError",
    "raise NotImplementedError",
]
```

---

## Core Fixture Architecture

### conftest.py - Complete Implementation

```python
# tests/conftest.py
"""
pytest configuration and fixtures for Playwright test suite.

Provides:
- Browser and context management
- Video/trace recording configuration
- Custom markers
- Artifact organization
- Test data fixtures
"""

import os
import pytest
import asyncio
import logging
from pathlib import Path
from datetime import datetime
from typing import Generator, AsyncGenerator

import pytest_asyncio
from playwright.sync_api import sync_playwright, Browser, BrowserContext, Page
from playwright.async_api import async_playwright, Browser as AsyncBrowser
from playwright.async_api import BrowserContext as AsyncBrowserContext
from playwright.async_api import Page as AsyncPage

# Logging configuration
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Environment & Configuration
# ============================================================================

def pytest_configure(config):
    """Configure pytest with environment-aware settings."""

    # Detect CI environment
    is_ci = os.getenv("CI", "").lower() in ("true", "1")

    # Set default options based on environment
    if not is_ci and not os.getenv("PW_HEADLESS"):
        # Local development: headed mode with slower execution
        logger.info("Local development mode: headed with slowdown")
        config.option.headed = True
        config.option.slowmo = 100
    else:
        # CI environment: headless, optimized
        logger.info("CI environment: headless mode")
        config.option.headed = False
        config.option.slowmo = 0


def pytest_collection_modifyitems(config, items):
    """Modify test collection to add markers."""

    for item in items:
        # Add slow marker to specific tests
        if "slow" in item.nodeid:
            item.add_marker(pytest.mark.slow)

        # Add e2e marker to integration tests
        if "e2e" in item.nodeid or "integration" in item.nodeid:
            item.add_marker(pytest.mark.e2e)


# ============================================================================
# Artifact Management
# ============================================================================

class ArtifactManager:
    """Manages test artifacts (videos, traces, screenshots)."""

    def __init__(self, base_dir: str = "artifacts"):
        self.base_dir = Path(base_dir)
        self.test_dir = None

    def create_test_directory(self, test_name: str) -> Path:
        """Create test-specific artifact directory."""

        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.test_dir = self.base_dir / test_name / timestamp

        # Create subdirectories
        for subdir in ["videos", "traces", "screenshots", "logs"]:
            (self.test_dir / subdir).mkdir(parents=True, exist_ok=True)

        logger.info(f"Artifact directory: {self.test_dir}")
        return self.test_dir

    def get_video_dir(self) -> str:
        """Get video directory path."""
        if not self.test_dir:
            raise RuntimeError("Test directory not initialized")
        return str(self.test_dir / "videos")

    def get_trace_path(self) -> str:
        """Get trace file path."""
        if not self.test_dir:
            raise RuntimeError("Test directory not initialized")
        return str(self.test_dir / "traces" / "trace.zip")


# ============================================================================
# Synchronous Fixtures
# ============================================================================

@pytest.fixture(scope="session")
def artifact_manager() -> ArtifactManager:
    """Session-scoped artifact manager."""
    return ArtifactManager()


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args):
    """Configure browser context arguments."""

    return {
        **browser_context_args,
        "record_video_size": {"width": 1280, "height": 720},
        "viewport": {"width": 1280, "height": 720},
    }


@pytest.fixture(scope="session")
def browser_type_launch_args(browser_type_launch_args):
    """Configure browser launch arguments."""

    is_ci = os.getenv("CI", "").lower() in ("true", "1")

    args = {
        **browser_type_launch_args,
        "headless": is_ci,
    }

    # Additional CI optimizations
    if is_ci:
        args["args"] = ["--disable-dev-shm-usage", "--no-sandbox"]

    return args


@pytest.fixture(scope="function")
def test_artifacts(request, artifact_manager: ArtifactManager) -> Path:
    """Create and provide test artifact directory."""

    test_name = request.node.name
    return artifact_manager.create_test_directory(test_name)


@pytest.fixture(scope="function")
def sync_context_with_video(browser, test_artifacts) -> Generator[BrowserContext, None, None]:
    """Browser context with video recording enabled."""

    context = browser.new_context(
        record_video_dir=str(test_artifacts / "videos"),
        record_video_size={"width": 1280, "height": 720}
    )

    yield context

    context.close()


@pytest.fixture(scope="function")
def sync_page_with_trace(sync_context_with_video, test_artifacts) -> Generator[Page, None, None]:
    """Page with trace recording enabled."""

    context = sync_context_with_video
    context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )

    page = context.new_page()

    yield page

    # Save trace
    context.tracing.stop(path=str(test_artifacts / "traces" / "trace.zip"))

    page.close()


# ============================================================================
# Asynchronous Fixtures
# ============================================================================

@pytest_asyncio.fixture(scope="function")
async def async_context_with_video(async_browser, test_artifacts) -> AsyncGenerator[AsyncBrowserContext, None]:
    """Async browser context with video recording."""

    context = await async_browser.new_context(
        record_video_dir=str(test_artifacts / "videos"),
        record_video_size={"width": 1280, "height": 720}
    )

    yield context

    await context.close()


@pytest_asyncio.fixture(scope="function")
async def async_page_with_trace(async_context_with_video, test_artifacts) -> AsyncGenerator[AsyncPage, None]:
    """Async page with trace recording."""

    context = async_context_with_video

    await context.tracing.start(
        screenshots=True,
        snapshots=True,
        sources=True
    )

    page = await context.new_page()

    yield page

    await context.tracing.stop(path=str(test_artifacts / "traces" / "trace.zip"))
    await page.close()


# ============================================================================
# Hooks & Reporting
# ============================================================================

@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    """Generate test report and capture artifacts on failure."""

    outcome = yield
    rep = outcome.get_result()

    if rep.when == "call" and rep.failed:
        # Test failed - capture additional artifacts
        logger.error(f"Test failed: {item.name}")


def pytest_sessionfinish(session, exitstatus):
    """Run after all tests complete."""

    logger.info(f"Test session finished with status: {exitstatus}")

    if exitstatus == 0:
        logger.info("All tests passed!")
    else:
        logger.warning("Some tests failed. Check artifacts directory.")


# ============================================================================
# Helper Utilities
# ============================================================================

@pytest.fixture
def test_data():
    """Provide common test data."""

    return {
        "user": {
            "email": "test@example.com",
            "password": "SecurePassword123!",
            "username": "testuser"
        },
        "product": {
            "id": "SKU-12345",
            "name": "Test Product",
            "price": 99.99
        },
        "urls": {
            "home": "https://example.com/",
            "login": "https://example.com/login",
            "dashboard": "https://example.com/dashboard",
            "checkout": "https://example.com/checkout"
        }
    }


@pytest.fixture
def wait_helper(sync_page):
    """Helper for common wait conditions."""

    class WaitHelper:
        def __init__(self, page):
            self.page = page

        def page_loaded(self, timeout=5000):
            """Wait for page to fully load."""
            self.page.wait_for_load_state("networkidle", timeout=timeout)

        def element_visible(self, selector, timeout=5000):
            """Wait for element to be visible."""
            self.page.wait_for_selector(selector, state="visible", timeout=timeout)

        def element_gone(self, selector, timeout=5000):
            """Wait for element to disappear."""
            self.page.wait_for_selector(selector, state="hidden", timeout=timeout)

    return WaitHelper(sync_page)
```

---

## Test Implementation Examples

### Example 1: Basic Authentication Test

```python
# tests/test_authentication.py
"""Authentication flow tests with full artifact capture."""

import pytest
from playwright.sync_api import Page


@pytest.mark.smoke
def test_valid_login(sync_page_with_trace: Page, test_data, test_artifacts):
    """Test successful login with valid credentials."""

    page = sync_page_with_trace

    # Navigate to login
    page.goto(test_data["urls"]["login"])
    page.screenshot(path=str(test_artifacts / "screenshots" / "01_login_form.png"))

    # Fill login form
    page.fill("input[name='email']", test_data["user"]["email"])
    page.fill("input[name='password']", test_data["user"]["password"])

    # Submit form
    page.click("button[type='submit']")
    page.wait_for_load_state("networkidle")

    # Verify successful login
    page.screenshot(path=str(test_artifacts / "screenshots" / "02_dashboard.png"))
    assert "Dashboard" in page.title()
    assert page.locator("text=Welcome").is_visible()


@pytest.mark.critical
def test_invalid_password(sync_page_with_trace: Page, test_data, test_artifacts):
    """Test login with invalid password."""

    page = sync_page_with_trace

    page.goto(test_data["urls"]["login"])

    # Use wrong password
    page.fill("input[name='email']", test_data["user"]["email"])
    page.fill("input[name='password']", "WrongPassword123!")

    page.click("button[type='submit']")
    page.wait_for_timeout(500)

    # Capture error state
    page.screenshot(path=str(test_artifacts / "screenshots" / "error_state.png"))

    # Verify error message
    error_msg = page.locator(".error-message")
    assert error_msg.is_visible()
    assert "Invalid credentials" in error_msg.text_content()


@pytest.mark.parametrize("email,password", [
    ("", "password123"),
    ("user@example.com", ""),
    ("", ""),
])
def test_missing_credentials(sync_page_with_trace: Page, email, password, test_artifacts):
    """Test login with missing credentials."""

    page = sync_page_with_trace

    page.goto("https://example.com/login")

    if email:
        page.fill("input[name='email']", email)
    if password:
        page.fill("input[name='password']", password)

    page.click("button[type='submit']")
    page.wait_for_timeout(500)

    page.screenshot(path=str(test_artifacts / "screenshots" / f"missing_{email or 'all'}.png"))

    # Submit button should be disabled or error shown
    assert not page.locator("button[type='submit']").is_enabled() or \
           page.locator(".error-message").is_visible()
```

### Example 2: E2E Checkout Test with Async

```python
# tests/test_checkout_async.py
"""End-to-end checkout flow with async operations."""

import pytest
from playwright.async_api import Page


@pytest.mark.e2e
@pytest.mark.critical
async def test_complete_checkout(async_page_with_trace: Page, test_data, test_artifacts):
    """Test complete checkout flow with video and trace."""

    page = async_page_with_trace

    # Navigate to home
    await page.goto(test_data["urls"]["home"])
    await page.screenshot(path=str(test_artifacts / "screenshots" / "01_home.png"))

    # Search for product
    await page.fill("input[placeholder='Search products']", test_data["product"]["name"])
    await page.press("input[placeholder='Search products']", "Enter")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=str(test_artifacts / "screenshots" / "02_search_results.png"))

    # Click first result
    await page.click("a.product-link:first-child")
    await page.wait_for_selector(".product-detail")
    await page.screenshot(path=str(test_artifacts / "screenshots" / "03_product_detail.png"))

    # Add to cart
    await page.click("button:has-text('Add to Cart')")
    await page.wait_for_timeout(500)
    await page.screenshot(path=str(test_artifacts / "screenshots" / "04_added_to_cart.png"))

    # Navigate to cart
    await page.click("a[href='/cart']")
    await page.wait_for_load_state("networkidle")
    await page.screenshot(path=str(test_artifacts / "screenshots" / "05_cart.png"))

    # Proceed to checkout
    await page.click("button:has-text('Checkout')")
    await page.wait_for_selector(".checkout-form")
    await page.screenshot(path=str(test_artifacts / "screenshots" / "06_checkout_form.png"))

    # Fill shipping info
    await page.fill("input[name='firstName']", "John")
    await page.fill("input[name='lastName']", "Doe")
    await page.fill("input[name='address']", "123 Main St")
    await page.fill("input[name='city']", "Springfield")

    # Fill payment info
    await page.fill("input[name='cardNumber']", "4111111111111111")
    await page.fill("input[name='expiryDate']", "12/25")
    await page.fill("input[name='cvv']", "123")

    await page.screenshot(path=str(test_artifacts / "screenshots" / "07_payment_filled.png"))

    # Submit order
    await page.click("button:has-text('Place Order')")
    await page.wait_for_selector("text=Order Confirmed")
    await page.screenshot(path=str(test_artifacts / "screenshots" / "08_confirmation.png"))

    # Verify confirmation
    assert "Order Confirmed" in await page.title()
    assert await page.locator(".order-number").is_visible()
```

---

## Running Tests & Analysis

### Running Tests with Different Configurations

```bash
# Basic test run
pytest tests/ -v

# With video recording
pytest tests/ --video on

# Only on failure
pytest tests/ --video retain-on-failure

# With trace recording
pytest tests/ --trace on

# Parallel execution (4 workers)
pytest tests/ -n 4

# Specific markers
pytest tests/ -m "smoke" -v
pytest tests/ -m "critical and not slow" -v

# With HTML report
pytest tests/ --html=report.html --self-contained-html

# With coverage
pytest tests/ --cov=tests --cov-report=html

# Headed mode for debugging
pytest tests/ --headed --slowmo 500 -s

# With Playwright Inspector
PWDEBUG=1 pytest tests/test_authentication.py -s

# Combined debugging
PWDEBUG=1 pytest tests/ --headed --video on --trace on --slowmo 500 -s
```

### CI/CD Pipeline Integration

**GitHub Actions Example:**
```yaml
# .github/workflows/playwright-tests.yml
name: Playwright Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        browser: [chromium, firefox]

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'

      - name: Install dependencies
        run: |
          pip install -r requirements.txt
          playwright install

      - name: Run tests
        run: |
          pytest tests/ \
            --browser ${{ matrix.browser }} \
            --video retain-on-failure \
            --trace retain-on-failure \
            --junitxml=results-${{ matrix.browser }}.xml

      - name: Upload results
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: test-results-${{ matrix.browser }}
          path: artifacts/
```

---

## Best Practices Checklist

### Code Quality
- [ ] Use type hints in fixtures and test functions
- [ ] Implement comprehensive logging
- [ ] Follow DRY principle - extract common operations to fixtures
- [ ] Use descriptive test names that indicate what is being tested
- [ ] Document complex test flows with comments

### Artifact Management
- [ ] Organize artifacts by test name and timestamp
- [ ] Implement automated cleanup for old artifacts
- [ ] Retain videos/traces only on failure in CI
- [ ] Capture screenshots at key decision points
- [ ] Archive artifacts for failed tests

### Performance
- [ ] Use parallel execution (`-n 4`) for faster CI runs
- [ ] Implement test isolation to avoid cross-test dependencies
- [ ] Use appropriate wait strategies (not `time.sleep()`)
- [ ] Configure reasonable timeouts (5-10 seconds for most operations)
- [ ] Monitor test execution time and optimize slow tests

### Debugging
- [ ] Use markers to categorize tests (smoke, critical, slow)
- [ ] Implement selective test execution for development
- [ ] Use `--headed` and `--slowmo` for interactive debugging locally
- [ ] Enable PWDEBUG=1 for Playwright Inspector
- [ ] Review videos and traces for failed tests

### Maintenance
- [ ] Version control test code with application code
- [ ] Review and update selectors when UI changes
- [ ] Implement wait strategies robust to network delays
- [ ] Document custom fixtures and utilities
- [ ] Keep dependencies updated

---

## Troubleshooting

### Issue: Videos Not Saving

```python
# Problem: context.close() not called
context = browser.new_context(record_video_dir="videos/")
# ... test code ...
# MISSING: context.close()

# Solution: Always close context
try:
    # ... test code ...
finally:
    context.close()  # Ensures video is saved
```

### Issue: Timing Failures

```python
# Problem: Using time.sleep() in async context
await page.click("button")
time.sleep(2)  # WRONG - blocks event loop
await page.screenshot()

# Solution: Use async wait
await page.click("button")
await page.wait_for_timeout(2000)  # Non-blocking
await page.screenshot()
```

### Issue: Out of Memory in CI

```python
# Problem: Not closing browsers/contexts
for i in range(100):
    context = browser.new_context()
    # ... test ...
    # MISSING: context.close()

# Solution: Proper cleanup
for i in range(100):
    context = browser.new_context()
    try:
        # ... test ...
    finally:
        context.close()
```

---

## Monitoring & Reporting

### Test Report Generation

```bash
# HTML report with screenshots
pytest tests/ --html=report.html \
  --self-contained-html \
  --screenshots=only-on-failure

# ALLURE report
pytest tests/ --alluredir=allure-results
allure serve allure-results

# JUnit XML for CI integration
pytest tests/ --junitxml=results.xml
```

### Artifact Analysis Workflow

1. Test completes → artifacts saved to organized directory
2. Failed tests → videos, traces, screenshots retained
3. Post-test analysis:
   - Review video for visual flow
   - Open trace in trace.playwright.dev
   - Examine screenshots for state validation
   - Check logs for error details

---

## Summary

This implementation guide provides:
- Complete project setup and configuration
- Production-grade fixture architecture
- Real-world test implementation examples
- CI/CD integration patterns
- Debugging and troubleshooting guidance

Follow the structure and patterns outlined to build maintainable, reliable Playwright test automation suites.

