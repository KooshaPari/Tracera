import { readFile } from 'node:fs/promises'

const path = new URL('../../docs/sessions/20260722-rich-dashboard-recovery/capability-manifest.json', import.meta.url)
const manifest = JSON.parse(await readFile(path, 'utf8'))
const allowed = new Set(manifest.statuses)
if (!Array.isArray(manifest.capabilities) || manifest.capabilities.length === 0) {
  throw new Error('capability manifest must contain capabilities')
}
const ids = new Set()
for (const capability of manifest.capabilities) {
  if (!capability.id || ids.has(capability.id)) throw new Error(`duplicate or missing capability id: ${capability.id}`)
  ids.add(capability.id)
  if (!allowed.has(capability.status)) throw new Error(`invalid status for ${capability.id}: ${capability.status}`)
  if (!Array.isArray(capability.backend) || !Array.isArray(capability.frontend)) throw new Error(`route arrays missing for ${capability.id}`)
}
console.log(`capability manifest valid: ${manifest.capabilities.length} capabilities`)
