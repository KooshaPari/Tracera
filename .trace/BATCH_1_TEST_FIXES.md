# Unit Test Fixes - Batch 1 Summary

## Overview
Fixed 7 failing unit tests across 2 test files in frontend/apps/web. All targeted tests now pass.

## Files Fixed

### 1. Header.test.tsx (4 failures → 4 passed)
**Location:** `/frontend/apps/web/src/__tests__/components/layout/Header.test.tsx`

**Root Cause:**
Header component uses `useTheme()` hook which requires a `ThemeProvider` context. Tests were rendering Header directly without the provider, causing:
```
Error: useTheme must be used within a ThemeProvider
```

**Fixes Applied:**
- Imported `ThemeProvider` from `@/providers/ThemeProvider`
- Wrapped all Header render calls with `<ThemeProvider>`
- Added `import React from "react"` for createElement support

**Tests Fixed:**
1. ✓ renders header with title
2. ✓ displays search input
3. ✓ displays create button
4. ✓ handles theme toggle

**Code Change Example:**
```typescript
// Before
render(<Header />);

// After
render(
  <ThemeProvider>
    <Header />
  </ThemeProvider>
);
```

### 2. useLinks.test.ts (3 failures → 6 passed)
**Location:** `/frontend/apps/web/src/__tests__/hooks/useLinks.test.ts`

**Root Cause:**
The `useLinks()` hook's `fetchLinks()` function returns `{ links: Link[], total: number }`, but tests were:
1. Mocking responses as plain arrays
2. Expecting plain arrays in assertions
3. Missing options parameter in fetch mock expectations

**Failures:**
- "should fetch links" - Expected array, received { links: [], total: 2 }
- "should fetch links with source filter" - Same shape mismatch
- "should fetch links with target filter" - Missing options in fetch.toHaveBeenCalledWith()

**Fixes Applied:**

#### Fix 1: Update Mock Response Shape
Changed all mock responses to match API contract:
```typescript
// Before
const mockLinks = [
  { id: "1", sourceId: "item-1", targetId: "item-2", type: "depends_on" },
];
mockFetch.mockResolvedValueOnce({
  ok: true,
  json: async () => mockLinks,
});

// After
const mockLinksArray = [
  { id: "1", sourceId: "item-1", targetId: "item-2", type: "depends_on" },
];
const mockResponse = {
  links: mockLinksArray,
  total: mockLinksArray.length,
};
mockFetch.mockResolvedValueOnce({
  ok: true,
  json: async () => mockResponse,
});
```

#### Fix 2: Update Test Assertions
Changed expectations to match actual response shape:
```typescript
// Before
expect(result.current.data).toEqual(mockLinks);

// After
expect(result.current.data).toEqual(mockResponse);
```

#### Fix 3: Fix Fetch Mock Expectations
Added options parameter to fetch call verification:
```typescript
// Before
expect(mockFetch).toHaveBeenCalledWith(
  expect.stringContaining("source_id=item-1"),
);

// After
expect(mockFetch).toHaveBeenCalledWith(
  expect.stringContaining("source_id=item-1"),
  expect.any(Object),  // <- Added headers/options object
);
```

**Tests Fixed:**
1. ✓ should fetch links (useLinks suite)
2. ✓ should fetch links with source filter
3. ✓ should fetch links with target filter
4. ✓ should handle fetch error (already passing)
5. ✓ should create a link (useCreateLink suite)
6. ✓ should handle create error

## Test Results

### Before
```
Test Files: 2 failed (2)
Tests: 7 failed | 3 passed (10)
```

### After
```
Test Files: 2 passed (2)
Tests: 10 passed (10)
```

## Key Lessons Learned

1. **Provider Wrappers:** Components using context hooks must have their provider in tests
2. **API Contract Alignment:** Mock responses must match actual implementation (useLinks returns { links, total })
3. **Fetch Mocking:** When mocking fetch with multiple parameters, all expected parameters must be accounted for in assertions

## Files Modified
- `/frontend/apps/web/src/__tests__/components/layout/Header.test.tsx`
- `/frontend/apps/web/src/__tests__/hooks/useLinks.test.ts`

## Commit Hash
c553df49: FIX: Resolve all failing unit tests - Header and useLinks (batch 1)
