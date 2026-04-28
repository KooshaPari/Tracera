# API Client Quick Reference

## File Location
- **Main:** `/frontend/apps/web/src/api/client.ts`
- **Types:** `/frontend/apps/web/src/api/schema.ts` (auto-generated)
- **Usage Examples:** `/frontend/apps/web/src/api/endpoints.ts`

## Key Exports

```typescript
// Main client instance
export const apiClient: ReturnType<typeof createClient<any>>;

// Error handling
export class ApiError extends Error;

// Helpers
export async function handleApiResponse<T>(promise): Promise<T>;
export function safeApiCall<T>(apiCall): Promise<...>;

// Auth
export async function validateSession(): Promise<boolean>;

// Config
export const API_BASE_URL: string;
```

## Basic Usage Pattern

```typescript
// 1. Make API call with proper typing
const response = await handleApiResponse<User>(
    safeApiCall(
        apiClient.GET("/api/v1/auth/me", { params: { query: {...} } })
    )
);

// 2. Response is properly typed
console.log(response.id, response.email);  // IntelliSense works

// 3. Error handling is automatic
try {
    const data = await handleApiResponse<T>(apiCall);
} catch (error) {
    if (error instanceof ApiError) {
        // Handle API errors
    }
}
```

## Available HTTP Methods

```typescript
// GET - Retrieve data
apiClient.GET(path, { params: { query, path } });

// POST - Create/Execute
apiClient.POST(path, { params: { path, query }, body });

// PUT - Full update
apiClient.PUT(path, { params: { path, query }, body });

// PATCH - Partial update
apiClient.PATCH(path, { params: { path, query }, body });

// DELETE - Remove
apiClient.DELETE(path, { params: { path, query } });
```

## Common Patterns

### Fetch Single Item
```typescript
const item = await handleApiResponse<Item>(
    safeApiCall(
        apiClient.GET("/api/v1/items/{id}", {
            params: { path: { id: itemId } }
        })
    )
);
```

### Fetch with Query Parameters
```typescript
const items = await handleApiResponse<{ items: Item[] }>(
    safeApiCall(
        apiClient.GET("/api/v1/items", {
            params: { query: { limit: 10, offset: 0 } }
        })
    )
);
```

### Create with Body
```typescript
const newItem = await handleApiResponse<Item>(
    safeApiCall(
        apiClient.POST("/api/v1/items", {
            body: { title: "New Item", description: "..." }
        })
    )
);
```

### Update Resource
```typescript
const updated = await handleApiResponse<Item>(
    safeApiCall(
        apiClient.PUT("/api/v1/items/{id}", {
            params: { path: { id: itemId } },
            body: { title: "Updated" }
        })
    )
);
```

### Delete Resource
```typescript
await handleApiResponse<void>(
    safeApiCall(
        apiClient.DELETE("/api/v1/items/{id}", {
            params: { path: { id: itemId } }
        })
    )
);
```

## Type Safety Examples

### Correct Usage ✅
```typescript
// Type is specified
const user = await handleApiResponse<User>(call);
// user.id and user.email available with IntelliSense

const users = await handleApiResponse<User[]>(call);
// users[0].id available with IntelliSense

const response = await handleApiResponse<{ items: Item[] }>(call);
// response.items available with IntelliSense
```

### Incorrect Usage ❌
```typescript
// No type specified - returns unknown
const result = await handleApiResponse(call);
// result.anything is not type-safe

// Wrong type specified - runtime error likely
const item = await handleApiResponse<string>(call);
// Runtime error if response isn't a string
```

## Error Handling

### ApiError Class
```typescript
class ApiError extends Error {
    status: number;        // HTTP status code
    statusText: string;    // HTTP status text
    data?: unknown;        // Response body on error
}
```

### Catching Errors
```typescript
try {
    const data = await handleApiResponse<T>(apiCall);
} catch (error) {
    if (error instanceof ApiError) {
        console.error(`API Error ${error.status}: ${error.statusText}`);
        console.error("Response:", error.data);
    } else {
        console.error("Other error:", error);
    }
}
```

## Authentication

### Session Validation
```typescript
// Call on app startup
const isValid = await validateSession();
if (!isValid) {
    // User not logged in, redirect handled automatically
}
```

### Automatic Features
- ✅ HTTP-Only cookies sent automatically
- ✅ CSRF tokens added to requests
- ✅ 401 responses trigger logout
- ✅ Session stored server-side only

## Debugging

### View Request Headers
```typescript
// Open DevTools → Network tab → Filter by /api/v1/
// Check:
// - Cookie header (should be present)
// - X-CSRF-Token header (should be present)
// - Content-Type: application/json
```

### Check Current CSRF Token
```typescript
import { getCSRFToken } from "@/lib/csrf";
console.log("Current CSRF token:", getCSRFToken());
```

### Validate Session
```typescript
const isValid = await validateSession();
console.log("Session valid:", isValid);
```

### Log API Calls
```typescript
// In client.ts middleware (add temporary logging):
onRequest: async ({ request }) => {
    console.log(`[API] ${request.method} ${request.url}`);
    return request;
}
```

## Configuration

### Change API Base URL
```typescript
// Set environment variable
VITE_API_URL=https://api.example.com

// Fallback (used if not set)
// Defaults to http://localhost:8000
```

## Middleware

### CSRF Protection
- Automatically added to POST/PUT/DELETE/PATCH
- Token refreshed from response headers
- Validates token on each request

### Auth Interceptor
- Detects 401 responses
- Triggers automatic logout
- Redirects to /login

### Error Response Handling
- Extracts error data
- Converts to ApiError
- Provides stack trace information

## Best Practices

### Do ✅
- Always specify the response type: `<T>`
- Use `handleApiResponse<T>()` for validation
- Use `safeApiCall<T>()` for error safety
- Let middleware handle CSRF automatically
- Check `error instanceof ApiError` in catch blocks

### Don't ❌
- Don't use `any` for response types
- Don't bypass `handleApiResponse()`
- Don't manually set CSRF headers
- Don't try to refresh tokens manually
- Don't ignore API errors

## Common Endpoints

### Authentication
```typescript
apiClient.POST("/api/v1/auth/login", { body: { email, password } });
apiClient.GET("/api/v1/auth/me", {});
apiClient.POST("/api/v1/auth/logout", {});
```

### Projects
```typescript
apiClient.GET("/api/v1/projects", { params: { query: { limit: 10 } } });
apiClient.GET("/api/v1/projects/{id}", { params: { path: { id } } });
apiClient.POST("/api/v1/projects", { body: { name, description } });
```

### Items
```typescript
apiClient.GET("/api/v1/items", { params: { query: { limit: 10 } } });
apiClient.GET("/api/v1/items/{id}", { params: { path: { id } } });
apiClient.POST("/api/v1/items", { body: { title, description } });
```

### Links
```typescript
apiClient.GET("/api/v1/links", { params: { query: { limit: 10 } } });
apiClient.POST("/api/v1/links", { body: { source_id, target_id } });
```

### Analysis
```typescript
apiClient.GET("/api/v1/graph/impact/{id}", { params: { path: { id } } });
apiClient.GET("/api/v1/analysis/cycles/{project_id}", { params: { path: { project_id } } });
```

## Troubleshooting

### 401 Unauthorized
- Session expired
- Check if logged in: `await validateSession()`
- Middleware redirects to /login automatically

### 403 Forbidden
- CSRF token mismatch
- Check CSRF token: `getCSRFToken()`
- Middleware tries to refresh automatically

### 404 Not Found
- Wrong endpoint URL
- Check path parameters are provided
- Verify endpoint exists in schema.ts

### Type Errors
- Specify explicit generic type: `handleApiResponse<T>()`
- Check type matches actual response
- Use exact path from schema if defined

### Missing Data
- Check response structure
- Verify API returns data field
- Some endpoints may return different structure

## Links

- Source: `/frontend/apps/web/src/api/client.ts`
- Schema: `/frontend/apps/web/src/api/schema.ts`
- Examples: `/frontend/apps/web/src/api/endpoints.ts`
- Auth: `/frontend/apps/web/src/api/auth.ts`

## Support

For detailed information, see:
- `API_CLIENT_TECHNICAL_REFERENCE.md` - Full technical guide
- `API_CLIENT_UPDATE_SUMMARY.md` - Design decisions
- `API_CLIENT_COMPLETION_CHECKLIST.md` - Status and verification
