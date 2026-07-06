# Tracera Brand

**AI-CODED, not AI-generated.** Keycap family — midnight `#090a0c` + teal `#7ebab5` with indigo
accent. Vision-pillar L96 ships the static icon set; L101 ships the animated motion variant.

## The mark

Hexagonal trace-link matrix with a central requirement diamond — the requirement-graph view of
Tracera in a single glyph.

## Files

| File | Purpose |
|------|---------|
| `icon.svg` | Source of truth — static, hand-coded vector |
| `icon-animated.svg` | L101 motion variant — SMIL teal wave + breathing core (no JavaScript) |
| `favicon.svg` | Tab favicon (smaller variant) |

## Regenerating

Static raster exports derive from the SVG via the repo's brand-export script.

## Motion variant (L101)

`icon-animated.svg` ships a 4-second loop:

- The teal→indigo gradient on the outer hexagon flows horizontally (`<animate>` on stop offsets).
- The central requirement diamond breathes (scale 1 → 1.08 → 1).
- Loop is seamless: last frame == first frame.

All animation is SVG-native SMIL — no JavaScript, no external CSS. Safe to inline in HTML, SVG
`<img src>`, README previews, and the Tracera desktop splash (Electrobun).