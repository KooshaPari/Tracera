# React Memoization Patterns - Quick Reference

This document provides quick-reference patterns for the memoization techniques used in ItemsKanbanView and ItemsTreeView.

## Pattern 1: Simple Component Memoization

**Use case:** Component with stable props that rarely change

```typescript
interface SimpleProps {
  title: string;
  count: number;
}

const SimpleComponent = memo(function SimpleComponent({ title, count }: SimpleProps) {
  return <div>{title}: {count}</div>;
});
```

**When to use:**

- ✓ Props are primitives (string, number, boolean)
- ✓ No callback prop changes
- ✓ Component is rendered many times

---

## Pattern 2: Custom Comparator (Property-Level)

**Use case:** Complex objects where default comparison fails

```typescript
interface Item {
  id: string;
  title: string;
  status: string;
  details: NestedObject; // Not compared
}

const ItemDisplay = memo(
  function ItemDisplay({ item, onUpdate }: ItemDisplayProps) {
    return <div>{item.title}</div>;
  },
  (prev, next) => {
    // Return true if props are equal (SKIP re-render)
    // Return false if props differ (DO re-render)
    return (
      prev.item.id === next.item.id &&
      prev.item.title === next.item.title &&
      prev.item.status === next.item.status
      // Skip comparing deeply nested details
    );
  },
);
```

**Key points:**

- Compare only properties that affect rendering
- Skip expensive nested object comparisons
- Return `true` to skip render, `false` to render

---

## Pattern 3: Array Comparison in Custom Comparator

**Use case:** Arrays with dynamic content that needs careful comparison

```typescript
const ColumnList = memo(
  function ColumnList({ items, isActive }: ColumnListProps) {
    return <div>{items.map((item) => <Item key={item.id} {...item} />)}</div>;
  },
  (prev, next) => {
    // Bad: Just comparing length
    // return prev.items.length === next.items.length;

    // Good: Compare actual content
    return (
      prev.items.length === next.items.length &&
      prev.items.every(
        (item, idx) =>
          next.items[idx] &&
          item.id === next.items[idx].id &&
          item.status === next.items[idx].status,
      ) &&
      prev.isActive === next.isActive
    );
  },
);
```

**Key points:**

- Check length first (fast path)
- Then check content equality
- Compare only relevant properties

---

## Pattern 4: useCallback with Dependencies

**Use case:** Event handlers that depend on parent state

```typescript
interface Props {
  onUpdate: (id: string, data: object) => void;
  itemId: string;
}

function ParentComponent({ onUpdate, itemId }: Props) {
  const [count, setCount] = useState(0);

  // Bad: Handler changes on every render
  // const handleClick = () => onUpdate(itemId, { count });

  // Good: Handler is stable across renders
  const handleClick = useCallback(() => {
    onUpdate(itemId, { count });
  }, [itemId, onUpdate, count]); // Update when dependencies change

  return <ChildComponent onClick={handleClick} />;
}
```

**Key points:**

- Dependencies: Include all used variables
- Stable reference: Function doesn't change unless dependencies change
- Memoized children: Only re-render if callback actually changes

---

## Pattern 5: useMemo for Expensive Computations

**Use case:** Filtering, sorting, or transforming data

```typescript
function ItemList({ items, searchQuery, typeFilter }: ItemListProps) {
  // Bad: Runs on every render
  // const filtered = items.filter(i =>
  //   i.type === typeFilter &&
  //   i.title.includes(searchQuery)
  // );

  // Good: Only recomputes when dependencies change
  const filtered = useMemo(() => {
    return items.filter((item) => {
      if (typeFilter && item.type !== typeFilter) return false;
      if (searchQuery) {
        const query = searchQuery.toLowerCase();
        return item.title.toLowerCase().includes(query);
      }
      return true;
    });
  }, [items, searchQuery, typeFilter]);

  return <div>{filtered.map((item) => <Item key={item.id} {...item} />)}</div>;
}
```

**Key points:**

- Dependency array: Must include all used variables
- Skip if: Operation is cheap (<1ms)
- Use for: Filtering, sorting, tree building, grouping

---

## Pattern 6: Memoizing Children with Props

**Use case:** Lists of memoized components

```typescript
interface CardProps {
  item: Item;
  onDragStart: (item: Item) => void;
}

const Card = memo(function Card({ item, onDragStart }: CardProps) {
  // Handler must be memoized
  const handleDrag = useCallback(() => {
    onDragStart(item);
  }, [item, onDragStart]);

  return <div onDragStart={handleDrag}>{item.title}</div>;
});

function CardList({ items, onDragStart }: CardListProps) {
  // Callback must be stable or Card re-renders on each parent render
  const memoizedOnDragStart = useCallback(
    (item: Item) => onDragStart(item),
    [onDragStart],
  );

  return (
    <div>
      {items.map((item) => (
        <Card key={item.id} item={item} onDragStart={memoizedOnDragStart} />
      ))}
    </div>
  );
}
```

**Key points:**

- Parent callback: Must be memoized with useCallback
- Child component: Memoized with memo
- Dependencies: Only change when truly needed

---

## Pattern 7: Extracting Sub-Components

**Use case:** Large component with repeated or independent sections

```typescript
// Before: Everything in one component
function Dashboard({ items, onUpdate, onDelete }) {
  return (
    <div>
      <div className="header">{/* Header code */}</div>
      <div className="filters">{/* Filter code */}</div>
      <div className="list">
        {items.map((item) => (
          <div key={item.id}>{/* Item rendering */}</div>
        ))}
      </div>
    </div>
  );
}

// After: Extract memoized sub-components
const DashboardHeader = memo(function DashboardHeader() {
  return <div className="header">{/* Header code */}</div>;
});

const DashboardFilters = memo(function DashboardFilters({ onFilterChange }) {
  return <div className="filters">{/* Filter code */}</div>;
});

const DashboardList = memo(
  function DashboardList({ items, onUpdate, onDelete }) {
    return (
      <div className="list">
        {items.map((item) => (
          <div key={item.id}>{/* Item rendering */}</div>
        ))}
      </div>
    );
  },
  (prev, next) => {
    return (
      prev.items.length === next.items.length &&
      prev.items.every((item, idx) => item.id === next.items[idx]?.id)
    );
  },
);

function Dashboard({ items, onUpdate, onDelete }) {
  return (
    <>
      <DashboardHeader />
      <DashboardFilters />
      <DashboardList items={items} onUpdate={onUpdate} onDelete={onDelete} />
    </>
  );
}
```

**Benefits:**

- ✓ Smaller components are easier to memoize
- ✓ Can apply custom comparators per component
- ✓ Better re-render isolation
- ✓ Easier to test

---

## Pattern 8: Set-Based State in Callbacks

**Use case:** Toggling items in a collection (like expanded nodes)

```typescript
interface Props {
  nodes: TreeNode[];
  onToggleExpand: (nodeId: string) => void;
}

function TreeView({ nodes, onToggleExpand }: Props) {
  const [expandedIds, setExpandedIds] = useState<Set<string>>(new Set());

  // Bad: Creates new callback every render
  // const handleToggle = (id: string) => {
  //   setExpandedIds(prev => {
  //     const next = new Set(prev);
  //     next.has(id) ? next.delete(id) : next.add(id);
  //     return next;
  //   });
  // };

  // Good: Stable callback with useCallback
  const handleToggle = useCallback((id: string) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(id)) next.delete(id);
      else next.add(id);
      return next;
    });
  }, []);

  return (
    <div>
      {nodes.map((node) => (
        <TreeNode
          key={node.id}
          node={node}
          isExpanded={expandedIds.has(node.id)}
          onToggle={handleToggle}
        />
      ))}
    </div>
  );
}
```

**Key points:**

- Set state updates in functional setState
- useCallback with empty deps if no external dependencies
- Functional setState doesn't require Set in dependency array

---

## Pattern 9: Memoizing Collections

**Use case:** Static or rarely-changing list of options

```typescript
function FilterPanel() {
  // Bad: New array every render
  // const types = ["requirement", "feature", "test", "bug"];
  const types = useMemo(() => ["requirement", "feature", "test", "bug"], []);

  // Or use const outside component if truly static
  return (
    <Select>
      {types.map((type) => (
        <SelectItem key={type} value={type}>
          {type}
        </SelectItem>
      ))}
    </Select>
  );
}

// Better: Static arrays outside component
const ITEM_TYPES = ["requirement", "feature", "test", "bug"] as const;

function FilterPanel() {
  return (
    <Select>
      {ITEM_TYPES.map((type) => (
        <SelectItem key={type} value={type}>
          {type}
        </SelectItem>
      ))}
    </Select>
  );
}
```

**When to use:**

- ✓ useMemo: Array depends on component props
- ✓ const outside: Array is truly static
- ✓ Skip: Simple primitives or short lists

---

## Pattern 10: Conditional Memoization

**Use case:** Components with complex conditional rendering

```typescript
const ComplexItem = memo(
  function ComplexItem({ item, mode, onUpdate }: ComplexItemProps) {
    return (
      <div>
        {mode === "edit" && <EditForm item={item} onSave={onUpdate} />}
        {mode === "view" && <ViewDisplay item={item} />}
        {mode === "delete" && <DeleteConfirm item={item} />}
      </div>
    );
  },
  (prev, next) => {
    // If mode changes significantly, re-render
    if (prev.mode !== next.mode) return false;

    // Otherwise, check item properties
    return (
      prev.item.id === next.item.id &&
      prev.item.title === next.item.title &&
      prev.item.content === next.item.content
    );
  },
);
```

**Key points:**

- Comparator can be conditional
- Don't over-optimize - false is not expensive
- Return false to re-render (safe default)

---

## Common Mistakes & Fixes

### ❌ Mistake 1: Forgetting useCallback dependencies

```typescript
// Bad: onUpdate is missing from dependency array
const handleSave = useCallback(() => {
  onUpdate(data); // onUpdate might be stale!
}, []); // Missing onUpdate

// Good: Include all dependencies
const handleSave = useCallback(() => {
  onUpdate(data);
}, [onUpdate, data]);
```

### ❌ Mistake 2: useMemo with no dependencies

```typescript
// Bad: Computed on every render (defeats the purpose)
const result = useMemo(() => expensiveOperation(items), []);

// Good: Include dependency
const result = useMemo(() => expensiveOperation(items), [items]);
```

### ❌ Mistake 3: Comparing arrays by reference

```typescript
// Bad: Array comparison always fails
return (
  prev.items === next.items // Arrays are different references!
);

// Good: Compare content
return (
  prev.items.length === next.items.length &&
  prev.items.every((item, idx) => item.id === next.items[idx]?.id)
);
```

### ❌ Mistake 4: Inline objects in memoized component props

```typescript
function Parent() {
  return (
    <MemoizedChild
      config={{ option1: true, option2: false }} // New object every render!
      onUpdate={(id) => console.log(id)} // New function every render!
    />
  );
}

// Better: Use useCallback and useMemo
function Parent() {
  const config = useMemo(() => ({ option1: true, option2: false }), []);
  const handleUpdate = useCallback((id) => console.log(id), []);

  return <MemoizedChild config={config} onUpdate={handleUpdate} />;
}
```

---

## Performance Testing Quick Checklist

Use these steps to verify memoization effectiveness:

### In React DevTools Profiler:

- [ ] Record interaction (search, filter, drag)
- [ ] Check flame graph - should be flat (not tall)
- [ ] Memoized components appear in blue (skipped)
- [ ] Actual renders appear in yellow/red
- [ ] Total render time <10ms for most interactions

### In Chrome DevTools Performance:

- [ ] Start recording
- [ ] Perform action (type, click, drag)
- [ ] Stop recording
- [ ] Scripting time should be <20ms
- [ ] No excessive garbage collection
- [ ] Consistent 60 FPS frame rate

### In Console:

```javascript
// Check render count
performance.mark('start');
// ... perform interaction ...
performance.mark('end');
performance.measure('interaction', 'start', 'end');
console.log(performance.getEntriesByName('interaction'));
```

---

## Summary

| Pattern                  | Use Case                       | Performance Gain |
| ------------------------ | ------------------------------ | ---------------- |
| Component Memoization    | Stable props, repeated renders | 50-70%           |
| Custom Comparator        | Complex objects                | 60-80%           |
| useCallback              | Event handlers                 | 40-60%           |
| useMemo                  | Expensive computations         | 70-90%           |
| Sub-component Extraction | Large components               | 50-75%           |
| Set-based State          | Toggle operations              | 40-50%           |
| Collection Memoization   | Static lists                   | 30-40%           |

**Golden Rule:** Measure before and after. Not all optimizations are beneficial—premature optimization wastes time.

---

## References

- [React.memo docs](https://react.dev/reference/react/memo)
- [useCallback docs](https://react.dev/reference/react/useCallback)
- [useMemo docs](https://react.dev/reference/react/useMemo)
- [Performance Best Practices](https://react.dev/learn/render-and-commit)

---

**Last Updated:** January 30, 2026
**Created for:** ItemsKanbanView & ItemsTreeView optimization
