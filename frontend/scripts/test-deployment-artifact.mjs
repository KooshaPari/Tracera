#!/usr/bin/env node
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { isAbsolute, join, relative, resolve, sep } from 'node:path'

const dist = process.argv[2] || 'dist'
if (isAbsolute(dist) || dist.split(/[\\/]/).includes('..')) {
  throw new Error('Deployment artifact path must remain relative to the working directory')
}
const distRoot = resolve(dist)
const insideDist = (candidate) => {
  const path = resolve(candidate)
  const rel = relative(distRoot, path)
  return rel === '' || (!isAbsolute(rel) && rel !== '..' && !rel.startsWith(`..${sep}`))
}
const indexPath = join(distRoot, 'index.html')
if (!insideDist(indexPath)) throw new Error('Deployment entrypoint escapes artifact root')
if (!existsSync(indexPath)) throw new Error(`Missing deployment entrypoint: ${indexPath}`)

const index = readFileSync(indexPath, 'utf8')
if (!/<title>\s*Tracera\b/i.test(index)) {
  throw new Error('Deployment artifact is missing canonical TRACERA title')
}

const assetDir = join(distRoot, 'assets')
const assets = existsSync(assetDir)
  ? readdirSync(assetDir).filter((name) => name.endsWith('.js') && !name.includes('/') && !name.includes('\\'))
  : []
const javascript = assets.map((name) => {
  const assetPath = join(assetDir, name)
  if (!insideDist(assetPath)) throw new Error(`Deployment asset escapes artifact root: ${name}`)
  return readFileSync(assetPath, 'utf8')
}).join('\n')
if (!javascript.includes('Traceability') || !javascript.includes('Evidence')) {
  throw new Error('Deployment artifact is missing canonical dashboard markers')
}

console.log(`Canonical Tracera artifact verified: ${indexPath} (${assets.length} JS assets)`)
