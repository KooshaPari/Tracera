# Table Accessibility - Quick Start Guide

## Quick Implementation

### Step 1: Use Accessible Base Components

The base table components now include full ARIA support:

```tsx
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from '@/components/ui/table';

export function MyTable() {
  return (
    <Table ariaLabel='Sample data table'>
      <TableHeader>
        <TableRow>
          <TableHead colIndex={1} isSortable sortDirection='ascending'>
            Name
          </TableHead>
          <TableHead colIndex={2}>Email</TableHead>
        </TableRow>
      </TableHeader>
      <TableBody>
        <TableRow rowIndex={2}>
          <TableCell colIndex={1} headerText='Name'>
            John Doe
          </TableCell>
          <TableCell colIndex={2} headerText='Email'>
            john@example.com
          </TableCell>
        </TableRow>
      </TableBody>
    </Table>
  );
}
```

### Step 2: Add Keyboard Navigation

```tsx
import { useTableKeyboardNavigation } from "@/hooks/useTableKeyboardNavigation";

export function MyAccessibleTable() {
  const [items, setItems] = useState([...]);

  const { focusState } = useTableKeyboardNavigation({
    rowCount: items.length,
    colCount: 3,
    containerId: "my-table",
  });

  return (
    <div
      id="my-table"
      role="region"
      aria-label="Data table with keyboard navigation"
      aria-describedby="table-instructions"
    >
      <div id="table-instructions" className="sr-only">
        Use arrow keys to navigate. Home and End jump to columns.
        Ctrl+Home and Ctrl+End jump to table edges.
      </div>

      <Table>
        {/* table content */}
      </Table>

      {/* Live region for announcements */}
      <div
        id="table-announcements"
        role="status"
        aria-live="polite"
        aria-atomic="true"
        className="sr-only"
      />
    </div>
  );
}
```

### Step 3: Make Cells Focusable

```tsx
// In your table row component
<TableCell
  data-col-index={colIndex}
  tabIndex={isKeyboardFocused ? 0 : -1}
  className='focus:ring-2 focus:ring-primary'
>
  <button onClick={handleClick}>Interactive content</button>
</TableCell>
```

## Essential ARIA Attributes

| Attribute             | Where          | Example                     | Purpose             |
| --------------------- | -------------- | --------------------------- | ------------------- |
| `role="table"`        | `<table>`      | `<table role="table">`      | Identifies as table |
| `aria-label`          | `<table>`      | `ariaLabel="Items"`         | Describes table     |
| `role="columnheader"` | `<th>`         | Auto with TableHead         | Header cell         |
| `aria-colindex`       | `<th>`, `<td>` | `colIndex={1}`              | Column position     |
| `aria-sort`           | `<th>`         | `sortDirection="ascending"` | Sort state          |
| `role="row"`          | `<tr>`         | Auto with TableRow          | Table row           |
| `aria-rowindex`       | `<tr>`         | `rowIndex={2}`              | Row position        |
| `role="gridcell"`     | `<td>`         | Auto with TableCell         | Data cell           |

## Common Patterns

### Sortable Column Header

```tsx
<TableHead colIndex={1} isSortable sortDirection={sortColumn === 'name' ? 'ascending' : 'none'}>
  <button
    onClick={() => setSortColumn('name')}
    aria-label={`Name, ${sortColumn === 'name' ? 'sorted ascending' : 'not sorted'}`}
    className='focus:ring-2 focus:ring-primary'
  >
    Name
    {sortColumn === 'name' && <ArrowUp aria-hidden='true' />}
  </button>
</TableHead>
```

### Focusable Data Cell

```tsx
<TableCell
  data-col-index={0}
  colIndex={1}
  headerText='Title'
  tabIndex={isKeyboardFocused ? 0 : -1}
  className='focus:ring-2 focus:ring-primary rounded'
>
  <button onClick={handleNavigate} aria-label={`Item ${item.title}`}>
    {item.title}
  </button>
</TableCell>
```

### Action Buttons with Roving Tabindex

```tsx
// Use roving tabindex: only focused element has tabindex="0"
<button
  tabIndex={isFocused ? 0 : -1}
  className='focus:ring-2 focus:ring-primary focus:ring-offset-2'
  aria-label={`Delete item ${item.name}`}
  onClick={handleDelete}
>
  <Trash2 aria-hidden='true' />
</button>
```

### Screen Reader Announcements

```tsx
function announceToScreenReader(message: string) {
  const liveRegion = document.getElementById('table-announcements');
  if (liveRegion) {
    liveRegion.textContent = message;
  }
}

// Use in handlers
await deleteItem(id);
announceToScreenReader('Item deleted successfully');
```

## Keyboard Shortcuts

Users should be able to use these keys:

| Key         | Action                          |
| ----------- | ------------------------------- |
| Tab         | Focus first cell in table       |
| ← / →       | Move left/right between columns |
| ↑ / ↓       | Move up/down between rows       |
| Home        | Jump to first column in row     |
| End         | Jump to last column in row      |
| Ctrl+Home   | Jump to first cell in table     |
| Ctrl+End    | Jump to last cell in table      |
| PageUp      | Move up 5 rows                  |
| PageDown    | Move down 5 rows                |
| Enter/Space | Activate item (if focusable)    |
| Escape      | Close any dialogs               |

## Testing Checklist

### Keyboard Navigation

- [ ] Can tab into table
- [ ] Arrow keys move between cells
- [ ] Home/End navigate columns
- [ ] Ctrl+Home/End jump to edges
- [ ] Focus indicator visible
- [ ] No keyboard traps

### Screen Readers

- [ ] Table is announced with label
- [ ] Column headers are announced
- [ ] Row numbers are announced
- [ ] Cell content is readable
- [ ] Sort state is announced
- [ ] Actions are announced

### Focus

- [ ] Focus visible on all interactive elements
- [ ] Focus indicator has sufficient contrast
- [ ] Focus order is logical
- [ ] Focus not lost when navigating

### Information

- [ ] No information by color alone
- [ ] Status has text + icon/color
- [ ] Priority has text + icon/color
- [ ] All buttons have labels
- [ ] Form inputs have labels

## Quick Command

Add to your component and you're done:

```tsx
// 1. Wrap table container
<div id='my-table' role='region' aria-label='Data table' aria-describedby='table-instructions'>
  {/* 2. Add instructions */}
  <div id='table-instructions' className='sr-only'>
    Use arrow keys to navigate table. Home and End keys jump to first and last columns.
  </div>

  {/* 3. Use accessible Table components */}
  <Table ariaLabel='Table label'>
    <TableHeader>
      <TableRow>
        <TableHead colIndex={1} isSortable>
          Column 1
        </TableHead>
        <TableHead colIndex={2}>Column 2</TableHead>
      </TableRow>
    </TableHeader>
    <TableBody>{/* rows */}</TableBody>
  </Table>

  {/* 4. Add live region */}
  <div
    id='table-announcements'
    role='status'
    aria-live='polite'
    aria-atomic='true'
    className='sr-only'
  />
</div>
```

## Common Issues

### Focus Not Working

- Check `containerId` matches div id
- Verify event listeners are attached
- Ensure elements have `tabIndex` set

### Screen Reader Not Announcing

- Verify live region exists with correct id
- Check role="status" and aria-live="polite"
- Ensure content is being set on the element

### Keyboard Navigation Not Working

- Verify table is focused first (Tab key)
- Check that elements have `data-col-index` and `data-row-index`
- Ensure keyboard handler is attached to correct element

### Focus Not Visible

- Add `focus:ring-2 focus:ring-primary` to element
- Verify CSS doesn't override focus styles
- Check that ring has sufficient contrast

## Resources

- Full Documentation: See `TABLE_ACCESSIBILITY.md`
- Examples: See `ItemsTableViewA11y.tsx`
- Tests: See `TableAccessibility.test.tsx`
- E2E Tests: See `table-accessibility.spec.ts`

## Support

For questions or issues:

1. Check the full documentation
2. Review example implementations
3. Run tests to verify setup
4. Test with actual keyboard and screen reader
