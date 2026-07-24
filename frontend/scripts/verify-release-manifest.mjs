#!/usr/bin/env node
/** Validate release-manifest.json before promotion or archival. */
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { resolve, sep } from 'node:path'
import { tmpdir } from 'node:os'

const repoRoot = resolve(import.meta.dirname, '..', '..')
const fail = (message) => {
  console.error(`release manifest invalid: ${message}`)
  process.exitCode = 1
}

function repoPath(value, label, allowTemp = false) {
  const path = resolve(repoRoot, value)
  const tempRoot = resolve(tmpdir())
  const insideRepo = path === repoRoot || path.startsWith(`${repoRoot}${sep}`)
  const insideTemp = path === tempRoot || path.startsWith(`${tempRoot}${sep}`)
  if ((!allowTemp && !insideRepo) || (allowTemp && !insideRepo && !insideTemp)) {
    throw new Error(`${label} must remain inside the repository`)
  }
  return path
}

let manifestPath
try { manifestPath = repoPath(process.argv[2] ?? 'release-manifest.json', 'manifest', Boolean(process.argv[2])) }
catch (error) { fail(error.message); manifestPath = '' }

if (!existsSync(manifestPath)) fail(`missing ${manifestPath}`)
else {
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  if (manifest.schema !== 'tracera.release-manifest.v1') fail('unsupported schema')
  if (!manifest.git?.commit) fail('missing source commit')
  if (manifest.reproducibility?.secrets_included !== false) fail('secrets_included must be false')
  for (const lockfile of manifest.reproducibility?.lockfiles ?? []) {
    let lockfilePath
    try { lockfilePath = repoPath(lockfile, 'lockfile') }
    catch (error) { fail(error.message); continue }
    if (!existsSync(lockfilePath)) fail(`missing lockfile ${lockfile}`)
  }
  for (const artifact of manifest.artifacts ?? []) {
    if (!artifact.present) fail(`artifact missing: ${artifact.path}`)
    const path = repoPath(artifact.path, 'artifact')
    if (!existsSync(path)) fail(`artifact disappeared: ${artifact.path}`)
    else {
      const hash = createHash('sha256').update(readFileSync(path)).digest('hex')
      if (hash !== artifact.sha256) fail(`hash mismatch: ${artifact.path}`)
      if (readFileSync(path).byteLength !== artifact.bytes) fail(`size mismatch: ${artifact.path}`)
    }
  }
  if (!process.exitCode) console.log(`release manifest verified: ${manifestPath}`)
}
