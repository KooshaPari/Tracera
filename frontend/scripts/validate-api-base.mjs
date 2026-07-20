#!/usr/bin/env node
import assert from 'node:assert/strict'
import net from 'node:net'

const raw = process.env.VITE_API_BASE || 'http://localhost:8080'
const allowInsecure = process.env.ALLOW_INSECURE_API_BASE === '1'
const production = process.env.PRODUCTION_DEPLOY === '1'
const url = new URL(raw)
const loopback = ['localhost', '127.0.0.1', '[::1]'].includes(url.hostname)
const hostname = url.hostname.replace(/^\[|\]$/g, '')
const privateIpv4 = (value) => {
  if (net.isIP(value) !== 4) return false
  const octets = value.split('.').map(Number)
  return (
    octets[0] === 10 ||
    (octets[0] === 100 && octets[1] >= 64 && octets[1] <= 127) ||
    octets[0] === 127 ||
    (octets[0] === 172 && octets[1] >= 16 && octets[1] <= 31) ||
    (octets[0] === 192 && octets[1] === 168)
  )
}
const privateNetwork = loopback || privateIpv4(hostname) || hostname.endsWith('.local')

assert.ok(['http:', 'https:'].includes(url.protocol), `unsupported API protocol: ${url.protocol}`)
if (url.protocol === 'http:' && !loopback && !allowInsecure) {
  throw new Error(
    `refusing insecure non-loopback API base ${raw}; use an HTTPS ingress or set ` +
      'ALLOW_INSECURE_API_BASE=1 only for isolated development',
  )
}
if (production && (url.protocol !== 'https:' || privateNetwork)) {
  throw new Error(`production Pages requires a public HTTPS API base, got ${raw}`)
}

console.log(`PASS API base policy (${url.protocol}//${url.host})`)
