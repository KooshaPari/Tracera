# Application Icons

This directory should contain application icons for different platforms.

## Required Icons

### macOS
- `icon.icns` - macOS app icon (512x512 and other sizes)

### Windows
- `icon.ico` - Windows app icon (256x256 with multiple sizes)

### Linux/Universal
- `32x32.png` - Small icon
- `128x128.png` - Medium icon
- `128x128@2x.png` - High DPI medium icon
- `icon.png` - Large icon (512x512 or 1024x1024)

## Generating Icons

You can use the Tauri icon generator:

```bash
npm install --save-dev @tauri-apps/cli

# Generate all icons from a single 1024x1024 PNG
npm run tauri icon path/to/icon.png
```

This will automatically generate all required icon formats.

## Icon Requirements

- **Source Image**: 1024x1024 PNG with transparency
- **Format**: PNG with transparent background
- **Content**: Should be recognizable at small sizes (32x32)
- **Safe Area**: Keep important elements within center 80%

## Placeholder

Until custom icons are created, Tauri will use default icons.
