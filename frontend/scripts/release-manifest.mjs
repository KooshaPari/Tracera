#!/usr/bin/env node
/**
 * Emit a deterministic release manifest for local installs and CI artifacts.
 * The manifest never embeds secrets and tolerates missing build outputs so it
 * can be run before or after packaging.
 */
import { createHash } from 'node:crypto'
import { existsSync, readFileSync, writeFileSync } from 'node:fs'
import { basename, relative, resolve, isAbsolute } from 'node:path'
import { tmpdir } from 'node:os'
import { execFileSync } from 'node:child_process'

const repoRoot = resolve(import.meta.dirname, '..', '..')
function repoPath(value, label, allowTemp = false) {
  const path = resolve(repoRoot, value)
  const rel = relative(repoRoot, path)
  const tempRoot = resolve(tmpdir())
  if ((!allowTemp && (isAbsolute(rel) || rel === '..' || rel.startsWith(`..${process.platform === 'win32' ? '\\' : '/'}`))) ||
      (allowTemp && isAbsolute(rel) && !path.startsWith(tempRoot))) {
    throw new Error(`${label} must remain inside the repository`)
  }
  return path
}

const output = process.argv[2] ? repoPath(process.argv[2], 'manifest output', true) : resolve(repoRoot, 'release-manifest.json')

function readJson(path) {
  return JSON.parse(readFileSync(resolve(repoRoot, path), 'utf8'))
}

function git(args) {
  try {
    return execFileSync('git', args, { cwd: repoRoot, encoding: 'utf8' }).trim()
  } catch {
    return null
  }
}

function sha256(path) {
  const hash = createHash('sha256')
  hash.update(readFileSync(path))
  return hash.digest('hex')
}

const cargo = readFileSync(resolve(repoRoot, 'crates/tracera-server/Cargo.toml'), 'utf8')
const cargoVersion = cargo.match(/^version\s*=\s*"([^"]+)"/m)?.[1] ?? null
const frontend = readJson('frontend/package.json')
const web = readJson('frontend/apps/web/package.json')
const artifactPaths = process.env.TRACERA_RELEASE_ARTIFACTS?.split(',').map((item) => item.trim()).filter(Boolean) ?? []
const generatedAt = process.env.SOURCE_DATE_EPOCH
  ? new Date(Number(process.env.SOURCE_DATE_EPOCH) * 1000).toISOString()
  : new Date().toISOString()
const artifacts = artifactPaths.map((item) => {
  const path = repoPath(item, 'release artifact')
  if (!existsSync(path)) return { path: item, present: false }
  return { path: item, name: basename(path), present: true, bytes: readFileSync(path).byteLength, sha256: sha256(path) }
})

const manifest = {
  schema: 'tracera.release-manifest.v1',
  generated_at: generatedAt,
  git: { commit: process.env.GITHUB_SHA ?? git(['rev-parse', 'HEAD']), tag: process.env.GITHUB_REF_NAME ?? git(['describe', '--tags', '--always']) },
  versions: { server: cargoVersion, frontend: frontend.version ?? null, web: web.version ?? null },
  artifacts,
  reproducibility: { lockfiles: ['Cargo.lock', 'frontend/bun.lock'], secrets_included: false },
}

writeFileSync(output, `${JSON.stringify(manifest, null, 2)}\n`)
console.log(`release manifest: ${output}`)
