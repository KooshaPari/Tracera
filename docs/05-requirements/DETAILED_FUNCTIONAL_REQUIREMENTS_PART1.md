# Detailed Functional Requirements - Part 1: Item Management & Links

**Date**: 2025-11-22  
**Version**: 2.0 (EXTENDED)  
**Status**: APPROVED

---

## FR-1: ITEM MANAGEMENT (EXTENDED)

### FR-1.1: Create Item (DETAILED)

**Description**: Users can create new items representing different types of work (requirements, designs, implementations, tests, deployments) with comprehensive metadata and tracking.

**Detailed Acceptance Criteria**:
- [ ] User can create item with title (1-255 characters, required)
- [ ] User can select item type from enum (REQUIREMENT, DESIGN, IMPLEMENTATION, TEST, DEPLOYMENT)
- [ ] User can enter description (0-5000 characters, optional, supports markdown)
- [ ] User can add tags (0-20 tags, each 1-50 characters)
- [ ] User can set priority (LOW, MEDIUM, HIGH, CRITICAL)
- [ ] User can set estimated effort (1-100 story points)
- [ ] User can set due date (optional, future date only)
- [ ] User can assign to team members (0-10 assignees)
- [ ] User can add custom metadata (key-value pairs, up to 50 pairs)
- [ ] Item is assigned unique UUID (v4)
- [ ] Item status defaults to DRAFT
- [ ] Item creation timestamp recorded (UTC)
- [ ] Item creator recorded (from JWT token)
- [ ] Item appears in all views immediately (real-time)
- [ ] User receives confirmation notification (toast)
- [ ] Item appears in activity feed
- [ ] Item indexed for search (full-text search)
- [ ] Item version history initialized (version 1)
- [ ] Item change log initialized
- [ ] Item audit trail initialized

**API Endpoint**: `POST /api/items`

**Request Body**:
```json
{
  "title": "string (1-255)",
  "type": "REQUIREMENT|DESIGN|IMPLEMENTATION|TEST|DEPLOYMENT",
  "description": "string (0-5000, markdown)",
  "tags": ["string"],
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "estimatedEffort": "number (1-100)",
  "dueDate": "ISO8601 date (optional)",
  "assignees": ["uuid"],
  "metadata": {
    "key": "value"
  }
}
```

**Response**:
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
  "assignees": ["uuid"],
  "metadata": {},
  "status": "DRAFT",
  "createdAt": "ISO8601",
  "createdBy": "uuid",
  "updatedAt": "ISO8601",
  "updatedBy": "uuid",
  "version": 1
}
```

**GraphQL Mutation**:
```graphql
mutation CreateItem($input: CreateItemInput!) {
  createItem(input: $input) {
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
```

**tRPC Procedure**: `items.create`

```typescript
export const itemsRouter = router({
  create: protectedProcedure
    .input(z.object({
      title: z.string().min(1).max(255),
      type: z.enum(['REQUIREMENT', 'DESIGN', 'IMPLEMENTATION', 'TEST', 'DEPLOYMENT']),
      description: z.string().max(5000).optional(),
      tags: z.array(z.string()).max(20).optional(),
      priority: z.enum(['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']).optional(),
      estimatedEffort: z.number().min(1).max(100).optional(),
      dueDate: z.date().optional(),
      assignees: z.array(z.string().uuid()).max(10).optional(),
      metadata: z.record(z.any()).optional(),
    }))
    .mutation(async ({ ctx, input }) => {
      // Implementation
    }),
});
```

**Validation Rules**:
- Title: Required, 1-255 chars, no leading/trailing whitespace
- Type: Required, must be valid enum value
- Description: Optional, max 5000 chars, markdown allowed
- Tags: Optional, max 20 tags, each 1-50 chars
- Priority: Optional, defaults to MEDIUM
- Estimated Effort: Optional, 1-100 story points
- Due Date: Optional, must be future date
- Assignees: Optional, max 10 assignees, must be valid user IDs
- Metadata: Optional, max 50 key-value pairs

**Error Handling**:
- 400: Invalid input (validation error)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (no permission to create items)
- 409: Conflict (duplicate title in same project)
- 500: Server error

**Real-Time Events**:
- `items:created` - Broadcast to all connected clients
- `activity:item-created` - Add to activity feed
- `search:index-item` - Index for full-text search

**Notifications**:
- Toast: "Item created successfully"
- Email: Send to assignees (if configured)
- Slack: Send to team channel (if configured)

**Audit Trail**:
- Action: CREATE
- Entity: Item
- EntityId: UUID
- UserId: Creator UUID
- Timestamp: UTC
- Changes: All fields

**Performance Requirements**:
- Response time: <100ms (p95)
- Database write: <50ms
- Real-time broadcast: <100ms

**Concurrency Handling**:
- Optimistic locking with version numbers
- Conflict resolution: Last write wins
- Retry logic: Exponential backoff (3 retries)

---

### FR-1.2: Read Item (DETAILED)

**Description**: Users can view comprehensive item details including all metadata, relationships, history, and real-time status.

**Detailed Acceptance Criteria**:
- [ ] User can view item title, type, description
- [ ] User can view item status (DRAFT, ACTIVE, ARCHIVED)
- [ ] User can view item priority (LOW, MEDIUM, HIGH, CRITICAL)
- [ ] User can view item estimated effort (story points)
- [ ] User can view item due date (if set)
- [ ] User can view item assignees (with avatars, names, emails)
- [ ] User can view item tags (with colors)
- [ ] User can view item custom metadata
- [ ] User can view item creation timestamp and creator
- [ ] User can view item last update timestamp and updater
- [ ] User can view item version number
- [ ] User can view incoming links (items that depend on this)
- [ ] User can view outgoing links (items this depends on)
- [ ] User can view link count by type
- [ ] User can view agents working on item (real-time)
- [ ] User can view agent status (IDLE, WORKING, ERROR)
- [ ] User can view quality checks (results, status, timestamp)
- [ ] User can view quality check recommendations
- [ ] User can view change history (last 10 changes)
- [ ] User can view comments (threaded, with timestamps)
- [ ] User can view attachments (files, links, images)
- [ ] User can view activity feed (related to this item)
- [ ] User can view item dependencies (graph visualization)
- [ ] User can view item impact (items affected by changes)
- [ ] User can view item progress (if applicable)
- [ ] User can view item completion percentage
- [ ] User can view item risk level (calculated)
- [ ] User can view item health status (calculated)

**API Endpoint**: `GET /api/items/:id`

**Query Parameters**:
- `include`: Comma-separated list of related data to include
  - `links`: Include incoming/outgoing links
  - `agents`: Include assigned agents
  - `qualityChecks`: Include quality check results
  - `history`: Include change history
  - `comments`: Include comments
  - `attachments`: Include attachments
  - `activity`: Include activity feed
  - `dependencies`: Include dependency graph
  - `impact`: Include impact analysis
  - `all`: Include everything

**Response**:
```json
{
  "id": "uuid",
  "title": "string",
  "type": "string",
  "description": "string",
  "status": "string",
  "priority": "string",
  "estimatedEffort": "number",
  "dueDate": "ISO8601",
  "tags": ["string"],
  "assignees": [
    {
      "id": "uuid",
      "name": "string",
      "email": "string",
      "avatar": "url"
    }
  ],
  "metadata": {},
  "createdAt": "ISO8601",
  "createdBy": {
    "id": "uuid",
    "name": "string"
  },
  "updatedAt": "ISO8601",
  "updatedBy": {
    "id": "uuid",
    "name": "string"
  },
  "version": "number",
  "incomingLinks": [
    {
      "id": "uuid",
      "type": "string",
      "sourceId": "uuid",
      "sourceTitle": "string"
    }
  ],
  "outgoingLinks": [
    {
      "id": "uuid",
      "type": "string",
      "targetId": "uuid",
      "targetTitle": "string"
    }
  ],
  "agents": [
    {
      "id": "uuid",
      "name": "string",
      "status": "string",
      "lastSeen": "ISO8601"
    }
  ],
  "qualityChecks": [
    {
      "id": "uuid",
      "type": "string",
      "status": "PASS|FAIL|WARNING",
      "result": "string",
      "recommendations": ["string"],
      "timestamp": "ISO8601"
    }
  ],
  "history": [
    {
      "version": "number",
      "changes": {},
      "changedBy": "uuid",
      "changedAt": "ISO8601"
    }
  ],
  "comments": [
    {
      "id": "uuid",
      "text": "string",
      "author": "uuid",
      "createdAt": "ISO8601",
      "replies": []
    }
  ],
  "attachments": [
    {
      "id": "uuid",
      "name": "string",
      "type": "string",
      "url": "string",
      "size": "number",
      "uploadedAt": "ISO8601"
    }
  ],
  "activity": [
    {
      "id": "uuid",
      "action": "string",
      "actor": "uuid",
      "timestamp": "ISO8601",
      "details": {}
    }
  ],
  "dependencies": {
    "nodes": [],
    "edges": []
  },
  "impact": {
    "directlyAffected": ["uuid"],
    "indirectlyAffected": ["uuid"],
    "riskLevel": "LOW|MEDIUM|HIGH|CRITICAL"
  },
  "progress": {
    "percentage": "number",
    "status": "string",
    "completedAt": "ISO8601"
  },
  "health": {
    "status": "HEALTHY|WARNING|CRITICAL",
    "issues": ["string"]
  }
}
```

**GraphQL Query**:
```graphql
query GetItem($id: UUID!, $include: [String!]) {
  item(id: $id, include: $include) {
    id
    title
    type
    description
    status
    priority
    estimatedEffort
    dueDate
    tags
    assignees {
      id
      name
      email
      avatar
    }
    metadata
    createdAt
    createdBy {
      id
      name
    }
    updatedAt
    updatedBy {
      id
      name
    }
    version
    incomingLinks {
      id
      type
      source {
        id
        title
      }
    }
    outgoingLinks {
      id
      type
      target {
        id
        title
      }
    }
    agents {
      id
      name
      status
      lastSeen
    }
    qualityChecks {
      id
      type
      status
      result
      recommendations
      timestamp
    }
    history {
      version
      changes
      changedBy {
        id
        name
      }
      changedAt
    }
    comments {
      id
      text
      author {
        id
        name
      }
      createdAt
      replies {
        id
        text
        author {
          id
          name
        }
        createdAt
      }
    }
    attachments {
      id
      name
      type
      url
      size
      uploadedAt
    }
    activity {
      id
      action
      actor {
        id
        name
      }
      timestamp
      details
    }
    dependencies {
      nodes {
        id
        title
      }
      edges {
        source
        target
        type
      }
    }
    impact {
      directlyAffected {
        id
        title
      }
      indirectlyAffected {
        id
        title
      }
      riskLevel
    }
    progress {
      percentage
      status
      completedAt
    }
    health {
      status
      issues
    }
  }
}
```

**tRPC Procedure**: `items.get`

**Caching**:
- Cache duration: 5 minutes
- Cache key: `item:{id}:{include}`
- Invalidate on: item update, link change, comment added
- Cache strategy: LRU (Least Recently Used)

**Performance Requirements**:
- Response time: <200ms (p95)
- Database query: <100ms
- Cache hit rate: >80%

**Authorization**:
- User must have READ permission on item
- User must be in same organization as item
- User can see only their own private items

**Real-Time Updates**:
- Subscribe to item changes
- Subscribe to agent status changes
- Subscribe to quality check results
- Subscribe to comments
- Subscribe to activity feed

---

### FR-1.3: Update Item (DETAILED)

**Description**: Users can modify item details with real-time synchronization, conflict resolution, and comprehensive audit trail.

**Detailed Acceptance Criteria**:
- [ ] User can update title (1-255 chars)
- [ ] User can update description (0-5000 chars, markdown)
- [ ] User can update status (DRAFT → ACTIVE → ARCHIVED)
- [ ] User can update priority (LOW, MEDIUM, HIGH, CRITICAL)
- [ ] User can update estimated effort (1-100 story points)
- [ ] User can update due date (future date only)
- [ ] User can add/remove tags (max 20 tags)
- [ ] User can add/remove assignees (max 10 assignees)
- [ ] User can update custom metadata
- [ ] User can add comments
- [ ] User can add attachments
- [ ] Update timestamp recorded (UTC)
- [ ] Update user recorded (from JWT token)
- [ ] Change history tracked (all changes)
- [ ] Real-time sync to all connected clients (<100ms)
- [ ] Conflict detection (concurrent edits)
- [ ] Conflict resolution (CRDT merge)
- [ ] Change notifications sent (to assignees, watchers)
- [ ] Activity feed updated
- [ ] Search index updated
- [ ] Version number incremented
- [ ] Undo available for 30 days
- [ ] Optimistic locking (version check)
- [ ] Partial updates supported (only changed fields)

**API Endpoint**: `PATCH /api/items/:id`

**Request Body** (all fields optional):
```json
{
  "title": "string (1-255)",
  "description": "string (0-5000)",
  "status": "DRAFT|ACTIVE|ARCHIVED",
  "priority": "LOW|MEDIUM|HIGH|CRITICAL",
  "estimatedEffort": "number (1-100)",
  "dueDate": "ISO8601 date",
  "tags": ["string"],
  "assignees": ["uuid"],
  "metadata": {
    "key": "value"
  },
  "version": "number (for optimistic locking)"
}
```

**Response**:
```json
{
  "id": "uuid",
  "title": "string",
  "description": "string",
  "status": "string",
  "priority": "string",
  "estimatedEffort": "number",
  "dueDate": "ISO8601",
  "tags": ["string"],
  "assignees": ["uuid"],
  "metadata": {},
  "updatedAt": "ISO8601",
  "updatedBy": "uuid",
  "version": "number",
  "changes": {
    "title": {
      "old": "string",
      "new": "string"
    }
  }
}
```

**GraphQL Mutation**:
```graphql
mutation UpdateItem($id: UUID!, $input: UpdateItemInput!) {
  updateItem(id: $id, input: $input) {
    id
    title
    description
    status
    priority
    estimatedEffort
    dueDate
    tags
    assignees {
      id
      name
    }
    metadata
    updatedAt
    updatedBy {
      id
      name
    }
    version
    changes {
      field
      oldValue
      newValue
    }
  }
}

input UpdateItemInput {
  title: String
  description: String
  status: ItemStatus
  priority: Priority
  estimatedEffort: Int
  dueDate: Date
  tags: [String!]
  assignees: [UUID!]
  metadata: JSON
  version: Int!
}
```

**tRPC Procedure**: `items.update`

**Conflict Resolution**:
- Detect concurrent edits (version mismatch)
- Use CRDT (Conflict-free Replicated Data Type) for merge
- Merge strategy: Last write wins for scalars, union for arrays
- Notify user of conflict
- Provide merge options (local, remote, manual)

**Validation Rules**:
- Title: 1-255 chars, no leading/trailing whitespace
- Description: Max 5000 chars, markdown allowed
- Status: Valid enum value, valid transition
- Priority: Valid enum value
- Estimated Effort: 1-100 story points
- Due Date: Future date only
- Tags: Max 20 tags, each 1-50 chars
- Assignees: Max 10 assignees, valid user IDs

**Error Handling**:
- 400: Invalid input (validation error)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (no permission to update item)
- 409: Conflict (version mismatch, concurrent edit)
- 410: Gone (item deleted)
- 500: Server error

**Real-Time Events**:
- `items:updated` - Broadcast to all connected clients
- `items:conflict-detected` - Notify user of conflict
- `activity:item-updated` - Add to activity feed
- `search:update-index` - Update search index

**Notifications**:
- Toast: "Item updated successfully"
- Email: Send to assignees (if configured)
- Slack: Send to team channel (if configured)
- Mention: Send to mentioned users

**Audit Trail**:
- Action: UPDATE
- Entity: Item
- EntityId: UUID
- UserId: Updater UUID
- Timestamp: UTC
- Changes: All changed fields (old value, new value)
- Version: New version number

**Performance Requirements**:
- Response time: <100ms (p95)
- Database write: <50ms
- Real-time broadcast: <100ms
- Conflict resolution: <500ms

**Concurrency Handling**:
- Optimistic locking with version numbers
- Conflict detection and resolution
- Retry logic: Exponential backoff (3 retries)
- Deadlock prevention: Ordered locking

---

### FR-1.4: Delete Item (DETAILED)

**Description**: Users can delete items with soft-delete (archive) and hard-delete (admin only) options, with comprehensive audit trail and undo support.

**Detailed Acceptance Criteria**:
- [ ] User can soft-delete item (mark as archived)
- [ ] User can hard-delete item (admin only, permanent)
- [ ] Soft-delete: Item status changes to ARCHIVED
- [ ] Soft-delete: Item remains in database (recoverable)
- [ ] Soft-delete: Item hidden from normal views
- [ ] Soft-delete: Item visible in archive view
- [ ] Hard-delete: Item permanently removed from database
- [ ] Hard-delete: Item removed from all relationships
- [ ] Hard-delete: Item removed from search index
- [ ] Linked items notified of deletion
- [ ] Incoming links removed
- [ ] Outgoing links removed
- [ ] Assigned agents notified
- [ ] Deletion logged in audit trail
- [ ] Deletion logged in activity feed
- [ ] Undo available for 30 days (soft-delete only)
- [ ] Undo restores item to previous state
- [ ] Undo restores all relationships
- [ ] Deletion timestamp recorded
- [ ] Deletion user recorded
- [ ] Deletion reason recorded (optional)
- [ ] Cascading delete handled (sub-items)
- [ ] Orphaned links handled

**API Endpoint**: `DELETE /api/items/:id`

**Query Parameters**:
- `hard`: Boolean (default: false)
  - false: Soft-delete (archive)
  - true: Hard-delete (permanent, admin only)
- `reason`: String (optional, max 500 chars)

**Response**:
```json
{
  "id": "uuid",
  "status": "ARCHIVED|DELETED",
  "deletedAt": "ISO8601",
  "deletedBy": "uuid",
  "reason": "string",
  "undoToken": "string (for soft-delete only)",
  "undoExpiresAt": "ISO8601"
}
```

**GraphQL Mutation**:
```graphql
mutation DeleteItem($id: UUID!, $hard: Boolean, $reason: String) {
  deleteItem(id: $id, hard: $hard, reason: $reason) {
    id
    status
    deletedAt
    deletedBy {
      id
      name
    }
    reason
    undoToken
    undoExpiresAt
  }
}
```

**tRPC Procedure**: `items.delete`

**Soft-Delete Process**:
1. Validate user has DELETE permission
2. Check if item is already deleted
3. Update item status to ARCHIVED
4. Record deletion metadata
5. Notify linked items
6. Notify assigned agents
7. Update search index
8. Broadcast real-time event
9. Add to activity feed
10. Generate undo token (valid for 30 days)

**Hard-Delete Process**:
1. Validate user is admin
2. Validate user has DELETE permission
3. Check if item is already deleted
4. Remove all incoming links
5. Remove all outgoing links
6. Remove from search index
7. Delete from database
8. Notify linked items
9. Notify assigned agents
10. Broadcast real-time event
11. Add to activity feed
12. Archive audit trail

**Undo Process**:
1. Validate undo token
2. Check undo expiration (30 days)
3. Restore item from archive
4. Restore all relationships
5. Restore search index
6. Notify linked items
7. Notify assigned agents
8. Broadcast real-time event
9. Add to activity feed

**Authorization**:
- Soft-delete: User must have DELETE permission on item
- Hard-delete: User must be admin
- User must be in same organization as item

**Error Handling**:
- 400: Invalid input (validation error)
- 401: Unauthorized (not authenticated)
- 403: Forbidden (no permission to delete item)
- 404: Not found (item doesn't exist)
- 410: Gone (item already deleted)
- 500: Server error

**Real-Time Events**:
- `items:deleted` - Broadcast to all connected clients
- `items:archived` - Broadcast to all connected clients
- `activity:item-deleted` - Add to activity feed
- `search:remove-index` - Remove from search index

**Notifications**:
- Toast: "Item deleted successfully" or "Item archived successfully"
- Email: Send to assignees (if configured)
- Slack: Send to team channel (if configured)

**Audit Trail**:
- Action: DELETE or ARCHIVE
- Entity: Item
- EntityId: UUID
- UserId: Deleter UUID
- Timestamp: UTC
- Reason: Optional reason
- Hard: Boolean (hard delete or soft delete)

**Performance Requirements**:
- Response time: <100ms (p95)
- Database write: <50ms
- Real-time broadcast: <100ms
- Cascading delete: <500ms

**Data Retention**:
- Soft-deleted items: Retained for 30 days (undo window)
- Hard-deleted items: Permanently removed
- Audit trail: Retained for 1 year
- Activity feed: Retained for 1 year


