#!/usr/bin/env node

import assert from 'node:assert/strict'
import fs from 'node:fs'

const read = (path) => fs.readFileSync(new URL(path, import.meta.url), 'utf8')
const globalCss = read('../apps/web/src/index.css')
const layout = read('../apps/web/src/components/layout/Layout.tsx')
const header = read('../apps/web/src/components/layout/Header.tsx')
const sidebar = read('../apps/web/src/components/layout/sidebar-view.tsx')
const apiView = read('../apps/web/src/pages/projects/views/ApiView.tsx')
const documentationView = read('../apps/web/src/pages/projects/views/DocumentationView.tsx')
const flowGraph = read('../apps/web/src/components/graph/FlowGraphView.tsx')
const nginx = read('../deploy/nginx.local.conf')

assert.match(globalCss, /:focus-visible[\s\S]*outline:/, 'global focus indicator must be present')
assert.match(globalCss, /prefers-reduced-motion: reduce/, 'reduced-motion support must be present')
assert.match(layout, /id='skip-to-main'/, 'layout must expose a skip link')
assert.match(layout, /id='main-content'/, 'layout must expose the main content target')
assert.match(header, /role='banner'/, 'header must expose banner landmark')
assert.match(sidebar, /<nav[^>]+aria-label='Main navigation'/, 'sidebar must expose navigation landmark')
assert.match(sidebar, /aria-label='Search navigation items'/, 'sidebar search must be labelled')
assert.match(apiView, /aria-label=\{`Copy \$\{endpoint\.method\}/, 'API copy controls must be labelled')
assert.match(apiView, /aria-label=\{`Try \$\{endpoint\.method\}/, 'API try controls must be labelled')
for (const label of ['Preview documentation', 'Edit documentation', 'Open documentation']) {
  assert.match(documentationView, new RegExp(`aria-label='${label}'`), `${label} control must be labelled`)
}
for (const label of ['Graph layout selection', 'Zoom in', 'Zoom out', 'Fit view to content']) {
  assert.match(flowGraph, new RegExp(`aria-label='${label}'`), `${label} control must be labelled`)
}
for (const header of ['X-Content-Type-Options "nosniff"', 'X-Frame-Options "DENY"', 'Referrer-Policy "strict-origin-when-cross-origin"', 'Permissions-Policy "geolocation=(), microphone=(), camera=()"']) {
  assert.ok(nginx.includes(`add_header ${header}`), `${header} must be set by local nginx`)
}

console.log('UI accessibility contract: PASS')
