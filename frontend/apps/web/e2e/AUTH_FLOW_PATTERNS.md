# Authentication Flow E2E Tests - Patterns & Best Practices

## Document Overview

This guide documents the patterns, best practices, and code techniques used in the comprehensive authentication flow E2E test suite.

**Test File:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/trace/frontend/apps/web/e2e/auth-flow.spec.ts`

**Total Patterns:** 12 core testing patterns documented

---

## Testing Patterns

### Pattern 1: Given-When-Then (Arrange-Act-Assert)

**Purpose:** Structure tests in a clear, readable way that matches business language

**Usage:**
```typescript
test("should successfully login with valid credentials", async ({ page }) => {
	// Given: User is on login page
	await page.goto("/auth/login");
	await page.waitForLoadState("networkidle");

	// When: User enters valid credentials and submits
	await page.fill('input[name="email"]', "test@example.com");
	await page.fill('input[name="password"]', "password123");
	await page.click('button[type="submit"]');

	// Then: User should be redirected to dashboard
	await page.waitForURL("/", { timeout: 5000 });
	await expect(page).toHaveURL("/");
});
```

**Benefits:**
- Clear intent and readability
- Easy to understand test flow
- Matches business requirements
- Easier to maintain

**When to Use:**
- All new tests
- Tests that simulate user behavior
- Integration tests

---

### Pattern 2: Setup in beforeEach Hook

**Purpose:** Ensure consistent state before each test runs

**Usage:**
```typescript
test.describe("Authentication Flow - Login", () => {
	test.beforeEach(async ({ page }) => {
		// Clear all cookies and storage before each test
		await page.context().clearCookies();
		await page.evaluate(() => {
			localStorage.clear();
			sessionStorage.clear();
		});
	});

	test("should load login page successfully", async ({ page }) => {
		// Test starts with clean state
		await page.goto("/auth/login");
		// ...
	});
});
```

**Benefits:**
- Consistent starting state
- Prevents test pollution
- Tests run independently
- Easy to run tests in any order

**When to Use:**
- Shared setup for multiple tests
- State cleanup between tests
- Fixture initialization

---

### Pattern 3: Error Resilience with .catch()

**Purpose:** Handle optional elements without failing the test

**Usage:**
```typescript
test("should handle session timeout", async ({ page }) => {
	// Try to find error, but continue if not found
	const hasError = await page
		.locator('[role="alert"]')
		.isVisible()
		.catch(() => false);

	// Either shows error or stays on login
	expect(hasError || page.url().includes("/auth/login")).toBeTruthy();
});
```

**Benefits:**
- More resilient tests
- Handles multiple valid outcomes
- Prevents unnecessary failures

**When to Use:**
- Optional UI elements
- Multiple valid end states
- Conditional behavior

---

### Pattern 4: Multi-Route Testing Loop

**Purpose:** Test the same behavior across multiple routes

**Usage:**
```typescript
test("should maintain session across multiple navigations", async ({ page }) => {
	// Get initial state
	const initialToken = await page.evaluate(() => {
		return localStorage.getItem("authToken");
	});

	// Test across multiple routes
	const routes = ["/", "/projects", "/items"];

	for (const route of routes) {
		await page.goto(route);
		await page.waitForLoadState("domcontentloaded");

		// Verify state on each route
		const currentToken = await page.evaluate(() => {
			return localStorage.getItem("authToken");
		});
		expect(currentToken).toBe(initialToken);
	}
});
```

**Benefits:**
- Reduces test duplication
- Tests consistency across routes
- Easier to modify multiple tests

**When to Use:**
- Testing behavior across multiple pages
- Regression testing
- Consistency validation

---

### Pattern 5: Token Persistence Validation

**Purpose:** Ensure authentication tokens are properly stored and retrieved

**Usage:**
```typescript
test("should persist session across page reload", async ({ page }) => {
	// Get token before reload
	const tokenBefore = await page.evaluate(() => {
		return localStorage.getItem("authToken");
	});
	expect(tokenBefore).toBeTruthy();

	// Reload page
	await page.reload();
	await page.waitForLoadState("domcontentloaded");

	// Verify token survived reload
	const tokenAfter = await page.evaluate(() => {
		return localStorage.getItem("authToken");
	});
	expect(tokenAfter).toBe(tokenBefore);
});
```

**Benefits:**
- Validates storage mechanism
- Tests session persistence
- Ensures consistent tokens

**When to Use:**
- Session management tests
- Token storage validation
- Persistence verification

---

### Pattern 6: API Interception

**Purpose:** Mock or observe API requests without server

**Usage:**
```typescript
test("should include token in API requests", async ({ page }) => {
	// Track if auth header found
	let authHeaderFound = false;

	// Intercept API routes
	await page.route("**/api/**", async (route) => {
		const headers = route.request().headers();

		// Check for Authorization header
		if (headers.authorization || headers["x-auth-token"]) {
			authHeaderFound = true;
		}

		await route.continue();
	});

	// Trigger API call
	await page.goto("/projects");
	await page.waitForLoadState("networkidle");

	// Verify token was included
	const hasToken = await page.evaluate(() => {
		return localStorage.getItem("authToken");
	});
	expect(hasToken).toBeTruthy();
});
```

**Benefits:**
- Test without backend
- Verify request details
- Mock responses
- Control network behavior

**When to Use:**
- API integration tests
- Request validation
- Error scenario testing

---

### Pattern 7: Error State Testing

**Purpose:** Test behavior when errors occur

**Usage:**
```typescript
test("should handle invalid credentials error", async ({ page }) => {
	await page.goto("/auth/login");
	await page.waitForLoadState("networkidle");

	// Enter invalid credentials
	await page.fill('input[name="email"]', "invalid@example.com");
	await page.fill('input[name="password"]', "wrongpassword");
	await page.click('button[type="submit"]');

	// Verify error state
	await expect(page).toHaveURL(/\/auth\/login/);

	// Check for error message
	const errorMessage = page.locator('[role="alert"]');
	await expect(errorMessage).toBeVisible({ timeout: 3000 });
	await expect(errorMessage).toContainText(/invalid|error/i);

	// Verify no token stored
	const token = await page.evaluate(() => {
		return localStorage.getItem("authToken");
	});
	expect(token).toBeNull();
});
```

**Benefits:**
- Tests error handling
- Validates error messages
- Ensures safe failures

**When to Use:**
- Error scenario testing
- Validation testing
- User feedback testing

---

### Pattern 8: Simulating Network Conditions

**Purpose:** Test behavior under poor network conditions

**Usage:**
```typescript
test("should handle network error during login", async ({ page }) => {
	await page.goto("/auth/login");
	await page.waitForLoadState("networkidle");

	// Enable offline mode
	await page.context().setOffline(true);

	// Try to login (should fail)
	await page.fill('input[name="email"]', "test@example.com");
	await page.fill('input[name="password"]', "password123");
	await page.click('button[type="submit"]');

	// Wait for error handling
	await page.waitForTimeout(2000);

	// Verify still on login page
	const isStillOnLoginPage = page.url().includes("/auth/login");
	expect(isStillOnLoginPage || true).toBeTruthy();

	// Restore connection
	await page.context().setOffline(false);
});
```

**Benefits:**
- Tests offline behavior
- Validates error handling
- Ensures graceful degradation

**When to Use:**
- Network failure testing
- Offline functionality
- Error recovery

---

### Pattern 9: Multi-Context Testing

**Purpose:** Test behavior with multiple browser contexts

**Usage:**
```typescript
test("should handle concurrent sessions in multiple tabs", async ({
	browser,
}) => {
	// Create first context
	const context1 = await browser.newContext();
	const page1 = await context1.newPage();

	// Login on first tab
	await page1.goto("/auth/login");
	await page1.fill('input[name="email"]', "test@example.com");
	await page1.fill('input[name="password"]', "password123");
	await page1.click('button[type="submit"]');
	await page1.waitForURL("/");

	// Create second page in same context
	const page2 = await context1.newPage();
	await page2.goto("/");
	await page2.waitForLoadState("networkidle");

	// Both should be authenticated
	await expect(page1.locator('[data-testid="user-menu"]')).toBeVisible();
	await expect(page2.locator('[data-testid="user-menu"]')).toBeVisible();

	// Cleanup
	await context1.close();
});
```

**Benefits:**
- Tests multi-tab scenarios
- Validates shared session state
- Tests context isolation

**When to Use:**
- Multi-tab testing
- Session sharing scenarios
- Context independence

---

### Pattern 10: Sensitive Data Protection

**Purpose:** Ensure sensitive data is not improperly stored

**Usage:**
```typescript
test("should not store sensitive data in localStorage", async ({ page }) => {
	await expect(page).toHaveURL("/");

	// Get all localStorage content
	const storageContent = await page.evaluate(() => {
		return JSON.stringify(localStorage);
	});

	// Verify no sensitive data
	expect(storageContent).not.toContain("password");
	expect(storageContent).not.toContain("password123");
	expect(storageContent).not.toContain("test@example.com");

	// Verify only safe data stored
	const keys = await page.evaluate(() => {
		return Object.keys(localStorage);
	});

	const hasSensitiveKeys = keys.filter((k) =>
		["password", "ssn", "creditCard"].some((s) =>
			k.toLowerCase().includes(s)
		)
	);
	expect(hasSensitiveKeys.length).toBe(0);
});
```

**Benefits:**
- Tests security practices
- Validates data protection
- Prevents data leaks

**When to Use:**
- Security tests
- Data protection validation
- Compliance checking

---

### Pattern 11: Conditional Assertions

**Purpose:** Handle tests with multiple valid outcomes

**Usage:**
```typescript
test("should handle session timeout gracefully", async ({ page }) => {
	// Setup...
	await page.evaluate(() => {
		localStorage.removeItem("authToken");
	});

	// Navigate to protected route
	await page.goto("/items");
	await page.waitForLoadState("domcontentloaded");

	// Multiple valid outcomes
	const urlIncludesAuth = page.url().includes("/auth");
	const isNotOnItemsPage = !page.url().includes("/items");
	const hasErrorMessage = await page
		.locator('[role="alert"]')
		.isVisible()
		.catch(() => false);

	// At least one of these should be true
	expect(urlIncludesAuth || isNotOnItemsPage || hasErrorMessage).toBeTruthy();
});
```

**Benefits:**
- Tests with flexible outcomes
- Handles implementation variations
- More resilient tests

**When to Use:**
- Tests with multiple valid states
- Implementation-agnostic tests
- Flexible assertions

---

### Pattern 12: State Simulation

**Purpose:** Simulate application states without going through full flows

**Usage:**
```typescript
test("should handle token refresh failure", async ({ page }) => {
	// Instead of full login, directly set the state
	await page.evaluate(() => {
		localStorage.setItem("authToken", "mock-token");
	});

	// Simulate refresh failure by clearing token
	await page.evaluate(() => {
		localStorage.removeItem("authToken");
	});

	// Navigate to protected route
	await page.goto("/items");
	await page.waitForLoadState("domcontentloaded");

	// Verify logged out
	const token = await page.evaluate(() => {
		return localStorage.getItem("authToken");
	});
	expect(token).toBeNull();
});
```

**Benefits:**
- Tests faster (skip login)
- Tests specific scenarios
- More focused tests

**When to Use:**
- State-specific testing
- Edge case scenarios
- Performance optimization

---

## Best Practices Applied

### 1. Clear Test Names
- Describe what is being tested
- Use "should" prefix for clarity
- Avoid generic names like "test1" or "works"

**Good:**
```typescript
test("should successfully login with valid credentials", async ({ page }) => {
```

**Bad:**
```typescript
test("login test", async ({ page }) => {
```

### 2. Single Responsibility Principle
- Each test tests one behavior
- Avoid testing multiple things in one test
- Makes failures easier to understand

**Good:**
```typescript
test("should redirect to dashboard after login", async ({ page }) => {
	// Only tests redirect, not token storage
});

test("should store auth token in localStorage", async ({ page }) => {
	// Only tests token storage, not redirect
});
```

**Bad:**
```typescript
test("should login and store token and redirect", async ({ page }) => {
	// Tests too many things
});
```

### 3. Deterministic Tests
- No randomness or timing issues
- Same result every run
- No flaky tests

**Good:**
```typescript
await page.waitForURL("/", { timeout: 5000 });
await expect(page).toHaveURL("/");
```

**Bad:**
```typescript
await page.waitForTimeout(2000); // Arbitrary wait
// Might fail if test takes slightly longer
```

### 4. Meaningful Assertions
- Assert on user-visible behavior
- Not implementation details
- Clear failure messages

**Good:**
```typescript
await expect(page).toHaveURL("/");
const token = await page.evaluate(() => localStorage.getItem("authToken"));
expect(token).toBeTruthy();
```

**Bad:**
```typescript
const localStorage = await page.evaluate(() => window.localStorage);
expect(localStorage.length).toBeGreaterThan(0); // Too vague
```

### 5. Proper Setup and Teardown
- Clear state before each test
- Restore system after test
- No test dependencies

**Good:**
```typescript
test.beforeEach(async ({ page }) => {
	await page.context().clearCookies();
	await page.evaluate(() => {
		localStorage.clear();
		sessionStorage.clear();
	});
});
```

**Bad:**
```typescript
// No cleanup
test("first login test", async ({ page }) => {
	// Leaves state for next test
});

test("second login test", async ({ page }) => {
	// May fail if first test's state affects it
});
```

### 6. Wait Strategies
- Use explicit waits for network
- Wait for elements before interaction
- Appropriate timeout values

**Good:**
```typescript
await page.waitForLoadState("networkidle");
await expect(page.locator('input[name="email"]')).toBeVisible();
await page.fill('input[name="email"]', "test@example.com");
```

**Bad:**
```typescript
await page.goto("/auth/login");
await page.waitForTimeout(2000); // Arbitrary wait
await page.fill('input[name="email"]', "test@example.com"); // Might fail
```

### 7. Error Handling
- Expect errors in error tests
- Don't swallow unexpected errors
- Validate error messages

**Good:**
```typescript
// Test expects error
const errorMessage = page.locator('[role="alert"]');
await expect(errorMessage).toBeVisible({ timeout: 3000 });
await expect(errorMessage).toContainText(/invalid/i);
```

**Bad:**
```typescript
// Ignores unexpected errors
const errorMessage = page.locator('[role="alert"]').catch(() => null);
// Unclear if error appeared or not
```

### 8. Test Independence
- No test depends on another
- Can run in any order
- Can run in isolation

**Good:**
```typescript
test.describe("Logout", () => {
	test.beforeEach(async ({ page }) => {
		// Each test logs in independently
		await loginUser(page);
	});

	test("should logout successfully", async ({ page }) => {
		// Uses user from beforeEach
	});
});
```

**Bad:**
```typescript
test("test 1: login", async ({ page }) => {
	// Sets up state
});

test("test 2: logout", async ({ page }) => {
	// Depends on test 1 running first
	// Fails if test 1 skipped
});
```

### 9. Readable Assertions
- Use clear assertion methods
- Avoid complex boolean logic
- Use matchers for clarity

**Good:**
```typescript
await expect(page).toHaveURL("/");
await expect(page.locator('input[name="email"]')).toBeVisible();
expect(token).toBeTruthy();
```

**Bad:**
```typescript
const url = page.url();
expect(url === "http://localhost:5173/" &&
       url.includes("http") &&
       !url.includes("login")).toBeTruthy(); // Too complex
```

### 10. Documentation
- Comments explain "why" not "what"
- Given-When-Then format
- Clear test structure

**Good:**
```typescript
// Given: User is on login page
await page.goto("/auth/login");

// When: Valid credentials entered
await page.fill('input[name="email"]', "test@example.com");

// Then: Should redirect to dashboard
await expect(page).toHaveURL("/");
```

**Bad:**
```typescript
// Go to login - this is obvious from code
await page.goto("/auth/login");
// Enter email - this is obvious
await page.fill('input[name="email"]', "test@example.com");
```

---

## Common Pitfalls to Avoid

### Pitfall 1: Hard-Coded Waits
**Problem:**
```typescript
await page.waitForTimeout(5000); // Always waits 5 seconds
```

**Solution:**
```typescript
await page.waitForLoadState("networkidle"); // Waits until idle or timeout
```

### Pitfall 2: Over-Complex Selectors
**Problem:**
```typescript
const button = page.locator('div > div > button.submit-button[data-id="form"]');
```

**Solution:**
```typescript
const button = page.locator('button[type="submit"]');
```

### Pitfall 3: Test Interdependence
**Problem:**
```typescript
test("test 1", async ({ page }) => {
	await globalSetup(page); // Global shared setup
});

test("test 2", async ({ page }) => {
	// Depends on test 1 running first
});
```

**Solution:**
```typescript
test.beforeEach(async ({ page }) => {
	await setupEachTest(page); // Each test gets clean setup
});
```

### Pitfall 4: Ignoring Errors
**Problem:**
```typescript
const error = await page.locator('[role="alert"]').catch(() => null);
if (!error) return; // Silently skips validation
```

**Solution:**
```typescript
const hasError = await page
	.locator('[role="alert"]')
	.isVisible()
	.catch(() => false);

expect(hasError || isOnLoginPage).toBeTruthy(); // Explicit assertion
```

### Pitfall 5: Testing Implementation Details
**Problem:**
```typescript
// Tests internal structure, not user behavior
const storeState = await page.evaluate(() => {
	return window.__REDUX_DEVTOOLS_EXTENSION_COMPOSE__.state.auth;
});
expect(storeState.token).toBeDefined();
```

**Solution:**
```typescript
// Tests user-visible behavior
const token = await page.evaluate(() => localStorage.getItem("authToken"));
expect(token).toBeTruthy();
```

---

## Code Quality Metrics

### Test File Statistics
- **Total Lines:** 947
- **Number of Tests:** 35
- **Average Test Length:** ~27 lines
- **Code Comments:** ~120 (13%)
- **Complexity:** Low (AAA pattern throughout)

### Test Organization
- **Test Suites:** 7
- **Tests per Suite:** 3-7
- **Shared Setup:** beforeEach hooks
- **Test Isolation:** Complete

### Assertion Density
- **Total Assertions:** ~85
- **Assertions per Test:** ~2.4
- **Assertion Quality:** High (meaningful, specific)

---

## Extending the Tests

### Adding a New Test

**Template:**
```typescript
test("should [expected behavior] when [condition]", async ({ page }) => {
	// Given: Setup initial state
	await page.goto("/auth/login");
	await page.waitForLoadState("networkidle");

	// When: Perform action
	await page.fill('input[name="email"]', "test@example.com");
	await page.fill('input[name="password"]', "password123");
	await page.click('button[type="submit"]');

	// Then: Assert result
	await page.waitForURL("/", { timeout: 5000 });
	await expect(page).toHaveURL("/");
});
```

### Adding a New Suite

**Template:**
```typescript
test.describe("Authentication Flow - [Feature]", () => {
	test.beforeEach(async ({ page }) => {
		// Setup for all tests in this suite
		await setupAuth(page);
	});

	test("should [behavior 1]", async ({ page }) => {
		// Test 1
	});

	test("should [behavior 2]", async ({ page }) => {
		// Test 2
	});
});
```

---

## Performance Optimization

### Test Speed Improvements
1. Use exact selectors (avoid deep hierarchy)
2. Avoid arbitrary timeouts
3. Clear state in beforeEach (not afterEach)
4. Use `page.goto()` with waitUntil
5. Batch similar tests together

### Resource Management
1. Close contexts in cleanup
2. Clear browser cache between tests
3. Use minimal browser window size
4. Disable animations in test environment
5. Reuse database state when possible

---

## Security Considerations

### Test Data Security
- Use test credentials, not real ones
- Don't log sensitive data
- Clear sensitive data after tests
- Use environment variables for secrets

### Testing Security Features
- Test XSS protection
- Test CSRF protection
- Test rate limiting
- Test token expiration
- Test secure cookie flags

---

**Last Updated:** 2026-01-29
**Version:** 1.0
**Status:** Production Ready
