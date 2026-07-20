#!/usr/bin/env node
import assert from 'node:assert/strict'

const raw = process.env.VITE_API_BASE || 'http://localhost:8080'
const allowInsecure = process.env.ALLOW_INSECURE_API_BASE === '1'
const url = new URL(raw)
const loopback = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)

assert.ok(['http:', 'https:'].includes(url.protocol), `unsupported API protocol: ${url.protocol}`)
if (url.protocol === 'http:' && !loopback && !allowInsecure) {
  throw new Error(
    `refusing insecure non-loopback API base ${raw}; use an HTTPS ingress or set ` +
      'ALLOW_INSECURE_API_BASE=1 only for isolated development',
  )
}

console.log(`PASS API base policy (${url.protocol}//${url.host})`)
