# URL Redirect Implementation - Backward Compatibility

## Overview

This implementation adds redirect handlers for old URL formats to maintain backward compatibility after the URL structure refactoring. Old bookmarks and links will automatically redirect to the new format.

## Implemented Redirects

### 1. Item Detail Redirect: `/items/:itemId` → `/projects/:projectId/views/:viewType/:itemId`

**File:** `/frontend/apps/web/src/routes/items.$itemId.tsx`

**Behavior:**

- Fetches the item by ID
- Extracts `projectId` and `view` from the item data
- Redirects to the new URL format: `/projects/{projectId}/views/{viewType}/{itemId}`
- Converts view type to lowercase (e.g., "FEATURE" → "feature")
- Uses `replace: true` to prevent back button issues

**States:**

- **Loading:** Shows spinner with "Redirecting..." message
- **Success:** Redirects to new URL
- **Error:** Shows "Item Not Found" message with link back to projects

**Example:**

```
Old: /items/abc123
New: /projects/proj-456/views/feature/abc123
```

### 2. Items List Redirect: `/items` → `/projects`

**File:** `/frontend/apps/web/src/routes/items.index.tsx`

**Behavior:**

- Immediately redirects to projects list page
- Shows "Redirecting to projects..." message during redirect
- Uses `replace: true` to prevent back button issues

**Example:**

```
Old: /items
New: /projects
```

### 3. Graph Redirect: `/graph` → `/projects`

**File:** `/frontend/apps/web/src/routes/graph.index.tsx`

**Behavior:**

- Redirects to projects list page
- Shows helpful message: "Please select a project to view its graph"
- Uses `replace: true` to prevent back button issues

**Example:**

```
Old: /graph
New: /projects
```

### 4. Search Redirect: `/search` → `/projects`

**File:** `/frontend/apps/web/src/routes/search.index.tsx`

**Behavior:**

- Redirects to projects list page
- Shows helpful message: "Use Cmd+K or Ctrl+K to open global search"
- Uses `replace: true` to prevent back button issues

**Example:**

```
Old: /search
New: /projects
```

## Implementation Details

### URL Format Conversion

The item detail redirect handles several transformations:

1. **Project Context:** Fetches item to get `projectId`
2. **View Type:** Converts uppercase view types to lowercase (API returns "FEATURE", URL needs "feature")
3. **Path Structure:** Constructs new hierarchical path

### History Management

All redirects use `replace: true` to:

- Prevent users from going back to old URLs
- Maintain clean browser history
- Avoid redirect loops

### Error Handling

- **Item Not Found:** Shows user-friendly error with navigation options
- **API Errors:** Displays error message instead of redirecting
- **Loading State:** Shows spinner during data fetch

## Testing

### Unit Tests

**File:** `/frontend/apps/web/src/__tests__/routes/redirects.test.tsx`

Tests cover:

- Loading states
- Successful redirects
- Error handling
- View type case conversion
- History management (back button behavior)

### E2E Tests

**File:** `/frontend/apps/web/e2e/url-redirects.spec.ts`

Tests cover:

- Full redirect flow in real browser
- URL format validation
- Accessibility of loading and error states
- History navigation
- Multiple redirect scenarios

### Running Tests

```bash
# Unit tests
bun test src/__tests__/routes/redirects.test.tsx

# E2E tests
bun run test:e2e -- url-redirects.spec.ts

# All tests
bun run test:all
```

## Manual Verification

### Local Testing

1. Start the dev server:

   ```bash
   bun run dev
   ```

2. Test each redirect:

   ```bash
   # Item detail (replace with a real item ID from your database)
   open http://localhost:5173/items/YOUR_ITEM_ID

   # Items list
   open http://localhost:5173/items

   # Graph
   open http://localhost:5173/graph

   # Search
   open http://localhost:5173/search
   ```

3. Verify:
   - Loading spinner appears briefly
   - Redirect completes successfully
   - URL changes to new format
   - Page content loads correctly
   - Back button goes to previous page (not redirect URL)

### Accessibility

Each redirect page includes:

- Semantic HTML (h1, p, a elements)
- Visible loading state
- Clear error messages
- Keyboard-accessible links
- Screen reader friendly content

## Migration Notes

### For Users

- Old bookmarks will continue to work
- No action required
- Redirects are automatic and fast

### For Developers

- New code should use new URL format
- Old URL format is deprecated
- Redirects will be maintained for backward compatibility
- Consider adding redirect notices in release notes

## Files Modified/Created

### New Files

- `/frontend/apps/web/src/routes/items.$itemId.tsx`
- `/frontend/apps/web/src/routes/items.index.tsx`
- `/frontend/apps/web/src/routes/graph.index.tsx`
- `/frontend/apps/web/src/routes/search.index.tsx`
- `/frontend/apps/web/src/__tests__/routes/redirects.test.tsx`
- `/frontend/apps/web/e2e/url-redirects.spec.ts`
- `/frontend/apps/web/URL_REDIRECT_IMPLEMENTATION.md`

### Dependencies

- Uses existing `useItem` hook from `@/hooks/useItems`
- Uses TanStack Router for navigation
- No new dependencies added

## Performance Considerations

- Redirects happen client-side (no server round-trip)
- Item fetch uses React Query caching
- Redirect delay: ~100-500ms (item fetch time)
- No impact on SEO (client-side routing)

## Future Enhancements

Potential improvements:

1. Add server-side redirects in production (via Nginx/CDN)
2. Add analytics to track redirect usage
3. Deprecation warnings in console (dev mode)
4. Redirect logging for monitoring

## Troubleshooting

### Redirect Not Working

1. Check browser console for errors
2. Verify item ID exists in database
3. Check API response for item data
4. Verify React Query cache is working

### Infinite Redirect Loop

- Should not happen due to `replace: true`
- Check for circular dependencies in routing
- Verify URL format is correct

### Back Button Issues

- Redirects use `replace: true` to prevent this
- If issues occur, check navigation implementation
- Verify history state is not being manipulated elsewhere

## API Response Format

The item redirect expects this response format:

```json
{
  "id": "item-123",
  "project_id": "project-456",
  "view": "FEATURE",
  "type": "epic",
  "title": "Example Item",
  "status": "todo",
  "priority": "high",
  "version": 1,
  "created_at": "2024-01-01T00:00:00Z",
  "updated_at": "2024-01-01T00:00:00Z"
}
```

Required fields for redirect:

- `id`: Item identifier
- `project_id`: Project identifier
- `view`: View type (will be converted to lowercase)

## Monitoring

Consider tracking:

- Redirect success rate
- Failed item fetches (404s)
- Redirect latency
- Old URL usage frequency

This helps determine when redirects can be safely removed.
