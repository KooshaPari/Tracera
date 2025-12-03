# API Documentation Quick Reference

## Quick Links

- **Landing Page**: [/api-docs](/api-docs)
- **Swagger UI**: [/api-docs/swagger](/api-docs/swagger)
- **ReDoc**: [/api-docs/redoc](/api-docs/redoc)
- **OpenAPI Spec**: [/specs/openapi.json](/specs/openapi.json)

## Common Tasks

### View Documentation
```bash
# Start dev server
bun run dev

# Navigate to:
http://localhost:3000/api-docs
```

### Test Authentication
```bash
# Set token in browser console
localStorage.setItem('api_token', 'your-token-here');

# Or use the auth test endpoint
curl -X POST http://localhost:3000/api/auth-test \
  -H "Authorization: Bearer your-token"
```

### Download OpenAPI Spec
```bash
# Via browser
http://localhost:3000/specs/openapi.json

# Via curl
curl http://localhost:3000/api/spec -o openapi.json

# Via API docs
# Click "Download Spec" button in Swagger UI or ReDoc
```

### Generate Code Examples
```typescript
import { generateCodeExamples } from '@/lib/openapi-utils';

const examples = generateCodeExamples(
  'GET',
  '/api/v1/items',
  'http://localhost:8000',
  'your-token'
);

console.log('cURL:', examples.curl);
console.log('JavaScript:', examples.javascript);
console.log('Python:', examples.python);
console.log('TypeScript:', examples.typescript);
```

## File Locations

| File | Purpose |
|------|---------|
| `/public/specs/openapi.json` | OpenAPI specification |
| `/src/components/api-docs/swagger-ui-wrapper.tsx` | Swagger UI component |
| `/src/components/api-docs/redoc-wrapper.tsx` | ReDoc component |
| `/src/lib/openapi-utils.ts` | Utility functions |
| `/src/routes/api-docs/index.tsx` | Landing page |
| `/src/routes/api-docs/swagger.tsx` | Swagger route |
| `/src/routes/api-docs/redoc.tsx` | ReDoc route |
| `/src/routes/api/spec.ts` | Spec API endpoint |
| `/src/routes/api/swagger-config.ts` | Config API endpoint |
| `/src/routes/api/auth-test.ts` | Auth test endpoint |

## API Endpoints

### GET /api/spec
Returns OpenAPI specification
```bash
curl http://localhost:3000/api/spec
```

### GET /api/swagger-config
Returns Swagger configuration
```bash
curl http://localhost:3000/api/swagger-config
```

### POST /api/auth-test
Tests authentication
```bash
curl -X POST http://localhost:3000/api/auth-test \
  -H "Authorization: Bearer token" \
  -H "Content-Type: application/json"
```

## Utility Functions

```typescript
// Fetch spec
const spec = await fetchOpenAPISpec('/specs/openapi.json');

// Validate spec
const isValid = validateOpenAPISpec(spec);

// Get HTTP methods
const methods = getHttpMethods(spec);

// Get tags
const tags = getTags(spec);

// Check if auth required
const needsAuth = requiresAuth(spec);

// Get auth types
const authTypes = getSupportedAuthTypes(spec);

// Get server URLs
const urls = getServerUrls(spec);

// Generate code examples
const examples = generateCodeExamples('GET', '/api/v1/items', 'http://localhost:8000');

// Download spec
downloadSpec(spec, 'my-api.json');

// Get endpoint by operation ID
const endpoint = getEndpointByOperationId(spec, 'listItems');

// Format path with params
const path = formatPathWithParams('/items/{id}', { id: '123' });

// Get response examples
const examples = getResponseExamples(operation);

// Auth storage
authStorage.setToken('token');
authStorage.setApiKey('key');
const token = authStorage.getToken();
authStorage.clearAll();
```

## Component Props

### SwaggerUIWrapper
```typescript
<SwaggerUIWrapper
  specUrl="/specs/openapi.json"      // URL to spec
  spec={specObject}                   // Or pass spec object
  tryItOutEnabled={true}              // Enable try-it-out
  persistAuthorization={true}         // Persist auth
  displayRequestDuration={true}       // Show request time
  filter={true}                       // Enable filtering
  deepLinking={true}                  // Enable deep links
  requestInterceptor={(req) => req}   // Request interceptor
  responseInterceptor={(res) => res}  // Response interceptor
/>
```

### RedocWrapper
```typescript
<RedocWrapper
  specUrl="/specs/openapi.json"       // URL to spec
  spec={specObject}                   // Or pass spec object
  scrollYOffset={80}                  // Scroll offset
  hideDownloadButton={false}          // Show download
  disableSearch={false}               // Enable search
  expandResponses="200,201"           // Auto-expand responses
  requiredPropsFirst={true}           // Sort by required
  sortPropsAlphabetically={false}     // Alpha sorting
  showExtensions={false}              // Show extensions
  expandSingleSchemaField={true}      // Auto-expand single
/>
```

## Customization

### Change API Base URL
Update `openapi.json`:
```json
{
  "servers": [
    {
      "url": "https://your-api.com",
      "description": "Production"
    }
  ]
}
```

### Add New Endpoint
Update `openapi.json` paths:
```json
{
  "paths": {
    "/api/v1/new-endpoint": {
      "get": {
        "tags": ["New"],
        "summary": "New endpoint",
        "operationId": "newEndpoint",
        "responses": {
          "200": {
            "description": "Success"
          }
        }
      }
    }
  }
}
```

### Add Authentication Scheme
Update `openapi.json` components:
```json
{
  "components": {
    "securitySchemes": {
      "oauth2": {
        "type": "oauth2",
        "flows": {
          "authorizationCode": {
            "authorizationUrl": "https://auth.example.com/oauth/authorize",
            "tokenUrl": "https://auth.example.com/oauth/token",
            "scopes": {
              "read": "Read access",
              "write": "Write access"
            }
          }
        }
      }
    }
  }
}
```

### Custom Theme
Edit wrapper components to customize colors, fonts, etc.

## Troubleshooting

### Spec not loading
```typescript
// Check if file exists
fetch('/specs/openapi.json').then(r => console.log(r.status));

// Validate JSON
fetch('/specs/openapi.json')
  .then(r => r.json())
  .then(j => console.log('Valid JSON:', j));
```

### Auth not working
```typescript
// Check stored token
console.log('Token:', localStorage.getItem('api_token'));

// Test auth endpoint
fetch('/api/auth-test', {
  method: 'POST',
  headers: {
    'Authorization': 'Bearer ' + localStorage.getItem('api_token')
  }
}).then(r => r.json()).then(console.log);
```

### Clear cache
```typescript
// Clear auth
localStorage.removeItem('api_token');
localStorage.removeItem('api_key');

// Clear browser cache
// Cmd+Shift+R (Mac) or Ctrl+Shift+R (Windows)
```

## Environment Variables

Create `.env` file:
```bash
# API base URL
API_URL=http://localhost:8000

# Public URL (for OAuth redirects)
PUBLIC_URL=http://localhost:3000

# Enable debug logging
DEBUG=true
```

## Production Checklist

- [ ] Update server URLs in `openapi.json`
- [ ] Remove development endpoints
- [ ] Add real authentication validation
- [ ] Configure CORS headers
- [ ] Enable HTTPS
- [ ] Add rate limiting
- [ ] Set up monitoring
- [ ] Test all endpoints
- [ ] Document all parameters
- [ ] Add response examples
- [ ] Review security schemes
- [ ] Test authentication flows
- [ ] Verify deep links work
- [ ] Check mobile responsiveness
- [ ] Test in all browsers

## Support

- OpenAPI Spec: https://spec.openapis.org/oas/v3.1.0
- Swagger UI: https://swagger.io/docs/
- ReDoc: https://redocly.com/docs/
