# Tracera — Identity Demo Media (L105)

Animated SVG + MP4 showcasing the [Tracera teal-flowing-rhythm palette](../../assets/tokens.css) in motion.

## Files

| File | Purpose |
|---|---|
| `demo.svg` | 480×270 animated SVG — teal flow ribbon + traveling bead (looped CSS animation, ~5s) |
| `demo.mp4` | H.264/MP4 rendered from `demo.svg` via playwright + ffmpeg (24fps, 5s loop) |

## Palette (Tracera — teal flowing rhythm)

- Outer background `#0b1414` / `#102323`
- Teal accent `#14b8a6` (dominant — flow + bead)
- Off-white `#f6f8fa` (label)

## Animation

- Flow ribbon: 2.6s ease-in-out horizontal sway (currents)
- Bead: 2.6s linear translate across 480px with scale up/down (tracer dot)
- Label fade: synchronized 2.6s breathing

## Render command

```sh
python /tmp/svg2mp4.py demo.svg demo.mp4 480 270 24 5
```

## Source of truth

- Tokens: [`../../assets/tokens.css`](../../assets/tokens.css)
- Source icon: [`../../assets/brand/icon.svg`](../../assets/brand/icon.svg)
- Scorecard: `.claude/audit/.vision/L96-L107.md`