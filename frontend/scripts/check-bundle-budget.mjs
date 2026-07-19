import { existsSync, readdirSync, statSync, readFileSync } from 'node:fs'
import { join, extname } from 'node:path'
import { gzipSync } from 'node:zlib'

const distDir = join(process.cwd(), 'dist')
const limits = { js: 250 * 1024, css: 100 * 1024, total: 400 * 1024, gzip: 125 * 1024 }

if (!existsSync(distDir)) {
  console.error(`bundle budget: missing ${distDir}; run npm run build first`)
  process.exit(1)
}

const files = []
function walk(dir) {
  for (const name of readdirSync(dir)) {
    const path = join(dir, name)
    if (statSync(path).isDirectory()) walk(path)
    else files.push(path)
  }
}
walk(distDir)
const assets = files.filter((path) => ['.js', '.css'].includes(extname(path)))
const size = (path) => statSync(path).size
const total = assets.reduce((sum, path) => sum + size(path), 0)
const js = assets.filter((path) => extname(path) === '.js').reduce((sum, path) => sum + size(path), 0)
const css = assets.filter((path) => extname(path) === '.css').reduce((sum, path) => sum + size(path), 0)
const gzip = assets.reduce((sum, path) => sum + gzipSync(readFileSync(path), { level: 9 }).byteLength, 0)
for (const [label, value, limit] of [['JavaScript', js, limits.js], ['CSS', css, limits.css], ['assets total', total, limits.total], ['assets gzip total', gzip, limits.gzip]]) {
  console.log(`${value <= limit ? 'ok' : 'FAIL'} ${label}: ${(value / 1024).toFixed(1)} KiB / ${(limit / 1024).toFixed(0)} KiB`)
  if (value > limit) process.exitCode = 1
}
if (assets.length === 0) {
  console.error('bundle budget: no JS/CSS assets found')
  process.exitCode = 1
}
