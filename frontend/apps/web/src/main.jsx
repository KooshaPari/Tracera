import React from 'react'
import ReactDOM from 'react-dom/client'
import { AuthKitProvider } from '@workos-inc/authkit-react'
import App from './App'
import { resolveAuthConfiguration } from './authConfig.js'
// Shared vision-pillar palette library (5-family cross-palette registry).
// Vendored from /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/.claude/worktrees/vision-pillar/assets/tokens.css
// Must be imported BEFORE ./index.css so :root vars here are available
// to component overrides. Existing --color-* aliases in index.css remain
// untouched for backward compat.
import './assets/tokens.css'
import './index.css'

const authConfiguration = resolveAuthConfiguration(
  import.meta.env.VITE_WORKOS_CLIENT_ID,
  import.meta.env.VITE_WORKOS_API_HOSTNAME,
)

function Root() {
  if (authConfiguration.error) {
    return (
      <main className="app">
        <section className="error-banner" role="alert">
          <h1>Tracera authentication is not configured</h1>
          <p>{authConfiguration.error}</p>
        </section>
      </main>
    )
  }

  return (
    <AuthKitProvider
      clientId={authConfiguration.clientId}
      apiHostname={authConfiguration.apiHostname}
    >
      <App />
    </AuthKitProvider>
  )
}

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <Root />
  </React.StrictMode>,
)
