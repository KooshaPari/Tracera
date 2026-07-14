import assert from 'node:assert/strict'
import test from 'node:test'

import {
  normalizeWorkOsApiHostname,
  normalizeWorkOsClientId,
  resolveAuthConfiguration,
} from './authConfig.js'

test('WorkOS client ID is required and normalized', () => {
  assert.equal(normalizeWorkOsClientId('  client_01ABCxyz  '), 'client_01ABCxyz')
  assert.throws(
    () => normalizeWorkOsClientId(undefined),
    /VITE_WORKOS_CLIENT_ID is required/,
  )
  assert.throws(
    () => normalizeWorkOsClientId('project_01ABCxyz'),
    /beginning with client_/,
  )
})

test('optional WorkOS API hostname accepts only an exact HTTPS origin', () => {
  assert.equal(normalizeWorkOsApiHostname(undefined), undefined)
  assert.equal(
    normalizeWorkOsApiHostname('  https://auth.tracera.example  '),
    'https://auth.tracera.example',
  )
  for (const invalidValue of [
    'http://auth.tracera.example',
    'https://auth.tracera.example/',
    'https://auth.tracera.example/path',
  ]) {
    assert.throws(
      () => normalizeWorkOsApiHostname(invalidValue),
      /must be an exact https origin/,
    )
  }
})

test('invalid WorkOS configuration resolves to a visible diagnostic', () => {
  assert.deepEqual(resolveAuthConfiguration('', undefined), {
    clientId: '',
    apiHostname: undefined,
    error:
      'VITE_WORKOS_CLIENT_ID is required and must be a WorkOS client ID beginning with client_',
  })
})

test('valid WorkOS configuration is ready for AuthKitProvider', () => {
  assert.deepEqual(
    resolveAuthConfiguration(
      'client_01ABCxyz',
      'https://auth.tracera.example',
    ),
    {
      clientId: 'client_01ABCxyz',
      apiHostname: 'https://auth.tracera.example',
      error: null,
    },
  )
})
