#!/usr/bin/env node

import assert from 'node:assert/strict'
import fs from 'node:fs'

const css = fs.readFileSync(new URL('../apps/web/src/components/Dashboard.css', import.meta.url), 'utf8')
const globalCss = fs.readFileSync(new URL('../apps/web/src/index.css', import.meta.url), 'utf8')
const nav = fs.readFileSync(new URL('../apps/web/src/components/TopNav.jsx', import.meta.url), 'utf8')
const nginx = fs.readFileSync(new URL('../deploy/nginx.local.conf', import.meta.url), 'utf8')

assert.match(css, /\.top-nav \.nav-item\s*\{[\s\S]*?min-height:\s*2\.75rem;/)
assert.match(css, /\.nav-item:focus-visible/)
assert.match(globalCss, /:focus-visible\s*\{[\s\S]*?outline:/, 'global focus indicator must be present')
for (const header of ['X-Content-Type-Options "nosniff"', 'X-Frame-Options "DENY"', 'Referrer-Policy "strict-origin-when-cross-origin"', 'Permissions-Policy "geolocation=(), microphone=(), camera=()"']) {
  assert.ok(nginx.includes(`add_header ${header}`), `${header} must be set by local nginx`)
}
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
assert.match(dashboard, /Existing values may be stale/, 'partial refreshes must disclose stale values')
assert.match(dashboard, /data-freshness/, 'dashboard must expose refresh freshness to assistive technology')
for (const [name, source] of [['TraceViewer', traceViewer], ['CoverageMatrix', coverageMatrix]]) {
  assert.match(source, /role="status" aria-live="polite"/, `${name} loading state must be announced politely`)
  assert.match(source, /role="alert"/, `${name} errors must be announced assertively`)
}

console.log('UI accessibility contract: PASS')
