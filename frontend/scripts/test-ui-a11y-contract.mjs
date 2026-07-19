#!/usr/bin/env node

import assert from 'node:assert/strict'
import fs from 'node:fs'

const css = fs.readFileSync(new URL('../apps/web/src/components/Dashboard.css', import.meta.url), 'utf8')
const nav = fs.readFileSync(new URL('../apps/web/src/components/TopNav.jsx', import.meta.url), 'utf8')

assert.match(css, /\.top-nav \.nav-item\s*\{[\s\S]*?min-height:\s*2\.75rem;/)
assert.match(css, /\.nav-item:focus-visible/)
assert.match(nav, /<nav[^>]+aria-label=["']Primary navigation["']/)
assert.match(nav, /aria-current=\{current === page\.id \? ['"]page['"] : undefined\}/)

console.log('UI accessibility contract: PASS')
