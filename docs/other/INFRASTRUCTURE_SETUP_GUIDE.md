# TraceRTM Infrastructure Setup Guide

## Overview

TraceRTM uses a hybrid infrastructure stack:
- **Supabase** (PostgreSQL + Auth + Realtime)
- **Redis** (Caching + Sessions)
- **NATS** (Message Queue + Real-time Sync)

## ✅ Completed Setup

### 1. Supabase Project Created

**Project Details**:
- Name: TraceRTM
- Reference ID: `uftgquyagdvshekivcat`
- Region: East US (North Virginia)
- Dashboard: https://supabase.com/dashboard/project/uftgquyagdvshekivcat

**API Keys**:
```
Anon Key:        eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVmdGdxdXlhZ2R2c2hla2l2Y2F0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjQ0Mjc3NzQsImV4cCI6MjA4MDAwMzc3NH0.ce1_quKU8mItVFctUeKjNuMOMDif18Ry5Rh2bmxLx9A
Service Role:    eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InVmdGdxdXlhZ2R2c2hla2l2Y2F0Iiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2NDQyNzc3NCwiZXhwIjoyMDgwMDAzNzc0fQ.JP1b_gSswlqt6C_KgaDywFiok6GAyRzBT7OMbZy4OlM
```

**Database Connection**:
```
postgresql://postgres:TraceRTM_Secure_2025!@db.uftgquyagdvshekivcat.supabase.co:5432/postgres
```

### 2. Redis Setup

**Status**: Ready (CLI installed)

**Start Redis**:
```bash
redis-server
```

**Verify Connection**:
```bash
redis-cli ping
# Expected: PONG
```

**Configuration**:
- Host: localhost
- Port: 6379
- DB: 0

### 3. NATS Setup

**Status**: Ready (Credentials available)

**Credentials File**:
```
/Users/kooshapari/Downloads/NGS-Default-CLI.creds
```

**Connection Details**:
- URL: nats://connect.ngs.global:4222
- Type: NATS Cloud (NGS - Freemium)

**Test Connection**:
```bash
nats --creds /Users/kooshapari/Downloads/NGS-Default-CLI.creds server info
```

## 🚀 Next Steps

### 1. Update Backend Configuration

Copy `.env.production` to `.env`:
```bash
cd backend
cp .env.production .env
```

### 2. Start Services

**Terminal 1 - Redis**:
```bash
redis-server
```

**Terminal 2 - Backend**:
```bash
cd backend
go run main.go
```

**Terminal 3 - CLI** (optional):
```bash
cd cli
trace health
```

### 3. Deploy Schema to Supabase

```bash
cd backend
supabase db push
```

### 4. Verify Connections

```bash
# Test PostgreSQL
psql postgresql://postgres:TraceRTM_Secure_2025!@db.uftgquyagdvshekivcat.supabase.co:5432/postgres

# Test Redis
redis-cli ping

# Test NATS
nats --creds /Users/kooshapari/Downloads/NGS-Default-CLI.creds server info
```

## 📊 Architecture

```
┌─────────────────────────────────────────────────────┐
│                   TraceRTM Stack                    │
├─────────────────────────────────────────────────────┤
│                                                     │
│  CLI (Python)          Web (React)    Desktop (Tauri)
│  ├─ Typer              ├─ React 19    ├─ Rust
│  ├─ Rich               ├─ Vite        ├─ Tauri
│  └─ HTTP Client        └─ TanStack    └─ React
│         │                    │              │
│         └────────┬───────────┴──────────────┘
│                  │
│         ┌────────▼────────┐
│         │  Backend (Go)   │
│         │  ├─ Echo        │
│         │  ├─ sqlc + pgx  │
│         │  └─ REST API    │
│         └────────┬────────┘
│                  │
│    ┌─────────────┼─────────────┐
│    │             │             │
│    ▼             ▼             ▼
│ Supabase      Redis          NATS
│ ├─ PostgreSQL ├─ Cache       ├─ Messaging
│ ├─ Auth       ├─ Sessions    ├─ Real-time
│ └─ Realtime   └─ Queues      └─ Sync
│
└─────────────────────────────────────────────────────┘
```

## 🔐 Security Notes

1. **Never commit credentials** to version control
2. **Use `.env.local`** for local development
3. **Rotate keys** regularly in production
4. **Use environment variables** for all secrets
5. **Enable RLS** on Supabase tables

## 📝 Configuration Files

- `backend/.env.example` - Template
- `backend/.env.production` - Production config
- `backend/.env.local` - Local development (git-ignored)

## 🆘 Troubleshooting

### Redis Connection Refused
```bash
# Start Redis server
redis-server

# Or use Homebrew
brew services start redis
```

### NATS Connection Failed
```bash
# Verify credentials file
cat /Users/kooshapari/Downloads/NGS-Default-CLI.creds

# Test connection
nats --creds /Users/kooshapari/Downloads/NGS-Default-CLI.creds server info
```

### Supabase Connection Failed
```bash
# Verify database URL
psql $DATABASE_URL

# Check project status
supabase projects list
```

## 📚 References

- [Supabase Docs](https://supabase.com/docs)
- [Redis Docs](https://redis.io/docs/)
- [NATS Docs](https://docs.nats.io/)
- [PostgreSQL Docs](https://www.postgresql.org/docs/)

---

**Status**: ✅ Infrastructure ready for Phase 2 implementation

