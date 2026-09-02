# Tracera — Complete Deployment & Release Checklist

> **Purpose**: Every credential, key, service, and config needed to go from code to production.  
> **Status**: Track your progress by checking off each item.

---

## 0. Prerequisites (What You Need Before Starting)

| # | Item | Where to Get | Status |
|---|------|-------------|--------|
| 0.1 | **GitHub account** | github.com | ✅ (KooshaPari) |
| 0.2 | **Render account** | render.com (free tier) | ☐ |
| 0.3 | **Vercel account** | vercel.com (free tier) | ✅ |
| 0.4 | **Cloudflare account** | cloudflare.com (free tier) | ☐ |
| 0.5 | **Domain registered** | phenotype.studio (or similar) | ☐ |
| 0.6 | **Git installed** | git-scm.com | ✅ |
| 0.7 | **Rust toolchain** | rustup.rs | ✅ |
| 0.8 | **Bun installed** | bun.sh | ✅ |
| 0.9 | **Node.js + npm** | nodejs.org | ✅ |
| 0.10 | **wrangler CLI** | `npm install -g wrangler` | ☐ |
| 0.11 | **vercel CLI** | `npm install -g vercel` | ☐ |
| 0.12 | **Docker Desktop** | docker.com (for local) | ☐ |
| 0.13 | **SSH key** | `ssh-keygen -t ed25519` | ☐ |
| 0.14 | **GPG key** | `gpg --full-generate-key` | ☐ |

---

## 1. Secrets & Credentials (Generate These First)

### 1.1 — Auth Token (Backend)
```bash
# Generate a secure 32-byte hex token
openssl rand -hex 32
# Example output: a3f8b2c1d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0c1d2e3f4a5b6c7d8e9f0
# Save as: TRACERA_AUTH_TOKEN
```

### 1.2 — JWT Signing Key (If using JWT auth)
```bash
# Generate Ed25519 key pair
openssl genpkey -algorithm Ed25519 -out jwt-private-key.pem
openssl pkey -in jwt-private-key.pem -pubout -out jwt-public-key.pem
# Save private key securely, public key goes in config
```

### 1.3 — Cloudflare API Token
- Go to: https://dash.cloudflare.com/profile/api-tokens
- Create token with permissions:
  - `Workers: Edit`
  - `Workers KV: Edit`
  - `R2: Edit`
  - `DNS: Edit`
- Save as: `CLOUDFLARE_API_TOKEN`

### 1.4 — Vercel CLI Auth
```bash
vercel login
# Follow browser OAuth flow
# Save: VERCEL_TOKEN (auto-managed by CLI)
```

### 1.5 — Render CLI Auth
```bash
# Render doesn't have a CLI, use API token
# Go to: https://render.com/dashboard/settings/api
# Generate API token
# Save as: RENDER_API_TOKEN
```

### 1.6 — GPG Commit Signing Key
```bash
gpg --list-secret-keys --keyid-format=long
# Note the key ID
git config --global commit.gpgsign true
git config --global user.signingkey <KEY_ID>
```

### 1.7 — SSH Deploy Key (for GitHub)
```bash
ssh-keygen -t ed25519 -C "deploy@tracera" -f ~/.ssh/deploy_tracera
# Add public key to GitHub Deploy Keys
# Save private key securely
```

---

## 2. Domain & DNS

### 2.1 — Register / Configure Domain
| Domain | Purpose | DNS Provider | Status |
|--------|---------|-------------|--------|
| `phenotype.studio` | Main dashboard | Cloudflare | ☐ |
| `api.phenotype.studio` | API gateway (Render) | Cloudflare | ☐ |
| `ws.phenotype.studio` | WebSocket (Render) | Cloudflare | ☐ |
| `worker.phenotype.studio` | Cloudflare Worker | Cloudflare | ☐ |
| `docs.phenotype.studio` | Documentation (Vercel) | Cloudflare | ☐ |

### 2.2 — DNS Records (Cloudflare)
```
A       @       <Render external IP>        TTL Auto
CNAME   api     @                           TTL Auto (point to Render)
CNAME   www     @                           TTL Auto (point to Vercel)
TXT     @       v=spf1 include:vercel.com   TTL Auto
TXT     _dmarc  v=DMARC1; p=none            TTL Auto
```

### 2.3 — SSL/TLS Certificates
- **Automatic**: Cloudflare Universal SSL (free, auto-issued)
- **Manual backup**: Let's Encrypt via certbot if not using Cloudflare
```bash
certbot certonly --standalone -d phenotype.studio -d api.phenotype.studio
```

---

## 3. Backend Deployment (Render)

### 3.1 — Prerequisites
- [ ] Render account created
- [ ] GitHub repo connected to Render
- [ ] `render.yaml` exists in repo root ✅
- [ ] `Dockerfile.rust` exists ✅
- [ ] `Cargo.toml` workspace configured ✅

### 3.2 — Render Setup Steps
```bash
# 1. Login to Render (via browser)
# 2. Go to https://render.com/dashboard
# 3. Click "New +" → "Web Service"
# 4. Connect GitHub repo: KooshaPari/Tracera
# 5. Select branch: main
# 6. Render will auto-detect render.yaml

# OR use Render API:
curl -X POST https://api.render.com/v1/services \
  -H "Authorization: Bearer $RENDER_API_TOKEN" \
  -H "Content-Type: application/json" \
  -d @render.yaml
```

### 3.3 — Environment Variables (Render)
| Variable | Value | Source |
|----------|-------|--------|
| `DATABASE_URL` | Auto-provided by Render PostgreSQL | Render DB |
| `TRACERA_AUTH_TOKEN` | From §1.1 | Generated |
| `TRACERA_BIND_ADDR` | `0.0.0.0:8080` | Hardcoded |
| `TRACERA_PUBLIC_BIND_MODE` | `loopback-published` | Hardcoded |
| `RUST_LOG` | `info` | Hardcoded |
| `RUST_BACKTRACE` | `1` | Hardcoded |

### 3.4 — PostgreSQL Database (Render)
```bash
# Create via render.yaml (auto-provisioned)
# Or manually:
# Render Dashboard → Databases → New PostgreSQL
# Plan: Free (256MB RAM, 1GB disk)
# Region: Closest to you
```

### 3.5 — Verify Backend
```bash
# After deploy, get the URL:
# https://tracera-server.onrender.com

curl https://tracera-server.onrender.com/healthz
# Expected: {"status":"ok","service":"tracera-server"}

curl https://tracera-server.onrender.com/readyz
# Expected: {"status":"ready","version":"0.1.3","backend":"postgres"}
```

---

## 4. Frontend Deployment (Vercel)

### 4.1 — Prerequisites
- [ ] Vercel account ✅
- [ ] `vercel.json` exists ✅
- [ ] `frontend/apps/web/package.json` exists ✅
- [ ] `frontend/apps/web/vite.config.ts` exists ✅

### 4.2 — Environment Variables (Vercel)
```bash
# Set production API URL
vercel env add VITE_API_URL production
# Value: https://api.phenotype.studio (or your Render URL)

vercel env add VITE_WS_URL production
# Value: wss://api.phenotype.studio

vercel env add VITE_APP_ENV production
# Value: production

# Verify:
vercel env ls
```

### 4.3 — Deploy
```bash
# First deploy (or re-deploy after changes):
vercel --prod --yes

# Or from CI:
vercel deploy --prod --yes --cwd frontend
```

### 4.4 — Verify Frontend
```bash
curl -s -o /dev/null -w "%{http_code}" https://tracera-kappa.vercel.app
# Expected: 200

# Check API connectivity:
curl https://tracera-kappa.vercel.app/api/health
# Expected: proxy to backend healthz
```

---

## 5. Cloudflare Worker Deployment

### 5.1 — Prerequisites
- [ ] Cloudflare account ✅
- [ ] `wrangler.toml` exists ✅
- [ ] `CLOUDFLARE_API_TOKEN` from §1.3
- [ ] KV namespace provisioned (see §5.2)
- [ ] R2 bucket provisioned (see §5.3)

### 5.2 — Provision KV Namespace
```bash
wrangler kv namespace create tracera_cache
# Copy the "id" from output → update wrangler.toml id field

wrangler kv namespace create tracera_cache --preview
# Copy preview_id → update wrangler.toml preview_id field
```

### 5.3 — Provision R2 Bucket
```bash
wrangler r2 bucket create tracera-artifacts
```

### 5.4 — Deploy Worker
```bash
# Login if needed:
wrangler login

# Deploy:
wrangler deploy --env production

# Or with specific config:
wrangler deploy -c wrangler.toml
```

### 5.5 — Verify Worker
```bash
curl -s https://tracera-edge.workers.dev
# Expected: Worker response

# Check KV:
wrangler kv:key list --namespace TRACERA_KV

# Check R2:
wrangler r2 bucket list --name tracera-artifacts
```

---

## 6. Desktop Client (Electrobun / Tauri)

### 6.1 — Prerequisites
- [ ] Electrobun installed (Electron + Bun)
- [ ] Code signing certificates (§7)
- [ ] Auto-update server configured

### 6.2 — Build
```bash
cd frontend/apps/desktop
bun run build
# Output: electrum build → .exe/.dmg/.AppImage
```

### 6.3 — Code Signing (Windows)
- [ ] Windows Authenticode certificate (e.g., from DigiCert, Sectigo)
- [ ] Install certificate in Windows Store
- [ ] Configure in `electrobun.config.ts`:
```ts
export default {
  build: {
    win: {
      certificateSubjectName: "Your Company Name",
      publisherName: "Your Publisher Name",
    },
  },
};
```

### 6.4 — Code Signing (macOS)
- [ ] Apple Developer ID certificate
- [ ] Notarization enabled
- [ ] `electron-builder` notarization config

### 6.5 — Auto-Update Setup
- [ ] Update server (e.g., S3, R2, or Render endpoint)
- [ ] Configure `updater.ts` with update URL
- [ ] Test update flow from v0.1.0 → v0.1.1

---

## 7. CLI Tool (`tracera` / `tracera-server`)

### 7.1 — Build Release Binaries
```bash
# Linux x64
cargo build --release --target x86_64-unknown-linux-gnu

# macOS
cargo build --release --target x86_64-apple-darwin

# Windows
cargo build --release --target x86_64-pc-windows-msvc
```

### 7.2 — Publish to Package Managers
- [ ] **npm** (as `tracera-cli`): `npm publish`
- [ ] **Cargo** (crates.io): `cargo publish`
- [ ] **GitHub Releases**: Upload binaries to releases

### 7.3 — Install Scripts
```bash
# curl-based installer (like `curl | sh`):
curl -fsSL https://tracera.phenotype.studio/install | sh

# PowerShell installer (Windows):
irm https://tracera.phenotype.studio/install.ps1 | iex
```

---

## 8. Database & Storage

### 8.1 — PostgreSQL (Render Managed)
- [ ] Database created via Render
- [ ] Migrations applied on deploy
- [ ] Connection string in `DATABASE_URL`
- [ ] Backup schedule configured (Render auto-backup)

### 8.2 — SQLite (Local/Client)
- [ ] `sqlite::memory:` for dev
- [ ] `sqlite:tracera.db` for local prod
- [ ] Migrations applied on first run

### 8.3 — R2 (Cloudflare)
- [ ] Bucket created: `tracera-artifacts`
- [ ] Used for: uploaded evidence, generated reports, export files

### 8.4 — KV (Cloudflare)
- [ ] Namespace: `tracera_cache`
- [ ] Used for: session tokens, rate limiting, cached queries

---

## 9. Monitoring & Observability

### 9.1 — Health Checks
| Endpoint | Method | Expected | Frequency |
|----------|--------|----------|-----------|
| `/healthz` | GET | `{"status":"ok"}` | 30s |
| `/readyz` | GET | `{"status":"ready"}` | 30s |
| `/metrics` | GET | Prometheus text | 60s |

### 9.2 — Alerting
- [ ] Render: Email alerts on deploy failure
- [ ] Vercel: Slack/email on build failure
- [ ] Cloudflare: Worker error alerts
- [ ] Custom: `/metrics` scraped by Prometheus/Grafana

### 9.3 — Logging
- [ ] Render: Log drain to external service
- [ ] Cloudflare: Workers logs via `wrangler tail`
- [ ] Vercel: Function logs in dashboard

---

## 10. CI/CD Pipeline

### 10.1 — GitHub Actions Workflows
| Workflow | Trigger | What It Does |
|----------|---------|-------------|
| `ci.yml` | PR/push | Lint, test, build |
| `e2e.yml` | PR/push | E2E contract tests |
| `coverage.yml` | push | Coverage report |
| `mutants.yml` | push | Mutation testing |
| `audit-sla.yml` | cron (1st of month) | Auto-scorecard |
| `release-desktop-sign.yml` | tag `v*` | Build + sign desktop |

### 10.2 — Branch Protection (Already Applied)
- [x] `enforce_admins: true`
- [x] `required_pull_request_reviews: 1`
- [x] `required_linear_history: true`
- [x] `allow_force_pushes: false`
- [x] `required_conversation_resolution: true`

### 10.3 — Signed Commits
- [x] GPG/SSH signing configured
- [x] `verify-signed-commits.sh` in CI
- [x] CONTRIBUTING.md documents signing setup

---

## 11. Security Hardening

### 11.1 — Rate Limiting
- [x] Implemented in `main.rs` (100 req/min per IP)
- [ ] Verify in production

### 11.2 — CORS
- [ ] Configure for `phenotype.studio` and `phenotype.space`
- [ ] Update `main.rs` CORS middleware

### 11.3 — Auth Token Rotation
- [ ] `TRACERA_AUTH_TOKEN` generated
- [ ] Rotate every 90 days
- [ ] Store in Render env vars (not in repo)

### 11.4 — Dependency Scanning
- [x] `cargo audit` in CI
- [x] `npm audit` in CI
- [x] Dependabot enabled

### 11.5 — Secrets Management
- [x] All secrets in env vars (never in repo)
- [x] `.env.example` has placeholders only
- [x] `.gitignore` excludes `.env` files

---

## 12. Release Process

### 12.1 — Version Bumping
```bash
# Semantic versioning:
# v0.1.0 — Initial release
# v0.1.1 — Patch
# v0.2.0 — Minor
# v1.0.0 — Major

# Bump version:
cargo set-version 0.1.0  # In Cargo.toml
# Update version in main.rs, package.json, vercel.json
```

### 12.2 — Git Tag & Push
```bash
git tag -s v0.1.0 -m "Release v0.1.0"
git push origin v0.1.0
```

### 12.3 — CI Triggers on Tag
- [ ] Build all binaries (Rust + Frontend + Desktop)
- [ ] Run all tests
- [ ] Deploy to Render (backend)
- [ ] Deploy to Vercel (frontend)
- [ ] Deploy Cloudflare Worker
- [ ] Publish to npm/Cargo
- [ ] Create GitHub Release with binaries
- [ ] Send notification (Discord/Slack)

---

## 13. Post-Deployment Verification

### 13.1 — Smoke Tests
```bash
# Backend:
curl https://api.phenotype.studio/healthz
# → {"status":"ok"}

curl https://api.phenotype.studio/readyz
# → {"status":"ready","backend":"postgres"}

# Frontend:
curl -s -o /dev/null -w "%{http_code}" https://phenotype.studio
# → 200

# Worker:
curl -s https://tracera-edge.workers.dev
# → Worker response

# CLI:
tracera --version
# → 0.1.0

tracera server status
# → Running on port 8080
```

### 13.2 — End-to-End Flow
1. Create a spec in the governance layer
2. Ingest an agent/task via `/ingest/agileplus`
3. Create a trace link
4. Query the graph: `GET /api/v1/graph/nodes`
5. Run coverage matrix: `POST /api/v1/coverage-matrix`
6. Run spec-check: `POST /api/v1/governance/spec-check`
7. Verify memory distillation generates an insight
8. Check metrics: `GET /metrics`

### 13.3 — Scorecard Verification
```bash
# Re-run the audit scorecard:
cargo test -p tracera-server
# All tests pass

# Verify all 435 pillars are scored:
cat audit/SCORECARD-FULL-2026-08-30.md | grep "TOTAL"
# → 435/435 (100%)
```

---

## 14. Cost Summary (Free Tier)

| Service | Cost | What It Provides |
|---------|------|-----------------|
| **Render** | $0/mo | Rust backend + PostgreSQL 17 |
| **Vercel** | $0/mo | Frontend hosting + edge |
| **Cloudflare** | $0/mo | Workers + KV + R2 + DNS + SSL |
| **GitHub** | $0/mo | Repo + CI/CD + Packages |
| **Domain** | ~$10/yr | phenotype.studio |
| **Total** | **~$10/yr** | Full production stack |

---

## 15. Quick Start (Everything in One Place)

```bash
# 1. Clone repo
git clone https://github.com/KooshaPari/Tracera.git
cd Tracera

# 2. Install tools
curl -fsSL https://bun.sh/install | bash
npm install -g vercel wrangler
rustup target add wasm32-unknown-unknown

# 3. Build everything
cargo build --release -p tracera-server
cargo build --release -p tracera-cli
cd frontend && bun install && bun run build
cd .. && cd crates/tracera-edge && worker-build --release

# 4. Start local backend
set DATABASE_URL=sqlite::memory: && tracera-server

# 5. Deploy (in order):
# a) Render: Push to main → auto-deploys
# b) Vercel: vercel --prod
# c) Cloudflare: wrangler deploy
# d) Desktop: tag v0.1.0 → CI builds + signs

# 6. Verify
curl https://api.phenotype.studio/healthz
curl https://phenotype.studio
curl https://tracera-edge.workers.dev
tracera --version
```

---

## 16. Checklist Master (Copy and Track)

```
□ 0. Prerequisites (all tools installed)
□ 1. Secrets & Credentials (all tokens generated)
□ 2. Domain & DNS (all records configured)
□ 3. Backend on Render (deployed and healthy)
□ 4. Frontend on Vercel (deployed and healthy)
□ 5. Cloudflare Worker (deployed and healthy)
□ 6. Desktop Client (built, signed, published)
□ 7. CLI Tool (published to npm/Cargo)
□ 8. Database & Storage (provisioned and tested)
□ 9. Monitoring & Observability (alerts configured)
□ 10. CI/CD Pipeline (all workflows passing)
□ 11. Security Hardening (all checks pass)
□ 12. Release Process (v0.1.0 tagged and deployed)
□ 13. Post-Deployment Verification (all smoke tests pass)
□ 14. Cost Summary (confirmed within budget)
```

---

*Generated: 2026-09-01*  
*Scorecard: 435/435 (100%)*  
*Status: Ready for deployment*
