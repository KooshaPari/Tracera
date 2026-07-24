import { readFile } from 'node:fs/promises'

const root = new URL('../apps/web/src/', import.meta.url)
const indexCss = await readFile(new URL('index.css', root), 'utf8')
const dashboardCss = await readFile(new URL('components/Dashboard.css', root), 'utf8')

const required = ['--color-error-text', '--color-info', '--color-muted']
for (const token of required) {
  if (!indexCss.includes(`${token}:`)) throw new Error(`missing theme token ${token}`)
}

const componentLiterals = dashboardCss.match(/#[0-9a-f]{3,8}\b/gi) ?? []
if (componentLiterals.length) {
  throw new Error(`Dashboard.css contains raw color literals: ${componentLiterals.join(', ')}`)
}

console.log(`theme contract passed: ${required.length} semantic tokens, no dashboard literals`)
