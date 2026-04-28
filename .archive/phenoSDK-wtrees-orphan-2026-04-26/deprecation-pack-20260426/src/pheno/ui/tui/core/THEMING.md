# Advanced Theming System

A comprehensive theming engine for TUI applications with CSS-like cascade, accessibility features, and WCAG compliance.

## Features

- **CSS-like Cascade**: Specificity-based style resolution (inline > id > class > element)
- **Accessibility**: High contrast, colorblind palettes, large text, reduced motion
- **WCAG Compliance**: Automatic contrast checking and color adjustment
- **Color Utilities**: Manipulation, blending, shade generation
- **Theme Inheritance**: Derive themes with overrides
- **Hot Reloading**: Dynamic theme switching
- **Performance**: Built-in caching for style resolution

## Quick Start

```python
from tui_kit.core.theming import (
    ThemeEngine,
    Theme,
    ColorPalette,
    AccessibilityMode,
)

# Create theme engine
engine = ThemeEngine()

# Create a theme from base color
theme = Theme(
    name="ocean",
    palette=ColorPalette.from_base_color("#0077be")
)

# Register and activate
engine.register_theme(theme)
engine.set_active_theme("ocean")

# Add cascade rules
engine.add_rule("button", {"color": "primary", "padding": "md"})
engine.add_rule("#submit", {"color": "success"})

# Resolve styles
styles = engine.resolve("button", id="submit")
# Result: {"color": "#4caf50", "padding": 16}
```

## Core Components

### 1. ThemeEngine

The main theme management system with CSS-like cascade resolution.

```python
engine = ThemeEngine()

# Register themes
engine.register_theme(my_theme)
engine.set_active_theme("my-theme")

# Add cascade rules (CSS-like selectors)
engine.add_rule("button", {"color": "primary"})        # Element
engine.add_rule(".primary-button", {"color": "info"})  # Class
engine.add_rule("#submit-btn", {"color": "success"})   # ID (highest priority)

# Resolve styles with specificity
styles = engine.resolve(
    "button",
    id="submit-btn",
    classes=["primary-button"]
)
# ID selector wins: color = success
```

#### Specificity Order

1. **Inline styles** (highest priority)
2. **ID selectors** (`#id`)
3. **Class selectors** (`.class`)
4. **Element selectors** (lowest priority)

### 2. Theme

Complete theme definition with palette, typography, spacing, and animations.

```python
theme = Theme(
    name="custom",
    palette=ColorPalette.from_base_color("#0178d4"),
    typography=TypographySettings(
        base_size=16,
        scale_ratio=1.25
    ),
    spacing=SpacingSettings(base_unit=8),
    animation=AnimationSettings(duration=200)
)
```

#### Theme Inheritance

```python
# Create base theme
base = Theme(name="base", palette=ColorPalette.from_base_color("#0178d4"))

# Derive with overrides
custom = base.derive(
    name="custom",
    palette={"accent": "#ff5722"}
)

print(custom.palette.primary)  # Inherited from base
print(custom.palette.accent)   # Overridden: #ff5722
```

### 3. ColorPalette

Comprehensive color system with semantic names and automatic shade generation.

```python
# Create from base color
palette = ColorPalette.from_base_color("#0178d4", dark_mode=False)

# Access semantic colors
print(palette.primary)      # Main brand color
print(palette.success)      # Success state
print(palette.error)        # Error state

# Access shades (50-900)
print(palette.primary_shades[100])  # Light
print(palette.primary_shades[500])  # Base
print(palette.primary_shades[900])  # Dark

# Convert modes
dark_palette = palette.to_dark_mode()
light_palette = palette.to_light_mode()
```

#### Automatic Palette Generation

The system automatically generates:
- Complementary secondary color
- Analogous accent color
- 9 shades for each semantic color
- 9 neutral gray shades

### 4. Color Utilities

Rich color manipulation with WCAG support.

```python
from tui_kit.core.theming import RGBColor, WCAGLevel

color = RGBColor.from_hex("#0178d4")

# Manipulation
lighter = color.lighten(0.2)      # Lighten by 20%
darker = color.darken(0.2)        # Darken by 20%
saturated = color.saturate(0.3)   # Increase saturation
desaturated = color.desaturate(0.3)
rotated = color.rotate_hue(180)   # Complementary color

# Blending
other = RGBColor.from_hex("#ff5722")
blended = color.blend(other, 0.5)  # 50% blend

# WCAG Contrast
bg = RGBColor.from_hex("#ffffff")
ratio = color.contrast_ratio(bg)
meets_aa = color.meets_wcag(bg, WCAGLevel.AA_NORMAL)
meets_aaa = color.meets_wcag(bg, WCAGLevel.AAA_NORMAL)
```

### 5. Accessibility

Built-in accessibility enhancements.

#### High Contrast Mode

```python
hc_theme = AccessibilityMode.apply_high_contrast(base_theme)
# - Pure black/white text
# - AAA contrast compliance
# - Animations disabled
```

#### Colorblind Palettes

```python
from tui_kit.core.theming import ColorBlindType

# Deuteranopia (green-blind)
cb_theme = AccessibilityMode.apply_colorblind_filter(
    base_theme,
    ColorBlindType.DEUTERANOPIA
)

# Available types:
# - PROTANOPIA (red-blind)
# - DEUTERANOPIA (green-blind)
# - TRITANOPIA (blue-blind)
# - ACHROMATOPSIA (total colorblind)
```

#### Large Text Mode

```python
large_text = AccessibilityMode.apply_large_text(
    base_theme,
    scale=1.5  # 150% larger
)
```

#### Reduced Motion

```python
reduced_motion = AccessibilityMode.apply_reduced_motion(base_theme)
# Disables all animations
```

### 6. WCAG Compliance

Automatic contrast checking and adjustment.

```python
palette = ColorPalette(
    background="#ffffff",
    text="#aaaaaa"  # Too light - won't pass AA
)

# Ensure compliance
compliant = palette.ensure_wcag_compliance(WCAGLevel.AA_NORMAL)
# Automatically adjusts text color to meet requirements
```

#### WCAG Levels

- **AA Normal**: 4.5:1 contrast (normal text)
- **AA Large**: 3.0:1 contrast (18pt+ text)
- **AAA Normal**: 7.0:1 contrast (enhanced)
- **AAA Large**: 4.5:1 contrast (18pt+ enhanced)

## Typography System

Type scale based on modular scale ratio.

```python
typography = TypographySettings(
    base_size=16,
    scale_ratio=1.25,  # Major third scale
    line_height=1.5,
    font_family="system-ui, sans-serif",
    font_weight=400
)

# Generated sizes
print(typography.sizes)
# {
#   'xs': 10,    # base / ratio^2
#   'sm': 13,    # base / ratio
#   'base': 16,  # base
#   'lg': 20,    # base * ratio
#   'xl': 25,    # base * ratio^2
#   '2xl': 31,   # base * ratio^3
#   '3xl': 39,   # base * ratio^4
#   '4xl': 49,   # base * ratio^5
# }
```

## Spacing System

8px grid-based spacing scale.

```python
spacing = SpacingSettings(base_unit=8)

# Generated scale
print(spacing.scale)
# {
#   'xs': 4,     # base / 2
#   'sm': 8,     # base
#   'md': 16,    # base * 2
#   'lg': 24,    # base * 3
#   'xl': 32,    # base * 4
#   '2xl': 48,   # base * 6
#   '3xl': 64,   # base * 8
#   '4xl': 96,   # base * 12
# }
```

## Animation System

Configurable animation settings with duration scale.

```python
animation = AnimationSettings(
    duration=200,          # Base duration in ms
    easing="ease-in-out",
    enabled=True
)

# Generated durations
print(animation.durations)
# {
#   'instant': 0,
#   'fast': 100,      # duration / 2
#   'normal': 200,    # duration
#   'slow': 400,      # duration * 2
#   'slower': 800,    # duration * 4
# }
```

## CSS Export

Export themes as CSS variables.

```python
engine = ThemeEngine()
engine.register_theme(my_theme)
engine.set_active_theme("my-theme")

css = engine.export_css()
# :root {
#   --primary: #0178d4;
#   --secondary: #666666;
#   --spacing-xs: 4px;
#   --spacing-sm: 8px;
#   --font-size-base: 16px;
#   ...
# }
```

## Hot Reloading

Update themes dynamically without restarting.

```python
# Add change listener
def on_theme_change(old_name, new_name):
    print(f"Theme changed: {old_name} -> {new_name}")

engine.add_theme_callback(on_theme_change)

# Hot reload updated theme
updated_theme = Theme(name="ocean", palette=new_palette)
engine.hot_reload_theme(updated_theme)
# Triggers callback and clears cache
```

## Performance

### Caching

Style resolution results are cached automatically:

```python
# First call - computed and cached
styles1 = engine.resolve("button", id="submit")

# Second call - retrieved from cache (instant)
styles2 = engine.resolve("button", id="submit")

# Cache is cleared on:
# - Theme changes
# - Rule additions
# - Hot reloads
```

## Best Practices

### 1. Use Semantic Colors

```python
# Good: Semantic meaning
engine.add_rule("button.danger", {"color": "error"})

# Avoid: Hard-coded values
engine.add_rule("button.danger", {"color": "#f44336"})
```

### 2. Use Spacing Scale

```python
# Good: Consistent spacing
engine.add_rule("button", {"padding": "md"})

# Avoid: Arbitrary values
engine.add_rule("button", {"padding": 15})
```

### 3. Ensure Accessibility

```python
# Always check contrast for custom colors
palette = my_palette.ensure_wcag_compliance(WCAGLevel.AA_NORMAL)

# Provide alternative themes
hc_theme = AccessibilityMode.apply_high_contrast(base_theme)
engine.register_theme(hc_theme)
```

### 4. Use Theme Inheritance

```python
# Create base themes
light_base = Theme(name="light-base", ...)
dark_base = Theme(name="dark-base", ...)

# Derive variations
blue_light = light_base.derive(name="blue-light", palette={"primary": "#0178d4"})
green_light = light_base.derive(name="green-light", palette={"primary": "#4caf50"})
```

## Examples

### Complete Example: Custom Theme with Accessibility

```python
from tui_kit.core.theming import (
    ThemeEngine,
    Theme,
    ColorPalette,
    WCAGLevel,
    AccessibilityMode,
    ColorBlindType,
)

# Create engine
engine = ThemeEngine()

# Create base theme
base_theme = Theme(
    name="my-app",
    palette=ColorPalette.from_base_color("#0178d4")
)

# Ensure WCAG compliance
base_theme.palette = base_theme.palette.ensure_wcag_compliance(
    WCAGLevel.AA_NORMAL
)

# Create accessibility variants
hc_theme = AccessibilityMode.apply_high_contrast(base_theme)
cb_theme = AccessibilityMode.apply_colorblind_filter(
    base_theme,
    ColorBlindType.DEUTERANOPIA
)
large_text_theme = AccessibilityMode.apply_large_text(base_theme)

# Register all themes
for theme in [base_theme, hc_theme, cb_theme, large_text_theme]:
    engine.register_theme(theme)

# Set active theme
engine.set_active_theme("my-app")

# Add cascade rules
engine.add_rule("button", {
    "color": "primary",
    "padding": "md",
    "font-size": "base",
})

engine.add_rule(".primary-button", {
    "font-weight": 600,
})

engine.add_rule("#submit-btn", {
    "color": "success",
})

# Resolve styles
styles = engine.resolve("button", id="submit-btn", classes=["primary-button"])
print(styles)
# {'color': '#4caf50', 'padding': 16, 'font-size': 16, 'font-weight': 600}

# Switch to high contrast
engine.set_active_theme("my-app-high-contrast")
```

## Accessibility Guidelines

### Color Contrast

- **Normal text**: Minimum 4.5:1 (AA), 7:1 (AAA)
- **Large text** (18pt+): Minimum 3:1 (AA), 4.5:1 (AAA)
- **UI components**: Minimum 3:1

### Colorblind Considerations

- Don't rely on color alone for information
- Use patterns, textures, or labels in addition to color
- Test with colorblind simulation tools
- Provide colorblind-friendly themes

### Motion Sensitivity

- Respect `prefers-reduced-motion`
- Provide option to disable animations
- Keep animations subtle and purposeful

### Large Text

- Support text scaling up to 200%
- Maintain layout at larger text sizes
- Use relative units (em, rem) not absolute (px)

## API Reference

### ThemeEngine

- `register_theme(theme)` - Register a theme
- `unregister_theme(name)` - Remove a theme
- `set_active_theme(name)` - Set active theme
- `get_active_theme()` - Get active theme
- `list_themes()` - List registered themes
- `add_rule(selector, properties, important)` - Add cascade rule
- `resolve(element, id, classes, inline_styles)` - Resolve styles
- `add_theme_callback(callback)` - Add change listener
- `hot_reload_theme(theme)` - Hot reload theme
- `export_css(theme_name)` - Export as CSS

### Theme

- `get_value(path, default)` - Get value by path
- `to_dict()` - Convert to dictionary
- `from_dict(data)` - Create from dictionary
- `derive(name, **overrides)` - Create derived theme

### ColorPalette

- `from_base_color(color, dark_mode)` - Generate from color
- `to_dark_mode()` - Convert to dark mode
- `to_light_mode()` - Convert to light mode
- `ensure_wcag_compliance(level)` - Ensure contrast

### RGBColor

- `from_hex(hex_color)` - Create from hex
- `to_hex()` - Convert to hex
- `to_hsl()` - Convert to HSL
- `from_hsl(h, s, l)` - Create from HSL
- `luminance()` - Calculate luminance
- `contrast_ratio(other)` - Calculate contrast
- `meets_wcag(background, level)` - Check WCAG
- `lighten(amount)` - Lighten color
- `darken(amount)` - Darken color
- `saturate(amount)` - Increase saturation
- `desaturate(amount)` - Decrease saturation
- `rotate_hue(degrees)` - Rotate hue
- `blend(other, amount)` - Blend colors

### AccessibilityMode

- `apply_high_contrast(theme)` - Apply high contrast
- `apply_colorblind_filter(theme, type)` - Apply colorblind palette
- `apply_large_text(theme, scale)` - Apply large text
- `apply_reduced_motion(theme)` - Apply reduced motion

## License

Part of the TUI Kit framework.
