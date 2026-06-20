# Documentation Standards & Best Practices

## Code Documentation Standards

### Go Documentation

**Package-level documentation:**

```go
// Package handlers provides HTTP request handlers for the TraceRTM API.
//
// This package implements all REST endpoints for managing projects, items,
// links, and agents. Each handler follows the Echo framework conventions
// and includes proper error handling and validation.
//
// Example:
//
//	handler := NewProjectHandler(db, cache, publisher, broadcaster, auth)
//	e.GET("/projects", handler.ListProjects)
//	e.POST("/projects", handler.CreateProject)
package handlers
```

**Function documentation:**

```go
// CreateProject creates a new project with the given parameters.
//
// This function validates the request, creates a new project in the database,
// publishes a ProjectCreated event, and broadcasts the update to connected
// clients via WebSocket.
//
// Parameters:
//   - c: Echo context containing the HTTP request and response
//
// Returns:
//   - error: nil on success, or an error if the operation fails
//
// Errors:
//   - ErrInvalidRequest: if the request body is invalid
//   - ErrUnauthorized: if the user is not authenticated
//   - ErrDatabaseError: if the database operation fails
//
// Example:
//
//	e.POST("/projects", handler.CreateProject)
//	// POST /projects
//	// Content-Type: application/json
//	// Authorization: Bearer <token>
//	//
//	// {
//	//   "name": "My Project",
//	//   "description": "A project for tracking requirements"
//	// }
func (h *ProjectHandler) CreateProject(c echo.Context) error {
    // Implementation
}
```

**Type documentation:**

```go
// Project represents a project in the TraceRTM system.
//
// A project is the top-level organizational unit that contains items,
// links, and agents. Each project belongs to a single user and can have
// multiple collaborators.
//
// Fields:
//   - ID: Unique identifier (UUID v4)
//   - Name: Project name (1-255 characters)
//   - Description: Optional project description
//   - Metadata: Optional key-value metadata
//   - CreatedAt: Creation timestamp
//   - UpdatedAt: Last update timestamp
//   - CreatedBy: User ID of the creator
//   - UpdatedBy: User ID of the last updater
type Project struct {
    ID          string                 `json:"id" db:"id"`
    Name        string                 `json:"name" db:"name"`
    Description string                 `json:"description" db:"description"`
    Metadata    map[string]interface{} `json:"metadata" db:"metadata"`
    CreatedAt   time.Time              `json:"created_at" db:"created_at"`
    UpdatedAt   time.Time              `json:"updated_at" db:"updated_at"`
    CreatedBy   string                 `json:"created_by" db:"created_by"`
    UpdatedBy   string                 `json:"updated_by" db:"updated_by"`
}
```

**Interface documentation:**

```go
// AuthProvider defines the interface for authentication providers.
//
// Implementations of this interface handle user authentication, token
// validation, and user profile management. Currently, only AuthKit
// (WorkOS) is supported.
//
// Security Note:
// - All tokens must be validated before use
// - User IDs must be verified against the auth provider
// - Tokens should be cached with appropriate TTL
type AuthProvider interface {
    // ValidateToken validates a JWT token and returns the user.
    //
    // Parameters:
    //   - ctx: Context for cancellation
    //   - token: JWT token string
    //
    // Returns:
    //   - *User: User information if valid
    //   - error: ErrInvalidToken if invalid, or other errors
    ValidateToken(ctx context.Context, token string) (*User, error)

    // GetUser retrieves user information by ID.
    //
    // Parameters:
    //   - ctx: Context for cancellation
    //   - userID: User ID
    //
    // Returns:
    //   - *User: User information
    //   - error: ErrUserNotFound if not found, or other errors
    GetUser(ctx context.Context, userID string) (*User, error)

    // UpdateUser updates user information.
    //
    // Parameters:
    //   - ctx: Context for cancellation
    //   - userID: User ID
    //   - updates: User updates
    //
    // Returns:
    //   - *User: Updated user information
    //   - error: ErrUserNotFound if not found, or other errors
    UpdateUser(ctx context.Context, userID string, updates *UserUpdate) (*User, error)
}
```

### TypeScript/JavaScript Documentation

**JSDoc format:**

```typescript
/**
 * Creates a new project with the given parameters.
 *
 * This function validates the request, creates a new project in the database,
 * publishes a ProjectCreated event, and broadcasts the update to connected
 * clients via WebSocket.
 *
 * @param {CreateProjectRequest} request - The project creation request
 * @param {string} request.name - Project name (required, 1-255 chars)
 * @param {string} [request.description] - Project description (optional)
 * @param {Record<string, unknown>} [request.metadata] - Project metadata
 * @param {string} userId - The ID of the user creating the project
 *
 * @returns {Promise<Project>} The created project
 *
 * @throws {ValidationError} If the request is invalid
 * @throws {UnauthorizedError} If the user is not authenticated
 * @throws {DatabaseError} If the database operation fails
 *
 * @example
 * const project = await createProject({
 *   name: 'My Project',
 *   description: 'A project for tracking requirements',
 *   metadata: { team: 'engineering' }
 * }, userId)
 */
export async function createProject(
  request: CreateProjectRequest,
  userId: string
): Promise<Project> {
  // Implementation
}
```

**Interface documentation:**

```typescript
/**
 * Represents a project in the TraceRTM system.
 *
 * A project is the top-level organizational unit that contains items,
 * links, and agents. Each project belongs to a single user and can have
 * multiple collaborators.
 *
 * @interface Project
 * @property {string} id - Unique identifier (UUID v4)
 * @property {string} name - Project name (1-255 characters)
 * @property {string} [description] - Optional project description
 * @property {Record<string, unknown>} [metadata] - Optional metadata
 * @property {Date} createdAt - Creation timestamp
 * @property {Date} updatedAt - Last update timestamp
 * @property {string} createdBy - User ID of the creator
 * @property {string} updatedBy - User ID of the last updater
 */
export interface Project {
  id: string
  name: string
  description?: string
  metadata?: Record<string, unknown>
  createdAt: Date
  updatedAt: Date
  createdBy: string
  updatedBy: string
}
```

**React Component documentation:**

```typescript
/**
 * ProjectCard displays a project summary with actions.
 *
 * This component renders a card showing project information including
 * name, description, item count, and action buttons for editing and
 * deleting the project.
 *
 * @component
 * @param {ProjectCardProps} props - Component props
 * @param {Project} props.project - The project to display
 * @param {Function} props.onEdit - Callback when edit button is clicked
 * @param {Function} props.onDelete - Callback when delete button is clicked
 * @param {boolean} [props.isLoading] - Whether the card is in loading state
 *
 * @returns {React.ReactElement} The rendered project card
 *
 * @example
 * <ProjectCard
 *   project={project}
 *   onEdit={handleEdit}
 *   onDelete={handleDelete}
 *   isLoading={false}
 * />
 */
export function ProjectCard({
  project,
  onEdit,
  onDelete,
  isLoading = false,
}: ProjectCardProps): React.ReactElement {
  // Implementation
}
```

---

## MDX Documentation Standards

### Page Structure

```mdx
---
title: "Getting Started"
description: "Get up and running with TraceRTM in 5 minutes"
---

# Getting Started

Brief introduction paragraph explaining what this page covers.

## Prerequisites

- Node.js 18+
- PostgreSQL 14+
- Docker (optional)

## Installation

Step-by-step installation instructions.

### Using Docker

```bash
docker run -d tracertm:latest
```

### Manual Setup

```bash
git clone https://github.com/tracertm/tracertm.git
cd tracertm
npm install
npm run dev
```

## Configuration

Explain configuration options.

## Next Steps

- [User Guide](/docs/user-guide)
- [API Reference](/docs/api-reference)
- [Architecture](/docs/architecture)
```

### Code Examples

```mdx
## Creating a Project

Here's how to create a new project:

<Tabs items={["cURL", "JavaScript", "Python", "Go"]}>
  <Tabs.Tab>
    ```bash
    curl -X POST http://localhost:8080/api/v1/projects \
      -H "Authorization: Bearer $TOKEN" \
      -H "Content-Type: application/json" \
      -d '{
        "name": "My Project",
        "description": "A project for tracking requirements"
      }'
    ```
  </Tabs.Tab>

  <Tabs.Tab>
    ```typescript
    const project = await client.projects.create({
      name: 'My Project',
      description: 'A project for tracking requirements'
    })
    ```
  </Tabs.Tab>

  <Tabs.Tab>
    ```python
    project = client.projects.create(
      name='My Project',
      description='A project for tracking requirements'
    )
    ```
  </Tabs.Tab>

  <Tabs.Tab>
    ```go
    project, err := client.Projects.Create(ctx, &CreateProjectRequest{
      Name: "My Project",
      Description: "A project for tracking requirements",
    })
    ```
  </Tabs.Tab>
</Tabs>
```

---

## Docstring Checklist

- [ ] **Summary**: One-line description of purpose
- [ ] **Description**: Detailed explanation of functionality
- [ ] **Parameters**: All parameters documented with types and descriptions
- [ ] **Returns**: Return type and description
- [ ] **Errors**: All possible errors documented
- [ ] **Examples**: At least one usage example
- [ ] **Notes**: Any important caveats or considerations
- [ ] **See Also**: Links to related functions/docs

---

## Documentation Review Checklist

- [ ] All public functions documented
- [ ] All public types documented
- [ ] All parameters documented
- [ ] All return values documented
- [ ] All errors documented
- [ ] Examples provided
- [ ] Links to related docs
- [ ] No broken links
- [ ] Consistent formatting
- [ ] Accurate and up-to-date

---

**Version:** 1.0  
**Last Updated:** December 2, 2025

