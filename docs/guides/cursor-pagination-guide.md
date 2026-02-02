# Cursor-Based Pagination Guide

## Overview

TraceRTM now supports cursor-based pagination for efficient navigation through large datasets. This replaces traditional offset-based pagination for better performance and consistency.

## Why Cursor-Based Pagination?

### Advantages over Offset Pagination

1. **Consistent Results**: Prevents duplicate or skipped items when data changes during pagination
2. **Better Performance**: Avoids expensive OFFSET queries on large datasets
3. **Scalability**: O(1) complexity vs O(n) for offset-based pagination
4. **Real-time Friendly**: Works seamlessly with frequently updated data

### Use Cases

- Listing items in a project
- Search results
- Activity feeds
- Any dataset that changes frequently

## Backend Implementation

### Cursor Structure

Cursors are base64-encoded strings containing:
- **Item ID**: Unique identifier of the last item
- **Timestamp**: Creation timestamp for consistent ordering

Example cursor: `MTIzZTQ1NjctZTg5Yi0xMmQzLWE0NTYtNDI2NjE0MTc0MDAwOjEyMzQ1Njc4OTA=`

### API Endpoints

#### GET /api/v1/items

**Query Parameters:**
- `cursor` (optional): Cursor for next page
- `limit` (optional): Number of items per page (default: 50, max: 100)
- `offset` (optional, deprecated): Legacy offset pagination
- `project_id` (optional): Filter by project

**Response with Cursor:**
```json
{
  "items": [...],
  "next_cursor": "MTIzZTQ1NjctZTg5Yi0xMmQzLWE0NTYtNDI2NjE0MTc0MDAwOjEyMzQ1Njc4OTA=",
  "has_more": true,
  "count": 50
}
```

**Response without Cursor (legacy):**
```json
[...]
```

### Backend Code Example

```go
// Using cursor pagination in handler
cursorStr := c.QueryParam("cursor")
useCursor := cursorStr != ""
var cursorPtr *string

if useCursor {
    cursor, limit, err := utils.ParseCursorPaginationParams(cursorStr, 0, 50, 100)
    if err != nil {
        return c.JSON(http.StatusBadRequest, map[string]string{
            "error": "Invalid cursor: " + err.Error(),
        })
    }
    cursorPtr = &cursor
}

filter := repository.ItemFilter{
    ProjectID: projectIDPtr,
    Limit:     limit,
    Cursor:    cursorPtr,
    UseCursor: useCursor,
}

items, err := h.itemService.ListItems(c.Request().Context(), filter)
// ... handle response
```

### Repository Layer

The repository layer handles cursor-based queries:

```go
// Cursor-based query
if filter.UseCursor && filter.Cursor != nil {
    cursor, err := utils.DecodeCursor(*filter.Cursor)
    if err == nil && cursor != nil {
        query = query.Where(
            "(created_at < ?) OR (created_at = ? AND id > ?)",
            cursor.Timestamp,
            cursor.Timestamp,
            cursor.ID,
        )
    }
}

// Ensure consistent ordering
query.Order("created_at DESC, id ASC")
```

## Frontend Implementation

### TypeScript Types

```typescript
export interface PaginationParams {
  limit?: number;
  cursor?: string;
  offset?: number; // Deprecated
}

export interface CursorPaginationResponse<T> {
  items: T[];
  next_cursor?: string;
  has_more: boolean;
  count: number;
}
```

### API Client Usage

```typescript
// Fetch first page
const response = await itemsApi.list({
  project_id: projectId,
  limit: 50,
});

if ("next_cursor" in response) {
  // Cursor pagination response
  const { items, next_cursor, has_more } = response;

  // Fetch next page
  if (has_more && next_cursor) {
    const nextPage = await itemsApi.list({
      project_id: projectId,
      cursor: next_cursor,
      limit: 50,
    });
  }
} else {
  // Legacy array response
  const items = response;
}
```

### React Hook Example

```typescript
function useItemsPagination(projectId: string) {
  const [items, setItems] = useState<Item[]>([]);
  const [cursor, setCursor] = useState<string | undefined>();
  const [hasMore, setHasMore] = useState(false);
  const [loading, setLoading] = useState(false);

  const loadMore = async () => {
    setLoading(true);
    try {
      const response = await itemsApi.list({
        project_id: projectId,
        cursor,
        limit: 50,
      });

      if ("next_cursor" in response) {
        setItems(prev => [...prev, ...response.items]);
        setCursor(response.next_cursor);
        setHasMore(response.has_more);
      } else {
        setItems(response);
        setHasMore(false);
      }
    } finally {
      setLoading(false);
    }
  };

  return { items, loadMore, hasMore, loading };
}
```

## Migration Guide

### Backward Compatibility

The implementation maintains backward compatibility:
- Old clients using `offset` continue to work
- New clients can use `cursor` for better performance
- Response format adapts based on request parameters

### Migrating Existing Code

1. **Update API calls to check response type:**
```typescript
// Before
const items = await itemsApi.list(params);

// After
const response = await itemsApi.list(params);
const items = "next_cursor" in response ? response.items : response;
```

2. **Implement cursor-based pagination:**
```typescript
// Replace offset-based pagination
let offset = 0;
const limit = 50;
while (true) {
  const items = await itemsApi.list({ offset, limit });
  if (items.length < limit) break;
  offset += limit;
}

// With cursor-based pagination
let cursor: string | undefined;
do {
  const response = await itemsApi.list({ cursor, limit: 50 });
  if ("next_cursor" in response) {
    // Process items
    cursor = response.next_cursor;
    if (!response.has_more) break;
  } else {
    break;
  }
} while (cursor);
```

## Best Practices

### Cursor Management

1. **Store cursors temporarily**: Don't persist cursors across sessions
2. **Validate cursors**: Always handle invalid cursor errors gracefully
3. **Set appropriate limits**: Balance between performance and UX
4. **Handle edge cases**: Empty results, invalid cursors, etc.

### Performance Considerations

1. **Index optimization**: Ensure `created_at` and `id` are indexed
2. **Limit boundaries**: Enforce maximum limit (100 items)
3. **Cache first page**: Cache first page for frequently accessed data
4. **Prefetch next page**: Improve perceived performance

### Error Handling

```typescript
try {
  const response = await itemsApi.list({ cursor, limit: 50 });
  // Handle response
} catch (error) {
  if (error.message.includes("Invalid cursor")) {
    // Reset to first page
    const response = await itemsApi.list({ limit: 50 });
  } else {
    // Handle other errors
  }
}
```

## Testing

### Unit Tests

```go
func TestCursorPagination(t *testing.T) {
    // Test cursor encoding/decoding
    id := "123e4567-e89b-12d3-a456-426614174000"
    timestamp := time.Now()

    encoded := utils.EncodeCursor(id, timestamp)
    decoded, err := utils.DecodeCursor(encoded)

    assert.NoError(t, err)
    assert.Equal(t, id, decoded.ID)
    assert.Equal(t, timestamp.Unix(), decoded.Timestamp.Unix())
}
```

### Integration Tests

```go
func TestItemsPaginationWithCursor(t *testing.T) {
    // Create test items
    items := createTestItems(100)

    // Fetch first page
    response := listItems(ListParams{Limit: 50})
    assert.Len(t, response.Items, 50)
    assert.True(t, response.HasMore)

    // Fetch second page
    page2 := listItems(ListParams{
        Cursor: response.NextCursor,
        Limit: 50,
    })
    assert.Len(t, page2.Items, 50)
    assert.False(t, page2.HasMore)
}
```

## Monitoring

### Metrics to Track

1. **Cursor usage rate**: Percentage of requests using cursors
2. **Average page size**: Distribution of limit values
3. **Error rates**: Invalid cursor errors
4. **Query performance**: Response times for cursor vs offset queries

### Logging

```go
log.Printf("[PAGINATION] type=%s limit=%d cursor_provided=%v",
    paginationType, limit, cursor != nil)
```

## References

- [Backend Cursor Utils](/backend/internal/utils/cursor.go)
- [Repository Implementation](/backend/internal/repository/repository.go)
- [Handler Implementation](/backend/internal/handlers/item_handler.go)
- [Frontend Types](/frontend/apps/web/src/api/types.ts)
- [Frontend API Client](/frontend/apps/web/src/api/endpoints.ts)
