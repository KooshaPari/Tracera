#!/usr/bin/env node
import { execFileSync } from 'node:child_process'
import { readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'

const root = resolve(import.meta.dirname, '..', '..')
const script = resolve(root, 'frontend/scripts/release-manifest.mjs')
const verify = resolve(root, 'frontend/scripts/verify-release-manifest.mjs')
const first = join(tmpdir(), 'tracera-release-manifest-a.json')
const second = join(tmpdir(), 'tracera-release-manifest-b.json')
const malicious = join(tmpdir(), 'tracera-release-manifest-malicious.json')
const env = { ...process.env, SOURCE_DATE_EPOCH: '1700000000' }

try {
  execFileSync('node', [script, first], { cwd: root, env, stdio: 'ignore' })
  execFileSync('node', [script, second], { cwd: root, env, stdio: 'ignore' })
  if (readFileSync(first, 'utf8') !== readFileSync(second, 'utf8')) {
    throw new Error('SOURCE_DATE_EPOCH did not produce byte-identical manifests')
  }
  execFileSync('node', [verify, first], { cwd: root, env, stdio: 'ignore' })
  let rejected = false
  try {
    execFileSync('node', [verify, '/tmp/../outside-release-manifest.json'], { cwd: root, env, stdio: 'pipe' })
  } catch {
    rejected = true
  }
  if (!rejected) throw new Error('manifest verifier accepted path outside permitted roots')
  writeFileSync(malicious, JSON.stringify({
    schema: 'tracera.release-manifest.v1',
    git: { commit: 'test' },
    reproducibility: { secrets_included: false, lockfiles: ['../../etc/passwd'] },
    artifacts: [],
  }))
  let lockfileRejected = false
  try {
    execFileSync('node', [verify, malicious], { cwd: root, env, stdio: 'pipe' })
  } catch {
    lockfileRejected = true
  }
  if (!lockfileRejected) throw new Error('manifest verifier accepted lockfile outside repository')
  console.log('release manifest reproducibility: PASS')
} finally {
  rmSync(first, { force: true })
  rmSync(second, { force: true })
  rmSync(malicious, { force: true })
}
