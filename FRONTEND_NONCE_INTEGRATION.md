# Frontend Nonce Integration Guide

## Overview

This guide demonstrates how to integrate the nonce-based CSP system with your Next.js frontend.

## Step 1: Server-Side Nonce Injection

### Backend Handler

```go
// backend/internal/handlers/page.go
package handlers

import (
	"net/http"
	"github.com/labstack/echo/v4"
	"github.com/kooshapari/tracertm-backend/internal/middleware"
	"github.com/kooshapari/tracertm-backend/internal/templates"
)

func RenderIndex(c echo.Context) error {
	nonce := middleware.GetNonce(c)

	return c.Render(http.StatusOK, "index.html", map[string]interface{}{
		"Nonce": nonce,
	})
}
```

## Step 2: HTML Template with Nonce

### Template File (index.html)

```html
<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>Trace RTM</title>

	<!-- Critical CSS with nonce -->
	<style nonce="{{ .Nonce }}">
		/* Critical CSS only - loaded before React */
		html {
			background: #fff;
			color: #000;
		}
		body {
			margin: 0;
			font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', 'Roboto', sans-serif;
		}
		#root {
			display: flex;
			justify-content: center;
			align-items: center;
			height: 100vh;
		}
	</style>
</head>
<body>
	<div id="root"></div>

	<!-- React App Entry Script with nonce -->
	<script nonce="{{ .Nonce }}" src="/app.js"></script>

	<!-- Initialize App with Nonce -->
	<script nonce="{{ .Nonce }}">
		window.__CSP_NONCE__ = "{{ .Nonce }}";
		window.__APP_CONFIG__ = {
			nonce: "{{ .Nonce }}",
			apiBaseUrl: "/api",
			environment: "{{ .Environment }}"
		};
	</script>
</body>
</html>
```

## Step 3: React Component Integration

### Access Nonce in React

```typescript
// frontend/apps/web/src/hooks/useCspNonce.ts
export function useCspNonce(): string {
	const [nonce, setNonce] = React.useState<string>('');

	React.useEffect(() => {
		// Method 1: From window global
		if (typeof window !== 'undefined' && window.__CSP_NONCE__) {
			setNonce(window.__CSP_NONCE__);
		}
		// Method 2: From DOM meta tag
		else if (typeof document !== 'undefined') {
			const metaTag = document.querySelector('meta[name="csp-nonce"]');
			if (metaTag) {
				setNonce(metaTag.getAttribute('content') || '');
			}
		}
	}, []);

	return nonce;
}
```

### Use in Components

```typescript
// frontend/apps/web/src/components/Dashboard.tsx
import React from 'react';
import { useCspNonce } from '../hooks/useCspNonce';

export function Dashboard() {
	const nonce = useCspNonce();

	// Example: Dynamic script injection with nonce
	const handleAddScript = React.useCallback((scriptCode: string) => {
		const script = document.createElement('script');
		script.setAttribute('nonce', nonce);
		script.textContent = scriptCode;
		document.head.appendChild(script);
	}, [nonce]);

	// Example: Dynamic style injection with nonce
	const handleAddStyle = React.useCallback((css: string) => {
		const style = document.createElement('style');
		style.setAttribute('nonce', nonce);
		style.textContent = css;
		document.head.appendChild(style);
	}, [nonce]);

	return (
		<div>
			<h1>Dashboard</h1>
			{/* Your dashboard content */}
		</div>
	);
}
```

## Step 4: Handling Dynamic Content

### Pattern 1: API Response with Nonce

Backend:
```go
func getPageConfig(c echo.Context) error {
	nonce := middleware.GetNonce(c)
	return c.JSON(http.StatusOK, map[string]interface{}{
		"nonce": nonce,
		"config": pageConfig,
	})
}
```

Frontend:
```typescript
// frontend/apps/web/src/api/config.ts
export async function fetchPageConfig() {
	const response = await fetch('/api/page-config');
	const { nonce, config } = await response.json();
	return { nonce, config };
}

// Usage in component
const { nonce, config } = await fetchPageConfig();

// Use nonce for dynamic content
const script = document.createElement('script');
script.nonce = nonce;
script.src = '/dynamic-script.js';
document.head.appendChild(script);
```

### Pattern 2: Inline Event Handlers

**DO NOT do this:**
```html
<!-- BLOCKED by CSP -->
<button onclick="handleClick()">Click</button>
```

**DO this instead:**
```typescript
export function MyButton() {
	const handleClick = () => {
		console.log('Button clicked');
	};

	return (
		<button onClick={handleClick}>
			Click
		</button>
	);
}
```

## Step 5: Styled Components & CSS-in-JS

### Emotion/Styled Components

```typescript
// frontend/apps/web/src/components/StyledButton.tsx
import styled from '@emotion/styled';

export const StyledButton = styled.button`
	background-color: blue;
	color: white;
	padding: 10px 20px;
	border: none;
	border-radius: 4px;
	cursor: pointer;

	&:hover {
		background-color: darkblue;
	}
`;

// This is SAFE with CSP because Emotion injects nonce automatically
export function MyButton() {
	return <StyledButton>Click me</StyledButton>;
}
```

### Emotion with Nonce (Advanced)

```typescript
import { CacheProvider } from '@emotion/react';
import createCache from '@emotion/cache';

// Create cache with nonce
function createEmotionCache(nonce: string) {
	return createCache({
		key: 'css',
		nonce: nonce,
	});
}

// Use in app
const nonce = useCspNonce();
const cache = React.useMemo(() => createEmotionCache(nonce), [nonce]);

return (
	<CacheProvider value={cache}>
		<App />
	</CacheProvider>
);
```

## Step 6: Testing CSP Violations

### Manual Testing

1. Open browser DevTools (F12)
2. Go to Console tab
3. Try inline script without nonce:
```javascript
eval('console.log("This will be blocked")');
// Output: Refused to execute the script...
```

4. Check CSP header:
```bash
curl -i http://localhost:3000 | grep -i content-security-policy
```

### Automated Testing

```typescript
// frontend/apps/web/e2e/csp.spec.ts
import { test, expect } from '@playwright/test';

test('CSP header is present with nonce', async ({ page }) => {
	await page.goto('http://localhost:3000');

	// Check CSP header
	const response = await page.context().request.get('http://localhost:3000');
	const csp = response.headers()['content-security-policy'];

	expect(csp).toContain('nonce-');
	expect(csp).not.toContain('unsafe-inline');
	expect(csp).not.toContain('unsafe-eval');
});

test('inline scripts without nonce are blocked', async ({ page, context }) => {
	const violations: string[] = [];

	// Listen for CSP violations
	page.on('console', msg => {
		if (msg.type() === 'error') {
			violations.push(msg.text());
		}
	});

	await page.goto('http://localhost:3000');

	// Try to execute inline script
	await page.evaluate(() => {
		// This should fail silently due to CSP
		eval('console.log("xss")');
	});

	// Verify no eval execution
	expect(violations.length).toBeGreaterThan(0);
});
```

## Step 7: Common Patterns

### Pattern: Loading External Scripts

```typescript
// SAFE - external scripts loaded from same origin
<script src="/scripts/app.js"></script>

// SAFE - external scripts from trusted CDN (if added to CSP)
<script src="https://cdn.example.com/lib.js"></script>

// REQUIRES NONCE - inline scripts
<script nonce={nonce}>
	console.log('This requires nonce');
</script>
```

### Pattern: Dynamic Content with Sanitization

```typescript
import DOMPurify from 'dompurify';

export function RichTextEditor({ content }: { content: string }) {
	// Sanitize HTML to prevent XSS
	const sanitized = DOMPurify.sanitize(content);

	return (
		<div
			dangerouslySetInnerHTML={{ __html: sanitized }}
		/>
	);
}
```

### Pattern: Analytics & Tracking

```typescript
// Safe with CSP - async loading
<script async src="https://analytics.example.com/track.js"></script>

// For inline tracking code
const nonce = useCspNonce();

const trackEvent = (event: string) => {
	const script = document.createElement('script');
	script.nonce = nonce;
	script.textContent = `
		fetch('/api/analytics', {
			method: 'POST',
			body: JSON.stringify({ event: '${event}' })
		});
	`;
	document.head.appendChild(script);
};
```

## Step 8: Migration Checklist

- [ ] Backend: Nonce generation and header setting (DONE)
- [ ] Frontend: Extract nonce from window global or meta tag
- [ ] Update HTML templates with nonce in scripts
- [ ] Update inline styles with nonce
- [ ] Remove all inline event handlers (onclick, onload, etc.)
- [ ] Use React onClick handlers instead
- [ ] Configure CSS-in-JS library to use nonce
- [ ] Test with browser DevTools CSP violations
- [ ] Run E2E tests
- [ ] Verify performance metrics
- [ ] Deploy to staging
- [ ] Monitor CSP violation reports
- [ ] Deploy to production

## Step 9: CSP Violation Monitoring

### Log Violations to Backend

```typescript
// frontend/apps/web/src/hooks/useCspViolationMonitoring.ts
export function useCspViolationMonitoring() {
	React.useEffect(() => {
		const handler = (event: SecurityPolicyViolationEvent) => {
			// Log to backend
			fetch('/api/csp-violations', {
				method: 'POST',
				headers: { 'Content-Type': 'application/json' },
				body: JSON.stringify({
					blockedUri: event.blockedURI,
					violatedDirective: event.violatedDirective,
					originalPolicy: event.originalPolicy,
					timestamp: new Date().toISOString(),
				}),
			}).catch(console.error);
		};

		document.addEventListener('securitypolicyviolation', handler);
		return () => {
			document.removeEventListener('securitypolicyviolation', handler);
		};
	}, []);
}
```

## Step 10: Troubleshooting

### Issue: Inline Scripts Not Executing

**Symptom:** Console error about CSP

**Solution:**
```typescript
// ❌ WRONG - No nonce
<script>
	console.log('test');
</script>

// ✅ RIGHT - With nonce
<script nonce={nonce}>
	console.log('test');
</script>
```

### Issue: Styles Not Applied

**Symptom:** Inline styles ignored, page looks unstyled

**Solution:**
```typescript
// ❌ WRONG - No nonce
<div style={{ color: 'red' }}>Text</div>

// ✅ RIGHT - Use styled components or style tag with nonce
<style nonce={nonce}>
	.text { color: red; }
</style>
<div className="text">Text</div>
```

### Issue: External Script Blocked

**Symptom:** CSP violation for external script

**Solution:** Add to CSP in backend:
```go
"script-src 'self' 'nonce-{NONCE}' https://trusted-domain.com; "
```

## References

- [MDN: Content-Security-Policy](https://developer.mozilla.org/en-US/docs/Web/HTTP/Headers/Content-Security-Policy)
- [OWASP: CSP Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Content_Security_Policy_Cheat_Sheet.html)
- [React: Dangerously Setting Inner HTML](https://react.dev/reference/react-dom/dangerouslySetInnerHTML)
- [DOMPurify: XSS Sanitizer](https://github.com/cure53/DOMPurify)

## Summary

Key takeaways for frontend integration:

1. **Always use nonce**: Include `nonce={nonce}` in all inline scripts and styles
2. **Prefer external files**: Load CSS/JS from external files when possible
3. **Use React patterns**: Leverage React onClick instead of inline event handlers
4. **Sanitize content**: Use DOMPurify for user-generated HTML
5. **Monitor violations**: Log CSP violations to identify issues
6. **Test thoroughly**: Verify in DevTools and E2E tests

The nonce-based CSP provides defense-in-depth against XSS attacks while maintaining full functionality for legitimate content.
