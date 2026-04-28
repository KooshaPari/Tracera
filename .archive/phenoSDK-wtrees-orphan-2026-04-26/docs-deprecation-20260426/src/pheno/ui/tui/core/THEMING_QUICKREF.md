# Theming System - Quick Reference

## Import

```python
from tui_kit.core.theming import (
    ThemeEngine, Theme, ColorPalette, RGBColor, WCAGLevel,
    AccessibilityMode, ColorBlindType,
    DEFAULT_LIGHT_THEME, DEFAULT_DARK_THEME
)
```

## Basic Usage

```python
# 1. Create engine
engine = ThemeEngine()

# 2. Create theme
theme = Theme(
    name="my-theme",
    palette=ColorPalette.from_base_color("#0178d4")
)

# 3. Register and activate
engine.register_theme(theme)
engine.set_active_theme("my-theme")

# 4. Add rules
engine.add_rule("button", {"color": "primary", "padding": "md"})
engine.add_rule("#submit", {"color": "success"})  # Higher priority

# 5. Resolve styles
styles = engine.resolve("button", id="submit")
# Result: {"color": "#4caf50", "padding": 16}
```

## Cascade Specificity (CSS-like)

1. **Inline styles** - Highest priority
2. **#id** - High priority
3. **.class** - Medium priority
4. **element** - Low priority

```python
engine.add_rule("button", {"color": "primary"})         # 1. element
engine.add_rule(".primary-button", {"color": "info"})   # 2. class (overrides)
engine.add_rule("#submit-btn", {"color": "success"})    # 3. id (wins!)

styles = engine.resolve("button", id="submit-btn", classes=["primary-button"])
# color = "success" (id has highest specificity)
```

## Color Palette

### Semantic Colors
- `primary` - Main brand color
- `secondary` - Secondary brand color
- `accent` - Accent/highlight
- `success` - Success states
- `warning` - Warning states
- `error` - Error states
- `info` - Info states

### Shades (50-900)
```python
palette.primary_shades[100]  # Very light
palette.primary_shades[500]  # Base color
palette.primary_shades[900]  # Very dark
```

### Create Palette
```python
# From base color
light = ColorPalette.from_base_color("#0178d4", dark_mode=False)
dark = ColorPalette.from_base_color("#0178d4", dark_mode=True)

# Convert modes
dark_mode = light.to_dark_mode()
light_mode = dark.to_light_mode()
```

## Color Manipulation

```python
color = RGBColor.from_hex("#0178d4")

# Adjust lightness
lighter = color.lighten(0.2)      # +20% lighter
darker = color.darken(0.2)        # +20% darker

# Adjust saturation
saturated = color.saturate(0.3)   # +30% saturation
desaturated = color.desaturate(0.3)

# Hue rotation
complementary = color.rotate_hue(180)  # Opposite color
analogous = color.rotate_hue(30)       # Adjacent color

# Blending
other = RGBColor.from_hex("#ff5722")
mixed = color.blend(other, 0.5)   # 50/50 blend
```

## WCAG Contrast

```python
text = RGBColor.from_hex("#666666")
bg = RGBColor.from_hex("#ffffff")

# Check contrast
ratio = text.contrast_ratio(bg)
meets_aa = text.meets_wcag(bg, WCAGLevel.AA_NORMAL)    # 4.5:1
meets_aaa = text.meets_wcag(bg, WCAGLevel.AAA_NORMAL)  # 7:1

# Auto-fix
palette = ColorPalette(text="#999999", background="#ffffff")
compliant = palette.ensure_wcag_compliance(WCAGLevel.AA_NORMAL)
```

### WCAG Levels
- `WCAGLevel.AA_NORMAL` - 4.5:1 (normal text)
- `WCAGLevel.AA_LARGE` - 3.0:1 (18pt+ text)
- `WCAGLevel.AAA_NORMAL` - 7.0:1 (enhanced)
- `WCAGLevel.AAA_LARGE` - 4.5:1 (18pt+ enhanced)

## Accessibility

### High Contrast
```python
hc_theme = AccessibilityMode.apply_high_contrast(base_theme)
# - Pure black/white text
# - AAA contrast
# - Animations disabled
```

### Colorblind Palettes
```python
cb_theme = AccessibilityMode.apply_colorblind_filter(
    base_theme,
    ColorBlindType.DEUTERANOPIA  # Green-blind
)

# Types: PROTANOPIA, DEUTERANOPIA, TRITANOPIA, ACHROMATOPSIA
```

### Large Text
```python
large = AccessibilityMode.apply_large_text(base_theme, scale=1.5)
# 150% larger text
```

### Reduced Motion
```python
reduced = AccessibilityMode.apply_reduced_motion(base_theme)
# Disables all animations
```

## Typography

```python
from tui_kit.core.theming import TypographySettings

typography = TypographySettings(
    base_size=16,
    scale_ratio=1.25,  # Major third
    line_height=1.5
)

# Sizes: xs, sm, base, lg, xl, 2xl, 3xl, 4xl
print(typography.sizes['xl'])  # 25px
```

## Spacing

```python
from tui_kit.core.theming import SpacingSettings

spacing = SpacingSettings(base_unit=8)

# Scale: xs, sm, md, lg, xl, 2xl, 3xl, 4xl
print(spacing.scale['md'])  # 16px
```

## Theme Inheritance

```python
# Base theme
base = Theme(name="base", palette=ColorPalette.from_base_color("#0178d4"))

# Derive with overrides
custom = base.derive(
    name="custom",
    palette={"accent": "#ff5722"}  # Override accent only
)

# Access inherited values
print(custom.palette.primary)  # From base
print(custom.palette.accent)   # Overridden
print(custom.parent.name)      # "base"
```

## Hot Reloading

```python
# Add change listener
def on_theme_change(old, new):
    print(f"Theme changed: {old} -> {new}")

engine.add_theme_callback(on_theme_change)

# Hot reload
updated = Theme(name="my-theme", palette=new_palette)
engine.hot_reload_theme(updated)  # Triggers callback
```

## CSS Export

```python
css = engine.export_css("my-theme")
# :root {
#   --primary: #0178d4;
#   --secondary: #666666;
#   --spacing-md: 16px;
#   --font-size-base: 16px;
#   ...
# }
```

## Common Patterns

### Multi-Theme Support
```python
# Register multiple themes
themes = [
    Theme(name="light", palette=ColorPalette.from_base_color("#0178d4", dark_mode=False)),
    Theme(name="dark", palette=ColorPalette.from_base_color("#0178d4", dark_mode=True)),
    AccessibilityMode.apply_high_contrast(light_theme),
]

for theme in themes:
    engine.register_theme(theme)

# Switch dynamically
engine.set_active_theme("dark")
```

### Component Styling
```python
# Define component styles
engine.add_rule("input", {
    "color": "text",
    "background": "surface",
    "padding": "sm",
    "border-radius": 4,
})

engine.add_rule("input.error", {
    "color": "error",
    "border-color": "error",
})

engine.add_rule("input:focus", {
    "border-color": "primary",
})

# Resolve for state
normal_input = engine.resolve("input")
error_input = engine.resolve("input", classes=["error"])
```

### Responsive Theming
```python
# Create size variants
compact = base_theme.derive(
    name="compact",
    spacing={"base_unit": 4},
    typography={"base_size": 14}
)

comfortable = base_theme.derive(
    name="comfortable",
    spacing={"base_unit": 12},
    typography={"base_size": 18}
)
```

## Performance Tips

- Styles are cached automatically
- Cache cleared on theme change, rule addition, or hot reload
- Reuse theme objects when possible
- Use semantic color names instead of hex values

## Cheat Sheet

| Task | Code |
|------|------|
| Create theme | `Theme(name="x", palette=ColorPalette.from_base_color("#..."))` |
| Add rule | `engine.add_rule("element", {"prop": "value"})` |
| Resolve styles | `engine.resolve("element", id="x", classes=["y"])` |
| Lighten color | `color.lighten(0.2)` |
| Check contrast | `color.meets_wcag(bg, WCAGLevel.AA_NORMAL)` |
| High contrast | `AccessibilityMode.apply_high_contrast(theme)` |
| Colorblind | `AccessibilityMode.apply_colorblind_filter(theme, type)` |
| Derive theme | `base.derive(name="x", palette={"primary": "#..."})` |
| Export CSS | `engine.export_css("theme-name")` |
