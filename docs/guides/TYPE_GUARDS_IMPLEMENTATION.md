# Type Guards Implementation Reference

## Overview
This document provides the complete implementation of type guards used to replace unsafe type casts in graph components.

## 1. ExpandableNodeData Type Guard

**Location:** `/frontend/apps/web/src/components/graph/nodes/ExpandableNode.tsx` (lines 522-550)

```typescript
/**
 * Type guard to validate ExpandableNodeData structure
 */
function isExpandableNodeData(data: unknown): data is ExpandableNodeData {
  if (typeof data !== "object" || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;

  // Required properties
  if (
    typeof obj.item !== "object" ||
    obj.item === null ||
    typeof (obj.item as Record<string, unknown>).id !== "string"
  ) {
    return false;
  }

  if (typeof obj.label !== "string") {
    return false;
  }

  if (typeof obj.type !== "string") {
    return false;
  }

  return true;
}
```

**Usage:**
```typescript
function ExpandableNodeComponent({ data: nodeData, selected }: NodeProps) {
  if (!isExpandableNodeData(nodeData)) {
    console.error("Invalid ExpandableNodeData structure:", nodeData);
    return null;
  }

  const data = nodeData; // TypeScript knows data is ExpandableNodeData
  // ... rest of component
}
```

**What it validates:**
- `data` is an object
- `data.item` exists and is an object
- `data.item.id` exists and is a string
- `data.label` is a string
- `data.type` is a string

**Optional properties** (not validated but available on type):
- `data.description` (string)
- `data.status` (string)
- `data.priority` (string)
- `data.depth` (number)
- `data.hasChildren` (boolean)
- `data.childCount` (number)
- `data.parentId` (string)
- `data.path` (string[])
- `data.thumbnailUrl` (string)
- `data.previewComponent` (string)
- `data.incomingLinks` (number)
- `data.outgoingLinks` (number)
- `data.canEdit` (boolean)
- `data.editType` (string)
- `data.expansionState` (NodeExpansionState)
- `data.isSelected` (boolean)
- `data.onExpand` (callback)
- `data.onNavigate` (callback)
- `data.onEdit` (callback)
- `data.onViewFullPage` (callback)

## 2. AggregateNodeData Type Guard

**Location:** `/frontend/apps/web/src/components/graph/AggregateGroupNode.tsx` (lines 33-68)

```typescript
/**
 * Type guard to validate AggregateNodeData structure
 */
function isAggregateNodeData(data: unknown): data is AggregateNodeData {
  if (typeof data !== "object" || data === null) {
    return false;
  }

  const obj = data as Record<string, unknown>;

  // Validate group property
  if (
    typeof obj.group !== "object" ||
    obj.group === null ||
    typeof (obj.group as Record<string, unknown>).id !== "string"
  ) {
    return false;
  }

  // Validate items array
  if (!Array.isArray(obj.items)) {
    return false;
  }

  // Validate isExpanded boolean
  if (typeof obj.isExpanded !== "boolean") {
    return false;
  }

  // Validate onToggle function
  if (typeof obj.onToggle !== "function") {
    return false;
  }

  return true;
}
```

**Usage:**
```typescript
function AggregateGroupNodeComponent({ data: nodeData, selected }: NodeProps) {
  if (!isAggregateNodeData(nodeData)) {
    console.error("Invalid AggregateNodeData structure:", nodeData);
    return null;
  }

  const data = nodeData; // TypeScript knows data is AggregateNodeData

  const handleToggle = useCallback(() => {
    data.onToggle(data.group.id);
  }, [data]);

  // ... rest of component
}
```

**What it validates:**
- `data` is an object
- `data.group` exists and is an object
- `data.group.id` exists and is a string
- `data.items` is an array
- `data.isExpanded` is a boolean
- `data.onToggle` is a function

**Optional properties** (not validated but available on type):
- `data.onItemSelect` (callback)

## 3. PendingRequest Type Update

**Location:** `/frontend/apps/web/src/components/graph/hooks/useGraphWorker.ts` (lines 38-43)

```typescript
interface PendingRequest {
  id: string;
  resolve: (value: LayoutResult) => void;
  reject: (reason: Error) => void;
  // Store timeout as NodeJS.Timeout | number to support both browser and Node.js environments
  timeout: NodeJS.Timeout | number;
}
```

**Why this changed:**
- `setTimeout()` in browsers returns `number`
- `setTimeout()` in Node.js returns `NodeJS.Timeout`
- Using a union type `NodeJS.Timeout | number` handles both environments
- No need for unsafe casting anymore
- `clearTimeout()` accepts both types, so no usage changes needed

**Explanation of environments:**
```typescript
// Browser environment
const timeoutId = setTimeout(fn, 1000); // timeoutId is number

// Node.js environment
const timeoutId = setTimeout(fn, 1000); // timeoutId is NodeJS.Timeout

// Both work with the union type
timeout: NodeJS.Timeout | number
```

## Pattern Explanation

### What is a Type Guard?

A type guard is a TypeScript feature that allows runtime validation of types. It uses the special `data is Type` syntax to tell TypeScript that if the function returns `true`, the `data` parameter is now known to be of type `Type`.

### General Pattern

```typescript
function isMyType(data: unknown): data is MyType {
  // Check all required properties
  // Return true only if ALL checks pass
  // Return false if ANY check fails
  return true;
}

// Usage
function processData(data: unknown) {
  if (isMyType(data)) {
    // Inside this block, TypeScript knows data is MyType
    const typed = data; // No cast needed
    console.log(typed.requiredProperty);
  } else {
    // Handle invalid data
    console.error("Invalid data:", data);
  }
}
```

### Key Benefits

1. **Type Safety:** Compile-time checking + runtime validation
2. **No Performance Cost:** Simple `typeof` and `instanceof` checks
3. **Clear Intent:** Code is explicit about what it expects
4. **Error Handling:** Can handle invalid data gracefully
5. **Maintainability:** Requirements are documented in code

## Comparison: Before vs After

### Before (Unsafe)
```typescript
const data = nodeData as unknown as ExpandableNodeData;
// Problems:
// - No validation
// - Assumes data structure is correct
// - Silent failures if data is wrong
// - Hard to debug
// - Type system is bypassed
```

### After (Safe)
```typescript
if (!isExpandableNodeData(nodeData)) {
  console.error("Invalid ExpandableNodeData structure:", nodeData);
  return null;
}
const data = nodeData; // data is ExpandableNodeData (type-safe)
// Benefits:
// - Runtime validation
// - Early error detection
// - Clear error messages
// - TypeScript type narrowing
// - No unsafe casts
```

## Testing Type Guards

Type guards can be tested to ensure they correctly validate data:

```typescript
describe('isExpandableNodeData', () => {
  it('returns true for valid data', () => {
    const valid = {
      item: { id: '123' },
      label: 'Test',
      type: 'feature'
    };
    expect(isExpandableNodeData(valid)).toBe(true);
  });

  it('returns false for missing required property', () => {
    const invalid = {
      item: { id: '123' },
      label: 'Test'
      // missing type
    };
    expect(isExpandableNodeData(invalid)).toBe(false);
  });

  it('returns false for null', () => {
    expect(isExpandableNodeData(null)).toBe(false);
  });

  it('returns false for non-object', () => {
    expect(isExpandableNodeData('string')).toBe(false);
    expect(isExpandableNodeData(123)).toBe(false);
  });
});
```

## Future Improvements

### Option 1: Use Zod for Complex Validation
```typescript
import { z } from 'zod';

const ExpandableNodeDataSchema = z.object({
  item: z.object({ id: z.string() }),
  label: z.string(),
  type: z.string(),
  description: z.string().optional(),
  status: z.string().optional(),
  // ... other properties
});

type ExpandableNodeData = z.infer<typeof ExpandableNodeDataSchema>;

// Usage
try {
  const data = ExpandableNodeDataSchema.parse(nodeData);
} catch (error) {
  console.error('Invalid data:', error.message);
}
```

### Option 2: Use io-ts for Codecs
```typescript
import * as t from 'io-ts';

const ExpandableNodeDataCodec = t.type({
  item: t.type({ id: t.string }),
  label: t.string,
  type: t.string,
});

// Usage with either/Either monad
const result = ExpandableNodeDataCodec.decode(nodeData);
if (result._tag === 'Right') {
  const data = result.right; // data is ExpandableNodeData
}
```

## Conclusion

Type guards provide a TypeScript-native way to validate data at runtime while maintaining full type safety. They're lightweight, performant, and explicit about requirements. For more complex validation scenarios, consider Zod or io-ts.
