# OpenAPI Generation Guide

## Phase 2: Backend API Documentation

### 1. Add Swagger Comments to Go Handlers

**Pattern for each handler:**

```go
// @Summary Create a new project
// @Description Creates a new project with the given name and description
// @Tags Projects
// @Accept json
// @Produce json
// @Param request body CreateProjectRequest true "Project data"
// @Success 201 {object} Project "Project created successfully"
// @Failure 400 {object} ErrorResponse "Invalid request"
// @Failure 401 {object} ErrorResponse "Unauthorized"
// @Failure 500 {object} ErrorResponse "Internal server error"
// @Router /projects [post]
// @Security Bearer
func (h *ProjectHandler) CreateProject(c echo.Context) error {
    // Implementation
}
```

### 2. Define Request/Response Models

**backend/internal/models/openapi.go:**

```go
package models

// CreateProjectRequest represents a project creation request
// @Description Project creation request body
type CreateProjectRequest struct {
    // Project name (required)
    // @example "My Project"
    Name string `json:"name" validate:"required,min=1,max=255"`
    
    // Project description (optional)
    // @example "A project for tracking requirements"
    Description string `json:"description" validate:"max=1000"`
    
    // Project metadata (optional)
    // @example {"team":"engineering","priority":"high"}
    Metadata map[string]interface{} `json:"metadata"`
}

// Project represents a project
// @Description A project in TraceRTM
type Project struct {
    // Project ID
    // @example "550e8400-e29b-41d4-a716-446655440000"
    ID string `json:"id"`
    
    // Project name
    // @example "My Project"
    Name string `json:"name"`
    
    // Project description
    // @example "A project for tracking requirements"
    Description string `json:"description"`
    
    // Creation timestamp
    // @example "2025-12-02T10:00:00Z"
    CreatedAt time.Time `json:"created_at"`
    
    // Last update timestamp
    // @example "2025-12-02T10:00:00Z"
    UpdatedAt time.Time `json:"updated_at"`
}

// ErrorResponse represents an error response
// @Description Standard error response format
type ErrorResponse struct {
    // Error code
    // @example "INVALID_REQUEST"
    Code string `json:"code"`
    
    // Error message
    // @example "Invalid request parameters"
    Message string `json:"message"`
    
    // Error details (optional)
    // @example {"field":"name","reason":"required"}
    Details map[string]interface{} `json:"details,omitempty"`
}
```

### 3. Install Swag

```bash
cd backend
go install github.com/swaggo/swag/cmd/swag@latest
```

### 4. Generate OpenAPI Spec

```bash
# Generate from comments
swag init -g main.go

# Output: docs/swagger.yaml, docs/swagger.json
```

### 5. Create Generation Script

**docs/scripts/generate-openapi.ts:**

```typescript
import fs from 'fs'
import path from 'path'
import yaml from 'yaml'

interface OpenAPISpec {
  openapi: string
  info: {
    title: string
    version: string
    description: string
    contact: { name: string; url: string }
    license: { name: string }
  }
  servers: Array<{ url: string; description: string }>
  paths: Record<string, any>
  components: {
    schemas: Record<string, any>
    securitySchemes: Record<string, any>
    responses: Record<string, any>
  }
}

function generateOpenAPI(): OpenAPISpec {
  return {
    openapi: '3.1.0',
    info: {
      title: 'TraceRTM API',
      version: '1.0.0',
      description: 'Multi-view Requirements Traceability System API',
      contact: {
        name: 'TraceRTM Team',
        url: 'https://tracertm.com',
      },
      license: {
        name: 'MIT',
      },
    },
    servers: [
      {
        url: 'https://api.tracertm.com/api/v1',
        description: 'Production',
      },
      {
        url: 'http://localhost:8080/api/v1',
        description: 'Development',
      },
    ],
    paths: {
      '/projects': {
        get: {
          summary: 'List projects',
          tags: ['Projects'],
          parameters: [
            {
              name: 'limit',
              in: 'query',
              schema: { type: 'integer', default: 20 },
            },
            {
              name: 'offset',
              in: 'query',
              schema: { type: 'integer', default: 0 },
            },
          ],
          responses: {
            '200': {
              description: 'Success',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/ProjectList' },
                },
              },
            },
            '401': { $ref: '#/components/responses/Unauthorized' },
            '500': { $ref: '#/components/responses/ServerError' },
          },
        },
        post: {
          summary: 'Create project',
          tags: ['Projects'],
          requestBody: {
            required: true,
            content: {
              'application/json': {
                schema: { $ref: '#/components/schemas/CreateProjectRequest' },
              },
            },
          },
          responses: {
            '201': {
              description: 'Created',
              content: {
                'application/json': {
                  schema: { $ref: '#/components/schemas/Project' },
                },
              },
            },
            '400': { $ref: '#/components/responses/BadRequest' },
            '401': { $ref: '#/components/responses/Unauthorized' },
            '500': { $ref: '#/components/responses/ServerError' },
          },
        },
      },
    },
    components: {
      schemas: {
        Project: {
          type: 'object',
          required: ['id', 'name', 'created_at'],
          properties: {
            id: { type: 'string', format: 'uuid' },
            name: { type: 'string', minLength: 1, maxLength: 255 },
            description: { type: 'string', nullable: true },
            metadata: { type: 'object' },
            created_at: { type: 'string', format: 'date-time' },
            updated_at: { type: 'string', format: 'date-time' },
          },
        },
        CreateProjectRequest: {
          type: 'object',
          required: ['name'],
          properties: {
            name: { type: 'string', minLength: 1, maxLength: 255 },
            description: { type: 'string', maxLength: 1000 },
            metadata: { type: 'object' },
          },
        },
        ErrorResponse: {
          type: 'object',
          required: ['code', 'message'],
          properties: {
            code: { type: 'string' },
            message: { type: 'string' },
            details: { type: 'object' },
          },
        },
      },
      securitySchemes: {
        Bearer: {
          type: 'http',
          scheme: 'bearer',
          bearerFormat: 'JWT',
          description: 'WorkOS/AuthKit JWT token',
        },
      },
      responses: {
        BadRequest: {
          description: 'Bad Request',
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/ErrorResponse' },
            },
          },
        },
        Unauthorized: {
          description: 'Unauthorized',
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/ErrorResponse' },
            },
          },
        },
        ServerError: {
          description: 'Internal Server Error',
          content: {
            'application/json': {
              schema: { $ref: '#/components/schemas/ErrorResponse' },
            },
          },
        },
      },
    },
  }
}

// Write to file
const spec = generateOpenAPI()
const yamlContent = yaml.stringify(spec)
fs.writeFileSync(
  path.join(__dirname, '../fumadocs/public/openapi.yaml'),
  yamlContent
)

console.log('✅ OpenAPI spec generated')
```

### 6. Run Generation

```bash
npm run generate:openapi
```

### 7. Validate OpenAPI Spec

```bash
# Install validator
npm install -D @redocly/cli

# Validate
redocly lint public/openapi.yaml
```

---

## Endpoint Documentation Template

For each endpoint, document:

```markdown
## Create Project

Creates a new project with the given name and description.

### Request

```http
POST /api/v1/projects
Authorization: Bearer <token>
Content-Type: application/json

{
  "name": "My Project",
  "description": "A project for tracking requirements",
  "metadata": {
    "team": "engineering",
    "priority": "high"
  }
}
```

### Response

```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "name": "My Project",
  "description": "A project for tracking requirements",
  "metadata": {
    "team": "engineering",
    "priority": "high"
  },
  "created_at": "2025-12-02T10:00:00Z",
  "updated_at": "2025-12-02T10:00:00Z"
}
```

### Errors

- `400 Bad Request` - Invalid request parameters
- `401 Unauthorized` - Missing or invalid authentication
- `500 Internal Server Error` - Server error
```

---

## Next Steps

1. Add swagger comments to all handlers
2. Generate OpenAPI spec
3. Validate spec
4. Integrate with Swagger UI
5. Integrate with ReDoc

---

**Status:** Ready for Phase 3  
**Estimated Time:** 4-6 hours

