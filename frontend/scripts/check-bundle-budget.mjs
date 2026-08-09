import { existsSync, readdirSync, statSync, readFileSync } from 'node:fs'
import { extname, join } from 'node:path'
import { gzipSync } from 'node:zlib'

const distDir = join(process.cwd(), 'dist')
const initialLimits = {
  js: 3 * 1024 * 1024,
  css: 200 * 1024,
  total: 3.25 * 1024 * 1024,
  gzip: 1 * 1024 * 1024,
}
const allAssetsLimits = {
  js: 7 * 1024 * 1024,
  css: 200 * 1024,
  total: 7.5 * 1024 * 1024,
  gzip: 2 * 1024 * 1024,
}

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

function measure(paths) {
  const js = paths.filter((path) => extname(path) === '.js')
  const css = paths.filter((path) => extname(path) === '.css')
  const bytes = (list) => list.reduce((sum, path) => sum + size(path), 0)
  const gzip = (list) => list.reduce(
    (sum, path) => sum + gzipSync(readFileSync(path), { level: 9 }).byteLength,
    0,
  )
  return { js: bytes(js), css: bytes(css), total: bytes(paths), gzip: gzip(paths) }
}

function report(scope, values, limits) {
  for (const [label, key] of [['JavaScript', 'js'], ['CSS', 'css'], ['assets total', 'total'], ['assets gzip total', 'gzip']]) {
    const value = values[key]
    const limit = limits[key]
    const unit = key === 'gzip' ? 'KiB gzip' : 'KiB'
    console.log(`${value <= limit ? 'ok' : 'FAIL'} ${scope} ${label}: ${(value / 1024).toFixed(1)} ${unit} / ${(limit / 1024).toFixed(0)} KiB`)
    if (value > limit) process.exitCode = 1
  }
}

const indexPath = join(distDir, 'index.html')
const initialAssets = []
if (existsSync(indexPath)) {
  const html = readFileSync(indexPath, 'utf8')
  const refs = [...html.matchAll(/\b(?:src|href)=["']([^"']+)["']/g)]
  for (const [, ref] of refs) {
    const pathname = ref.split(/[?#]/, 1)[0]
    if (!pathname.startsWith('/assets/')) continue
    const extension = extname(pathname)
    if (!['.js', '.css'].includes(extension)) continue
    const path = join(distDir, pathname.slice(1))
    if (!existsSync(path)) {
      console.error(`bundle budget: index.html references missing asset ${pathname}`)
      process.exitCode = 1
      continue
    }
    if (!initialAssets.includes(path)) initialAssets.push(path)
  }
} else {
  console.error(`bundle budget: missing ${indexPath}`)
  process.exitCode = 1
}

if (initialAssets.length === 0) {
  console.error('bundle budget: index.html references no JS/CSS assets')
  process.exitCode = 1
} else {
  report('initial-load', measure(initialAssets), initialLimits)
}

report('all-assets', measure(assets), allAssetsLimits)

if (assets.length === 0) {
  console.error('bundle budget: no JS/CSS assets found')
  process.exitCode = 1
}
