# Core Components Quick Reference

## Import

```python
from tui_kit.core.components import (
    # Base classes
    BaseWidget,
    BaseContainer,
    BaseLayout,

    # Layouts
    FlexLayout,
    GridLayoutManager,

    # Systems
    LifecycleState,
    StateManager,
    EventBus,
    PluginProtocol,

    # Utilities
    SizeConstraint,
    StateTransition,
    LayoutPosition,
)
```

## Lifecycle States

```
CREATED → MOUNTING → MOUNTED → SHOWING ⇄ HIDING → UNMOUNTING → UNMOUNTED
```

## BaseWidget Quick Start

```python
class MyWidget(BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        # State management
        self.state.set("value", 0)
        self.state.observe("value", self._on_value_change)

        # Event handling
        self.events.subscribe("update", self._on_update)

    def _on_value_change(self, old, new):
        """Called when 'value' state changes."""
        self.refresh()

    def _on_update(self, data):
        """Handle 'update' event."""
        self.state.set("value", data)

    # Lifecycle hooks (always call super() first/last)
    def on_mount(self) -> None:
        super().on_mount()  # FIRST
        # Initialize

    def on_show(self) -> None:
        super().on_show()  # FIRST
        # Start updates

    def on_hide(self) -> None:
        super().on_hide()  # FIRST
        # Pause updates

    def on_resize(self, size: Size) -> None:
        super().on_resize(size)  # FIRST
        # Handle responsive behavior

    def on_unmount(self) -> None:
        # Cleanup
        super().on_unmount()  # LAST
```

## BaseContainer Quick Start

```python
class Panel(BaseContainer):
    def __init__(self, **kwargs):
        # Set layout
        layout = FlexLayout(direction="column", gap=1)
        super().__init__(layout=layout, **kwargs)

    def on_mount(self) -> None:
        super().on_mount()

        # Add children
        self.add_child(HeaderWidget(), z_index=100)
        self.add_child(ContentWidget(), z_index=0)

        # Set constraints
        self.layout.set_constraint(
            self.children[0],
            SizeConstraint(min_height=3, max_height=3)
        )
```

## Plugin Quick Start

```python
class MyPlugin(PluginProtocol):
    def on_mount(self, widget: BaseWidget) -> None:
        print(f"{widget.id} mounted")

    def on_show(self, widget: BaseWidget) -> None:
        print(f"{widget.id} shown")

    def on_hide(self, widget: BaseWidget) -> None:
        print(f"{widget.id} hidden")

    def on_resize(self, widget: BaseWidget, size: Size) -> None:
        print(f"{widget.id} resized to {size.width}x{size.height}")

    def on_unmount(self, widget: BaseWidget) -> None:
        print(f"{widget.id} unmounted")

# Use plugin
widget = MyWidget()
widget.add_plugin(MyPlugin())
```

## State Management

```python
# Set state
widget.state.set("key", "value")

# Get state
value = widget.state.get("key", default=None)

# Observe changes
def observer(old_value, new_value):
    print(f"{old_value} → {new_value}")

widget.state.observe("key", observer)

# Batch update
widget.state.update({
    "key1": "value1",
    "key2": "value2",
})
```

## Event Bus

```python
# Subscribe
def handler(data):
    print(f"Received: {data}")

widget.events.subscribe("my_event", handler)

# Publish
widget.events.publish("my_event", {"value": 42})

# Unsubscribe
widget.events.unsubscribe("my_event", handler)

# Propagate to children
container.propagate_event("update", data)
```

## Layouts

### FlexLayout

```python
# Horizontal
layout = FlexLayout(direction="row", gap=2)

# Vertical
layout = FlexLayout(direction="column", gap=1)

container.set_layout(layout)
```

### GridLayoutManager

```python
layout = GridLayoutManager(rows=3, cols=3, gap=1)
container.set_layout(layout)
```

### Size Constraints

```python
constraint = SizeConstraint(
    min_width=20,
    max_width=100,
    min_height=10,
    max_height=50,
    aspect_ratio=16/9,
)

layout.set_constraint(widget, constraint)
```

## Lifecycle Hook Registration

```python
def custom_mount_hook(widget):
    print(f"{widget.id} is mounting!")

widget.register_hook("mount", custom_mount_hook)
widget.register_hook("show", lambda w: print("Showing!"))
widget.register_hook("resize", lambda w, s: print(f"Size: {s}"))
```

## Best Practices

1. **Always call super()** in lifecycle methods
2. **Use state** for reactive values
3. **Use events** for decoupled communication
4. **Use plugins** for cross-cutting concerns
5. **Validate transitions** automatically handled
6. **Clean up** in `on_unmount()`

## Common Patterns

### Counter Widget

```python
class Counter(BaseWidget):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.state.set("count", 0)
        self.events.subscribe("increment", self._increment)

    def _increment(self):
        self.state.set("count", self.state.get("count") + 1)
```

### Dashboard Container

```python
class Dashboard(BaseContainer):
    def __init__(self, **kwargs):
        super().__init__(
            layout=GridLayoutManager(rows=2, cols=2, gap=1),
            **kwargs
        )

    def on_mount(self) -> None:
        super().on_mount()
        for i in range(4):
            self.add_child(PanelWidget(f"Panel {i+1}"))
```

### Logging Plugin

```python
class Logger(PluginProtocol):
    def on_mount(self, w): print(f"✓ {w.id} mounted")
    def on_show(self, w): print(f"👁 {w.id} shown")
    def on_hide(self, w): print(f"🙈 {w.id} hidden")
    def on_resize(self, w, s): print(f"📐 {w.id}: {s}")
    def on_unmount(self, w): print(f"✗ {w.id} unmounted")
```

## Error Handling

All lifecycle hooks, plugins, and observers have isolated error handling:

```python
# Plugin errors won't crash widget
plugin.on_mount(widget)  # Error logged, execution continues

# Observer errors won't crash state updates
state.set("key", "value")  # Observers called, errors logged

# Event handler errors won't crash publishing
events.publish("event", data)  # All handlers called, errors logged
```

## Debugging

```python
# Get state history
history = widget.get_state_history()
for transition in history:
    print(f"{transition.from_state.name} → {transition.to_state.name}")

# Check current state
print(f"State: {widget.lifecycle_state.name}")

# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

---

**Full Documentation:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit/COMPONENTS_GUIDE.md`

**Module Path:** `/Users/kooshapari/temp-PRODVERCEL/485/kush/pheno-sdk/tui-kit/tui_kit/core/components.py`
