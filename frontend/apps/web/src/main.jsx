import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
// Shared vision-pillar palette library (5-family cross-palette registry).
// Vendored from /Users/kooshapari/CodeProjects/Phenotype/repos/AgilePlus/.claude/worktrees/vision-pillar/assets/tokens.css
// Must be imported BEFORE ./index.css so :root vars here are available
// to component overrides. Existing --color-* aliases in index.css remain
// untouched for backward compat.
import './assets/tokens.css'
import './index.css'

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
