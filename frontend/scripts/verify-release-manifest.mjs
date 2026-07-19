#!/usr/bin/env node
/** Validate release-manifest.json before promotion or archival. */
import { createHash } from 'node:crypto'
import { existsSync, readFileSync } from 'node:fs'
import { resolve } from 'node:path'

const repoRoot = resolve(import.meta.dirname, '..', '..')
const manifestPath = resolve(process.argv[2] ?? resolve(repoRoot, 'release-manifest.json'))
const fail = (message) => {
  console.error(`release manifest invalid: ${message}`)
  process.exitCode = 1
}

if (!existsSync(manifestPath)) fail(`missing ${manifestPath}`)
else {
  const manifest = JSON.parse(readFileSync(manifestPath, 'utf8'))
  if (manifest.schema !== 'tracera.release-manifest.v1') fail('unsupported schema')
  if (!manifest.git?.commit) fail('missing source commit')
  if (manifest.reproducibility?.secrets_included !== false) fail('secrets_included must be false')
  for (const lockfile of manifest.reproducibility?.lockfiles ?? []) {
    if (!existsSync(resolve(repoRoot, lockfile))) fail(`missing lockfile ${lockfile}`)
  }
  for (const artifact of manifest.artifacts ?? []) {
    if (!artifact.present) fail(`artifact missing: ${artifact.path}`)
    const path = resolve(repoRoot, artifact.path)
    if (!existsSync(path)) fail(`artifact disappeared: ${artifact.path}`)
    else {
      const hash = createHash('sha256').update(readFileSync(path)).digest('hex')
      if (hash !== artifact.sha256) fail(`hash mismatch: ${artifact.path}`)
      if (readFileSync(path).byteLength !== artifact.bytes) fail(`size mismatch: ${artifact.path}`)
    }
  }
  if (!process.exitCode) console.log(`release manifest verified: ${manifestPath}`)
}
