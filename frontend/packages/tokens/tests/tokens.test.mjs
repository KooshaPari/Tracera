// ---------------------------------------------------------------------------
// WCAG 2.2 AA contrast ratio tests for all Tracera color pairs.
// Uses the WCAG relative luminance formula to compute contrast ratios.
// Requirements:
//   - Normal text (< 18pt / < 14pt bold):  ratio >= 4.5
//   - Large text (>= 18pt / >= 14pt bold): ratio >= 3.0
//   - UI components / graphical objects:    ratio >= 3.0
// ---------------------------------------------------------------------------

import { describe, it } from 'node:test';
import assert from 'node:assert/strict';

// ── Color definitions (mirrored from tokens.ts) ─────────────────────────

const neutral = {
  0:   '#ffffff',
  50:  '#f9fafb',
  100: '#f3f4f6',
  200: '#e5e7eb',
  300: '#d1d5db',
  400: '#9ca3af',
  500: '#6b7280',
  600: '#4b5563',
  700: '#374151',
  800: '#1f2937',
  900: '#111827',
  950: '#030712',
};

const semantic = {
  success: { DEFAULT: '#22c55e', dark: '#15803d', light: '#dcfce7' },
  warning: { DEFAULT: '#f59e0b', dark: '#b45309', light: '#fef3c7' },
  error:   { DEFAULT: '#ef4444', dark: '#b91c1c', light: '#fee2e2' },
  info:    { DEFAULT: '#0ea5e9', dark: '#0369a1', light: '#e0f2fe' },
};

// ── Luminance & contrast helpers ────────────────────────────────────────

function hexToRgb(hex) {
  const h = hex.replace('#', '');
  return [
    parseInt(h.slice(0, 2), 16),
    parseInt(h.slice(2, 4), 16),
    parseInt(h.slice(4, 6), 16),
  ];
}

function relativeLuminance([r, g, b]) {
  const [rs, gs, bs] = [r, g, b].map((c) => {
    const s = c / 255;
    return s <= 0.03928 ? s / 12.92 : Math.pow((s + 0.055) / 1.055, 2.4);
  });
  return 0.2126 * rs + 0.7152 * gs + 0.0722 * bs;
}

function contrastRatio(hex1, hex2) {
  const l1 = relativeLuminance(hexToRgb(hex1));
  const l2 = relativeLuminance(hexToRgb(hex2));
  const lighter = Math.max(l1, l2);
  const darker = Math.min(l1, l2);
  return (lighter + 0.05) / (darker + 0.05);
}

// ── Pairs to test ───────────────────────────────────────────────────────

const foregroundColors = {
  'primary-700':  '#1d4ed8',
  'primary-800':  '#1e40af',
  'primary-900':  '#1e3a8a',
  'neutral-900':  '#111827',
  'neutral-950':  '#030712',
  'error-dark':   '#b91c1c',
  'success-dark': '#15803d',
};

const backgroundColors = {
  'white':       '#ffffff',
  'neutral-50':  '#f9fafb',
  'neutral-100': '#f3f4f6',
  'success-light': '#dcfce7',
  'warning-light': '#fef3c7',
  'error-light':   '#fee2e2',
  'info-light':    '#e0f2fe',
};

// ── Tests ───────────────────────────────────────────────────────────────

describe('WCAG 2.2 AA contrast ratios', () => {
  describe('normal text — ratio >= 4.5', () => {
    for (const [fgName, fgColor] of Object.entries(foregroundColors)) {
      for (const [bgName, bgColor] of Object.entries(backgroundColors)) {
        it(`${fgName} on ${bgName}`, () => {
          const ratio = contrastRatio(fgColor, bgColor);
          assert.ok(
            ratio >= 4.5,
            `Contrast ratio ${ratio.toFixed(2)} is below 4.5 for ${fgName} on ${bgName}`,
          );
        });
      }
    }
  });

  describe('large text — ratio >= 3.0', () => {
    for (const [fgName, fgColor] of Object.entries(foregroundColors)) {
      for (const [bgName, bgColor] of Object.entries(backgroundColors)) {
        it(`${fgName} on ${bgName} (large)`, () => {
          const ratio = contrastRatio(fgColor, bgColor);
          assert.ok(
            ratio >= 3.0,
            `Contrast ratio ${ratio.toFixed(2)} is below 3.0 for ${fgName} on ${bgName} (large)`,
          );
        });
      }
    }
  });

  describe('inverted — dark backgrounds with light text', () => {
    const lightForegrounds = {
      'white':   '#ffffff',
      'neutral-50': '#f9fafb',
    };
    const darkBackgrounds = {
      'neutral-800': '#1f2937',
      'neutral-900': '#111827',
      'neutral-950': '#030712',
    };

    for (const [fgName, fgColor] of Object.entries(lightForegrounds)) {
      for (const [bgName, bgColor] of Object.entries(darkBackgrounds)) {
        it(`${fgName} on ${bgName}`, () => {
          const ratio = contrastRatio(fgColor, bgColor);
          assert.ok(
            ratio >= 4.5,
            `Contrast ratio ${ratio.toFixed(2)} is below 4.5 for ${fgName} on ${bgName}`,
          );
        });
      }
    }
  });

  describe('semantic status indicators — ratio >= 3.0 against white', () => {
    for (const [name, variant] of Object.entries(semantic)) {
      it(`${name}-DEFAULT on white`, () => {
        const ratio = contrastRatio(variant.DEFAULT, '#ffffff');
        assert.ok(
          ratio >= 3.0,
          `Semantic color ${name} DEFAULT contrast ${ratio.toFixed(2)} < 3.0 on white`,
        );
      });
      it(`${name}-dark on white`, () => {
        const ratio = contrastRatio(variant.dark, '#ffffff');
        assert.ok(
          ratio >= 3.0,
          `Semantic color ${name} dark contrast ${ratio.toFixed(2)} < 3.0 on white`,
        );
      });
    }
  });
});
