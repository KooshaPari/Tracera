# API Documentation Setup - Swagger UI & ReDoc

Complete setup for interactive API documentation using Swagger UI and ReDoc with OpenAPI 3.1 specification.

## Overview

This setup provides two complementary API documentation interfaces:

- **Swagger UI** (`/api-docs/swagger`) - Interactive documentation with "Try it out" functionality
- **ReDoc** (`/api-docs/redoc`) - Clean, responsive reference documentation
- **Index Page** (`/api-docs`) - Documentation gateway with quick links

## Directory Structure

```
frontend/apps/web/
├── public/
│   └── specs/
│       └── openapi.json              # OpenAPI 3.1 specification
├── src/
│   ├── components/
│   │   └── api-docs/
│   │       ├── swagger-ui-wrapper.tsx  # Swagger UI component
│   │       └── redoc-wrapper.tsx       # ReDoc component
│   ├── lib/
│   │   └── openapi-utils.ts          # Utility functions
│   └── routes/
│       ├── api/
│       │   ├── spec.ts               # GET /api/spec
│       │   ├── swagger-config.ts     # GET /api/swagger-config
│       │   └── auth-test.ts          # POST /api/auth-test
│       └── api-docs/
│           ├── index.tsx             # /api-docs (landing page)
│           ├── swagger.tsx           # /api-docs/swagger
│           └── redoc.tsx             # /api-docs/redoc
```

## Installed Packages

```json
{
  "dependencies": {
    "swagger-ui-react": "^5.30.3",
    "redoc": "^2.5.2"
  }
}
```

## Features

### Swagger UI Features
- ✅ Interactive "Try it out" functionality
- ✅ Request/response examples
- ✅ Authentication testing (Bearer token & API key)
- ✅ Dark/light mode toggle
- ✅ Download OpenAPI spec
- ✅ Copy spec URL
- ✅ Request duration tracking
- ✅ Deep linking support
- ✅ Filter endpoints
- ✅ Persistent authorization

### ReDoc Features
- ✅ Clean three-panel layout
- ✅ Responsive design
- ✅ Dark/light mode toggle
- ✅ Download OpenAPI spec
- ✅ Search functionality
- ✅ Code examples in multiple languages
- ✅ Deep linking support
- ✅ Required props first
- ✅ Expand/collapse sections

### Utility Functions
- ✅ Fetch and validate OpenAPI specs
- ✅ Extract HTTP methods and tags
- ✅ Check authentication requirements
- ✅ Generate code examples (cURL, JavaScript, Python, TypeScript)
- ✅ Format paths with parameters
- ✅ Parse response examples
- ✅ Auth token storage helpers

## API Routes

### 1. GET /api/spec
Returns the OpenAPI specification.

**Response:**
```json
{
  "openapi": "3.1.0",
  "info": { ... },
  "paths": { ... }
}
```

### 2. GET /api/swagger-config
Returns Swagger UI configuration.

**Response:**
```json
{
  "apiUrl": "http://localhost:8000",
  "authType": "bearer",
  "persistAuth": true,
  "tryItOut": true
}
```

### 3. POST /api/auth-test
Test authentication credentials.

**Headers:**
- `Authorization: Bearer <token>` OR
- `X-API-Key: <api-key>`

**Response:**
```json
{
  "timestamp": "2025-12-01T00:00:00Z",
  "authentication": {
    "bearer": {
      "present": true,
      "valid": true,
      "token": "eyJhbGciOi...",
      "type": "Bearer"
    }
  },
  "authenticated": true,
  "message": "Bearer token authentication successful"
}
```

## Usage

### Accessing Documentation

1. **Landing Page**: Navigate to `/api-docs`
2. **Swagger UI**: Navigate to `/api-docs/swagger`
3. **ReDoc**: Navigate to `/api-docs/redoc`

### Authentication Setup

#### For Swagger UI:
1. Click "Authorize" button at the top
2. Enter your Bearer token or API key
3. Click "Authorize"
4. Token is persisted in localStorage

#### For ReDoc:
Authentication credentials are automatically included from localStorage if available.

### Testing Authentication

Use the `/api/auth-test` endpoint to verify your credentials:

```bash
# Test Bearer token
curl -X POST http://localhost:3000/api/auth-test \
  -H "Authorization: Bearer your-token-here" \
  -H "Content-Type: application/json"

# Test API key
curl -X POST http://localhost:3000/api/auth-test \
  -H "X-API-Key: your-api-key-here" \
  -H "Content-Type: application/json"
```

### Using Utility Functions

```typescript
import {
  fetchOpenAPISpec,
  validateOpenAPISpec,
  generateCodeExamples,
  authStorage,
} from '@/lib/openapi-utils';

// Fetch and validate spec
const spec = await fetchOpenAPISpec('/specs/openapi.json');
const isValid = validateOpenAPISpec(spec);

// Generate code examples
const examples = generateCodeExamples(
  'GET',
  '/api/v1/items',
  'http://localhost:8000',
  'your-token'
);

console.log(examples.curl);
console.log(examples.javascript);
console.log(examples.python);

// Manage authentication
authStorage.setToken('your-token');
const token = authStorage.getToken();
authStorage.clearAll();
```

## Customization

### Swagger UI Configuration

Edit `/src/components/api-docs/swagger-ui-wrapper.tsx`:

```typescript
<SwaggerUIWrapper
  specUrl="/specs/openapi.json"
  tryItOutEnabled={true}
  persistAuthorization={true}
  displayRequestDuration={true}
  filter={true}
  deepLinking={true}
  // Add custom interceptors
  requestInterceptor={(req) => {
    // Modify requests
    return req;
  }}
  responseInterceptor={(res) => {
    // Handle responses
    return res;
  }}
/>
```

### ReDoc Configuration

Edit `/src/components/api-docs/redoc-wrapper.tsx`:

```typescript
<RedocWrapper
  specUrl="/specs/openapi.json"
  scrollYOffset={80}
  hideDownloadButton={false}
  disableSearch={false}
  expandResponses="200,201"
  requiredPropsFirst={true}
  sortPropsAlphabetically={false}
  expandSingleSchemaField={true}
/>
```

### Updating OpenAPI Spec

Edit `/public/specs/openapi.json` to update your API specification. The spec follows OpenAPI 3.1.0 standard.

Key sections:
- `info`: API metadata
- `servers`: API server URLs
- `tags`: Endpoint groupings
- `paths`: API endpoints
- `components`: Reusable schemas and security schemes

## OpenAPI Spec Structure

The included spec documents the TraceRTM API with:

### Endpoints
- **Health**: `/health`
- **Items**: `/api/v1/items`, `/api/v1/items/{item_id}`
- **Links**: `/api/v1/links`
- **Analysis**:
  - `/api/v1/analysis/impact/{item_id}`
  - `/api/v1/analysis/cycles/{project_id}`
  - `/api/v1/analysis/shortest-path`

### Security Schemes
- **Bearer Token**: JWT authentication
- **API Key**: Header-based API key (`X-API-Key`)

### Response Formats
- Success: 200, 201
- Client Errors: 400, 401, 404
- Server Errors: 500

## Code Examples

### Fetch Items
```bash
curl -X GET "http://localhost:8000/api/v1/items?project_id=123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Impact Analysis
```bash
curl -X GET "http://localhost:8000/api/v1/analysis/impact/456?project_id=123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Detect Cycles
```bash
curl -X GET "http://localhost:8000/api/v1/analysis/cycles/123" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## Dark Mode

Both Swagger UI and ReDoc support dark mode:
- Toggle using the moon/sun icon in the toolbar
- Preference is saved to localStorage
- Automatically detects system preference on first load

## Responsive Design

All documentation pages are fully responsive:
- Desktop: Full three-panel layout
- Tablet: Optimized two-panel layout
- Mobile: Stacked single-column layout

## Browser Support

- Chrome/Edge: Full support
- Firefox: Full support
- Safari: Full support
- Mobile browsers: Full support

## Performance

- OpenAPI spec is cached for 1 hour
- Swagger config cached for 5 minutes
- Lazy loading of large schemas
- Optimized rendering with virtualization

## Troubleshooting

### Spec not loading
1. Check `/public/specs/openapi.json` exists
2. Verify JSON is valid
3. Check browser console for errors
4. Ensure API route `/api/spec` is accessible

### Authentication not working
1. Verify token is stored: `localStorage.getItem('api_token')`
2. Check token format (Bearer + space + token)
3. Test with `/api/auth-test` endpoint
4. Verify API server accepts the token

### Dark mode not persisting
1. Check localStorage is enabled
2. Clear browser cache
3. Check for conflicting CSS

## Next Steps

1. **Update OpenAPI Spec**: Modify `/public/specs/openapi.json` with your actual API
2. **Add More Endpoints**: Document all your API endpoints
3. **Configure Authentication**: Set up real authentication validation
4. **Add Examples**: Include request/response examples for each endpoint
5. **Deploy**: Deploy to production with proper CORS and security headers

## Resources

- [OpenAPI 3.1 Specification](https://spec.openapis.org/oas/v3.1.0)
- [Swagger UI Documentation](https://swagger.io/docs/open-source-tools/swagger-ui/)
- [ReDoc Documentation](https://redocly.com/docs/redoc/)
- [TanStack Router](https://tanstack.com/router)

## Support

For issues or questions:
- Check the documentation above
- Review the OpenAPI spec format
- Test with `/api/auth-test` endpoint
- Check browser console for errors
