# TraceRTM Frontend Master Plan
## Consolidated, Optimized & Extended Architecture

**Date**: 2025-11-29  
**Status**: READY FOR IMPLEMENTATION  
**Scope**: Desktop App + Website + Mobile (PWA)

---

## Executive Summary

This document consolidates all frontend planning into a single actionable plan with **multiple technology options** for Desktop and Website development.

### Key Decisions Made
- ✅ **Monorepo**: pnpm workspaces + Turborepo
- ✅ **Web Framework**: React 19 + TypeScript + Vite 5.0
- ✅ **State Management**: Legend State (offline-first) + TanStack Query v5
- ✅ **UI Components**: shadcn/ui + TailwindCSS
- ✅ **Graph Visualization**: Cytoscape.js + React Flow
- ✅ **Testing**: Vitest + Playwright

### Options to Decide
- 🔄 **Desktop**: Electron vs Tauri vs Neutralino
- 🔄 **Deployment**: Vercel vs Cloudflare Pages vs Self-hosted

---

## Part 1: Technology Stack Options Matrix

### Desktop Framework Comparison

| Feature | Electron | Tauri | Neutralino |
|---------|----------|-------|------------|
| **Bundle Size** | 150MB+ | 3-10MB | 2-5MB |
| **Memory Usage** | 150MB+ | 30-50MB | 20-40MB |
| **Language** | JS/TS | Rust + JS | JS/TS |
| **Native APIs** | ✅ Full | ✅ Full | ⚠️ Limited |
| **Auto-Updates** | ✅ Built-in | ✅ Built-in | ⚠️ Manual |
| **Maturity** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Learning Curve** | Low | Medium (Rust) | Low |
| **Security** | ⚠️ Chromium | ✅ Sandboxed | ⚠️ WebView |
| **Cross-Platform** | ✅ Win/Mac/Linux | ✅ Win/Mac/Linux | ✅ Win/Mac/Linux |

**Recommendation**: 
- **MVP**: Electron (fastest to ship, proven)
- **V2**: Migrate to Tauri (smaller, faster, more secure)

### Web Deployment Options

| Feature | Vercel | Cloudflare Pages | Self-Hosted |
|---------|--------|------------------|-------------|
| **Free Tier** | 100GB/mo | Unlimited | N/A |
| **Edge Functions** | ✅ Yes | ✅ Workers | ⚠️ Manual |
| **Build Time** | Fast | Fast | Depends |
| **Custom Domain** | ✅ Free | ✅ Free | ✅ Yes |
| **Analytics** | ✅ Built-in | ✅ Built-in | ⚠️ Manual |
| **Cost at Scale** | $$$$ | $$ | $ |

**Recommendation**: Vercel for MVP, Cloudflare for scale

---

## Part 2: Monorepo Architecture

```
tracertm-frontend/
├── apps/
│   ├── web/                    # React SPA (Vite)
│   │   ├── src/
│   │   │   ├── pages/          # 16 views
│   │   │   ├── components/     # View-specific components
│   │   │   ├── hooks/          # Custom hooks
│   │   │   ├── stores/         # Legend State stores
│   │   │   └── lib/            # Utilities
│   │   ├── public/
│   │   └── package.json
│   │
│   ├── desktop/                # Electron/Tauri wrapper
│   │   ├── src/
│   │   │   ├── main/           # Main process
│   │   │   ├── preload/        # Preload scripts
│   │   │   └── renderer/       # Uses @tracertm/web
│   │   └── package.json
│   │
│   ├── docs/                   # Documentation site (Astro)
│   │   ├── src/
│   │   └── package.json
│   │
│   └── storybook/              # Component workshop
│       ├── stories/
│       └── package.json
│
├── packages/
│   ├── ui/                     # Shared UI components (shadcn/ui)
│   │   ├── components/
│   │   │   ├── Button.tsx
│   │   │   ├── Dialog.tsx
│   │   │   ├── ItemCard.tsx
│   │   │   ├── LinkViewer.tsx
│   │   │   └── ...
│   │   └── package.json
│   │
│   ├── api-client/             # Generated OpenAPI client
│   │   ├── generated/
│   │   ├── hooks/              # TanStack Query hooks
│   │   └── package.json
│   │
│   ├── state/                  # Legend State stores
│   │   ├── stores/
│   │   │   ├── project.ts
│   │   │   ├── items.ts
│   │   │   ├── links.ts
│   │   │   └── sync.ts
│   │   └── package.json
│   │
│   ├── types/                  # Shared TypeScript types
│   │   ├── api.ts
│   │   ├── domain.ts
│   │   └── package.json
│   │
│   └── config/                 # Shared configuration
│       ├── tailwind.config.ts
│       ├── tsconfig.base.json
│       └── package.json
│
├── turbo.json                  # Turborepo config
├── pnpm-workspace.yaml         # pnpm workspaces
└── package.json                # Root package.json
```

---

## Part 3: Core Technology Stack

### Frontend Core
```json
{
  "dependencies": {
    "react": "^19.0.0",
    "react-dom": "^19.0.0",
    "react-router-dom": "^7.0.0",
    "@legendapp/state": "^3.0.0",
    "@tanstack/react-query": "^5.0.0",
    "@tanstack/react-table": "^8.0.0",
    "@tanstack/react-virtual": "^3.0.0"
  }
}
```

### UI & Visualization
```json
{
  "dependencies": {
    "tailwindcss": "^3.4.0",
    "@radix-ui/react-*": "^1.0.0",
    "cytoscape": "^3.28.0",
    "react-cytoscapejs": "^2.0.0",
    "reactflow": "^11.10.0",
    "@monaco-editor/react": "^4.6.0",
    "@dnd-kit/core": "^8.0.0",
    "sonner": "^1.3.0"
  }
}
```

### Forms & Validation
```json
{
  "dependencies": {
    "react-hook-form": "^7.50.0",
    "zod": "^3.22.0",
    "@hookform/resolvers": "^3.3.0"
  }
}
```

### API & HTTP
```json
{
  "dependencies": {
    "openapi-fetch": "^0.9.0",
    "openapi-typescript": "^6.7.0"
  }
}
```

---

## Part 4: Desktop App Architecture

### Option A: Electron (Recommended for MVP)

```
apps/desktop/
├── src/
│   ├── main/
│   │   ├── index.ts           # Main process entry
│   │   ├── ipc.ts             # IPC handlers
│   │   ├── menu.ts            # Native menus
│   │   ├── tray.ts            # System tray
│   │   └── updater.ts         # Auto-updates
│   ├── preload/
│   │   └── index.ts           # Preload script (secure bridge)
│   └── renderer/
│       └── index.html         # Loads web app
├── electron-builder.yml       # Build config
└── package.json
```

**Key Features**:
- ✅ Native file system access
- ✅ System tray integration
- ✅ Native menus
- ✅ Auto-updates (electron-updater)
- ✅ Offline-first with local SQLite
- ✅ Deep linking (tracertm://)

### Option B: Tauri (Recommended for V2)

```
apps/desktop-tauri/
├── src/
│   └── main.rs                # Rust backend
├── src-tauri/
│   ├── src/
│   │   ├── main.rs
│   │   ├── commands.rs        # Tauri commands
│   │   └── menu.rs            # Native menus
│   ├── tauri.conf.json        # Tauri config
│   └── Cargo.toml
└── package.json
```

**Key Features**:
- ✅ 10-50x smaller bundle
- ✅ Better security (Rust sandbox)
- ✅ Lower memory usage
- ✅ Native performance
- ⚠️ Requires Rust knowledge

---

## Part 5: Website Architecture

### Web App Structure (apps/web)

```
apps/web/
├── src/
│   ├── pages/                 # Route pages
│   │   ├── index.tsx          # Dashboard
│   │   ├── projects/
│   │   │   ├── index.tsx      # Project list
│   │   │   └── [id]/
│   │   │       ├── index.tsx  # Project detail
│   │   │       └── views/
│   │   │           ├── feature.tsx
│   │   │           ├── code.tsx
│   │   │           ├── test.tsx
│   │   │           ├── api.tsx
│   │   │           ├── database.tsx
│   │   │           ├── wireframe.tsx
│   │   │           ├── documentation.tsx
│   │   │           ├── deployment.tsx
│   │   │           └── graph.tsx
│   │   └── settings/
│   │       └── index.tsx
│   │
│   ├── components/
│   │   ├── layout/
│   │   │   ├── Layout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   └── ViewSwitcher.tsx
│   │   ├── views/
│   │   │   ├── FeatureView.tsx
│   │   │   ├── CodeView.tsx
│   │   │   ├── TestView.tsx
│   │   │   └── ...
│   │   ├── items/
│   │   │   ├── ItemList.tsx
│   │   │   ├── ItemDetail.tsx
│   │   │   ├── ItemForm.tsx
│   │   │   └── ItemCard.tsx
│   │   ├── links/
│   │   │   ├── LinkViewer.tsx
│   │   │   ├── LinkCreator.tsx
│   │   │   └── GraphView.tsx
│   │   └── agents/
│   │       ├── AgentFeed.tsx
│   │       ├── ConflictResolver.tsx
│   │       └── SyncStatus.tsx
│   │
│   ├── hooks/
│   │   ├── useItems.ts
│   │   ├── useLinks.ts
│   │   ├── useProject.ts
│   │   ├── useSync.ts
│   │   └── useOffline.ts
│   │
│   ├── stores/
│   │   ├── project.ts
│   │   ├── items.ts
│   │   ├── links.ts
│   │   └── sync.ts
│   │
│   └── lib/
│       ├── api.ts
│       ├── websocket.ts
│       └── indexeddb.ts
│
├── public/
│   ├── manifest.json          # PWA manifest
│   └── sw.js                  # Service worker
│
├── index.html
├── vite.config.ts
└── package.json
```

---

## Part 6: Implementation Phases

### Phase 1: Foundation (Week 1-2)
- [ ] Initialize monorepo with pnpm + Turborepo
- [ ] Setup shared packages (ui, types, config)
- [ ] Configure Vite + React 19 + TypeScript
- [ ] Setup ESLint + Prettier + TypeScript strict
- [ ] Generate OpenAPI types from backend
- [ ] Setup Vitest + Playwright

**Deliverables**:
- Working monorepo structure
- CI/CD pipeline (GitHub Actions)
- Pre-commit hooks

### Phase 2: Core UI (Week 3-4)
- [ ] Implement Layout + Sidebar + Header
- [ ] Create ViewSwitcher component
- [ ] Build 3 core views: Feature, Code, Test
- [ ] Implement ItemList + ItemDetail + ItemForm
- [ ] Add keyboard shortcuts
- [ ] Setup responsive design

**Deliverables**:
- 3 working views
- CRUD operations
- Responsive layout

### Phase 3: State & Sync (Week 5-6)
- [ ] Setup Legend State stores
- [ ] Implement TanStack Query hooks
- [ ] Create IndexedDB schema
- [ ] Build sync manager
- [ ] Add conflict resolution UI
- [ ] Implement offline detection

**Deliverables**:
- Offline-first functionality
- Real-time sync
- Conflict resolution

### Phase 4: Advanced Features (Week 7-8)
- [ ] Build Graph visualization (Cytoscape.js)
- [ ] Implement Node editor (React Flow)
- [ ] Add Link creation UI
- [ ] Build bulk operations
- [ ] Implement undo/redo
- [ ] Add search & filters

**Deliverables**:
- Graph visualization
- Link management
- Bulk operations

### Phase 5: Desktop App (Week 9-10)
- [ ] Setup Electron project
- [ ] Implement IPC security
- [ ] Add file system access
- [ ] Setup auto-updates
- [ ] Create native menus
- [ ] Build installers (Win/Mac/Linux)

**Deliverables**:
- Desktop app for all platforms
- Auto-update system
- Native integrations

### Phase 6: Polish & Testing (Week 11-12)
- [ ] 100% test coverage
- [ ] Performance optimization
- [ ] Accessibility (WCAG 2.1 AA)
- [ ] Documentation
- [ ] Storybook components
- [ ] Production deployment

**Deliverables**:
- Production-ready apps
- Complete documentation
- Component library

---

## Part 7: Quick Start Commands

### Initialize Monorepo
```bash
# Create monorepo
mkdir tracertm-frontend && cd tracertm-frontend
pnpm init

# Setup workspaces
cat > pnpm-workspace.yaml << 'EOF'
packages:
  - 'apps/*'
  - 'packages/*'
EOF

# Install Turborepo
pnpm add -D turbo

# Create turbo.json
cat > turbo.json << 'EOF'
{
  "$schema": "https://turbo.build/schema.json",
  "tasks": {
    "build": {
      "outputs": ["dist/**"],
      "dependsOn": ["^build"]
    },
    "dev": {
      "cache": false,
      "persistent": true
    },
    "test": {
      "outputs": ["coverage/**"]
    },
    "lint": {
      "outputs": [".eslintcache"]
    }
  }
}
EOF
```

### Create Web App
```bash
# Create web app with Vite
pnpm create vite apps/web --template react-ts

# Install dependencies
cd apps/web
pnpm add react-router-dom @legendapp/state @tanstack/react-query
pnpm add tailwindcss postcss autoprefixer -D
pnpm add @radix-ui/react-dialog @radix-ui/react-dropdown-menu
pnpm add cytoscape react-cytoscapejs reactflow
pnpm add react-hook-form zod @hookform/resolvers
pnpm add openapi-fetch sonner
```

### Create Desktop App (Electron)
```bash
# Create desktop app
mkdir -p apps/desktop/src/{main,preload,renderer}

# Install Electron
cd apps/desktop
pnpm add electron electron-builder -D
pnpm add electron-updater
```

---

## Part 8: Success Criteria

### Performance Targets
| Metric | Target |
|--------|--------|
| Initial Load | < 2s |
| List 10K items | < 500ms |
| Create item | < 100ms |
| Sync 100 mutations | < 2s |
| WebSocket latency | < 100ms |
| Desktop bundle | < 100MB |

### Quality Gates
- ✅ 100% test coverage
- ✅ 0 lint errors
- ✅ 0 type errors
- ✅ WCAG 2.1 AA accessibility
- ✅ Lighthouse score > 90

### Feature Parity
- ✅ All 16 views on web
- ✅ All 16 views on desktop
- ✅ Offline-first on all platforms
- ✅ Real-time sync on all platforms

---

## Part 9: Decision Points for User

### 1. Desktop Framework
**Question**: Which desktop framework to use?

| Option | Pros | Cons |
|--------|------|------|
| **Electron** | Fast to ship, proven, large ecosystem | Large bundle, high memory |
| **Tauri** | Tiny bundle, secure, fast | Requires Rust, newer |
| **Neutralino** | Smallest bundle, simple | Limited APIs, less mature |

**Recommendation**: Start with Electron, migrate to Tauri in V2

### 2. Deployment Platform
**Question**: Where to deploy the web app?

| Option | Pros | Cons |
|--------|------|------|
| **Vercel** | Best DX, fast, analytics | Expensive at scale |
| **Cloudflare** | Cheap, fast, unlimited | Less features |
| **Self-hosted** | Full control, cheapest | More work |

**Recommendation**: Vercel for MVP, evaluate Cloudflare for scale

### 3. Mobile Strategy
**Question**: How to handle mobile?

| Option | Pros | Cons |
|--------|------|------|
| **PWA** | No app store, instant updates | Limited native APIs |
| **React Native** | Native performance, code sharing | Separate codebase |
| **Capacitor** | Use web code, native wrapper | Performance overhead |

**Recommendation**: PWA for MVP, React Native for V2 if needed

---

## Next Steps

1. **Confirm decisions** on Desktop framework and deployment
2. **Initialize monorepo** with the structure above
3. **Start Phase 1** implementation
4. **Setup CI/CD** pipeline

Ready to proceed with implementation?

