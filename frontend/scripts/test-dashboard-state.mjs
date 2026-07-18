#!/usr/bin/env node
import assert from 'node:assert/strict'
import { isHealthOk, mergeDashboardFetchResults } from '../apps/web/src/components/dashboardState.js'

function runCase(name, fn) {
  try {
    fn()
    console.log(`PASS ${name}`)
  } catch (err) {
    console.error(`FAIL ${name}`)
    console.error(err.message)
    process.exitCode = 1
  }
}

runCase('mergeDashboardFetchResults: returns normalized success payload', () => {
  const merged = mergeDashboardFetchResults([
    { status: 'fulfilled', value: { status: 'ok' } },
    { status: 'fulfilled', value: [{ id: 'S1' }, { id: 'S2' }] },
    { status: 'fulfilled', value: [{ id: 'T1' }] },
    { status: 'fulfilled', value: { total_artifacts: 5, coverage_ratio: 0.5, open_gaps: 2 } },
    { status: 'fulfilled', value: { count: '4', items: [{ id: '1' }, { id: '2' }, { id: '3' }, { id: '4' }] } },
  ])

  assert.deepEqual(merged.error, null)
  assert.deepEqual(merged.health, { status: 'ok' })
  assert.equal(merged.sprints.length, 2)
  assert.equal(merged.teams.length, 1)
  assert.equal(merged.evidenceCount, 4)
  assert.deepEqual(merged.metrics, { total_artifacts: 5, coverage_ratio: 0.5, open_gaps: 2 })
})

runCase('mergeDashboardFetchResults: handles missing + malformed evidence gracefully', () => {
  const merged = mergeDashboardFetchResults([
    { status: 'fulfilled', value: { status: 'ok' } },
    { status: 'rejected', reason: new Error('sprints') },
    { status: 'fulfilled', value: [] },
    { status: 'rejected', reason: new Error('metrics') },
    { status: 'fulfilled', value: { items: [] } },
  ])

  assert.deepEqual(merged.sprints, [])
  assert.deepEqual(merged.teams, [])
  assert.equal(merged.evidenceCount, 0)
  assert.equal(merged.metrics, null)
  assert.ok(merged.error.includes('sprints'))
  assert.ok(merged.error.includes('metrics'))
  assert.equal(merged.health?.status, 'ok')
})

runCase('mergeDashboardFetchResults: preserves fallback health and null evidence', () => {
  const merged = mergeDashboardFetchResults([
    { status: 'rejected', reason: new Error('boom') },
    { status: 'fulfilled', value: [] },
    { status: 'fulfilled', value: [{ id: 'team-x' }] },
    { status: 'fulfilled', value: { total_artifacts: 1 } },
    { status: 'fulfilled', value: { count: null, items: null } },
  ])

  assert.deepEqual(merged.health, { status: 'unknown' })
  assert.equal(merged.evidenceCount, 0)
  assert.ok(merged.error.includes('boom'))
})

runCase('isHealthOk: validates explicit ok only', () => {
  assert.equal(isHealthOk({ status: 'ok' }), true)
  assert.equal(isHealthOk({ status: 'unknown' }), false)
  assert.equal(isHealthOk(null), false)
})

console.log('dashboard state tests complete')
