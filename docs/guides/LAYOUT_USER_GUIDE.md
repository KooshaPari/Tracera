# Graph Layout User Guide - Choosing the Right View

For requirements and traceability teams, choosing the right layout helps you understand your project better.

---

## Visual Overview

### 1. Flow Chart
**Icon**: 🔄

```
        [Requirement]
              ↓
          [Test Case]
              ↓
          [Release]
```

**When to use**:
- Understanding requirement workflow
- Tracing requirements through testing to release
- Finding dependencies
- New team members learning the process

**Benefits**:
- Clean, easy to follow
- Shows clear direction of flow
- Minimizes crossing lines
- Professional appearance

**Best for**: Most requirements and traceability work

---

### 2. Hierarchical
**Icon**: 🔗

```
    [Req A]    [Req B]    [Req C]
       ↓          ↓          ↓
    [Test]     [Test]     [Test]
       └────────┬────────┘
              ↓
        [Release]
```

**When to use**:
- Complex requirement dependencies
- Many-to-many relationships
- Where requirements merge together
- Multiple paths to same release

**Benefits**:
- Handles complex relationships
- Minimizes line crossings
- Highly configurable
- Professional engineering look

**Best for**: Complex enterprise requirements

---

### 3. Mind Map
**Icon**: 🧠

```
              [Central]
             /    |    \
        [Child] [Child] [Child]
         / | \   / | \   / | \
       ...
```

**When to use**:
- Brainstorming new requirements
- Understanding relationships
- Exploring a requirement family
- Knowledge organization

**Benefits**:
- Great for discovery
- Shows all relationships at once
- Intuitive (like mind mapping)
- Space-efficient

**Best for**: Initial planning, exploration, familiarization

---

### 4. Organic Network
**Icon**: 🌐

```
    [A] ──┐
   ╱│ \  │
 [B] [D][E]
  │╲   ╱│
  │ [C] │
  └─────┘
```

**When to use**:
- Discovering unexpected relationships
- Understanding overall structure
- Visual exploration
- Relationship validation

**Benefits**:
- Natural clustering
- Interesting to explore
- Reveals unexpected connections
- Relaxing to view

**Best for**: Exploratory analysis, discovery phase

---

### 5. Tree
**Icon**: 🌳

```
           [Root]
          /  |  \
        [A] [B] [C]
       /|\  /
     [D][E][F]
```

**When to use**:
- Single-root hierarchies
- Organizational structures
- Feature breakdowns
- Parent-child only relationships

**Benefits**:
- Simple and clean
- No cycles or branches
- Easy to understand
- Minimal visual complexity

**Best for**: Structured hierarchies, org charts, feature trees

---

### 6. Advanced Flow
**Icon**: ⚡

**When to use**:
- Enterprise-level complexity
- Multiple convergent paths
- Advanced cross-cutting dependencies
- Formal specification documents

**Benefits**:
- Most powerful layout
- Highly optimized
- Professional appearance
- Handles any structure

**Best for**: Enterprise requirements, regulatory compliance

---

## Choosing Your Layout

### Flow Chart vs Hierarchical

**Use Flow Chart if**:
- Requirements mostly follow a single path
- Dependencies are relatively simple
- First time viewing this project
- Team is non-technical

**Use Hierarchical if**:
- Many requirements feed into one release
- Cross-dependencies exist
- Team is technical
- Optimizing for complex visualization

---

### Exploratory vs Final

**Use Organic Network if**:
- You're in discovery/planning phase
- Looking for unexpected patterns
- First time exploring this dataset
- Validating structure

**Use Flow Chart/Hierarchical if**:
- Creating documentation
- Presenting to stakeholders
- Finalizing requirement structure
- Creating formal diagrams

---

### Organization Type

**Technical Teams** → Flow Chart or Hierarchical
**Non-Technical Stakeholders** → Flow Chart or Mind Map
**Mixed Teams** → Flow Chart (most universal)
**Executive Review** → Flow Chart (clearest)

---

## Keyboard Shortcuts (Coming Soon)

```
F     → Flow Chart layout
H     → Hierarchical layout
M     → Mind Map layout
O     → Organic layout
T     → Tree layout

+/-   → Zoom in/out
0     → Fit to screen
Space → Pan mode
```

---

## Troubleshooting

### "The diagram is too crowded"
**Solution**: Try "Organic Network" or increase zoom out

### "I can't see the flow"
**Solution**: Switch to "Flow Chart" for clearer direction

### "Dependencies look messy"
**Solution**: Try "Hierarchical" layout (best for complexity)

### "I want to understand structure"
**Solution**: Use "Mind Map" for relationship discovery

---

## Tips & Tricks

**Tip 1**: Start with Flow Chart, switch to other layouts to explore

**Tip 2**: Use Organic Network to find requirements with many dependencies

**Tip 3**: Mind Map works great for brainstorming sessions

**Tip 4**: Hover over nodes to see full requirement text

**Tip 5**: Double-click a requirement to see details in side panel

---

## Which Layout for Your Use Case?

| Use Case | Best Layout | Reason |
|---|---|---|
| Understanding a new project | Flow Chart | Simple, clear flow |
| Validating complex dependencies | Hierarchical | Minimizes visual clutter |
| Initial planning/brainstorm | Mind Map | Great for discovery |
| Finding related requirements | Organic | Natural clustering |
| Org structure | Tree | Single-root hierarchy |
| Compliance documentation | Hierarchical | Professional, optimized |
| Training new team member | Flow Chart | Easiest to understand |
| Performance analysis | Organic | See heavy nodes |
| Requirements review | Hierarchical | Clear dependencies |

---

## Common Questions

**Q: Can I save my layout preference?**
A: Yes! Your last used layout is remembered across sessions.

**Q: What if I switch layouts - will I lose my position?**
A: No, you can switch back and forth. Your work is saved.

**Q: Can I manually rearrange nodes?**
A: Yes! Click and drag any node to reposition it. Your changes are preserved.

**Q: How many requirements can I view at once?**
A: Comfortably 50-100. Use clustering for larger graphs (coming soon).

**Q: Can I print the diagram?**
A: Yes! Use your browser's print function. Flow Chart layout recommended for printing.

**Q: What if I want to save the diagram as an image?**
A: Right-click → Export as image (PNG, SVG available).

---

## Layout Algorithm Explanations (Technical Details)

For those interested in how each layout works:

### Flow Chart (Dagre Algorithm)
- Arranges nodes in layers
- Each layer is completely separate
- Edges always flow downward
- Minimizes edge crossings
- Very fast, deterministic

### Hierarchical (ELK Algorithm)
- More sophisticated than Flow Chart
- Allows complex routing
- Optimizes for readability
- Takes more time but looks better
- Industry standard for engineering

### Mind Map (Radial Layout)
- Places root in center
- Children in orbit around root
- Each orbit is a generation
- Good for hierarchies with many children
- Very intuitive

### Organic Network (Force-Directed)
- Physics simulation (like magnets and springs)
- Nodes repel each other
- Edges attract connected nodes
- Self-organizes naturally
- Non-deterministic (different each time)

### Tree (D3 Hierarchy)
- Optimized for pure trees
- No convergence paths
- Clean, minimal design
- Very fast
- Limited flexibility

### Advanced (ELK Advanced Routing)
- Like Hierarchical but with more options
- Multiple routing algorithms
- Port constraints
- For advanced users
- Slower but most powerful

---

## For Administrators

### Configuring Default Layout

**Setting 1: Default View**
```
Set system default to: Flow Chart
Users can override: Yes
Remember user preference: Yes
```

**Setting 2: Performance Mode**
For graphs > 500 requirements, auto-switch to:
```
Use: Hierarchical (ELK)
Reduce spacing: Yes
Clustering: Enable
```

**Setting 3: Large Graph Threshold**
```
Switch to clustering at: 300 requirements
Show warning at: 500 requirements
```

---

## Accessibility Notes

All layouts are designed for:
- Color-blind users (layout doesn't rely on color)
- Keyboard navigation (all functions accessible)
- Screen readers (proper labels)
- High-contrast mode support
- Zoom to at least 200%

---

## Related Documentation

- [Detailed Implementation Guide](LAYOUT_IMPLEMENTATION_GUIDE.md)
- [Technical Research](GRAPH_LAYOUT_RESEARCH.md)
- [Configuration Reference](LAYOUT_CONFIGURATION_REFERENCE.md)

---

## Quick Decision Tree

```
START
  │
  ├─ First time viewing? → USE: Flow Chart
  │
  ├─ Exploring relationships? → USE: Organic Network
  │
  ├─ Complex dependencies? → USE: Hierarchical
  │
  ├─ Learning structure? → USE: Mind Map
  │
  ├─ Parent-child only? → USE: Tree
  │
  └─ Enterprise complexity? → USE: Advanced
```

---

## Feedback

Have suggestions for layouts? Contact the product team with:
- Current layout you're using
- What you're trying to accomplish
- What's not working well
- Ideas for improvement

Your feedback shapes future layout options!
