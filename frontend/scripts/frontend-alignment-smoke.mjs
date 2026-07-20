#!/usr/bin/env node

const base = process.env.VITE_API_BASE || 'http://127.0.0.1:8080'
const endpoints = [
  '/health',
  '/readyz',
  '/sdlc-pm/sprints',
  '/org-intel/teams',
  '/org-intel/metrics',
  '/evidence',
]

async function request(path) {
  const response = await fetch(`${base}${path}`)
  const text = await response.text()
  if (!response.ok) {
    throw new Error(`${path}: ${response.status} ${response.statusText}: ${text || 'empty'}`)
  }
  return text ? JSON.parse(text) : {}
}

try {
  const failures = []
  for (const path of endpoints) {
    try {
      const payload = await request(path)
      const isArrayPayload = Array.isArray(payload)
      if (path === '/evidence' && !(Array.isArray(payload?.items) || Number.isInteger(payload?.count))) {
        throw new Error('evidence response must include items/count')
      }

      if ((path === '/sdlc-pm/sprints' || path === '/org-intel/teams') && !isArrayPayload) {
        throw new Error('expected JSON array')
      }

      if (path === '/org-intel/metrics' && !payload) {
        throw new Error('expected metrics object')
      }

      console.log(`OK ${path}`)
    } catch (err) {
      failures.push(err.message)
      console.error(`FAIL ${path}: ${err.message}`)
    }
  }

  if (failures.length > 0) {
    console.error(`\nSmoke check failed with ${failures.length} endpoint failure(s).`)
    process.exitCode = 1
    return
  }

  console.log('\nTracera frontend backend alignment smoke: PASS')
} catch (err) {
  console.error(err)
  process.exitCode = 1
}
