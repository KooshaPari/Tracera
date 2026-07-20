#!/usr/bin/env node

import assert from 'node:assert/strict'
import fs from 'node:fs'

const css = fs.readFileSync(new URL('../apps/web/src/components/Dashboard.css', import.meta.url), 'utf8')
const nav = fs.readFileSync(new URL('../apps/web/src/components/TopNav.jsx', import.meta.url), 'utf8')

assert.match(css, /\.top-nav \.nav-item\s*\{[\s\S]*?min-height:\s*2\.75rem;/)
assert.match(css, /\.nav-item:focus-visible/)
assert.match(nav, /<nav[^>]+aria-label=["']Primary navigation["']/)
assert.match(nav, /aria-current=\{current === page\.id \? ['"]page['"] : undefined\}/)
const dashboard = fs.readFileSync(new URL('../apps/web/src/components/Dashboard.jsx', import.meta.url), 'utf8')
const traceViewer = fs.readFileSync(new URL('../apps/web/src/components/TraceViewer.jsx', import.meta.url), 'utf8')
const coverageMatrix = fs.readFileSync(new URL('../apps/web/src/components/CoverageMatrix.jsx', import.meta.url), 'utf8')
const statusIcons = dashboard.match(/className="status-icon"/g) || []
assert.equal(statusIcons.length, 5, 'Dashboard should expose five status icon wrappers')
assert.equal(
  (dashboard.match(/className="status-icon" aria-hidden="true"/g) || []).length,
  5,
  'Dashboard status icons must be decorative to assistive technology',
)
for (const [name, source] of [['TraceViewer', traceViewer], ['CoverageMatrix', coverageMatrix]]) {
  assert.match(source, /role="status" aria-live="polite"/, `${name} loading state must be announced politely`)
  assert.match(source, /role="alert"/, `${name} errors must be announced assertively`)
}

console.log('UI accessibility contract: PASS')
