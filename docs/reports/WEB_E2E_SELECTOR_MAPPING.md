# E2E Test Selector Mapping

Complete mapping of old selectors to new selectors for graph.spec.ts and links.spec.ts

## Graph.spec.ts Selectors

### Graph Container

| Old Selector                      | New Selector  | Reason                                                |
| --------------------------------- | ------------- | ----------------------------------------------------- |
| `[data-testid="graph-container"]` | `.react-flow` | React Flow uses standard CSS class for main container |

### Graph Nodes

| Old Selector                 | New Selector                                    | Reason                                                  |
| ---------------------------- | ----------------------------------------------- | ------------------------------------------------------- |
| `[data-testid="graph-node"]` | `.react-flow .react-flow__nodes > div[data-id]` | React Flow renders nodes as divs with data-id attribute |
| `.cy-node`                   | (removed)                                       | Cytoscape not used - React Flow is library              |

### Graph Edges

| Old Selector                 | New Selector             | Reason                                         |
| ---------------------------- | ------------------------ | ---------------------------------------------- |
| `[data-testid="graph-edge"]` | `.react-flow__edges > g` | React Flow renders edges as SVG group elements |
| `.cy-edge`                   | (removed)                | Cytoscape not used - React Flow is library     |

### Zoom Controls

| Old Selector                                    | New Selector                           | Reason                                  |
| ----------------------------------------------- | -------------------------------------- | --------------------------------------- |
| `getByRole("button", { name: /zoom in/i })`     | `.react-flow__controls button` (nth 0) | React Flow controls are ordered buttons |
| `getByRole("button", { name: /zoom out/i })`    | `.react-flow__controls button` (nth 1) |                                         |
| `getByRole("button", { name: /fit\|center/i })` | `.react-flow__controls button` (nth 2) |                                         |
| `getByRole("button", { name: /reset/i })`       | `.react-flow__controls button` (nth 3) |                                         |

### Node Details

| Old Selector                   | New Selector          | Reason                                  |
| ------------------------------ | --------------------- | --------------------------------------- |
| `[data-testid="node-details"]` | `.w-96` (with filter) | Details panel uses Tailwind width class |
| `[class*="selected\|active"]`  | (removed)             | Node selection is visual only           |

### Mini-map

| Old Selector                    | New Selector           | Reason                                  |
| ------------------------------- | ---------------------- | --------------------------------------- |
| `[data-testid="graph-minimap"]` | `.react-flow__minimap` | React Flow mini-map uses standard class |

### Layout Selector

| Old Selector                               | New Selector              | Reason                                       |
| ------------------------------------------ | ------------------------- | -------------------------------------------- |
| `getByRole("button", { name: /layout/i })` | `button` filtered by text | Layout selector is a custom Select component |

### Node Tooltips

| Old Selector           | New Selector | Reason                                    |
| ---------------------- | ------------ | ----------------------------------------- |
| `getByRole("tooltip")` | (kept)       | Radix UI tooltips work with role selector |

### Path Highlighting

| Old Selector                       | New Selector | Reason                                        |
| ---------------------------------- | ------------ | --------------------------------------------- |
| `[data-testid="highlighted-path"]` | (removed)    | Feature optional - visual verification needed |

## Links.spec.ts Selectors

### Item Navigation

| Old Selector                                          | New Selector                                   | Reason                               |
| ----------------------------------------------------- | ---------------------------------------------- | ------------------------------------ |
| `[data-testid="item-row"]`                            | `a` filtered by text                           | Items list uses semantic anchor tags |
| `getByRole("link", { name: /user authentication/i })` | `locator("a").filter({ hasText: /pattern/i })` | More flexible text matching          |

### Links Tab

| Old Selector       | New Selector                           | Reason                         |
| ------------------ | -------------------------------------- | ------------------------------ |
| (implicit in form) | `getByRole("tab", { name: /links/i })` | Item detail uses Radix UI tabs |

### Link Sections

| Old Selector          | New Selector                                            | Reason                                 |
| --------------------- | ------------------------------------------------------- | -------------------------------------- |
| (no heading selector) | `getByRole("heading", { name: /outgoing\|incoming/i })` | Tab content has clear section headings |

### Link Items

| Old Selector           | New Selector                     | Reason                                 |
| ---------------------- | -------------------------------- | -------------------------------------- |
| (custom div structure) | `div` with text containing `/→/` | Link items show source → target format |

### Link Forms

| Old Selector                         | New Selector | Reason                           |
| ------------------------------------ | ------------ | -------------------------------- |
| `getByLabel(/target item\|target/i)` | (kept as is) | Form labels work with getByLabel |
| `getByLabel(/link type\|type/i)`     | (kept as is) |                                  |

### Graph Edge Labels

| Old Selector  | New Selector              | Reason                                         |
| ------------- | ------------------------- | ---------------------------------------------- |
| (no selector) | `.react-flow__edge-label` | React Flow renders edge labels with this class |

### Delete Buttons

| Old Selector                                       | New Selector | Reason                           |
| -------------------------------------------------- | ------------ | -------------------------------- |
| `getByRole("button", { name: /delete\|remove/i })` | (kept as is) | Delete buttons use semantic role |

## React Flow CSS Classes

All React Flow internal classes:

```css
/* Container */
.react-flow                 /* Main container */
.react-flow__viewport       /* Viewport/transform container */

/* Nodes */
.react-flow__nodes          /* Nodes container */
.react-flow__node           /* Individual node */
.react-flow__node-{type}    /* Node type specific */

/* Edges */
.react-flow__edges          /* Edges SVG container */
.react-flow__edge           /* Individual edge group */
.react-flow__edge-label     /* Edge label text */

/* Handles */
.react-flow__handle         /* Connection points */
.react-flow__handle-{position}  /* Position specific */

/* Controls */
.react-flow__controls       /* Controls container */
.react-flow__controls-button /* Individual buttons */
.react-flow__zoom-in        /* Zoom in button */
.react-flow__zoom-out       /* Zoom out button */
.react-flow__fit-view       /* Fit view button */

/* Mini-map */
.react-flow__minimap        /* Mini-map container */
.react-flow__minimap-canvas /* Canvas element */

/* Background */
.react-flow__background     /* Background container */
.react-flow__background-pattern /* Pattern element */

/* Viewport Classes */
.react-flow__nodes          /* Nodes wrapper */
.react-flow__edges          /* Edges wrapper */

/* Pane Classes */
.react-flow__pane           /* Pane container */
.react-flow__selection      /* Selection rect */
.react-flow__edges-wrapper  /* Edges wrapper */
.react-flow__nodes-wrapper  /* Nodes wrapper */
```

## Selection Strategy

### Recommended Order of Selectors

1. **First Choice**: Use CSS class selectors from React Flow
2. **Second Choice**: Use semantic HTML roles (button, link, heading, tab)
3. **Third Choice**: Use text content with `filter({ hasText: /pattern/i })`
4. **Fourth Choice**: Use data attributes if available
5. **Last Resort**: Complex XPath expressions

### Example Patterns

```typescript
// Pattern 1: CSS class selection
page.locator('.react-flow__nodes > div[data-id]');

// Pattern 2: Role-based selection
page.getByRole('tab', { name: /links/i });

// Pattern 3: Text filtering
page.locator('a').filter({ hasText: /item|requirement/i });

// Pattern 4: Combination
page.locator('.w-96').filter({ hasText: /incoming|outgoing/ });
```

## Notes

- All selectors are modern and compatible with Playwright
- Tests use graceful degradation with `.catch()` for optional features
- CSS selectors are more stable than text-based selectors
- Roles are preferred over data-testid when semantically appropriate
- Text filters should use case-insensitive regex patterns
