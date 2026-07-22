#!/usr/bin/env node
import assert from 'node:assert/strict'
import net from 'node:net'

const raw = process.env.VITE_API_BASE || 'http://localhost:8080'
const allowInsecure = process.env.ALLOW_INSECURE_API_BASE === '1'
const production = process.env.PRODUCTION_DEPLOY === '1'
let url
try {
  url = new URL(raw)
} catch {
  throw new Error(`invalid API base URL: ${raw}`)
}
const hostname = url.hostname.replace(/^\[|\]$/g, '').toLowerCase()
const ipv6Loopback = (value) => {
  if (net.isIP(value) !== 6) return false
  const mappedIpv4 = value.match(/(\d+\.\d+\.\d+\.\d+)$/)?.[1]
  if (mappedIpv4 && net.isIP(mappedIpv4) === 4) {
    const octets = mappedIpv4.split('.').map(Number)
    const high = ((octets[0] << 8) | octets[1]).toString(16)
    const low = ((octets[2] << 8) | octets[3]).toString(16)
    value = value.replace(mappedIpv4, `${high}:${low}`)
  }
  const parts = value.split(':')
  const marker = parts.indexOf('')
  const expanded = marker >= 0
    ? [...parts.slice(0, marker), ...Array(9 - parts.length).fill('0'), ...parts.slice(marker + 1)]
    : parts
  if (expanded.length !== 8) return false
  const words = expanded.map((part) => Number.parseInt(part || '0', 16))
  const direct = words.slice(0, 7).every((word) => word === 0) && words[7] === 1
  const mapped = words.slice(0, 5).every((word) => word === 0) && words[5] === 0xffff
  return direct || (mapped && words[6] === 0x7f00 && words[7] === 1)
}
const loopback = hostname === 'localhost' || hostname === '127.0.0.1' || ipv6Loopback(hostname)
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
