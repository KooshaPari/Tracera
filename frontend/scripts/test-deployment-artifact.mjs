#!/usr/bin/env node
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { isAbsolute, join, resolve, sep } from 'node:path'

const dist = process.argv[2] || 'dist'
if (!/^[A-Za-z0-9._/-]+$/.test(dist) || isAbsolute(dist) || dist.includes('..')) {
  throw new Error('Deployment artifact path must remain relative to the working directory')
}
const distRoot = resolve(dist)
const indexPath = join(distRoot, 'index.html')
if (!existsSync(indexPath)) throw new Error(`Missing deployment entrypoint: ${indexPath}`)

const index = readFileSync(indexPath, 'utf8')
if (!/<title>\s*Tracera\b/i.test(index)) {
  throw new Error('Deployment artifact is missing canonical TRACERA title')
}

const assetDir = join(distRoot, 'assets')
const assets = existsSync(assetDir)
  ? readdirSync(assetDir).filter((name) => /^[A-Za-z0-9._-]+\.js$/.test(name))
  : []
const javascript = assets.map((name) => {
  const assetPath = join(assetDir, name)
  if (!assetPath.startsWith(`${assetDir}${sep}`)) {
    throw new Error(`Deployment asset escapes artifact root: ${name}`)
  }
  return readFileSync(assetPath, 'utf8')
}).join('\n')
if (!javascript.includes('Traceability') || !javascript.includes('Evidence')) {
  throw new Error('Deployment artifact is missing canonical dashboard markers')
}

console.log(`Canonical Tracera artifact verified: ${indexPath} (${assets.length} JS assets)`)
