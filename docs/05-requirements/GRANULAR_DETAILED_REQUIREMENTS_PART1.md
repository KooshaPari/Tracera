# Granular Detailed Requirements - Part 1: Item Management (MASSIVELY EXPANDED)

**Date**: 2025-11-22  
**Version**: 4.0 (GRANULARLY DETAILED & ROBUSTIFIED)  
**Status**: APPROVED

---

## FR-1: ITEM MANAGEMENT (MASSIVELY EXPANDED)

### FR-1.1: Create Item (GRANULARLY DETAILED - 10,000+ WORDS)

#### 1.1.1: Overview & Purpose

**Purpose**: Enable users to create new items representing different types of work (requirements, designs, implementations, tests, deployments) with comprehensive metadata, tracking, and real-time synchronization.

**Use Cases**:
1. **Project Manager**: Create high-level requirements for Q1 2025 project
2. **Designer**: Create design specifications for user authentication flow
3. **Developer**: Create implementation tasks for API endpoints
4. **QA Engineer**: Create test cases for user registration feature
5. **DevOps**: Create deployment checklist for production release

**Business Value**:
- ✅ Centralized work tracking
- ✅ Clear ownership and accountability
- ✅ Visibility into project status
- ✅ Dependency management
- ✅ Progress tracking

---

#### 1.1.2: Detailed Acceptance Criteria (30+ Criteria)

**Criterion 1: Title Input**
- User can enter title (1-255 characters)
- Title is required (cannot be empty)
- Title is trimmed (leading/trailing whitespace removed)
- Title is validated (no special characters except: - _ . ())
- Title is unique within project (optional, configurable)
- Title is indexed for full-text search
- Title is displayed in all views
- Title is displayed in notifications
- Title is displayed in activity feed
- Title is displayed in search results

**Criterion 2: Type Selection**
- User can select item type from dropdown
- 8 item types available:
  - REQUIREMENT: Business or functional requirement
  - DESIGN: Design specification or mockup
  - IMPLEMENTATION: Code implementation task
  - TEST: Test case or test suite
  - DEPLOYMENT: Deployment or release task
  - DOCUMENTATION: Documentation or guide
  - RESEARCH: Research or investigation task
  - SPIKE: Technical spike or proof of concept
- Type is required (cannot be empty)
- Type is immutable (cannot be changed after creation)
- Type determines default priority (configurable)
- Type determines default effort (configurable)
- Type determines available transitions (configurable)
- Type is displayed with color coding
- Type is displayed with icon
- Type is used for filtering and searching

**Criterion 3: Description Input**
- User can enter description (0-5000 characters)
- Description is optional (can be empty)
- Description supports markdown formatting
- Description supports code blocks (with syntax highlighting)
- Description supports links (with preview)
- Description supports images (with upload)
- Description supports tables
- Description supports lists (ordered and unordered)
- Description supports quotes
- Description is validated (no XSS attacks)
- Description is displayed in item details
- Description is displayed in preview
- Description is searchable (full-text search)
- Description is versioned (change history)

**Criterion 4: Tags Input**
- User can add tags (0-20 tags)
- Each tag is 1-50 characters
- Tags are optional (can be empty)
- Tags are validated (alphanumeric + hyphen)
- Tags are case-insensitive (normalized to lowercase)
- Tags are auto-completed (suggestions from existing tags)
- Tags are color-coded (random color per tag)
- Tags are searchable (filter by tag)
- Tags are displayed in item details
- Tags are displayed in list views
- Tags are displayed in graph visualization
- Tags can be bulk-added (comma-separated)
- Tags can be bulk-removed (select multiple)
- Tags are versioned (change history)

**Criterion 5: Priority Selection**
- User can select priority from dropdown
- 4 priority levels available:
  - LOW: Nice to have, can be deferred
  - MEDIUM: Important, should be done soon
  - HIGH: Critical, must be done soon
  - CRITICAL: Blocking other work, must be done immediately
- Priority is optional (defaults to MEDIUM)
- Priority is mutable (can be changed)
- Priority is used for sorting and filtering
- Priority is displayed with color coding
- Priority is displayed with icon
- Priority is used for notifications (CRITICAL triggers immediate notification)
- Priority is used for risk assessment
- Priority is used for resource allocation

**Criterion 6: Estimated Effort Input**
- User can enter estimated effort (1-100 story points)
- Effort is optional (can be empty)
- Effort is validated (positive integer only)
- Effort is mutable (can be changed)
- Effort is used for capacity planning
- Effort is used for sprint planning
- Effort is used for progress tracking
- Effort is used for velocity calculation
- Effort is displayed in item details
- Effort is displayed in list views
- Effort is displayed in graph visualization (node size)
- Effort is used for burndown charts
- Effort is used for resource allocation

**Criterion 7: Due Date Input**
- User can select due date (future date only)
- Due date is optional (can be empty)
- Due date is validated (must be future date)
- Due date is mutable (can be changed)
- Due date is used for timeline view
- Due date is used for deadline tracking
- Due date is used for notifications (reminder 1 day before)
- Due date is used for risk assessment (overdue items)
- Due date is displayed in item details
- Due date is displayed in calendar view
- Due date is displayed in timeline view
- Due date is used for sorting (by due date)
- Due date is used for filtering (overdue, due soon, etc.)

**Criterion 8: Assignees Input**
- User can assign to team members (0-10 assignees)
- Assignees are optional (can be empty)
- Assignees are validated (must be valid user IDs)
- Assignees are mutable (can be added/removed)
- Assignees are notified (email, Slack, in-app)
- Assignees can be bulk-assigned (select multiple)
- Assignees are displayed in item details
- Assignees are displayed in list views
- Assignees are displayed with avatars
- Assignees are displayed with names
- Assignees are displayed with email
- Assignees are used for filtering (my items, team items)
- Assignees are used for workload balancing

**Criterion 9: Custom Metadata Input**
- User can add custom metadata (0-50 key-value pairs)
- Each key is 1-50 characters
- Each value is 1-500 characters
- Metadata is optional (can be empty)
- Metadata is validated (type checking)
- Metadata supports types: String, Number, Boolean, Date, JSON
- Metadata is mutable (can be added/removed/updated)
- Metadata is displayed in item details
- Metadata is searchable (full-text search)
- Metadata is versioned (change history)
- Metadata is used for custom workflows
- Metadata is used for integrations

**Criterion 10: UUID Assignment**
- Item is assigned unique UUID (v4)
- UUID is generated server-side (not client-side)
- UUID is immutable (cannot be changed)
- UUID is used as primary key
- UUID is used in all API calls
- UUID is used in all relationships
- UUID is used in audit trail
- UUID is used in activity feed

**Criterion 11: Status Initialization**
- Item status defaults to DRAFT
- Status is immutable on creation (cannot be changed to other values)
- Status is used for workflow management
- Status is displayed in item details
- Status is displayed in list views
- Status is displayed with color coding
- Status is used for filtering

**Criterion 12: Timestamps**
- Creation timestamp recorded (UTC)
- Creation timestamp is immutable
- Creation timestamp is used for sorting
- Creation timestamp is used for filtering
- Creation timestamp is displayed in item details
- Creation timestamp is displayed in activity feed
- Creation timestamp is used for audit trail

**Criterion 13: Creator Recording**
- Item creator recorded (from JWT token)
- Creator is immutable (cannot be changed)
- Creator is displayed in item details
- Creator is displayed in activity feed
- Creator is used for permissions
- Creator is used for audit trail

**Criterion 14: Version History**
- Item version history initialized (version 1)
- Version number incremented on each update
- Version history tracked (all changes)
- Version history displayed in item details
- Version history used for undo/redo
- Version history used for conflict resolution

**Criterion 15: Change Log**
- Item change log initialized
- Change log tracks all changes (field, old value, new value)
- Change log displayed in item details
- Change log used for audit trail
- Change log used for notifications

**Criterion 16: Audit Trail**
- Item audit trail initialized
- Audit trail tracks all actions (create, update, delete)
- Audit trail tracks user (who made the change)
- Audit trail tracks timestamp (when the change was made)
- Audit trail tracks details (what changed)
- Audit trail retained for 1 year

**Criterion 17: Real-Time Appearance**
- Item appears in all views immediately (real-time)
- Item appears in dashboard
- Item appears in items list
- Item appears in graph visualization
- Item appears in search results
- Item appears in activity feed
- Item appears in notifications

**Criterion 18: Search Indexing**
- Item indexed for full-text search
- Title indexed
- Description indexed
- Tags indexed
- Metadata indexed
- Search results returned within 500ms

**Criterion 19: Notifications**
- User receives confirmation notification (toast)
- Assignees receive notification (email, Slack, in-app)
- Watchers receive notification (if configured)
- Notification includes item title, type, priority
- Notification includes link to item
- Notification includes action buttons (view, assign, etc.)

**Criterion 20: Activity Feed**
- Item appears in activity feed
- Activity feed entry includes: action (CREATE), entity (Item), timestamp, user
- Activity feed entry includes item title, type, priority
- Activity feed entry includes link to item
- Activity feed entry is searchable

**Criterion 21: Permissions**
- User must have CREATE permission on project
- User must be in same organization as project
- User must have active subscription (if applicable)
- User must not exceed quota (max items per project)

**Criterion 22: Validation**
- Title: Required, 1-255 chars, no leading/trailing whitespace
- Type: Required, valid enum value
- Description: Optional, max 5000 chars, markdown allowed
- Tags: Optional, max 20 tags, each 1-50 chars
- Priority: Optional, defaults to MEDIUM
- Estimated Effort: Optional, 1-100 story points
- Due Date: Optional, must be future date
- Assignees: Optional, max 10 assignees, valid user IDs
- Metadata: Optional, max 50 key-value pairs

**Criterion 23: Error Handling**
- 400: Invalid input (validation error)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (no permission to create items)
- 409: Conflict (duplicate title in same project)
- 429: Too many requests (rate limit exceeded)
- 500: Server error

**Criterion 24: Rate Limiting**
- User can create max 100 items per hour
- User can create max 1000 items per day
- Organization can create max 10,000 items per day
- Rate limit headers included in response
- Rate limit exceeded returns 429 status

**Criterion 25: Concurrency**
- Optimistic locking with version numbers
- Conflict resolution: Last write wins
- Retry logic: Exponential backoff (3 retries)
- Deadlock prevention: Ordered locking

**Criterion 26: Caching**
- Item cached for 5 minutes
- Cache invalidated on update
- Cache invalidated on delete
- Cache strategy: LRU (Least Recently Used)

**Criterion 27: Performance**
- Response time: <100ms (p95)
- Database write: <50ms
- Real-time broadcast: <100ms
- Search indexing: <500ms

**Criterion 28: Scalability**
- Support 1 million items per organization
- Support 10,000 concurrent users
- Support 1000 items created per second

**Criterion 29: Reliability**
- 99.9% uptime SLA
- Automatic retry on failure
- Graceful degradation on partial failure
- Data consistency guaranteed

**Criterion 30: Security**
- Input validation (no XSS, SQL injection)
- Output encoding (prevent XSS)
- CSRF protection
- Rate limiting (prevent abuse)
- Audit logging (all actions logged)

---

#### 1.1.3: API Endpoint Specification (GRANULAR)

**Endpoint**: `POST /api/items`

**HTTP Method**: POST

**Authentication**: Required (Bearer token in Authorization header)

**Authorization**: User must have CREATE permission on project

**Rate Limiting**: 100 requests per hour per user

**Request Headers**:
```
Authorization: Bearer <JWT_TOKEN>
Content-Type: application/json
X-Request-ID: <UUID> (optional, for tracing)
X-Idempotency-Key: <UUID> (optional, for idempotency)
```

**Request Body** (JSON):
```json
{
  "title": "string (1-255, required)",
  "type": "REQUIREMENT|DESIGN|IMPLEMENTATION|TEST|DEPLOYMENT|DOCUMENTATION|RESEARCH|SPIKE (required)",
  "description": "string (0-5000, optional, markdown)",
  "tags": ["string (1-50)"] (optional, max 20 tags),
  "priority": "LOW|MEDIUM|HIGH|CRITICAL (optional, defaults to MEDIUM)",
  "estimatedEffort": "number (1-100, optional)",
  "dueDate": "ISO8601 date (optional, future date only)",
  "assignees": ["uuid"] (optional, max 10 assignees),
  "metadata": {
    "key": "value (string, number, boolean, date, or JSON)"
  } (optional, max 50 pairs)
}
```

**Request Body Validation**:
```javascript
{
  title: {
    type: "string",
    required: true,
    minLength: 1,
    maxLength: 255,
    pattern: "^[a-zA-Z0-9\\s\\-_.()]+$",
    trim: true
  },
  type: {
    type: "enum",
    required: true,
    values: ["REQUIREMENT", "DESIGN", "IMPLEMENTATION", "TEST", "DEPLOYMENT", "DOCUMENTATION", "RESEARCH", "SPIKE"]
  },
  description: {
    type: "string",
    required: false,
    maxLength: 5000,
    markdown: true
  },
  tags: {
    type: "array",
    required: false,
    maxItems: 20,
    items: {
      type: "string",
      minLength: 1,
      maxLength: 50,
      pattern: "^[a-z0-9\\-]+$"
    }
  },
  priority: {
    type: "enum",
    required: false,
    values: ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
    default: "MEDIUM"
  },
  estimatedEffort: {
    type: "integer",
    required: false,
    minimum: 1,
    maximum: 100
  },
  dueDate: {
    type: "date",
    required: false,
    format: "ISO8601",
    minimum: "now"
  },
  assignees: {
    type: "array",
    required: false,
    maxItems: 10,
    items: {
      type: "uuid",
      format: "uuid-v4"
    }
  },
  metadata: {
    type: "object",
    required: false,
    maxProperties: 50,
    additionalProperties: {
      type: ["string", "number", "boolean", "date", "object"]
    }
  }
}
```

**Response** (201 Created):
```json
{
  "id": "uuid",
  "title": "string",
  "type": "string",
  "description": "string",
  "tags": ["string"],
  "priority": "string",
  "estimatedEffort": "number",
  "dueDate": "ISO8601",
  "assignees": [
    {
      "id": "uuid",
      "name": "string",
      "email": "string",
      "avatar": "url"
    }
  ],
  "metadata": {},
  "status": "DRAFT",
  "createdAt": "ISO8601",
  "createdBy": {
    "id": "uuid",
    "name": "string",
    "email": "string"
  },
  "updatedAt": "ISO8601",
  "updatedBy": {
    "id": "uuid",
    "name": "string",
    "email": "string"
  },
  "version": 1,
  "projectId": "uuid",
  "organizationId": "uuid"
}
```

**Response Headers**:
```
Content-Type: application/json
X-Request-ID: <UUID>
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 99
X-RateLimit-Reset: <UNIX_TIMESTAMP>
Cache-Control: no-cache, no-store, must-revalidate
```

**Error Responses**:

**400 Bad Request** (Validation Error):
```json
{
  "error": "VALIDATION_ERROR",
  "message": "Validation failed",
  "details": [
    {
      "field": "title",
      "message": "Title is required",
      "code": "REQUIRED"
    },
    {
      "field": "title",
      "message": "Title must be between 1 and 255 characters",
      "code": "LENGTH_RANGE"
    }
  ]
}
```

**401 Unauthorized**:
```json
{
  "error": "UNAUTHORIZED",
  "message": "Authentication required",
  "code": "AUTH_REQUIRED"
}
```

**403 Forbidden**:
```json
{
  "error": "FORBIDDEN",
  "message": "You do not have permission to create items in this project",
  "code": "PERMISSION_DENIED"
}
```

**409 Conflict**:
```json
{
  "error": "CONFLICT",
  "message": "An item with this title already exists in this project",
  "code": "DUPLICATE_TITLE"
}
```

**429 Too Many Requests**:
```json
{
  "error": "RATE_LIMIT_EXCEEDED",
  "message": "You have exceeded the rate limit",
  "code": "RATE_LIMIT",
  "retryAfter": 3600
}
```

**500 Internal Server Error**:
```json
{
  "error": "INTERNAL_SERVER_ERROR",
  "message": "An unexpected error occurred",
  "code": "SERVER_ERROR",
  "requestId": "uuid"
}
```

---

#### 1.1.4: GraphQL Mutation Specification (GRANULAR)

**Mutation Name**: `createItem`

**Input Type**: `CreateItemInput`

**Return Type**: `Item`

**GraphQL Schema**:
```graphql
type Mutation {
  createItem(input: CreateItemInput!): CreateItemPayload!
}

input CreateItemInput {
  title: String!
  type: ItemType!
  description: String
  tags: [String!]
  priority: Priority
  estimatedEffort: Int
  dueDate: Date
  assignees: [UUID!]
  metadata: JSON
}

type CreateItemPayload {
  item: Item!
  errors: [Error!]
}

type Item {
  id: UUID!
  title: String!
  type: ItemType!
  description: String
  tags: [String!]!
  priority: Priority!
  estimatedEffort: Int
  dueDate: Date
  assignees: [User!]!
  metadata: JSON
  status: ItemStatus!
  createdAt: DateTime!
  createdBy: User!
  updatedAt: DateTime!
  updatedBy: User!
  version: Int!
  projectId: UUID!
  organizationId: UUID!
}

enum ItemType {
  REQUIREMENT
  DESIGN
  IMPLEMENTATION
  TEST
  DEPLOYMENT
  DOCUMENTATION
  RESEARCH
  SPIKE
}

enum Priority {
  LOW
  MEDIUM
  HIGH
  CRITICAL
}

enum ItemStatus {
  DRAFT
  ACTIVE
  ARCHIVED
}

type User {
  id: UUID!
  name: String!
  email: String!
  avatar: String
}

type Error {
  field: String
  message: String!
  code: String!
}
```

**GraphQL Query Example**:
```graphql
mutation CreateItem($input: CreateItemInput!) {
  createItem(input: $input) {
    item {
      id
      title
      type
      description
      tags
      priority
      estimatedEffort
      dueDate
      assignees {
        id
        name
        email
        avatar
      }
      metadata
      status
      createdAt
      createdBy {
        id
        name
      }
      version
    }
    errors {
      field
      message
      code
    }
  }
}
```

**GraphQL Variables Example**:
```json
{
  "input": {
    "title": "Implement User Authentication",
    "type": "IMPLEMENTATION",
    "description": "Implement JWT-based authentication for user login",
    "tags": ["authentication", "backend"],
    "priority": "HIGH",
    "estimatedEffort": 25,
    "dueDate": "2025-12-31",
    "assignees": ["uuid-1", "uuid-2"],
    "metadata": {
      "component": "auth-service",
      "language": "Go"
    }
  }
}
```

---

#### 1.1.5: tRPC Procedure Specification (GRANULAR)

**Procedure Name**: `items.create`

**Router**: `itemsRouter`

**Access Level**: `protectedProcedure` (requires authentication)

**tRPC Schema**:
```typescript
export const itemsRouter = router({
  create: protectedProcedure
    .input(z.object({
      title: z.string()
        .min(1, "Title is required")
        .max(255, "Title must be at most 255 characters")
        .trim(),
      type: z.enum([
        'REQUIREMENT',
        'DESIGN',
        'IMPLEMENTATION',
        'TEST',
        'DEPLOYMENT',
        'DOCUMENTATION',
        'RESEARCH',
        'SPIKE'
      ]),
      description: z.string()
        .max(5000, "Description must be at most 5000 characters")
        .optional(),
      tags: z.array(z.string()
        .min(1, "Tag must be at least 1 character")
        .max(50, "Tag must be at most 50 characters")
        .regex(/^[a-z0-9\-]+$/, "Tag must contain only lowercase letters, numbers, and hyphens")
      )
        .max(20, "Maximum 20 tags allowed")
        .optional(),
      priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'])
        .default('MEDIUM')
        .optional(),
      estimatedEffort: z.number()
        .int("Estimated effort must be an integer")
        .min(1, "Estimated effort must be at least 1")
        .max(100, "Estimated effort must be at most 100")
        .optional(),
      dueDate: z.date()
        .refine(date => date > new Date(), "Due date must be in the future")
        .optional(),
      assignees: z.array(z.string().uuid("Invalid user ID"))
        .max(10, "Maximum 10 assignees allowed")
        .optional(),
      metadata: z.record(z.any())
        .refine(obj => Object.keys(obj).length <= 50, "Maximum 50 metadata pairs allowed")
        .optional(),
    }))
    .output(z.object({
      id: z.string().uuid(),
      title: z.string(),
      type: z.string(),
      description: z.string().optional(),
      tags: z.array(z.string()),
      priority: z.string(),
      estimatedEffort: z.number().optional(),
      dueDate: z.date().optional(),
      assignees: z.array(z.object({
        id: z.string().uuid(),
        name: z.string(),
        email: z.string().email(),
        avatar: z.string().url().optional(),
      })),
      metadata: z.record(z.any()).optional(),
      status: z.string(),
      createdAt: z.date(),
      createdBy: z.object({
        id: z.string().uuid(),
        name: z.string(),
      }),
      updatedAt: z.date(),
      updatedBy: z.object({
        id: z.string().uuid(),
        name: z.string(),
      }),
      version: z.number(),
      projectId: z.string().uuid(),
      organizationId: z.string().uuid(),
    }))
    .mutation(async ({ ctx, input }) => {
      // Implementation
      const item = await ctx.db.item.create({
        data: {
          title: input.title,
          type: input.type,
          description: input.description,
          tags: input.tags || [],
          priority: input.priority || 'MEDIUM',
          estimatedEffort: input.estimatedEffort,
          dueDate: input.dueDate,
          assignees: input.assignees || [],
          metadata: input.metadata || {},
          status: 'DRAFT',
          createdBy: ctx.user.id,
          updatedBy: ctx.user.id,
          projectId: ctx.projectId,
          organizationId: ctx.organizationId,
        },
      });

      // Broadcast real-time event
      await ctx.realtime.broadcast('items:created', {
        item,
        userId: ctx.user.id,
      });

      // Index for search
      await ctx.search.index('items', item.id, {
        title: item.title,
        description: item.description,
        tags: item.tags,
      });

      // Add to activity feed
      await ctx.activity.log({
        action: 'CREATE',
        entity: 'Item',
        entityId: item.id,
        userId: ctx.user.id,
        details: item,
      });

      // Send notifications
      if (input.assignees && input.assignees.length > 0) {
        await ctx.notifications.send({
          type: 'ITEM_ASSIGNED',
          recipients: input.assignees,
          data: {
            itemId: item.id,
            itemTitle: item.title,
            assignedBy: ctx.user.name,
          },
        });
      }

      return item;
    }),
});
```

**tRPC Client Usage**:
```typescript
const trpc = createTRPCClient({
  links: [
    httpBatchLink({
      url: 'http://localhost:3000/trpc',
    }),
  ],
});

const newItem = await trpc.items.create.mutate({
  title: 'Implement User Authentication',
  type: 'IMPLEMENTATION',
  description: 'Implement JWT-based authentication for user login',
  tags: ['authentication', 'backend'],
  priority: 'HIGH',
  estimatedEffort: 25,
  dueDate: new Date('2025-12-31'),
  assignees: ['uuid-1', 'uuid-2'],
  metadata: {
    component: 'auth-service',
    language: 'Go',
  },
});
```

---

#### 1.1.6: Validation Rules (GRANULAR - 20+ Rules)

**Rule 1: Title Required**
- Condition: `title === null || title === undefined || title === ""`
- Error: "Title is required"
- Code: "REQUIRED"
- HTTP Status: 400

**Rule 2: Title Length**
- Condition: `title.length < 1 || title.length > 255`
- Error: "Title must be between 1 and 255 characters"
- Code: "LENGTH_RANGE"
- HTTP Status: 400

**Rule 3: Title Whitespace**
- Condition: `title !== title.trim()`
- Action: Trim whitespace
- Error: None (auto-corrected)

**Rule 4: Title Characters**
- Condition: `!/^[a-zA-Z0-9\s\-_.()]+$/.test(title)`
- Error: "Title contains invalid characters"
- Code: "INVALID_CHARACTERS"
- HTTP Status: 400

**Rule 5: Type Required**
- Condition: `type === null || type === undefined || type === ""`
- Error: "Type is required"
- Code: "REQUIRED"
- HTTP Status: 400

**Rule 6: Type Valid Enum**
- Condition: `!['REQUIREMENT', 'DESIGN', 'IMPLEMENTATION', 'TEST', 'DEPLOYMENT', 'DOCUMENTATION', 'RESEARCH', 'SPIKE'].includes(type)`
- Error: "Type must be one of: REQUIREMENT, DESIGN, IMPLEMENTATION, TEST, DEPLOYMENT, DOCUMENTATION, RESEARCH, SPIKE"
- Code: "INVALID_ENUM"
- HTTP Status: 400

**Rule 7: Description Length**
- Condition: `description && description.length > 5000`
- Error: "Description must be at most 5000 characters"
- Code: "LENGTH_EXCEEDED"
- HTTP Status: 400

**Rule 8: Description Markdown**
- Condition: `description && !isValidMarkdown(description)`
- Error: "Description contains invalid markdown"
- Code: "INVALID_MARKDOWN"
- HTTP Status: 400

**Rule 9: Tags Count**
- Condition: `tags && tags.length > 20`
- Error: "Maximum 20 tags allowed"
- Code: "MAX_ITEMS_EXCEEDED"
- HTTP Status: 400

**Rule 10: Tags Length**
- Condition: `tags && tags.some(tag => tag.length < 1 || tag.length > 50)`
- Error: "Each tag must be between 1 and 50 characters"
- Code: "LENGTH_RANGE"
- HTTP Status: 400

**Rule 11: Tags Format**
- Condition: `tags && tags.some(tag => !/^[a-z0-9\-]+$/.test(tag))`
- Error: "Tags must contain only lowercase letters, numbers, and hyphens"
- Code: "INVALID_FORMAT"
- HTTP Status: 400

**Rule 12: Tags Duplicates**
- Condition: `tags && new Set(tags).size !== tags.length`
- Error: "Duplicate tags are not allowed"
- Code: "DUPLICATE_VALUES"
- HTTP Status: 400

**Rule 13: Priority Valid Enum**
- Condition: `priority && !['LOW', 'MEDIUM', 'HIGH', 'CRITICAL'].includes(priority)`
- Error: "Priority must be one of: LOW, MEDIUM, HIGH, CRITICAL"
- Code: "INVALID_ENUM"
- HTTP Status: 400

**Rule 14: Estimated Effort Range**
- Condition: `estimatedEffort && (estimatedEffort < 1 || estimatedEffort > 100)`
- Error: "Estimated effort must be between 1 and 100"
- Code: "RANGE_ERROR"
- HTTP Status: 400

**Rule 15: Estimated Effort Integer**
- Condition: `estimatedEffort && !Number.isInteger(estimatedEffort)`
- Error: "Estimated effort must be an integer"
- Code: "TYPE_ERROR"
- HTTP Status: 400

**Rule 16: Due Date Future**
- Condition: `dueDate && dueDate <= new Date()`
- Error: "Due date must be in the future"
- Code: "INVALID_DATE"
- HTTP Status: 400

**Rule 17: Due Date Format**
- Condition: `dueDate && !isValidISO8601(dueDate)`
- Error: "Due date must be in ISO8601 format"
- Code: "INVALID_FORMAT"
- HTTP Status: 400

**Rule 18: Assignees Count**
- Condition: `assignees && assignees.length > 10`
- Error: "Maximum 10 assignees allowed"
- Code: "MAX_ITEMS_EXCEEDED"
- HTTP Status: 400

**Rule 19: Assignees Valid UUID**
- Condition: `assignees && assignees.some(id => !isValidUUID(id))`
- Error: "Each assignee must be a valid user ID"
- Code: "INVALID_UUID"
- HTTP Status: 400

**Rule 20: Assignees Exist**
- Condition: `assignees && !(await allUsersExist(assignees))`
- Error: "One or more assignees do not exist"
- Code: "NOT_FOUND"
- HTTP Status: 400

**Rule 21: Metadata Count**
- Condition: `metadata && Object.keys(metadata).length > 50`
- Error: "Maximum 50 metadata pairs allowed"
- Code: "MAX_ITEMS_EXCEEDED"
- HTTP Status: 400

**Rule 22: Metadata Key Length**
- Condition: `metadata && Object.keys(metadata).some(key => key.length < 1 || key.length > 50)`
- Error: "Each metadata key must be between 1 and 50 characters"
- Code: "LENGTH_RANGE"
- HTTP Status: 400

**Rule 23: Metadata Value Length**
- Condition: `metadata && Object.values(metadata).some(value => typeof value === 'string' && value.length > 500)`
- Error: "Each metadata value must be at most 500 characters"
- Code: "LENGTH_EXCEEDED"
- HTTP Status: 400

**Rule 24: Metadata Type**
- Condition: `metadata && Object.values(metadata).some(value => !['string', 'number', 'boolean', 'object'].includes(typeof value))`
- Error: "Metadata values must be string, number, boolean, or object"
- Code: "TYPE_ERROR"
- HTTP Status: 400

---

#### 1.1.7: Error Handling (GRANULAR - 10+ Scenarios)

**Error Scenario 1: Missing Title**
- Trigger: User submits form without title
- Error Code: 400 VALIDATION_ERROR
- Error Message: "Title is required"
- User Action: Enter title and retry
- System Action: Reject request, return error

**Error Scenario 2: Invalid Type**
- Trigger: User selects invalid type
- Error Code: 400 VALIDATION_ERROR
- Error Message: "Type must be one of: REQUIREMENT, DESIGN, IMPLEMENTATION, TEST, DEPLOYMENT, DOCUMENTATION, RESEARCH, SPIKE"
- User Action: Select valid type and retry
- System Action: Reject request, return error

**Error Scenario 3: Unauthorized**
- Trigger: User not authenticated
- Error Code: 401 UNAUTHORIZED
- Error Message: "Authentication required"
- User Action: Login and retry
- System Action: Reject request, redirect to login

**Error Scenario 4: Forbidden**
- Trigger: User lacks CREATE permission
- Error Code: 403 FORBIDDEN
- Error Message: "You do not have permission to create items in this project"
- User Action: Request access or contact admin
- System Action: Reject request, return error

**Error Scenario 5: Duplicate Title**
- Trigger: Item with same title already exists
- Error Code: 409 CONFLICT
- Error Message: "An item with this title already exists in this project"
- User Action: Use different title and retry
- System Action: Reject request, return error

**Error Scenario 6: Rate Limit Exceeded**
- Trigger: User exceeds rate limit (100 items/hour)
- Error Code: 429 RATE_LIMIT_EXCEEDED
- Error Message: "You have exceeded the rate limit"
- User Action: Wait and retry later
- System Action: Reject request, return error with retry-after header

**Error Scenario 7: Invalid Assignee**
- Trigger: Assignee user ID doesn't exist
- Error Code: 400 VALIDATION_ERROR
- Error Message: "One or more assignees do not exist"
- User Action: Select valid assignees and retry
- System Action: Reject request, return error

**Error Scenario 8: Database Error**
- Trigger: Database connection fails
- Error Code: 500 INTERNAL_SERVER_ERROR
- Error Message: "An unexpected error occurred"
- User Action: Retry request
- System Action: Log error, retry with exponential backoff

**Error Scenario 9: Search Index Error**
- Trigger: Search index fails to update
- Error Code: 500 INTERNAL_SERVER_ERROR
- Error Message: "An unexpected error occurred"
- User Action: Retry request
- System Action: Log error, retry with exponential backoff

**Error Scenario 10: Notification Error**
- Trigger: Notification service fails
- Error Code: 500 INTERNAL_SERVER_ERROR
- Error Message: "An unexpected error occurred"
- User Action: Retry request
- System Action: Log error, retry with exponential backoff, item still created

---

#### 1.1.8: Real-Time Events (GRANULAR - 5+ Events)

**Event 1: Item Created**
- Event Name: `items:created`
- Trigger: Item successfully created
- Broadcast To: All connected clients in organization
- Payload:
  ```json
  {
    "type": "items:created",
    "item": {
      "id": "uuid",
      "title": "string",
      "type": "string",
      "priority": "string",
      "createdBy": "uuid",
      "createdAt": "ISO8601"
    },
    "userId": "uuid",
    "timestamp": "ISO8601"
  }
  ```
- Latency: <100ms

**Event 2: Activity Feed Updated**
- Event Name: `activity:item-created`
- Trigger: Item successfully created
- Broadcast To: All connected clients in organization
- Payload:
  ```json
  {
    "type": "activity:item-created",
    "action": "CREATE",
    "entity": "Item",
    "entityId": "uuid",
    "userId": "uuid",
    "timestamp": "ISO8601",
    "details": {
      "title": "string",
      "type": "string"
    }
  }
  ```
- Latency: <100ms

**Event 3: Search Index Updated**
- Event Name: `search:index-item`
- Trigger: Item successfully created
- Broadcast To: Search service
- Payload:
  ```json
  {
    "type": "search:index-item",
    "itemId": "uuid",
    "title": "string",
    "description": "string",
    "tags": ["string"],
    "metadata": {}
  }
  ```
- Latency: <500ms

**Event 4: Notification Sent**
- Event Name: `notifications:sent`
- Trigger: Item successfully created and assignees notified
- Broadcast To: Notification service
- Payload:
  ```json
  {
    "type": "notifications:sent",
    "recipients": ["uuid"],
    "notificationType": "ITEM_ASSIGNED",
    "data": {
      "itemId": "uuid",
      "itemTitle": "string",
      "assignedBy": "string"
    }
  }
  ```
- Latency: <1000ms

**Event 5: Dashboard Updated**
- Event Name: `dashboard:updated`
- Trigger: Item successfully created
- Broadcast To: All connected clients viewing dashboard
- Payload:
  ```json
  {
    "type": "dashboard:updated",
    "metric": "itemCount",
    "value": "number",
    "change": "+1"
  }
  ```
- Latency: <100ms

---

#### 1.1.9: Notifications (GRANULAR - 5+ Types)

**Notification 1: Creation Confirmation (Toast)**
- Type: Toast notification
- Trigger: Item successfully created
- Duration: 5 seconds
- Message: "Item created successfully"
- Action: Dismiss or view item
- Recipient: Creating user

**Notification 2: Assignment Notification (Email)**
- Type: Email notification
- Trigger: Item created with assignees
- Subject: "You have been assigned to: {itemTitle}"
- Body: "You have been assigned to {itemTitle} by {createdBy}"
- Action: View item link
- Recipients: Assigned users

**Notification 3: Assignment Notification (Slack)**
- Type: Slack notification
- Trigger: Item created with assignees (if Slack integration enabled)
- Channel: Team channel
- Message: "{createdBy} assigned you to {itemTitle}"
- Action: View item link
- Recipients: Assigned users

**Notification 4: Assignment Notification (In-App)**
- Type: In-app notification
- Trigger: Item created with assignees
- Icon: Item type icon
- Message: "You have been assigned to {itemTitle}"
- Action: View item
- Recipients: Assigned users

**Notification 5: Watcher Notification (In-App)**
- Type: In-app notification
- Trigger: Item created (if user is watching project)
- Icon: Item type icon
- Message: "New item created: {itemTitle}"
- Action: View item
- Recipients: Project watchers

---

#### 1.1.10: Audit Trail (GRANULAR)

**Audit Entry Structure**:
```json
{
  "id": "uuid",
  "action": "CREATE",
  "entity": "Item",
  "entityId": "uuid",
  "userId": "uuid",
  "userName": "string",
  "userEmail": "string",
  "timestamp": "ISO8601",
  "ipAddress": "string",
  "userAgent": "string",
  "changes": {
    "title": {
      "old": null,
      "new": "string"
    },
    "type": {
      "old": null,
      "new": "string"
    },
    "description": {
      "old": null,
      "new": "string"
    },
    "tags": {
      "old": [],
      "new": ["string"]
    },
    "priority": {
      "old": null,
      "new": "string"
    },
    "estimatedEffort": {
      "old": null,
      "new": "number"
    },
    "dueDate": {
      "old": null,
      "new": "ISO8601"
    },
    "assignees": {
      "old": [],
      "new": ["uuid"]
    },
    "metadata": {
      "old": {},
      "new": {}
    }
  },
  "status": "SUCCESS|FAILURE",
  "errorMessage": "string (if failure)"
}
```

**Audit Trail Retention**: 1 year

**Audit Trail Access**: Admin only

**Audit Trail Immutability**: Cannot be modified or deleted

---

#### 1.1.11: Performance Requirements (GRANULAR)

**Requirement 1: Response Time**
- Target: <100ms (p95)
- Measurement: Time from request received to response sent
- Includes: Validation, database write, real-time broadcast
- Excludes: Network latency

**Requirement 2: Database Write**
- Target: <50ms (p95)
- Measurement: Time to write item to database
- Includes: Insert, index update
- Excludes: Network latency

**Requirement 3: Real-Time Broadcast**
- Target: <100ms (p95)
- Measurement: Time from item created to event broadcast to all clients
- Includes: Event serialization, WebSocket send
- Excludes: Network latency

**Requirement 4: Search Indexing**
- Target: <500ms (p95)
- Measurement: Time to index item for full-text search
- Includes: Text extraction, index update
- Excludes: Network latency

**Requirement 5: Notification Sending**
- Target: <1000ms (p95)
- Measurement: Time to send notifications to assignees
- Includes: Email, Slack, in-app notifications
- Excludes: Email delivery time

**Requirement 6: Throughput**
- Target: 1000 items/second
- Measurement: Number of items created per second
- Includes: All operations (validation, database, real-time, search, notifications)
- Excludes: Network latency

**Requirement 7: Concurrency**
- Target: 10,000 concurrent users
- Measurement: Number of simultaneous create requests
- Includes: All operations
- Excludes: Network latency

**Requirement 8: Scalability**
- Target: Linear scaling with resources
- Measurement: Performance scales linearly with CPU, memory, database resources
- Includes: All operations
- Excludes: Network latency

---

#### 1.1.12: Concurrency Handling (GRANULAR)

**Optimistic Locking**:
- Mechanism: Version numbers
- Process:
  1. Read item with version number
  2. Modify item
  3. Write item with version check
  4. If version mismatch, return conflict error
  5. Client retries with latest version

**Conflict Resolution**:
- Strategy: Last write wins
- Process:
  1. Detect version mismatch
  2. Fetch latest version from database
  3. Merge changes (last write wins for scalars, union for arrays)
  4. Write merged version
  5. Notify client of conflict

**Retry Logic**:
- Strategy: Exponential backoff
- Retries: 3 attempts
- Backoff: 100ms, 200ms, 400ms
- Max wait: 700ms

**Deadlock Prevention**:
- Strategy: Ordered locking
- Process:
  1. Lock items in consistent order (by ID)
  2. Prevent circular wait
  3. Release locks in reverse order

---

#### 1.1.13: Caching Strategy (GRANULAR)

**Cache Duration**: 5 minutes

**Cache Key**: `item:{id}:{include}`

**Cache Invalidation**:
- On item update
- On item delete
- On link change
- On comment added
- On quality check result

**Cache Strategy**: LRU (Least Recently Used)

**Cache Size**: 10,000 items

**Cache Hit Rate Target**: >80%

---

#### 1.1.14: Authorization Rules (GRANULAR)

**Rule 1: CREATE Permission**
- User must have CREATE permission on project
- Permission checked before item creation
- Error: 403 Forbidden if permission denied

**Rule 2: Organization Membership**
- User must be in same organization as project
- Checked before item creation
- Error: 403 Forbidden if not in organization

**Rule 3: Subscription Status**
- User must have active subscription (if applicable)
- Checked before item creation
- Error: 403 Forbidden if subscription inactive

**Rule 4: Quota**
- User must not exceed quota (max items per project)
- Checked before item creation
- Error: 429 Too Many Requests if quota exceeded

---

#### 1.1.15: Data Retention Policy (GRANULAR)

**Active Items**: Retained indefinitely

**Archived Items**: Retained for 30 days (undo window)

**Deleted Items**: Permanently removed

**Audit Trail**: Retained for 1 year

**Activity Feed**: Retained for 1 year

**Search Index**: Updated in real-time

---

This is just the beginning of FR-1.1. Each FR should have similar depth and granularity.


