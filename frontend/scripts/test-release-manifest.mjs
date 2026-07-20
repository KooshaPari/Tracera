#!/usr/bin/env node
import { execFileSync } from 'node:child_process'
import { readFileSync, rmSync, writeFileSync } from 'node:fs'
import { tmpdir } from 'node:os'
import { join, resolve } from 'node:path'
import { mkdtempSync } from 'node:fs'

const root = resolve(import.meta.dirname, '..', '..')
const script = resolve(root, 'frontend/scripts/release-manifest.mjs')
const verify = resolve(root, 'frontend/scripts/verify-release-manifest.mjs')
const tempRoot = mkdtempSync(join(tmpdir(), 'tracera-release-manifest-'))
const first = join(tempRoot, 'a.json')
const second = join(tempRoot, 'b.json')
const malicious = join(tempRoot, 'malicious.json')
const env = { ...process.env, PATH: '/usr/bin:/bin:/usr/sbin:/sbin', SOURCE_DATE_EPOCH: '1700000000' }

try {
  execFileSync(process.execPath, [script, first], { cwd: root, env, stdio: 'ignore' })
  execFileSync(process.execPath, [script, second], { cwd: root, env, stdio: 'ignore' })
  if (readFileSync(first, 'utf8') !== readFileSync(second, 'utf8')) {
    throw new Error('SOURCE_DATE_EPOCH did not produce byte-identical manifests')
  }
  execFileSync(process.execPath, [verify, first], { cwd: root, env, stdio: 'ignore' })
  let rejected = false
  try {
    execFileSync(process.execPath, [verify, join(root, '..', 'outside-release-manifest.json')], { cwd: root, env, stdio: 'pipe' })
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
    execFileSync(process.execPath, [verify, malicious], { cwd: root, env, stdio: 'pipe' })
  } catch {
    lockfileRejected = true
  }
  if (!lockfileRejected) throw new Error('manifest verifier accepted lockfile outside repository')
  console.log('release manifest reproducibility: PASS')
} finally {
  rmSync(first, { force: true })
  rmSync(second, { force: true })
  rmSync(tempRoot, { force: true, recursive: true })
}
