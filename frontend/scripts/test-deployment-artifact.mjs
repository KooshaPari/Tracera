#!/usr/bin/env node
import { existsSync, readFileSync, readdirSync } from 'node:fs'
import { join } from 'node:path'

const dist = process.argv[2] || 'dist'
const indexPath = join(dist, 'index.html')
if (!existsSync(indexPath)) throw new Error(`Missing deployment entrypoint: ${indexPath}`)

const index = readFileSync(indexPath, 'utf8')
if (!/<title>\s*Tracera\b/i.test(index)) {
  throw new Error('Deployment artifact is missing canonical TRACERA title')
}

const assetDir = join(dist, 'assets')
const assets = existsSync(assetDir) ? readdirSync(assetDir).filter((name) => name.endsWith('.js')) : []
const javascript = assets.map((name) => readFileSync(join(assetDir, name), 'utf8')).join('\n')
if (!javascript.includes('Traceability') || !javascript.includes('Evidence')) {
  throw new Error('Deployment artifact is missing canonical dashboard markers')
}

console.log(`Canonical Tracera artifact verified: ${indexPath} (${assets.length} JS assets)`)
