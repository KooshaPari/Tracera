import assert from 'node:assert/strict'
import test from 'node:test'

import { createDashboardPoller } from './polling.js'

function deferred() {
  let resolve
  const promise = new Promise((resolvePromise) => {
    resolve = resolvePromise
  })
  return { promise, resolve }
}

test('dashboard polling never overlaps in-flight refreshes', async () => {
  const first = deferred()
  let loadCount = 0
  const poller = createDashboardPoller({
    load: async () => {
      loadCount += 1
      return first.promise
    },
    onData: () => {},
    onError: assert.fail,
    setIntervalImpl: () => 1,
    clearIntervalImpl: () => {},
  })

  await Promise.resolve()
  await poller.refresh()
  assert.equal(loadCount, 1)

  first.resolve({ health: { status: 'ok' } })
  await Promise.resolve()
  await Promise.resolve()
  await poller.refresh()
  assert.equal(loadCount, 2)
  poller.stop()
})

test('stopping polling aborts work and suppresses late state updates', async () => {
  const request = deferred()
  let signal
  let dataUpdates = 0
  let clearedInterval
  const poller = createDashboardPoller({
    load: async (requestSignal) => {
      signal = requestSignal
      return request.promise
    },
    onData: () => {
      dataUpdates += 1
    },
    onError: assert.fail,
    setIntervalImpl: () => 42,
    clearIntervalImpl: (intervalId) => {
      clearedInterval = intervalId
    },
  })

  await Promise.resolve()
  poller.stop()
  assert.equal(signal.aborted, true)
  assert.equal(clearedInterval, 42)

  request.resolve({ health: { status: 'ok' } })
  await Promise.resolve()
  await Promise.resolve()
  assert.equal(dataUpdates, 0)
})
