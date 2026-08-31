# 014 — Design Token System & WCAG 2.2 AA Compliance

| Field | Value |
|-------|-------|
| **Spec ID** | TRACERA-SPEC-014 |
| **Status** | Draft |
| **Version** | 2.0 |
| **Author** | Tracera Core Team |
| **Created** | 2026-08-30 |
| **Scope** | Design token architecture, WCAG 2.2 AA compliance, a11y testing, responsive policy |

---

## 1. Purpose

This specification defines the design token system for Tracera's frontend — a single source of truth for all visual design decisions. It enforces WCAG 2.2 AA compliance, mandates automated testing via axe-core, and describes the pipeline that compiles tokens into CSS custom properties.

---

## 2. Token Categories

### 2.1 Color

**Primitive tokens** — raw color values:

| Token | Value | Usage |
|-------|-------|-------|
| `color.blue.500` | `#3b82f6` | Brand blue |
| `color.gray.900` | `#111827` | Near-black |
| `color.red.600` | `#dc2626` | Error |
| `color.green.600` | `#16a34a` | Success |
| `color.white` | `#ffffff` | White |
| `color.black` | `#000000` | Black |

**Semantic tokens** — intent-based references:

| Token | Reference | Purpose |
|-------|-----------|---------|
| `color.bg.primary` | `color.white` | Page background |
| `color.bg.secondary` | `color.gray.50` | Card background |
| `color.text.primary` | `color.gray.900` | Body text |
| `color.text.secondary` | `color.gray.600` | Captions |
| `color.interactive.default` | `color.blue.500` | Buttons, links |
| `color.feedback.error` | `color.red.600` | Error states |
| `color.feedback.success` | `color.green.600` | Success states |

Dark mode inverts semantic mappings (e.g., `color.bg.primary` → `color.gray.900`).

### 2.2 Typography

**Font families:**

| Token | Value |
|-------|-------|
| `font.family.sans` | `"Inter", "Helvetica Neue", Arial, sans-serif` |
| `font.family.mono` | `"JetBrains Mono", "Fira Code", monospace` |

**Type scale** (1.250 Major Third ratio):

| Token | px | rem | Usage |
|-------|-----|-----|-------|
| `font.size.xs` | 12 | 0.75 | Fine print |
| `font.size.sm` | 14 | 0.875 | Secondary text |
| `font.size.md` | 16 | 1.000 | Body (base) |
| `font.size.lg` | 20 | 1.250 | Subheadings |
| `font.size.xl` | 25 | 1.5625 | Section headings |
| `font.size.2xl` | 31 | 1.9375 | Page titles |
| `font.size.3xl` | 39 | 2.4375 | Hero headings |
| `font.size.4xl` | 49 | 3.0625 | Display |

**Composite tokens:**

| Token | Weight | Size | Line-Height |
|-------|--------|------|-------------|
| `typography.body.md` | regular | md | normal |
| `typography.heading.lg` | semibold | lg | tight |
| `typography.label.md` | medium | sm | normal |

### 2.3 Spacing (4px grid)

| Token | px | rem |
|-------|-----|-----|
| `space.0` | 0 | 0 |
| `space.1` | 4 | 0.25 |
| `space.2` | 8 | 0.5 |
| `space.3` | 12 | 0.75 |
| `space.4` | 16 | 1.00 |
| `space.6` | 24 | 1.50 |
| `space.8` | 32 | 2.00 |
| `space.12` | 48 | 3.00 |
| `space.16` | 64 | 4.00 |

Components must reference spacing tokens exclusively — raw pixel values are prohibited.

### 2.4 Shadow & Elevation

| Token | Value |
|-------|-------|
| `shadow.xs` | `0 1px 2px rgba(0,0,0,0.05)` |
| `shadow.sm` | `0 1px 3px rgba(0,0,0,0.1)` |
| `shadow.md` | `0 4px 6px -1px rgba(0,0,0,0.1)` |
| `shadow.lg` | `0 10px 15px -3px rgba(0,0,0,0.1)` |
| `shadow.xl` | `0 20px 25px -5px rgba(0,0,0,0.1)` |

**Semantic elevation:**

| Token | Reference | Usage |
|-------|-----------|-------|
| `elevation.card` | `shadow.sm` | Cards, panels |
| `elevation.dropdown` | `shadow.lg` | Dropdowns, popovers |
| `elevation.modal` | `shadow.xl` | Modal dialogs |

### 2.5 Border & Radius

| Token | Value |
|-------|-------|
| `radius.none` | 0 |
| `radius.sm` | 4px |
| `radius.md` | 8px |
| `radius.lg` | 12px |
| `radius.full` | 9999px |

### 2.6 Motion & Easing

| Token | Value | Usage |
|-------|-------|-------|
| `motion.duration.immediate` | 50ms | Micro-interactions |
| `motion.duration.quick` | 100ms | Button states |
| `motion.duration.normal` | 200ms | Standard transitions |
| `motion.duration.moderate` | 300ms | Panel slides |
| `motion.easing.standard` | `cubic-bezier(0.2, 0, 0, 1)` | General transitions |
| `motion.easing.spring` | `cubic-bezier(0.34, 1.56, 0.64, 1)` | Playful overshoot |

**Reduced-motion policy:** When `prefers-reduced-motion: reduce` is active, all durations → `0ms`, easings → `linear`.

### 2.7 Breakpoints

| Token | Min-Width | Devices |
|-------|-----------|---------|
| `breakpoint.sm` | 640px | Large phones |
| `breakpoint.md` | 768px | Tablets |
| `breakpoint.lg` | 1024px | Small laptops |
| `breakpoint.xl` | 1280px | Desktops |
| `breakpoint.2xl` | 1536px | Large monitors |

### 2.8 Z-Index

| Token | Value | Usage |
|-------|-------|-------|
| `z.base` | 0 | Default |
| `z.dropdown` | 100 | Dropdowns |
| `z.sticky` | 200 | Sticky headers |
| `z.modal` | 400 | Modals |
| `z.toast` | 600 | Toasts |
| `z.tooltip` | 700 | Tooltips |

---

## 3. WCAG 2.2 AA Compliance

### 3.1 Contrast Ratios

| Criterion | Requirement |
|-----------|-------------|
| Normal text (< 24px) | ≥ 4.5:1 against background |
| Large text (≥ 24px or ≥ 18.66px bold) | ≥ 3:1 |
| UI components & graphical objects | ≥ 3:1 |

Every semantic color pair (`text` on `bg`) is validated during token generation. Failing pairs cause build failure. Dark mode pairs are tested independently.

### 3.2 Focus Indicators

| Requirement | Specification |
|-------------|--------------|
| Minimum area | 2px solid outline |
| Contrast ratio | ≥ 3:1 against adjacent + background |
| Offset | ≥ 2px |
| Token | `focus.ring` applied on `:focus-visible` |

### 3.3 Text Sizing

| Rule | Value |
|------|-------|
| Base font size | 16px (`font.size.md`) |
| Minimum body | 14px (`font.size.sm`) |
| Minimum caption | 12px (`font.size.xs`) |
| Resize support | All `rem` units; reflow at 200% zoom |
| Line length | 45–75 characters |
| Line height | ≥ 1.5× body, ≥ 1.2× headings |

### 3.4 Touch Targets

| Rule | Value |
|------|-------|
| Minimum size | 44×44 CSS pixels |
| Spacing between targets | ≥ 8px gap |
| Compact exceptions | Icons ≤ 24px in dense toolbars with ≥ 8px spacing |

---

## 4. axe-core Integration

### 4.1 Configuration

```ts
const config: axe.RunOptions = {
  runOnly: {
    type: 'tag',
    values: ['wcag2a', 'wcag2aa', 'wcag22aa', 'best-practice'],
  },
  rules: {
    'color-contrast': { enabled: true },
    'target-size': { enabled: true },
    'focus-order-semantics': { enabled: true },
    'label': { enabled: true },
    'button-name': { enabled: true },
    'image-alt': { enabled: true },
  },
};
```

### 4.2 Test Stages

| Stage | Scope | Blocking |
|-------|-------|----------|
| Unit (Storybook) | Component renderings | Yes |
| Integration (Playwright) | Full page compositions | Yes |
| Regression (CI) | Visual + a11y diff | Warning → Yes |
| Nightly (full crawl) | All routable pages | Report only |

### 4.3 Violation Handling

- **Critical / Serious**: Block merge.
- **Moderate**: Must have linked issue with assignee.
- **Minor / Best-practice**: Tracked, not blocking.

### 4.4 Custom axe Rules

| Rule ID | Description | Severity |
|---------|-------------|----------|
| `token-usage-color` | Flags raw hex/rgb in CSS | serious |
| `token-usage-spacing` | Flags raw px spacing | moderate |
| `token-usage-radius` | Flags raw border-radius | minor |
| `token-usage-shadow` | Flags raw box-shadow | minor |

---

## 5. Responsive Design Policy

- **Mobile-first**: styles for smallest viewport; breakpoints enhance progressively.
- **Fluid typography**: `font.size.sm` through `xl` use `clamp()` for smooth scaling.
- **Container queries** preferred over viewport queries for local responsive behavior.
- **Spacing adaptation**: scales by 50% below `breakpoint.md`; minimum unit is `space.1` (4px).

---

## 6. Token Generation Pipeline

### 6.1 Source Structure

```
tokens/
├── primitives/   (color.json, font.json, space.json, ...)
├── semantic/     (color.light.json, color.dark.json, ...)
├── component/    (button.json, input.json, ...)
└── index.json
```

### 6.2 Build Steps

1. **Validation** — parse + validate against DTCG schema.
2. **Contrast check** — test all semantic text/bg pairs.
3. **Transformation** — Style Dictionary compiles to targets.
4. **Output generation** — CSS, SCSS, TypeScript, JSON, docs.
5. **Diff check** — PR token diff with accessibility annotations.

### 6.3 Output Formats

| Artifact | Format | Consumers |
|----------|--------|-----------|
| CSS custom properties | `.css` | Browser, Storybook |
| TypeScript constants | `.ts` | Tests, SSR |
| JSON (resolved) | `.json` | Downstream tools |
| Documentation | `.md` | Token reference |

### 6.4 CSS Output

```css
::root {
  --color-blue-500: #3b82f6;
  --font-size-md: 1rem;
  --space-4: 1rem;
  --shadow-sm: 0 1px 3px rgba(0,0,0,0.1);
  --radius-md: 8px;
  --duration-normal: 200ms;
  --z-modal: 400;
}
[data-theme="dark"] {
  --color-bg-primary: var(--color-gray-900);
  --color-text-primary: var(--color-gray-50);
}
@media (prefers-reduced-motion: reduce) {
  :root {
    --duration-normal: 0ms;
    --easing-standard: linear;
  }
}
```

---

## 7. Acceptance Criteria

| # | Criterion |
|---|-----------|
| AC-01 | All 8 token categories defined with primitive + semantic layers |
| AC-02 | Spacing tokens exclusively multiples of 4px |
| AC-03 | Typography scale follows 1.250 ratio, xs through 4xl |
| AC-04 | CSS custom properties resolve in `:root`, dark, and reduced-motion |
| AC-05 | All text/bg pairs achieve ≥ 4.5:1 (normal) or ≥ 3:1 (large) |
| AC-06 | Every interactive element has visible focus with ≥ 3:1 contrast |
| AC-07 | No body text below 14px; no caption below 12px |
| AC-08 | All text uses `rem`; reflows at 200% zoom without horizontal scroll |
| AC-09 | Touch targets ≥ 44×44px on viewports < 768px |
| AC-10 | Adjacent interactive elements ≥ 8px spacing |
| AC-11 | axe-core runs on every PR (unit + integration stages) |
| AC-12 | Critical/Serious violations block PR merge |
| AC-13 | Custom token-usage axe rules enforced |
| AC-14 | Nightly crawl produces a11y report with no new Critical regressions |
| AC-15 | Token validation + contrast check completes in < 30 seconds |
| AC-16 | Generated CSS ≤ 8KB gzipped |
| AC-17 | Token diff reports include contrast impact annotations |

---

## Appendix A — Token Count Summary

| Category | Count | Prefix |
|----------|-------|--------|
| Color (primitives) | 60+ | `color.{hue}.{shade}` |
| Color (semantic) | 30+ | `color.{role}.{variant}` |
| Typography | 30+ | `font.*`, `typography.*` |
| Spacing | 15 | `space.{n}` |
| Shadow / Elevation | 13 | `shadow.*`, `elevation.*` |
| Border / Radius | 12 | `border.*`, `radius.*` |
| Motion / Easing | 12 | `motion.*` |
| Breakpoints | 10 | `breakpoint.*`, `container.*` |
| Z-Index | 10 | `z.*` |
| **Total** | **190+** | — |

## Appendix B — WCAG 2.2 References

| Criterion | Level | Relevance |
|-----------|-------|-----------|
| 1.4.3 Contrast (Minimum) | AA | Text contrast ratios |
| 1.4.4 Resize Text | AA | 200% zoom reflow |
| 1.4.10 Reflow | AA | No horizontal scroll at 320px |
| 2.4.7 Focus Visible | AA | Visible focus indicator |
| 2.4.11 Focus Not Obscured | AA (2.2) | Focus not hidden |
| 2.5.8 Target Size (Minimum) | AA (2.2) | 44×44px touch targets |

---

*End of Spec 014 — TRACERA-SPEC-014 v2.0*
